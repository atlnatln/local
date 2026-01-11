from rest_framework import serializers
from .models import CalculationHistory

class CalculationHistorySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Result alanını olduğu gibi döndür - frontend'de zaten işlenmiş HTML var
        # HTML sanitization yapılmayacak çünkü kullanıcının gördüğü orijinal format korunmalı
        return data
    class Meta:
        model = CalculationHistory
        fields = ['id', 'calculation_type', 'title', 'description', 'parameters', 'result', 'map_coordinates', 'created_at', 'is_successful']
        read_only_fields = ['id', 'created_at']

class CalculationHistoryCreateSerializer(serializers.ModelSerializer):
    """Hesaplama kaydetmek için kullanılan serializer"""
    class Meta:
        model = CalculationHistory
        fields = ['calculation_type', 'title', 'description', 'parameters', 'result', 'map_coordinates']
        
    def validate_title(self, value):
        """Başlık validasyonu"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Başlık en az 2 karakter olmalıdır.")
        if value and len(value.strip()) > 200:
            raise serializers.ValidationError("Başlık en fazla 200 karakter olabilir.")
        return value.strip() if value else value
    
    def validate_parameters(self, value):
        """Parametreler validasyonu"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parametreler dict formatında olmalıdır.")
        if not value:
            raise serializers.ValidationError("Parametreler boş olamaz.")
        return value
    
    def validate_result(self, value):
        """Sonuç validasyonu"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Sonuç dict formatında olmalıdır.")
        return value
    
    def validate_map_coordinates(self, value):
        """Koordinat validasyonu"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Koordinatlar dict formatında olmalıdır.")
        if value:
            # Lat/lng kontrolü
            lat = value.get('lat') or value.get('latitude')
            lng = value.get('lng') or value.get('longitude')
            if lat is not None:
                try:
                    lat_float = float(lat)
                    if not (-90 <= lat_float <= 90):
                        raise serializers.ValidationError("Latitude -90 ile 90 arasında olmalıdır.")
                except (ValueError, TypeError):
                    raise serializers.ValidationError("Latitude numerik bir değer olmalıdır.")
            if lng is not None:
                try:
                    lng_float = float(lng)
                    if not (-180 <= lng_float <= 180):
                        raise serializers.ValidationError("Longitude -180 ile 180 arasında olmalıdır.")
                except (ValueError, TypeError):
                    raise serializers.ValidationError("Longitude numerik bir değer olmalıdır.")
        return value
    
    def validate(self, data):
        """Genel validasyon"""
        # Temel alanların varlığını kontrol et
        if not data.get('calculation_type'):
            raise serializers.ValidationError("Hesaplama türü zorunludur.")
        
        # Parameters ve result arasında tutarlılık kontrolü
        parameters = data.get('parameters', {})
        if isinstance(parameters, dict) and 'alan_m2' in parameters:
            try:
                alan = float(parameters['alan_m2'])
                if alan <= 0:
                    raise serializers.ValidationError("Alan sıfırdan büyük olmalıdır.")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Alan numerik bir değer olmalıdır.")
        
        return data
