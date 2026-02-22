import logging
import json
import time
import os
from decimal import Decimal
from typing import List, Dict
from django.db import transaction
from django.utils import timezone
from apps.batches.models import Batch, BatchItem
from apps.common.alerts import emit_alarm
from apps.exports.models import Export
from apps.exports.tasks import generate_export_file
from apps.ledger.models import CreditPackage, LedgerEntry
from apps.providers.google_places import GooglePlacesClient
from apps.providers.grid_search import Rectangle
from apps.providers.email_enrichment import EmailEnrichmentClient

logger = logging.getLogger(__name__)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        logger.warning("Invalid integer for %s=%r, using default=%s", name, raw, default)
        return default
    return max(1, value)

class BatchProcessor:
    def __init__(self, batch_id):
        self.batch = Batch.objects.get(id=batch_id)
        self.client = GooglePlacesClient()
        self.max_hard_limit = _env_int("ANKA_BATCH_MAX_RECORDS", 50)
        self.stage1_api_call_cap = _env_int("ANKA_STAGE1_MAX_API_CALLS", 20)
        self.stage2_api_call_cap = _env_int("ANKA_STAGE2_MAX_API_CALLS", 80)
        self.stage3_api_call_cap = _env_int("ANKA_STAGE3_MAX_API_CALLS", 80)

    def _settle_credits(self, delivered_count: int, reason: str = "") -> Decimal:
        estimated_cost = Decimal(str(self.batch.estimated_cost or 0))
        actual_cost = Decimal(str(max(delivered_count, 0)))
        refund_amount = estimated_cost - actual_cost

        if refund_amount <= 0:
            return Decimal("0")

        spent_exists = LedgerEntry.objects.filter(
            reference_type="batch",
            reference_id=str(self.batch.id),
            transaction_type="spent",
        ).exists()
        if not spent_exists:
            logger.info(
                "Batch %s: No spent ledger entry found, skipping refund settlement",
                self.batch.id,
            )
            return Decimal("0")

        refund_reference = f"batch-refund:{self.batch.id}"

        with transaction.atomic():
            credit_package, _ = CreditPackage.objects.select_for_update().get_or_create(
                organization=self.batch.organization,
                defaults={"balance": 0, "total_purchased": 0, "total_spent": 0, "total_refunded": 0},
            )

            refund_balance_before = Decimal(str(credit_package.balance))
            refund_balance_after = refund_balance_before + refund_amount

            refund_entry, created = LedgerEntry.objects.get_or_create(
                reference_type="dispute",
                reference_id=refund_reference,
                defaults={
                    "organization": self.batch.organization,
                    "transaction_type": "refund",
                    "amount": refund_amount,
                    "status": "completed",
                    "description": "Batch settlement refund",
                    "balance_before": refund_balance_before,
                    "balance_after": refund_balance_after,
                    "metadata": {
                        "batch_id": str(self.batch.id),
                        "estimated_cost": str(estimated_cost),
                        "actual_cost": str(actual_cost),
                        "reason": reason,
                    },
                },
            )

            if not created:
                logger.info(
                    "Batch %s: Refund ledger already exists (%s), skipping duplicate settlement",
                    self.batch.id,
                    refund_reference,
                )
                return Decimal("0")

            credit_package.balance = refund_balance_after
            credit_package.total_refunded = Decimal(str(credit_package.total_refunded)) + refund_amount
            credit_package.save(update_fields=["balance", "total_refunded", "updated_at"])

        metadata = dict(self.batch.metadata or {})
        metadata.update(
            {
                "settlement_refund": str(refund_amount),
                "settlement_delivered": int(delivered_count),
                "settlement_reason": reason,
            }
        )
        self.batch.metadata = metadata
        self.batch.save(update_fields=["metadata", "updated_at"])

        logger.info(
            "Batch %s: Settlement refund applied amount=%s (estimated=%s actual=%s)",
            self.batch.id,
            refund_amount,
            estimated_cost,
            actual_cost,
        )

        return refund_amount

    def _enqueue_exports(self):
        if self.batch.contacts_enriched <= 0:
            return

        for export_format in ("csv", "xlsx"):
            export_obj, created = Export.objects.get_or_create(
                organization=self.batch.organization,
                batch=self.batch,
                format=export_format,
                defaults={"status": "pending"},
            )

            if not created and export_obj.status == "completed":
                continue

            if not created and export_obj.status == "processing":
                continue

            if not created:
                export_obj.status = "pending"
                export_obj.error_message = ""
                export_obj.save(update_fields=["status", "error_message", "updated_at"])

            generate_export_file.delay(str(export_obj.id))

    def run_pipeline(self):
        try:
            # 1. Start
            self.batch.status = 'COLLECTING_IDS'
            self.batch.started_at = timezone.now()
            self.batch.save()
            
            # 2. Collect IDs (Stage 1)
            raw_candidates = self._stage_collect_ids()
            self.batch.ids_collected = len(raw_candidates)
            self.batch.save()

            if not raw_candidates:
                self.batch.status = 'PARTIAL'
                self.batch.aborted_reason = 'Stage 1 aday bulunamadı'
                self.batch.contacts_enriched = 0
                self.batch.processed_records = 0
                self.batch.completed_at = timezone.now()
                self.batch.save()
                self._settle_credits(delivered_count=0, reason='no_candidates_stage_1')
                return
            
            # 3. Filter (Stage 2)
            self.batch.status = 'FILTERING'
            self.batch.save()
            
            verified_items = self._stage_filter_details_pro(raw_candidates)
            self.batch.ids_verified = len(verified_items)
            self.batch.skipped_404 = self.batch.error_records # We are tracking errors in stage 2
            self.batch.save()

            if not verified_items:
                self.batch.status = 'PARTIAL'
                self.batch.aborted_reason = 'Stage 2 doğrulamada sonuç kalmadı'
                self.batch.contacts_enriched = 0
                self.batch.processed_records = 0
                self.batch.completed_at = timezone.now()
                self.batch.save()
                self._settle_credits(delivered_count=0, reason='no_verified_stage_2')
                return

            if self.batch.status == 'PARTIAL':
                # Aborted in stage 2, stop here
                self.batch.completed_at = timezone.now()
                self.batch.save()
                self._settle_credits(delivered_count=0, reason='partial_stage_2')
                return

            # 4. Enrich (Stage 3)
            self.batch.status = 'ENRICHING_CONTACTS'
            self.batch.save()
            
            enriched_items = self._stage_enrich_enterprise(verified_items)
            self.batch.contacts_enriched = len([i for i in enriched_items if i.data.get('stage_3_enterprise')])

            if self.batch.contacts_enriched == 0:
                self.batch.status = 'PARTIAL'
                self.batch.aborted_reason = 'Stage 3 iletişim zenginleştirmede sonuç yok'
                self.batch.completed_at = timezone.now()
                self.batch.processed_records = len(verified_items)
                self.batch.save()
                self._settle_credits(delivered_count=0, reason='no_enrichment_stage_3')
                return

            # 5. Email Enrichment (Stage 4 - opsiyonel)
            if self._email_enrichment_enabled():
                self.batch.status = 'ENRICHING_EMAILS'
                self.batch.save()
                self._stage_enrich_emails(enriched_items)

            # 6. Finish
            self.batch.status = 'READY'
            self.batch.completed_at = timezone.now()
            self.batch.processed_records = len(verified_items)
            self.batch.save()
            self._settle_credits(
                delivered_count=self.batch.contacts_enriched,
                reason='ready_settlement',
            )
            self._enqueue_exports()
            
        except Exception as e:
            logger.exception(f"Batch {self.batch.id} failed: {e}")
            self.batch.status = 'FAILED'
            self.batch.save()
            emit_alarm(
                code="BATCH_PIPELINE_FAILED",
                message="Batch pipeline hit an unhandled exception and was marked FAILED",
                metadata={
                    "batch_id": str(self.batch.id),
                    "city": self.batch.city,
                    "sector": self.batch.sector,
                    "error": str(e),
                },
                exc=e,
            )
            
    def _stage_collect_ids(self, include_stage2=False, include_stage3=False):
        """
        Stage 1: Adaptive Quadtree Text Search (Cost-Optimized)
        Goal: Collect pool of IDs with minimal API calls
        
        Args:
            include_stage2: If True, run Stage 2 verification after ID collection
            include_stage3: If True, run Stage 3 enrichment after verification (requires include_stage2=True)
        """
        # Guard: Hard limit maximum records to prevent abuse
        limit = min(self.batch.record_count_estimate or 100, self.max_hard_limit)
        
        candidates = []
        seen_ids = set()
        
        # Try Adaptive Search first
        from apps.providers.grid_search import get_adaptive_search_regions
        
        target_district = self.batch.filters.get('district') if self.batch.filters else None
        start_region = get_adaptive_search_regions(self.batch.city, target_district)
        
        if start_region:
            logger.info(f"Batch {self.batch.id}: Starting Adaptive Search for {self.batch.city}")
            
            # Adaptive search with recursive splitting
            total_requests = [0]  # Use list for mutable counter in nested function
            
            def adaptive_search_recursive(region: 'Rectangle', depth: int = 0) -> List[dict]:
                """Recursively search a region, splitting if too many results"""
                MAX_DEPTH = 4  # Prevent infinite recursion
                SPLIT_THRESHOLD = 60  # Google's typical max per request
                
                if depth > MAX_DEPTH:
                    return []

                if total_requests[0] >= self.stage1_api_call_cap:
                    logger.warning(
                        "Batch %s: Stage 1 API cap reached (%s), stopping ID collection early",
                        self.batch.id,
                        self.stage1_api_call_cap,
                    )
                    return []
                
                total_requests[0] += 1
                response = self.client.text_search_ids_only(
                    query=self.batch.sector,
                    location_restriction=region.to_dict(),
                    language_code='tr'
                )
                
                places = response.get('places', []) if response else []
                logger.debug(f"Depth {depth}: Found {len(places)} places (Request #{total_requests[0]})")
                
                # If few results, we're done with this region
                if len(places) < SPLIT_THRESHOLD:
                    return places
                
                # Too many results - split into quadrants and search each
                logger.debug(f"Splitting region at depth {depth} ({len(places)} >= {SPLIT_THRESHOLD})")
                sub_results = []
                
                for quad in region.split():
                    if len(sub_results) + len(candidates) >= limit:
                        break  # Don't exceed our limit
                    quad_results = adaptive_search_recursive(quad, depth + 1)
                    sub_results.extend(quad_results)
                
                return sub_results
            
            # Start the adaptive search
            all_places = adaptive_search_recursive(start_region)
            
            # Process results
            for p in all_places:
                if len(candidates) >= limit:
                    break
                pid = p.get('id')
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    candidates.append({'id': pid, 'name': p.get('name')})
            
            logger.info(f"Batch {self.batch.id}: Adaptive Search completed with {total_requests[0]} API calls")
            
            # Stage 2: Verification if requested
            if include_stage2:
                logger.info(f"Batch {self.batch.id}: Starting Stage 2 Verification")
                verified_places = self._stage2_verify_businesses([p.get('id') for p in all_places if p.get('id')])
                logger.info(f"Batch {self.batch.id}: Stage 2 completed. {len(verified_places)} verified")
                
                # Stage 3: Enrichment if requested
                if include_stage3:
                    logger.info(f"Batch {self.batch.id}: Starting Stage 3 Enrichment")
                    enriched_places = self._stage3_enrich_contacts([p.get('place_id') for p in verified_places])
                    logger.info(f"Batch {self.batch.id}: Stage 3 completed. {len(enriched_places)} enriched")
                    
                    # Create mapping of enriched data by place_id
                    enriched_map = {e.get('place_id'): e for e in enriched_places}
                    
                    # Clear candidates and add enriched results
                    candidates = []
                    for verified in verified_places:
                        if len(candidates) >= limit:
                            break
                        
                        # Get enriched data for this place
                        place_id = verified.get('place_id')
                        enriched_data = enriched_map.get(place_id, {})
                        
                        candidates.append({
                            'id': place_id,
                            'name': verified.get('display_name', 'Unknown'),
                            'address': verified.get('formatted_address', ''),
                            'types': verified.get('types', []),
                            'verification_reason': verified.get('verification_reason'),
                            'website': enriched_data.get('website_uri', 'No website'),
                            'phone': enriched_data.get('phone_number', 'No phone')
                        })
                else:
                    # Stage 2 only - add verified results
                    candidates = []
                    for verified in verified_places:
                        if len(candidates) >= limit:
                            break
                        candidates.append({
                            'id': verified.get('place_id'),
                            'name': verified.get('display_name', 'Unknown'),
                            'address': verified.get('formatted_address', ''),
                            'types': verified.get('types', []),
                            'verification_reason': verified.get('verification_reason')
                        })
            else:
                # Stage 1 only - just collect IDs
                for p in all_places:
                    if len(candidates) >= limit:
                        break
                    pid = p.get('id')
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        candidates.append({'id': pid, 'name': p.get('name')})
                
        logger.info(f"Batch {self.batch.id}: Collected {len(candidates)} IDs")
        return candidates
        
    def _stage2_verify_businesses(self, place_ids: List[str]) -> List[Dict]:
        """
        Stage 2: Verification - Check business status and category
        
        Args:
            place_ids: List of place IDs from Stage 1
            
        Returns:
            List of verified business data with key fields
        """
        verified_businesses = []
        api_calls_stage2 = 0
        
        # Professional service types that match "şehir plancısı" profile
        # Based on Google Places Table A categories
        target_business_types = {
            'consultant',  # Generic professional consultant
            'corporate_office',  # Professional office
            'establishment',  # Generic establishment marker
            'point_of_interest'  # General POI (often includes prof services)
        }
        
        for place_id in place_ids:
            try:
                # API Call: Place Details Pro
                result = self.client.get_place_details_pro(place_id)
                api_calls_stage2 += 1
                
                if not result:
                    logger.debug(f"Place {place_id}: Not found (404)")
                    continue
                    
                # Check business status
                business_status = result.get('businessStatus')
                if business_status != 'OPERATIONAL':
                    logger.debug(f"Place {place_id}: Not operational ({business_status})")
                    continue
                    
                # Check types (categories)
                types = result.get('types', [])
                display_name = result.get('displayName', {}).get('text', 'Unknown')
                
                # Verification logic: Either has target type OR name indicates planning profession
                has_target_type = bool(set(types) & target_business_types)
                name_indicates_planning = any(keyword in display_name.lower() for keyword in [
                    'planc', 'planlam', 'urban', 'şehir', 'kent', 'peyzaj', 'mimar', 'architect'
                ])
                
                if has_target_type or name_indicates_planning:
                    verified_data = {
                        'place_id': place_id,
                        'display_name': display_name,
                        'formatted_address': result.get('formattedAddress', 'N/A'),
                        'types': types,
                        'business_status': business_status,
                        'verification_reason': 'type_match' if has_target_type else 'name_match'
                    }
                    verified_businesses.append(verified_data)
                    logger.debug(f"✅ Verified: {display_name} ({verified_data['verification_reason']})")
                else:
                    logger.debug(f"❌ Rejected: {display_name} (types: {types[:3]}...)")
                    
            except Exception as e:
                logger.warning(f"Stage 2 error for place {place_id}: {e}")
                continue
        
        logger.info(f"Batch {self.batch.id}: Stage 2 API calls: {api_calls_stage2}")
        logger.info(f"Batch {self.batch.id}: Verification rate: {len(verified_businesses)}/{len(place_ids)} ({len(verified_businesses)/len(place_ids)*100:.1f}%)")
        
        return verified_businesses

    def _stage3_enrich_contacts(self, place_ids):
        """
        Stage 3: Enterprise Contact Enrichment
        Goal: Get contact information (website, phone) for verified businesses
        
        Args:
            place_ids: List of verified place IDs from Stage 2
        
        Returns:
            List of enriched business data
        """
        enriched_businesses = []
        api_calls_stage3 = 0
        
        logger.info(f"Batch {self.batch.id}: Enriching {len(place_ids)} verified businesses")
        
        for place_id in place_ids:
            try:
                api_calls_stage3 += 1
                result = self.client.get_place_details_enterprise(place_id)
                
                if result:
                    # Extract contact information
                    website_uri = result.get('websiteUri')
                    phone_number = result.get('nationalPhoneNumber')
                    
                    # Create enriched data structure
                    enriched_data = {
                        'place_id': place_id,
                        'website_uri': website_uri,
                        'phone_number': phone_number,
                        'has_contact_info': bool(website_uri or phone_number)
                    }
                    
                    enriched_businesses.append(enriched_data)
                    
                    contact_info = []
                    if website_uri:
                        contact_info.append(f"Website: {website_uri}")
                    if phone_number:
                        contact_info.append(f"Phone: {phone_number}")
                    
                    logger.debug(f"📞 Enriched: {place_id} - {', '.join(contact_info) if contact_info else 'No contact info'}")
                else:
                    logger.debug(f"❌ No enterprise data for: {place_id}")
                    
            except Exception as e:
                logger.warning(f"Stage 3 error for place {place_id}: {e}")
                continue
        
        logger.info(f"Batch {self.batch.id}: Stage 3 API calls: {api_calls_stage3}")
        logger.info(f"Batch {self.batch.id}: Contact enrichment rate: {len([b for b in enriched_businesses if b.get('has_contact_info')])}/{len(enriched_businesses)} ({len([b for b in enriched_businesses if b.get('has_contact_info')])/len(enriched_businesses)*100:.1f}% have contact info)")
        
        return enriched_businesses

    def _stage_filter_details_pro(self, candidates):
        """
        Stage 2: Place Details Pro
        Goal: Get human readable name, address, validate
        """
        verified_items = []
        error_count = 0
        THRESHOLD_ABORT = 0.5 # If 50% fail, stop batch to save money
        
        for i, cand in enumerate(candidates):
            if i >= self.stage2_api_call_cap:
                logger.warning(
                    "Batch %s: Stage 2 API cap reached (%s), stopping verification early",
                    self.batch.id,
                    self.stage2_api_call_cap,
                )
                self.batch.status = 'PARTIAL'
                self.batch.aborted_reason = "Stage 2 API cap reached"
                break

            # Circuit breaker check every 10 items
            if i > 10 and (error_count / i) > THRESHOLD_ABORT:
                logger.error(f"Batch {self.batch.id} aborted: High failure rate in Stage 2")
                self.batch.status = 'PARTIAL'
                self.batch.aborted_reason = "High failure rate in Stage 2 (Place Details Pro)"
                break

            try:
                # API Call
                details = self.client.get_place_details_pro(cand['id'])
                
                if not details: # 404 or other non-critical error handled by client
                    error_count += 1
                    continue

                # Validation Logic here
                # E.g. check if address is valid. 
                # For now, if we got details, we assume it's valid enough.
                
                item = BatchItem(
                    batch=self.batch,
                    firm_id=cand['id'],
                    firm_name=details.get('displayName', {}).get('text', cand.get('name')), 
                    data={
                        'formatted_address': details.get('formattedAddress'),
                        'formattedAddress': details.get('formattedAddress'),
                        'google_place_id': cand['id'],
                        'stage_2_pro': True
                    },
                    is_verified=True 
                )
                item.save()
                verified_items.append(item)
                
            except Exception as e:
                logger.error(f"Failed Pro Details for {cand['id']}: {e}")
                error_count += 1
                
        self.batch.error_records = error_count
        self.batch.save()
        return verified_items

    def _stage_enrich_enterprise(self, items):
        """
        Stage 3: Place Details Enterprise
        Goal: Get contact info
        """
        success_count = 0
        
        for idx, item in enumerate(items):
            if idx >= self.stage3_api_call_cap:
                logger.warning(
                    "Batch %s: Stage 3 API cap reached (%s), skipping remaining enrichments",
                    self.batch.id,
                    self.stage3_api_call_cap,
                )
                break

            try:
                # Guard: Extra check to ensure we don't enrich if previous stages looked fishy
                # or if we hit a unexpected snag (redundant with stage 2 checks but good for future)
                
                details = self.client.get_place_details_enterprise(item.firm_id)
                
                if not details:
                    continue

                # Update item data
                item.data['website_uri'] = details.get('websiteUri')
                item.data['websiteUri'] = details.get('websiteUri')
                item.data['phone_number'] = details.get('nationalPhoneNumber')
                item.data['nationalPhoneNumber'] = details.get('nationalPhoneNumber')
                item.data['stage_3_enterprise'] = True
                
                item.save()
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed Enterprise Details for {item.firm_id}: {e}")
                # We don't abort batch here typically, getting partial contact info is better than none
                
        return items

    # ------------------------------------------------------------------
    # Stage 4: Email Enrichment (opsiyonel, ANKA_EMAIL_ENRICHMENT_ENABLED)
    # ------------------------------------------------------------------

    @staticmethod
    def _email_enrichment_enabled() -> bool:
        val = os.environ.get("ANKA_EMAIL_ENRICHMENT_ENABLED", "true").strip().lower()
        return val not in ("0", "false", "no", "off")

    def _stage_enrich_emails(self, items: List) -> None:
        """
        Stage 4: Email Enrichment
        BatchItem.data'ya 'email' anahtarı yazar.
        Strateji 1 – website biliniyorsa: HTTP scrape (0 Gemini token)
        Strateji 2 – website yoksa: Gemini Search Grounding → HTTP scrape (1 Gemini call)
        Hatalar batch'i durdurmaz; o kayıt için email boş kalır.
        """
        stage4_api_cap = _env_int("ANKA_STAGE4_MAX_API_CALLS", 80)
        email_client = EmailEnrichmentClient()
        found_count = 0
        gemini_calls = 0

        for idx, item in enumerate(items):
            if not item.data.get("stage_3_enterprise"):
                continue  # Stage 3'ten geçmemiş kayıtları atla

            if gemini_calls >= stage4_api_cap:
                logger.warning(
                    "Batch %s: Stage 4 Gemini cap reached (%s), skipping remaining",
                    self.batch.id,
                    stage4_api_cap,
                )
                break

            # Mevcut website yoksa bu kayıt için Gemini kullanılacak (1 call)
            website = item.data.get("website_uri") or item.data.get("websiteUri") or ""
            will_use_gemini = not bool(website)

            try:
                email = email_client.enrich(
                    firm_name=item.firm_name or "",
                    address=item.data.get("formatted_address") or "",
                    website_url=website or None,
                )

                if will_use_gemini:
                    gemini_calls += 1

                if email:
                    item.data["email"] = email
                    item.save(update_fields=["data", "updated_at"])
                    found_count += 1
                    logger.debug(
                        "Batch %s: Stage 4 email found [%s] → %s",
                        self.batch.id,
                        item.firm_name,
                        email,
                    )

            except Exception as exc:
                logger.warning(
                    "Batch %s: Stage 4 email error for %s: %s",
                    self.batch.id,
                    item.firm_name,
                    exc,
                )
                if will_use_gemini:
                    gemini_calls += 1  # sayacı artır ki kota aşımında loop durabilsin

        self.batch.emails_enriched = found_count
        self.batch.save(update_fields=["emails_enriched", "updated_at"])
        logger.info(
            "Batch %s: Stage 4 complete – %s email found (%s Gemini calls)",
            self.batch.id,
            found_count,
            gemini_calls,
        )

    def run_email_enrichment_stage(self) -> None:
        """
        Standalone email enrichment – pipeline dışından çağrılabilir.
        enrich_emails_task Celery task'ı tarafından kullanılır.
        Batch READY veya PARTIAL durumunda olmalıdır.
        """
        allowed_statuses = ("READY", "PARTIAL", "ENRICHING_EMAILS")
        if self.batch.status not in allowed_statuses:
            logger.warning(
                "Batch %s: run_email_enrichment_stage called on status=%s (beklenen: %s)",
                self.batch.id,
                self.batch.status,
                allowed_statuses,
            )
            return

        items = list(
            BatchItem.objects.filter(
                batch=self.batch,
                is_verified=True,
                has_error=False,
            )
        )
        self._stage_enrich_emails(items)
        logger.info(
            "Batch %s: Standalone email enrichment done. emails_enriched=%s",
            self.batch.id,
            self.batch.emails_enriched,
        )
