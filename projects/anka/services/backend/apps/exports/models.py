"""Exports app: CSV/XLSX file generation and signed URLs"""

from django.db import models
import uuid
from apps.accounts.models import Organization
from apps.batches.models import Batch

class Export(models.Model):
    """Data export job"""
    
    FORMAT_CHOICES = (
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='exports')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='exports')
    
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='csv')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # File info
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(default=0)
    
    # Signed URL (S3)
    signed_url = models.URLField(blank=True)
    signed_url_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    total_rows = models.PositiveIntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exports_export'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
        ]
    
    def __str__(self):
        return f"Export {self.id} ({self.format})"


class ExportLog(models.Model):
    """Export operation audit log"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    export = models.ForeignKey(Export, on_delete=models.CASCADE, related_name='logs')
    
    event = models.CharField(max_length=100)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exports_export_log'
        ordering = ['-created_at']
