from .base import *

class DeviceTokenSignerTest(TestCase):
    """DeviceTokenSigner unit testleri."""

    def test_sign_returns_different_value(self):
        signer = DeviceTokenSigner()
        raw = str(uuid.uuid4())
        signed = signer.sign(raw)
        self.assertNotEqual(raw, signed)
        self.assertIn(raw, signed)

    def test_unsign_returns_original(self):
        signer = DeviceTokenSigner()
        raw = str(uuid.uuid4())
        signed = signer.sign(raw)
        self.assertEqual(signer.unsign(signed), raw)

    def test_unsign_bad_signature(self):
        signer = DeviceTokenSigner()
        with self.assertRaises(BadSignature):
            signer.unsign('tampered-token')

    def test_unsign_expired(self):
        signer = DeviceTokenSigner()
        raw = str(uuid.uuid4())
        signed = signer.sign(raw)
        with self.assertRaises(SignatureExpired):
            signer.unsign(signed, max_age=0)  # hemen expire

class DeviceTokenAuthenticationTest(ThrottleMixin, TestCase):
    """DRF DeviceTokenAuthentication davranış testleri."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='auth-test-001',
            device_token=uuid.uuid4(),
        )
        CreditBalance.objects.create(device=self.device)
        self.signer = DeviceTokenSigner()

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Device {token}')

    def test_valid_signed_token_returns_200(self):
        signed = self.signer.sign(str(self.device.device_token))
        self._auth(signed)
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 200)

    def test_missing_authorization_header_returns_403(self):
        self.client.credentials()
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 403)

    def test_wrong_keyword_returns_403(self):
        signed = self.signer.sign(str(self.device.device_token))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {signed}')
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 403)

    def test_tampered_token_returns_403(self):
        self.client.credentials(HTTP_AUTHORIZATION='Device tampered-token')
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 403)

    def test_expired_token_returns_403(self):
        signed = self.signer.sign(str(self.device.device_token))
        # Django TimestampSigner.unsign'i patch'le — tüm DeviceTokenSigner instance'ları etkilenir
        with patch('credits.authentication.TimestampSigner.unsign', side_effect=SignatureExpired('expired')):
            auth = DeviceTokenAuthentication()
            request = MagicMock()
            request.headers = {'Authorization': f'Device {signed}'}
            with self.assertRaises(AuthenticationFailed) as ctx:
                auth.authenticate(request)
            self.assertIn('expired', str(ctx.exception).lower())

    def test_valid_token_but_deleted_device_returns_403(self):
        deleted_device = Device.objects.create(
            installation_id='deleted-device',
            device_token=uuid.uuid4(),
        )
        signed = self.signer.sign(str(deleted_device.device_token))
        deleted_device.delete()
        self.client.credentials(HTTP_AUTHORIZATION=f'Device {signed}')
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 403)

    def test_allowany_endpoints_bypass_auth(self):
        """register ve health endpoint'leri auth gerektirmez."""
        resp = self.client.post('/api/mathlock/register/', {
            'installation_id': 'no-auth-register-001'
        }, format='json')
        self.assertEqual(resp.status_code, 200)

        resp2 = self.client.get('/api/mathlock/health/')
        self.assertEqual(resp.status_code, 200)

    def test_query_param_token_fallback(self):
        """Eski app versiyonları: ?device_token=<signed> kabul edilir."""
        signed = self.signer.sign(str(self.device.device_token))
        self.client.credentials()  # header temizle
        resp = self.client.get(f'/api/mathlock/credits/?device_token={signed}')
        self.assertEqual(resp.status_code, 200)

    def test_json_body_token_fallback(self):
        """Eski app versiyonları: POST body'de device_token kabul edilir."""
        signed = self.signer.sign(str(self.device.device_token))
        self.client.credentials()  # header temizle
        resp = self.client.post('/api/mathlock/levels/progress/', {
            'device_token': signed,
            'completed_level_ids': [],
        }, format='json')
        # 404 = auth başarılı ama child bulunamadı (test setup'ında child yok)
        self.assertEqual(resp.status_code, 404)

    def test_no_token_returns_403(self):
        """Header, query param ve body'de token yoksa 403."""
        self.client.credentials()
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 403)
