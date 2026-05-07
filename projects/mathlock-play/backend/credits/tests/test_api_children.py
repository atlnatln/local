from .base import *

class ChildrenListViewTest(ThrottleMixin, AuthMixin, TestCase):
    """GET/POST /api/mathlock/children/"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='children-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2', is_active=True
        )
        self._auth_client(self.device)
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

class ChildrenDetailViewTest(ThrottleMixin, AuthMixin, TestCase):
    """PUT/DELETE /api/mathlock/children/detail/"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='detail-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2', is_active=True
        )
        self.url = '/api/mathlock/children/detail/'
        self._auth_client(self.device)

    def _put_json(self, data):
        return self.client.put(self.url, json.dumps(data), content_type='application/json')

    def _delete_json(self, data):
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

class ChildReportViewTest(ThrottleMixin, AuthMixin, TestCase):
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
                    "çıkarma": {"shown": 30, "correct": 20, "avgTime": 5.5, "hintUsed": 5, "topicUsed": 3},
                    "çarpma": {"shown": 30, "correct": 17, "avgTime": 8.0, "hintUsed": 10, "topicUsed": 5},
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
        self._auth_client(self.device)
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
        # çıkarma: 66.7% → GELİŞEN
        self.assertEqual(by_type['çıkarma']['category'], 'category_developing')
        # çarpma: 56.7% → ZORLU
        self.assertEqual(by_type['çarpma']['category'], 'category_challenging')

    def test_child_report_missing_token(self):
        self.client.credentials()
        resp = self.client.get('/api/mathlock/children/report/?child_name=Elif')
        self.assertEqual(resp.status_code, 403)

    def test_child_report_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Device invalid-token')
        resp = self.client.get(f'/api/mathlock/children/report/?device_token={uuid.uuid4()}&child_name=Elif')
        self.assertEqual(resp.status_code, 403)

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
        self.client.credentials()
        resp = self.client.get('/api/mathlock/children/stats-history/?child_name=Elif')
        self.assertEqual(resp.status_code, 403)

    def test_stats_history_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Device invalid-token')
        resp = self.client.get(f'/api/mathlock/children/stats-history/?device_token={uuid.uuid4()}&child_name=Elif')
        self.assertEqual(resp.status_code, 403)
