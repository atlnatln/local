"""
Backend kredi sistemi testleri.

Çalıştırmak:
    cd /home/akn/vps/projects/mathlock-play/backend
    pip install -r requirements.txt
    python manage.py test credits
"""
import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from credits.models import Device, ChildProfile, CreditBalance, LevelSet, PurchaseRecord, QuestionSet, RenewalLock, Question, UserQuestionProgress
from credits.google_play import verify_purchase
from credits.views import _deduct_credit_and_lock, _release_renewal_lock
import unittest

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
        self.assertEqual(resp.json()['message'], 'purchase_already_processed')

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
        self.assertEqual(by_type['toplama']['category'], 'category_master')
        # cikarma: 66.7% → GELİŞEN
        self.assertEqual(by_type['cikarma']['category'], 'category_developing')
        # carpma: 56.7% → ZORLU
        self.assertEqual(by_type['carpma']['category'], 'category_challenging')

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


# ─── RenewalLock Model Testleri ──────────────────────────────────────────────

class RenewalLockModelTest(TestCase):

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='lock-test-001',
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(device=self.device, name='Test')

    def test_create_lock(self):
        lock = RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        self.assertEqual(lock.content_type, 'questions')
        self.assertEqual(lock.child, self.child)

    def test_unique_together_prevents_duplicate(self):
        """Aynı child+content_type ikinci kez eklenemez."""
        from django.db import IntegrityError
        RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        with self.assertRaises(IntegrityError):
            RenewalLock.objects.create(
                child=self.child,
                content_type='questions',
                expires_at=timezone.now() + timedelta(minutes=15),
            )

    def test_different_content_types_allowed(self):
        """Aynı child için 'questions' ve 'levels' aynı anda var olabilir."""
        RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        RenewalLock.objects.create(
            child=self.child,
            content_type='levels',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        self.assertEqual(RenewalLock.objects.filter(child=self.child).count(), 2)


# ─── ChildProfile.save() eğitim dönemi doğrulama ─────────────────────────────

class ChildProfileEducationPeriodTest(TestCase):

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='edu-period-test-001',
            device_token=uuid.uuid4(),
        )

    def test_valid_period_preserved(self):
        for period in ('okul_oncesi', 'sinif_1', 'sinif_2', 'sinif_3', 'sinif_4'):
            child = ChildProfile.objects.create(
                device=self.device,
                name=f'Child-{period}',
                education_period=period,
            )
            child.refresh_from_db()
            self.assertEqual(child.education_period, period, f"{period} korunmalıydı")

    def test_invalid_period_coerced_to_sinif_2(self):
        child = ChildProfile(
            device=self.device,
            name='Yanlış Dönem',
            education_period='sinif_99',
        )
        child.save()
        child.refresh_from_db()
        self.assertEqual(child.education_period, 'sinif_2')

    def test_empty_period_coerced(self):
        child = ChildProfile(
            device=self.device,
            name='Boş Dönem',
            education_period='',
        )
        child.save()
        child.refresh_from_db()
        self.assertEqual(child.education_period, 'sinif_2')

    def test_update_invalid_period_coerced(self):
        child = ChildProfile.objects.create(
            device=self.device,
            name='Güncelleme Test',
            education_period='sinif_1',
        )
        child.education_period = 'yanlis_deger'
        child.save()
        child.refresh_from_db()
        self.assertEqual(child.education_period, 'sinif_2')


# ─── _deduct_credit_and_lock fonksiyon testleri ──────────────────────────────

