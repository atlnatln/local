"""
Serializers for disputes app.
"""

from rest_framework import serializers

from apps.disputes.models import Dispute, DisputeItem


class DisputeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeItem
        fields = [
            "id",
            "dispute",
            "batch_item",
            "field_name",
            "reported_value",
            "current_value",
            "is_accepted",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_accepted"]


class DisputeSerializer(serializers.ModelSerializer):
    items = DisputeItemSerializer(many=True, read_only=True)

    class Meta:
        model = Dispute
        fields = [
            "id",
            "organization",
            "batch",
            "reason",
            "evidence_url",
            "evidence_data",
            "status",
            "decision",
            "decision_reason_code",
            "refund_amount",
            "metadata",
            "created_at",
            "resolved_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "status",
            "decision",
            "decision_reason_code",
            "refund_amount",
            "metadata",
            "created_at",
            "resolved_at",
            "updated_at",
            "items",
        ]


class DisputeCreateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeItem
        fields = [
            "batch_item",
            "field_name",
            "reported_value",
            "current_value",
            "metadata",
        ]


class DisputeCreateSerializer(serializers.ModelSerializer):
    items = DisputeCreateItemSerializer(many=True, required=False)

    class Meta:
        model = Dispute
        fields = [
            "id",
            "organization",
            "batch",
            "reason",
            "evidence_url",
            "evidence_data",
            "items",
        ]
        read_only_fields = ["id"]
