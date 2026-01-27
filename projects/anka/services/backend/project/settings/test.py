"""
Test-specific settings for Anka Backend.
"""

import os
from .base import *

DEBUG = True

# Allow test-only login helper endpoint (Playwright/e2e)
ANKA_ALLOW_TEST_LOGIN = True

# Dummy Google client id for unit tests (verification is mocked)
GOOGLE_OIDC_CLIENT_ID = os.environ.get('GOOGLE_OIDC_CLIENT_ID', 'test-google-client-id')

# Database configuration - support both SQLite (default) and PostgreSQL (via DATABASE_URL)
DB_URL = os.environ.get('DATABASE_URL')
if DB_URL:
    # PostgreSQL (for CI/advanced testing)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DB_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # SQLite (for local testing)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
# Use in-memory cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Celery configuration for tests (synchronous)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable CORS for tests
CORS_ALLOWED_ORIGINS = []

# Logging for tests
LOGGING['root']['level'] = 'WARNING'
