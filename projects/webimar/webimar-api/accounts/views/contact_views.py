# contact_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
import json
import logging
import requests

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def contact_form_view(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()

        # Basit validasyon
        if not all([name, email, message]):
            return JsonResponse({
                'success': False,
                'detail': 'Tüm alanlar doldurulmalıdır.'
            }, status=400)

        # Email validasyonu
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False,
                'detail': 'Geçerli bir email adresi girin.'
            }, status=400)

        # Telegram Bildirimi (Opsiyonel)
        telegram_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        
        if telegram_token and chat_id:
            try:
                telegram_message = f"📩 *Yeni İletişim Formu Mesajı*\n\n" \
                                   f"👤 *Gönderen:* {name}\n" \
                                   f"📧 *E-posta:* {email}\n\n" \
                                   f"📝 *Mesaj:*\n{message}"
                
                telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                requests.post(telegram_url, data={
                    'chat_id': chat_id,
                    'text': telegram_message,
                    'parse_mode': 'Markdown'
                }, timeout=5)
                logger.info(f"Telegram notification sent to {chat_id}")
            except Exception as tg_error:
                logger.error(f"Telegram sending failed: {str(tg_error)}")
                # Telegram hatası akışı bozmasın

        # Mail gönderimi
        try:
            mail_subject = f"Web Sitesi İletişim Formu - {name}"
            mail_body = f"""
Gönderen: {name}
E-posta: {email}

Mesaj:
{message}

---
Bu mesaj tarım-imar.com.tr web sitesi iletişim formundan gönderilmiştir.
            """
            
            # Development ortamında mail gönderimi atla, sadece log yap
            if settings.DEBUG:
                logger.info(f"Contact form email (DEBUG MODE - not sent): From {email}, Subject: {mail_subject}")
                logger.info(f"Message body: {mail_body}")
                
                return JsonResponse({
                    'success': True,
                    'detail': 'Mesajınız başarıyla gönderildi! (Development Mode)'
                })
            else:
                # Production'da gerçekten mail gönder
                send_mail(
                    subject=mail_subject,
                    message=mail_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,  # info@tarimimar.com.tr (verified email)
                    recipient_list=['info@tarimimar.com.tr'],
                    fail_silently=False,
                )
                
                logger.info(f"Contact form email sent successfully from {email}")
                
                return JsonResponse({
                    'success': True,
                    'detail': 'Mesajınız başarıyla gönderildi!'
                })
            
        except Exception as mail_error:
            logger.error(f"Mail sending failed: {str(mail_error)}")
            return JsonResponse({
                'success': False,
                'detail': 'Mail gönderilemedi. Lütfen daha sonra tekrar deneyin.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'detail': 'Geçersiz JSON verisi.'
        }, status=400)
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return JsonResponse({
            'success': False,
            'detail': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
        }, status=500)
