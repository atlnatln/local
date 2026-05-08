from .base import *

class EndToEndFlowTest(ThrottleMixin, AuthMixin, TestCase):
    """Tam kullanıcı döngüsü: kayıt → kredi kullan → soru al → ilerle → yenile."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='e2e-device', device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='E2E', education_period='sinif_2'
        )
        CreditBalance.objects.create(device=self.device, balance=1)
        # Ücretsiz soruları seed'le
        for i in range(1, 4):
            Question.objects.create(
                question_id=i, text=f'Q{i}', answer=i,
                question_type='arithmetic', difficulty=1, batch_number=0
            )
        self._auth_client(self.device)

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'AI1', 'answer': 1, 'type': 'a', 'difficulty': 2}
    ] * 50)
    def test_full_question_cycle(self, mock_gen):
        # 1. İlk kredi kullanım (ücretsiz)
        resp = self.client.post('/api/mathlock/credits/use/', {
            'device_token': str(self.device.device_token),
            'child_name': 'E2E',
            'stats': {},
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['is_free'])

        # 2. Soruları al
        resp = self.client.get(
            f'/api/mathlock/questions/?device_token={self.device.device_token}'
        )
        self.assertEqual(resp.status_code, 200)
        questions = resp.json()['questions']
        self.assertGreater(len(questions), 0)
        free_ids = [q['id'] for q in questions if q['source'] == 'free']
        ai_ids = [q['id'] for q in questions if q['source'] == 'ai']
        self.assertEqual(len(free_ids), 3)
        self.assertEqual(len(ai_ids), 50)

        # 3. Tüm soruları çöz (partial progress)
        all_ids = free_ids + ai_ids
        # Global ID'leri çöz
        resp = self.client.post('/api/mathlock/questions/progress/', {
            'device_token': str(self.device.device_token),
            'solved_questions': all_ids,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['auto_renewal_started'])

    @patch('credits.views._generate_levels_via_kimi', return_value=[
        {'id': i, 'title': f'S{i}'} for i in range(1, 4)
    ])
    def test_full_level_cycle(self, mock_gen):
        # 1. Seviyeleri al (ilk erişim → fallback oluşturur)
        resp = self.client.get(
            f'/api/mathlock/levels/?device_token={self.device.device_token}&child_id={self.child.pk}'
        )
        self.assertEqual(resp.status_code, 200)
        set_id = resp.json()['set_id']
        total_levels = resp.json()['total_levels']
        self.assertGreater(total_levels, 0)

        # 2. Tüm seviyeleri tamamla
        level_ids = list(range(1, total_levels + 1))
        resp = self.client.post('/api/mathlock/levels/progress/', {
            'device_token': str(self.device.device_token),
            'child_id': self.child.pk,
            'set_id': set_id,
            'completed_level_ids': level_ids,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['all_completed'])
        self.assertTrue(resp.json()['auto_renewal_started'])

        # 3. Yeni seviyelerin geldiğini doğrula (Celery task mock'lanmadı,
        #    bu yüzden doğrudan DB'den kontrol edemeyiz ama response yapısı doğru)
        self.assertIn('job_id', resp.json())

class CrossDeviceAuthorizationTest(ThrottleMixin, AuthMixin, TestCase):
    """Cihaz A'nın Cihaz B'nin verilerine erişememesi testleri."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device_a = Device.objects.create(
            installation_id='device-a', device_token=uuid.uuid4()
        )
        self.child_a = ChildProfile.objects.create(
            device=self.device_a, name='Ali', education_period='sinif_2'
        )
        CreditBalance.objects.create(device=self.device_a)
        self.device_b = Device.objects.create(
            installation_id='device-b', device_token=uuid.uuid4()
        )
        self.child_b = ChildProfile.objects.create(
            device=self.device_b, name='Veli', education_period='sinif_1'
        )
        CreditBalance.objects.create(device=self.device_b)

    def test_device_a_cannot_access_device_b_child_report(self):
        self._auth_client(self.device_a)
        resp = self.client.get(
            f'/api/mathlock/children/report/?device_token={self.device_a.device_token}&child_name=Veli'
        )
        self.assertEqual(resp.status_code, 404)

    def test_device_a_cannot_update_device_b_child(self):
        self._auth_client(self.device_a)
        resp = self.client.put('/api/mathlock/children/detail/', {
            'device_token': str(self.device_a.device_token),
            'child_id': self.child_b.pk,
            'new_name': 'Hacked',
        }, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_device_a_cannot_delete_device_b_child(self):
        self._auth_client(self.device_a)
        resp = self.client.delete('/api/mathlock/children/detail/', {
            'device_token': str(self.device_a.device_token),
            'child_id': self.child_b.pk,
        }, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_device_a_cannot_access_device_b_levels(self):
        LevelSet.objects.create(
            child=self.child_b, version=1,
            levels_json=[{'id': 1}], completed_level_ids=[]
        )
        self._auth_client(self.device_a)
        resp = self.client.get(
            f'/api/mathlock/levels/?device_token={self.device_a.device_token}&child_id={self.child_b.pk}'
        )
        self.assertEqual(resp.status_code, 404)

    def test_device_a_cannot_upload_device_b_stats(self):
        self._auth_client(self.device_a)
        resp = self.client.post('/api/mathlock/stats/', {
            'device_token': str(self.device_a.device_token),
            'child_name': 'Veli',
            'stats': {'totalCorrect': 10, 'totalShown': 10},
        }, format='json')
        self.assertEqual(resp.status_code, 404)

class InputValidationEdgeCaseTest(ThrottleMixin, AuthMixin, TestCase):
    """Kötü niyetli/bozuk input davranış testleri."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='input-val-device',
            device_token=uuid.uuid4(),
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        CreditBalance.objects.create(device=self.device)
        self._auth_client(self.device)

    def test_xss_in_child_name_sanitized(self):
        resp = self.client.post('/api/mathlock/children/', {
            'device_token': str(self.device.device_token),
            'name': '<script>alert(1)</script>',
            'education_period': 'sinif_2',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertNotIn('<script>', resp.json()['child']['name'])

    def test_sql_injection_in_child_name_ignored(self):
        resp = self.client.post('/api/mathlock/children/', {
            'device_token': str(self.device.device_token),
            'name': "'; DROP TABLE credits_childprofile; --",
            'education_period': 'sinif_2',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        # Tablo hâlâ var mı?
        self.assertTrue(ChildProfile.objects.filter(device=self.device).exists())

    def test_very_long_child_name_truncated(self):
        resp = self.client.post('/api/mathlock/children/', {
            'device_token': str(self.device.device_token),
            'name': 'A' * 500,
            'education_period': 'sinif_2',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertLessEqual(len(resp.json()['child']['name']), 100)

    def test_solved_questions_non_list_returns_400(self):
        resp = self.client.post('/api/mathlock/questions/progress/', {
            'device_token': str(self.device.device_token),
            'solved_questions': 'not-a-list',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_solved_questions_invalid_elements_returns_400(self):
        resp = self.client.post('/api/mathlock/questions/progress/', {
            'device_token': str(self.device.device_token),
            'solved_questions': ['abc', 'def'],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'AI1', 'answer': 1, 'type': 'a', 'difficulty': 1}
    ] * 50)
    def test_solved_questions_truncated_at_500(self, mock_gen):
        """500'den fazla ID gönderilirse sadece ilk 500 işlenmeli."""
        Question.objects.create(question_id=1, text='Q1', answer=1,
                                question_type='a', difficulty=1, batch_number=0)
        resp = self.client.post('/api/mathlock/questions/progress/', {
            'device_token': str(self.device.device_token),
            'solved_questions': list(range(1, 502)),
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        # 1 batch 0'da var, updated=1 olmalı; 501. eleman truncation nedeniyle işlenmez
        self.assertEqual(resp.json()['updated'], 1)

    def test_completed_level_ids_non_list_returns_400(self):
        resp = self.client.post('/api/mathlock/levels/progress/', {
            'device_token': str(self.device.device_token),
            'completed_level_ids': 'not-a-list',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_completed_level_ids_invalid_elements_returns_400(self):
        resp = self.client.post('/api/mathlock/levels/progress/', {
            'device_token': str(self.device.device_token),
            'completed_level_ids': ['abc'],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    @patch('credits.views._generate_via_kimi', return_value=[
        {'text': 'AI1', 'answer': 1, 'type': 'a', 'difficulty': 1}
    ] * 50)
    def test_negative_question_id_in_progress(self, mock_gen):
        Question.objects.create(question_id=1, text='Q1', answer=1,
                                question_type='a', difficulty=1, batch_number=0)
        resp = self.client.post('/api/mathlock/questions/progress/', {
            'device_token': str(self.device.device_token),
            'solved_questions': [-1, 1],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['updated'], 1)

    def test_register_invalid_locale_coerced(self):
        """Geçersiz locale kayıtta tr'ye coerce edilmeli."""
        resp = self.client.post('/api/mathlock/register/', {
            'installation_id': 'locale-coerce-001',
            'locale': 'xyz123',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        device = Device.objects.get(installation_id='locale-coerce-001')
        child = ChildProfile.objects.get(device=device)
        self.assertEqual(child.locale, 'tr')


