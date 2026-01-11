"""
Apps configuration and conftest for test fixtures.
"""

import os
import django
from django.conf import settings

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.test')
django.setup()

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """Fixture for REST API client."""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, django_user_model):
    """Fixture for authenticated API client."""
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def test_user(django_user_model):
    """Fixture for creating a test user."""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def test_admin_user(django_user_model):
    """Fixture for creating a test admin user."""
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass
