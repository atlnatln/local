from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.accounts.models import Organization
from apps.batches.models import Batch, BatchItem
from apps.batches.services import BatchProcessor
from apps.ledger.models import CreditPackage, LedgerEntry


@pytest.mark.django_db
def test_partial_batch_no_candidates_refunds_full_estimate_idempotent():
    org = Organization.objects.create(
        name="Org Refund 1",
        slug="org-refund-1",
        email="org-refund-1@example.com",
    )

    credit_package = CreditPackage.objects.create(
        organization=org,
        balance=Decimal("8.00"),
        total_spent=Decimal("2.00"),
    )

    batch = Batch.objects.create(
        organization=org,
        created_by="tester",
        city="ankara",
        sector="plancı",
        filters={},
        record_count_estimate=2,
        estimated_cost=Decimal("2.00"),
    )

    LedgerEntry.objects.create(
        organization=org,
        transaction_type="spent",
        amount=Decimal("2.00"),
        status="completed",
        reference_type="batch",
        reference_id=str(batch.id),
        description="Batch create spend",
        balance_before=Decimal("10.00"),
        balance_after=Decimal("8.00"),
        metadata={"batch_id": str(batch.id)},
    )

    with patch.object(BatchProcessor, "_stage_collect_ids", return_value=[]):
        BatchProcessor(batch.id).run_pipeline()

    batch.refresh_from_db()
    credit_package.refresh_from_db()

    assert batch.status == "PARTIAL"
    assert batch.contacts_enriched == 0
    assert credit_package.balance == Decimal("10.00")
    assert credit_package.total_refunded == Decimal("2.00")

    refund_entries = LedgerEntry.objects.filter(
        reference_type="dispute",
        reference_id=f"batch-refund:{batch.id}",
        transaction_type="refund",
    )
    assert refund_entries.count() == 1
    assert refund_entries.first().amount == Decimal("2.00")

    # Retry safety: second run must not create duplicate refund
    with patch.object(BatchProcessor, "_stage_collect_ids", return_value=[]):
        BatchProcessor(batch.id).run_pipeline()

    credit_package.refresh_from_db()
    assert credit_package.balance == Decimal("10.00")
    assert LedgerEntry.objects.filter(
        reference_type="dispute",
        reference_id=f"batch-refund:{batch.id}",
    ).count() == 1


@pytest.mark.django_db
def test_ready_batch_refunds_estimate_minus_delivered_count():
    org = Organization.objects.create(
        name="Org Refund 2",
        slug="org-refund-2",
        email="org-refund-2@example.com",
    )

    credit_package = CreditPackage.objects.create(
        organization=org,
        balance=Decimal("7.00"),
        total_spent=Decimal("3.00"),
    )

    batch = Batch.objects.create(
        organization=org,
        created_by="tester",
        city="ankara",
        sector="şehir plancısı",
        filters={},
        record_count_estimate=3,
        estimated_cost=Decimal("3.00"),
    )

    LedgerEntry.objects.create(
        organization=org,
        transaction_type="spent",
        amount=Decimal("3.00"),
        status="completed",
        reference_type="batch",
        reference_id=str(batch.id),
        description="Batch create spend",
        balance_before=Decimal("10.00"),
        balance_after=Decimal("7.00"),
        metadata={"batch_id": str(batch.id)},
    )

    verified_items = [
        BatchItem.objects.create(
            batch=batch,
            firm_id="p1",
            firm_name="Firm 1",
            is_verified=True,
            data={"stage_2_pro": True},
        ),
        BatchItem.objects.create(
            batch=batch,
            firm_id="p2",
            firm_name="Firm 2",
            is_verified=True,
            data={"stage_2_pro": True},
        ),
    ]

    def enrich_side_effect(items):
        items[0].data["stage_3_enterprise"] = True
        items[0].save()
        return items

    with patch.object(BatchProcessor, "_stage_collect_ids", return_value=[{"id": "p1"}, {"id": "p2"}]), \
         patch.object(BatchProcessor, "_stage_filter_details_pro", return_value=verified_items), \
         patch.object(BatchProcessor, "_stage_enrich_enterprise", side_effect=enrich_side_effect):
        BatchProcessor(batch.id).run_pipeline()

    batch.refresh_from_db()
    credit_package.refresh_from_db()

    assert batch.status == "READY"
    assert batch.contacts_enriched == 1
    assert credit_package.balance == Decimal("9.00")
    assert credit_package.total_refunded == Decimal("2.00")

    refund_entry = LedgerEntry.objects.get(
        reference_type="dispute",
        reference_id=f"batch-refund:{batch.id}",
        transaction_type="refund",
    )
    assert refund_entry.amount == Decimal("2.00")
