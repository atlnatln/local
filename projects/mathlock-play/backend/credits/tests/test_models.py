from .base import *

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
