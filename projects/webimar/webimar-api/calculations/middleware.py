"""
Hesaplama limit kontrolü için middleware ve decoratorlar
"""
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .models import DailyCalculationLimit, CalculationLog
import hashlib
import json
import logging

logger = logging.getLogger('calculations')

def get_client_ip(request):
    """İstek yapan IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_device_fingerprint(request):
    """Cihaz parmak izi oluştur"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    
    # Basit parmak izi oluşturma
    fingerprint_data = f"{user_agent}:{accept_language}:{accept_encoding}"
    return hashlib.md5(fingerprint_data.encode('utf-8')).hexdigest()[:16]

def check_calculation_limit(user=None, ip_address=None, device_fingerprint=None):
    """
    Hesaplama limitini kontrol et
    Returns: (allowed: bool, limit_obj: DailyCalculationLimit, message: str)
    """
    # Geliştirme ortamında limit bypass
    if getattr(settings, 'DEVELOPMENT_BYPASS_LIMITS', False):
        logger.info("Development mode - bypassing calculation limits")
        return True, None, "Development mode - limits bypassed"
    
    # Süper kullanıcı bypass - admin ve superuser'lar için limit yok
    if user and user.is_authenticated and (user.is_superuser or user.is_staff):
        logger.info(f"Superuser/Staff bypass - user: {user.username} (superuser: {user.is_superuser}, staff: {user.is_staff})")
        return True, None, "Superuser/Staff - limits bypassed"
    
    try:
        # Limit objesi al veya oluştur
        limit_obj, created = DailyCalculationLimit.get_or_create_limit(
            user=user,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint
        )
        
        # Limit kontrolü
        if limit_obj.is_limit_reached:
            # Limit dolmuş - uygun mesajı döndür
            if user and user.is_authenticated and user.is_active:
                message = "Bugünlük işlem hakkınız doldu, daha fazla işlem için iletişime geçin"
                limit_type = "registered"
            else:
                message = "Daha fazla işlem için üye olun, bugünlük limitiniz doldu"
                limit_type = "anonymous"
                
            logger.warning(f"Calculation limit exceeded - {limit_type}: {limit_obj}")
            return False, limit_obj, message
        
        # Limit uygun
        logger.info(f"Calculation limit OK - Remaining: {limit_obj.remaining_calculations}")
        return True, limit_obj, ""
        
    except Exception as e:
        logger.error(f"Limit control error: {e}")
        # Hata durumunda izin ver ama logla
        return True, None, ""

def increment_calculation_count(user=None, ip_address=None, device_fingerprint=None):
    """Hesaplama sayısını artır"""
    try:
        limit_obj, created = DailyCalculationLimit.get_or_create_limit(
            user=user,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint
        )
        limit_obj.increment_count()
        return limit_obj
    except Exception as e:
        logger.error(f"Error incrementing calculation count: {e}")
        return None

