from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.conf import settings
from utils.email_service import EmailService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class EmailVerificationService:
    """
    Email doğrulama servisi
    """
    
    @staticmethod
    def generate_verification_token(user):
        """Email doğrulama token'ı oluştur"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return token, uid
    
    @staticmethod
    def verify_token(uidb64, token):
        """Token'ı doğrula ve kullanıcıyı döndür"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                return user
            return None
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
    
    @staticmethod
    def send_verification_email(user, request=None):
        """Email doğrulama maili gönder (admin’e)"""
        try:
            token, uid = EmailVerificationService.generate_verification_token(user)
            
            # Verification link oluştur
            if request:
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
            else:
                domain = 'tarimimar.com.tr'  # Default domain
                protocol = 'https'
            
            verification_link = f"{protocol}://{domain}/verify-email/{uid}/{token}/"
            
            # Email içeriği
            subject = "Email Adresinizi Doğrulayın"
            message = f"""
            Merhaba {user.first_name or user.username},
            
            Webimar hesabınızı aktifleştirmek için aşağıdaki linke tıklayın:
            {verification_link}
            
            Bu link 24 saat geçerlidir.
            
            Eğer bu talebi siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.
            
            İyi çalışmalar!
            Webimar Ekibi
            """
            
            success = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject,
                message=message,
                force_admin=True
            )
            
            if success:
                logger.info(f"Email doğrulama maili gönderildi: {user.email}")
            else:
                logger.error(f"Email doğrulama maili gönderilemedi: {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Email doğrulama hatası: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, request=None):
        """Şifre sıfırlama maili gönder (admin’e)"""
        try:
            token, uid = EmailVerificationService.generate_verification_token(user)
            
            # Reset link oluştur
            if request:
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
            else:
                domain = 'tarimimar.com.tr'  # Default domain
                protocol = 'https'
            
            reset_link = f"{protocol}://{domain}/reset-password/{uid}/{token}/"
            
            # Email içeriği
            subject = "Şifre Sıfırlama Talebi"
            message = f"""
            Merhaba {user.first_name or user.username},
            
            Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:
            {reset_link}
            
            Bu link 24 saat geçerlidir.
            
            Eğer bu talebi siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.
            
            İyi çalışmalar!
            Webimar Ekibi
            """
            
            success = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject,
                message=message,
                force_admin=True
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Şifre sıfırlama hatası: {e}")
            return False
    
    @staticmethod
    def send_email_change_verification(user, new_email):
        """E-posta değişikliği doğrulaması (admin’e)"""
        try:
            token, uid = EmailVerificationService.generate_verification_token(user)
            
            # Verification link oluştur (özel e-posta değişikliği linki)
            domain = 'tarimimar.com.tr'
            protocol = 'https'
            change_link = f"{protocol}://{domain}/email-change/{uid}/{token}/?new_email={new_email}"
            
            # Email içeriği
            subject = "E-posta Adresi Değişikliği Doğrulama"
            message = f"""
            Merhaba {user.first_name or user.username},
            
            E-posta adresinizi değiştirmek için aşağıdaki linke tıklayın:
            {change_link}
            
            Bu işlem ile e-posta adresiniz {user.email} adresinden {new_email} adresine değişecektir.
            
            Bu link 24 saat geçerlidir.
            
            Eğer bu talebi siz yapmadıysanız, lütfen mevcut e-posta adresinizde aldığınız bilgilendirme mailini kontrol edin.
            
            İyi çalışmalar!
            Webimar Ekibi
            """
            
            success = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject,
                message=message,
                force_admin=True
            )
            
            return success
            
        except Exception as e:
            logger.error(f"E-posta değişikliği doğrulama hatası: {e}")
            return False
    
    @staticmethod
    def send_email_change_notification(user, new_email):
        """E-posta değişikliği bildirimi (admin’e)"""
        try:
            # Email içeriği
            subject = "E-posta Adresi Değişikliği Talebi"
            message = f"""
            Merhaba {user.first_name or user.username},
            
            Hesabınız için e-posta adresi değişikliği talep edildi.
            
            Mevcut e-posta: {user.email}
            Talep edilen yeni e-posta: {new_email}
            
            Bu talebi siz yaptıysanız, yeni e-posta adresinize gönderilen doğrulama linkine tıklayarak işlemi tamamlayabilirsiniz.
            
            Eğer bu talebi siz yapmadıysanız:
            1. Hesap güvenliğiniz için şifrenizi değiştirin
            2. Bu e-postayı güvenliğinize yönelik bir uyarı olarak değerlendirin
            3. Şüpheli durumda bizimle iletişime geçin
            
            İyi çalışmalar!
            Webimar Ekibi
            """
            
            success = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject,
                message=message,
                force_admin=True
            )
            
            return success
            
        except Exception as e:
            logger.error(f"E-posta değişikliği bildirim hatası: {e}")
            return False
    
    @staticmethod
    def verify_email_change_token(uidb64, token, new_email):
        """E-posta değişikliği token'ını doğrula"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                # Yeni e-posta adresi hala müsait mi kontrol et
                if User.objects.filter(email=new_email).exists():
                    logger.warning(f"E-posta değişikliği sırasında e-posta çakışması: {new_email}")
                    return None
                return user
            return None
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
    
    @staticmethod
    def send_email_change_success_notification(user, old_email, new_email):
        """E-posta değişikliği başarı bildirimi (admin’e)"""
        try:
            # Eski e-posta adresine bildirim
            subject_old = "E-posta Adresi Değiştirildi"
            message_old = f"""
            Merhaba {user.first_name or user.username},
            
            Hesabınızın e-posta adresi başarıyla değiştirildi.
            
            Eski e-posta: {old_email}
            Yeni e-posta: {new_email}
            
            Bu değişikliği siz yapmadıysanız, lütfen derhal bizimle iletişime geçin.
            
            İyi çalışmalar!
            Webimar Ekibi
            """
            
            # Yeni e-posta adresine hoş geldin
            subject_new = "E-posta Adresi Değişikliği Tamamlandı"
            message_new = f"""
            Merhaba {user.first_name or user.username},
            
            E-posta adresi değişikliğiniz başarıyla tamamlandı!
            
            Artık hesabınıza {new_email} adresi ile erişebilirsiniz.
            
            İyi çalışmalar!
            Webimar Ekibi
            """
            
            # Her iki e-postaya da gönder
            success_old = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject_old,
                message=message_old,
                force_admin=True
            )
            
            success_new = EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject=subject_new,
                message=message_new,
                force_admin=True
            )
            
            logger.info(f"E-posta değişikliği başarı bildirimi gönderildi: {old_email} -> {new_email}")
            return success_old and success_new
            
        except Exception as e:
            logger.error(f"E-posta değişikliği başarı bildirimi hatası: {e}")
            return False
