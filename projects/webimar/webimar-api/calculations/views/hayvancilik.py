# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
import html  # HTML unescape için eklendi
from calculations.views.base import calculation_exception_handler, calculation_view
from calculations.views.utils import get_arazi_alani, get_emsal_orani, standard_success_response, standard_error_response, unescape_result_html_fields

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kaz_ordek(request):
    """Kaz Ördek çiftliği hesaplaması (ID: 23)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    if arazi_alani <= 0:
        return standard_error_response('Alan 0\'dan büyük olmalıdır')
    
    result = kanatli.kaz_ordek_degerlendir(arazi_alani, emsal_orani=emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Kaz Ördek çiftlik hesaplama başarıyla tamamlandı'
    })

from calculations.models import CalculationHistory
from calculations.tarimsal_yapilar import (
    hara_tesisi_degerlendir, 
    evcil_hayvan_tesisi_degerlendir,
    hesapla_ipek_bocekciligi_kurallari,
    sut_sigiri_degerlendir, 
    besi_sigiri_degerlendir,
    kucukbas_degerlendir,
)
from calculations.tarimsal_yapilar import kanatli

logger = logging.getLogger('calculations')

# unescape_result_html_fields fonksiyonu utils.py'ye taşındı

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_hara(request):
    """At yetiştiriciliği tesisi (hara) hesaplaması (ID: 24)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    logger.info(f"[HARA] API request.data: {request.data}")
    
    # Koordinat kontrolleri
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
        if not location_info['location_valid']:
            return standard_error_response(location_info['location_message'])
    
    emsal_orani = get_emsal_orani(request.data)
    alan_m2 = get_arazi_alani(request.data)
    arazi_vasfi = request.data.get('arazi_vasfi', 'Dikili tarım')
    su_tahsis_belgesi = request.data.get('su_tahsis_belgesi', False)
    yas_kapali_alan_durumu = request.data.get('yas_kapali_alan_durumu', 'dışında')
    
    # arazi_bilgileri mapping'ini düzelt
    if alan_m2 is not None:
        arazi_bilgileri = {
            'alan_m2': alan_m2,
            'buyukluk_m2': alan_m2,
            'arazi_vasfi': arazi_vasfi,
            'su_tahsis_belgesi': str(su_tahsis_belgesi).lower(),
            'yas_kapali_alan_durumu': yas_kapali_alan_durumu
        }
        yapi_bilgileri = {}
    else:
        arazi_bilgileri = request.data.get('arazi_bilgileri', {})
        yapi_bilgileri = request.data.get('yapi_bilgileri', {})
        # Eğer arazi_bilgileri boşsa ve alan_m2 de yoksa request.data'dan doğrudan al
        if not arazi_bilgileri.get('alan_m2') and not arazi_bilgileri.get('buyukluk_m2'):
            arazi_bilgileri['alan_m2'] = request.data.get('alan_m2', 0)
            arazi_bilgileri['buyukluk_m2'] = request.data.get('alan_m2', 0)
    
    logger.info(f"[HARA] arazi_bilgileri: {arazi_bilgileri}, yapi_bilgileri: {yapi_bilgileri}")
    result = hara_tesisi_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini sonuca ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    logger.info(f"[HARA] result: {result}")
    return Response({
        'success': True,
        'results': result,
        'message': 'Hara tesisi hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_evcil_hayvan(request):
    """Evcil hayvan ve bilimsel araştırma hayvanı üretim tesisi hesaplaması (ID: 26)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    logger.info(f"Evcil hayvan calculation request: {request.data}")
    
    # Koordinat kontrolleri
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
        if not location_info['location_valid']:
            return standard_error_response(location_info['location_message'])
    
    emsal_orani = get_emsal_orani(request.data)
    alan_m2 = get_arazi_alani(request.data)
    arazi_vasfi = request.data.get('arazi_vasfi', 'Dikili tarım')
    su_tahsis_belgesi = request.data.get('su_tahsis_belgesi', False)
    yas_kapali_alan_durumu = request.data.get('yas_kapali_alan_durumu', 'dışında')
    
    if alan_m2 is not None:
        arazi_bilgileri = {
            'buyukluk_m2': alan_m2,
            'arazi_vasfi': arazi_vasfi,
            'su_tahsis_belgesi': str(su_tahsis_belgesi).lower(),
            'yas_kapali_alan_durumu': yas_kapali_alan_durumu
        }
        yapi_bilgileri = {}
    else:
        arazi_bilgileri = request.data.get('arazi_bilgileri', {})
        yapi_bilgileri = request.data.get('yapi_bilgileri', {})
    
    result = evcil_hayvan_tesisi_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini sonuca ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Evcil hayvan tesisi hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_ipek_bocekciligi(request):
    """İpek böcekçiliği hesaplaması (ID: 25)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    logger.info(f"Ipek bocekciligi calculation request: {request.data}")
    
    # Koordinat kontrolleri
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
        if not location_info['location_valid']:
            return standard_error_response(location_info['location_message'])
    
    alan_m2 = get_arazi_alani(request.data)
    dut_bahcesi_var_mi = request.data.get('dut_bahcesi_var_mi', True)
    arazi_vasfi = request.data.get('arazi_vasfi', 'Dikili tarım')
    genel_emsal_orani = request.data.get('genel_emsal_orani', 0.20)
    
    if alan_m2 is not None:
        arazi_bilgileri = {
            'alan_m2': alan_m2,
            'buyukluk_m2': alan_m2,
            'arazi_vasfi': arazi_vasfi
        }
        yapi_bilgileri = {
            'dut_bahcesi_var_mi': dut_bahcesi_var_mi
        }
    else:
        arazi_bilgileri = request.data.get('arazi_bilgileri', {})
        yapi_bilgileri = request.data.get('yapi_bilgileri', {})
    
    result = hesapla_ipek_bocekciligi_kurallari(arazi_bilgileri, yapi_bilgileri, genel_emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini sonuca ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'İpek böcekçiliği hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_sut_sigirciligi(request):
    """Süt sığırcılığı hesaplaması (ID: 17)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message, check_water_restrictions_for_livestock
    
    logger.info(f"[SUT_SIGIRCILIGI] API request.data: {request.data}")
    
    # Koordinat kontrolleri
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
        if not location_info['location_valid']:
            return standard_error_response(location_info['location_message'])
            
        # Su kısıtı kontrolü
        can_proceed, restriction_msg = check_water_restrictions_for_livestock(location_info, 'sut-sigirciligi')
        if not can_proceed:
            return standard_error_response(restriction_msg)
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    logger.info(f"[SUT_SIGIRCILIGI] su_tahsis_belgesi: {request.data.get('su_tahsis_belgesi')}")
    logger.info(f"[SUT_SIGIRCILIGI] yas_kapali_alan_durumu: {request.data.get('yas_kapali_alan_durumu')}")
    
    if arazi_alani is None:
        arazi_bilgileri = request.data.get('arazi_bilgileri', {})
        yapi_bilgileri = request.data.get('yapi_bilgileri', {})
        buyuk_ova_alaninda_mi = arazi_bilgileri.get('buyuk_ova_icinde', False)
        result = sut_sigiri_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani, buyuk_ova_alaninda_mi)
    else:
        arazi_bilgileri = {
            'buyukluk_m2': arazi_alani,
            'su_tahsis_belgesi': request.data.get('su_tahsis_belgesi', 'false'),
            'yas_kapali_alan_durumu': request.data.get('yas_kapali_alan_durumu', 'dışında')
        }
        yapi_bilgileri = {}
        buyuk_ova_alaninda_mi = request.data.get('buyuk_ova_icinde', False)
        logger.info(f"[SUT_SIGIRCILIGI] Created arazi_bilgileri: {arazi_bilgileri}")
        logger.info(f"[SUT_SIGIRCILIGI] buyuk_ova_alaninda_mi: {buyuk_ova_alaninda_mi}")
        result = sut_sigiri_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani, buyuk_ova_alaninda_mi)
    
    result = unescape_result_html_fields(result)
    logger.info(f"[SUT_SIGIRCILIGI] result izin_durumu: {result.get('izin_durumu', 'NO_RESULT')}")
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    # UX formatter'ı BYPASS ET: Direkt ham sonucu döndür
    return Response({
        'success': True,
        'results': result,
        'message': 'Süt sığırcılığı hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_besi_sigirciligi(request):
    """Besi sığırcılığı hesaplaması (ID: 27)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message, check_water_restrictions_for_livestock
    
    logger.info(f"Besi sigirciligi calculation request: {request.data}")
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
        
        # Su kısıtı kontrolü
        can_proceed, restriction_msg = check_water_restrictions_for_livestock(location_info, 'besi-sigirciligi')
        if not can_proceed:
            return standard_error_response(restriction_msg)
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    if arazi_alani is None:
        # Eski format için fallback
        arazi_bilgileri = request.data.get('arazi_bilgileri', {})
        yapi_bilgileri = request.data.get('yapi_bilgileri', {})
        buyuk_ova_alaninda_mi = arazi_bilgileri.get('buyuk_ova_icinde', False)
        result = besi_sigiri_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani, buyuk_ova_alaninda_mi)
    else:
        # Yeni format: arazi_bilgileri ve yapi_bilgileri structure'ını oluştur
        arazi_bilgileri = {
            'buyukluk_m2': arazi_alani,
            'su_tahsis_belgesi': request.data.get('su_tahsis_belgesi', 'false'),
            'yas_kapali_alan_durumu': request.data.get('yas_kapali_alan_durumu', 'dışında')
        }
        yapi_bilgileri = {}
        buyuk_ova_alaninda_mi = request.data.get('buyuk_ova_icinde', False)
        result = besi_sigiri_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani, buyuk_ova_alaninda_mi)
    
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Besi sığırcılığı hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_agil_kucukbas(request):
    """Ağıl (küçükbaş hayvan barınağı) hesaplaması (ID: 18)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    logger.info(f"Agil kucukbas calculation request: {request.data}")
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    if arazi_alani is None:
        # Eski format için fallback
        arazi_bilgileri = request.data.get('arazi_bilgileri', {})
        yapi_bilgileri = request.data.get('yapi_bilgileri', {})
        result = kucukbas_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani)
    else:
        # Yeni format: arazi_bilgileri ve yapi_bilgileri structure'ını oluştur
        arazi_bilgileri = {
            'buyukluk_m2': arazi_alani,
            'su_tahsis_belgesi': request.data.get('su_tahsis_belgesi', 'false'),
            'yas_kapali_alan_durumu': request.data.get('yas_kapali_alan_durumu', 'dışında')
        }
        yapi_bilgileri = {}
        result = kucukbas_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani)
    
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Ağıl hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kumes_yumurtaci(request):
    """Kümes (yumurtacı tavuk) hesaplaması (ID: 19)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    if arazi_alani <= 0:
        return standard_error_response('Alan 0\'dan büyük olmalıdır')
    
    result = kanatli.yumurtaci_tavuk_degerlendir(arazi_alani, emsal_orani=emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Yumurtacı tavuk kümesi hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kumes_etci(request):
    """Kümes (etçi tavuk) hesaplaması (ID: 20)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    if arazi_alani <= 0:
        return standard_error_response('Alan 0\'dan büyük olmalıdır')
    
    result = kanatli.etci_tavuk_degerlendir(arazi_alani, emsal_orani=emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Etçi tavuk kümesi hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kumes_gezen(request):
    """Kümes (gezen tavuk) hesaplaması (ID: 21)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    result = kanatli.gezen_tavuk_degerlendir(arazi_alani, emsal_orani=emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Gezen tavuk kümes hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kumes_hindi(request):
    """Kümes (hindi) hesaplaması (ID: 22)"""
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
    # Koordinat kontrolleri
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    location_info = None
    if latitude is not None and longitude is not None:
        is_valid, error_msg = validate_coordinates(float(latitude), float(longitude))
        if not is_valid:
            return standard_error_response(f'Koordinat hatası: {error_msg}')
        location_info = check_location_status(float(latitude), float(longitude))
    
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    result = kanatli.hindi_degerlendir(arazi_alani, emsal_orani=emsal_orani)
    result = unescape_result_html_fields(result)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Hindi kümes hesaplama başarıyla tamamlandı'
    })

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kaz_ordek(request):
    """Kaz Ördek çiftliği hesaplaması (ID: 23)"""
    emsal_orani = get_emsal_orani(request.data)
    arazi_alani = get_arazi_alani(request.data)
    
    if arazi_alani == 0:
        return standard_error_response('Alan bilgisi gereklidir')
    
    result = kanatli.kaz_ordek_degerlendir(arazi_alani, emsal_orani=emsal_orani)
    result = unescape_result_html_fields(result)
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Kaz ördek çiftliği hesaplama başarıyla tamamlandı'
    })
