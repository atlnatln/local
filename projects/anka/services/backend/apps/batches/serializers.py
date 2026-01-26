"""
Serializers for batches app.
"""

from rest_framework import serializers

from apps.accounts.models import Organization, OrganizationMember
from apps.batches.models import Batch, BatchItem


class BatchItemSerializer(serializers.ModelSerializer):
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
