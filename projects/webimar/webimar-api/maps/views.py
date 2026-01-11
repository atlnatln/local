from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import logging
from .kml_helper import (
    load_kml_data, check_point_in_polygons,
    get_kml_polygons, get_yas_kapali_polygons, get_province_polygons, get_district_polygons
)

logger = logging.getLogger('maps')

@api_view(['GET'])
def health_check(request):
    """Maps app health check endpoint"""
    return Response({
        'status': 'ok',
        'app': 'maps',
        'detail': 'Maps app is running successfully'
    })

@api_view(['POST'])
def check_coordinate(request):
    """
    Verilen koordinatın hangi poligonların içinde olduğunu kontrol eder.
    
    POST parametreleri:
    - lat: Enlem
    - lng: Boylam
    
    Yanıt:
    - inside_ova_polygons: Koordinatın içinde kaldığı büyük ova poligonlarının listesi (Türkiye geneli)
    - inside_yas_polygons: Koordinatın içinde kaldığı YAS kapalı alan poligonlarının listesi (Türkiye geneli)
    - province: Noktanın bulunduğu il adı (varsa)
    - district: Noktanın bulunduğu ilçe adı (varsa)
    """
    try:
        # İstek verilerini al
        lat = float(request.data.get('lat'))
        lng = float(request.data.get('lng'))
        
        logger.info(f"Coordinate check request: lat={lat}, lng={lng}")
    except (ValueError, TypeError) as e:
        return Response({
            'error': f'Geçersiz koordinat değerleri: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # KML dosyalarını yükle (eğer henüz yüklenmemişse)
        load_kml_data()
        
        # Polygon verilerini thread-safe şekilde al
        polygons, polygon_names = get_kml_polygons()
        yas_polygons, yas_names = get_yas_kapali_polygons()
        province_polygons, province_names = get_province_polygons()
        district_polygons, district_names = get_district_polygons()
        
        # Koordinatı her üç KML için kontrol et
        inside_polygons = check_point_in_polygons(lat, lng, polygons, polygon_names)
        inside_yas_polygons = check_point_in_polygons(lat, lng, yas_polygons, yas_names)
        inside_province = check_point_in_polygons(lat, lng, province_polygons, province_names)
        inside_district = check_point_in_polygons(lat, lng, district_polygons, district_names)

        result = {
            'inside_ova_polygons': inside_polygons,
            'inside_yas_polygons': inside_yas_polygons,
            'province': inside_province[0] if inside_province else None,
            'district': inside_district[0] if inside_district else None,
            'lat': lat,
            'lng': lng,
            'total_ova_polygons': len(polygons),
            'total_yas_polygons': len(yas_polygons),
            'total_provinces': len(province_polygons),
            'total_districts': len(district_polygons),
            # backward compatibility
            'inside_polygons': inside_polygons,
            'inside_kapali_alan_polygons': inside_yas_polygons,
            'in_yas_kapali_alan': len(inside_yas_polygons) > 0,
        }
        
        logger.info(f"Coordinate check result: {result}")
        return Response(result)
        
    except Exception as e:
        logger.error(f"Coordinate check error: {str(e)}")
        return Response({
            'error': f'Koordinat kontrol sırasında hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
