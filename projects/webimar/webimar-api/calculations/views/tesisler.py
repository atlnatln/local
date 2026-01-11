# --- Zeytinyağı Üretim Tesisi ---
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .base import calculation_exception_handler, calculation_view
from .utils import get_emsal_orani, standard_success_response, standard_error_response, unescape_result_html_fields

logger = logging.getLogger('calculations')

@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_zeytinyagi_uretim_tesisi(request):
    """Zeytinyağı üretim tesisi hesaplaması (ID: 15)"""
    from calculations.tarimsal_yapilar import zeytinyagi_uretim_tesisi
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    alan_m2 = request.data.get('alan_m2')
    arazi_buyuklugu_m2 = request.data.get('arazi_buyuklugu_m2')
    if alan_m2:
        arazi_alani = float(alan_m2)
    elif arazi_buyuklugu_m2:
        arazi_alani = float(arazi_buyuklugu_m2)
    else:
        return standard_error_response('alan_m2 veya arazi_buyuklugu_m2 parametresi gereklidir')
    result = zeytinyagi_uretim_tesisi.zeytinyagi_uretim_tesisi_hesapla(arazi_alani)
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
        'message': 'Zeytinyağı üretim tesisi hesaplama başarıyla tamamlandı'
    })

# --- Bağ Evi ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_bag_evi(request):
    """
    Bağ evi hesaplaması (ID: 14) - LEGACY WRAPPER
    
    ⚠️ DEPRECATION NOTICE: Bu endpoint backwards compatibility için korunuyor.
    Yeni modular endpoint kullanın: /api/calculations/bag-evi-v2/
    
    Bu wrapper yeni modular view'i çağırır.
    """
    from calculations.tarimsal_yapilar.bag_evi.views import _calculate_bag_evi_view_impl
    
    # Deprecation log
    logger.info("⚠️ calculate_bag_evi in tesisler.py is deprecated - delegating to bag_evi.views.calculate_bag_evi_view")
    
    # Ortak implementasyon (dekoratörsüz) - double limit sayımı ve Request/HttpRequest
    # uyuşmazlığını önler.
    return _calculate_bag_evi_view_impl(request)

# --- Soğuk Hava Deposu ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_soguk_hava_deposu(request):
    """Soğuk hava deposu hesaplaması (ID: 16) - MD Belgesi Uyumlu"""
    from calculations.tarimsal_yapilar import soguk_hava_deposu
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    # YENİ SİSTEM: Arazi bilgilerini topla
    # Emsal tipi kontrolü
    emsal_tipi = request.data.get('emsal_tipi')
    if not emsal_tipi:
        # Eski sistem uyumluluğu: emsal_orani'ndan emsal_tipi çıkar
        emsal_orani = get_emsal_orani(request.data)
        if emsal_orani == 0.20:
            emsal_tipi = 'marjinal'
        elif emsal_orani == 0.05:
            emsal_tipi = 'mutlak_dikili_ozel'
        else:
            return standard_error_response('Emsal tipi seçimi zorunludur. Lütfen Marjinal (%20) veya Mutlak/Dikili/Özel (%5) seçin.')
    
    # Arazi bilgilerini hazırla
    arazi_bilgileri = {
        'emsal_tipi': emsal_tipi,
        'buyukluk_m2': request.data.get('arazi_alani_m2') or request.data.get('alan_m2') or request.data.get('alan', 0),
        'ana_vasif': request.data.get('arazi_vasfi'),
        'alan_m2': request.data.get('alan_m2', 0),
        'tarla_alani': request.data.get('tarla_alani', 0),
        'dikili_alani': request.data.get('dikili_alani', 0),
        'zeytinlik_alani': request.data.get('zeytinlik_alani', 0),
        'sera_alani': request.data.get('sera_alani', 0),
        'zeytin_agac_sayisi': request.data.get('zeytin_agac_sayisi', 0),
        'zeytin_agac_adedi': request.data.get('zeytin_agac_adedi', 0),
        'tapu_zeytin_agac_adedi': request.data.get('tapu_zeytin_agac_adedi', 0),
        'mevcut_zeytin_agac_adedi': request.data.get('mevcut_zeytin_agac_adedi', 0)
    }
    
    # Arazi vasfi smart detection (tarımsal depo sisteminden)
    if not arazi_bilgileri['ana_vasif'] and arazi_bilgileri['emsal_tipi'] == 'mutlak_dikili_ozel':
        # Smart detection
        if arazi_bilgileri.get('dikili_alani', 0) > 0:
            arazi_bilgileri['ana_vasif'] = 'Dikili vasıflı'
        elif arazi_bilgileri.get('sera_alani', 0) > 0:
            arazi_bilgileri['ana_vasif'] = 'Sera'
        elif arazi_bilgileri.get('tarla_alani', 0) > 0:
            arazi_bilgileri['ana_vasif'] = 'Tarla'
        elif arazi_bilgileri['buyukluk_m2'] > 0:
            # Varsayılan olarak tarla
            arazi_bilgileri['ana_vasif'] = 'Tarla'
    
    print(f"🏢 Soğuk hava deposu API çağrısı")
    print(f"📍 Arazi bilgileri: {arazi_bilgileri}")
    
    # Yeni sistem fonksiyonunu çağır
    try:
        result = soguk_hava_deposu.soguk_hava_deposu_degerlendir(arazi_bilgileri, {})
        
        # ESKİ API UYUMLULUĞU: Eski format alanları ekle
        if result.get('success', False):
            result['sonuc'] = result.get('ana_mesaj', '')
            result['mesaj'] = result.get('html_mesaj', '')
            
            # Soğuk depo kapasitesi hesabı (MD'de istenmiyor ama uyumluluk için)
            max_alan = result.get('maksimum_insaat_alani_m2', 0)
            if max_alan > 0:
                # 1 m² = 2.5 ton kapasiteyle hesapla
                result['soguk_depo_kapasitesi_ton'] = round(max_alan * 2.5, 1)
        
        # Lokasyon bilgilerini sonuca ekle
        if location_info:
            result['location_info'] = location_info
            buyuk_ova_message = format_buyuk_ova_message(location_info)
            if buyuk_ova_message:
                result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    except Exception as e:
        print(f"❌ Soğuk hava deposu hesaplama API hatası: {e}")
        # Hata durumunda eski sistemi dene (fallback)
        alan_m2 = arazi_bilgileri['buyukluk_m2']
        emsal_orani = get_emsal_orani(request.data)
        if not alan_m2 or float(alan_m2) <= 0:
            return standard_error_response('Arazi alanı pozitif bir sayı olmalıdır')
        result = soguk_hava_deposu.calculate_soguk_hava_deposu(float(alan_m2), emsal_orani)
        
        # Lokasyon bilgilerini sonuca ekle
        if location_info:
            result['location_info'] = location_info
            buyuk_ova_message = format_buyuk_ova_message(location_info)
            if buyuk_ova_message:
                result['buyuk_ova_mesaji'] = buyuk_ova_message

    return Response({
        'success': True,
        'results': result,
        'message': 'Soğuk hava deposu hesaplama başarıyla tamamlandı'
    })

