"""Payments app models"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class PaymentIntent(models.Model):
    """
    Payment intent represents a user's intention to purchase credits.
    Maps to Iyzico payment request.
    """
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_intents')
    
    # Amount in Turkish Lira (smallest unit)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # e.g. 99.00
    credits = models.IntegerField()  # Number of credits to purchase
    
    # Iyzico identifiers
    conversation_id = models.CharField(max_length=255, unique=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(null=True, blank=True)
    error_code = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['conversation_id']),
        ]
    
    def __str__(self):
        return f"Intent {self.id} - {self.user.username} - {self.credits} credits - {self.status}"
    
    def mark_completed(self):
        """Mark intent as completed and set completion time.
        
        Uses save(update_fields=...) so that post_save signal receivers
        can detect exactly which fields changed (required for credit granting).
        """
        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])


class PaymentTransaction(models.Model):
    """
    Represents actual payment transaction through Iyzico.
    One intent can have multiple transactions if retries occur.
    """
    PENDING = 'pending'
    AUTHORIZED = 'authorized'
    SUCCESS = 'success'
    DECLINED = 'declined'
    ERROR = 'error'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (AUTHORIZED, 'Authorized'),
        (SUCCESS, 'Success'),
        (DECLINED, 'Declined'),
        (ERROR, 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intent = models.ForeignKey(PaymentIntent, on_delete=models.CASCADE, related_name='transactions')
    
    # Iyzico response data
    iyzico_transaction_id = models.CharField(max_length=255, unique=True)
    iyzico_payment_id = models.CharField(max_length=255, null=True, blank=True)
    iyzico_conversation_id = models.CharField(max_length=255)
    
    # Payment method info (masked for security)
    card_last_four = models.CharField(max_length=4, null=True, blank=True)
    card_bin = models.CharField(max_length=6, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Amount and fee
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Error tracking
    error_message = models.TextField(null=True, blank=True)
    error_code = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['intent']),
            models.Index(fields=['status']),
            models.Index(fields=['iyzico_transaction_id']),
        ]
    
    def __str__(self):
        return f"Transaction {self.id} - {self.status}"


class PaymentWebhook(models.Model):
    """
    Stores incoming webhooks from Iyzico for audit trail and retry handling.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Webhook metadata
    event_type = models.CharField(max_length=50)  # e.g., 'payment.completed', 'payment.failed'
    conversation_id = models.CharField(max_length=255)
    
    # Payload
    payload = models.JSONField()  # Raw webhook payload from Iyzico
    
    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(null=True, blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['processed']),
        ]
    
    def __str__(self):
        return f"Webhook {self.id} - {self.event_type} - {self.conversation_id}"
    
    def mark_processed(self):
        """Mark webhook as processed."""
        self.processed = True
        self.processed_at = timezone.now()
        self.save()