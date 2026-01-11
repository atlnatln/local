from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


def custom_exception_handler(exc, context):
    """DRF genel hata yakalayıcısı: Throttled için tutarlı JSON döndürür"""
    # Test ortamında throttle exception'larını yakalama
    if getattr(settings, 'TESTING', False) and isinstance(exc, Throttled):
        return None  # Varsayılan handler'a devret
    
    # Önce DRF'nin varsayılan handler'ını çağır
    response = exception_handler(exc, context)

    # Rate limit aşımlarında özel yanıt
    if isinstance(exc, Throttled):
        wait = getattr(exc, 'wait', None)
        return Response({
            'detail': 'Çok fazla istek gönderiyorsunuz. Lütfen bir süre bekleyin.',
            'retry_after': wait,
            'error_code': 'RATE_LIMIT_EXCEEDED'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Diğer durumlarda varsayılan yanıtı döndür
    return response
