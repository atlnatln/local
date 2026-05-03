"""DRF authentication backed by Django signing for device tokens."""

import json

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Device


class DeviceTokenSigner:
    """Signs and verifies UUID device tokens using Django's TimestampSigner."""

    def __init__(self):
        self._signer = TimestampSigner()

    def sign(self, device_token: str) -> str:
        return self._signer.sign(device_token)

    def unsign(self, signed_token: str, max_age: int = None) -> str:
        """Verify signature and return the raw device_token UUID string.

        Args:
            signed_token: The signed token from the Authorization header.
            max_age: Max age in seconds. None = no expiry check.
        """
        return self._signer.unsign(signed_token, max_age=max_age)


class DeviceTokenAuthentication(BaseAuthentication):
    """Authenticate requests via Authorization: Device <signed_token> header.

    Fallbacks (for older app versions):
      - Query param: ?device_token=<signed_token>
      - JSON body:   { "device_token": "<signed_token>" }
    """

    keyword = 'Device'

    def authenticate(self, request):
        signed_token = None

        # 1. Authorization header (preferred)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith(self.keyword + ' '):
            signed_token = auth_header[len(self.keyword) + 1 :].strip()

        # 2. Query param fallback
        if not signed_token:
            signed_token = request.query_params.get('device_token', '').strip()

        # 3. JSON body fallback (Content-Type check skipped for older clients)
        if not signed_token:
            try:
                body = json.loads(request.body)
                signed_token = body.get('device_token', '').strip()
            except Exception:
                pass

        if not signed_token:
            return None

        signer = DeviceTokenSigner()
        try:
            device_token = signer.unsign(signed_token)
        except SignatureExpired:
            raise AuthenticationFailed('Token expired.')
        except BadSignature:
            raise AuthenticationFailed('Invalid token.')

        try:
            device = Device.objects.get(device_token=device_token)
        except Device.DoesNotExist:
            raise AuthenticationFailed('Device not found.')

        # DRF expects (user, auth) tuple. We use Device as the user proxy.
        return (device, signed_token)
