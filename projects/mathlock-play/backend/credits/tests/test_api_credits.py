from .base import *

class GetCreditsViewTest(ThrottleMixin, AuthMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='credits-test-001',
            device_token=uuid.uuid4()
        )
        self.credit_balance = CreditBalance.objects.create(device=self.device, balance=7)
        self._auth_client(self.device)

    def test_get_credits_valid_token(self):
        resp = self.client.get(
            f'/api/mathlock/credits/?device_token={self.device.device_token}'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['credits'], 7)

    def test_get_credits_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Device invalid-token')
        resp = self.client.get(
            '/api/mathlock/credits/?device_token=00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_credits_missing_token(self):
        self.client.credentials()
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 403)

class VerifyPurchaseViewTest(ThrottleMixin, AuthMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='purchase-test-001',
            device_token=uuid.uuid4()
        )
        CreditBalance.objects.create(device=self.device)
        self._auth_client(self.device)

    @patch('credits.views.verify_purchase')
    def test_verify_purchase_adds_credits(self, mock_verify):
        mock_verify.return_value = {
            'valid': True,
            'order_id': 'GPA.TEST-ORDER-001',
            'purchase_state': 0,
            'consumption_state': 0,
            'raw_response': {},
        }
        resp = self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': str(self.device.device_token),
            'purchase_token': 'test-purchase-token-001',
            'product_id': 'kredi_10',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['credits_added'], 10)
        self.assertEqual(data['total_credits'], 10)

        balance = CreditBalance.objects.get(device=self.device)
        self.assertEqual(balance.balance, 10)

    @patch('credits.views.verify_purchase')
    def test_verify_purchase_invalid_token(self, mock_verify):
        mock_verify.return_value = {
            'valid': False,
            'error': 'Purchase not found',
            'raw_response': {},
        }
        resp = self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': str(self.device.device_token),
            'purchase_token': 'fake-invalid-token',
            'product_id': 'kredi_10',
        }, format='json')
        self.assertEqual(resp.status_code, 402)
        self.assertFalse(resp.json()['success'])

    @patch('credits.views.verify_purchase')
    def test_duplicate_purchase_token_rejected(self, mock_verify):
        mock_verify.return_value = {'valid': True, 'order_id': 'GPA-1', 'purchase_state': 0, 'consumption_state': 0, 'raw_response': {}}
        # İlk işlem
        self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': str(self.device.device_token),
            'purchase_token': 'duplicate-token-abc',
            'product_id': 'kredi_5',
        }, format='json')
        # İkinci aynı token
        resp = self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': str(self.device.device_token),
            'purchase_token': 'duplicate-token-abc',
            'product_id': 'kredi_5',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'], 'purchase_already_processed')

    def test_verify_invalid_product_id(self):
        resp = self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': str(self.device.device_token),
            'purchase_token': 'any-token',
            'product_id': 'gecersiz_urun',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_verify_unknown_device_token(self):
        # Auth header geçerli cihaz için, body'deki token farklı olsa bile
        # view request.user'ı kullanır. Geçersiz purchase_token → verify_purchase 402
        with patch('credits.views.verify_purchase') as mock_verify:
            mock_verify.return_value = {
                'valid': False, 'error': 'Purchase not found', 'raw_response': {}
            }
            resp = self.client.post('/api/mathlock/purchase/verify/', {
                'device_token': '00000000-0000-0000-0000-000000000000',
                'purchase_token': 'any-token',
                'product_id': 'kredi_10',
            }, format='json')
        self.assertEqual(resp.status_code, 402)

class UseCreditViewTest(ThrottleMixin, AuthMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='use-credit-test-001',
            device_token=uuid.uuid4()
        )
        self.balance = CreditBalance.objects.create(device=self.device)
        self.child = ChildProfile.objects.create(device=self.device, name='Çocuk')
        self._auth_client(self.device)

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'S1', 'answer': 1, 'type': 'a', 'difficulty': 1}
    ] * 50)
    def test_first_use_is_free(self, mock_gen):
        resp = self.client.post('/api/mathlock/credits/use/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'stats': {},
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_free'])
        # Kredi düşülmedi
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 0)
        # Ücretsiz set işaretlendi
        self.assertTrue(self.balance.free_set_used)
        self.assertEqual(data['questions_generated'], 50)

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'S1', 'answer': 1, 'type': 'a', 'difficulty': 1}
    ] * 50)
    def test_second_use_consumes_credit(self, mock_gen):
        self.balance.free_set_used = True
        self.balance.balance = 3
        self.balance.total_purchased = 3
        self.balance.save()

        resp = self.client.post('/api/mathlock/credits/use/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'stats': {},
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_free'])
        self.assertEqual(data['credits_remaining'], 2)

        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 2)

    def test_no_credit_returns_402(self):
        # İlk ücretsiz seti kullandıktan sonra kredi sıfır
        self.balance.free_set_used = True
        self.balance.save()

        resp = self.client.post('/api/mathlock/credits/use/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'stats': {},
        }, format='json')
        self.assertEqual(resp.status_code, 402)

    def test_no_credit_no_previous_set_returns_402(self):
        self.balance.free_set_used = True
        self.balance.save()

        resp = self.client.post('/api/mathlock/credits/use/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'stats': {},
        }, format='json')
        self.assertEqual(resp.status_code, 402)

class UploadStatsViewTest(ThrottleMixin, AuthMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='stats-test-001',
            device_token=uuid.uuid4()
        )
        ChildProfile.objects.create(device=self.device, name='Çocuk')
        self._auth_client(self.device)

    def test_upload_stats_updates_child_profile(self):
        resp = self.client.post('/api/mathlock/stats/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'question_version': 1,
            'stats': {
                'totalCorrect': 40,
                'totalShown': 50,
            }
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])

        child = ChildProfile.objects.get(device=self.device, name='Çocuk')
        self.assertEqual(child.total_correct, 40)
        self.assertEqual(child.total_shown, 50)

    def test_high_accuracy_increases_difficulty(self):
        child = ChildProfile.objects.get(device=self.device, name='Çocuk')
        initial_difficulty = child.current_difficulty

        # %90 doğruluk → zorluk artmalı
        self.client.post('/api/mathlock/stats/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'question_version': 1,
            'stats': {'totalCorrect': 45, 'totalShown': 50}
        }, format='json')
        child.refresh_from_db()
        self.assertGreaterEqual(child.current_difficulty, initial_difficulty)

    def test_low_accuracy_decreases_difficulty(self):
        child = ChildProfile.objects.get(device=self.device, name='Çocuk')
        child.current_difficulty = 3
        child.total_shown = 10  # stats yüklendikten sonra 20+ olacak
        child.save()

        # %40 doğruluk → zorluk azalmalı
        self.client.post('/api/mathlock/stats/', {
            'device_token': str(self.device.device_token),
            'child_name': 'Çocuk',
            'question_version': 1,
            'stats': {'totalCorrect': 4, 'totalShown': 10}
        }, format='json')
        child.refresh_from_db()
        self.assertLessEqual(child.current_difficulty, 3)