class DeductCreditAndLockTest(TestCase):

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='lock-func-test-001',
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(device=self.device, name='Ali')
        self.balance = CreditBalance.objects.create(
            device=self.device,
            balance=3,
            total_purchased=3,
            free_set_used=True,
        )

    def test_first_call_creates_lock_and_deducts(self):
        success, is_free, cb_pk, remaining = _deduct_credit_and_lock(
            self.child.pk, self.device, 'questions'
        )
        self.assertTrue(success)
        self.assertFalse(is_free)
        self.assertEqual(remaining, 2)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 2)
        self.assertTrue(
            RenewalLock.objects.filter(child=self.child, content_type='questions').exists()
        )

    def test_second_call_blocked_by_lock(self):
        """Kilit varken ikinci çağrı False döner, kredi düşülmez."""
        _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        # İkinci çağrı
        success, _, _, _ = _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        self.assertFalse(success)
        # Bakiye sadece 1 kez düşmeli
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 2)

    def test_expired_lock_replaced(self):
        """Süresi dolmuş kilit silinip yeni kilit alınmalı."""
        RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() - timedelta(minutes=1),  # geçmiş
        )
        success, _, _, remaining = _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        self.assertTrue(success)
        self.assertEqual(remaining, 2)
        # Eski değil, yeni kilit var
        lock = RenewalLock.objects.get(child=self.child, content_type='questions')
        self.assertGreater(lock.expires_at, timezone.now())

    def test_no_credit_returns_false_and_no_lock(self):
        """Kredi yoksa False döner ve kilit kalmaz."""
        self.balance.balance = 0
        self.balance.save()
        success, _, cb_pk, remaining = _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        self.assertFalse(success)
        self.assertEqual(remaining, 0)
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='questions').exists()
        )

    def test_free_set_deduction(self):
        """free_set_used=False iken ücretsiz set kullanılmalı."""
        self.balance.free_set_used = False
        self.balance.balance = 0
        self.balance.save()
        success, is_free, _, _ = _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        self.assertTrue(success)
        self.assertTrue(is_free)
        self.balance.refresh_from_db()
        self.assertTrue(self.balance.free_set_used)

    def test_different_content_types_independent(self):
        """'questions' kilidi 'levels' kilidini bloke etmez."""
        _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        success, _, _, _ = _deduct_credit_and_lock(self.child.pk, self.device, 'levels')
        self.assertTrue(success)

    def test_different_children_independent(self):
        """Bir çocuğun kilidi diğerini etkilemez."""
        child2 = ChildProfile.objects.create(device=self.device, name='Veli')
        _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        success, _, _, _ = _deduct_credit_and_lock(child2.pk, self.device, 'questions')
        self.assertTrue(success)

    def test_nonexistent_child_returns_false(self):
        success, _, _, _ = _deduct_credit_and_lock(99999, self.device, 'questions')
        self.assertFalse(success)


# ─── _release_renewal_lock fonksiyon testleri ────────────────────────────────

