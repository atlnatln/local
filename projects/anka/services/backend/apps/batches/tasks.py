from celery import shared_task
from apps.batches.services import BatchProcessor
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_batch_task(batch_id):
    logger.info(f"Starting processing for batch {batch_id}")
    processor = BatchProcessor(batch_id)
    processor.run_pipeline()
