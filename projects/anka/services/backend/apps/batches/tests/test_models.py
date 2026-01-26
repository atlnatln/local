import pytest

from apps.accounts.models import Organization
from apps.batches.models import Batch


@pytest.mark.django_db
def test_batch_query_hash_deterministic():
    org = Organization.objects.create(
        name="Test Org",
        slug="test-org",
        email="org@example.com",
    )

    batch = Batch.objects.create(
        organization=org,
        created_by="tester",
        city="Istanbul",
        sector="IT",
        filters={"size": "large", "employees": 100},
        sort_rule_version=1,
    )

    first_hash = batch.query_hash
    second_hash = batch.calculate_query_hash()

    assert first_hash == second_hash
