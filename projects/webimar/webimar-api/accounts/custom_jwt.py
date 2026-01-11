"""
Custom JWT Token views with Turkish error messages
"""

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with Turkish error messages and email login support
    """
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Email ile giriş yapmaya çalışıyorsa, önce email'den username'i bul
            user = None
            
            # Önce email ile dene
            if '@' in username:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user_obj = User.objects.get(email=username)
                    # Email bulundu, şimdi username ile authenticate et
                    user = authenticate(
                        request=self.context.get('request'),
                        username=user_obj.username,
                        password=password
                    )
                except User.DoesNotExist:
                    # Email bulunamadı, normal flow'a geç
                    pass
                except Exception as e:
                    # Diğer beklenmeyen hatalar için log
                    logger.error(f"Error during email lookup for {username}: {str(e)}")
                    pass
            
            # Email ile bulunamadıysa veya email değilse, normal username ile dene
            if not user:
                user = authenticate(
                    request=self.context.get('request'),
                    username=username,
                    password=password
                )
            
            if not user:
                # Kullanıcının email ile mi username ile mi denendiğini belirle
                if '@' in username:
                    # Email ile denendi ama bulunamadı
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        if User.objects.filter(email=username).exists():
                            error_msg = 'E-posta doğru ancak şifre hatalı.'
                        else:
                            error_msg = 'Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.'
                    except Exception:
                        error_msg = 'E-posta veya şifre hatalı.'
                else:
                    # Username ile denendi ama bulunamadı
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user_exists = User.objects.filter(username=username).exists()
                        if user_exists:
                            # Kullanıcı var ama şifre yanlış
                            error_msg = 'Kullanıcı adı doğru ancak şifre hatalı.'
                        else:
                            # Kullanıcı hiç yok
                            # Benzer kullanıcı adları var mı kontrol et
                            similar_users = User.objects.filter(username__icontains=username[:3]).values_list('username', flat=True) if len(username) >= 3 else []
                            if similar_users:
                                similar_list = ', '.join(list(similar_users)[:3])  # İlk 3'ünü göster
                                error_msg = f'"{username}" kullanıcı adı bulunamadı. Benzer kullanıcılar: {similar_list}'
                            else:
                                error_msg = f'"{username}" kullanıcı adı ile kayıtlı kullanıcı bulunamadı.'
                    except Exception:
                        error_msg = 'Kullanıcı adı veya şifre hatalı.'
                
                # Hatalı giriş denemesini logla
                ip = self.get_client_ip()
                logger.warning(f"Failed login attempt for username/email '{username}' from IP {ip}")
                
                # Türkçe hata mesajı
                raise serializers.ValidationError(
                    error_msg,
                    code='INVALID_CREDENTIALS'
                )
            
            if not user.is_active:
                # Pasif hesap hatası
                logger.warning(f"Login attempt for inactive user '{username}'")
                raise serializers.ValidationError(
                    'Hesabınız aktif değil, lütfen e-posta doğrulamasını tamamlayın.',
                    code='INACTIVE_ACCOUNT'
                )
        
        # Normal JWT doğrulama
        return super().validate(attrs)
    
    def get_client_ip(self):
        """İstemci IP adresini al"""
        request = self.context.get('request')
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0]
            return request.META.get('REMOTE_ADDR', 'unknown')
        return 'unknown'


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with Turkish error messages
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            # İstek detaylarını logla
            username = request.data.get('username', 'N/A')
            logger.info(f"🔐 Login attempt for username/email: {username}")
            
            return super().post(request, *args, **kwargs)
        except serializers.ValidationError as e:
            # Validation error - bu zaten doğru formatta
            logger.warning(f"Validation error in login for {request.data.get('username', 'N/A')}: {str(e)}")
            raise e
        except Exception as e:
            # Beklenmeyen hatalar için detaylı log
            username = request.data.get('username', 'N/A')
            logger.error(f"Unexpected error in login for {username}: {str(e)}", exc_info=True)
            return Response({
                'detail': 'Giriş işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.',
                'error_code': 'LOGIN_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Custom JWT refresh serializer with Turkish error messages
    """
    
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except Exception:
            raise serializers.ValidationError({
                'detail': 'Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.',
                'error_code': 'TOKEN_EXPIRED'
            })


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view with Turkish error messages
    """
    serializer_class = CustomTokenRefreshSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response({
                'detail': 'Token yenileme işlemi başarısız. Lütfen tekrar giriş yapın.',
                'error_code': 'TOKEN_REFRESH_ERROR'
            }, status=status.HTTP_401_UNAUTHORIZED)
