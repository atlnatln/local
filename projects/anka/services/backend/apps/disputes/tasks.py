"""
Celery tasks for disputes app.
"""

from celery import shared_task

from apps.disputes.models import Dispute
from apps.disputes.rule_engine import DecisionEngine


@shared_task
def auto_resolve_dispute(dispute_id):
    dispute = Dispute.objects.get(id=dispute_id)
    decision, reason_code = DecisionEngine.evaluate(dispute.evidence_data or {})

    dispute.decision = decision
    dispute.decision_reason_code = reason_code
    dispute.status = "resolved"
    dispute.save(update_fields=["decision", "decision_reason_code", "status", "updated_at"])

    return str(dispute.id)