def calculation_limit_required(view_func):
    """
    Hesaplama limit kontrolü decorator'u
    Bu decorator, hesaplama endpoint'lerine eklenir
    DRF Request ve Django HttpRequest uyumlu
    """
    def wrapper(request, *args, **kwargs):
        try:
            logger.info(f"🧮 Calculation limit check for: {view_func.__name__}")
            
            # DRF Request → Django HttpRequest conversion
            django_request = getattr(request, '_request', request)
            
            # Development bypass kontrolü - en başta yap
            if (getattr(settings, 'DEVELOPMENT_BYPASS_LIMITS', False) or
                getattr(settings, 'DEBUG', False) or  
                getattr(settings, 'TESTING', False)):
                logger.info("🚀 Development mode - bypassing all limits")
                response = view_func(request, *args, **kwargs)
                
                # Development response'ına mock limit bilgileri ekle
                if hasattr(response, 'data') and isinstance(response.data, dict):
                    response.data['calculation_limits'] = {
                        'user_type': 'development',
                        'daily_limit': 999,
                        'used_calculations': 0,
                        'remaining_calculations': 999
                    }
                
                return response
            
            # İstek bilgilerini al - Django request kullan
            ip_address = get_client_ip(django_request)
            device_fingerprint = get_device_fingerprint(django_request)
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            user_agent = django_request.META.get('HTTP_USER_AGENT', '')
            
            logger.info(f"📊 Request info - IP: {ip_address}, User: {user}, Device: {device_fingerprint[:8]}...")
            
            # Limit kontrolü
            allowed, limit_obj, error_message = check_calculation_limit(
                user=user,
                ip_address=ip_address,
                device_fingerprint=device_fingerprint
            )
            
            logger.info(f"🔍 Limit check result - Allowed: {allowed}, Limit obj: {limit_obj}")
            
            if not allowed:
                logger.warning(f"🚫 Limit exceeded for {user or ip_address}")
                # Limit aşımı logla
                CalculationLog.log_calculation(
                    user=user,
                    ip_address=ip_address,
                    calculation_type=view_func.__name__.replace('calculate_', ''),
                    calculation_data=getattr(request, 'data', {}),
                    user_agent=user_agent,
                    device_fingerprint=device_fingerprint,
                    is_successful=False,
                    limit_exceeded=True,
                    current_count=limit_obj.calculation_count if limit_obj else 0,
                    current_limit=limit_obj.current_limit if limit_obj else 0,
                    error_message="Daily calculation limit exceeded"
                )
                
                # Limit aşımı yanıtı
                response_data = {
                    'success': False,
                    'limit_exceeded': True,
                    'message': error_message,
                    'user_type': 'registered' if (user and user.is_authenticated) else 'anonymous',
                    'daily_limit': limit_obj.current_limit if limit_obj else 0,
                    'used_calculations': limit_obj.calculation_count if limit_obj else 0,
                    'remaining_calculations': 0
                }
                
                return JsonResponse(response_data, status=429)  # Too Many Requests
            
            # Limit uygun - hesaplama sayısını artır
            limit_obj = increment_calculation_count(
                user=user,
                ip_address=ip_address,
                device_fingerprint=device_fingerprint
            )
            
            logger.info(f"✅ Limit incremented - New count: {limit_obj.calculation_count if limit_obj else 'Unknown'}")
            
            # Orijinal view'i çalıştır
            response = view_func(request, *args, **kwargs)
            
            # Başarılı hesaplama logla
            if hasattr(response, 'data') and response.status_code == 200:
                calculation_type = view_func.__name__.replace('calculate_', '')
                
                CalculationLog.log_calculation(
                    user=user,
                    ip_address=ip_address,
                    calculation_type=calculation_type,
                    calculation_data=getattr(request, 'data', {}),
                    result_data=response.data if hasattr(response, 'data') else {},
                    user_agent=user_agent,
                    device_fingerprint=device_fingerprint,
                    is_successful=True,
                    limit_exceeded=False,
                    current_count=limit_obj.calculation_count if limit_obj else 0,
                    current_limit=limit_obj.current_limit if limit_obj else 0
                )
                
                logger.info(f"📋 Calculation logged successfully")
                
                # Response'a limit bilgilerini ekle
                if hasattr(response, 'data') and isinstance(response.data, dict):
                    response.data['calculation_limits'] = {
                        'user_type': 'registered' if (user and user.is_authenticated) else 'anonymous',
                        'daily_limit': limit_obj.current_limit if limit_obj else 0,
                        'used_calculations': limit_obj.calculation_count if limit_obj else 0,
                        'remaining_calculations': limit_obj.remaining_calculations if limit_obj else 0
                    }
            
            return response
            
        except Exception as e:
            logger.exception(f"❌ Calculation limit decorator error: {e}")
            # Hata durumunda normal hesaplamaya devam et
            return view_func(request, *args, **kwargs)
    
    return wrapper

class CalculationLimitMiddleware:
    """
    Hesaplama limit kontrolü middleware'i
    Bu middleware, tüm hesaplama endpoint'lerini otomatik izler
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # İsteği işle
        response = self.get_response(request)
        
        # Hesaplama endpoint'i mi kontrol et
        if (request.method == 'POST' and 
            '/api/calculations/' in request.path and 
            'calculate' in request.path):
            
            # DRF Request → Django HttpRequest conversion
            django_request = getattr(request, '_request', request)
            
            # Başlık bilgilerini ekle
            if hasattr(response, 'data'):
                ip_address = get_client_ip(django_request)
                device_fingerprint = get_device_fingerprint(django_request)
                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                
                # Mevcut limit durumunu al
                try:
                    limit_obj, _ = DailyCalculationLimit.get_or_create_limit(
                        user=user,
                        ip_address=ip_address,
                        device_fingerprint=device_fingerprint
                    )
                    
                    # Response header'larına limit bilgilerini ekle
                    response['X-Daily-Limit'] = str(limit_obj.current_limit)
                    response['X-Used-Calculations'] = str(limit_obj.calculation_count)
                    response['X-Remaining-Calculations'] = str(limit_obj.remaining_calculations)
                    response['X-User-Type'] = limit_obj.user_type
                    
                except Exception as e:
                    logger.error(f"Middleware limit info error: {e}")
        
        return response
