"""
Ledger app: Financial transactions (Sade design - batch-level only)
KRİTİK: 1 row per batch event, NOT N rows for N records
"""

from django.db import models
from django.db.models import UniqueConstraint, Q
from decimal import Decimal
import uuid
from apps.accounts.models import Organization

class CreditPackage(models.Model):
    """
    User's credit balance (pre-paid model)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='credits')
    
    # Balance (hesap bakiyesi)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Historical
    total_purchased = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_refunded = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ledger_credit_package'
    
    def __str__(self):
        return f"Credits: {self.organization.name} (${self.balance})"


class LedgerEntry(models.Model):
    """
    Financial transaction log (Batch-level, not record-level)
    
    DESIGN: 1 ledger row = 1 batch event
    
    Types:
    - 'purchase': Credit package purchase (payment)
    - 'spent': Batch data retrieval (cost deducted)
    - 'refund': Dispute/cancellation refund
    """
    
    TRANSACTION_TYPE_CHOICES = (
        ('purchase', 'Credit Purchase'),
        ('spent', 'Data Retrieval'),
        ('refund', 'Refund/Dispute'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='ledger_entries')
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Transaction amount
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # References (esas batch/payment/dispute ile bağlantı)
    reference_type = models.CharField(
        max_length=20,
        choices=[('batch', 'Batch'), ('payment', 'Payment'), ('dispute', 'Dispute')],
        default='batch'
    )
    reference_id = models.CharField(max_length=255, db_index=True)  # batch_id, payment_id, dispute_id
    
    # Description
    description = models.TextField(blank=True)
    
    # Balance Snapshot (audit trail)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ledger_ledger_entry'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['reference_id']),
        ]
        constraints = [
            UniqueConstraint(
                fields=['reference_type', 'reference_id'],
                name='ledger_unique_reference',
                violation_error_message='Bu reference için zaten bir ledger kaydı mevcut.'
            ),
        ]
    
    def __str__(self):
        return f"{self.transaction_type.upper()} - {self.organization.name} ({self.amount})"


class RecurringCharge(models.Model):
    """
    Recurring subscription charges (opsiyonel - MVP-0 da pasif)
    """
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='recurring_charges')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Billing cycle
    billing_date = models.IntegerField(default=1)  # Day of month
    next_charge_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ledger_recurring_charge'
    
    def __str__(self):
        return f"{self.organization.name} - ${self.amount}/{self.frequency}"
