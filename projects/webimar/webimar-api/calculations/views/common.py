"""
Ortak ve genel API endpoint'leri
"""
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import logging
import re
import unicodedata
import requests

from ..models import CalculationHistory, CalculationLog
from ..serializers import CalculationHistorySerializer, CalculationHistoryCreateSerializer
from ..tarimsal_yapilar import constants
from accounts.utils import log_calculation, log_map_interaction
from accounts.logging_utils import safe_log_request_data
from ..throttles import CalculationFeedbackRateThrottle
from rest_framework.decorators import throttle_classes

logger = logging.getLogger('calculations')


def _get_client_ip(request) -> str:
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        return ip_address.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize('NFD', str(value or ''))
    normalized = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    return normalized.lower().strip()


def _normalize_key(key: str) -> str:
    return re.sub(r'[^a-z0-9]', '', _normalize_text(key))


PROVINCE_KEYS = {
    'il',
    'sehir',
    'province',
    'city',
    'iladi',
    'selectedil',
    'selectedprovince',
    'provincevalue',
}


def _extract_province_from_payload(payload) -> str | None:
    if isinstance(payload, dict):
        for raw_key, raw_value in payload.items():
            key = _normalize_key(raw_key)
            if key in PROVINCE_KEYS and isinstance(raw_value, str) and raw_value.strip():
                return raw_value.strip().upper()

            nested_value = _extract_province_from_payload(raw_value)
            if nested_value:
                return nested_value

    if isinstance(payload, list):
        for item in payload:
            nested_value = _extract_province_from_payload(item)
            if nested_value:
                return nested_value

    return None


def _normalize_province_group_key(province: str) -> str:
    return _normalize_key(province)


TARIMSAL_YAPI_TYPES = {
    'bag-evi', 'bag_evi',
    'solucan-tesisi', 'solucan_tesisi',
    'mantar-tesisi', 'mantar_tesisi',
    'sera',
    'aricilik',
    'hububat-silo', 'hububat_silo',
    'tarimsal-depo', 'tarimsal_depo', 'tarimsal-amacli-depo', 'tarimsal_amacli_depo',
    'lisansli-depo', 'lisansli_depo',
    'yikama-tesisi', 'yikama_tesisi',
    'kurutma-tesisi', 'kurutma_tesisi',
    'meyve-sebze-kurutma', 'meyve_sebze_kurutma',
    'zeytinyagi-fabrikasi', 'zeytinyagi_fabrikasi',
    'soguk-hava-deposu', 'soguk_hava_deposu',
    'su-depolama', 'su_depolama',
    'su-kuyulari', 'su_kuyulari',
    'sut-sigirciligi', 'sut_sigirciligi',
    'agil-kucukbas', 'agil_kucukbas',
    'kumes-yumurtaci', 'kumes_yumurtaci',
    'kumes-etci', 'kumes_etci',
    'kumes-gezen', 'kumes_gezen',
    'kumes-hindi', 'kumes_hindi',
    'kaz-ordek', 'kaz_ordek',
    'hara',
    'ipek-bocekciligi', 'ipek_bocekciligi',
    'evcil-hayvan', 'evcil_hayvan',
    'besi-sigirciligi', 'besi_sigirciligi',
}

@api_view(['GET'])
def health_check(request):
    """Calculations app health check endpoint"""
    return Response({
        'status': 'ok',
        'app': 'calculations',
        'detail': 'Calculations app is running successfully'
    })


