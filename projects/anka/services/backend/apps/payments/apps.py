"""
Payment app configuration.
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """Configuration for payments app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'Payments'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.payments.signals  # noqa: F401
