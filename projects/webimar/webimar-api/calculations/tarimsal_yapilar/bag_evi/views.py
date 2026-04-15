# -*- coding: utf-8 -*-
"""
Ayrılmış Bağ Evi View Modülü
Tesisler.py'den ayrıştırılan, tek sorumluluklu ve test edilebilir bağ evi hesaplama endpoint'i.

Bu modül:
- Koordinat kontrolü yapar
- Input normalizasyonu sağlar  
- Core hesaplama çağrısı (unified adapter veya hotfix adapter)
- Response sanitization ve unescape işlemleri
- Backwards compatibility için eski contract'ı korunur
"""

import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

# Import utilities
from calculations.utils.location_utils import (
    check_location_status, 
    validate_coordinates, 
    format_buyuk_ova_message
)
from calculations.utils.response_utils import sanitize_bag_evi_result
from calculations.views.base import calculation_view
from calculations.views.utils import standard_error_response, unescape_result_html_fields

# Import core adapters
from .hotfix_adapter_v2 import calculate_bag_evi_fixed
from . import unified_adapter

logger = logging.getLogger('calculations.bag_evi')

def _calculate_bag_evi_view_impl(request):
    """
    Bağ evi hesaplamasının dekoratörsüz implementasyonu.

    Not: Bu fonksiyon DRF Request bekler ve Response döner.
    Hem legacy wrapper hem de v2 endpoint aynı implementasyonu kullanır.
    
    Bu implementasyon tesisler.py'den ayrıştırılmış, modüler ve test edilebilir yapıda:
    - Input normalize
    - Location kontrolü  
    - Core hesaplama (unified adapter veya hotfix adapter)
    - Sanitize & unescape
    - Response formatting
    
    Args:
        request: DRF request object containing bag evi calculation parameters
        
    Returns:
        Response: JSON response with calculation results
    """
    logger.info("📋 Bağ evi hesaplama view - ayrılmış modül")
    
    # 1) Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        # Koordinat geçerliliği kontrol et
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        
        # Lokasyon durumunu kontrol et
        location_info = check_location_status(float(latitude), float(longitude))
        if not location_info.get('location_valid', True):
            return standard_error_response(location_info.get('location_message', 'Konum geçersiz'))

    # 2) Payload normalize (lightweight - unified_adapter yapacak heavy mapping)
    request_data = dict(request.data)  # shallow copy for safety
    
    try:
        # 3) Core calculation - unified adapter preferred, hotfix fallback
        core_result = _execute_core_calculation(request_data)
        
        # 4) Response processing
        processed_result = _process_calculation_result(core_result, request, location_info)
        
        # Success field'ını izin_durumu'na göre belirle
        success = False
        if processed_result.get('izin_durumu') in ['izin_verilebilir_varsayimsal', 'izin_verilebilir_manuel']:
            success = True
        
        # Eğer success false ise data alanını temizle - frontend karışıklığını önle
        if not success:
            # Sadece temel bilgileri tut, detayları temizle
            processed_result = {
                'izin_durumu': processed_result.get('izin_durumu', 'izin_verilemez'),
                'mesaj': processed_result.get('mesaj', 'Hesaplama başarısız oldu'),
                'ana_mesaj': processed_result.get('ana_mesaj', 'Hesaplama başarısız oldu'),
                'detay_mesaji': processed_result.get('detay_mesaji', 'Hesaplama başarısız oldu'),
                'location_info': processed_result.get('location_info'),
                'buyuk_ova_mesaji': processed_result.get('buyuk_ova_mesaji')
            }
        
        return Response({
            'success': success,
            'results': processed_result,
            'message': 'Bağ evi hesaplama başarıyla tamamlandı'
        })
        
    except Exception as exc:
        logger.exception("❌ Bağ evi hesaplama sırasında hata oluştu")
        return standard_error_response(str(exc))


@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_bag_evi_view(request):
    """Yeni ayrılmış Bağ Evi endpoint (v2)."""
    return _calculate_bag_evi_view_impl(request)

def _execute_core_calculation(request_data: dict) -> dict:
    """
    Execute core calculation using unified or hotfix adapter
    
    Args:
        request_data: Normalized request data
        
    Returns:
        dict: Core calculation results
    """
    try:
        # Try unified adapter first (preferred method)
        logger.info("🎯 Unified adapter kullanılıyor...")
        core_result = unified_adapter.bag_evi_unified_calculate(
            request_data, 
            legacy_format=False
        )
        logger.info("✅ Unified adapter başarılı")
        return core_result
        
    except Exception as e:
        logger.warning("⚠️ Unified adapter başarısız, hotfix adapter'e geçiliyor: %s", e)
        
        # Fallback to hotfix adapter with normalized data
        arazi_bilgileri, yapi_bilgileri = _normalize_for_hotfix_adapter(request_data)
        
        core_result = calculate_bag_evi_fixed(
            arazi_bilgileri, 
            yapi_bilgileri,
            bag_evi_var_mi=request_data.get('bag_evi_var_mi', False),
            manuel_kontrol_sonucu=request_data.get('manuel_kontrol_sonucu')
        )
        logger.info("✅ Hotfix adapter başarılı - fallback tamamlandı")
        return core_result

