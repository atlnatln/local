from decimal import Decimal

import pytest

from apps.accounts.models import Organization
from apps.ledger.models import CreditPackage, LedgerEntry


@pytest.mark.django_db
def test_credit_package_str():
    org = Organization.objects.create(
        name="Ledger Org",
        slug="ledger-org",
        email="ledger@example.com",
    )
    package = CreditPackage.objects.create(organization=org, balance=Decimal("100.00"))

    assert str(package) == f"Credits: {org.name} (${package.balance})"


@pytest.mark.django_db
def test_ledger_entry_str():
    org = Organization.objects.create(
        name="Ledger Org 2",
        slug="ledger-org-2",
        email="ledger2@example.com",
    )
    entry = LedgerEntry.objects.create(
        organization=org,
        transaction_type="purchase",
        amount=Decimal("50.00"),
        reference_type="payment",
        reference_id="pay_123",
    )

    assert str(entry) == f"{entry.transaction_type.upper()} - {org.name} ({entry.amount})"
