"""
Celery tasks for exports app.
"""

import csv
import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from openpyxl import Workbook

from apps.batches.models import BatchItem
from apps.common.alerts import emit_alarm
from apps.exports.models import Export, ExportLog


def _normalize_item_data(data):
    if not isinstance(data, dict):
        return {}

    normalized = dict(data)
    if "formatted_address" not in normalized and "formattedAddress" in normalized:
        normalized["formatted_address"] = normalized.get("formattedAddress")
    if "website_uri" not in normalized and "websiteUri" in normalized:
        normalized["website_uri"] = normalized.get("websiteUri")
    if "phone_number" not in normalized and "nationalPhoneNumber" in normalized:
        normalized["phone_number"] = normalized.get("nationalPhoneNumber")
    return normalized


def _collect_export_rows(export):
    queryset = BatchItem.objects.filter(
        batch=export.batch,
        is_verified=True,
        has_error=False,
    ).order_by("created_at")

    rows = []
    for item in queryset:
        item_data = _normalize_item_data(item.data)
        rows.append(
            {
                "firma": item.firm_name or "",
                "telefon": item_data.get("phone_number") or item_data.get("phone") or "",
                "website": item_data.get("website_uri") or item_data.get("website") or "",
                "email": item_data.get("email") or "",
                "adres": item_data.get("formatted_address") or item_data.get("address") or "",
            }
        )
    return rows


def _build_signed_url(relative_media_path: str) -> str:
    base_url = (
        os.environ.get("APP_PUBLIC_BASE_URL")
        or os.environ.get("NEXT_PUBLIC_SITE_URL")
        or "https://ankadata.com.tr"
    ).rstrip("/")
    media_path = quote(relative_media_path.strip("/"), safe="/")
    return f"{base_url}/media/{media_path}"


def _log_export_event(export, event: str, message: str, metadata=None):
    ExportLog.objects.create(
        export=export,
        event=event,
        message=message,
        metadata=metadata or {},
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_export_file(self, export_id):
    """
    Generate a CSV or XLSX export file for the given export_id.

    Retries up to 3 times with exponential back-off (2m → 4m → 8m).
    Emits an alarm on final failure.
    """
    export = Export.objects.select_related("batch", "organization").get(id=export_id)
    export.status = "processing"
    export.error_message = ""
    export.save(update_fields=["status", "error_message", "updated_at"])
    _log_export_event(
        export,
        "processing_started",
        f"Export generation started (attempt {self.request.retries + 1}/{self.max_retries + 1})",
    )

    try:
        rows = _collect_export_rows(export)
        headers = ["Firma", "Telefon", "Website", "Email", "Adres"]

        export_dir = Path(settings.MEDIA_ROOT) / "exports" / str(export.batch.id)
        export_dir.mkdir(parents=True, exist_ok=True)

        prefix = slugify(f"{export.batch.city}-{export.batch.sector}") or "batch-export"
        safe_filename = f"{prefix}-{export.batch.id}.{export.format}"
        file_path = export_dir / safe_filename

        if export.format == "csv":
            with file_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(headers)
                for row in rows:
                    writer.writerow([row["firma"], row["telefon"], row["website"], row["email"], row["adres"]])
        elif export.format == "xlsx":
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Anka Export"
            worksheet.append(headers)
            for row in rows:
                worksheet.append([row["firma"], row["telefon"], row["website"], row["email"], row["adres"]])
            workbook.save(file_path)
        else:
            raise ValueError(f"Unsupported export format: {export.format}")

        relative_media_path = file_path.relative_to(settings.MEDIA_ROOT).as_posix()
        signed_url = _build_signed_url(relative_media_path)

        export.status = "completed"
        export.file_path = str(file_path)
        export.file_size = file_path.stat().st_size
        export.total_rows = len(rows)
        export.signed_url = signed_url
        export.signed_url_expires_at = timezone.now() + timedelta(hours=24)
        export.completed_at = timezone.now()
        export.save(
            update_fields=[
                "status",
                "file_path",
                "file_size",
                "total_rows",
                "signed_url",
                "signed_url_expires_at",
                "completed_at",
                "updated_at",
            ]
        )
        _log_export_event(
            export,
            "completed",
            "Export generated successfully",
            {
                "format": export.format,
                "file_path": export.file_path,
                "rows": export.total_rows,
                "size": export.file_size,
            },
        )

        batch = export.batch
        if export.format == "csv":
            batch.csv_url = signed_url
            batch.save(update_fields=["csv_url", "updated_at"])
        elif export.format == "xlsx":
            batch.xlsx_url = signed_url
            batch.save(update_fields=["xlsx_url", "updated_at"])

        return str(export.id)
    except Exception as exc:
        retries_left = self.max_retries - self.request.retries

        if retries_left > 0:
            # Transient failure — schedule a retry with exponential back-off
            countdown = 120 * (2 ** self.request.retries)  # 2m, 4m, 8m
            _log_export_event(
                export,
                "retry_scheduled",
                f"Export generation failed, retrying in {countdown}s ({retries_left} attempts left)",
                {"error": str(exc), "attempt": self.request.retries + 1, "countdown": countdown},
            )
            # Reset status so the SLA watchdog tracks the next attempt's timer
            export.status = "pending"
            export.error_message = f"Retrying ({retries_left} left): {exc}"
            export.save(update_fields=["status", "error_message", "updated_at"])
            raise self.retry(exc=exc, countdown=countdown)

        # Final failure — mark export and emit alarm
        export.status = "failed"
        export.error_message = str(exc)
        export.save(update_fields=["status", "error_message", "updated_at"])
        _log_export_event(
            export,
            "failed",
            "Export generation failed (max retries exhausted)",
            {"error": str(exc), "attempts": self.max_retries + 1},
        )
        emit_alarm(
            code="EXPORT_FAILED",
            message="Export generation failed after all retries",
            metadata={
                "export_id": str(export_id),
                "batch_id": str(export.batch_id),
                "format": export.format,
                "error": str(exc),
            },
            exc=exc,
        )
        raise


@shared_task
def monitor_stuck_exports_task():
    sla_minutes = int(os.environ.get("ANKA_EXPORT_SLA_MINUTES", "5"))
    threshold = timezone.now() - timedelta(minutes=max(1, sla_minutes))

    stuck_exports = Export.objects.filter(
        status="processing",
        updated_at__lt=threshold,
    ).select_related("batch")

    count = 0
    for export in stuck_exports:
        export.status = "failed"
        export.error_message = f"Export processing SLA exceeded ({sla_minutes}m)"
        export.save(update_fields=["status", "error_message", "updated_at"])
        _log_export_event(
            export,
            "sla_failed",
            "Export marked failed by SLA watchdog",
            {
                "sla_minutes": sla_minutes,
                "batch_id": str(export.batch_id),
                "format": export.format,
            },
        )
        emit_alarm(
            code="EXPORT_SLA_EXCEEDED",
            message=f"Export stuck in processing for >{sla_minutes}m — SLA watchdog killed it",
            metadata={
                "export_id": str(export.id),
                "batch_id": str(export.batch_id),
                "format": export.format,
                "sla_minutes": sla_minutes,
            },
        )
        count += 1

    return count
