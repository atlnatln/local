"""
Production-specific settings for Anka Backend.
"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database
DATABASES['default']['PASSWORD'] = os.environ.get('DB_PASSWORD')

# Email (production)
EMAIL_BACKEND = 'anymail.backends.postmark.EmailBackend'
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': os.environ.get('POSTMARK_SERVER_TOKEN'),
}
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@anka.co')

# Logging for production
LOGGING['root']['level'] = 'INFO'
LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'sentry_sdk.integrations.django.DjangoIntegration',
}

# Sentry
import sentry_sdk
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[sentry_sdk.integrations.django.DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)

# CORS (restricted)
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# REST Framework (production)
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# Cache and Session configuration for production
CACHES['default']['LOCATION'] = os.environ.get('REDIS_URL')
SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', '')
