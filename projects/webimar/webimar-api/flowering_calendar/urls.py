from django.urls import path
from . import views

app_name = 'flowering_calendar'

urlpatterns = [
    # Tarih aralığına göre çiçeklenen bitkiler
    path('flowering-districts/', views.FloweringDistrictsView.as_view(), name='flowering-districts'),
    
    # Belirli bir bitkinin yetiştiği ilçeler
    path('plant-districts/', views.PlantDistrictsView.as_view(), name='plant-districts'),
    
    # Tüm bitki listesi
    path('plants/', views.PlantListView.as_view(), name='plant-list'),
    
    # Bir ilçedeki tüm bitkiler
    path('district-plants/', views.DistrictPlantsView.as_view(), name='district-plants'),
    
    # İlçelerdeki bitki çeşitliliği (heat map)
    path('district-diversity/', views.DistrictDiversityView.as_view(), name='district-diversity'),
    
    # İl listesi
    path('provinces/', views.ProvinceListView.as_view(), name='province-list'),
    
    # İldeki ilçeler
    path('province-districts/', views.ProvinceDistrictsView.as_view(), name='province-districts'),
    
    # 🐝 Arıcılık Planlama API
    path('beekeeping-plan/', views.BeekeepingPlanView.as_view(), name='beekeeping-plan'),
]
