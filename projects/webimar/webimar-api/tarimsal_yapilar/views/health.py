from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def health_check(request):
    """
    API health check endpoint for monitoring and load balancer.
    Used by nginx, Docker health checks, and monitoring systems.
    """
    try:
        # Basic response data
        response_data = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "service": "webimar-api",
            "version": "2.1.0"
        }
        
        # Additional health checks in DEBUG mode
        if settings.DEBUG:
            from django.db import connection
            try:
                # Test database connectivity
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                response_data["database"] = "connected"
            except Exception as e:
                response_data["database"] = f"error: {str(e)}"
                
            # Test cache if available
            try:
                from django.core.cache import cache
                cache.set('health_check', 'ok', timeout=10)
                if cache.get('health_check') == 'ok':
                    response_data["cache"] = "connected"
                else:
                    response_data["cache"] = "not working"
            except Exception as e:
                response_data["cache"] = f"error: {str(e)}"
        
        return HttpResponse(
            json.dumps(response_data, indent=2),
            content_type='application/json',
            status=200
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        error_response = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": timezone.now().isoformat(),
            "service": "webimar-api"
        }
        return HttpResponse(
            json.dumps(error_response, indent=2),
            content_type='application/json',
            status=500
        )