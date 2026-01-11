# Rate limiting ve güvenlik middleware'leri

from django.http import JsonResponse
from django.core.cache import cache
import time
import logging

logger = logging.getLogger(__name__)

class SecurityLoggingMiddleware:
    """
    Güvenlik olaylarını loglama middleware'i - Rate limiting yapmaz (throttle ile çakışma önlenir)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sadece güvenlik loglaması yap, rate limit uygulamaz  
        self.log_security_events(request)
        
        response = self.get_response(request)
        return response

    def log_security_events(self, request):
        """Güvenlik olaylarını logla"""
        # API isteklerini logla
        if request.path.startswith('/api/'):
            ip = self.get_client_ip(request)
            
            # Hassas endpoint'lerde extra loglama
            if any(path in request.path for path in [
                '/api/accounts/register/',
                '/api/accounts/change-password/', 
                '/api/accounts/me/delete-account/',
                '/api/token/'
            ]):
                logger.info(f"API REQUEST: {request.method} {request.path} from IP {ip}")

    def is_rate_limited(self, request):
        """Rate limiting devre dışı - throttle kullanılıyor"""
        return False  # Middleware rate limiting yapmaz, sadece throttle kullanılır
        """Rate limiting kontrolü"""
        # API istekleri için rate limiting
        if not request.path.startswith('/api/'):
            return False
            
        # IP adresini al
        ip = self.get_client_ip(request)
        
        # Farklı endpoint'ler için farklı limitler
        if '/api/accounts/register/' in request.path:
            # Kayıt için: 50 istek / 10 dakika (development için daha gevşek)
            return self.check_rate_limit(ip, 'register', 50, 600)
        elif '/api/accounts/change-password/' in request.path:
            # Şifre değiştirme için: 5 istek / 10 dakika  
            return self.check_rate_limit(ip, 'change_password', 5, 600)
        elif '/api/accounts/me/delete-account/' in request.path:
            # Hesap silme için: 2 istek / 30 dakika
            return self.check_rate_limit(ip, 'delete_account', 2, 1800)
        elif request.method == 'POST':
            # /api/token/ endpointini POST limiti dışında bırak
            if '/api/token/' in request.path:
                return False
            # Diğer POST istekleri için: 30 istek / 5 dakika
            return self.check_rate_limit(ip, 'post_requests', 30, 300)
        else:
            # Genel API istekleri için: 100 istek / 5 dakika
            return self.check_rate_limit(ip, 'api_requests', 100, 300)

    def check_rate_limit(self, ip, action, limit, window):
        """Rate limit kontrolü"""
        cache_key = f"rate_limit:{ip}:{action}"
        current_requests = cache.get(cache_key, [])
        now = time.time()
        
        # Eski istekleri temizle
        current_requests = [req_time for req_time in current_requests if now - req_time < window]
        
        # Limit kontrolü
        if len(current_requests) >= limit:
            return True
        
        # Yeni isteği ekle
        current_requests.append(now)
        cache.set(cache_key, current_requests, window)
        
        return False

    def get_client_ip(self, request):
        """İstemci IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Güvenlik başlıkları middleware'i
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Güvenlik başlıkları ekle
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HTTPS zorunlu kılma (production için)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RequestLoggingMiddleware:
    """
    İstek loglama middleware'i
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # İstek bilgilerini logla
        logger.info(f"Request: {request.method} {request.path} from {self.get_client_ip(request)}")
        
        response = self.get_response(request)
        
        # Yanıt süresini hesapla ve logla
        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {duration:.2f}s")
        
        return response

    def get_client_ip(self, request):
        """İstemci IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class InputSanitizationMiddleware:
    """
    Girdi temizleme middleware'i - XSS koruması
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # POST verilerini temizle
        # request.POST asla override edilmemeli! Sadece okuma sırasında sanitize edin.
        
        # JSON verilerini temizle
        if hasattr(request, 'body') and request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body.decode('utf-8'))
                sanitized_data = self.sanitize_data(data)
                request._body = json.dumps(sanitized_data).encode('utf-8')
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        response = self.get_response(request)
        return response

    def sanitize_data(self, data):
        """Veriyi temizle"""
        import html
        
        if isinstance(data, dict):
            return {key: self.sanitize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # HTML karakterlerini escape et
            return html.escape(data.strip())
        else:
            return data