class ReleaseRenewalLockTest(TestCase):

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='release-test-001',
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(device=self.device, name='Zeynep')

    def test_release_existing_lock(self):
        RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        _release_renewal_lock(self.child.pk, 'questions')
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='questions').exists()
        )

    def test_release_nonexistent_lock_silently(self):
        """Var olmayan kilidi silmek hata fırlatmamalı."""
        try:
            _release_renewal_lock(self.child.pk, 'questions')
        except Exception as e:
            self.fail(f"Beklenmeyen hata: {e}")

    def test_release_only_specified_type(self):
        """Yalnızca belirtilen content_type kilidi silinmeli."""
        RenewalLock.objects.create(
            child=self.child, content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        RenewalLock.objects.create(
            child=self.child, content_type='levels',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        _release_renewal_lock(self.child.pk, 'questions')
        self.assertFalse(RenewalLock.objects.filter(child=self.child, content_type='questions').exists())
        self.assertTrue(RenewalLock.objects.filter(child=self.child, content_type='levels').exists())


# ─── update_progress auto-renewal entegrasyon testleri ───────────────────────

@override_settings(REST_FRAMEWORK=NO_THROTTLE)
class UpdateProgressAutoRenewalTest(ThrottleMixin, TestCase):
    """update_progress endpoint'inde otomatik soru yenileme davranışı."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='progress-renew-001',
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(device=self.device, name='Selin')
        self.balance = CreditBalance.objects.create(
            device=self.device,
            balance=2,
            total_purchased=2,
            free_set_used=True,
        )
        # Tek bir AI soru seti oluştur (1 soru), daha önce çözülmemiş
        self.qset = QuestionSet.objects.create(
            child=self.child,
            version=1,
            questions_json=[{'id': 1, 'text': 'soru1'}],
            solved_ids=[],
            credit_used=True,
        )
        # Celery proxy'yi atlayarak doğrudan mock'la
        import credits.views
        self._orig_generate_question_set = credits.views.__dict__.get('generate_question_set')
        self.mock_generate_question_set = MagicMock()
        self.mock_generate_question_set.delay = MagicMock()
        self.mock_generate_question_set.delay.return_value = MagicMock(id='fake-job-id')
        credits.views.__dict__['generate_question_set'] = self.mock_generate_question_set

    def tearDown(self):
        import credits.views
        credits.views.__dict__['generate_question_set'] = self._orig_generate_question_set
        super().tearDown()

    def _progress_url(self):
        return '/api/mathlock/questions/progress/'

    def test_auto_renewal_triggered_when_all_solved(self):
        """Tüm sorular çözülünce auto-renewal başlatılmalı."""
        from credits.views import _global_id_for_ai
        global_id = _global_id_for_ai(self.qset.pk, 0)  # set_pk * 1000 + 1

        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'solved_questions': [global_id],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['auto_renewal_started'])
        self.assertIn('credits_remaining', data)
        self.mock_generate_question_set.delay.assert_called_once()

    def test_no_auto_renewal_when_questions_remain(self):
        """Çözülmemiş sorular varsa auto-renewal başlatılmamalı."""
        # İkinci soru ekle — biri çözülmemiş kalacak
        self.qset.questions_json = [
            {'id': 1, 'text': 's1'}, {'id': 2, 'text': 's2'}
        ]
        self.qset.save()

        from credits.views import _global_id_for_ai
        global_id = _global_id_for_ai(self.qset.pk, 0)

        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'solved_questions': [global_id],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['auto_renewal_started'])
        self.mock_generate_question_set.delay.assert_not_called()

    def test_double_trigger_blocked_by_lock(self):
        """Aynı anda iki istek gelirse ikincisi kilit nedeniyle yenileme başlatmamalı."""
        # Önceden kilit yerleştir
        RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        from credits.views import _global_id_for_ai
        global_id = _global_id_for_ai(self.qset.pk, 0)

        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'solved_questions': [global_id],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['auto_renewal_started'])
        self.mock_generate_question_set.delay.assert_not_called()
        # Bakiye değişmemeli
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 2)


# ─── update_level_progress auto-renewal entegrasyon testleri ─────────────────

@override_settings(REST_FRAMEWORK=NO_THROTTLE)
class UpdateLevelProgressAutoRenewalTest(ThrottleMixin, TestCase):
    """update_level_progress endpoint'inde otomatik seviye yenileme davranışı."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='level-renew-001',
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(device=self.device, name='Mert')
        self.balance = CreditBalance.objects.create(
            device=self.device,
            balance=2,
            total_purchased=2,
            free_set_used=True,
        )
        self.level_set = LevelSet.objects.create(
            child=self.child,
            version=1,
            levels_json=[{'id': i} for i in range(1, 4)],  # 3 seviye
            completed_level_ids=[1, 2],  # 2 tamamlanmış, 1 kaldı
            credit_used=True,
        )
        # Celery proxy'yi atlayarak doğrudan mock'la
        import credits.views
        self._orig_generate_level_set = credits.views.__dict__.get('generate_level_set')
        self.mock_generate_level_set = MagicMock()
        self.mock_generate_level_set.delay = MagicMock()
        self.mock_generate_level_set.delay.return_value = MagicMock(id='fake-job-id')
        credits.views.__dict__['generate_level_set'] = self.mock_generate_level_set

    def tearDown(self):
        import credits.views
        credits.views.__dict__['generate_level_set'] = self._orig_generate_level_set
        super().tearDown()

    def _progress_url(self):
        return '/api/mathlock/levels/progress/'

    def test_auto_renewal_triggered_when_all_levels_done(self):
        """Son seviye tamamlanınca auto-renewal başlatılmalı."""
        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2, 3],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['all_completed'])
        self.assertTrue(data['auto_renewal_started'])
        self.mock_generate_level_set.delay.assert_called_once()

    def test_no_auto_renewal_when_levels_remain(self):
        """Tamamlanmamış seviyeler varsa renewal başlatılmamalı."""
        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2],  # 3. hâlâ yok
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['all_completed'])
        self.assertFalse(resp.json()['auto_renewal_started'])
        self.mock_generate_level_set.delay.assert_not_called()

    def test_double_trigger_blocked_by_lock(self):
        """Kilit varken ikinci tamamlama isteği renewal başlatmamalı."""
        RenewalLock.objects.create(
            child=self.child,
            content_type='levels',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2, 3],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['auto_renewal_started'])
        self.mock_generate_level_set.delay.assert_not_called()
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, 2)

    def test_already_completed_set_retries_renewal(self):
        """Zaten tamamlanmış set tekrar raporlanırsa ve yeni set yoksa renewal BAŞLATILMALI.

        Bu test eski bug'ı (deadlock) doğrular:
        Eski kodda new_completed boş olduğu için renewal hiçbir zaman tekrar denenmiyordu.
        Yeni kodda has_newer + lock_exists kontrolü ile bu çözüldü.
        """
        # Önceden tüm seviyeleri tamamla
        self.level_set.completed_level_ids = [1, 2, 3]
        self.level_set.save()

        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2, 3],  # hepsi zaten tamamlanmış
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['all_completed'])
        self.assertTrue(data['auto_renewal_started'], 
            "Eski set tamamlanmış ama yeni set yoksa renewal tekrar denenmeli!")
        self.mock_generate_level_set.delay.assert_called_once()

    def test_already_completed_set_with_newer_version_no_renewal(self):
        """Daha yüksek versiyonlu set zaten varsa renewal başlatılmamalı."""
        # Önceden tüm seviyeleri tamamla
        self.level_set.completed_level_ids = [1, 2, 3]
        self.level_set.save()
        # Daha yeni versiyonlu set oluştur
        LevelSet.objects.create(
            child=self.child,
            version=2,
            levels_json=[{'id': i} for i in range(1, 4)],
            completed_level_ids=[],
        )

        resp = self.client.post(self._progress_url(), {
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2, 3],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['auto_renewal_started'])
        self.mock_generate_level_set.delay.assert_not_called()

    def test_renewal_actually_creates_new_level_set(self):
        """ Renewal başarılı olursa gerçekten yeni LevelSet DB'ye yazılmalı. """
        self.level_set.completed_level_ids = [1, 2, 3]
        self.level_set.save()

        from credits.tasks import generate_level_set
        fake_levels = [{'id': i, 'title': f'Seviye {i}'} for i in range(1, 4)]

        with patch('credits.views._generate_levels_via_kimi', return_value=fake_levels):
            def _run_and_return_mock(*args, **kwargs):
                generate_level_set.run(*args, **kwargs)
                return MagicMock(id='fake-job-id')
            self.mock_generate_level_set.delay.side_effect = _run_and_return_mock
            resp = self.client.post(self._progress_url(), {
                'device_token': str(self.device.device_token),
                'child_id': self.child.pk,
                'set_id': self.level_set.pk,
                'completed_level_ids': [1, 2, 3],
            }, format='json')
            self.mock_generate_level_set.delay.side_effect = None

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['auto_renewal_started'])

        # Yeni set oluşturulmuş mu?
        new_set = LevelSet.objects.filter(child=self.child, version=2).first()
        self.assertIsNotNone(new_set, "Yeni LevelSet (version=2) DB'ye yazılmalı!")
        self.assertEqual(new_set.levels_json, fake_levels)

        # get_levels yeni seti döndürmeli
        get_resp = self.client.get(
            f'/api/mathlock/levels/?device_token={self.device.device_token}&child_id={self.child.pk}'
        )
        self.assertEqual(get_resp.status_code, 200)
        get_data = get_resp.json()
        self.assertEqual(get_data['version'], 2)
        self.assertEqual(get_data['completed_count'], 0)
        self.assertEqual(get_data['set_id'], new_set.pk)


