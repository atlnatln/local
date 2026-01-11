from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Amazon SES SMTP ile email gönderim servisi
    """
    
    @staticmethod
    def _resolve_recipient(to_email, force_admin=False):
        """Alıcı adresini belirle. force_admin True ise admin'e yönlendir."""
        if force_admin:
            return settings.ADMIN_NOTIFICATION_EMAIL
        return to_email
    
    @staticmethod
    def send_simple_email(to_email, subject, message, from_email=None, force_admin=False):
        """
        Basit text email gönder (isteğe bağlı admin’e yönlendirme)
        """
        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            recipient = EmailService._resolve_recipient(to_email, force_admin=force_admin)
            
            result = send_mail(
                subject=f"{settings.EMAIL_SUBJECT_PREFIX}{subject}",
                message=message,
                from_email=from_email,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            logger.info(f"Email gönderildi: {recipient} - {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Email gönderim hatası: {e}")
            return False
    
    @staticmethod
    def send_html_email(to_email, subject, html_content, text_content=None, from_email=None, force_admin=False):
        """
        HTML email gönder (isteğe bağlı admin’e yönlendirme)
        """
        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            recipient = EmailService._resolve_recipient(to_email, force_admin=force_admin)
            
            # HTML'den text çıkar
            if not text_content:
                text_content = strip_tags(html_content)
            
            email = EmailMessage(
                subject=f"{settings.EMAIL_SUBJECT_PREFIX}{subject}",
                body=html_content,
                from_email=from_email,
                to=[recipient],
            )
            email.content_subtype = "html"
            
            result = email.send(fail_silently=False)
            
            logger.info(f"HTML Email gönderildi: {recipient} - {subject}")
            return result
            
        except Exception as e:
            logger.error(f"HTML Email gönderim hatası: {e}")
            return False
    
    @staticmethod
    def send_template_email(to_email, subject, template_name, context, from_email=None, force_admin=False):
        """
        Template ile email gönder (isteğe bağlı admin’e yönlendirme)
        """
        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            recipient = EmailService._resolve_recipient(to_email, force_admin=force_admin)
            
            # HTML template render et
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = render_to_string(f'emails/{template_name}.txt', context)
            
            email = EmailMessage(
                subject=f"{settings.EMAIL_SUBJECT_PREFIX}{subject}",
                body=html_content,
                from_email=from_email,
                to=[recipient],
            )
            email.content_subtype = "html"
            
            result = email.send(fail_silently=False)
            
            logger.info(f"Template Email gönderildi: {recipient} - {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Template Email gönderim hatası: {e}")
            return False
    
    @staticmethod
    def send_bulk_email(email_list, subject, message, from_email=None, force_admin=False):
        """
        Toplu email gönder (kritik akışlarda tek admin’e yönlendir)
        """
        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            recipients = [settings.ADMIN_NOTIFICATION_EMAIL] if force_admin else email_list
            
            result = send_mail(
                subject=f"{settings.EMAIL_SUBJECT_PREFIX}{subject}",
                message=message,
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            logger.info(f"Toplu email gönderildi: {len(recipients)} alıcı - {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Toplu email gönderim hatası: {e}")
            return False

# Özel email fonksiyonları (kullanıcıya değil admin’e yönlendirecek şekilde)
def send_welcome_email(user_email, username):
    """Hoş geldin emaili (admin’e bilgi amaçlı)"""
    return EmailService.send_simple_email(
        to_email=settings.ADMIN_NOTIFICATION_EMAIL,
        subject="Yeni Kayıt - Hoş Geldiniz",
        message=f"Yeni kullanıcı kaydı: {username} ({user_email})",
        force_admin=True
    )

def send_password_reset_email(user_email, reset_link):
    """Şifre sıfırlama emaili (admin’e bilgi ve link)"""
    message = f"""
    Şifre sıfırlama talebi alındı.
    Kullanıcı: {user_email}
    Link: {reset_link}
    """
    return EmailService.send_simple_email(
        to_email=settings.ADMIN_NOTIFICATION_EMAIL,
        subject="Şifre Sıfırlama Talebi",
        message=message,
        force_admin=True
    )

def send_calculation_report_email(user_email, calculation_data):
    """Hesaplama raporu emaili (admin’e bilgi)"""
    message = f"""
    Hesaplama raporu hazırlandı.
    Kullanıcı: {user_email}
    Tip: {calculation_data.get('type', 'Bilinmiyor')}
    Sonuç: {calculation_data.get('result', 'Bilinmiyor')}
    """
    return EmailService.send_simple_email(
        to_email=settings.ADMIN_NOTIFICATION_EMAIL,
        subject="Hesaplama Raporu Bilgisi",
        message=message,
        force_admin=True
    )
