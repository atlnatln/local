import json
import logging
import time
from typing import Any

from django.conf import settings

from accounts.models import TrackedApiCall

logger = logging.getLogger(__name__)


_SENSITIVE_KEYS = {
    'password',
    'token',
    'access',
    'refresh',
    'secret',
    'client_secret',
    'authorization',
}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if str(key).lower() in _SENSITIVE_KEYS:
                redacted[key] = '[REDACTED]'
            else:
                redacted[key] = _redact(item)
        return redacted

    if isinstance(value, list):
        return [_redact(item) for item in value]

    return value


def _safe_json_loads(raw: bytes) -> Any | None:
    if not raw:
        return None

    try:
        return json.loads(raw.decode('utf-8'))
    except Exception:
        return None


def _get_client_ip(request) -> str | None:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()

    return request.META.get('REMOTE_ADDR')


def _extract_calculation_type(path: str, request_json: Any | None) -> str | None:
    # /api/calculations/{slug}/... gibi rotalarda slug'ı yakala
    if path.startswith('/api/calculations/'):
        parts = [p for p in path.split('/') if p]
        # parts: ['api','calculations','{slug}', ...]
        if len(parts) >= 3:
            slug = parts[2]

            # Calculation olmayan endpoint'leri dışarıda bırak
            non_calc_slugs = {
                'health',
                'arazi-tipleri',
                'yapi-turleri',
                'history',
                'save',
                'detail',
                'delete',
                'static',
            }
            if slug in non_calc_slugs:
                return None

            # Canonical mapping (örn: bag-evi-v2 -> bag-evi)
            if slug.endswith('-v2'):
                return slug[:-3]

            return slug

    if isinstance(request_json, dict):
        # Bazı eski/karma mapping'lerde yapı türü farklı key'lerde gelebilir
        for key in ('yapi_turu', 'calculation_type', 'structure_type'):
            value = request_json.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def _extract_dimensions(
    request_json: Any | None,
    query_params: dict[str, Any] | None,
    response_json: Any | None,
) -> dict[str, Any] | None:
    dims: dict[str, Any] = {}

    def take(obj: dict[str, Any], keys: tuple[str, ...], out_key: str) -> None:
        for key in keys:
            value = obj.get(key)
            if value is not None and value != '':
                dims[out_key] = value
                return

    if isinstance(query_params, dict):
        take(query_params, ('il', 'city'), 'il')
        take(query_params, ('ilce', 'district'), 'ilce')
        take(query_params, ('mahalle', 'neighborhood'), 'mahalle')
        take(query_params, ('yapi_turu', 'calculation_type'), 'yapi_turu')
        take(query_params, ('latitude', 'lat'), 'latitude')
        take(query_params, ('longitude', 'lng', 'lon'), 'longitude')

    if isinstance(request_json, dict):
        take(request_json, ('il', 'city'), 'il')
        take(request_json, ('ilce', 'district'), 'ilce')
        take(request_json, ('mahalle', 'neighborhood'), 'mahalle')
        take(request_json, ('yapi_turu', 'calculation_type'), 'yapi_turu')
        take(request_json, ('latitude', 'lat'), 'latitude')
        take(request_json, ('longitude', 'lng', 'lon'), 'longitude')

    # Hesaplama endpoint'leri çoğunlukla location_info döndürüyor.
    # Bu alanlar request'te yoksa response'tan tamamlayalım.
    location_info: Any | None = None
    if isinstance(response_json, dict):
        # Tipik format: { success: true, results: { ..., location_info: {...} } }
        results = response_json.get('results')
        if isinstance(results, dict) and isinstance(results.get('location_info'), dict):
            location_info = results.get('location_info')
        # Bazı endpoint'ler doğrudan root seviyede döndürebilir
        if location_info is None and isinstance(response_json.get('location_info'), dict):
            location_info = response_json.get('location_info')

    if isinstance(location_info, dict):
        # location_utils.check_location_status çıktısı: province/district/buyuk_ova_icinde...
        take(location_info, ('province',), 'il')
        take(location_info, ('district',), 'ilce')
        take(location_info, ('buyuk_ova_icinde',), 'buyuk_ova_icinde')
        take(location_info, ('buyuk_ova_adi',), 'buyuk_ova_adi')
        take(location_info, ('yas_kapali_icinde',), 'yas_kapali_icinde')
        take(location_info, ('yas_kapali_adi',), 'yas_kapali_adi')

        coords = location_info.get('coordinates')
        if isinstance(coords, dict):
            take(coords, ('latitude',), 'latitude')
            take(coords, ('longitude',), 'longitude')

    # Bazı hesaplama endpoint'leri response içine location_info koymuyor.
    # Bu durumda tracking tarafında koordinattan il/ilçe/büyükova/yas bilgilerini tamamlayalım.
    lat_raw = dims.get('latitude')
    lon_raw = dims.get('longitude')
    needs_location_enrichment = any(
        key not in dims
        for key in (
            'il',
            'ilce',
            'buyuk_ova_icinde',
            'buyuk_ova_adi',
            'yas_kapali_icinde',
            'yas_kapali_adi',
        )
    )

    if lat_raw is not None and lon_raw is not None and needs_location_enrichment:
        try:
            lat = float(lat_raw)
            lon = float(lon_raw)
        except Exception:
            lat = None
            lon = None

        if lat is not None and lon is not None:
            try:
                from calculations.utils.location_utils import check_location_status, validate_coordinates

                is_valid, _msg = validate_coordinates(lat, lon)
                if is_valid:
                    location_status = check_location_status(lat, lon)
                    if isinstance(location_status, dict):
                        take(location_status, ('province',), 'il')
                        take(location_status, ('district',), 'ilce')
                        take(location_status, ('buyuk_ova_icinde',), 'buyuk_ova_icinde')
                        take(location_status, ('buyuk_ova_adi',), 'buyuk_ova_adi')
                        take(location_status, ('yas_kapali_icinde',), 'yas_kapali_icinde')
                        take(location_status, ('yas_kapali_adi',), 'yas_kapali_adi')
            except Exception:
                # Tracking asla ana request'i bozmamalı
                logger.exception('ApiRequestTrackingMiddleware lokasyon enrichment hatası')

    return dims or None


