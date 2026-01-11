"""Custom middleware for webimar_api project."""

from django.http import HttpResponse
from django.core.exceptions import DisallowedHost
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class InternalHostMiddleware(MiddlewareMixin):
    """
    Internal nginx upstream/container hostname'lerini handle eder.
    
    Bazı durumlarda nginx upstream name (api_backend) veya container name 
    (webimar-nginx) HTTP_HOST olarak gelebilir. Bunlar RFC 1034/1035'e uymaz 
    (underscore içeriyor) ve Django DisallowedHost hatası verir.
    
    Bu middleware:
    1. Bilinen internal hostname'leri yakalar
    2. Host header'ı webimar-api'ye yazar (geçerli internal host)
    3. Normal akışa devam eder
    """
    
    INTERNAL_HOSTS = {
        'api_backend',      # Nginx upstream name (underscore - invalid)
        'webimar-nginx',    # Nginx container hostname
    }
    
    def process_request(self, request):
        """Request işlenmeden önce Host header'ı düzelt."""
        try:
            host = request.META.get('HTTP_HOST', '')
            
            # Internal hostname kontrolü
            if host in self.INTERNAL_HOSTS:
                # webimar-api'ye yönlendir (geçerli internal host)
                request.META['HTTP_HOST'] = 'webimar-api'
                logger.debug(f"Internal host '{host}' -> 'webimar-api' olarak düzeltildi")
        except Exception as e:
            # Middleware hatası ana akışı bozmamalı
            logger.warning(f"InternalHostMiddleware hatası: {e}")
        
        return None  # Normal akışa devam
