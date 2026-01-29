import logging
import json
import time
from typing import List, Dict
from django.utils import timezone
from apps.batches.models import Batch, BatchItem
from apps.providers.google_places import GooglePlacesClient
from apps.providers.grid_search import Rectangle

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self, batch_id):
        self.batch = Batch.objects.get(id=batch_id)
        self.client = GooglePlacesClient()

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
            
            # 3. Filter (Stage 2)
            self.batch.status = 'FILTERING'
            self.batch.save()
            
            verified_items = self._stage_filter_details_pro(raw_candidates)
            self.batch.ids_verified = len(verified_items)
            self.batch.skipped_404 = self.batch.error_records # We are tracking errors in stage 2
            self.batch.save()

            if self.batch.status == 'PARTIAL':
                # Aborted in stage 2, stop here
                self.batch.completed_at = timezone.now()
                self.batch.save()
                return

            # 4. Enrich (Stage 3)
            self.batch.status = 'ENRICHING_CONTACTS'
            self.batch.save()
            
            enriched_items = self._stage_enrich_enterprise(verified_items)
            self.batch.contacts_enriched = len([i for i in enriched_items if i.data.get('stage_3_enterprise')])
            
            # 5. Finish
            self.batch.status = 'READY'
            self.batch.completed_at = timezone.now()
            self.batch.processed_records = len(verified_items)
            self.batch.save()
            
        except Exception as e:
            logger.exception(f"Batch {self.batch.id} failed: {e}")
            self.batch.status = 'FAILED'
            self.batch.save()
            
    def _stage_collect_ids(self, include_stage2=False, include_stage3=False):
        """
        Stage 1: Adaptive Quadtree Text Search (Cost-Optimized)
        Goal: Collect pool of IDs with minimal API calls
        
        Args:
            include_stage2: If True, run Stage 2 verification after ID collection
            include_stage3: If True, run Stage 3 enrichment after verification (requires include_stage2=True)
        """
        # Guard: Hard limit maximum records to prevent abuse
        MAX_HARD_LIMIT = 300
        limit = min(self.batch.record_count_estimate or 100, MAX_HARD_LIMIT)
        
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
        
        for item in items:
            try:
                # Guard: Extra check to ensure we don't enrich if previous stages looked fishy
                # or if we hit a unexpected snag (redundant with stage 2 checks but good for future)
                
                details = self.client.get_place_details_enterprise(item.firm_id)
                
                if not details:
                    continue

                # Update item data
                item.data['websiteUri'] = details.get('websiteUri')
                item.data['nationalPhoneNumber'] = details.get('nationalPhoneNumber')
                item.data['stage_3_enterprise'] = True
                
                item.save()
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed Enterprise Details for {item.firm_id}: {e}")
                # We don't abort batch here typically, getting partial contact info is better than none
                
        return items
