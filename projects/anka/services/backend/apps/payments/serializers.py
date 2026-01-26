"""
Serializers for payment operations.
"""

from rest_framework import serializers
from decimal import Decimal
from .models import PaymentIntent, PaymentTransaction


class PaymentIntentSerializer(serializers.ModelSerializer):
    """Serializer for PaymentIntent model."""
    
    class Meta:
        model = PaymentIntent
        fields = [
            'id',
            'user',
            'amount',
            'credits',
            'conversation_id',
            'payment_id',
            'status',
            'created_at',
            'updated_at',
            'completed_at',
            'error_message',
            'error_code',
        ]
        read_only_fields = [
            'id',
            'user',
            'conversation_id',
            'payment_id',
            'status',
            'created_at',
            'updated_at',
            'completed_at',
            'error_message',
            'error_code',
        ]
    
    def validate_amount(self, value):
        """Validate amount is positive and not too large."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        if value > Decimal('99999.99'):
            raise serializers.ValidationError("Amount too large")
        return value
    
    def validate_credits(self, value):
        """Validate credits is positive."""
        if value <= 0:
            raise serializers.ValidationError("Credits must be greater than 0")
        return value


class PaymentIntentCreateSerializer(serializers.Serializer):
    """Serializer for creating a new payment intent."""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    credits = serializers.IntegerField(min_value=1)
    package_type = serializers.ChoiceField(
        choices=['starter', 'professional', 'enterprise'],
        required=False,
        help_text="Optional package type for tracking"
    )
    
    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class PaymentIntentConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a payment."""
    
    token = serializers.CharField(
        required=True,
        help_text="Token from Iyzico checkout form"
    )
    conversation_id = serializers.CharField(
        required=True,
        help_text="Conversation ID of the payment intent"
    )


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PaymentTransaction model."""
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id',
            'payment_intent',
            'iyzico_transaction_id',
            'iyzico_payment_id',
            'iyzico_conversation_id',
            'card_last_four',
            'card_bin',
            'status',
            'amount',
            'fees',
            'created_at',
            'updated_at',
            'error_message',
            'error_code',
        ]
        read_only_fields = [
            'id',
            'payment_intent',
            'iyzico_transaction_id',
            'iyzico_payment_id',
            'iyzico_conversation_id',
            'card_last_four',
            'card_bin',
            'status',
            'amount',
            'fees',
            'created_at',
            'updated_at',
            'error_message',
            'error_code',
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer for listing payment intents."""
    
    class Meta:
        model = PaymentIntent
        fields = [
            'id',
            'amount',
            'credits',
            'status',
            'created_at',
            'completed_at',
        ]
