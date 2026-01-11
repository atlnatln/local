"""
Google OAuth 2.0 Authentication Views
Admin onaylı sistem ile entegreli Google giriş
"""

from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import UserDetailSerializer
from accounts.utils import log_user_activity, log_security_event
import google.oauth2.credentials
import google_auth_oauthlib.flow
import google.auth.transport.requests
import os
import json
import logging
from urllib.parse import urlencode, urljoin, urlparse

logger = logging.getLogger(__name__)

# Google OAuth yapılandırması
# OAuth2 standartlarına uygun scope'lar kullan
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

def get_frontend_base():
    """
    FRONTEND base URL konfigürasyonunu al:
    - settings.FRONTEND_BASE_URL (tercih)
    - DEBUG -> http://localhost:3000
    - production fallback -> https://tarimimar.com.tr
    """
    base = getattr(settings, 'FRONTEND_BASE_URL', None)
    if base:
        return base.rstrip('/')
    if settings.DEBUG:
        return 'http://localhost:3000'
    return 'https://tarimimar.com.tr'

def build_frontend_callback(params: dict = None, requires_approval: bool = False, extra_path: str = '/hesaplama/auth/google/callback'):
    """
    Frontend'e yönlendirme URL'i oluşturur. params dict query paramları ekler.
    """
    base = get_frontend_base()
    path = extra_path
    url = base + path
    if requires_approval:
        # Eğer onay gerektiriyorsa farklı bir parametre set et
        if not params:
            params = {}
        params.update({'requires_approval': 'true'})
    if params:
        return f"{url}?{urlencode(params)}"
    return url

def get_cookie_domain_from_frontend():
    try:
        parsed = urlparse(get_frontend_base())
        return parsed.hostname or None
    except Exception:
        return None

def get_google_oauth_flow(request):
    """Google OAuth flow objesi oluştur"""
    
    # Development ortamında HTTPS zorunluluğunu kaldır
    if settings.DEBUG:
        import os
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        print("🚧 DEBUG MODE: HTTPS zorunluluğu kaldırıldı")
    
    # Client secrets JSON formatını oluştur
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
    }
    
    # Scope'ları OAuth2 standartlarına uygun hale getir
    normalized_scopes = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config, scopes=normalized_scopes)
    
    # redirect_uri'yi her zaman settings'den al
    flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    print(f"🔗 OAuth redirect_uri: {flow.redirect_uri}")
    
    return flow

