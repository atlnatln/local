import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/androidpublisher']


def get_android_publisher_service():
    """
    Google Play Developer API servisi oluştur.

    GOOGLE_PLAY_SERVICE_ACCOUNT_JSON ortam değişkeni iki biçimi destekler:
      - Dosya yolu : '/path/to/service-account.json'
      - JSON string: '{"type":"service_account","project_id":"...",...}'
    """
    json_config = settings.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON

    # JSON string mi, dosya yolu mu?
    if isinstance(json_config, str) and json_config.strip().startswith('{'):
        info = json.loads(json_config)
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )
    else:
        credentials = service_account.Credentials.from_service_account_file(
            str(json_config), scopes=SCOPES
        )
    return build('androidpublisher', 'v3', credentials=credentials)


def verify_purchase(purchase_token: str, product_id: str) -> dict:
    """
    Google Play Developer API ile satın alma doğrulama.

    Returns:
        dict: {
            'valid': bool,
            'order_id': str,
            'purchase_state': int,  # 0=purchased, 1=canceled, 2=pending
            'consumption_state': int,  # 0=not consumed, 1=consumed
            'raw_response': dict
        }
    """
    try:
        service = get_android_publisher_service()
        result = service.purchases().products().get(
            packageName=settings.GOOGLE_PLAY_PACKAGE_NAME,
            productId=product_id,
            token=purchase_token
        ).execute()

        purchase_state = result.get('purchaseState', -1)
        consumption_state = result.get('consumptionState', -1)
        order_id = result.get('orderId', '')

        # purchaseState=0 → satın alma tamamlandı
        is_valid = purchase_state == 0

        logger.info(
            "Purchase verification: product=%s, valid=%s, state=%s, order=%s",
            product_id, is_valid, purchase_state, order_id
        )

        return {
            'valid': is_valid,
            'order_id': order_id,
            'purchase_state': purchase_state,
            'consumption_state': consumption_state,
            'raw_response': result,
        }

    except FileNotFoundError:
        logger.error("Google service account JSON dosyası bulunamadı: %s",
                      settings.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON)
        return {'valid': False, 'error': 'Service account config missing'}

    except Exception as e:
        logger.error("Google Play API doğrulama hatası: %s", str(e))
        return {'valid': False, 'error': str(e)}
