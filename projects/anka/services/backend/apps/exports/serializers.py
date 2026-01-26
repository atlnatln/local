"""
Serializers for exports app.
"""

from rest_framework import serializers

from apps.exports.models import Export


class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = [
            "id",
            "organization",
            "batch",
            "format",
            "status",
            "file_path",
            "file_size",
            "signed_url",
            "signed_url_expires_at",
            "total_rows",
            "error_message",
            "created_at",
            "completed_at",
            "updated_at",
        ]
        read_only_fields = fields


class ExportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = ["id", "batch", "format"]
        read_only_fields = ["id"]
