import logging
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from ..middleware import calculation_limit_required, get_client_ip, get_device_fingerprint
from ..models import CalculationLog

logger = logging.getLogger('calculations')

def calculation_exception_handler(func):
    """View fonksiyonları için ortak try/catch/logging decorator'ı."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} hata: {str(e)}")
            
            # Hata logu kaydet
            try:
                ip_address = get_client_ip(request)
                device_fingerprint = get_device_fingerprint(request)
                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                
                CalculationLog.log_calculation(
                    user=user,
                    ip_address=ip_address,
                    calculation_type=func.__name__.replace('calculate_', ''),
                    calculation_data=getattr(request, 'data', {}),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    device_fingerprint=device_fingerprint,
                    is_successful=False,
                    error_message=str(e)
                )
            except Exception as log_error:
                logger.error(f"Error logging calculation error: {log_error}")
            
            return Response({
                'success': False,
                'message': 'Hesaplama işlemi sırasında bir hata oluştu',
                'detail': 'Bir hata oluştu',
                'error': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

def with_calculation_limits(func):
    """
    Hesaplama limitlerini kontrol eden ve logları tutan decorator
    calculation_exception_handler ile birlikte kullanılır
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Önce limit kontrolü
        limit_decorated_func = calculation_limit_required(func)
        return limit_decorated_func(request, *args, **kwargs)
    return wrapper

# Ortak kullanım için kombine decorator
def calculation_view(func):
    """
    Tüm hesaplama view'ları için ortak decorator
    Hem limit kontrolü hem de exception handling yapar
    """
    return calculation_exception_handler(with_calculation_limits(func))
