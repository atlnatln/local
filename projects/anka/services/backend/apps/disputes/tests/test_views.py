from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organization, OrganizationMember
from apps.batches.models import Batch


def test_dispute_create_view(db, settings):
    settings.SECURE_SSL_REDIRECT = False

    user_model = get_user_model()
    user = user_model.objects.create_user(username="disputer", password="pass123")
    org = Organization.objects.create(name="Dispute Org", slug="dispute-org", email="dispute@example.com")
    OrganizationMember.objects.create(organization=org, user=user, role="owner", is_active=True)

    batch = Batch.objects.create(
        organization=org,
        created_by="disputer",
        city="Istanbul",
        sector="IT",
        filters={"size": "large"},
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/disputes/",
        {
            "organization": str(org.id),
            "batch": str(batch.id),
            "reason": "Data inaccurate",
            "evidence_data": {"email_bounce": True},
            "items": [
                {
                    "field_name": "email",
                    "reported_value": "correct@example.com",
                    "current_value": "wrong@example.com",
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 201
