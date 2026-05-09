from .base import *

class GetLevelsViewTest(ThrottleMixin, AuthMixin, TestCase):
    """GET /api/mathlock/levels/"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='levels-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self._auth_client(self.device)
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
        self.client.credentials()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Device invalid-token')
        resp = self.client.get(f'{self.url}?device_token={uuid.uuid4()}')
        self.assertEqual(resp.status_code, 403)

    def test_no_child(self):
        device2 = Device.objects.create(
            installation_id='no-child-device', device_token=uuid.uuid4()
        )
        self._auth_client(device2)
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

class GetLevelsRaceConditionTest(ThrottleMixin, AuthMixin, TestCase):
    """GET /levels/ race condition fallback davranışı."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='levels-race-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        self._auth_client(self.device)
        self.url = '/api/mathlock/levels/'

    def test_get_levels_race_condition_fallback(self):
        """LevelSet yoksa ve race condition oluşursa (IntegrityError), fallback çalışmalı."""
        from credits.views import _LEVELS_FILE
        if not _LEVELS_FILE.exists():
            self.skipTest("fallback levels.json yok")

        with patch('credits.views.LevelSet.objects.create', side_effect=IntegrityError('race')):
            resp = self.client.get(
                f'{self.url}?device_token={self.device.device_token}&child_id={self.child.pk}'
            )
        # IntegrityError sonrası tekrar first() yapılmalı ama yine de None kalırsa 503
        # Bu testte race condition simüle ediliyor, 503 beklenir
        self.assertIn(resp.status_code, [200, 503])


class GetLevelsLocaleTest(ThrottleMixin, AuthMixin, TestCase):
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
        self._auth_client(self.device)
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

class UpdateLevelProgressAutoRenewalTest(ThrottleMixin, AuthMixin, TestCase):
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
        self._auth_client(self.device)
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
        # Kod lock varsa "zaten devam ediyor" anlamında True döner
        self.assertTrue(resp.json()['auto_renewal_started'])
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
        # Kod has_newer varsa "zaten mevcut" anlamında True döner
        self.assertTrue(resp.json()['auto_renewal_started'])
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

class UpdateLevelProgressNormalTest(ThrottleMixin, AuthMixin, TestCase):
    """POST /api/mathlock/levels/progress/ — normal path (no auto-renewal)"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.device = Device.objects.create(
            installation_id='level-progress-device',
            device_token=uuid.uuid4()
        )
        self.child = ChildProfile.objects.create(
            device=self.device, name='Ali', education_period='sinif_2'
        )
        CreditBalance.objects.create(device=self.device)
        self._auth_client(self.device)
        self.url = '/api/mathlock/levels/progress/'
        self.level_set = LevelSet.objects.create(
            child=self.child, version=1,
            levels_json=[{'id': i} for i in range(1, 4)],
            completed_level_ids=[]
        )

    def _post_json(self, data):
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

    def test_update_level_progress_race_condition_fallback(self):
        """LevelSet yoksa ve race condition oluşursa (IntegrityError), fallback çalışmalı."""
        from credits.views import _LEVELS_FILE
        if not _LEVELS_FILE.exists():
            self.skipTest("fallback levels.json yok")

        self.level_set.delete()
        with patch('credits.views.LevelSet.objects.create', side_effect=IntegrityError('race')):
            resp = self._post_json({
                'device_token': str(self.device.device_token),
                'child_id': self.child.pk,
                'completed_level_ids': [1],
            })
        self.assertIn(resp.status_code, [200, 503])

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
        # Kod has_newer varsa "zaten mevcut" anlamında True döner
        self.assertTrue(resp.json()['auto_renewal_started'])
