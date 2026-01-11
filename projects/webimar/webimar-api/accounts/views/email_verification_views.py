from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, throttle_classes
from accounts.throttles import PasswordResetRateThrottle, EmailVerificationRateThrottle, handle_throttle_exception
from accounts.test_decorators import conditional_throttle_classes, conditional_handle_throttle_exception
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from utils.email_verification import EmailVerificationService
import json

User = get_user_model()

@require_http_methods(["POST"])
@csrf_exempt
@api_view(['POST'])
@conditional_throttle_classes([EmailVerificationRateThrottle])
@conditional_handle_throttle_exception
def send_verification_email(request):
    """
    Email doğrulama maili gönder
    POST /api/accounts/send-verification/
    { "email": "user@example.com" }
    """
    try:
        # Hem JSON hem form-encoded destekle
        try:
            email = getattr(request, 'data', {}).get('email')
        except Exception:
            try:
                data = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                data = {}
            email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'detail': 'Email adresi gerekli'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'detail': 'Bu email adresi ile kayıtlı kullanıcı bulunamadı'}, status=404)
        
        if user.is_active:
            return JsonResponse({'success': False, 'detail': 'Bu hesap zaten aktif'})
        
        success = EmailVerificationService.send_verification_email(user, request)
        
        return JsonResponse({
            'success': bool(success),
            'detail': 'Doğrulama maili gönderildi' if success else 'Mail gönderilemedi',
            'email': email
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'detail': f'Hata: {str(e)}'}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def verify_email(request):
    """
    Email doğrulama
    POST /api/accounts/verify-email/
    { "uid": "base64_user_id", "token": "verification_token" }
    """
    try:
        # Hem JSON hem form-encoded destekle
        try:
            data = getattr(request, 'data', {})
        except Exception:
            try:
                data = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                data = {}
        uid = data.get('uid')
        token = data.get('token')
        
        if not uid or not token:
            return JsonResponse({'success': False, 'detail': 'UID ve token gerekli'}, status=400)
        
        user = EmailVerificationService.verify_token(uid, token)
        
        if user:
            user.is_active = True
            user.save()
            return JsonResponse({
                'success': True,
                'detail': 'Email adresi başarıyla doğrulandı',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active
                }
            })
        else:
            return JsonResponse({'success': False, 'detail': 'Geçersiz veya süresi dolmuş doğrulama linki'}, status=400)
    except Exception:
        # Geçersiz girişlerde 400 dön
        return JsonResponse({'success': False, 'detail': 'Geçersiz veya süresi dolmuş doğrulama linki'}, status=400)

@require_http_methods(["POST"])
@csrf_exempt
@api_view(['POST'])
@conditional_throttle_classes([PasswordResetRateThrottle])
@conditional_handle_throttle_exception
def request_password_reset(request):
    """
    Şifre sıfırlama talebinde bulun
    POST /api/accounts/request-password-reset/
    { "email": "user@example.com" }
    """
    try:
        # Hem JSON hem form-encoded destekle
        try:
            email = getattr(request, 'data', {}).get('email')
        except Exception:
            try:
                data = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                data = {}
            email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'detail': 'Email adresi gerekli'}, status=400)
        
        profile = None
        try:
            user = User.objects.get(email=email)
            
            # Kullanıcı başına rate limit kontrolü
            from django.utils import timezone
            from datetime import timedelta, date
            from accounts.models import UserProfile
            
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Günlük limit kontrolü (günde en fazla 3 kez)
            today = date.today()
            if profile.password_reset_date == today:
                if profile.password_reset_count_today >= 3:
                    return JsonResponse({
                        'success': False,
                        'detail': 'Günlük şifre sıfırlama limiti aşıldı. Günde en fazla 3 kez şifre sıfırlama talebi gönderebilirsiniz. Lütfen yarın tekrar deneyin.'
                    }, status=429)
            else:
                # Yeni güne geçildiyse sayacı sıfırla
                profile.password_reset_date = today
                profile.password_reset_count_today = 0
            
            # Dakika bazlı rate limit kontrolü (5 dakikada bir)
            if not created and profile.last_password_reset_email:
                time_since_last_reset = timezone.now() - profile.last_password_reset_email
                if time_since_last_reset < timedelta(minutes=5):
                    remaining_minutes = 5 - int(time_since_last_reset.total_seconds() // 60)
                    return JsonResponse({
                        'success': False,
                        'detail': f'Çok sık şifre sıfırlama talebi. {remaining_minutes} dakika sonra tekrar deneyin.'
                    }, status=429)
            
        except User.DoesNotExist:
            # Güvenlik için her zaman başarılı mesajı döndür
            return JsonResponse({
                'success': True,
                'detail': 'Eğer bu email adresi sistemde kayıtlı ise, şifre sıfırlama maili gönderildi',
                'requires_login': True
            })
        
        success = EmailVerificationService.send_password_reset_email(user, request)
        
        # Şifre sıfırlama maili gönderme zamanını ve sayacını güncelle
        if profile:
            from django.utils import timezone
            from datetime import date
            
            today = date.today()
            profile.last_password_reset_email = timezone.now()
            
            # Günlük sayacı artır
            if profile.password_reset_date == today:
                profile.password_reset_count_today += 1
            else:
                profile.password_reset_date = today
                profile.password_reset_count_today = 1
            
            profile.save()
            
            # Log günlük limit durumu
            print(f"🔐 Password reset: {user.email} - Günlük talep: {profile.password_reset_count_today}/3")
        
        return JsonResponse({
            'success': True,
            'detail': 'Eğer bu email adresi sistemde kayıtlı ise, şifre sıfırlama maili gönderildi',
            'requires_login': True
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'detail': f'Hata: {str(e)}'}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def reset_password(request):
    """
    Şifre sıfırlama
    POST /api/accounts/reset-password/
    { "uid": "base64_user_id", "token": "reset_token", "new_password": "new_password123" }
    """
    try:
        # Hem JSON hem form-encoded destekle
        try:
            data = getattr(request, 'data', {})
        except Exception:
            data = json.loads(request.body or '{}')
        uid = data.get('uid')
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not uid or not token or not new_password:
            return JsonResponse({'success': False, 'detail': 'UID, token ve yeni şifre gerekli'}, status=400)
        
        if len(new_password) < 4:
            return JsonResponse({'success': False, 'detail': 'Şifre en az 4 karakter olmalı'}, status=400)
        
        user = EmailVerificationService.verify_token(uid, token)
        
        if user:
            from django.contrib.auth.hashers import make_password
            user.password = make_password(new_password)
            user.save()
            
            # Güvenlik için şifre sıfırlama sonrası otomatik giriş KAPALI
            from accounts.utils import log_user_activity
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            log_user_activity(
                user=user,
                action='password_reset_completed',
                ip_address=ip_address,
                description='Şifre başarıyla sıfırlandı - manuel giriş gerekli'
            )
            
            return JsonResponse({'success': True, 'detail': 'Şifre başarıyla değiştirildi. Lütfen yeni şifrenizle giriş yapın.', 'requires_login': True})
        else:
            return JsonResponse({'success': False, 'detail': 'Geçersiz veya süresi dolmuş sıfırlama linki'}, status=400)
        
    except Exception as e:
        return JsonResponse({'success': False, 'detail': f'Hata: {str(e)}'}, status=500)
