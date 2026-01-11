"""
Debug Views - Sadece development ortamında aktif
"""
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from ..serializers import UserDetailSerializer
from .google_auth_views import build_frontend_callback

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_jwt_token_test(request):
    """Debug: JWT token oluşturma test et"""
    if not settings.DEBUG:
        return Response({'detail': 'Bu endpoint sadece debug modunda aktif'}, status=404)
    
    print(f"🔬 DEBUG JWT TOKEN TEST")
    
    # İlk kullanıcıyı bul veya oluştur
    try:
        user = User.objects.first()
        if not user:
            print("   📝 Test kullanıcısı oluşturuluyor")
            user = User.objects.create_user(
                email='debug_jwt_test@example.com',
                first_name='Debug',
                last_name='JWT Test',
                password='debug123',
                is_active=True
            )
            
        print(f"   👤 Test kullanıcısı: {user.email} (ID: {user.id})")
        print(f"   ✅ Active: {user.is_active}")
        
        # Kullanıcıyı aktif yap
        if not user.is_active:
            user.is_active = True
            user.save()
            print(f"   🔧 Kullanıcı aktif yapıldı")
        
        # JWT token oluştur
        print(f"   🔑 JWT Token oluşturma başlıyor...")
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            print(f"   ✅ JWT Token başarılı!")
            print(f"      - Refresh: {len(refresh_token)} karakter")
            print(f"      - Access: {len(access_token)} karakter")
            print(f"      - Refresh preview: {refresh_token[:50]}...")
            print(f"      - Access preview: {access_token[:50]}...")
            
            # Kullanıcı bilgilerini al
            user_data = UserDetailSerializer(user).data
            
            # Frontend'e yönlendirme URL'i oluştur
            frontend_url = build_frontend_callback({'access': access_token, 'refresh': refresh_token})
            
            return Response({
                'status': 'success',
                'message': 'JWT token oluşturma başarılı',
                'user': user_data,
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                },
                'frontend_url': frontend_url,
                'debug_info': {
                    'user_id': user.id,
                    'user_email': user.email,
                    'refresh_length': len(refresh_token),
                    'access_length': len(access_token)
                }
            })
            
        except Exception as jwt_error:
            print(f"   ❌ JWT Token hatası: {jwt_error}")
            import traceback
            print(f"   📋 JWT Traceback: {traceback.format_exc()}")
            
            return Response({
                'status': 'error',
                'message': 'JWT token oluşturma başarısız',
                'error': str(jwt_error),
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        print(f"   ❌ Genel hata: {e}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        
        return Response({
            'status': 'error', 
            'message': 'Debug test başarısız',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny]) 
def debug_oauth_simulation(request):
    """Debug: OAuth callback simülasyonu"""
    if not settings.DEBUG:
        return Response({'detail': 'Bu endpoint sadece debug modunda aktif'}, status=404)
        
    print(f"🎭 DEBUG OAUTH SIMULATION")
    
    # Frontend'e jwt token'larla birlikte redirect
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                email='oauth_simulation@example.com',
                first_name='OAuth',
                last_name='Simulation',
                password='simulation123',
                is_active=True
            )
            
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Frontend'e redirect
        from django.shortcuts import redirect
        frontend_url = build_frontend_callback({'access': access_token, 'refresh': refresh_token})
        
        print(f"   🔄 Redirect URL: {frontend_url}")
        return redirect(frontend_url)
        
    except Exception as e:
        print(f"   ❌ Simulation hatası: {e}")
        return Response({'error': str(e)}, status=500)
