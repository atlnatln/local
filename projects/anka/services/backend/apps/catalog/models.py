"""
Catalog app: City, Sector, and Filter taxonomy
"""

from django.db import models
import uuid

class City(models.Model):
    """Metropolitan area / city"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    code = models.CharField(max_length=10, unique=True)
    country = models.CharField(max_length=100, default='TR')
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'catalog_city'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Sector(models.Model):
    """Industry sector / sektör"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'catalog_sector'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FilterDefinition(models.Model):
    """
    Query filter definitions for batch customization
    e.g., "employee_count", "annual_revenue", "founding_year"
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Data type
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('number', 'Number'),
            ('date', 'Date'),
            ('boolean', 'Boolean'),
            ('enum', 'Enum'),
        ],
        default='string'
    )
    
    # Enum values (if data_type='enum')
    enum_values = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'catalog_filter_definition'
        ordering = ['name']
    
    def __str__(self):
        return self.name
