from .base import *

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
