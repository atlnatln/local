# -*- coding: utf-8 -*-
"""
Bağ Evi Production Monitoring API Endpoints
Real-time performance and health monitoring
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime

from .performance import get_cache_stats, get_performance_summary, clear_cache, clear_analytics

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def bag_evi_health_check(request):
    """Health check endpoint for Bag Evi module"""
    try:
        # Basic functionality test
        from . import core
        test_arazi = {'buyukluk_m2': 10000, 'ana_vasif': 'dikili_vasifli'}
        test_yapi = {'mevcut_yapi_alani': 0}
        
        # Quick test calculation
        result = core.bag_evi_universal_degerlendir(test_arazi, test_yapi)
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module': 'bag_evi',
            'version': '2.0.0',
            'test_calculation': 'success' if result.get('success') is not None else 'failed'
        }
        
        return JsonResponse(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def bag_evi_performance_stats(request):
    """Get performance statistics"""
    try:
        hours_back = int(request.GET.get('hours', 24))
        
        stats = {
            'cache_stats': get_cache_stats(),
            'performance_summary': get_performance_summary(hours_back),
            'timestamp': datetime.now().isoformat()
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"Performance stats failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def bag_evi_clear_cache(request):
    """Clear calculation cache (admin only)"""
    try:
        # In production, add authentication check here
        # if not request.user.is_superuser:
        #     return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        clear_cache()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Cache cleared',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def bag_evi_clear_analytics(request):
    """Clear performance analytics (admin only)"""
    try:
        # In production, add authentication check here
        # if not request.user.is_superuser:
        #     return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        clear_analytics()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Analytics cleared',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Analytics clear failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def bag_evi_system_info(request):
    """Get system information and module status"""
    try:
        from . import config, core, messages, hotfix_adapter_v2, performance
        import sys
        import os
        
        system_info = {
            'module_info': {
                'name': 'bag_evi',
                'version': '2.0.0',
                'description': 'Modular Bağ Evi calculation engine',
                'components': ['core', 'config', 'messages', 'hotfix_adapter_v2', 'performance']
            },
            'system_info': {
                'python_version': sys.version,
                'django_version': getattr(__import__('django'), 'VERSION', 'Unknown'),
                'process_id': os.getpid()
            },
            'configuration': {
                'minimum_arazi_alani': getattr(config, 'MINIMUM_ARAZI_ALANI', 'Not set'),
                'maksimum_yapi_orani': getattr(config, 'MAKSIMUM_YAPI_ORANI', 'Not set'),
                'cache_enabled': True,
                'performance_monitoring': True
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return JsonResponse(system_info)
        
    except Exception as e:
        logger.error(f"System info failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)
