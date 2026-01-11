"""
Records app: Firm records with field-level provenance
"""

from django.db import models
import uuid
from apps.batches.models import Batch

class Record(models.Model):
    """
    Firm record with field-level provenance tracking
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='records', null=True, blank=True)
    
    # Firm reference
    firm_id = models.CharField(max_length=255, unique=True, db_index=True)
    firm_name = models.CharField(max_length=255)
    
    # Fields (generic - flexibility)
    data = models.JSONField(default=dict)  # All firm data
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'records_record'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['firm_id']),
        ]
    
    def __str__(self):
        return f"Record: {self.firm_name}"


class RecordField(models.Model):
    """
    Field-level provenance: value, verified, source, confidence
    """
    
    SOURCE_CHOICES = (
        ('direct', 'Direct'),  # Provider API
        ('aggregated', 'Aggregated'),  # Multiple sources
        ('inferred', 'Inferred'),  # Derived from other fields
        ('user_provided', 'User Provided'),  # Customer input
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='fields')
    
    # Field definition
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    
    # Provenance
    verified = models.BooleanField(default=False)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='direct')
    confidence = models.FloatField(default=1.0)  # 0.0 - 1.0
    
    # Source provider
    source_provider = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    observed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'records_record_field'
        unique_together = [['record', 'field_name']]
        ordering = ['-observed_at']
        indexes = [
            models.Index(fields=['record', 'field_name']),
            models.Index(fields=['verified']),
        ]
    
    def __str__(self):
        return f"{self.record.firm_name}.{self.field_name}"
