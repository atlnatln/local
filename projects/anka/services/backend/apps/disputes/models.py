"""
Disputes app: Auto-resolution of data accuracy disputes
"""

from django.db import models
import uuid
from apps.accounts.models import Organization
from apps.batches.models import Batch, BatchItem

class DisputeRule(models.Model):
    """
    Automated dispute resolution rules
    
    KARAR MATRİSİ:
    ACCEPT if ANY:
    - Email hard bounce (SMTP 550/5xx)
    - Phone validation: "bu firmaya ait değil"
    - Firm closed/inactive
    - Duplicate (same user→same firm→previous batch)
    
    REJECT if:
    - Sales result: ilgilenmiyor, no response, wrong person
    
    DEFAULT: REJECT (MVP-0 no manual review)
    """
    
    RULE_TYPE_CHOICES = (
        ('email_bounce', 'Email Hard Bounce'),
        ('phone_invalid', 'Phone Invalid'),
        ('firm_inactive', 'Firm Inactive/Closed'),
        ('duplicate', 'Duplicate Entry'),
        ('no_response', 'No Response'),
        ('wrong_person', 'Wrong Contact Person'),
    )
    
    DECISION_CHOICES = (
        ('accept', 'Accept Refund'),
        ('reject', 'Reject Refund'),
        ('manual', 'Manual Review'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES, unique=True)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default='manual')
    
    # Configuration
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)  # Higher = checked first
    
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'disputes_dispute_rule'
        ordering = ['-priority', 'rule_type']
    
    def __str__(self):
        return f"{self.rule_type} → {self.decision}"


class Dispute(models.Model):
    """
    Customer dispute about data accuracy
    """
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    DECISION_CHOICES = (
        ('accept', 'Accept Refund'),
        ('reject', 'Reject'),
        ('manual', 'Manual Review'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # References
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='disputes')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='disputes')
    
    # Dispute details
    reason = models.TextField(help_text="Why is the data inaccurate?")
    evidence_url = models.URLField(blank=True, null=True)
    evidence_data = models.JSONField(default=dict, blank=True)
    
    # Status & Decision
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', db_index=True)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, null=True, blank=True)
    decision_reason_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Rule type that triggered decision (from DisputeRule)"
    )
    
    # Refund
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_initiated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'disputes_dispute'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['batch']),
        ]
    
    def __str__(self):
        return f"Dispute {self.id} - {self.status}"


class DisputeItem(models.Model):
    """
    Individual record items in a dispute
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='items')
    batch_item = models.ForeignKey(BatchItem, on_delete=models.CASCADE, null=True, blank=True)
    
    # Item details
    field_name = models.CharField(max_length=255)  # e.g., "email", "phone"
    reported_value = models.TextField(help_text="What the customer says the correct value is")
    current_value = models.TextField(help_text="What we have in our database")
    
    # Status
    is_accepted = models.BooleanField(default=False)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'disputes_dispute_item'
    
    def __str__(self):
        return f"Dispute Item - {self.field_name}"
