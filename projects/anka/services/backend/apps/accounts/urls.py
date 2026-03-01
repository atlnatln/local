"""URL configuration for accounts app."""

from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LogoutView,
    CurrentUserView,
    ChangePasswordView,
    OrganizationViewSet,
    RefreshTokenView,
    GoogleLoginView,
    TestLoginView,
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organizations')

urlpatterns = [
    # Authentication endpoints
    # Not: 'google' (slash'sız) URL kaldırıldı — OpenAPI operationId çakışmasını önlemek için.
    # Frontend ve tüm istemciler '/api/auth/google/' (trailing slash) kullanmalıdır.
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Organization routes
    path('', include(router.urls)),
]

if getattr(settings, 'ANKA_ALLOW_TEST_LOGIN', False):
    urlpatterns.insert(0, path('test-login/', TestLoginView.as_view(), name='test-login'))