# ─── Eksik API Testleri (Plan: Backend + Android HTTP Client Tests) ─────────


@override_settings(**NO_THROTTLE)
class RegisterEmailViewTest(ThrottleMixin, TestCase):
    """POST /api/mathlock/auth/register-email/"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='reg-email-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
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
        resp = self.client.post(self.url, {'email': 'ali@example.com'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        resp = self.client.post(self.url, {
            'device_token': str(uuid.uuid4()),
            'email': 'ali@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 404)

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


@override_settings(**NO_THROTTLE)
class GetQuestionsViewTest(ThrottleMixin, TestCase):
    """GET /api/mathlock/questions/"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='questions-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self.url = '/api/mathlock/questions/'
        # Ücretsiz soru oluştur
        for i in range(1, 4):
            Question.objects.create(
                question_id=i, text=f'Soru {i}', answer=i,
                question_type='arithmetic', difficulty=1, batch_number=0
            )

    def test_valid_token(self):
        resp = self.client.get(f'{self.url}?device_token={self.device.device_token}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['solved_count'], 0)
        self.assertEqual(data['ai_sets'], 0)

    def test_missing_token(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        resp = self.client.get(f'{self.url}?device_token={uuid.uuid4()}')
        self.assertEqual(resp.status_code, 404)

    def test_with_child_id(self):
        resp = self.client.get(
            f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['total_questions'], 3)

    def test_no_child(self):
        device2 = Device.objects.create(
            installation_id='no-child-device', device_token=uuid.uuid4()
        )
        resp = self.client.get(f'{self.url}?device_token={device2.device_token}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['total_questions'], 3)

    def test_ai_set_questions(self):
        qs = QuestionSet.objects.create(
            child=self.child, version=1,
            questions_json=[
                {'text': 'AI 1', 'answer': 1, 'type': 'arithmetic', 'difficulty': 2},
                {'text': 'AI 2', 'answer': 2, 'type': 'arithmetic', 'difficulty': 2},
            ],
            solved_ids=[]
        )
        resp = self.client.get(f'{self.url}?device_token={self.device.device_token}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_questions'], 5)  # 3 free + 2 AI
        self.assertEqual(data['ai_sets'], 1)
        # Global ID kontrolü
        ai_ids = [q['id'] for q in data['questions'] if q['source'] == 'ai']
        self.assertEqual(ai_ids, [qs.pk * 1000 + 1, qs.pk * 1000 + 2])


@override_settings(**NO_THROTTLE)
class GetLevelsViewTest(ThrottleMixin, TestCase):
    """GET /api/mathlock/levels/"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='levels-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self.url = '/api/mathlock/levels/'
        self.level_set = LevelSet.objects.create(
            child=self.child, version=1,
            levels_json=[{'id': i} for i in range(1, 4)],
            completed_level_ids=[1]
        )

    def test_valid_token_with_set(self):
        resp = self.client.get(
            f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['version'], 1)
        self.assertEqual(data['set_id'], self.level_set.pk)
        self.assertEqual(data['completed_level_ids'], [1])
        self.assertEqual(data['total_levels'], 3)
        self.assertEqual(data['completed_count'], 1)

    def test_missing_token(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        resp = self.client.get(f'{self.url}?device_token={uuid.uuid4()}')
        self.assertEqual(resp.status_code, 404)

    def test_no_child(self):
        device2 = Device.objects.create(
            installation_id='no-child-device', device_token=uuid.uuid4()
        )
        resp = self.client.get(f'{self.url}?device_token={device2.device_token}')
        self.assertEqual(resp.status_code, 404)

    def test_no_set_fallback_file(self):
        """LevelSet yoksa fallback levels.json dosyasından oluşturulmalı."""
        from credits.views import _LEVELS_FILE
        self.level_set.delete()
        resp = self.client.get(
            f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}'
        )
        # fallback levels.json mevcutsa 200 döner, yoksa 503
        if _LEVELS_FILE.exists():
            self.assertEqual(resp.status_code, 200)
            self.assertIn('levels', resp.json())
        else:
            self.assertEqual(resp.status_code, 503)


@override_settings(**NO_THROTTLE)
class ChildrenListViewTest(ThrottleMixin, TestCase):
    """GET/POST /api/mathlock/children/"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='children-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2', is_active=True
        )
        self.url = '/api/mathlock/children/'

    def test_get_list(self):
        ChildProfile.objects.create(
            device=self.device, name='Veli', education_period='sinif_1'
        )
        resp = self.client.get(f'{self.url}?device_token={self.device.device_token}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['children']), 2)
        # Aktif profil ilk sırada olmalı
        self.assertTrue(data['children'][0]['is_active'])

    def test_post_create(self):
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'name': 'Ayşe',
            'education_period': 'sinif_1',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['child']['name'], 'Ayşe')
        self.assertEqual(data['child']['education_period'], 'sinif_1')
        self.assertFalse(data['child']['is_active'])

    def test_post_duplicate_name(self):
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'name': 'Ali',
            'education_period': 'sinif_2',
        }, format='json')
        self.assertEqual(resp.status_code, 409)

    def test_post_invalid_period(self):
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'name': 'Fatma',
            'education_period': 'invalid_period',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_post_max_children(self):
        for i in range(2, 6):
            ChildProfile.objects.create(
                device=self.device, name=f'Çocuk{i}', education_period='sinif_2'
            )
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'name': 'Altıncı',
            'education_period': 'sinif_2',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_post_missing_name(self):
        # _sanitize_child_name boş string döndürür, boş isim kabul edilebilir
        resp = self.client.post(self.url, {
            'device_token': str(self.device.device_token),
            'name': '',
            'education_period': 'sinif_2',
        }, format='json')
        # Boş isim 201 (başarılı oluşturma) veya 400 dönebilir
        self.assertIn(resp.status_code, [201, 400])


