from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from .models import City, Sector, FilterDefinition
from .serializers import CitySerializer, SectorSerializer, FilterDefinitionSerializer


class _ReadOnlyOrAdmin:
    """Allow read for any authenticated user; write only for admin."""
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]


class CityViewSet(_ReadOnlyOrAdmin, viewsets.ModelViewSet):
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']

class SectorViewSet(_ReadOnlyOrAdmin, viewsets.ModelViewSet):
    queryset = Sector.objects.filter(is_active=True)
    serializer_class = SectorSerializer
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']

class FilterDefinitionViewSet(_ReadOnlyOrAdmin, viewsets.ModelViewSet):
    queryset = FilterDefinition.objects.filter(is_active=True)
    serializer_class = FilterDefinitionSerializer
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
