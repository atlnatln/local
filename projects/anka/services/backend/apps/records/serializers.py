from rest_framework import serializers
from .models import Record, RecordField

class RecordFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordField
        fields = [
            'id', 'field_name', 'value', 'verified', 
            'source', 'confidence', 'source_provider', 
            'observed_at', 'created_at'
        ]

class RecordSerializer(serializers.ModelSerializer):
    fields = RecordFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Record
        fields = [
            'id', 'batch', 'firm_id', 'firm_name', 
            'data', 'fields', 'created_at', 'updated_at'
        ]
