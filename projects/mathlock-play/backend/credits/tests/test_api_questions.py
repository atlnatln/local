from .base import *

class GetQuestionsViewTest(ThrottleMixin, AuthMixin, TestCase):
    """GET /api/mathlock/questions/"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='questions-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self._auth_client(self.device)
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
        # Auth header'ı temizle
        self.client.credentials()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_invalid_token(self):
        # Geçersiz signed token gönder
        self.client.credentials(HTTP_AUTHORIZATION='Device invalid-token')
        resp = self.client.get(f'{self.url}?device_token={uuid.uuid4()}')
        self.assertEqual(resp.status_code, 403)

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
        self._auth_client(device2)
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

class UpdateProgressAutoRenewalTest(ThrottleMixin, AuthMixin, TestCase):
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
        self._auth_client(self.device)
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

class UpdateProgressNormalTest(ThrottleMixin, AuthMixin, TestCase):
    """POST /api/mathlock/questions/progress/ — normal path (no auto-renewal)"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='progress-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self._auth_client(self.device)
        self.url = '/api/mathlock/questions/progress/'
        for i in range(1, 4):
            Question.objects.create(
                question_id=i, text=f'Soru {i}', answer=i,
                question_type='arithmetic', difficulty=1, batch_number=0
            )

    def _post_json(self, data):
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