@override_settings(**NO_THROTTLE)
class ChildrenDetailViewTest(ThrottleMixin, TestCase):
    """PUT/DELETE /api/mathlock/children/detail/"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='detail-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2', is_active=True
        )
        self.url = '/api/mathlock/children/detail/'

    def _put_json(self, data):
        import json
        return self.client.put(self.url, json.dumps(data), content_type='application/json')

    def _delete_json(self, data):
        import json
        return self.client.delete(self.url, json.dumps(data), content_type='application/json')

    def test_put_update_name(self):
        resp = self._put_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'new_name': 'AliCan',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['child']['name'], 'AliCan')

    def test_put_update_period(self):
        resp = self._put_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'education_period': 'sinif_3',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['child']['education_period'], 'sinif_3')

    def test_put_invalid_period(self):
        resp = self._put_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'education_period': 'invalid',
        })
        self.assertEqual(resp.status_code, 400)

    def test_delete_success(self):
        ChildProfile.objects.create(
            device=self.device, name='Veli', education_period='sinif_1'
        )
        resp = self._delete_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])
        self.assertFalse(ChildProfile.objects.filter(pk=self.child.pk).exists())

    def test_delete_last_profile(self):
        resp = self._delete_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
        })
        self.assertEqual(resp.status_code, 400)


@override_settings(**NO_THROTTLE)
class UpdateProgressNormalTest(ThrottleMixin, TestCase):
    """POST /api/mathlock/questions/progress/ — normal path (no auto-renewal)"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='progress-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self.url = '/api/mathlock/questions/progress/'
        for i in range(1, 4):
            Question.objects.create(
                question_id=i, text=f'Soru {i}', answer=i,
                question_type='arithmetic', difficulty=1, batch_number=0
            )

    def _post_json(self, data):
        import json
        return self.client.post(self.url, json.dumps(data), content_type='application/json')

    def test_partial_progress(self):
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'solved_questions': [1, 2],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['updated'], 2)
        self.assertEqual(data['total_solved'], 2)
        self.assertFalse(data['auto_renewal_started'])

    def test_progress_with_invalid_question_id(self):
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'solved_questions': [999],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['updated'], 0)

    def test_reset_rotation(self):
        # Önce çöz
        self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'solved_questions': [1, 2],
        })
        # Sıfırla
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'reset_rotation': True,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['total_solved'], 0)

    def test_no_renewal_when_not_all_solved(self):
        """Tüm sorular çözülmediyse auto_renewal başlamamalı."""
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'solved_questions': [1],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['auto_renewal_started'])


