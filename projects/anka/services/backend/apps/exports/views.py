"""
ViewSets for exports app.
"""

import logging
import mimetypes
from pathlib import Path

from django.http import FileResponse, Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import OrganizationMember
from apps.exports.models import Export
from apps.exports.serializers import ExportCreateSerializer, ExportSerializer
from apps.exports.tasks import generate_export_file

logger = logging.getLogger(__name__)


def _enqueue_export_generation(export_id: str) -> None:
    try:
        generate_export_file.delay(export_id)
        return
    except Exception as exc:
        logger.warning(
            "Export %s: async enqueue failed, falling back to sync generation (%s)",
            export_id,
            exc,
        )

    try:
        generate_export_file(export_id)
    except Exception:
        logger.exception("Export %s: sync fallback generation failed", export_id)


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

        qs = super().get_queryset().filter(organization_id__in=org_ids)

        # Optional filtering by batch ID: GET /api/exports/?batch=<uuid>
        batch_id = self.request.query_params.get("batch")
        if batch_id:
            qs = qs.filter(batch_id=batch_id)

        return qs

    def perform_create(self, serializer):
        batch = serializer.validated_data.get("batch")
        is_member = OrganizationMember.objects.filter(
            organization=batch.organization, user=self.request.user, is_active=True
        ).exists()

        if not is_member:
            raise PermissionDenied("Organization erişimi yok.")

        if batch.status not in {"READY", "PARTIAL"}:
            raise ValidationError({"detail": "Batch henüz export için hazır değil."})

        if (batch.contacts_enriched or 0) <= 0:
            raise ValidationError({"detail": "Export için teslim edilebilir kayıt bulunamadı."})

        export = serializer.save(organization=batch.organization)
        _enqueue_export_generation(str(export.id))

    # ── Secure file download (no public media access needed) ──────────
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """
        GET /api/exports/{id}/download/

        Streams the actual file behind auth — no publicly-guessable URL required.
        """
        export = self.get_object()  # permission check via get_queryset filter

        if export.status != "completed":
            raise ValidationError({"detail": "Export henüz hazır değil."})

        file_path = Path(export.file_path) if export.file_path else None
        if not file_path or not file_path.exists():
            raise Http404("Export dosyası bulunamadı.")

        content_type, _ = mimetypes.guess_type(str(file_path))
        response = FileResponse(
            open(file_path, "rb"),
            content_type=content_type or "application/octet-stream",
        )
        filename = file_path.name
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    # ── Regenerate expired export URL ─────────────────────────────────
    @action(detail=True, methods=["post"], url_path="regenerate")
    def regenerate(self, request, pk=None):
        """
        POST /api/exports/{id}/regenerate/

        Re-queues the export generation task so the user gets a fresh file & URL.
        """
        export = self.get_object()

        if export.status == "processing":
            raise ValidationError({"detail": "Export zaten işleniyor."})

        # Reset and re-queue
        export.status = "pending"
        export.error_message = ""
        export.signed_url = ""
        export.signed_url_expires_at = None
        export.save(update_fields=[
            "status", "error_message", "signed_url", "signed_url_expires_at", "updated_at"
        ])
        _enqueue_export_generation(str(export.id))

        serializer = ExportSerializer(export)
        return Response(serializer.data)
