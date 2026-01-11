"""
URL configuration for webimar_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.custom_jwt import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('api/calculations/', include('calculations.urls')),
    path('api/maps/', include('maps.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/kullanicilar/', include('kullanicilar.urls')),
    path('api/flowering/', include('flowering_calendar.urls')),  # Çiçeklenme takvimi API
    # JWT Auth - DEVRE DIŞI: Sadece Google OAuth ile giriş yapılabilir
    # Mail/şifre ile giriş kaldırıldı - Sadece Google OAuth aktif
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Token refresh hala gerekli (Google OAuth sonrası token yenileme için)
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]

# Media dosya servisi (sadece development için)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Static dosyalar WhiteNoise tarafından serve edilecek
