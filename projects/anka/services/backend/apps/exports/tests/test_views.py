from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organization, OrganizationMember
from apps.batches.models import Batch


def test_export_create_view(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="exporter", password="pass123")
    org = Organization.objects.create(name="Export Org", slug="export-org", email="export@example.com")
    OrganizationMember.objects.create(organization=org, user=user, role="owner", is_active=True)

    batch = Batch.objects.create(
        organization=org,
        created_by="exporter",
        city="Istanbul",
        sector="IT",
        filters={"size": "large"},
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/exports/",
        {"batch": str(batch.id), "format": "csv"},
        format="json",
    )

    assert response.status_code == 201