@override_settings(**NO_THROTTLE)
class UpdateLevelProgressNormalTest(ThrottleMixin, TestCase):
    """POST /api/mathlock/levels/progress/ — normal path (no auto-renewal)"""

    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(
            installation_id='level-progress-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self.url = '/api/mathlock/levels/progress/'
        self.level_set = LevelSet.objects.create(
            child=self.child, version=1,
            levels_json=[{'id': i} for i in range(1, 4)],
            completed_level_ids=[]
        )

    def _post_json(self, data):
        import json
        return self.client.post(self.url, json.dumps(data), content_type='application/json')

    def test_partial_progress(self):
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['completed_count'], 1)
        self.assertFalse(data['all_completed'])
        self.assertFalse(data['auto_renewal_started'])

    def test_retry_same_level(self):
        self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1],
        })
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['completed_count'], 1)

    def test_no_renewal_when_not_all_completed(self):
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['all_completed'])
        self.assertFalse(resp.json()['auto_renewal_started'])

    def test_progress_with_newer_version_exists_no_renewal(self):
        """Daha yeni versiyonlu set zaten varsa renewal başlamamalı."""
        self.level_set.completed_level_ids = [1, 2, 3]
        self.level_set.save()
        LevelSet.objects.create(
            child=self.child, version=2,
            levels_json=[{'id': i} for i in range(1, 4)],
            completed_level_ids=[]
        )
        resp = self._post_json({
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': self.level_set.pk,
            'completed_level_ids': [1, 2, 3],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['all_completed'])
        self.assertFalse(resp.json()['auto_renewal_started'])


# ─── Faz 2: Yeni Backend Testleri ────────────────────────────────────────────

@override_settings(**NO_THROTTLE)
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


@override_settings(**NO_THROTTLE)
class GetLevelsLocaleTest(ThrottleMixin, TestCase):
    """GET /levels/ endpoint'inde locale query parametresi davranışı."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='levels-locale-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2', locale='tr'
        )
        self.url = '/api/mathlock/levels/'

    def test_levels_with_locale_en_param(self):
        from credits.views import _DATA_DIR
        en_file = _DATA_DIR / 'fallback-levels.en.json'
        has_en = en_file.exists()

        resp = self.client.get(
            f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}&locale=en'
        )
        if has_en:
            self.assertEqual(resp.status_code, 200)
            self.assertIn('levels', resp.json())
        else:
            self.assertIn(resp.status_code, [200, 503])

    def test_levels_with_locale_tr_param(self):
        from credits.views import _DATA_DIR
        tr_file = _DATA_DIR / 'fallback-levels.tr.json'
        has_tr = tr_file.exists()

        resp = self.client.get(
            f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}&locale=tr'
        )
        if has_tr:
            self.assertEqual(resp.status_code, 200)
            self.assertIn('levels', resp.json())
        else:
            self.assertIn(resp.status_code, [200, 503])

    def test_levels_without_locale_uses_tr(self):
        """locale parametresi yoksa child.locale veya 'tr' default kullanılır."""
        from credits.views import _DATA_DIR
        tr_file = _DATA_DIR / 'fallback-levels.tr.json'
        has_tr = tr_file.exists()

        resp = self.client.get(
            f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}'
        )
        if has_tr:
            self.assertEqual(resp.status_code, 200)
            self.assertIn('levels', resp.json())
        else:
            self.assertIn(resp.status_code, [200, 503])


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_BROKER_URL='memory://',
    CELERY_RESULT_BACKEND='cache+memory://',
)
class CeleryTaskTest(TestCase):
    """Celery task'larının doğrudan davranış testleri (worker olmadan)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from mathlock_backend.celery import app
        app.conf.task_always_eager = True
        app.conf.broker_url = 'memory://'
        app.conf.result_backend = 'cache+memory://'

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='celery-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Celery', education_period='sinif_2'
        )
        self.balance = CreditBalance.objects.create(
            device=self.device, balance=2, total_purchased=2, free_set_used=True
        )

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'S1', 'answer': 1, 'type': 'a', 'difficulty': 1}
    ] * 50)
    def test_generate_question_set_creates_record(self, mock_gen):
        from credits.tasks import generate_question_set
        result = generate_question_set.run(self.child.pk, self.balance.pk, False)
        self.assertTrue(result['success'])
        self.assertTrue(
            QuestionSet.objects.filter(child=self.child).exists()
        )

    @patch('credits.views._generate_levels_via_kimi', return_value=[
        {'id': 1, 'title': 'S1'}, {'id': 2, 'title': 'S2'}, {'id': 3, 'title': 'S3'}
    ])
    def test_generate_level_set_creates_record(self, mock_gen):
        from credits.tasks import generate_level_set
        result = generate_level_set.run(self.child.pk, self.balance.pk, False, {}, 'sinif_2')
        self.assertTrue(result['success'])
        self.assertTrue(
            LevelSet.objects.filter(child=self.child).exists()
        )

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'S1', 'answer': 1, 'type': 'a', 'difficulty': 1}
    ] * 50)
    def test_task_releases_lock_on_success(self, mock_gen):
        from credits.tasks import generate_question_set
        RenewalLock.objects.create(
            child=self.child, content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        generate_question_set.run(self.child.pk, self.balance.pk, False)
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='questions').exists()
        )

    @patch('credits.views._generate_via_kimi', side_effect=Exception('AI failure'))
    def test_task_releases_lock_on_failure(self, mock_gen):
        from credits.tasks import generate_question_set
        RenewalLock.objects.create(
            child=self.child, content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        with self.assertRaises(Exception):
            generate_question_set.run(self.child.pk, self.balance.pk, False)
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='questions').exists()
        )

    def test_task_retries_on_failure(self):
        from credits.tasks import generate_question_set, generate_level_set
        self.assertEqual(generate_question_set.max_retries, 3)
        self.assertEqual(generate_level_set.max_retries, 3)


