from pathlib import Path

import pytest

from apps.accounts.models import Organization
from apps.batches.models import Batch, BatchItem
from apps.exports.models import Export, ExportLog
from apps.exports.tasks import generate_export_file, monitor_stuck_exports_task


@pytest.mark.django_db
def test_generate_export_file_creates_csv_and_updates_batch_url(monkeypatch):
    monkeypatch.setenv("APP_PUBLIC_BASE_URL", "https://ankadata.com.tr")

    org = Organization.objects.create(
        name="Export Task Org",
        slug="export-task-org",
        email="export-task@example.com",
    )

    batch = Batch.objects.create(
        organization=org,
        created_by="tester",
        city="ankara",
        sector="şehir plancısı",
        contacts_enriched=1,
        status="READY",
    )

    BatchItem.objects.create(
        batch=batch,
        firm_id="p1",
        firm_name="Firma 1",
        is_verified=True,
        has_error=False,
        data={
            "phone_number": "(0312) 111 11 11",
            "website_uri": "https://example.com",
            "formatted_address": "Ankara",
            "stage_3_enterprise": True,
        },
    )

    export = Export.objects.create(
        organization=org,
        batch=batch,
        format="csv",
        status="pending",
    )

    generate_export_file.apply(args=[str(export.id)])

    export.refresh_from_db()
    batch.refresh_from_db()

    assert export.status == "completed"
    assert export.total_rows == 1
    assert export.file_size > 0
    assert export.signed_url.startswith("https://ankadata.com.tr/media/exports/")
    assert batch.csv_url == export.signed_url
    assert Path(export.file_path).exists()


@pytest.mark.django_db
def test_generate_export_file_creates_xlsx_and_updates_batch_url(monkeypatch):
    monkeypatch.setenv("APP_PUBLIC_BASE_URL", "https://ankadata.com.tr")

    org = Organization.objects.create(
        name="Export Task Org 2",
        slug="export-task-org-2",
        email="export-task-2@example.com",
    )

    batch = Batch.objects.create(
        organization=org,
        created_by="tester",
        city="izmir",
        sector="mimar",
        contacts_enriched=1,
        status="READY",
    )

    BatchItem.objects.create(
        batch=batch,
        firm_id="p2",
        firm_name="Firma 2",
        is_verified=True,
        has_error=False,
        data={
            "nationalPhoneNumber": "(0232) 222 22 22",
            "websiteUri": "https://example.org",
            "formattedAddress": "İzmir",
            "stage_3_enterprise": True,
        },
    )

    export = Export.objects.create(
        organization=org,
        batch=batch,
        format="xlsx",
        status="pending",
    )

    generate_export_file.apply(args=[str(export.id)])

    export.refresh_from_db()
    batch.refresh_from_db()

    assert export.status == "completed"
    assert export.total_rows == 1
    assert export.file_path.endswith(".xlsx")
    assert export.file_size > 0
    assert batch.xlsx_url == export.signed_url
    assert Path(export.file_path).exists()


@pytest.mark.django_db
def test_monitor_stuck_exports_marks_failed(monkeypatch):
    monkeypatch.setenv("ANKA_EXPORT_SLA_MINUTES", "1")

    org = Organization.objects.create(
        name="Export SLA Org",
        slug="export-sla-org",
        email="export-sla@example.com",
    )

    batch = Batch.objects.create(
        organization=org,
        created_by="tester",
        city="ankara",
        sector="şehir plancısı",
        contacts_enriched=1,
        status="READY",
    )

    export = Export.objects.create(
        organization=org,
        batch=batch,
        format="csv",
        status="processing",
    )

    Export.objects.filter(id=export.id).update(updated_at="2000-01-01T00:00:00Z")

    affected = monitor_stuck_exports_task()
    export.refresh_from_db()

    assert affected == 1
    assert export.status == "failed"
    assert "SLA exceeded" in export.error_message
    assert ExportLog.objects.filter(export=export, event="sla_failed").exists()
