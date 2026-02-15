import requests
from django.conf import settings
import logging
import time
from requests.exceptions import HTTPError, RequestException

logger = logging.getLogger(__name__)

class GooglePlacesClient:
    BASE_URL = "https://places.googleapis.com/v1"

    def __init__(self, api_key=None):
        # Try both possible env var names for flexibility
        self.api_key = api_key or getattr(settings, 'GOOGLE_PLACES_API_KEY', '') or getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        if not self.api_key:
            logger.warning("GOOGLE_PLACES_API_KEY or GOOGLE_MAPS_API_KEY is not set.")

    def _get_headers(self, field_mask: str, search_text=False):
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "Accept-Language": "tr",  # MD formatına uygun Türkçe lokalizasyon
            "X-Goog-FieldMask": field_mask
        }
        return headers

    def _make_request(self, method, url, headers, json=None, retry_count=3):
        """
        Robust request with retry for 429 (Rate Limit) and 5xx (Server Error).
        """
        for attempt in range(retry_count):
            try:
                if method == 'POST':
                    response = requests.post(url, headers=headers, json=json, timeout=10)
                else:
                    response = requests.get(url, headers=headers, timeout=10)
                
                # Check for 429 specifically
                if response.status_code == 429:
                    wait_time = (2 ** attempt) + 0.5 # Exponential backoff
                    logger.warning(f"Rate limited (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except HTTPError as e:
                # 404 is "Business Logic" failure (Place gone), not system failure.
                if e.response.status_code == 404:
                    logger.info(f"Place not found (404): {url}")
                    return None
                    
                # 403/400 are likely config/quota errors -> Don't retry, fail fast
                if e.response.status_code in (400, 403):
                    logger.error(f"Config Error {e.response.status_code}: {e.response.text}")
                    raise e
                
                # 5xx -> Retry
                if 500 <= e.response.status_code < 600:
                    wait_time = (2 ** attempt) + 0.5
                    logger.warning(f"Server Error {e.response.status_code}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                raise e
            except RequestException as e:
                # Network errors -> Retry
                logger.warning(f"Network Error: {e}. Retrying...")
                time.sleep(1)
                continue
                
        # If we get here, retries exhausted
        raise Exception(f"Max retries exceeded for {url}")

    def text_search_ids_only(self, query: str, page_token: str = None, location_restriction: dict = None, language_code: str = 'tr'):
        """
        Stage 1: Text Search (Free/Low Cost)
        Returns: places.id, places.name
        
        Args:
            query: The text query (e.g. "İzmir'de şehir plancısı")
            page_token: For pagination
            location_restriction: Optional viewport/rect restriction
            language_code: Defaults to 'tr' for better matching in Turkey
        """
        import unicodedata
        
        # Normalize query to NFC to ensure Turkish characters (İ, ı, ş, ğ) are handled correctly
        query = unicodedata.normalize('NFC', query)
        
        url = f"{self.BASE_URL}/places:searchText"
        payload = {
            "textQuery": query,
            "languageCode": language_code, # Explicit localization
            "pageSize": 20, # Explicit page size
        }
        
        if page_token:
            payload["pageToken"] = page_token
            
        if location_restriction:
            payload["locationRestriction"] = location_restriction
            # Note: When locationRestriction is used, textQuery should ideally be categorical 
            # (e.g. "City Planner") rather than including location (e.g. "City Planner in Izmir"),
            # but the API is generally smart enough to handle both.
            
        # Field mask for generic IDs and basic name
        field_mask = "places.id,places.name,nextPageToken"
        
        # Add Accept-Language header as an extra hint
        headers = self._get_headers(field_mask)
        headers["Accept-Language"] = language_code
        
        return self._make_request('POST', url, headers, json=payload)

    def get_place_details_pro(self, place_id: str):
        """
        Stage 2: Place Details Pro (Verification)
        Returns: id, displayName, formattedAddress, types, businessStatus
        
        Pricing: Pro tier (mid-cost)
        Purpose: Verify business is OPERATIONAL and in correct category
        """
        url = f"{self.BASE_URL}/places/{place_id}"
        # Stage 2 field mask - verification fields
        field_mask = "id,displayName,formattedAddress,types,businessStatus"
        
        return self._make_request('GET', url, self._get_headers(field_mask))

    def get_place_details_enterprise(self, place_id: str):
        """
        Stage 3: Place Details Enterprise (Contact Data)
        Returns: websiteUri, nationalPhoneNumber
        """
        url = f"{self.BASE_URL}/places/{place_id}"
        field_mask = "websiteUri,nationalPhoneNumber"
        
        return self._make_request('GET', url, self._get_headers(field_mask))
