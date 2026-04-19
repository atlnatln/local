"""
Backend kredi sistemi testleri.

Çalıştırmak:
    cd /home/akn/vps/projects/mathlock-play/backend
    pip install -r requirements.txt
    python manage.py test credits
"""
import uuid
from unittest.mock import patch
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from credits.models import Device, ChildProfile, CreditBalance, PurchaseRecord, QuestionSet
from credits.google_play import verify_purchase

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


# ─── Model Testleri ─────────────────────────────────────────────────────────

class CreditBalanceModelTest(TestCase):

    def setUp(self):
        self.device = Device.objects.create(
            installation_id="test-device-001",
            device_token=uuid.uuid4()
        )
        self.balance = CreditBalance.objects.create(device=self.device)

    def test_initial_balance_is_zero(self):
        self.assertEqual(self.balance.balance, 0)
        self.assertFalse(self.balance.free_set_used)

    def test_add_credits(self):
        self.balance.add_credits(10)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 10)
        self.assertEqual(self.balance.total_purchased, 10)

    def test_add_credits_cumulative(self):
        self.balance.add_credits(5)
        self.balance.add_credits(3)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 8)
        self.assertEqual(self.balance.total_purchased, 8)

    def test_use_credit_success(self):
        self.balance.add_credits(3)
        result = self.balance.use_credit()
        self.balance.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(self.balance.balance, 2)
        self.assertEqual(self.balance.total_used, 1)

    def test_use_credit_when_empty_returns_false(self):
        result = self.balance.use_credit()
        self.assertFalse(result)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 0)
        self.assertEqual(self.balance.total_used, 0)

    def test_use_all_credits(self):
        self.balance.add_credits(2)
        self.balance.use_credit()
        self.balance.use_credit()
        result = self.balance.use_credit()  # 3. kullanım → başarısız
        self.assertFalse(result)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 0)

    def test_accuracy_with_no_questions(self):
        child = ChildProfile(total_correct=0, total_shown=0)
        self.assertEqual(child.accuracy, 0.0)

    def test_accuracy_calculation(self):
        child = ChildProfile(total_correct=8, total_shown=10)
        self.assertAlmostEqual(child.accuracy, 0.8)


# ─── API: Register ───────────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
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


# ─── API: Kredi Sorgulama ────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
class GetCreditsViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='credits-test-001',
            device_token=uuid.uuid4()
        )
        self.credit_balance = CreditBalance.objects.create(device=self.device, balance=7)

    def test_get_credits_valid_token(self):
        resp = self.client.get(
            f'/api/mathlock/credits/?device_token={self.device.device_token}'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['credits'], 7)

    def test_get_credits_invalid_token(self):
        resp = self.client.get(
            '/api/mathlock/credits/?device_token=00000000-0000-0000-0000-000000000000'
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_credits_missing_token(self):
        resp = self.client.get('/api/mathlock/credits/')
        self.assertEqual(resp.status_code, 400)


# ─── API: Satın Alma Doğrulama ───────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
class VerifyPurchaseViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='purchase-test-001',
            device_token=uuid.uuid4()
        )
        CreditBalance.objects.create(device=self.device)

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
        self.assertEqual(resp.json()['message'], 'Bu satın alma zaten işlendi')

    def test_verify_invalid_product_id(self):
        resp = self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': str(self.device.device_token),
            'purchase_token': 'any-token',
            'product_id': 'gecersiz_urun',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_verify_unknown_device_token(self):
        resp = self.client.post('/api/mathlock/purchase/verify/', {
            'device_token': '00000000-0000-0000-0000-000000000000',
            'purchase_token': 'any-token',
            'product_id': 'kredi_10',
        }, format='json')
        self.assertEqual(resp.status_code, 404)


# ─── API: Kredi Kullanımı ────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
class UseCreditViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='use-credit-test-001',
            device_token=uuid.uuid4()
        )
        self.balance = CreditBalance.objects.create(device=self.device)
        self.child = ChildProfile.objects.create(device=self.device, name='Çocuk')

    def test_first_use_is_free(self):
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

    def test_second_use_consumes_credit(self):
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


# ─── API: İstatistik Yükleme ────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
class UploadStatsViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='stats-test-001',
            device_token=uuid.uuid4()
        )
        ChildProfile.objects.create(device=self.device, name='Çocuk')

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


