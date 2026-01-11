from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='maps_health'),
    path('check-coordinate/', views.check_coordinate, name='check_coordinate'),
]