def _normalize_for_hotfix_adapter(request_data: dict) -> tuple:
    """
    Normalize request data for hotfix adapter format
    
    Args:
        request_data: Raw request data
        
    Returns:
        tuple: (arazi_bilgileri, yapi_bilgileri) normalized for hotfix adapter
    """
    # Temel parametreler - eski tesisler.py logic'ini koruyoruz
    alan_m2 = request_data.get('alan_m2') or request_data.get('buyukluk_m2', 0)
    arazi_tipi = request_data.get('arazi_vasfi') or request_data.get('arazi_tipi', 'Dikili vasıflı')
    dikili_alani = request_data.get('dikili_alani', 0)
    tarla_alani = request_data.get('tarla_alani', 0)
    
    # Arazi vasfına göre alan mapping'i - tesisler.py'den aynen alındı  
    if arazi_tipi == "Bağ vasfı":
        dikili_alan_degeri = float(alan_m2)
    elif arazi_tipi == "Dikili vasıflı":
        dikili_alan_degeri = float(alan_m2)
    elif arazi_tipi == "Tarla":
        dikili_alan_degeri = 0
    elif arazi_tipi == "Tarla + herhangi bir dikili vasıflı":
        dikili_alan_degeri = float(dikili_alani) if dikili_alani else 0
    else:
        dikili_alan_degeri = float(dikili_alani) if dikili_alani else 0
    
    arazi_bilgileri = {
        'buyukluk_m2': float(alan_m2),
        'dikili_alani': dikili_alan_degeri,
        'arazi_tipi': arazi_tipi,
        'ana_vasif': arazi_tipi,
        'zeytin_agac_adedi': int(request_data.get('zeytin_agac_adedi', 0)),
        'tapu_zeytin_agac_adedi': int(request_data.get('tapu_zeytin_agac_adedi', 0)),
        'mevcut_zeytin_agac_adedi': int(request_data.get('mevcut_zeytin_agac_adedi', 0))
    }
    
    # Zeytinlik ve tarla alanı mapping - tesisler.py logic
    zeytinlik_alani = request_data.get('zeytinlik_alani', 0)
    if zeytinlik_alani and float(zeytinlik_alani) > 0:
        arazi_bilgileri['zeytinlik_alani'] = float(zeytinlik_alani)
    
    # Tarla alanı mapping - tesisler.py'den genişletilmiş logic
    if arazi_tipi == "Tarla":
        arazi_bilgileri['tarla_alani'] = float(alan_m2)
    elif arazi_tipi == "Tarla + herhangi bir dikili vasıflı":
        arazi_bilgileri['tarla_alani'] = float(tarla_alani) if tarla_alani else 0
    elif tarla_alani and float(tarla_alani) > 0:
        arazi_bilgileri['tarla_alani'] = float(tarla_alani)
    
    yapi_bilgileri = {
        'taban_alani_m2': 30,  # Maksimum taban alanı (2025 güncellemesi, eski: 75)
        'toplam_alan_m2': 60  # Maksimum toplam alan - 30 m² x 2 kat (2025, eski: 150)
    }
    
    return arazi_bilgileri, yapi_bilgileri

def _process_calculation_result(core_result: dict, request, location_info: dict = None) -> dict:
    """
    Process calculation result with sanitization and additional info
    
    Args:
        core_result: Raw calculation result from core
        request: DRF request for debug control
        location_info: Location information to attach
        
    Returns:
        dict: Processed and sanitized result
    """
    # HTML unescape işlemi
    result = unescape_result_html_fields(core_result)
    
    # Debug exposure kontrolü - tesisler.py'den aynen alındı
    expose_debug = False
    try:
        if getattr(settings, 'DEBUG', False):
            dbg_param = str(request.GET.get('debug', '')).lower()
            if dbg_param in ('1', 'true', 'yes'):
                expose_debug = True
            
            if hasattr(request, 'user') and getattr(request.user, 'is_staff', False):
                expose_debug = True
    except Exception:
        expose_debug = False
    
    # Result sanitization
    result = sanitize_bag_evi_result(result, expose_debug=expose_debug)
    
    # Lokasyon bilgilerini sonuca ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return result
