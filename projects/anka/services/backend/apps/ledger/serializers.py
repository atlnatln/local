"""
Serializers for ledger app.
"""

from rest_framework import serializers

from apps.ledger.models import CreditPackage, LedgerEntry


class CreditPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPackage
        fields = [
            "id",
            "organization",
            "balance",
            "total_purchased",
            "total_spent",
            "total_refunded",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "organization",
            "transaction_type",
            "amount",
            "status",
            "reference_type",
            "reference_id",
            "description",
            "balance_before",
            "balance_after",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
