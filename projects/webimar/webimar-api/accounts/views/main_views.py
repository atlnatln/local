from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from accounts.throttles import RegisterRateThrottle, handle_throttle_exception, EmailVerificationRateThrottle
from accounts.test_decorators import conditional_throttle_classes, conditional_handle_throttle_exception
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import os
from django.db import transaction
import logging
from accounts.models import UserProfile, UserSession, SecurityEvent
from accounts.serializers import UserDetailSerializer, UserProfileSerializer, UserSessionSerializer
from accounts.utils import log_user_activity, update_user_session, log_security_event

logger = logging.getLogger(__name__)

def validate_username_custom(username):
    """Kullanıcı adı validasyonu"""
    if not username:
        raise ValidationError('Kullanıcı adı gereklidir.')
    
    if len(username) < 3:
        raise ValidationError('Kullanıcı adı en az 3 karakter olmalıdır.')
    
    if len(username) > 30:
        raise ValidationError('Kullanıcı adı en fazla 30 karakter olmalıdır.')
    
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError('Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir.')

def validate_email_custom(email):
    """E-posta validasyonu"""
    if not email:
        raise ValidationError('E-posta adresi gereklidir.')
    
    import re
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        raise ValidationError('Geçerli bir e-posta adresi girin.')

@api_view(['POST'])
@conditional_throttle_classes([RegisterRateThrottle])
@conditional_handle_throttle_exception
def register(request):
    """Kullanıcı kaydı endpoint'i - Admin Onaylı Sistem + Atomic İşlem"""
    email = request.data.get('email')
    username = request.data.get('username')
    # Şifre artık isteğe bağlı (admin onaylı sistemde admin oluşturacak)
    password = request.data.get('password', None)
    password_provided = 'password' in request.data
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

    # E-posta normalizasyonu (küçük harfe çevir, boşlukları temizle)
    if email:
        email = email.strip().lower()
    if username:
        username = username.strip()

    if not email or not username:
        # Güvenlik olayını kaydet
        log_security_event(
            'failed_register', 
            ip, 
            'Eksik alan ile kayıt denemesi',
            request,
            username_attempted=username,
            email_attempted=email,
            metadata={'missing_fields': True}
        )
        return Response({'detail': 'E-posta ve kullanıcı adı gerekli.'}, status=status.HTTP_400_BAD_REQUEST)

    # Eğer şifre alanı gönderildiyse ancak boşsa 400 döndür
    if password_provided and not password:
        return Response({'detail': 'Şifre çok kısa. En az 4 karakter olmalı.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Atomic işlem - tüm database değişiklikleri bir arada yapılır
        with transaction.atomic():
            logger.info(f"Registration attempt: {username} - {email} from IP: {ip}")
            
            # E-posta validasyonu
            validate_email_custom(email)

            # Kullanıcı adı validasyonu
            validate_username_custom(username)

            # Kullanıcı adı benzersizlik kontrolü
            if User.objects.filter(username=username).exists():
                log_security_event(
                    'failed_register',
                    ip,
                    'Var olan kullanıcı adı ile kayıt denemesi',
                    request,
                    username_attempted=username,
                    email_attempted=email,
                    metadata={'reason': 'username_exists'}
                )
                return Response({'detail': 'Bu kullanıcı adı zaten kullanılıyor.'}, status=status.HTTP_400_BAD_REQUEST)

            # E-posta benzersizlik kontrolü (normalize edilmiş e-posta ile)
            if User.objects.filter(email=email).exists():
                log_security_event(
                    'failed_register',
                    ip,
                    'Var olan e-posta ile kayıt denemesi',
                    request,
                    username_attempted=username,
                    email_attempted=email,
                    metadata={'reason': 'email_exists'}
                )
                return Response({'detail': 'Bu e-posta adresi zaten kullanılıyor.'}, status=status.HTTP_400_BAD_REQUEST)

            # Admin onaylı sistem: Kullanıcı pasif olarak oluşturulur
            password_self_chosen = False
            if password:
                # Eğer şifre verilmişse (kullanıcı kendisi belirledi)
                if len(password) < 4:
                    return Response({'detail': 'Şifre çok kısa. En az 4 karakter olmalı.'}, status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.create_user(username=username, password=password, email=email)
                password_self_chosen = True
                logger.info(f"User created with self-chosen password: {username}")
            else:
                # Şifre verilmemişse geçici şifre ile oluştur (admin değiştirecek)
                user = User.objects.create_user(username=username, password='temp123', email=email)
                password_self_chosen = False
                logger.info(f"User created with temp password: {username}")
            
            # Admin onaylı sistem: Kullanıcı pasif olarak bekletilir
            user.is_active = False
            user.save()

            # Profil bilgisini güncelle (atomic blok içinde)
            try:
                profile = user.profile
                profile.password_self_chosen = password_self_chosen
                # Pasif kullanıcılar için aktivasyon bekliyor durumunu ayarla
                if not user.is_active:
                    profile.awaiting_activation = True
                    profile.activation_mail_sent = False
                profile.save()
                logger.info(f"User profile configured: {username} - awaiting_activation: True")
            except Exception as profile_error:
                logger.error(f"Profile creation error for {username}: {profile_error}")
                # Profile hatası kayıt sürecini durdurmasın
                pass

            # Kullanıcı aktivitesini kaydet (atomic blok içinde)
            try:
                log_user_activity(user, 'REGISTER_PENDING', 'Admin onayı bekleyen kullanıcı kaydı yapıldı', request)
                logger.info(f"User activity logged: {username} - REGISTER_PENDING")
            except Exception as log_error:
                logger.error(f"Activity logging error for {username}: {log_error}")
                # Log hatası kayıt sürecini durdurmasın
                pass

        # Atomic blok dışında - Admin'e bildirim gönder (hata olsa kayıt etkilenmesin)
        try:
            from accounts.admin import send_admin_registration_notification
            send_admin_registration_notification(user)
            logger.info(f"Admin notification sent for: {username}")
        except Exception as email_error:
            logger.error(f"Admin notification error for {username}: {email_error}")
            # Admin bildirimi hatası kayıt başarısını etkilemez
            pass

        logger.info(f"Registration completed successfully: {username} - {email}")

        # Admin onaylı sistem mesajı
        return Response({
            'detail': 'Kayıt talebiniz alınmıştır. Admin onayından sonra hesabınız açılacaktır.',
            'admin_approval_required': True,
            'status': 'pending_approval'
        }, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        # ValidationError mesajını düzgün çıkar
        if hasattr(e, 'message'):
            error_message = e.message
        elif hasattr(e, 'messages') and e.messages:
            error_message = e.messages[0] if isinstance(e.messages, list) else str(e.messages)
        else:
            error_message = str(e).strip("[]'\"")
        
        logger.warning(f"Registration validation error for {username}: {error_message}")
        
        log_security_event(
            'failed_register',
            ip,
            f'Validasyon hatası: {error_message}',
            request,
            username_attempted=username if username else None,
            email_attempted=email if email else None,
            metadata={'validation_error': error_message}
        )
        return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Registration error for {username}: {str(e)}")
        
        log_security_event(
            'failed_register',
            ip,
            f'Beklenmeyen hata: {str(e)}',
            request,
            username_attempted=username if username else None,
            email_attempted=email if email else None,
            metadata={'exception': str(e), 'exception_type': type(e).__name__}
        )
        return Response({'detail': f'Kullanıcı kaydı sırasında hata oluştu: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def health_check(request):
    """Accounts app health check endpoint"""
    return Response({
        'status': 'ok',
        'app': 'accounts',
        'detail': 'Accounts app is running successfully'
    })

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    
    # UserProfile signal ile otomatik oluşturulur, manual çağrı gereksiz
    # Oturumu güncelle
    update_user_session(user, request)
    
    if request.method == 'GET':
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        try:
            # Kullanıcı temel bilgilerini güncelle
            username = request.data.get('username')
            email = request.data.get('email')
            
            if username:
                # Kullanıcı adı validasyonu
                try:
                    validate_username_custom(username.strip())
                except ValidationError as e:
                    # ValidationError mesajını düzgün çıkar
                    if hasattr(e, 'message'):
                        error_message = e.message
                    elif hasattr(e, 'messages') and e.messages:
                        error_message = e.messages[0] if isinstance(e.messages, list) else str(e.messages)
                    else:
                        error_message = str(e).strip("[]'\"")
                    return Response({'username': [error_message]}, status=status.HTTP_400_BAD_REQUEST)
                
                # Kullanıcı adı benzersizlik kontrolü
                if User.objects.filter(username=username.strip()).exclude(id=user.id).exists():
                    return Response({'username': ['Bu kullanıcı adı zaten kullanılıyor.']}, status=status.HTTP_400_BAD_REQUEST)
                user.username = username.strip()
                
            if email:
                # E-posta değişikliği artık güvenli akış ile yapılıyor
                return Response({
                    'detail': 'E-posta değişikliği için /api/accounts/request-email-change/ endpoint\'ini kullanın.',
                    'info': 'Güvenlik nedeniyle e-posta değişikliği artık doğrulama gerektiriyor.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            user.save()
            
            # Aktiviteyi kaydet
            log_user_activity(
                user=user,
                activity_type='profile_update',
                description='Profil bilgilerini güncelledi',
                request=request
            )
            
            serializer = UserDetailSerializer(user, context={'request': request})
            return Response({
                **serializer.data,
                'detail': 'Profil başarıyla güncellendi.'
            })
        except Exception as e:
            return Response({'detail': f'Profil güncellenirken hata oluştu: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not old_password or not new_password:
        return Response({'detail': 'Mevcut ve yeni şifre gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
    if not user.check_password(old_password):
        return Response({'detail': 'Mevcut şifre yanlış.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Yeni şifre doğrulama: En az 4 karakter
    if len(new_password) < 4:
        return Response({'detail': 'Şifre çok kısa. En az 4 karakter olmalı.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    # Aktiviteyi kaydet
    log_user_activity(
        user=user,
        activity_type='password_change',
        description='Şifresini değiştirdi',
        request=request
    )
    
    return Response({'detail': 'Şifre başarıyla değiştirildi.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_sessions(request):
    """Kullanıcının son 1 ay oturum geçmişini listele"""
    user = request.user
    
    # Son 1 ayın oturumlarını getir (aktif ve pasif)
    one_month_ago = timezone.now() - timedelta(days=30)
    sessions = UserSession.objects.filter(
        user=user, 
        login_time__gte=one_month_ago
    ).order_by('-last_activity')
    
    serializer = UserSessionSerializer(sessions, many=True)
    return Response({
        'sessions': serializer.data,
        'total_count': sessions.count(),
        'active_count': sessions.filter(is_active=True).count()
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def terminate_session(request, session_key):
    """Belirtilen oturumu sonlandır"""
    try:
        session = UserSession.objects.get(session_key=session_key, user=request.user)
        session.is_active = False
        session.save()
        return Response({'detail': 'Oturum başarıyla sonlandırıldı.'})
    except UserSession.DoesNotExist:
        return Response({'detail': 'Oturum bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Kullanıcı çıkış işlemi - mevcut oturumu sonlandır"""
    try:
        # Mevcut request'in session_key'ini bul
        current_session_key = request.session.session_key
        
        # Session'ı pasifleştir
        from accounts.utils import deactivate_user_sessions_on_logout
        deactivated_count = deactivate_user_sessions_on_logout(
            user=request.user, 
            session_key=current_session_key
        )
        
        # Kullanıcı aktivitesini logla
        log_user_activity(
            user=request.user,
            activity_type='logout',
            description='Kullanıcı çıkış yaptı',
            request=request
        )
        
        return Response({
            'detail': 'Çıkış işlemi başarılı.',
            'detail': 'Oturum sonlandırıldı.',
            'deactivated_sessions': deactivated_count
        })
        
    except Exception as e:
        return Response({
            'detail': 'Çıkış işlemi sırasında hata oluştu.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Şifre sıfırlama talebi - Admin onaylı sistem"""
    email = request.data.get('email')
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    
    if not email:
        return Response({
            'detail': 'E-posta adresi gereklidir.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # E-posta validasyonu
        validate_email_custom(email.strip())
        
        # Kullanıcıyı bul
        user = User.objects.filter(email=email.strip()).first()
        if not user:
            # Güvenlik: E-posta bulunamasa bile başarılı mesaj göster
            return Response({
                'detail': 'Şifre sıfırlama talebi alınmıştır. Admin onayından sonra yeni şifreniz e-posta ile gönderilecektir.',
                'requires_login': True
            }, status=status.HTTP_200_OK)
        
        # Admin'e şifre sıfırlama talebi bildirimi gönder
        try:
            admin_panel_url = "https://tarimimar.com.tr/admin/auth/user/"
            admin_user_url = f"https://tarimimar.com.tr/admin/auth/user/{user.id}/change/"
            
            message = f"""
Şifre Sıfırlama Talebi

Kullanıcı Adı: {user.username}
E-posta: {user.email}
Tarih: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
IP Adresi: {ip}

Bu kullanıcının şifresini sıfırlamak için aşağıdaki linklerden admin panele giriş yapın:

🔗 Admin Panel - Kullanıcılar: {admin_panel_url}
👤 Bu Kullanıcı: {admin_user_url}

Şifre sıfırlama adımları:
1. Yukarıdaki linke tıklayarak admin panele giriş yapın
2. Kullanıcı sayfasında "✅ Aktif Et ve Şifre Gönder" butonuna basın
3. Yeni şifre otomatik olarak oluşturulup admin e-postasına gönderilecek
            """
            
            from utils.email_service import EmailService
            EmailService.send_simple_email(
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
                subject="Şifre Sıfırlama Talebi - Admin İşlemi Gerekli",
                message=message
            )
        except Exception as email_error:
            pass
        
        # Güvenlik olayını kaydet
        log_security_event(
            'password_reset_requested',
            ip,
            'Şifre sıfırlama talep edildi',
            request,
            user_id=user.id if user else None,
            username_attempted=user.username if user else None,
            email_attempted=email.strip(),
            metadata={'admin_approval_required': True}
        )
        
        return Response({
            'detail': 'Şifre sıfırlama talebi alınmıştır. Admin onayından sonra yeni şifreniz e-posta ile gönderilecektir.',
            'requires_login': True
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        if hasattr(e, 'message'):
            error_message = e.message
        elif hasattr(e, 'messages') and e.messages:
            error_message = e.messages[0] if isinstance(e.messages, list) else str(e.messages)
        else:
            error_message = str(e).strip("[]'\"")
        return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'detail': 'Şifre sıfırlama talebi işlenirken hata oluştu.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """Kullanıcı hesabını sil - Şifre doğrulaması ile"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Debug: İsteğin detaylarını logla
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    logger.warning(f"🔥 DELETE ACCOUNT REQUEST - User: {request.user}, IP: {ip}, User-Agent: {user_agent[:100]}")
    
    user = request.user
    password = request.data.get('password')
    
    if not password:
        return Response({
            'detail': 'Hesap silme işlemi için mevcut şifrenizi girmeniz gereklidir.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Şifre doğrulaması
    if not user.check_password(password):
        # Güvenlik olayı kaydet
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        log_security_event(
            'failed_account_deletion',
            ip,
            'Yanlış şifre ile hesap silme denemesi',
            request,
            user_id=user.id,
            username_attempted=user.username,
            metadata={'reason': 'wrong_password'}
        )
        return Response({
            'detail': 'Mevcut şifreniz yanlış. Hesap silme işlemi iptal edildi.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Güvenlik olayını kaydet
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        log_security_event(
            'account_deleted',
            ip,
            'Kullanıcı hesabını sildi',
            request,
            user_id=user.id,
            username_attempted=user.username,
            metadata={'deletion_confirmed': True}
        )
        
        # Kullanıcı hesabını sil
        username = user.username
        user.delete()
        
        return Response({
            'detail': 'Hesap başarıyla silindi.',
            'detail': f'{username} hesabı kalıcı olarak silindi.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'detail': 'Hesap silinirken bir hata oluştu.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_username_unique(request):
    """Kullanıcı adı benzersizliğini kontrol et"""
    username = request.data.get('value', '').strip()
    if not username:
        return Response({'is_unique': False, 'detail': 'Kullanıcı adı gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Eğer kullanıcı giriş yapmışsa, kendi kullanıcı adını kontrol etme
    if request.user.is_authenticated and username == request.user.username:
        return Response({'is_unique': True})
    
    # Başka kullanıcıda bu kullanıcı adı var mı?
    exists = User.objects.filter(username=username).exists()
    
    return Response({
        'is_unique': not exists,
        'detail': 'Bu kullanıcı adı zaten kullanılıyor.' if exists else 'Kullanıcı adı müsait.'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_unique(request):
    """Email benzersizliğini kontrol et"""
    email = request.data.get('value', '').strip()
    if not email:
        return Response({'is_unique': False, 'detail': 'Email gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Eğer kullanıcı giriş yapmışsa, kendi email'ini kontrol etme
    if request.user.is_authenticated and email == request.user.email:
        return Response({'is_unique': True})
    
    # Başka kullanıcıda bu email var mı?
    exists = User.objects.filter(email=email).exists()
    
    return Response({
        'is_unique': not exists,
        'detail': 'Bu email zaten kullanılıyor.' if exists else 'Email müsait.'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@conditional_throttle_classes([EmailVerificationRateThrottle])
@conditional_handle_throttle_exception
def request_email_change(request):
    """
    E-posta değişikliği talebi - güvenli akış
    POST /api/accounts/request-email-change/
    {
        "new_email": "yeni@email.com",
        "password": "kullanici_sifresi"
    }
    """
    user = request.user
    new_email = request.data.get('new_email')
    password = request.data.get('password')
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    
    if not new_email or not password:
        return Response({
            'detail': 'Yeni e-posta adresi ve şifre gereklidir.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Şifre kontrolü
    if not user.check_password(password):
        log_security_event(
            'failed_email_change',
            ip,
            'Yanlış şifre ile e-posta değiştirme denemesi',
            request,
            user_id=user.id,
            username_attempted=user.username,
            email_attempted=new_email,
            metadata={'reason': 'wrong_password'}
        )
        return Response({
            'detail': 'Mevcut şifreniz yanlış.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # E-posta validasyonu
    try:
        validate_email_custom(new_email.strip())
    except ValidationError as e:
        # ValidationError mesajını düzgün çıkar
        if hasattr(e, 'message'):
            error_message = e.message
        elif hasattr(e, 'messages') and e.messages:
            error_message = e.messages[0] if isinstance(e.messages, list) else str(e.messages)
        else:
            error_message = str(e).strip("[]'\"")
        return Response({
            'detail': error_message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Yeni e-posta aynı ise hata ver
    if user.email == new_email.strip():
        return Response({
            'detail': 'Yeni e-posta adresi mevcut adresinizle aynı.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Yeni e-posta başka kullanıcıda var mı kontrol et
    if User.objects.filter(email=new_email.strip()).exists():
        log_security_event(
            'failed_email_change',
            ip,
            'Var olan e-posta ile değiştirme denemesi',
            request,
            user_id=user.id,
            username_attempted=user.username,
            email_attempted=new_email.strip(),
            metadata={'reason': 'email_exists'}
        )
        return Response({
            'detail': 'Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from utils.email_verification import EmailVerificationService
        email_service = EmailVerificationService()
        
        # Yeni e-posta adresine doğrulama maili gönder
        verification_sent = email_service.send_email_change_verification(
            user=user,
            new_email=new_email.strip()
        )
        
        if verification_sent:
            # Eski e-posta adresine bilgilendirme maili gönder
            notification_sent = email_service.send_email_change_notification(
                user=user,
                new_email=new_email.strip()
            )
            
            # Güvenlik olayını kaydet
            log_security_event(
                'email_change_requested',
                ip,
                'E-posta değişikliği talep edildi',
                request,
                user_id=user.id,
                username_attempted=user.username,
                email_attempted=new_email.strip(),
                metadata={
                    'old_email': user.email,
                    'new_email': new_email.strip(),
                    'verification_sent': verification_sent,
                    'notification_sent': notification_sent
                }
            )
            
            return Response({
                'detail': 'E-posta değişikliği talebi alındı. Yeni e-posta adresinize doğrulama linki gönderildi.',
                'detail': 'Ayrıca mevcut e-posta adresinize bilgilendirme maili gönderildi.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'E-posta gönderiminde hata oluştu. Lütfen tekrar deneyin.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        log_security_event(
            'email_change_error',
            ip,
            f'E-posta değişikliği hatası: {str(e)}',
            request,
            user_id=user.id,
            username_attempted=user.username,
            email_attempted=new_email.strip() if new_email else None,
            metadata={'exception': str(e), 'exception_type': type(e).__name__}
        )
        return Response({
            'detail': 'E-posta değişikliği sırasında hata oluştu. Lütfen tekrar deneyin.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_email_change(request):
    """
    E-posta değişikliğini onaylama
    POST /api/accounts/confirm-email-change/
    {
        "uid": "base64_user_id",
        "token": "verification_token",
        "new_email": "yeni@email.com"
    }
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_email = request.data.get('new_email')
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    
    if not uid or not token or not new_email:
        return Response({
            'detail': 'UID, token ve yeni e-posta adresi gereklidir.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from utils.email_verification import EmailVerificationService
        email_service = EmailVerificationService()
        
        # Token'ı doğrula ve kullanıcıyı bul
        user = email_service.verify_email_change_token(uid, token, new_email)
        
        if user:
            old_email = user.email
            
            # E-posta adresini değiştir
            user.email = new_email.strip()
            user.save()
            
            # Güvenlik olayını kaydet
            log_security_event(
                'email_changed',
                ip,
                'E-posta adresi başarıyla değiştirildi',
                request,
                user_id=user.id,
                username_attempted=user.username,
                email_attempted=new_email.strip(),
                metadata={
                    'old_email': old_email,
                    'new_email': new_email.strip(),
                    'verified_via_token': True
                }
            )
            
            # Aktiviteyi kaydet
            log_user_activity(
                user=user,
                activity_type='email_changed',
                description=f'E-posta adresi {old_email} -> {new_email} olarak değiştirildi',
                request=request
            )
            
            # Her iki e-posta adresine de başarı bildirimi gönder
            try:
                email_service.send_email_change_success_notification(
                    user=user,
                    old_email=old_email,
                    new_email=new_email.strip()
                )
            except Exception:
                pass  # Bildirim hatası ana işlemi etkilemez
            
            return Response({
                'detail': 'E-posta adresiniz başarıyla değiştirildi.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            log_security_event(
                'failed_email_change',
                ip,
                'Geçersiz token ile e-posta değiştirme denemesi',
                request,
                email_attempted=new_email.strip(),
                metadata={'reason': 'invalid_token'}
            )
            return Response({
                'detail': 'Geçersiz veya süresi dolmuş doğrulama linki.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        log_security_event(
            'email_change_error',
            ip,
            f'E-posta değişikliği onaylama hatası: {str(e)}',
            request,
            email_attempted=new_email.strip() if new_email else None,
            metadata={'exception': str(e), 'exception_type': type(e).__name__}
        )
        return Response({
            'detail': 'E-posta değişikliği onaylanırken hata oluştu. Lütfen tekrar deneyin.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Kullanıcı hesabını sil - Şifre doğrulaması ile"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Debug: İsteğin detaylarını logla
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    logger.warning(f"🔥 DELETE ACCOUNT REQUEST - User: {request.user}, IP: {ip}, User-Agent: {user_agent[:100]}")
    
    user = request.user
    password = request.data.get('password')
    
    if not password:
        return Response({
            'detail': 'Hesap silme işlemi için mevcut şifrenizi girmeniz gereklidir.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Şifre doğrulaması
    if not user.check_password(password):
        # Güvenlik olayı kaydet
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        log_security_event(
            'failed_account_deletion',
            ip,
            'Yanlış şifre ile hesap silme denemesi',
            request,
            user_id=user.id,
            username_attempted=user.username,
            metadata={'reason': 'wrong_password'}
        )
        return Response({
            'detail': 'Mevcut şifreniz yanlış. Hesap silme işlemi iptal edildi.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Güvenlik olayını kaydet
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        log_security_event(
            'account_deleted',
            ip,
            'Kullanıcı hesabını sildi',
            request,
            user_id=user.id,
            username_attempted=user.username,
            metadata={'deletion_confirmed': True}
        )
        
        # Kullanıcı hesabını sil
        username = user.username
        user.delete()
        
        return Response({
            'detail': 'Hesap başarıyla silindi.',
            'detail': f'{username} hesabı kalıcı olarak silindi.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'detail': 'Hesap silinirken bir hata oluştu.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def ensure_user_profile(user):
    """Kullanıcı profilini garanti altına alır"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Kullanıcı giriş endpoint'i - JWT token döndürür"""
    try:
        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.tokens import RefreshToken
        
        data = request.data
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return Response({
                'detail': 'Kullanıcı adı ve şifre gereklidir.',
                'error_code': 'MISSING_CREDENTIALS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcı doğrulama
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Güvenlik olayını kaydet
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            log_security_event(
                'failed_login',
                ip,
                'Hatalı giriş denemesi',
                request,
                username_attempted=username,
                metadata={'reason': 'invalid_credentials'}
            )
            return Response({
                'detail': 'Kullanıcı adı veya şifre hatalı.',
                'error_code': 'INVALID_CREDENTIALS'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'detail': 'Hesabınız devre dışı bırakılmış.',
                'error_code': 'ACCOUNT_DISABLED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # JWT token oluştur
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Kullanıcı bilgilerini döndür (UserProfile signal ile otomatik oluşturulur)
        user_data = UserDetailSerializer(user).data
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'detail': 'Giriş işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.',
            'error_code': 'LOGIN_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
