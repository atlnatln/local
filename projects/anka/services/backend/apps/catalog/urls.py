from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, SectorViewSet, FilterDefinitionViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'sectors', SectorViewSet, basename='sector')
router.register(r'filters', FilterDefinitionViewSet, basename='filter')

urlpatterns = [
    path('', include(router.urls)),
]
