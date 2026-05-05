from .base import *

class SanitizationUnitTest(TestCase):
    """views._sanitize_child_name ve helper fonksiyon testleri."""

    def test_sanitize_removes_special_chars(self):
        from credits.views import _sanitize_child_name
        # < > silinir, script kalır
        self.assertEqual(_sanitize_child_name('Ali<script>'), 'Aliscript')

    def test_sanitize_trims_and_limits(self):
        from credits.views import _sanitize_child_name
        long_name = 'A' * 200
        self.assertEqual(len(_sanitize_child_name(long_name)), 100)

    def test_sanitize_empty_returns_default(self):
        from credits.views import _sanitize_child_name
        result = _sanitize_child_name('   ')
        self.assertTrue(len(result) > 0)

    def test_global_id_math(self):
        from credits.views import _global_id_for_ai, _parse_ai_global_id
        self.assertEqual(_global_id_for_ai(5, 0), 5001)
        self.assertEqual(_global_id_for_ai(5, 49), 5050)
        set_pk, idx = _parse_ai_global_id(5001)
        self.assertEqual(set_pk, 5)
        self.assertEqual(idx, 0)

    def test_parse_batch_zero(self):
        from credits.views import _parse_ai_global_id
        set_pk, idx = _parse_ai_global_id(50)
        self.assertIsNone(set_pk)
        self.assertEqual(idx, 50)

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

class RefundAndReportUnitTest(TestCase):
    """_refund_credit ve _refresh_weekly_report davranış testleri."""

    def setUp(self):
        self.device = Device.objects.create(
            installation_id='refund-device', device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Rapor', education_period='sinif_2',
            total_correct=10, total_shown=20, total_time_seconds=600,
            daily_stats={
                '2026-05-01': {'solved': 5, 'correct': 4, 'time_s': 300},
                '2026-05-02': {'solved': 5, 'correct': 3, 'time_s': 300},
            },
            stats_json={
                'byType': {
                    'toplama': {'shown': 10, 'correct': 8, 'avgTime': 3.0, 'hintUsed': 0, 'topicUsed': 0},
                }
            },
        )

    def test_refund_credit_restores_balance(self):
        cb = CreditBalance.objects.create(device=self.device, balance=5, total_used=2)
        from credits.views import _refund_credit
        _refund_credit(cb.pk, is_free=False)
        cb.refresh_from_db()
        self.assertEqual(cb.balance, 6)
        self.assertEqual(cb.total_used, 1)

    def test_refund_free_credit(self):
        cb = CreditBalance.objects.create(device=self.device, balance=0, free_set_used=True)
        from credits.views import _refund_credit
        _refund_credit(cb.pk, is_free=True)
        cb.refresh_from_db()
        self.assertFalse(cb.free_set_used)

    def test_refresh_weekly_report_structure(self):
        from credits.views import _refresh_weekly_report
        _refresh_weekly_report(self.child)
        self.child.refresh_from_db()
        report = self.child.weekly_report_json
        self.assertIn('totalSolved', report)
        self.assertIn('accuracy', report)
        self.assertIn('strongTopics', report)
        self.assertIn('weakTopics', report)
        self.assertIn('dailyBreakdown', report)

    def test_refresh_weekly_report_with_level_progress(self):
        LevelSet.objects.create(
            child=self.child, version=1,
            levels_json=[{'id': 1}, {'id': 2}],
            completed_level_ids=[1]
        )
        from credits.views import _refresh_weekly_report
        _refresh_weekly_report(self.child)
        self.child.refresh_from_db()
        self.assertIn('levelProgress', self.child.weekly_report_json)
        self.assertEqual(self.child.weekly_report_json['levelProgress']['completed'], 1)

class ThrottleConfigurationTest(TestCase):
    """Throttle scope ve rate yapılandırma doğrulama testleri."""

    def test_register_scope_rate_parsed(self):
        from credits.views import RegisterThrottle
        from rest_framework.throttling import SimpleRateThrottle
        # DRF SimpleRateThrottle.THROTTLE_RATES class variable olarak cache'lenir;
        # override_settings ile değişmeyebilir. Doğrudan patch'le.
        with patch.object(SimpleRateThrottle, 'THROTTLE_RATES', {
            'register': '2/minute',
            'purchase': '3/minute',
            'anon': '100/minute',
        }):
            t = RegisterThrottle()
            self.assertEqual(t.num_requests, 2)
            self.assertEqual(t.duration, 60)

    def test_purchase_scope_rate_parsed(self):
        from credits.views import PurchaseThrottle
        from rest_framework.throttling import SimpleRateThrottle
        with patch.object(SimpleRateThrottle, 'THROTTLE_RATES', {
            'register': '2/minute',
            'purchase': '3/minute',
            'anon': '100/minute',
        }):
            t = PurchaseThrottle()
            self.assertEqual(t.num_requests, 3)
            self.assertEqual(t.duration, 60)

    def test_health_has_no_throttle(self):
        """Health endpoint AllowAny + throttle yoktur, ardışık istekler 200 döner."""
        client = APIClient()
        for i in range(10):
            resp = client.get('/api/mathlock/health/')
            self.assertEqual(resp.status_code, 200)

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
