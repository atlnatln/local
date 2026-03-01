"""
Serializers for batches app.
"""

from rest_framework import serializers

from apps.accounts.models import Organization, OrganizationMember
from apps.batches.models import Batch, BatchItem


class BatchItemSerializer(serializers.ModelSerializer):
    @staticmethod
    def _normalize_item_data(data):
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        key_map = {
            "formattedAddress": "formatted_address",
            "websiteUri": "website_uri",
            "nationalPhoneNumber": "phone_number",
        }

        for source_key, target_key in key_map.items():
            if target_key not in normalized and source_key in normalized:
                normalized[target_key] = normalized.get(source_key)

        return normalized

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["data"] = self._normalize_item_data(representation.get("data"))
        return representation

    class Meta:
        model = BatchItem
        fields = [
            "id",
            "batch",
            "firm_id",
            "firm_name",
            "is_verified",
            "has_error",
            "error_message",
            "data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BatchListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoint — no nested items."""

    class Meta:
        model = Batch
        fields = [
            "id",
            "organization",
            "created_by",
            "city",
            "sector",
            "record_count_estimate",
            "estimated_cost",
            "status",
            "ids_collected",
            "ids_verified",
            "contacts_enriched",
            "emails_enriched",
            "csv_url",
            "xlsx_url",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class BatchSerializer(serializers.ModelSerializer):
    items = BatchItemSerializer(many=True, read_only=True)

    class Meta:
        model = Batch
        fields = [
            "id",
            "organization",
            "created_by",
            "city",
            "sector",
            "filters",
            "sort_rule_version",
            "query_hash",
            "input_snapshot",
            "total_records",
            "processed_records",
            "error_records",
            "ids_collected",
            "ids_verified",
            "contacts_enriched",
            "emails_enriched",
            "skipped_404",
            "aborted_reason",
            "record_count_estimate",
            "estimated_cost",
            "status",
            "csv_url",
            "xlsx_url",
            "metadata",
            "created_at",
            "started_at",
            "completed_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "query_hash",
            "input_snapshot",
            "total_records",
            "processed_records",
            "error_records",
            "ids_collected",
            "ids_verified",
            "contacts_enriched",
            "emails_enriched",
            "skipped_404",
            "aborted_reason",
            "estimated_cost",
            "status",
            "csv_url",
            "xlsx_url",
            "metadata",
            "created_at",
            "started_at",
            "completed_at",
            "updated_at",
            "items",
        ]

    def validate_organization(self, organization):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return organization

        is_member = OrganizationMember.objects.filter(
            organization=organization, user=request.user, is_active=True
        ).exists()
        if not is_member:
            raise serializers.ValidationError("Organization erişimi yok.")

        return organization
