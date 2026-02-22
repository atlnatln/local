from celery import shared_task
from apps.batches.services import BatchProcessor
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_batch_task(batch_id):
    logger.info(f"Starting processing for batch {batch_id}")
    processor = BatchProcessor(batch_id)
    processor.run_pipeline()


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def enrich_emails_task(self, batch_id):
    """
    Standalone email enrichment task.
    Batch pipeline tamamlandıktan sonra veya manuel retry için çağrılabilir.
    process_batch_task içinden de otomatik tetiklenir.

    Örnek manuel tetikleme::
        from apps.batches.tasks import enrich_emails_task
        enrich_emails_task.delay("<batch-uuid>")
    """
    logger.info(
        "[enrich_emails_task] batch_id=%s (attempt %s)",
        batch_id,
        self.request.retries + 1,
    )
    try:
        processor = BatchProcessor(batch_id)
        processor.run_email_enrichment_stage()
    except Exception as exc:
        logger.exception(
            "[enrich_emails_task] Failed for batch %s: %s", batch_id, exc
        )
        raise self.retry(exc=exc)



