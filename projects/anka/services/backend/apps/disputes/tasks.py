"""
Celery tasks for disputes app.
"""

import logging

from celery import shared_task

from apps.common.alerts import emit_alarm
from apps.disputes.models import Dispute
from apps.disputes.rule_engine import DecisionEngine

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def auto_resolve_dispute(self, dispute_id):
    """
    Evaluate evidence and auto-resolve a dispute via DecisionEngine.

    Retries up to 2 times with 60s / 120s backoff on transient errors.
    Emits DISPUTE_RESOLUTION_FAILED alarm on final failure.
    """
    try:
        dispute = Dispute.objects.get(id=dispute_id)
        decision, reason_code = DecisionEngine.evaluate(dispute.evidence_data or {})

        dispute.decision = decision
        dispute.decision_reason_code = reason_code
        dispute.status = "resolved"
        dispute.save(
            update_fields=["decision", "decision_reason_code", "status", "updated_at"]
        )

        logger.info(
            "Dispute %s auto-resolved: decision=%s reason=%s",
            dispute_id,
            decision,
            reason_code,
        )
        return str(dispute.id)

    except Dispute.DoesNotExist:
        logger.warning("auto_resolve_dispute: Dispute %s not found", dispute_id)
        return None

    except Exception as exc:
        retries_left = self.max_retries - self.request.retries
        if retries_left > 0:
            countdown = 60 * (2 ** self.request.retries)
            logger.warning(
                "Dispute %s resolution failed, retrying in %ds (%d left): %s",
                dispute_id, countdown, retries_left, exc,
            )
            raise self.retry(exc=exc, countdown=countdown)

        # Final failure
        logger.exception("Dispute %s resolution failed permanently: %s", dispute_id, exc)
        emit_alarm(
            code="DISPUTE_RESOLUTION_FAILED",
            message="Dispute auto-resolution failed after all retries",
            metadata={
                "dispute_id": str(dispute_id),
                "error": str(exc),
            },
            exc=exc,
        )
        raise
