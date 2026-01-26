from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organization, OrganizationMember
from apps.ledger.models import CreditPackage


@pytest.mark.django_db
def test_credit_purchase_view_creates_balance():
    user_model = get_user_model()
    user = user_model.objects.create_user(username="buyer", password="pass123")
    org = Organization.objects.create(name="Buyer Org", slug="buyer-org", email="buyer@example.com")
    OrganizationMember.objects.create(organization=org, user=user, role="owner", is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/credits/purchase/",
        {"organization": str(org.id), "amount": "25.00"},
        format="json",
    )

    assert response.status_code == 200
    package = CreditPackage.objects.get(organization=org)
    assert package.balance == Decimal("25.00")
