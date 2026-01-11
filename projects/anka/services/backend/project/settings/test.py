"""
Test-specific settings for Anka Backend.
"""

from .base import *

DEBUG = True

# Use SQLite for tests (faster)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password validation for tests
AUTH_PASSWORD_VALIDATORS = []

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
