from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health),
    path('register/', views.register_device),
    path('purchase/verify/', views.verify_purchase_view),
    path('credits/', views.get_credits),
    path('credits/use/', views.use_credit),
    path('stats/', views.upload_stats),
    path('packages/', views.get_packages),
    # Hesap & soru sistemi
    path('auth/register-email/', views.register_email),
    path('questions/', views.get_questions),
    path('questions/progress/', views.update_progress),
]
