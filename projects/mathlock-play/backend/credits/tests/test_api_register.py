from .base import *

class RegisterDeviceViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register_new_device(self):
        resp = self.client.post('/api/mathlock/register/', {
            'installation_id': 'install-abc-123'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('device_token', data)
        self.assertEqual(data['credits'], 0)
        self.assertFalse(data['free_set_used'])

    def test_register_same_device_returns_same_token(self):
        resp1 = self.client.post('/api/mathlock/register/', {
            'installation_id': 'install-dup-001'
        }, format='json')
        resp2 = self.client.post('/api/mathlock/register/', {
            'installation_id': 'install-dup-001'
        }, format='json')
        self.assertEqual(resp1.json()['device_token'], resp2.json()['device_token'])

    def test_register_creates_credit_balance(self):
        self.client.post('/api/mathlock/register/', {
            'installation_id': 'install-balance-001'
        }, format='json')
        device = Device.objects.get(installation_id='install-balance-001')
        self.assertTrue(CreditBalance.objects.filter(device=device).exists())

    def test_register_creates_child_profile(self):
        self.client.post('/api/mathlock/register/', {
            'installation_id': 'install-child-001'
        }, format='json')
        device = Device.objects.get(installation_id='install-child-001')
        self.assertTrue(ChildProfile.objects.filter(device=device).exists())

    def test_register_missing_installation_id(self):
        resp = self.client.post('/api/mathlock/register/', {}, format='json')
        self.assertEqual(resp.status_code, 400)

class RegisterDeviceLocaleTest(ThrottleMixin, TestCase):
    """POST /register/ endpoint'inde locale parametre davranışı."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_register_with_locale_en(self):
        resp = self.client.post('/api/mathlock/register/', {
            'installation_id': 'locale-en-001',
            'locale': 'en',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        device = Device.objects.get(installation_id='locale-en-001')
        child = ChildProfile.objects.get(device=device)
        self.assertEqual(child.locale, 'en')

    def test_register_default_locale_tr(self):
        resp = self.client.post('/api/mathlock/register/', {
            'installation_id': 'locale-default-001',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        device = Device.objects.get(installation_id='locale-default-001')
        child = ChildProfile.objects.get(device=device)
        self.assertEqual(child.locale, 'tr')

    def test_register_invalid_locale_coerced(self):
        resp = self.client.post('/api/mathlock/register/', {
            'installation_id': 'locale-invalid-001',
            'locale': 'xx',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        device = Device.objects.get(installation_id='locale-invalid-001')
        child = ChildProfile.objects.get(device=device)
        self.assertEqual(child.locale, 'tr')

class RegisterEmailViewTest(ThrottleMixin, AuthMixin, TestCase):
    """POST /api/mathlock/auth/register-email/"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='reg-email-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self._auth_client(self.device)
        self.url = '/api/mathlock/auth/register-email/'

    def test_success(self):
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'email': 'ali@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['email'], 'ali@example.com')
        self.assertFalse(data['recovered'])
        self.assertEqual(data['credits'], 0)
        self.device.refresh_from_db()
        self.assertEqual(self.device.email, 'ali@example.com')

    def test_invalid_email_format(self):
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'email': 'not-an-email',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_missing_token(self):
        self.client.credentials()
        resp = self.client.post(self.url, {'email': 'ali@example.com'}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Device invalid-token')
        resp = self.client.post(self.url, {
            'device_token': str(uuid.uuid4()),
            'email': 'ali@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_duplicate_email_same_device(self):
        self.device.email = 'ali@example.com'
        self.device.save()
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'email': 'ali@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['recovered'])

    def test_account_recovery(self):
        """Eski cihazdan yeni cihaza veri transferi."""
        old_device = Device.objects.create(
            installation_id='old-device',
            device_token=uuid.uuid4(),
            email='recover@example.com'
        )
        old_child = ChildProfile.objects.create(
            device=old_device, name='Veli', education_period='sinif_1'
        )
        old_credits = CreditBalance.objects.create(device=old_device, balance=5)

        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'email': 'recover@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['recovered'])
        self.assertEqual(data['credits'], 5)

        old_device.refresh_from_db()
        self.assertIsNone(old_device.email)
        # Eski cihaz silinmez, sadece email temizlenir
        self.assertTrue(Device.objects.filter(pk=old_device.pk).exists())
        self.assertTrue(
            ChildProfile.objects.filter(device=self.device, name='Veli').exists()
        )

    def test_recovery_name_collision(self):
        """Eski ve yeni cihazda aynı isimde çocuk varsa istatistikleri birleştir."""
        old_device = Device.objects.create(
            installation_id='old-device-2',
            device_token=uuid.uuid4(),
            email='collision@example.com'
        )
        old_child = ChildProfile.objects.create(
            device=old_device, name='Ali', education_period='sinif_1',
            total_correct=10, total_shown=20
        )
        self.child.total_correct = 5
        self.child.total_shown = 10
        self.child.save()

        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'email': 'collision@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['recovered'])
        self.child.refresh_from_db()
        self.assertEqual(self.child.total_correct, 15)
        self.assertEqual(self.child.total_shown, 30)

    def test_recovery_credit_transfer(self):
        """Eski cihazda kredi varsa yeni cihaza birleştir."""
        old_device = Device.objects.create(
            installation_id='old-device-3',
            device_token=uuid.uuid4(),
            email='credit@example.com'
        )
        CreditBalance.objects.create(device=old_device, balance=7, total_purchased=7)
        CreditBalance.objects.create(device=self.device, balance=3, total_used=1)

        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'email': 'credit@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['credits'], 10)
        cb = CreditBalance.objects.get(device=self.device)
        self.assertEqual(cb.total_purchased, 7)  # sadece eski cihazdan gelen
        self.assertEqual(cb.total_used, 1)

class HealthViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        resp = self.client.get('/api/mathlock/health/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'ok')

class GetPackagesViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_packages_from_settings_fallback(self):
        """DB'de paket yokken settings.py'den okuma yapmalı."""
        resp = self.client.get('/api/mathlock/packages/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('packages', data)
        self.assertEqual(data['source'], 'settings')
        # settings.py'de 4 ürün var
        self.assertEqual(len(data['packages']), 4)
        pids = [p['product_id'] for p in data['packages']]
        self.assertIn('kredi_1', pids)
        self.assertIn('kredi_5', pids)
        self.assertIn('kredi_10', pids)

    def test_packages_from_db(self):
        """DB'de paket varsa DB'den okuma yapmalı."""
        from credits.models import CreditPackage
        CreditPackage.objects.create(
            product_id='kredi_3',
            display_name='Test Paketi',
            credits=3,
            questions_count=150,
            sort_order=1,
        )
        resp = self.client.get('/api/mathlock/packages/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['source'], 'db')
        pids = [p['product_id'] for p in data['packages']]
        self.assertIn('kredi_3', pids)

    def test_inactive_packages_not_returned(self):
        """is_active=False olan paketler dönmemeli."""
        from credits.models import CreditPackage
        CreditPackage.objects.create(
            product_id='kredi_gizli',
            display_name='Gizli Paket',
            credits=99,
            questions_count=4950,
            is_active=False,
        )
        resp = self.client.get('/api/mathlock/packages/')
        data = resp.json()
        pids = [p['product_id'] for p in data['packages']]
        self.assertNotIn('kredi_gizli', pids)

    def test_packages_contain_questions_count(self):
        """Her paketin questions_count alanı olmalı."""
        resp = self.client.get('/api/mathlock/packages/')
        for pkg in resp.json()['packages']:
            self.assertIn('questions_count', pkg)
            self.assertGreater(pkg['questions_count'], 0)
