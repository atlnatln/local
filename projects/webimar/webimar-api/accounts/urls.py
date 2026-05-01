from django.urls import path
from . import views
from .views.email_test_views import test_email_send, test_email_connection
from .views.email_verification_views import (
    send_verification_email, verify_email, 
    request_password_reset, reset_password
)
from .views.google_auth_views import google_auth_url, google_oauth_callback
from .views.contact_views import contact_form_view
from .views.debug_views import debug_jwt_token_test, debug_oauth_simulation
from .admin import admin_dashboard_view

urlpatterns = [
    # Admin özel dashboard
    path('admin-dashboard/', admin_dashboard_view, name='accounts_dashboard'),
    
    # DEVRE DIŞI: Mail/şifre ile kayıt ve giriş kaldırıldı - Sadece Google OAuth aktif
    # path('register/', views.register, name='register'),
    # path('login/', views.login, name='login'),
    
    path('health/', views.health_check, name='accounts_health'),
    path('me/', views.me, name='accounts_me'),
    path('me/change-password/', views.change_password, name='accounts_change_password'),
    path('me/sessions/', views.user_sessions, name='user_sessions'),
    path('me/sessions/<str:session_key>/', views.terminate_session, name='terminate_session'),
    path('me/logout/', views.logout, name='logout'),
    path('me/logout-all/', views.logout_all_sessions, name='logout_all_sessions'),
    path('me/delete-account/', views.delete_account, name='delete_account'),
    path('check-username/', views.check_username_unique, name='check_username_unique'),
    path('check-email/', views.check_email_unique, name='check_email_unique'),
    # Google OAuth endpoints - AKTİF
    path('google/auth/', google_auth_url, name='google_auth_url'),
    path('google/callback/', google_oauth_callback, name='google_oauth_callback'),
    # Email test endpoints
    path('test-email/', test_email_send, name='test_email_send'),
    path('test-email-connection/', test_email_connection, name='test_email_connection'),
    # DEVRE DIŞI: Email verification endpoints - Google OAuth ile gerek kalmadı
    # path('send-verification/', send_verification_email, name='send_verification_email'),
    # path('verify-email/', verify_email, name='verify_email'),
    # DEVRE DIŞI: Şifre sıfırlama - Google OAuth ile gerek kalmadı
    # path('password-reset-request/', views.password_reset_request, name='password_reset_request'),
    # path('request-password-reset/', request_password_reset, name='request_password_reset'),
    # path('reset-password/', reset_password, name='reset_password'),
    # Email change endpoints
    path('request-email-change/', views.request_email_change, name='request_email_change'),
    path('confirm-email-change/', views.confirm_email_change, name='confirm_email_change'),
    # Contact form endpoint
    path('contact/', contact_form_view, name='contact_form'),

    # Analytics (anonim dahil) - pageview/navigation/duration
    path('analytics/events/', views.analytics_event, name='analytics_event'),
    
    # DEBUG ENDPOINTS - Sadece development modunda aktif
    path('debug/jwt-test/', debug_jwt_token_test, name='debug_jwt_token_test'),
    path('debug/oauth-simulation/', debug_oauth_simulation, name='debug_oauth_simulation'),
]