# --- Tarımsal Amaçlı Depo ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_tarimsal_amacli_depo(request):
    """
    Tarımsal amaçlı depo hesaplaması (ID: 6)
    MD dokümantasyonu uygulaması - Bağ evi modülü mantığıyla dinamik emsal sistemi
    """
    from calculations.tarimsal_yapilar import tarimsal_amacli_depo
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    # Request verilerini al
    alan_m2 = request.data.get('alan_m2') or request.data.get('alan', 0)
    arazi_vasfi = request.data.get('arazi_vasfi', 'Tarla')  # Varsayılan Tarla
    
    # MD dokümantasyonu için alan kontrolü - Arazi vasfına göre esnek kontrol
    alan_mevcut = False
    toplam_alan = 0
    
    # Farklı arazi tipleri için alan kontrolü
    if alan_m2 and float(alan_m2) > 0:
        alan_mevcut = True
        toplam_alan = float(alan_m2)
    elif arazi_vasfi in ['Tarla + Zeytinlik', 'Tarla + herhangi bir dikili vasıflı']:
        tarla_alani = request.data.get('tarla_alani', 0)
        dikili_alani = request.data.get('dikili_alani', 0)
        zeytinlik_alani = request.data.get('zeytinlik_alani', 0)
        if tarla_alani or dikili_alani or zeytinlik_alani:
            alan_mevcut = True
            toplam_alan = float(tarla_alani or 0) + float(dikili_alani or 0) + float(zeytinlik_alani or 0)
    elif arazi_vasfi in ['Dikili vasıflı', 'Zeytin ağaçlı + herhangi bir dikili vasıf']:
        dikili_alani = request.data.get('dikili_alani', 0)
        if dikili_alani and float(dikili_alani) > 0:
            alan_mevcut = True
            toplam_alan = float(dikili_alani)
    elif arazi_vasfi == 'Zeytin ağaçlı + tarla':
        tarla_alani = request.data.get('tarla_alani', 0)
        if tarla_alani and float(tarla_alani) > 0:
            alan_mevcut = True
            toplam_alan = float(tarla_alani)
    
    if not alan_mevcut or toplam_alan <= 0:
        return standard_error_response('Bu arazi vasfı için gerekli alan bilgileri eksik veya geçersiz')
    
    # YENİ SİSTEM: MD dokümantasyonu uygulaması
    # Arazi bilgilerini yeni formata çevir - Tüm form verilerini aktar
    arazi_bilgileri = {
        "buyukluk_m2": toplam_alan,
        "ana_vasif": arazi_vasfi,
        "buyuk_ova_icinde": location_info.get('buyuk_ova_icerisinde', False) if location_info else False,
        # Tüm form verilerini aktar
        "alan_m2": request.data.get('alan_m2', toplam_alan),
        "tarla_alani": request.data.get('tarla_alani', 0),
        "dikili_alani": request.data.get('dikili_alani', 0),
        "zeytinlik_alani": request.data.get('zeytinlik_alani', 0),
        "zeytin_agac_sayisi": request.data.get('zeytin_agac_sayisi', 0),
        "tapu_zeytin_agac_adedi": request.data.get('tapu_zeytin_agac_adedi', 0),
        "mevcut_zeytin_agac_adedi": request.data.get('mevcut_zeytin_agac_adedi', 0),
        "zeytin_agac_adedi": max(request.data.get('tapu_zeytin_agac_adedi', 0), request.data.get('mevcut_zeytin_agac_adedi', 0))
    }
    
    # Yapı bilgileri (kullanılmıyor ama uyumluluk için)
    yapi_bilgileri = {}
    
    # Yeni sistem fonksiyonunu çağır
    try:
        result = tarimsal_amacli_depo.tarimsal_depo_degerlendir(arazi_bilgileri, yapi_bilgileri)
        
        # ESKİ API UYUMLULUĞU: Eski format alanları ekle
        if result.get('success', False):
            result['sonuc'] = result.get('ana_mesaj', '')
            result['mesaj'] = result.get('html_mesaj', '')
            
            # Depolama kapasitesi hesabı (MD'de istenmiyor ama uyumluluk için)
            max_alan = result.get('maksimum_insaat_alani_m2', 0)
            result['depolama_kapasitesi_ton'] = round(max_alan * 2.5, 1) if max_alan > 0 else 0
        
        # Lokasyon bilgilerini sonuca ekle
        if location_info:
            result['location_info'] = location_info
            buyuk_ova_message = format_buyuk_ova_message(location_info)
            if buyuk_ova_message:
                result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    except Exception as e:
        print(f"❌ Depo hesaplama API hatası: {e}")
        # Hata durumunda eski sistemi dene (fallback)
        emsal_orani = get_emsal_orani(request.data)
        result = tarimsal_amacli_depo.calculate_tarimsal_amacli_depo(float(alan_m2), emsal_orani)
        
        # Lokasyon bilgilerini sonuca ekle
        if location_info:
            result['location_info'] = location_info
            buyuk_ova_message = format_buyuk_ova_message(location_info)
            if buyuk_ova_message:
                result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Tarımsal amaçlı depo hesaplama başarıyla tamamlandı'
    })