@api_view(['POST'])
def track_public_calculation_event(request):
    """Public sayfalardan hesaplama event kaydı alır (gübre/havza vb.)."""
    try:
        event_type = str(request.data.get('event_type') or '').strip()
        calculation_type = str(request.data.get('calculation_type') or '').strip()

        if event_type != 'calculation' or not calculation_type:
            return Response({
                'success': False,
                'detail': 'Geçersiz event verisi'
            }, status=status.HTTP_400_BAD_REQUEST)

        ip_address = _get_client_ip(request)

        CalculationLog.log_calculation(
            user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
            ip_address=ip_address,
            calculation_type=calculation_type,
            calculation_data=request.data.get('calculation_data') or {},
            result_data=request.data.get('result_data') or {},
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_fingerprint=request.data.get('device_fingerprint'),
            location_data=request.data.get('location_data') or {},
            is_successful=True,
        )

        return Response({
            'success': True,
            'detail': 'Event kaydedildi'
        })
    except Exception as e:
        logger.error(f"Public event tracking error: {e}")
        return Response({
            'success': False,
            'detail': 'Event kaydedilemedi'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@throttle_classes([CalculationFeedbackRateThrottle])
def submit_calculation_feedback(request):
    """Hesaplama sayfalarından gelen geri bildirimleri Telegram'a iletir."""
    try:
        message = str(request.data.get('message') or '').strip()
        calculation_type = str(request.data.get('calculation_type') or '').strip()
        source_app = str(request.data.get('source_app') or '').strip() or 'unknown'
        page_path = str(request.data.get('page_path') or '').strip() or '-'

        if not message:
            return Response({
                'success': False,
                'detail': 'Mesaj alanı zorunludur.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(message) < 5:
            return Response({
                'success': False,
                'detail': 'Mesaj en az 5 karakter olmalıdır.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(message) > 2000:
            return Response({
                'success': False,
                'detail': 'Mesaj en fazla 2000 karakter olabilir.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not calculation_type:
            return Response({
                'success': False,
                'detail': 'Hangi hesaplamadan gönderildiği bilgisi eksik.'
            }, status=status.HTTP_400_BAD_REQUEST)

        telegram_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

        if not telegram_token or not telegram_chat_id:
            logger.error('Calculation feedback Telegram ayarları eksik')
            return Response({
                'success': False,
                'detail': 'Geri bildirim servisi şu anda kullanılamıyor.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '-')

        telegram_message = (
            '🛠️ Yeni Hesaplama Geri Bildirimi\n\n'
            f'📌 Hesaplama: {calculation_type}\n'
            f'🧩 Kaynak: {source_app}\n'
            f'🔗 Sayfa: {page_path}\n'
            f'🌐 IP: {ip_address}\n'
            f'🕒 Tarih: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'🧭 User-Agent: {user_agent[:220]}\n\n'
            f'💬 Mesaj:\n{message}'
        )

        telegram_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
        telegram_response = requests.post(
            telegram_url,
            data={
                'chat_id': telegram_chat_id,
                'text': telegram_message,
            },
            timeout=8,
        )
        telegram_response.raise_for_status()

        return Response({
            'success': True,
            'detail': 'Geri bildiriminiz gönderildi. Teşekkür ederiz.'
        })
    except requests.RequestException as telegram_error:
        logger.error(f'Calculation feedback Telegram gönderim hatası: {telegram_error}')
        return Response({
            'success': False,
            'detail': 'Geri bildirim gönderilemedi. Lütfen daha sonra tekrar deneyin.'
        }, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f'Calculation feedback endpoint hatası: {e}')
        return Response({
            'success': False,
            'detail': 'Beklenmeyen bir hata oluştu.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def public_homepage_calculation_insights(request):
    """Ana sayfa için kamuya açık hesaplama istatistikleri."""
    try:
        cache_key = 'homepage_calculation_insights_v2'
        cached = cache.get(cache_key)
        if cached:
            response = Response(cached)
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response

        successful_logs = CalculationLog.objects.filter(is_successful=True)

        gubre_count = successful_logs.filter(calculation_type='gubre_cukuru').count()
        havza_count = successful_logs.filter(calculation_type__in=['havza-bazli-destekleme-modeli', 'havza_bazli_destekleme_modeli']).count()

        tarimsal_yapi_logs = successful_logs.filter(calculation_type__in=TARIMSAL_YAPI_TYPES)
        tarimsal_yapi_count = tarimsal_yapi_logs.count()

        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        twenty_eight_days_ago = now - timedelta(days=28)

        province_counts = {}
        for log in tarimsal_yapi_logs.iterator():
            payload_candidates = [
                log.calculation_data,
                log.location_data,
                log.result_data,
            ]

            province = None
            for payload in payload_candidates:
                province = _extract_province_from_payload(payload)
                if province:
                    break

            if province:
                province_key = _normalize_province_group_key(province)
                if not province_key:
                    continue

                stats = province_counts.setdefault(province_key, {
                    'province': province.strip().upper(),
                    'count': 0,
                    'count_7d': 0,
                    'count_28d': 0,
                })
                stats['count'] += 1

                if log.created_at >= twenty_eight_days_ago:
                    stats['count_28d'] += 1
                if log.created_at >= seven_days_ago:
                    stats['count_7d'] += 1

        tarimsal_yapi_by_province = [
            {
                'province': stats['province'],
                'count': stats['count'],
                'count_7d': stats['count_7d'],
                'count_28d': stats['count_28d'],
            }
            for _, stats in sorted(province_counts.items(), key=lambda item: item[1]['count'], reverse=True)
        ]

        response_data = {
            'success': True,
            'data': {
                'totals': {
                    'gubre_cukuru': gubre_count,
                    'havza_bazli_destekleme': havza_count,
                    'tarimsal_yapi': tarimsal_yapi_count,
                },
                'tarimsal_yapi_by_province': tarimsal_yapi_by_province,
                'province_count': len(tarimsal_yapi_by_province),
            },
            'detail': 'Ana sayfa hesaplama istatistikleri başarıyla getirildi'
        }

        cache.set(cache_key, response_data, timeout=300)
        response = Response(response_data)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Homepage insights error: {e}")
        response = Response({
            'success': False,
            'detail': 'İstatistikler getirilirken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

# Static dosya servisleri
@api_view(['GET'])
def get_yonetmelikler(request):
    return Response({
        'success': True,
        'detail': 'Yonetmelikler endpoint ready',
        'data': []
    })

@api_view(['GET'])
def get_kml_files(request):
    return Response({
        'success': True,
        'detail': 'KML files endpoint ready',
        'data': []
    })

@api_view(['GET'])
def get_arazi_tipleri(request):
    """Arazi tiplerini döndüren endpoint - GSC Performance: Cache optimized"""
    try:
        # Cache key based on query parameters
        yapi_turu = request.GET.get('yapi_turu', None)
        cache_key = f"arazi_tipleri_{yapi_turu or 'all'}"
        
        # Try to get from cache first (GSC response time optimization)
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        # Yapı türüne göre filtreleme yapılabilir
        if yapi_turu:
            # Yapı türüne göre arazi vasflarını filtrele
            filtered_arazi_tipleri = []
            
            # Zeytinyağı tesisleri için sadece zeytinlik vasıfları
            if yapi_turu.lower() in ["zeytinyağı fabrikası", "zeytinyagi-fabrikasi", "zeytinyağı üretim tesisi", "zeytinyagi-uretim-tesisi"]:
                for arazi in constants.ARAZI_TIPLERI:
                    # Sadece "Zeytinlik" vasıfı, "Tarla + Zeytinlik" değil
                    if arazi["ad"].lower() == "zeytinlik":
                        filtered_arazi_tipleri.append(arazi)
            else:
                # Diğer yapı türleri için zeytinlik hariç tüm vasıflar
                for arazi in constants.ARAZI_TIPLERI:
                    if "zeytinlik" not in arazi["ad"].lower():
                        filtered_arazi_tipleri.append(arazi)
            
            result = {
                'success': True,
                'data': filtered_arazi_tipleri,
                'detail': f'{yapi_turu} yapısı için arazi tipleri başarıyla getirildi'
            }
        else:
            # Filtreleme yoksa tüm arazi tiplerini döndür
            result = {
                'success': True,
                'data': constants.ARAZI_TIPLERI,
                'detail': 'Arazi tipleri başarıyla getirildi'
            }
        
        # Cache the result for 24 hours (CACHE_TIMEOUT_ARAZI_TIPLERI)
        cache.set(cache_key, result, timeout=86400)
        return Response(result)
    except Exception as e:
        logger.error(f"Arazi tipleri error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'detail': 'Arazi tipleri getirilirken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_yapi_turleri(request):
    """Yapı türlerini döndüren endpoint - GSC Performance: Cache optimized"""
    try:
        # Cache key based on query parameters
        arazi_vasfi = request.GET.get('arazi_vasfi', None)
        include_pasif = request.GET.get('include_pasif', 'false').lower() == 'true'
        cache_key = f"yapi_turleri_{arazi_vasfi or 'all'}_{'all' if include_pasif else 'aktif'}"
        
        # Try to get from cache first (GSC response time optimization)
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        # Temel kaynak: pasif dahil mi değil mi
        kaynak_liste = constants.YAPI_TURLERI if include_pasif else constants.AKTIF_YAPI_TURLERI
        
        # Arazi vasıfına göre filtreleme yapılabilir
        if arazi_vasfi:
            # Arazi vasfına göre yapı türlerini filtrele
            filtered_yapi_turleri = []
            
            for yapi in kaynak_liste:
                yapi_adi = yapi["ad"]
                
                # Zeytinlik vasıfları için sadece zeytinyağı tesisleri
                if arazi_vasfi.lower() == "zeytinlik":
                    if yapi_adi in ["Zeytinyağı fabrikası", "Zeytinyağı üretim tesisi"]:
                        filtered_yapi_turleri.append(yapi)
                else:
                    # Zeytinlik dışı vasıflar için zeytinyağı tesisleri hariç
                    if yapi_adi not in ["Zeytinyağı fabrikası", "Zeytinyağı üretim tesisi"]:
                        filtered_yapi_turleri.append(yapi)
            
            result = {
                'success': True,
                'data': filtered_yapi_turleri,
                'detail': f'{arazi_vasfi} vasıfı için yapı türleri başarıyla getirildi'
            }
        else:
            # Filtreleme yoksa yapı türlerini döndür
            result = {
                'success': True,
                'data': list(kaynak_liste),
                'detail': 'Yapı türleri başarıyla getirildi'
            }
        
        # Cache the result for 1 hour (CACHE_TIMEOUT_STRUCTURE_TYPES)
        cache.set(cache_key, result, timeout=3600)
        return Response(result)
    except Exception as e:
        logger.error(f"Yapı türleri error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'detail': 'Yapı türleri getirilirken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_structure_categories(request):
    """Yapı türlerini kategorilere göre gruplandırarak döndüren endpoint (SSR/SEO için)"""
    try:
        # Kategorilere göre yapı türlerini gruplandır
        categories = {
            "hayvancilik": {
                "name": "Hayvancılık Tesisleri",
                "icon": "🐄",
                "description": "Büyükbaş, küçükbaş ve kanatlı hayvan tesisleri",
                "structures": [
                    {"id": 17, "name": "Süt Sığırcılığı Tesisi", "url_key": "sut-sigirciligi"},
                    {"id": 27, "name": "Besi Sığırcılığı Tesisi", "url_key": "besi-sigirciligi"},
                    {"id": 18, "name": "Ağıl (küçükbaş hayvan barınağı)", "url_key": "agil-kucukbas"},
                    {"id": 19, "name": "Kümes (yumurtacı tavuk)", "url_key": "kumes-yumurtaci"},
                    {"id": 20, "name": "Kümes (etçi tavuk)", "url_key": "kumes-etci"},
                    {"id": 21, "name": "Kümes (gezen tavuk)", "url_key": "kumes-gezen"},
                    {"id": 22, "name": "Kümes (hindi)", "url_key": "kumes-hindi"},
                    {"id": 23, "name": "Kaz Ördek çiftliği", "url_key": "kaz-ordek"},
                    {"id": 24, "name": "Hara (at üretimi/yetiştiriciliği tesisi)", "url_key": "hara"},
                    {"id": 26, "name": "Evcil hayvan ve bilimsel araştırma hayvanı üretim tesisi", "url_key": "evcil-hayvan"},
                ]
            },
            "depolama": {
                "name": "Depolama ve İşleme Tesisleri",
                "icon": "🏭",
                "description": "Tarımsal ürün depolama, işleme ve muhafaza tesisleri",
                "structures": [
                    {"id": 5, "name": "Hububat ve yem depolama silosu", "url_key": "hububat-silo"},
                    {"id": 6, "name": "Tarımsal amaçlı depo", "url_key": "tarimsal-depo"},
                    {"id": 7, "name": "Lisanslı depolar", "url_key": "lisansli-depo"},
                    {"id": 8, "name": "Tarımsal ürün yıkama tesisi", "url_key": "yikama-tesisi"},
                    {"id": 9, "name": "Hububat, çeltik, ayçiçeği kurutma tesisi", "url_key": "kurutma-tesisi"},
                    {"id": 10, "name": "Açıkta meyve/sebze kurutma alanı", "url_key": "meyve-sebze-kurutma"},
                    {"id": 11, "name": "Zeytinyağı fabrikası", "url_key": "zeytinyagi-fabrikasi"},
                    {"id": 16, "name": "Soğuk hava deposu", "url_key": "soguk-hava-deposu"},
                    {"id": 28, "name": "Zeytinyağı üretim tesisi", "url_key": "zeytinyagi-uretim-tesisi"},
                ]
            },
            "ozel_uretim": {
                "name": "Özel Üretim Tesisleri",
                "icon": "🌱",
                "description": "Sera, mantar, arıcılık gibi özel üretim tesisleri",
                "structures": [
                    {"id": 1, "name": "Solucan ve solucan gübresi üretim tesisi", "url_key": "solucan-tesisi"},
                    {"id": 2, "name": "Mantar üretim tesisi", "url_key": "mantar-tesisi"},
                    {"id": 3, "name": "Sera", "url_key": "sera"},
                    {"id": 4, "name": "Arıcılık tesisleri", "url_key": "aricilik"},
                    {"id": 25, "name": "İpek böcekçiliği tesisi", "url_key": "ipek-bocekciligi"},
                ]
            },
            "altyapi": {
                "name": "Altyapı ve Destek Tesisleri",
                "icon": "💧",
                "description": "Su depolama, bağ evi gibi altyapı tesisleri",
                "structures": [
                    {"id": 12, "name": "Su depolama", "url_key": "su-depolama"},
                    {"id": 13, "name": "Su kuyuları", "url_key": "su-kuyulari"},
                    {"id": 14, "name": "Bağ evi", "url_key": "bag-evi"},
                ]
            }
        }
        
        return Response({
            'success': True,
            'data': categories,
            'detail': 'Yapı kategorileri başarıyla getirildi'
        })
    except Exception as e:
        logger.error(f"Yapı kategorileri error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'detail': 'Yapı kategorileri getirilirken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_seo_meta(request):
    """SEO meta verilerini döndüren endpoint"""
    try:
        seo_data = {
            'title': 'Tarımsal Yapılaşma Hesaplama Sistemi | Webimar',
            'description': 'Tarımsal arazilerde yapılaşma hesaplamaları için güvenilir ve hızlı çözümler. 27 farklı yapı türü için yasal uyumlu hesaplama sistemi.',
            'keywords': 'tarımsal yapılaşma, sera hesaplama, hayvancılık tesisi, tarımsal depo, emsal hesaplama, ziraat mühendisliği',
            'og_title': 'Tarımsal Yapılaşma Hesaplama Sistemi',
            'og_description': 'Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata uygun hesaplama çözümleri',
            'og_image': 'https://tarimimar.com.tr/static/images/webimar-og-image.jpg',
            'canonical_url': 'https://tarimimar.com.tr/',
            'schema_data': {
                '@context': 'https://schema.org',
                '@type': 'SoftwareApplication',
                'name': 'Webimar Tarımsal Yapılaşma Sistemi',
                'description': 'Tarımsal arazilerde yapılaşma hesaplamaları için profesyonel yazılım',
                'url': 'https://tarimimar.com.tr',
                'applicationCategory': 'Engineering',
                'operatingSystem': 'Web Browser',
                'offers': {
                    '@type': 'Offer',
                    'price': '0',
                    'priceCurrency': 'TRY'
                }
            }
        }
        
        return Response({
            'success': True,
            'data': seo_data,
            'detail': 'SEO meta verileri başarıyla getirildi'
        })
    except Exception as e:
        logger.error(f"SEO meta error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'detail': 'SEO meta verileri getirilirken hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculation_history(request):
    """Kullanıcının geçmiş hesaplamalarını döndürür"""
    user = request.user
    
    # Cache key with user identification 
    cache_key = f"calculation_history_{user.id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response({
            'success': True,
            'data': cached_data,
            'detail': 'Geçmiş hesaplamalar başarıyla getirildi (cached)'
        })
    
    # Optimize query with select_related for foreign keys
    queryset = CalculationHistory.objects.filter(user=user).select_related('user').order_by('-created_at')
    serializer = CalculationHistorySerializer(queryset, many=True)
    
    # Cache for 5 minutes (user-specific data should be fresh)
    cache.set(cache_key, serializer.data, 300)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'detail': 'Geçmiş hesaplamalar başarıyla getirildi'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_calculation(request):
    """Hesaplamayı kullanıcı adıyla kaydeder"""
    try:
        safe_data = safe_log_request_data(request.data)
        logger.info(f"Save calculation request data: {safe_data}")
        serializer = CalculationHistoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # IP adresini ekle
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        calculation = serializer.save(
            user=request.user,
            ip_address=ip_address
        )
        
        # Kullanıcı aktivitesini logla
        try:
            log_calculation(
                user=request.user,
                calculation_type=calculation.calculation_type,
                title=calculation.title or 'Başlıksız Hesaplama',
                parameters=calculation.parameters,
                result=calculation.result,
                request=request,
                map_coordinates=calculation.map_coordinates
            )
        except Exception as e:
            logger.warning(f"Hesaplama aktivitesi loglanamadı: {e}")
        
        response_serializer = CalculationHistorySerializer(calculation)
        return Response({
            'success': True,
            'data': response_serializer.data,
            'detail': 'Hesaplama başarıyla kaydedildi'
        })
    except Exception as e:
        logger.error(f"Hesaplama kaydetme hatası: {e}")
        return Response({
            'success': False,
            'detail': 'Bir hata oluştu, hesaplama kaydedilemedi'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculation_detail(request, calculation_id):
    """Belirli bir hesaplamanın detaylarını döndürür"""
    try:
        calculation = CalculationHistory.objects.get(id=calculation_id, user=request.user)
        serializer = CalculationHistorySerializer(calculation)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Hesaplama detayları başarıyla getirildi'
        })
    except CalculationHistory.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Hesaplama bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Hesaplama detayı getirme hatası: {e}")
        return Response({
            'success': False,
            'message': 'Bir hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_calculation(request, calculation_id):
    """Belirli bir hesaplamayı siler"""
    try:
        calculation = CalculationHistory.objects.get(id=calculation_id, user=request.user)
        calculation.delete()
        return Response({
            'success': True,
            'message': 'Hesaplama başarıyla silindi'
        })
    except CalculationHistory.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Hesaplama bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Hesaplama silme hatası: {e}")
        return Response({
            'success': False,
            'message': 'Hesaplama silinirken bir hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
