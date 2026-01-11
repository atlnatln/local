"""
Development-specific settings for Anka Backend.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Security settings for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Database
DATABASES['default']['PASSWORD'] = os.environ.get('DB_PASSWORD', 'postgres')

# Email (console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging for development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
}

# Disable CORS restrictions for development
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework settings for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.BrowsableAPIRenderer',
    'rest_framework.renderers.JSONRenderer',
]