# --- Hububat Silo ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_hububat_silo(request):
    """Hububat silo hesaplaması (ID: 5)"""
    from calculations.tarimsal_yapilar import tarimsal_silo
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    alan_m2 = request.data.get('alan_m2') or request.data.get('alan', 0)
    silo_taban_alani_m2 = request.data.get('silo_taban_alani_m2', 0)
    emsal_orani = get_emsal_orani(request.data)
    if not alan_m2 or float(alan_m2) <= 0:
        return standard_error_response('Arazi alanı pozitif bir sayı olmalıdır')
    if not silo_taban_alani_m2 or float(silo_taban_alani_m2) <= 0:
        return standard_error_response('Planlanan silo taban alanı pozitif bir sayı olmalıdır')
    result = tarimsal_silo.hububat_silo_degerlendir({
        'arazi_buyuklugu_m2': float(alan_m2),
        'silo_taban_alani_m2': float(silo_taban_alani_m2)
    }, emsal_orani=emsal_orani)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Hububat silo hesaplama başarıyla tamamlandı'
    })

# --- Lisanslı Depo ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_lisansli_depo(request):
    """Lisanslı depo hesaplaması (ID: 7)"""
    from calculations.tarimsal_yapilar import lisansli_depo
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    emsal_orani = get_emsal_orani(request.data)
    result = lisansli_depo.lisansli_depo_degerlendir_api(request.data, emsal_orani=emsal_orani)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Lisanslı depo hesaplama başarıyla tamamlandı'
    })

# --- Yıkama Tesisi ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_yikama_tesisi(request):
    """Yıkama tesisi hesaplaması"""
    from calculations.tarimsal_yapilar import yikama_tesisi
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    emsal_orani = get_emsal_orani(request.data)
    result = yikama_tesisi.yikama_tesisi_degerlendir(request.data, emsal_orani=emsal_orani)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Yıkama tesisi hesaplama başarıyla tamamlandı'
    })

