"""
History views for calculations
Hesaplama geçmişi ile ilgili endpoints.
"""
import logging
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from ..models import CalculationHistory
from ..serializers import CalculationHistorySerializer, CalculationHistoryCreateSerializer
from accounts.utils import log_calculation
from accounts.logging_utils import safe_log_request_data
from ..utils.html_extractor import extract_clean_html_from_result

logger = logging.getLogger('calculations')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculation_history(request):
    """Kullanıcının geçmiş hesaplamalarını döndürür"""
    user = request.user
    queryset = CalculationHistory.objects.filter(user=user).order_by('-created_at')
    serializer = CalculationHistorySerializer(queryset, many=True)
    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Geçmiş hesaplamalar başarıyla getirildi'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_calculation(request):
    """Hesaplamayı kullanıcı adıyla kaydeder"""
    try:
        safe_data = safe_log_request_data(request.data)
        logger.info(f"Save calculation request data: {safe_data}")
        
        # Backend'de HTML temizleme sistemi - Modal wrapper'ları ve zararlı HTML'i temizle
        cleaned_data = request.data.copy()
        if 'result' in cleaned_data and cleaned_data['result']:
            try:
                cleaned_data['result'] = extract_clean_html_from_result(cleaned_data['result'])
                logger.info("HTML extraction and sanitization completed successfully")
            except Exception as e:
                logger.warning(f"HTML cleaning failed, using original result: {e}")
                # Temizleme başarısız olursa orijinal veriyi kullan

        serializer = CalculationHistoryCreateSerializer(data=cleaned_data)
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
                calculation_data=calculation.parameters,
                result_data=calculation.result,
                ip_address=ip_address,
                location_data=calculation.map_coordinates
            )
        except Exception as e:
            logger.warning(f"Hesaplama aktivitesi loglanamadı: {e}")
        
        response_serializer = CalculationHistorySerializer(calculation)
        return Response({
            'success': True,
            'data': response_serializer.data,
            'detail': 'Hesaplama başarıyla kaydedildi'
        })
    except ValidationError as e:
        # Validasyon hataları kullanıcıya detaylı bilgi ile iletilir
        logger.warning(f"Hesaplama kaydetme validasyon hatası: {e}")
        return Response({
            'success': False,
            'message': 'Girilen veriler geçersiz',
            'errors': e.detail if hasattr(e, 'detail') else str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        # Unique constraint ihlali (duplicate kayıt)
        logger.warning(f"Hesaplama kaydetme integrity hatası: {e}")
        return Response({
            'success': False,
            'message': 'Bu hesaplama zaten kaydedilmiş. Farklı bir başlık deneyiniz.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Hesaplama kaydetme hatası: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Hesaplama kaydedilirken beklenmeyen bir hata oluştu'
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
