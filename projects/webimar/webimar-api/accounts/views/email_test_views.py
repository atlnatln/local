# Amazon SES SMTP Email Test View
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from utils.email_service import EmailService, send_welcome_email
from django.conf import settings
import json

@require_http_methods(["POST"])
@csrf_exempt
def test_email_send(request):
    """
    Email gönderim test endpoint'i
    POST /api/test-email/
    {
        "email": "test@example.com",
        "type": "simple|welcome|html"
    }
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        email_type = data.get('type', 'simple')
        
        if not email:
            return JsonResponse({
                'success': False,
                'detail': 'Email adresi gerekli'
            }, status=400)
        
        subject = "Test Email"
        message = "Bu bir test emailidir. Amazon SES SMTP çalışıyor! 🎉"
        html_content = """
        <h2>HTML Test Email</h2>
        <p>Bu bir <strong>HTML test emailidir</strong>.</p>
        <p>Amazon SES SMTP başarıyla çalışıyor! 🎉</p>
        """
        text_content = "Bu bir test emailidir. Amazon SES SMTP çalışıyor! 🎉"
        
        if email_type == 'simple':
            success = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject,
                message=message,
                force_admin=True
            )
        elif email_type == 'welcome':
            success = send_welcome_email(email, "Test Kullanıcısı")
        elif email_type == 'html':
            success = EmailService.send_html_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                force_admin=True
            )
        else:
            return JsonResponse({
                'success': False,
                'detail': 'Geçersiz email tipi'
            }, status=400)
        
        return JsonResponse({
            'success': success,
            'detail': 'Email gönderildi' if success else 'Email gönderilemedi',
            'email': email,
            'type': email_type
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'detail': f'Hata: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def test_email_connection(request):
    """
    Email bağlantı test endpoint'i
    GET /api/test-email-connection/
    """
    try:
        success = EmailService.test_email_connection()
        
        return JsonResponse({
            'success': success,
            'detail': 'Email bağlantısı başarılı' if success else 'Email bağlantısı başarısız'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'detail': f'Bağlantı test hatası: {str(e)}'
        }, status=500)
