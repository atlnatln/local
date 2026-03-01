"""
Production-specific settings for Anka Backend.
"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF (production)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'anka_prod'),
        'USER': os.environ.get('DB_USER', 'anka_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Email (production)
EMAIL_BACKEND = 'anymail.backends.postmark.EmailBackend'
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': os.environ.get('POSTMARK_SERVER_TOKEN'),
}
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@anka.co')

# Logging for production
LOGGING['root']['level'] = 'INFO'

# Sentry (optional) — only init when DSN is a real HTTPS URL
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    SENTRY_DSN = os.environ.get('SENTRY_DSN', '').strip()
    if SENTRY_DSN and SENTRY_DSN.startswith('https://'):
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False
        )
except Exception:  # noqa: BLE001
    pass

# CORS (restricted)
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# REST Framework (production)
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# Cache and Session configuration for production
CACHES['default']['LOCATION'] = os.environ.get('REDIS_URL')
SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', '')