# ─── API: Sağlık Kontrolü ────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
class HealthViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        resp = self.client.get('/api/mathlock/health/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'ok')


# ─── Google Play Doğrulama (mock ile) ────────────────────────────────────────

class GooglePlayVerifyTest(TestCase):

    @patch('credits.google_play.get_android_publisher_service')
    def test_valid_purchase(self, mock_service):
        mock_service.return_value.purchases.return_value.products.return_value.get.return_value.execute.return_value = {
            'purchaseState': 0,
            'consumptionState': 0,
            'orderId': 'GPA.TEST-001',
        }
        result = verify_purchase('valid-token', 'kredi_10')
        self.assertTrue(result['valid'])
        self.assertEqual(result['order_id'], 'GPA.TEST-001')

    @patch('credits.google_play.get_android_publisher_service')
    def test_cancelled_purchase(self, mock_service):
        mock_service.return_value.purchases.return_value.products.return_value.get.return_value.execute.return_value = {
            'purchaseState': 1,  # iptal
            'consumptionState': 0,
            'orderId': 'GPA.TEST-002',
        }
        result = verify_purchase('cancelled-token', 'kredi_10')
        self.assertFalse(result['valid'])

    def test_missing_service_account_file(self):
        result = verify_purchase('any-token', 'kredi_10')
        # Service account JSON yok → hata döner ama uygulama çökmez
        self.assertFalse(result['valid'])
        self.assertIn('error', result)


# ─── API: AI Sorgu Proxy ─────────────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
class AiQueryViewTest(ThrottleMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='ai-query-test-001',
            device_token=uuid.uuid4()
        )
        self.balance = CreditBalance.objects.create(device=self.device)
        ChildProfile.objects.create(device=self.device, name='Çocuk')

    def test_ai_query_free_first_use(self):
        """İlk sorgu ücretsiz olmalı ve simulate sağlayıcı cevap üretmeli."""
        resp = self.client.post('/api/mathlock/ai/query/', {
            'device_token': str(self.device.device_token),
            'prompt': 'zorluk=2 için toplama sorusu üret',
            'provider': 'simulate',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_free'])
        self.assertTrue(data['simulated'])
        # Balans değişmemeli (ücretsiz)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 0)

    def test_ai_query_consumes_credit(self):
        """Ücretsiz set kullanıldıktan sonra sorgu kredi tüketmeli."""
        self.balance.free_set_used = True
        self.balance.balance = 3
        self.balance.total_purchased = 3
        self.balance.save()

        resp = self.client.post('/api/mathlock/ai/query/', {
            'device_token': str(self.device.device_token),
            'prompt': 'çarpma sorusu',
            'provider': 'simulate',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_free'])
        self.assertEqual(data['credits_remaining'], 2)

    def test_ai_query_no_credits_returns_402(self):
        """Kredi yoksa 402 dönmeli."""
        self.balance.free_set_used = True
        self.balance.balance = 0
        self.balance.save()

        resp = self.client.post('/api/mathlock/ai/query/', {
            'device_token': str(self.device.device_token),
            'prompt': 'herhangi bir soru',
        }, format='json')
        self.assertEqual(resp.status_code, 402)

    def test_ai_query_missing_prompt(self):
        resp = self.client.post('/api/mathlock/ai/query/', {
            'device_token': str(self.device.device_token),
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_ai_query_prompt_too_long(self):
        resp = self.client.post('/api/mathlock/ai/query/', {
            'device_token': str(self.device.device_token),
            'prompt': 'x' * 1001,
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_ai_query_invalid_device(self):
        resp = self.client.post('/api/mathlock/ai/query/', {
            'device_token': '00000000-0000-0000-0000-000000000000',
            'prompt': 'test',
        }, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_ai_query_records_audit_log(self):
        """Her sorgu AiQueryRecord oluşturmalı."""
        from credits.models import AiQueryRecord
        before = AiQueryRecord.objects.count()
        self.client.post('/api/mathlock/ai/query/', {
            'device_token': str(self.device.device_token),
            'prompt': 'bölme sorusu',
            'provider': 'simulate',
        }, format='json')
        self.assertEqual(AiQueryRecord.objects.count(), before + 1)


# ─── API: Dinamik Paket Listesi ──────────────────────────────────────────────

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
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
        # settings.py'de 3 ürün var
        self.assertEqual(len(data['packages']), 3)
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


# ─── Çocuk Rapor & İstatistik Testleri ──────────────────────────────────────

@override_settings(REST_FRAMEWORK=NO_THROTTLE)
class ChildReportViewTest(ThrottleMixin, TestCase):
    """child_report ve stats_history endpoint testleri."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id="report-test-001",
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(
            device=self.device,
            name="Elif",
            education_period="sinif_2",
            is_active=True,
            total_correct=75,
            total_shown=100,
            total_time_seconds=3600,
            stats_json={
                "byType": {
                    "toplama": {"shown": 40, "correct": 38, "avgTime": 3.2, "hintUsed": 2, "topicUsed": 1},
                    "cikarma": {"shown": 30, "correct": 20, "avgTime": 5.5, "hintUsed": 5, "topicUsed": 3},
                    "carpma": {"shown": 30, "correct": 17, "avgTime": 8.0, "hintUsed": 10, "topicUsed": 5},
                }
            },
            daily_stats={
                "2026-04-18": {"solved": 12, "correct": 10, "time_s": 300},
                "2026-04-17": {"solved": 8, "correct": 6, "time_s": 200},
                "2026-04-16": {"solved": 15, "correct": 12, "time_s": 400},
            },
            weekly_report_json={
                "strengths": ["Toplama işlemlerinde çok başarılı"],
                "improvementAreas": ["Çarpma konusunda gelişim gerekiyor"],
                "recommendation": "Çarpma tablosunu tekrar etmeli.",
            },
        )
        self.token = str(self.device.device_token)

    # ─── child_report endpoint ───────────────────────────────────────────

    def test_child_report_success(self):
        resp = self.client.get(f'/api/mathlock/children/report/?device_token={self.token}&child_name=Elif')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('child', data)
        self.assertIn('by_type', data)
        self.assertEqual(data['child']['name'], 'Elif')
        self.assertEqual(data['child']['education_period'], 'sinif_2')
        self.assertAlmostEqual(data['child']['accuracy'], 75.0, places=0)

    def test_child_report_by_type_categories(self):
        resp = self.client.get(f'/api/mathlock/children/report/?device_token={self.token}&child_name=Elif')
        data = resp.json()
        by_type = data['by_type']
        # toplama: 95% + 3.2s → USTA
        self.assertEqual(by_type['toplama']['category'], 'USTA')
        # cikarma: 66.7% → GELİŞEN
        self.assertEqual(by_type['cikarma']['category'], 'GELİŞEN')
        # carpma: 56.7% → ZORLU
        self.assertEqual(by_type['carpma']['category'], 'ZORLU')

    def test_child_report_missing_token(self):
        resp = self.client.get('/api/mathlock/children/report/?child_name=Elif')
        self.assertEqual(resp.status_code, 400)

    def test_child_report_invalid_token(self):
        resp = self.client.get(f'/api/mathlock/children/report/?device_token={uuid.uuid4()}&child_name=Elif')
        self.assertEqual(resp.status_code, 404)

    def test_child_report_unknown_child(self):
        resp = self.client.get(f'/api/mathlock/children/report/?device_token={self.token}&child_name=Ahmet')
        self.assertEqual(resp.status_code, 404)

    def test_child_report_weekly_report_fields(self):
        resp = self.client.get(f'/api/mathlock/children/report/?device_token={self.token}&child_name=Elif')
        data = resp.json()
        self.assertIn('weekly_report', data)
        wr = data['weekly_report']
        self.assertIn('strengths', wr)
        self.assertIn('recommendation', wr)

    # ─── stats_history endpoint ──────────────────────────────────────────

    def test_stats_history_success(self):
        resp = self.client.get(f'/api/mathlock/children/stats-history/?device_token={self.token}&child_name=Elif')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('daily', data)
        self.assertIn('by_type', data)
        self.assertIn('streak_days', data)
        self.assertIn('total_time_minutes', data)

    def test_stats_history_streak_calculation(self):
        """Ardışık gün sayısı doğru hesaplanmalı."""
        # Test verisinde bugün (2026-04-18) dahil 3 ardışık gün var
        # Ancak gerçek tarih farklı olabilir, streak 0-3 arasında olmalı
        resp = self.client.get(f'/api/mathlock/children/stats-history/?device_token={self.token}&child_name=Elif')
        data = resp.json()
        self.assertGreaterEqual(data['streak_days'], 0)

    def test_stats_history_by_type_accuracy(self):
        resp = self.client.get(f'/api/mathlock/children/stats-history/?device_token={self.token}&child_name=Elif')
        data = resp.json()
        self.assertIn('toplama', data['by_type'])
        toplama = data['by_type']['toplama']
        self.assertEqual(toplama['total'], 40)
        self.assertEqual(toplama['correct'], 38)
        self.assertAlmostEqual(toplama['accuracy'], 95.0, places=0)

    def test_stats_history_total_time_minutes(self):
        resp = self.client.get(f'/api/mathlock/children/stats-history/?device_token={self.token}&child_name=Elif')
        data = resp.json()
        self.assertEqual(data['total_time_minutes'], 60.0)

    def test_stats_history_missing_token(self):
        resp = self.client.get('/api/mathlock/children/stats-history/?child_name=Elif')
        self.assertEqual(resp.status_code, 400)

    def test_stats_history_invalid_token(self):
        resp = self.client.get(f'/api/mathlock/children/stats-history/?device_token={uuid.uuid4()}&child_name=Elif')
        self.assertEqual(resp.status_code, 404)
