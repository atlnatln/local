from rest_framework import serializers
from .models import City, Sector, FilterDefinition

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            'id', 'name', 'code', 'country', 
            'is_active', 'created_at', 'updated_at'
        ]

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = [
            'id', 'name', 'code', 'description', 
            'is_active', 'created_at', 'updated_at'
        ]

class FilterDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterDefinition
        fields = [
            'id', 'name', 'description', 'data_type', 
            'enum_values', 'is_active', 'created_at', 'updated_at'
        ]
