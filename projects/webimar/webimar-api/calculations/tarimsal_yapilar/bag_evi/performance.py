# -*- coding: utf-8 -*-
"""
Bağ Evi Performance Monitoring & Caching Layer
Production-grade optimization and monitoring implementation
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import json
import hashlib
import copy

logger = logging.getLogger(__name__)

class BagEviCache:
    """In-memory cache for calculation results with TTL"""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
    
    def _generate_key(self, arazi_bilgileri: Dict, yapi_bilgileri: Dict) -> str:
        """Generate cache key from input parameters"""
        # Create deterministic hash from input data
        data_str = json.dumps(
            {"arazi": arazi_bilgileri, "yapi": yapi_bilgileri}, 
            sort_keys=True,
            default=str
        )
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, arazi_bilgileri: Dict, yapi_bilgileri: Dict) -> Optional[Dict[str, Any]]:
        """Get cached result if valid"""
        key = self._generate_key(arazi_bilgileri, yapi_bilgileri)
        
        if key in self._cache:
            cached_item = self._cache[key]
            if datetime.now() < cached_item['expires_at']:
                logger.debug(f"🎯 Cache HIT for key: {key[:8]}...")
                return cached_item['result']
            else:
                # Expired, remove from cache
                del self._cache[key]
                logger.debug(f"⏰ Cache EXPIRED for key: {key[:8]}...")
        
        logger.debug(f"💭 Cache MISS for key: {key[:8]}...")
        return None
    
    def set(self, arazi_bilgileri: Dict, yapi_bilgileri: Dict, result: Dict[str, Any]) -> None:
        """Cache calculation result"""
        key = self._generate_key(arazi_bilgileri, yapi_bilgileri)
        expires_at = datetime.now() + timedelta(seconds=self._ttl)
        
        self._cache[key] = {
            'result': result,
            'cached_at': datetime.now(),
            'expires_at': expires_at
        }
        
        logger.debug(f"💾 Cached result for key: {key[:8]}... (expires: {expires_at})")
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()
        logger.info("🧹 Cache cleared")
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        now = datetime.now()
        active_items = sum(1 for item in self._cache.values() if now < item['expires_at'])
        
        return {
            'total_items': len(self._cache),
            'active_items': active_items,
            'expired_items': len(self._cache) - active_items
        }

# Global cache instance
_bag_evi_cache = BagEviCache()

def performance_monitor(func: Callable) -> Callable:
    """Performance monitoring decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_memory = 0  # Could add memory monitoring here
        
        try:
            result = func(*args, **kwargs)
            
            # Performance metrics
            execution_time = time.perf_counter() - start_time
            
            # Log performance metrics
            logger.info(
                f"⚡ {func.__name__} executed",
                extra={
                    'execution_time_ms': round(execution_time * 1000, 2),
                    'function_name': func.__name__,
                    'success': True
                }
            )
            
            # Add performance info to result if it's a dict
            if isinstance(result, dict):
                result['_performance'] = {
                    'execution_time_ms': round(execution_time * 1000, 2),
                    'cached': False  # Will be overridden by cache decorator
                }
            
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            logger.error(
                f"❌ {func.__name__} failed",
                extra={
                    'execution_time_ms': round(execution_time * 1000, 2),
                    'function_name': func.__name__,
                    'error': str(e),
                    'success': False
                }
            )
            raise
    
    return wrapper

