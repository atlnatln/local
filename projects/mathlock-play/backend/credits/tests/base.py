"""
Backend kredi sistemi testleri — ortak base modül.

Çalıştırmak:
    cd /home/akn/vps/projects/mathlock-play/backend
    pip install -r requirements.txt
    python manage.py test credits
"""
import json
import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from credits.models import (
    Device, ChildProfile, CreditBalance, LevelSet, PurchaseRecord,
    QuestionSet, RenewalLock, Question, UserQuestionProgress,
)
from credits.google_play import verify_purchase
from credits.views import _deduct_credit_and_lock, _release_renewal_lock
from credits.authentication import DeviceTokenSigner, DeviceTokenAuthentication
from django.core.signing import BadSignature, SignatureExpired
from rest_framework.exceptions import AuthenticationFailed

# Test ortamında throttle'ı devre dışı bırak
NO_THROTTLE = {
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
}


class ThrottleMixin:
    """Her test öncesi DRF throttle cache'ini temizler."""
    def setUp(self):
        super().setUp()
        from django.core.cache import cache
        cache.clear()
        from rest_framework.throttling import SimpleRateThrottle
        # Scope-based throttle sınıflarının iç cache'lerini sıfırla
        if hasattr(SimpleRateThrottle, 'cache'):
            SimpleRateThrottle.cache.clear()


class AuthMixin:
    """DRF APIClient'a DeviceTokenAuthentication header'ı set eder."""
    def _auth_client(self, device):
        signer = DeviceTokenSigner()
        signed = signer.sign(str(device.device_token))
        self.client.credentials(HTTP_AUTHORIZATION=f'Device {signed}')


class _FakeAsyncResult:
    """Celery AsyncResult mock'u — backend bağlantısı olmadan."""
    def __init__(self, job_id):
        self.id = job_id
        self.state = 'PENDING'
        self.result = None


__all__ = [
    'NO_THROTTLE', 'ThrottleMixin', 'AuthMixin', '_FakeAsyncResult',
    '_deduct_credit_and_lock', '_release_renewal_lock',
    'DeviceTokenSigner', 'DeviceTokenAuthentication',
    'BadSignature', 'SignatureExpired', 'AuthenticationFailed',
    'json', 'uuid', 'timedelta', 'patch', 'MagicMock',
    'TestCase', 'override_settings', 'timezone', 'APIClient',
    'Device', 'ChildProfile', 'CreditBalance', 'LevelSet',
    'PurchaseRecord', 'QuestionSet', 'RenewalLock', 'Question', 'UserQuestionProgress',
    'verify_purchase',
]
