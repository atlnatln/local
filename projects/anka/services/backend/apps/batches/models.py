"""
Batches app: Batch processing with deterministic hashing.
"""

from django.db import models
from django.utils.functional import cached_property
import hashlib
import json
import uuid
from apps.accounts.models import Organization

class Batch(models.Model):
    """
    Deterministic batch - aynı query_hash = aynı sonuç kümesi
    KRİTİK: query_hash = SHA256(city + sector + filters_json + sort_rule_version)
    """
    
    STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('COLLECTING_IDS', 'Collecting IDs'),
        ('FILTERING', 'Filtering'),
        ('ENRICHING_CONTACTS', 'Enriching Contacts'),
        ('READY', 'Ready'),
        ('PARTIAL', 'Partial'),
        ('FAILED', 'Failed'),
        # Legacy/Fallback
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Organization & Owner
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='batches')
    created_by = models.CharField(max_length=255)  # User identifier
    
    # Query Definition
    city = models.CharField(max_length=100, db_index=True)
    sector = models.CharField(max_length=100, db_index=True)
    
    # Filters (JSON) - deterministic field
    filters = models.JSONField(default=dict)
    sort_rule_version = models.PositiveIntegerField(default=1)
    
    # Deterministic Hash (SHA256)
    query_hash = models.CharField(
        max_length=64,
        unique=False,  # Can have duplicates (same query = same hash)
        db_index=True,
        help_text="SHA256 of (city + sector + filters_json + sort_rule_version)"
    )
    
    # Input Snapshot (untuk audit & debugging)
    input_snapshot = models.JSONField(default=dict)
    
    # Stats
    total_records = models.PositiveIntegerField(default=0)
    processed_records = models.PositiveIntegerField(default=0)
    error_records = models.PositiveIntegerField(default=0)
    
    # Audit Metrics
    ids_collected = models.PositiveIntegerField(default=0)
    ids_verified = models.PositiveIntegerField(default=0)
    contacts_enriched = models.PositiveIntegerField(default=0)
    skipped_404 = models.PositiveIntegerField(default=0)
    aborted_reason = models.CharField(max_length=255, blank=True)

    # Pricing & Credits
    record_count_estimate = models.PositiveIntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status & Timeline
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED', db_index=True)
    
    # File References
    csv_url = models.URLField(blank=True, null=True)
    xlsx_url = models.URLField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'batches_batch'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['query_hash']),
            models.Index(fields=['city', 'sector']),
        ]
    
    def __str__(self):
        return f"Batch {self.id} - {self.city} / {self.sector}"
    
    def calculate_query_hash(self):
        """
        Calculate deterministic SHA256 hash from:
        city + sector + filters (JSON) + sort_rule_version
        """
        # Sort filters JSON to ensure determinism
        filters_str = json.dumps(self.filters, sort_keys=True, separators=(',', ':'))
        hash_input = f"{self.city}|{self.sector}|{filters_str}|{self.sort_rule_version}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        # Auto-calculate query_hash if not set
        if not self.query_hash:
            self.query_hash = self.calculate_query_hash()
        
        # Store input snapshot for audit
        if not self.input_snapshot:
            self.input_snapshot = {
                'city': self.city,
                'sector': self.sector,
                'filters': self.filters,
                'sort_rule_version': self.sort_rule_version,
            }
        
        super().save(*args, **kwargs)


class BatchItem(models.Model):
    """
    Individual record in a batch
    KRİTİK: Ledger is batch-level, NOT record-level
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='items')
    
    # Record Reference
    firm_id = models.CharField(max_length=255, db_index=True)
    firm_name = models.CharField(max_length=255)
    
    # Status
    is_verified = models.BooleanField(default=False)
    has_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Data (flexible)
    data = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'batches_batch_item'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['batch', 'firm_id']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"Item {self.firm_name} (Batch {self.batch.id})"
