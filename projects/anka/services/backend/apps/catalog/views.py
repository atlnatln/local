from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import City, Sector, FilterDefinition
from .serializers import CitySerializer, SectorSerializer, FilterDefinitionSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']

class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.filter(is_active=True)
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']

class FilterDefinitionViewSet(viewsets.ModelViewSet):
    queryset = FilterDefinition.objects.filter(is_active=True)
    serializer_class = FilterDefinitionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
