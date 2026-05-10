import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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

    @patch('credits.tasks.subprocess.Popen')
    def test_generate_question_set_creates_job(self, mock_popen):
        """Question launcher subprocess başlatır ve GenerationJob oluşturur."""
        from credits.tasks import generate_question_set
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        result = generate_question_set.run(self.child.pk, self.balance.pk, False)
        self.assertTrue(result['success'])
        self.assertTrue(
            GenerationJob.objects.filter(
                child=self.child, content_type='questions', status='running'
            ).exists()
        )

    @patch('credits.tasks.subprocess.Popen')
    def test_generate_level_set_creates_job(self, mock_popen):
        """Level launcher subprocess başlatır ve GenerationJob oluşturur."""
        from credits.tasks import generate_level_set
        mock_process = MagicMock()
        mock_process.pid = 12346
        mock_popen.return_value = mock_process

        result = generate_level_set.run(self.child.pk, self.balance.pk, False, {}, 'sinif_2')
        self.assertTrue(result['success'])
        self.assertTrue(
            GenerationJob.objects.filter(
                child=self.child, content_type='levels', status='running'
            ).exists()
        )

    @patch('credits.tasks.subprocess.Popen')
    def test_launcher_releases_lock_and_refunds_on_subprocess_failure(self, mock_popen):
        """Subprocess başlatılamazsa kilit serbest bırakılır ve kredi iade edilir."""
        from credits.tasks import generate_level_set
        mock_popen.side_effect = OSError("Cannot start")

        RenewalLock.objects.create(
            child=self.child, content_type='levels',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        old_balance = self.balance.balance

        result = generate_level_set.run(self.child.pk, self.balance.pk, False, {}, 'sinif_2')
        self.assertFalse(result['success'])
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, old_balance + 1)
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='levels').exists()
        )

    def test_poll_generations_completes_level_job(self):
        """Poller subprocess bitince LevelSet oluşturur."""
        from credits.tasks import poll_generation_jobs
        tmpdir = tempfile.mkdtemp()
        levels_file = Path(tmpdir) / 'levels.json'
        levels_file.write_text(json.dumps({
            'levels': [{'id': i, 'title': f'S{i}'} for i in range(1, 13)]
        }))

        job = GenerationJob.objects.create(
            child=self.child,
            content_type='levels',
            status='running',
            pid=99999,  # Non-existent PID → process bitti kabul edilir
            temp_dir=tmpdir,
            credit_balance_pk=self.balance.pk,
            is_free=False,
            education_period='sinif_2',
        )
        RenewalLock.objects.create(
            child=self.child, content_type='levels',
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        poll_generation_jobs.run()

        self.assertTrue(
            LevelSet.objects.filter(child=self.child, version=1).exists()
        )
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='levels').exists()
        )
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')

    def test_poll_generations_completes_question_job(self):
        """Poller subprocess bitince QuestionSet oluşturur."""
        from credits.tasks import poll_generation_jobs
        tmpdir = tempfile.mkdtemp()
        questions_file = Path(tmpdir) / 'questions.json'
        questions_file.write_text(json.dumps({
            'questions': [
                {'text': f'S{i}', 'answer': i, 'type': 'toplama', 'difficulty': 1}
                for i in range(1, 51)
            ]
        }))

        job = GenerationJob.objects.create(
            child=self.child,
            content_type='questions',
            status='running',
            pid=99999,
            temp_dir=tmpdir,
            credit_balance_pk=self.balance.pk,
            is_free=False,
            education_period='sinif_2',
        )
        RenewalLock.objects.create(
            child=self.child, content_type='questions',
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        poll_generation_jobs.run()

        self.assertTrue(
            QuestionSet.objects.filter(child=self.child, version=1).exists()
        )
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='questions').exists()
        )
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')

    def test_poll_generations_refunds_on_failure(self):
        """Poller output yoksa kredi iade eder."""
        from credits.tasks import poll_generation_jobs
        tmpdir = tempfile.mkdtemp()
        job = GenerationJob.objects.create(
            child=self.child,
            content_type='levels',
            status='running',
            pid=99999,
            temp_dir=tmpdir,
            credit_balance_pk=self.balance.pk,
            is_free=False,
        )
        RenewalLock.objects.create(
            child=self.child, content_type='levels',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        old_balance = self.balance.balance

        poll_generation_jobs.run()

        self.balance.refresh_from_db()
        self.assertEqual(self.balance.balance, old_balance + 1)
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertFalse(
            RenewalLock.objects.filter(child=self.child, content_type='levels').exists()
        )

    def test_poll_generations_skips_running_process(self):
        """PID hâlâ çalışıyorsa poller atlar."""
        import os
        from credits.tasks import poll_generation_jobs
        tmpdir = tempfile.mkdtemp()
        # Mevcut process PID'sini kullan (kesinlikle çalışıyor)
        job = GenerationJob.objects.create(
            child=self.child,
            content_type='levels',
            status='running',
            pid=os.getpid(),  # kendi process'imiz — kesinlikle çalışıyor
            temp_dir=tmpdir,
        )

        poll_generation_jobs.run()

        job.refresh_from_db()
        self.assertEqual(job.status, 'running')