@api_view(['GET'])
@permission_classes([AllowAny])
def google_auth_url(request):
    """Google OAuth URL'ini döndür"""
    try:
        # Debug bilgileri - Production'da da görünsün
        logger.info(f"🔍 Google OAuth Debug - DEBUG={settings.DEBUG}:")
        logger.info(f"CLIENT_ID exists: {bool(settings.GOOGLE_OAUTH_CLIENT_ID)}")
        logger.info(f"CLIENT_SECRET exists: {bool(settings.GOOGLE_OAUTH_CLIENT_SECRET)}")
        logger.info(f"REDIRECT_URI: {settings.GOOGLE_OAUTH_REDIRECT_URI}")
        logger.info(f"HTTP_ORIGIN: {request.META.get('HTTP_ORIGIN', 'None')}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        
        # Settings'lerin dolu olup olmadığını kontrol et
        if not settings.GOOGLE_OAUTH_CLIENT_ID:
            logger.error("❌ GOOGLE_OAUTH_CLIENT_ID boş!")
            return Response({
                'detail': 'Google OAuth Client ID tanımlanmamış'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        if not settings.GOOGLE_OAUTH_CLIENT_SECRET:
            logger.error("❌ GOOGLE_OAUTH_CLIENT_SECRET boş!")
            return Response({
                'detail': 'Google OAuth Client Secret tanımlanmamış'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        flow = get_google_oauth_flow(request)
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Her zaman consent ekranı göster
        )
        
        logger.info(f"Generated URL: {authorization_url}")
        logger.info(f"Redirect URI used: {flow.redirect_uri}")
        
        # State'i session'a kaydet (güvenlik için)
        request.session['google_oauth_state'] = state
        
        return Response({
            'authorization_url': authorization_url,
            'state': state
        })
    except Exception as e:
        logger.error(f"❌ Google OAuth URL Error: {e}")
        return Response({
            'detail': f'Google OAuth URL oluşturulurken hata: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_callback(request):
    """Google OAuth callback"""
    print(f"🚀 GOOGLE OAUTH CALLBACK START")
    print(f"   📋 GET params: {dict(request.GET)}")
    print(f"   🔍 Session state: {request.session.get('google_oauth_state')}")
    print(f"   🌐 Request URL: {request.get_full_path()}")
    
    try:
        # State parametresini kontrol et (CSRF koruması)
        state = request.GET.get('state')
        session_state = request.session.get('google_oauth_state')
        
        print(f"   ⚖️  State check: provided={state}, session={session_state}")
        
        # TEMPORARY: Debug modunda state kontrolünü bypass et
        if settings.DEBUG:
            print(f"   🚧 DEBUG MODE: State kontrolü bypass ediliyor")
            if not state:
                print(f"   ❌ State parametresi yok - OAuth hatalı")
                return Response({'detail': 'OAuth state parametresi eksik'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not state or state != session_state:
                log_security_event(
                    'google_oauth_invalid_state',
                    request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
                    'Google OAuth state mismatch',
                    request,
                    metadata={'provided_state': state, 'session_state': session_state}
                )
                return Response({
                    'detail': 'Güvenlik hatası: State parametresi uyuşmuyor.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authorization code al
        authorization_code = request.GET.get('code')
        if not authorization_code:
            return Response({
                'detail': 'Authorization code bulunamadı.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Token al - invalid_grant hatasından kaçınmak için daha robust yaklaşım
        flow = get_google_oauth_flow(request)
        try:
            # OAuth state ve session'u temizle (re-use önlemek için)
            if 'google_oauth_state' in request.session:
                del request.session['google_oauth_state']
            
            # Authorization code'u kullanarak token fetch
            print(f"   🔑 Token fetch başlatılıyor - Code: {authorization_code[:20]}...")
            flow.fetch_token(code=authorization_code)
            print(f"   ✅ Token fetch başarılı!")
            
        except Exception as token_err:
            import traceback
            tb = traceback.format_exc()
            print(f"   ❌ fetch_token hatası: {token_err}\n{tb}")
            
            # Detaylı hata analizi
            if 'invalid_grant' in str(token_err).lower():
                error_detail = "Authorization code geçersiz veya süresi dolmuş. Google OAuth akışını yeniden başlatın."
                print(f"   🔍 INVALID_GRANT tespit edildi - muhtemelen code yeniden kullanıldı")
            else:
                error_detail = f"Google token alınamadı: {token_err}"
            
            log_security_event(
                'google_oauth_token_fetch_error',
                request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
                f'Google token fetch hatası: {token_err}',
                request,
                metadata={'exception': str(token_err), 'error_type': 'invalid_grant' if 'invalid_grant' in str(token_err).lower() else 'other'}
            )
            
            # Frontend'e hata ile redirect
            if settings.DEBUG:
                error_url = build_frontend_callback({'error': 'token_fetch', 'message': error_detail})
            else:
                error_url = build_frontend_callback({'error': 'token_fetch', 'message': error_detail})
            
            return redirect(error_url)
        
        credentials = flow.credentials
        
        # Kullanıcı bilgilerini al
        user_info = get_google_user_info(credentials)
        
        if not user_info:
            return Response({
                'detail': 'Google\'dan kullanıcı bilgileri alınamadı.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcı oluştur veya bul
        user, created = handle_google_user(user_info, request)
        
        if not user:
            return Response({
                'detail': 'Kullanıcı işlemi başarısız.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Admin onaylı sistem kontrolü
        if not user.is_active:
            # Admin onay bekleyen kullanıcılar için frontend'e redirect yap
            if settings.DEBUG:
                frontend_url = build_frontend_callback({'requires_approval': 'true', 'user_email': user.email})
            else:
                frontend_url = build_frontend_callback({'requires_approval': 'true', 'user_email': user.email})
            
            return redirect(frontend_url)
        
        # JWT token oluştur
        print(f"   🔑 JWT Token oluşturma başlıyor - User: {user.email} (ID: {user.id})")
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            print(f"   ✅ JWT Token başarılı - Access: {len(access_token)} kar, Refresh: {len(refresh_token)} kar")
        except Exception as jwt_error:
            print(f"   ❌ JWT Token hatası: {jwt_error}")
            import traceback
            print(f"   📋 JWT Traceback: {traceback.format_exc()}")
            raise jwt_error
        
        # Kullanıcı bilgilerini döndür
        print(f"   📊 UserDetailSerializer çalıştırılıyor...")
        try:
            user_data = UserDetailSerializer(user).data
            print(f"   ✅ UserDetailSerializer başarılı - {len(user_data)} adet field")
        except Exception as serializer_error:
            print(f"   ❌ UserDetailSerializer hatası: {serializer_error}")
            raise serializer_error
        
        # Aktiviteyi kaydet
        print(f"   📝 log_user_activity çalıştırılıyor...")
        try:
            log_user_activity(
                user=user,
                activity_type='google_login',
                description=f'Google OAuth ile giriş yaptı {"(ilk kez)" if created else ""}',
                request=request
            )
            print(f"   ✅ log_user_activity başarılı")
        except Exception as activity_error:
            print(f"   ❌ log_user_activity hatası: {activity_error}")
            # Bu hata kritik değil, devam et
            pass
        
        # Frontend'e redirect
        print(f"   🔄 Frontend'e redirect hazırlanıyor...")
        
        # Doğru frontend URL'ini belirle
        frontend_url = build_frontend_callback({'access': access_token, 'refresh': refresh_token})
        
        print(f"   🎯 Redirect URL: {frontend_url[:100]}...")
        print(f"   🚀 Redirect işlemi başlatılıyor...")
        
        # Redirect yanıtını oluştur ve auth cookie ayarla (Next.js ana sayfa için)
        response = redirect(frontend_url)
        try:
            cookie_domain = get_cookie_domain_from_frontend() or ('localhost' if settings.DEBUG else 'tarimimar.com.tr')
            # Sadece oturum bilgisini göstermek için hafif bir bayrak cookie
            response.set_cookie(
                key='webimar_auth',
                value='1',
                max_age=7 * 24 * 60 * 60,  # 7 gün
                path='/',
                domain=cookie_domain,
                secure=not settings.DEBUG,
                httponly=False,  # Next.js istemci tarafında okunabilsin (sadece UI için)
                samesite='Lax'
            )
        except Exception as cookie_err:
            print(f"   ⚠️ Cookie set hatası: {cookie_err}")
        
        return response
        
    except Exception as e:
        log_security_event(
            'google_oauth_error',
            request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
            f'Google OAuth callback hatası: {str(e)}',
            request,
            metadata={'exception': str(e), 'exception_type': type(e).__name__}
        )
        return Response({
            'detail': f'Google OAuth işlemi sırasında hata: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_google_user_info(credentials):
    """Google API'den kullanıcı bilgilerini al"""
    try:
        # Önce google-api-python-client ile dene
        import googleapiclient.discovery
        service = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            'google_id': user_info.get('id'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'given_name': user_info.get('given_name'),
            'family_name': user_info.get('family_name'),
            'picture': user_info.get('picture'),
            'verified_email': user_info.get('verified_email', False)
        }
    except Exception as e:
        # googleapiclient yoksa veya hata verdiyse requests ile fallback
        print(f"Google user info alım hatası (apiclient): {e} - requests fallback denenecek")
        try:
            import requests as _requests
            token = getattr(credentials, 'token', None)
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            resp = _requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers, timeout=10)
            if resp.status_code == 200:
                user_info = resp.json()
                return {
                    'google_id': user_info.get('id'),
                    'email': user_info.get('email'),
                    'name': user_info.get('name'),
                    'given_name': user_info.get('given_name'),
                    'family_name': user_info.get('family_name'),
                    'picture': user_info.get('picture'),
                    'verified_email': user_info.get('verified_email', False)
                }
            else:
                print(f"Google userinfo HTTP hatası: {resp.status_code} - {resp.text}")
                return None
        except Exception as e2:
            print(f"Google user info alım hatası (fallback): {e2}")
            return None

def handle_google_user(user_info, request):
    """Google kullanıcısını işle - Admin onaylı sistemle entegreli"""
    try:
        email = user_info.get('email')
        google_id = user_info.get('google_id')
        name = user_info.get('name', '')
        
        if not email:
            return None, False
        
        user = User.objects.filter(email=email).first()
        
        if user:
            # Mevcut kullanıcı - profil ve flag’leri düzelt
            try:
                profile = getattr(user, 'profile', None)
                if profile:
                    profile.awaiting_activation = False
                    profile.activation_mail_sent = False
                    profile.awaiting_password_reset = False
                    profile.password_reset_mail_sent = False
                    profile.is_active_profile = True
                    profile.save()
            except Exception:
                pass
            
            # Kullanıcı aktif değilse, Google doğrulandığı için aktifleştir
            if not user.is_active:
                user.is_active = True
                user.save()
            
            try:
                log_user_activity(
                    user=user,
                    activity_type='google_login_existing',
                    description='Mevcut hesap ile Google OAuth giriş',
                    request=request
                )
            except Exception as activity_error:
                print(f"Google OAuth: Aktivite loglama hatası (mevcut kullanıcı): {activity_error}")
                # Hata loglama başarısız olsa da giriş devam etsin
            return user, False
        else:
            # Yeni kullanıcı - Google doğrulanmış e-posta -> direkt aktif oluştur
            username = email.split('@')[0]
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                is_active=True  # Admin onaylı sistem
            )
            
            # Profil flag’lerini temizle
            try:
                profile = getattr(user, 'profile', None)
                if profile:
                    profile.awaiting_activation = False
                    profile.activation_mail_sent = False
                    profile.awaiting_password_reset = False
                    profile.password_reset_mail_sent = False
                    profile.is_active_profile = True
                    profile.save()
            except Exception:
                pass
            
            # Admin'e aktivasyon e-postası GÖNDERME (sadece opsiyonel bilgi maili atılabilir)
            # from accounts.admin import send_admin_registration_notification
            # try:
            #     send_admin_registration_notification(user)
            # except Exception:
            #     pass
            
            try:
                log_user_activity(
                    user=user,
                    activity_type='google_register',
                    description='Google OAuth ile kayıt - otomatik aktif',
                    request=request
                )
            except Exception as activity_error:
                print(f"Google OAuth: Aktivite loglama hatası (yeni kullanıcı): {activity_error}")
                # Hata loglama başarısız olsa da kayıt devam etsin
            
            return user, True
            
    except Exception as e:
        print(f"Google user handle hatası: {e}")
        return None, False
