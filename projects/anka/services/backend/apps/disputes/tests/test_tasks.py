"""
Tests for apps.disputes.tasks.auto_resolve_dispute
"""

import pytest
from unittest.mock import patch

from apps.accounts.models import Organization
from apps.batches.models import Batch
from apps.disputes.models import Dispute
from apps.disputes.tasks import auto_resolve_dispute


@pytest.mark.django_db
def test_auto_resolve_dispute_accept():
    """Dispute with email_bounce evidence should be resolved as accept."""
    org = Organization.objects.create(
        name="Dispute Org", slug="dispute-org", email="dispute@example.com"
    )
    batch = Batch.objects.create(
        organization=org, created_by="tester", city="Istanbul", sector="IT"
    )
    dispute = Dispute.objects.create(
        organization=org,
        batch=batch,
        reason="Email bounced",
        evidence_data={"email_bounce": True},
    )

    auto_resolve_dispute.apply(args=[str(dispute.id)])

    dispute.refresh_from_db()
    assert dispute.status == "resolved"
    assert dispute.decision == "accept"
    assert dispute.decision_reason_code == "EMAIL_BOUNCE"


@pytest.mark.django_db
def test_auto_resolve_dispute_reject():
    """Dispute with no_response evidence should be resolved as reject."""
    org = Organization.objects.create(
        name="Dispute Org 2", slug="dispute-org-2", email="dispute2@example.com"
    )
    batch = Batch.objects.create(
        organization=org, created_by="tester", city="Ankara", sector="Hukuk"
    )
    dispute = Dispute.objects.create(
        organization=org,
        batch=batch,
        reason="No response from customer",
        evidence_data={"no_response": True},
    )

    auto_resolve_dispute.apply(args=[str(dispute.id)])

    dispute.refresh_from_db()
    assert dispute.status == "resolved"
    assert dispute.decision == "reject"


@pytest.mark.django_db
def test_auto_resolve_dispute_not_found_returns_none():
    """Non-existent dispute_id should return None without raising."""
    result = auto_resolve_dispute.apply(args=["00000000-0000-0000-0000-000000000000"])
    assert result.result is None


@pytest.mark.django_db
@patch("apps.disputes.tasks.emit_alarm")
def test_auto_resolve_dispute_emits_alarm_on_final_failure(mock_emit):
    """On permanent failure (max retries exhausted) emit_alarm is called.

    We test this by calling auto_resolve_dispute with a non-existent dispute_id
    that deliberately causes an exception, and patch max_retries via the task
    instance so retries_left == 0 on the first attempt.
    """
    org = Organization.objects.create(
        name="Dispute Alarm Org", slug="dispute-alarm-org", email="alarm@example.com"
    )
    batch = Batch.objects.create(
        organization=org, created_by="tester", city="Izmir", sector="Finans"
    )
    dispute = Dispute.objects.create(
        organization=org,
        batch=batch,
        reason="Test alarm",
        evidence_data={"email_bounce": True},
    )

    # Force max_retries=0 so there are no retries left on first call.
    # CELERY_TASK_ALWAYS_EAGER + CELERY_TASK_EAGER_PROPAGATES means apply()
    # will execute the task synchronously without actual retry scheduling.
    original_max_retries = auto_resolve_dispute.max_retries
    try:
        auto_resolve_dispute.max_retries = 0
        with patch("apps.disputes.tasks.DecisionEngine.evaluate", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                auto_resolve_dispute.apply(args=[str(dispute.id)], throw=True)
    finally:
        auto_resolve_dispute.max_retries = original_max_retries

    mock_emit.assert_called_once()
    call_kwargs = mock_emit.call_args[1]
    assert call_kwargs["code"] == "DISPUTE_RESOLUTION_FAILED"

    mock_emit.assert_called_once()
    call_kwargs = mock_emit.call_args[1]
    assert call_kwargs["code"] == "DISPUTE_RESOLUTION_FAILED"
