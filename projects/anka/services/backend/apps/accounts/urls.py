"""
URL configuration for accounts app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    CurrentUserView,
    ChangePasswordView,
    OrganizationViewSet,
    RefreshTokenView,
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organizations')

urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Organization routes
    path('', include(router.urls)),
]
