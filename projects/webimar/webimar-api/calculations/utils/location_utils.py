"""
Konum kontrol yardımcı fonksiyonları.
Büyük ova, İzmir sınır kontrolleri ve su kısıtı kontrolü için kullanılır.
"""
from typing import Dict, Optional, Tuple

from maps.kml_helper import (
    check_point_in_polygons,
    get_kml_polygons,
    get_province_polygons,
    get_district_polygons,
    get_yas_kapali_polygons,
)
from .water_restrictions import is_water_restricted_area, get_water_restriction_message


def check_location_status(latitude: float, longitude: float) -> Dict[str, any]:
    """
    Verilen koordinat için lokasyon bilgilerini kontrol eder.
    
    Args:
        latitude: Enlem değeri
        longitude: Boylam değeri
    
    Returns:
        dict: Lokasyon durumu bilgileri
    """
    result = {
        'coordinates': {
            'latitude': latitude,
            'longitude': longitude
        },
        'buyuk_ova_icinde': False,
        'buyuk_ova_adi': None,
        'yas_kapali_icinde': False,
        'yas_kapali_adi': None,
        'province': None,
        'district': None,
        'location_valid': True,
        'location_message': None
    }
    
    try:
        # Büyük ova kontrolü
        buyuk_ova_polygons, buyuk_ova_names = get_kml_polygons()
        buyuk_ova_list = check_point_in_polygons(
            latitude, longitude,
            buyuk_ova_polygons, buyuk_ova_names
        )

        if buyuk_ova_list:
            result['buyuk_ova_icinde'] = True
            result['buyuk_ova_adi'] = buyuk_ova_list[0]

        # YAS kapalı alan kontrolü
        yas_polygons, yas_names = get_yas_kapali_polygons()
        yas_list = check_point_in_polygons(
            latitude, longitude,
            yas_polygons, yas_names
        )

        if yas_list:
            result['yas_kapali_icinde'] = True
            result['yas_kapali_adi'] = yas_list[0]

        # İl ve ilçe bilgisi
        province_polygons, province_names = get_province_polygons()
        province_list = check_point_in_polygons(
            latitude, longitude,
            province_polygons, province_names
        )
        if province_list:
            result['province'] = province_list[0]

        district_polygons, district_names = get_district_polygons()
        district_list = check_point_in_polygons(
            latitude, longitude,
            district_polygons, district_names
        )
        if district_list:
            result['district'] = district_list[0]
        
        # Su kısıtı kontrolü
        if result['province'] and result['district']:
            result['su_kisiti_var'] = is_water_restricted_area(
                result['province'], 
                result['district']
            )
        else:
            result['su_kisiti_var'] = False
        
    except Exception as e:
        print(f"Lokasyon kontrol hatası: {e}")
        result['location_valid'] = False
        result['location_message'] = 'Konum kontrolünde hata oluştu.'
    
    return result


def format_buyuk_ova_message(location_status: Dict[str, any]) -> Optional[str]:
    """
    Büyük ova durumuna göre kullanıcıya gösterilecek mesajı formatlar.
    
    Args:
        location_status: check_location_status fonksiyonundan dönen sonuç
    
    Returns:
        str: Kullanıcıya gösterilecek mesaj veya None
    """
    if not location_status['location_valid']:
        return location_status['location_message']
    
    if location_status['buyuk_ova_icinde']:
        ova_adi = location_status['buyuk_ova_adi']
        return f"📍 Bu konum {ova_adi} büyük ovası içerisinde bulunmaktadır."
    
    return None


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """
    Koordinat değerlerinin geçerliliğini kontrol eder.
    
    Args:
        latitude: Enlem değeri
        longitude: Boylam değeri
    
    Returns:
        tuple: (geçerli_mi, hata_mesajı)
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False, "Koordinat değerleri sayısal olmalıdır."
    
    if not (-90 <= latitude <= 90):
        return False, "Enlem değeri -90 ile 90 arasında olmalıdır."
    
    if not (-180 <= longitude <= 180):
        return False, "Boylam değeri -180 ile 180 arasında olmalıdır."
    
    # Türkiye koordinat aralığı (kabaca)
    if not (25 <= longitude <= 46 and 35 <= latitude <= 43):
        return False, "Koordinat değerleri Türkiye sınırları dışında görünmektedir."
    
    return True, ""


def check_water_restrictions_for_livestock(location_info: Dict[str, any], calculation_type: str) -> Tuple[bool, Optional[str]]:
    """
    Büyükbaş hayvancılık hesaplamaları için su kısıtı kontrolü yapar.
    
    Args:
        location_info: check_location_status() sonucu
        calculation_type: Hesaplama türü
    
    Returns:
        tuple: (devam_edebilir_mi, hata_mesaji)
    """
    from .water_restrictions import is_livestock_calculation_type
    
    # Sadece büyükbaş hayvancılık hesaplamaları için kontrol yap
    if not is_livestock_calculation_type(calculation_type):
        return True, None
    
    # Su kısıtı kontrolü
    if location_info and location_info.get('su_kisiti_var', False):
        return False, get_water_restriction_message()
    
    return True, None