class ApiRequestTrackingMiddleware:
    """/api/* isteklerini DB'ye yazar.

    Notlar:
    - Hassas endpoint'lerde body/response kaydı yapılmaz.
    - Kayıt başarısız olursa request akışı bozulmaz.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, 'TRACKING_ENABLED', True):
            return self.get_response(request)

        path = getattr(request, 'path', '') or ''
        if not path.startswith('/api/'):
            return self.get_response(request)

        if path.startswith('/api/calculations/health/') or path.startswith('/api/accounts/health/'):
            return self.get_response(request)

        start = time.monotonic()

        method = (getattr(request, 'method', '') or '').upper()
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT')

        session_id = request.META.get('HTTP_X_WEBIMAR_SESSION_ID') or request.META.get('HTTP_X_SESSION_ID')
        if isinstance(session_id, str):
            session_id = session_id.strip() or None

        query_params: dict[str, Any] | None = None
        if hasattr(request, 'GET'):
            query_params = dict(request.GET.items()) or None

        should_log_body = method in {'POST', 'PUT', 'PATCH'}
        is_sensitive_path = (
            path.startswith('/api/token/')
            or path.startswith('/api/accounts/google/')
            or path.startswith('/api/accounts/me/')
        )

        request_json: Any | None = None
        if should_log_body and not is_sensitive_path:
            raw_body = b''
            try:
                raw_body = request.body  # Django caches body after first access
            except Exception:
                raw_body = b''

            # Çok büyük body'leri hiç loglamayalım
            max_bytes = getattr(settings, 'TRACKING_MAX_BODY_BYTES', 64 * 1024)
            if raw_body and len(raw_body) <= max_bytes:
                request_json = _safe_json_loads(raw_body)

        response = None
        exc: Exception | None = None
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            exc = e
            raise
        finally:
            try:
                duration_ms = int((time.monotonic() - start) * 1000)

                response_status = 500
                response_json: Any | None = None

                if response is not None:
                    response_status = getattr(response, 'status_code', 500)

                    should_log_response = (
                        getattr(settings, 'TRACKING_LOG_RESPONSE_BODY', True)
                        and path.startswith('/api/calculations/')
                        and not is_sensitive_path
                    )

                    if should_log_response:
                        content_type = (response.get('Content-Type') or '').lower() if hasattr(response, 'get') else ''
                        if 'application/json' in content_type:
                            raw = getattr(response, 'content', b'') or b''
                            max_bytes = getattr(settings, 'TRACKING_MAX_BODY_BYTES', 64 * 1024)
                            if raw and len(raw) <= max_bytes:
                                response_json = _safe_json_loads(raw)

                safe_request_json = _redact(request_json) if request_json is not None else None
                safe_query_params = _redact(query_params) if query_params is not None else None
                safe_response_json = _redact(response_json) if response_json is not None else None

                calculation_type = _extract_calculation_type(path, safe_request_json)
                dimensions = _extract_dimensions(safe_request_json, safe_query_params, safe_response_json)

                TrackedApiCall.objects.create(
                    user=getattr(request, 'user', None) if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False) else None,
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    method=method,
                    path=(path or '')[:512],
                    query_params=safe_query_params,
                    request_body=safe_request_json,
                    response_status=response_status,
                    response_body=safe_response_json,
                    duration_ms=duration_ms,
                    calculation_type=calculation_type,
                    dimensions=dimensions,
                )
            except Exception:
                # Loglama asla ana request'i bozmasın
                logger.exception('ApiRequestTrackingMiddleware loglama hatası')