def cached_calculation(cache_instance: BagEviCache = None) -> Callable:
    """Caching decorator for calculation functions"""
    if cache_instance is None:
        cache_instance = _bag_evi_cache
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(arazi_bilgileri: Dict, yapi_bilgileri: Dict, *args, **kwargs):
            # Augment the dicts used for key generation so that args/kwargs matter
            try:
                # Deepcopy to avoid mutating caller's dicts
                arazi_for_key = copy.deepcopy(arazi_bilgileri) if isinstance(arazi_bilgileri, dict) else {'value': arazi_bilgileri}
                yapi_for_key = copy.deepcopy(yapi_bilgileri) if isinstance(yapi_bilgileri, dict) else {'value': yapi_bilgileri}
                
                # Include args/kwargs in a small normalized form (only for key)
                # Use default=str in JSON to safely serialize unusual values
                meta = {
                    '_args': args,
                    '_kwargs': kwargs
                }
                arazi_for_key['_cache_meta'] = meta
                yapi_for_key['_cache_meta'] = meta
                
            except Exception:
                # Fallback: if deepcopy or augmentation fails, fall back to original dicts
                arazi_for_key = arazi_bilgileri
                yapi_for_key = yapi_bilgileri
            
            # Try to get from cache first (key now includes args/kwargs via _cache_meta)
            cached_result = cache_instance.get(arazi_for_key, yapi_for_key)
            if cached_result is not None:
                # Return a deep copy to avoid external mutation of cached object
                cached_copy = copy.deepcopy(cached_result)
                # Mark as cached in performance metrics
                if isinstance(cached_copy, dict):
                    cached_copy.setdefault('_performance', {})
                    cached_copy['_performance']['cached'] = True
                return cached_copy
            
            # Execute function and cache result
            result = func(arazi_bilgileri, yapi_bilgileri, *args, **kwargs)
            
            # Only cache successful results
            if isinstance(result, dict) and result.get('success', False):
                # store using the same augmented keys
                cache_instance.set(arazi_for_key, yapi_for_key, result)
            
            return result
        
        return wrapper
    return decorator

class PerformanceAnalytics:
    """Analytics collector for performance metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, list] = {
            'execution_times': [],
            'error_counts': [],
            'cache_hits': [],
            'calculation_types': []
        }
    
    def record_execution(self, func_name: str, execution_time_ms: float, success: bool, cached: bool = False):
        """Record function execution metrics"""
        self._metrics['execution_times'].append({
            'timestamp': datetime.now().isoformat(),
            'function': func_name,
            'time_ms': execution_time_ms,
            'success': success,
            'cached': cached
        })
        
        if not success:
            self._metrics['error_counts'].append({
                'timestamp': datetime.now().isoformat(),
                'function': func_name
            })
        
        if cached:
            self._metrics['cache_hits'].append({
                'timestamp': datetime.now().isoformat(),
                'function': func_name
            })
    
    def get_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cutoff_str = cutoff_time.isoformat()
        
        # Filter recent metrics
        recent_executions = [
            m for m in self._metrics['execution_times']
            if m['timestamp'] >= cutoff_str
        ]
        
        recent_errors = [
            m for m in self._metrics['error_counts']
            if m['timestamp'] >= cutoff_str
        ]
        
        recent_cache_hits = [
            m for m in self._metrics['cache_hits']
            if m['timestamp'] >= cutoff_str
        ]
        
        if not recent_executions:
            return {'message': 'No recent executions', 'period_hours': hours_back}
        
        # Calculate statistics
        execution_times = [m['time_ms'] for m in recent_executions]
        
        return {
            'period_hours': hours_back,
            'total_executions': len(recent_executions),
            'successful_executions': len([m for m in recent_executions if m['success']]),
            'failed_executions': len(recent_errors),
            'cache_hits': len(recent_cache_hits),
            'cache_hit_rate': round(len(recent_cache_hits) / len(recent_executions) * 100, 2),
            'avg_execution_time_ms': round(sum(execution_times) / len(execution_times), 2),
            'min_execution_time_ms': min(execution_times),
            'max_execution_time_ms': max(execution_times),
            'error_rate': round(len(recent_errors) / len(recent_executions) * 100, 2)
        }
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        for key in self._metrics:
            self._metrics[key].clear()
        logger.info("📊 Analytics metrics cleared")

# Global analytics instance
_analytics = PerformanceAnalytics()

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return _bag_evi_cache.stats()

def get_performance_summary(hours_back: int = 24) -> Dict[str, Any]:
    """Get performance analytics summary"""
    return _analytics.get_summary(hours_back)

def clear_cache():
    """Clear calculation cache"""
    _bag_evi_cache.clear()

def clear_analytics():
    """Clear performance analytics"""
    _analytics.clear_metrics()