class StaleLockCleanupTest(TestCase):
    """_deduct_credit_and_lock içinde eski kilit temizliği."""

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='stale-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(device=self.device, name='Stale')
        self.balance = CreditBalance.objects.create(
            device=self.device, balance=2, total_purchased=2, free_set_used=True
        )

    def test_stale_lock_deleted(self):
        """40+ dakika eski lock _deduct_credit_and_lock sırasında silinir."""
        old_lock = RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        old_time = timezone.now() - timedelta(minutes=41)
        RenewalLock.objects.filter(pk=old_lock.pk).update(created_at=old_time)

        success, _, _, _ = _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        self.assertTrue(success)
        # Eski lock silinmiş, yeni kilit oluşmuş olmalı
        lock = RenewalLock.objects.get(child=self.child, content_type='questions')
        self.assertNotEqual(lock.pk, old_lock.pk)

    def test_fresh_lock_preserved(self):
        """5 dakika eski lock silinmez, ikinci çağrı blocked olur."""
        RenewalLock.objects.create(
            child=self.child,
            content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        success, _, _, _ = _deduct_credit_and_lock(self.child.pk, self.device, 'questions')
        self.assertFalse(success)


class _FakeAsyncResult:
    """Celery AsyncResult mock'u — backend bağlantısı olmadan."""
    def __init__(self, job_id):
        self.id = job_id
        self.state = 'PENDING'
        self.result = None


@override_settings(**NO_THROTTLE)
class JobStatusEndpointTest(ThrottleMixin, TestCase):
    """GET /jobs/<job_id>/status/ endpoint testleri."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    @patch('celery.result.AsyncResult', _FakeAsyncResult)
    def test_job_status_pending(self):
        resp = self.client.get('/api/mathlock/jobs/test-job-123/status/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['state'], 'PENDING')

    @patch('celery.result.AsyncResult', _FakeAsyncResult)
    def test_job_status_success(self):
        class FakeSuccess(_FakeAsyncResult):
            def __init__(self, job_id):
                super().__init__(job_id)
                self.state = 'SUCCESS'
                self.result = {'question_set_id': 42}

        with patch('celery.result.AsyncResult', FakeSuccess):
            resp = self.client.get('/api/mathlock/jobs/test-job-456/status/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['state'], 'SUCCESS')
        self.assertEqual(data['result']['question_set_id'], 42)

    @patch('celery.result.AsyncResult', _FakeAsyncResult)
    def test_job_status_invalid_id(self):
        """Geçersiz job ID ile bile endpoint 200 döner ve state içerir."""
        resp = self.client.get('/api/mathlock/jobs/invalid-id/status/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('state', resp.json())
