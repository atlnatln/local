from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
import functools
from django.conf import settings


from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
import functools
import hashlib
from django.conf import settings


class RegisterRateThrottle(AnonRateThrottle):
    """Kayıt işlemleri için rate throttle - E-posta hash bazlı"""
    scope = 'register'
    
    def allow_request(self, request, view):
        # Test ortamında veya development bypass aktifse throttling'i devre dışı bırak
        if (getattr(settings, 'TESTING', False) or 
            getattr(settings, 'DEBUG', False) or 
            getattr(settings, 'DEVELOPMENT_BYPASS_LIMITS', False)):
            return True
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        """E-posta hash ve IP bazlı cache key oluştur"""
        ident = self.get_ident(request)
        
        # E-posta hash'i al
        email_hash = None
        try:
            email = request.data.get('email', '').strip().lower()
            if email:
                # E-posta adresini SHA256 ile hash'le (privacy için)
                email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
        except Exception:
            email_hash = None
        
        # Test modunda session key ile izolasyon
        session_key = None
        try:
            if getattr(settings, 'TESTING', False) and hasattr(request, 'session'):
                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key
        except Exception:
            session_key = None
        
        # Cache key bileşenleri: IP + E-posta hash + Session (test için)
        key_components = [ident]
        if email_hash:
            key_components.append(email_hash)
        if session_key:
            key_components.append(session_key)
            
        key_ident = "|".join(key_components)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': key_ident
        }


class PasswordResetRateThrottle(AnonRateThrottle):
    """Şifre sıfırlama işlemleri için rate throttle"""
    scope = 'password_reset'
    
    def allow_request(self, request, view):
        # Test ortamında veya development bypass aktifse throttling'i devre dışı bırak
        if (getattr(settings, 'TESTING', False) or 
            getattr(settings, 'DEBUG', False) or 
            getattr(settings, 'DEVELOPMENT_BYPASS_LIMITS', False)):
            return True
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        # IP adresi bazında throttling (+ testlerde session anahtarı ile izole)
        ident = self.get_ident(request)
        session_key = None
        try:
            if getattr(settings, 'TESTING', False) and hasattr(request, 'session'):
                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key
        except Exception:
            session_key = None
        key_ident = f"{ident}|{session_key}" if session_key else ident
        return self.cache_format % {
            'scope': self.scope,
            'ident': key_ident
        }


class EmailVerificationRateThrottle(AnonRateThrottle):
    """Email doğrulama işlemleri için rate throttle"""
    scope = 'email_verification'
    
    def allow_request(self, request, view):
        # Test ortamında veya development bypass aktifse throttling'i devre dışı bırak
        if (getattr(settings, 'TESTING', False) or 
            getattr(settings, 'DEBUG', False) or 
            getattr(settings, 'DEVELOPMENT_BYPASS_LIMITS', False)):
            return True
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        # IP adresi bazında throttling (+ testlerde session anahtarı ile izole)
        ident = self.get_ident(request)
        session_key = None
        try:
            if getattr(settings, 'TESTING', False) and hasattr(request, 'session'):
                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key
        except Exception:
            session_key = None
        key_ident = f"{ident}|{session_key}" if session_key else ident
        return self.cache_format % {
            'scope': self.scope,
            'ident': key_ident
        }


def handle_throttle_exception(view_func):
    """
    Throttle exception'ını yakalar ve 429 hatası için
    Türkçe mesaj ile JSON response döner
    """
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except Throttled as e:
            # Throttle hatasını Türkçe mesajla döndür
            retry_after = getattr(e, 'wait', None)
            return Response({
                'detail': 'Çok fazla istek gönderiyorsunuz. Lütfen bir süre bekleyin.',
                'retry_after': retry_after,
                'error_code': 'RATE_LIMIT_EXCEEDED'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    return wrapper
