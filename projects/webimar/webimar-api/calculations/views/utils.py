import logging
from rest_framework.response import Response
from rest_framework import status
import html

logger = logging.getLogger('calculations')

def get_arazi_alani(request_data):
    """Farklı isimlerle gelen arazi alanı parametrelerini standartlaştırır."""
    for key in ["arazi_alani", "alan_m2", "alan", "arazi_buyuklugu", "arazi_buyuklugu_m2", "buyukluk_m2", "arazi_alani_m2"]:
        val = request_data.get(key)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                continue
    return None

def get_emsal_orani(request_data):
    emsal = request_data.get("emsal_orani")
    if emsal is not None:
        try:
            return float(emsal)
        except (ValueError, TypeError):
            return None
    return None

def standard_success_response(data, message=None):
    return Response({
        'success': True,
        'results': data,
        'message': message or 'Hesaplama başarıyla tamamlandı'
    })

def standard_error_response(message, error=None, status_code=status.HTTP_400_BAD_REQUEST):
    logger.error(f"{message}: {error}")
    return Response({
        'success': False,
        'detail': message,
        'error': str(error) if error else None
    }, status=status_code)

def unescape_result_html_fields(result):
    """
    Sonuç sözlüğünde html olarak kullanılacak olan alanların escape'ini kaldırır.
    """
    for key in ['mesaj', 'html_mesaj', 'ana_mesaj']:
        if key in result and isinstance(result[key], str):
            result[key] = html.unescape(result[key])
    # Eğer result altında 'results' veya 'data' alanı varsa orada da uygula
    for subkey in ['results', 'data']:
        if subkey in result and isinstance(result[subkey], dict):
            for key in ['mesaj', 'html_mesaj', 'ana_mesaj']:
                if key in result[subkey] and isinstance(result[subkey][key], str):
                    result[subkey][key] = html.unescape(result[subkey][key])
    return result

def save_calculation_history(user, calculation_type, parameters, result, map_coordinates=None):
    from calculations.models import CalculationHistory
    try:
        # Escape'li HTML içeriği varsa unescape et
        result = unescape_result_html_fields(result)
        CalculationHistory.objects.create(
            user=user,
            calculation_type=calculation_type,
            parameters=parameters,
            result=result,
            map_coordinates=map_coordinates
        )
        logger.info(f"CalculationHistory kaydı oluşturuldu: {user} - {calculation_type}")
    except Exception as e:
        logger.error(f"CalculationHistory kaydı oluşturulurken hata: {str(e)}")
# Ortak yardımcı fonksiyonlar (alan/emsal çekme, validasyon, response vs.)
