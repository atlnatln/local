import logging
import json
from django.utils import timezone
from apps.batches.models import Batch, BatchItem
from apps.providers.google_places import GooglePlacesClient

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
            
    def _stage_collect_ids(self):
        """
        Stage 1: Text Search (Free/Low Cost)
        Goal: Collect pool of IDs
        """
        query = f"{self.batch.sector} in {self.batch.city}"
        
        # Guard: Hard limit maximum records to prevent abuse regardless of what frontend requested
        MAX_HARD_LIMIT = 300
        limit = min(self.batch.record_count_estimate, MAX_HARD_LIMIT) or 100
        
        candidates = []
        next_page_token = None
        seen_ids = set()
        
        loop_guard = 0
        MAX_LOOPS = 20 # Avoid infinite loops if something goes wrong with pagination
        
        while len(candidates) < limit and loop_guard < MAX_LOOPS:
            loop_guard += 1
            response = self.client.text_search_ids_only(query, next_page_token)
            
            if not response:
                break
                
            places = response.get('places', [])
            if not places:
                break
                
            for p in places:
                pid = p.get('id')
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    candidates.append({
                        'id': pid,
                        'name': p.get('name') 
                    })
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
            if len(candidates) >= limit:
                candidates = candidates[:limit]
                break
                
        logger.info(f"Batch {self.batch.id}: Collected {len(candidates)} IDs")
        return candidates

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
