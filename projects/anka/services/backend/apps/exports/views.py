"""
ViewSets for exports app.
"""

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import OrganizationMember
from apps.exports.models import Export
from apps.exports.serializers import ExportCreateSerializer, ExportSerializer


class ExportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Export.objects.all().select_related("organization", "batch")
    ordering = ["-created_at"]
    ordering_fields = ["created_at", "status", "format"]

    def get_serializer_class(self):
        if self.action in {"create"}:
            return ExportCreateSerializer
        return ExportSerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Export.objects.none()

        org_ids = OrganizationMember.objects.filter(
            user=self.request.user, is_active=True
        ).values_list("organization_id", flat=True)

        return super().get_queryset().filter(organization_id__in=org_ids)

    def perform_create(self, serializer):
        batch = serializer.validated_data.get("batch")
        is_member = OrganizationMember.objects.filter(
            organization=batch.organization, user=self.request.user, is_active=True
        ).exists()

        if not is_member:
            raise PermissionDenied("Organization erişimi yok.")

        serializer.save(organization=batch.organization)