# --- Kurutma Tesisi ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_kurutma_tesisi(request):
    """Kurutma tesisi hesaplaması"""
    from calculations.tarimsal_yapilar import kurutma_tesisi
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    emsal_orani = get_emsal_orani(request.data)
    result = kurutma_tesisi.kurutma_tesisi_degerlendir(request.data, emsal_orani=emsal_orani)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Kurutma tesisi hesaplama başarıyla tamamlandı'
    })

# --- Meyve Sebze Kurutma ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_meyve_sebze_kurutma(request):
    """Meyve sebze kurutma alanı hesaplaması (ID: 10)"""
    from calculations.tarimsal_yapilar import meyve_sebze_kurutma
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    emsal_orani = get_emsal_orani(request.data)
    result = meyve_sebze_kurutma.meyve_sebze_kurutma_degerlendir(request.data, emsal_orani=emsal_orani)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Meyve/sebze kurutma alanı hesaplama başarıyla tamamlandı'
    })

# --- Zeytinyağı Fabrikası ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_zeytinyagi_fabrikasi(request):
    """Zeytinyağı fabrikası hesaplaması (ID: 11)"""
    from calculations.tarimsal_yapilar import zeytinyagi_fabrikasi
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    result = zeytinyagi_fabrikasi.zeytinyagi_fabrikasi_degerlendir(request.data)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Zeytinyağı fabrikası hesaplama başarıyla tamamlandı'
    })

# --- Su Depolama ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_su_depolama(request):
    """Su depolama tesisi hesaplaması (ID: 12)"""
    from calculations.tarimsal_yapilar import su_depolama
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
    result = su_depolama.su_depolama_degerlendir(request.data, emsal_orani=emsal_orani)
    
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Su depolama tesisi hesaplama başarıyla tamamlandı'
    })

# --- Su Kuyuları ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_su_kuyulari(request):
    """Su kuyuları hesaplaması (ID: 13)"""
    from calculations.tarimsal_yapilar import su_kuyulari
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
    
    result = su_kuyulari.su_kuyulari_degerlendir(request.data)
    
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Su kuyuları hesaplama başarıyla tamamlandı'
    })

# --- Solucan Tesisi ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_solucan_tesisi(request):
    """Solucan tesisi hesaplaması (ID: 1)"""
    from calculations.tarimsal_yapilar import solucan_tesisi
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
    
    result = solucan_tesisi.solucan_degerlendir(request.data)
    
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Solucan tesisi hesaplama başarıyla tamamlandı'
    })

# --- Mantar Tesisi ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_mantar_tesisi(request):
    """Mantar tesisi hesaplaması (ID: 2)"""
    from calculations.tarimsal_yapilar import mantar_tesisi
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
    
    result = mantar_tesisi.mantar_degerlendir(request.data)
    
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Mantar tesisi hesaplama başarıyla tamamlandı'
    })

# --- Sera ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_sera(request):
    """Sera hesaplaması (ID: 3)"""
    from calculations.tarimsal_yapilar import sera
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
    
    alan_m2 = request.data.get('alan_m2')
    arazi_vasfi = request.data.get('arazi_vasfi', 'TA')
    sera_alani_m2 = request.data.get('sera_alani_m2')
    if alan_m2 is not None:
        adapted_data = {
            'arazi_buyuklugu_m2': float(alan_m2),
            'arazi_vasfi': arazi_vasfi
        }
        if sera_alani_m2 is not None:
            adapted_data['sera_alani_m2'] = float(sera_alani_m2)
    else:
        adapted_data = request.data
    result = sera.sera_degerlendir(adapted_data)
    
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Sera hesaplama başarıyla tamamlandı'
    })

# --- Arıcılık ---
@api_view(['POST'])
@calculation_view  # Limit kontrolü ve exception handling
def calculate_aricilik(request):
    """Arıcılık tesisi hesaplaması (ID: 4)"""
    from calculations.tarimsal_yapilar import aricilik
    from calculations.utils.location_utils import check_location_status, validate_coordinates, format_buyuk_ova_message
    
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
    
    result = aricilik.aricilik_frontend_degerlendir(request.data)
    
    # Lokasyon bilgilerini response'a ekle
    if location_info:
        result['location_info'] = location_info
        buyuk_ova_message = format_buyuk_ova_message(location_info)
        if buyuk_ova_message:
            result['buyuk_ova_mesaji'] = buyuk_ova_message
    
    return Response({
        'success': True,
        'results': result,
        'message': 'Arıcılık tesisi hesaplama başarıyla tamamlandı'
    })
