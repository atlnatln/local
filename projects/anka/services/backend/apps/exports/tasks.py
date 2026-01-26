"""
Celery tasks for exports app.
"""

from celery import shared_task

from apps.exports.models import Export


@shared_task
def generate_export_file(export_id):
    export = Export.objects.get(id=export_id)
    export.status = "processing"
    export.save(update_fields=["status", "updated_at"])

    # Placeholder for file generation logic
    export.status = "completed"
    export.signed_url = export.signed_url or ""
    export.save(update_fields=["status", "signed_url", "updated_at"])

    return str(export.id)
