%# MathLock Play — Test Durumu ve Geliştirme Planı

> **Tarih:** 26 Nisan 2026  
> **Kapsam:** Backend (Django), Android (Kotlin), E2E (ADB)

---

## 1. Mevcut Test Envanteri

### 1.1 Backend — `backend/credits/tests.py` (1.716 satır)

| Test Sınıfı | Test Sayısı | Durum | Notlar |
|-------------|-------------|-------|--------|
| `CreditBalanceModelTest` | 7 | ✅ Çalışır | `add_credits`, `use_credit`, `accuracy` |
| `RegisterDeviceViewTest` | 5 | ✅ Çalışır | Yeni cihaz, duplicate, child oluşturma |
| `GetCreditsViewTest` | 3 | ✅ Çalışır | Valid/invalid/missing token |
| `VerifyPurchaseViewTest` | 5 | ✅ Çalışır | Mock Google Play, duplicate token, invalid product |
| `UseCreditViewTest` | 4 | ✅ Çalışır | `@patch('_generate_via_kimi')` çalışır, Celery `.delay()` entegrasyonu test ediliyor |
| `UploadStatsViewTest` | 3 | ✅ Çalışır | Zorluk artışı/azalması |
| `HealthViewTest` | 1 | ✅ Çalışır | Basit 200 OK |
| `GooglePlayVerifyTest` | 3 | ✅ Çalışır | Mock service account |
| `GetPackagesViewTest` | 4 | ✅ Çalışır | DB vs settings fallback, inactive filter |
| `ChildReportViewTest` | 7 | ✅ Çalışır | Report + stats-history endpoint'leri |
| `RenewalLockModelTest` | 3 | ✅ Çalışır | unique_together, farklı content_type |
| `ChildProfileEducationPeriodTest` | 4 | ✅ Çalışır | Valid/invalid period coerce |
| `DeductCreditAndLockTest` | 8 | ✅ Çalışır | Atomic lock + deduct, expired lock, no credit |
| `ReleaseRenewalLockTest` | 3 | ✅ Çalışır | Silme, non-existent, type isolation |
| `UpdateProgressAutoRenewalTest` | 3 | ✅ Çalışır | `@patch('credits.views.generate_question_set')` mock'u ile düzeltildi |
| `UpdateLevelProgressAutoRenewalTest` | 5 | ✅ Çalışır | `@patch('credits.views.generate_level_set')` mock'u ile düzeltildi |
| `RegisterEmailViewTest` | 7 | ✅ Çalışır | Recovery, collision, credit transfer |
| `GetQuestionsViewTest` | 6 | ✅ Çalışır | Free + AI questions, global ID |
| `GetLevelsViewTest` | 5 | ✅ Çalışır | Set var/yok, fallback file |
| `ChildrenListViewTest` | 6 | ✅ Çalışır | CRUD, duplicate name, max children |
| `ChildrenDetailViewTest` | 5 | ✅ Çalışır | PUT name/period, DELETE last profile |
| `UpdateProgressNormalTest` | 4 | ✅ Çalışır | Partial progress, reset rotation |
| `UpdateLevelProgressNormalTest` | 4 | ✅ Çalışır | Partial progress, retry same level |

**Toplam:** 129 test  
**Kırık:** 0 test — tüm testler çalışır durumda  
**Eksik:** ~0 yeni test (Faz 2 tamamlandı)

### 1.2 Android Birim Testleri (~1.739 satır)

| Test Dosyası | Satır | Durum | Kapsam |
|--------------|-------|-------|--------|
| `SessionProgressTest.kt` | 639 | ✅ Güçlü | requiredCount, passScore, fallback, test/practice mode, regresyon |
| `SayiYolculuguGameEngineTest.kt` | 315 | ✅ Güçlü | Level geçiş, initGame, star calculation, tam akış |
| `CreditSystemTest.kt` | 246 | ✅ Güçlü | FakeQuestionSet, credit logic, JSON parse |
| `LockStateManagerTest.kt` | 333 | ✅ Güçlü | Unlock/relock, timer, parent bypass, active unlocks |
| `ChallengePickerUnlockPolicyTest.kt` | 115 | ✅ Güçlü | Hangi oyunlar kilit açabilir, pratik mod |
| `ApiClientContractTest.kt` | 91 | ✅ Güçlü | MockApiClient POST/GET/PUT/DELETE |

**Mevcut Android testleri:**
- `LocaleHelperTest.kt` — `setLocale` locale değişimi (tr/en/invalid), `getLocale` simülasyonu
- `PreferenceManagerLocaleTest.kt` — `appLocale` get/set simülasyonu, edge case'ler
- `SayiYolculuguPayloadTest.kt` — `initGame` payload (locale + forceClear)
- `PollForNewSetLogicTest.kt` — max attempts, interval, timeout, boundary conditions
- WebView JS — `I18N.t()` interpolasyon, `setLocale`, `initGame` forceClear (hâlâ eksik)

### 1.3 E2E Testleri — `test-e2e.sh` (403 satır)

| Test | Tip | Durum |
|------|-----|-------|
| Servis çalışıyor mu | ADB + `dumpsys` | ✅ |
| Shared preferences okunabiliyor mu | ADB + `run-as` | ✅ |
| Disclosure kabul | ADB + XML parse | ✅ |
| Timer sonrası davranış | ADB + manuel + logcat | ⚠️ Yarı otomatik |
| Ebeveyn bypass | Manuel | ⚠️ Tamamen manuel |
| Ön plan tespit | ADB + `dumpsys` | ✅ |
| Crash/ANR kontrolü | Logcat grep | ✅ |
| Play Store uyumluluk | Logcat + permission dump | ✅ |

---

## 2. Kritik Sorunlar

### 🔴 Sorun 1: Backend `.venv`'de Celery eksik
**Neden:** `requirements.txt`'te `celery[redis]` var ama `.venv` kurulumunda eksik.  
**Etki:** `python manage.py test credits` hiç çalışmıyor (`ModuleNotFoundError: No module named 'celery'`).  
**Çözüm:**
```bash
cd /home/akn/vps/projects/mathlock-play/backend
source .venv/bin/activate
pip install celery[redis]>=5.3 redis>=5.0
```

### 🔴 Sorun 2: `_run_in_background` mock testleri kırık
**Neden:** `credits/views.py`'de `_run_in_background()` fonksiyonu silindi, yerine `generate_level_set.delay()` ve `generate_question_set.delay()` kullanılıyor.  
**Etki:** 8 test başarısız olur:
- `UpdateProgressAutoRenewalTest` (3 test)
- `UpdateLevelProgressAutoRenewalTest` (5 test)
**Çözüm:** Testler `@patch('credits.tasks.generate_question_set.delay')` ve `@patch('credits.tasks.generate_level_set.delay')` kullanacak şekilde yeniden yazılacak.

### 🟡 Sorun 3: `_LEVELS_FILE` fallback testi dosya sistemine bağımlı
**Yer:** `GetLevelsViewTest.test_no_set_no_file`  
**Risk:** Test çalışma ortamına göre flaky olabilir (dosya var/yok durumu).

### 🟡 Sorun 4: Android testlerinde `testImplementation` sadece JUnit 4
**Risk:** Compose veya modern Android testing kütüphaneleri yok. Mevcut testler saf mantık testi (Context gerektirmez) — bu iyi, ama Activity/Fragment testi (Robolectric veya Espresso) yok.

---

## 3. Düzeltme Planı (Faz 1 — Kırık Testler)

### 3.1 Backend `.venv` onarımı
```bash
cd /home/akn/vps/projects/mathlock-play/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 `_run_in_background` → Celery `.delay()` geçişi

**Eski kod (tests.py satır 914):**
```python
@patch('credits.views._run_in_background')
def test_auto_renewal_triggered_when_all_solved(self, mock_bg):
    ...
    mock_bg.assert_called_once()
```

**Yeni kod:**
```python
@patch('credits.tasks.generate_question_set.delay')
def test_auto_renewal_triggered_when_all_solved(self, mock_delay):
    ...
    mock_delay.assert_called_once()
```

Aynı değişiklik `UpdateLevelProgressAutoRenewalTest` için de geçerli (`generate_level_set.delay`).

### 3.3 Celery task testleri (yeni sınıf)

```python
class CeleryTaskTest(TestCase):
    """generate_level_set ve generate_question_set task'larının doğrudan testi."""

    @patch('credits.tasks._generate_via_kimi')
    def test_generate_question_set_creates_db_record(self, mock_gen):
        ...

    @patch('credits.tasks._generate_levels_via_kimi')
    def test_generate_level_set_creates_db_record(self, mock_gen):
        ...

    def test_task_releases_lock_on_failure(self):
        """Task exception durumunda finally'de kilit serbest bırakılmalı."""
        ...
```

---

## 4. Yeni Test Ekleme Planı (Faz 2 — Eksik Kapsam)

### 4.1 Backend — i18n & Locale

| Test Sınıfı | Testler | Öncelik |
|-------------|---------|---------|
| `RegisterDeviceLocaleTest` | `locale='en'` ile kayıt → `ChildProfile.locale='en'`; default `'tr'`; invalid locale coerce | Yüksek |
| `GetLevelsLocaleTest` | `?locale=en` → `fallback-levels.en.json` kullanımı; `?locale=tr` → `fallback-levels.tr.json`; missing locale → `tr` | Yüksek |
| `GetQuestionsLocaleTest` | `?locale=en` query param parsing; `Accept-Language` header desteği | Orta |
| `GettextLazyResponseTest` | Error response'ları semantic key döndürüyor mu (`device_token_required` vs Türkçe çeviri) | Orta |

### 4.2 Backend — Celery & Jobs

| Test Sınıfı | Testler | Öncelik |
|-------------|---------|---------|
| `CeleryTaskTest` | Task success → DB kaydı + kilit serbest; Task failure → retry 3× + kredi iade + kilit serbest; Stale lock cleanup (`created_at__lt=very_old`) | Yüksek |
| `JobStatusEndpointTest` | `GET /jobs/{id}/status/` → PENDING/SUCCESS/FAILURE; Invalid job ID → 404 | Yüksek |

### 4.3 Backend — Stale Lock & TTL

| Test Sınıfı | Testler | Öncelik |
|-------------|---------|---------|
| `StaleLockCleanupTest` | 40 dk eski kilit `_deduct_credit_and_lock` içinde siliniyor mu; Yeni kilit (5 dk) silinmiyor | Yüksek |

### 4.4 Android — Locale & i18n

| Test Dosyası | Testler | Öncelik |
|--------------|---------|---------|
| `LocaleHelperTest.kt` | `setLocale(context, "en")` → configuration locale `en`; `setLocale(context, "tr")` → `tr`; Invalid locale → default | Yüksek |
| `PreferenceManagerLocaleTest.kt` | `appLocale` get/set; Default `"tr"`; Persist across instances | Orta |

### 4.5 Android — Sayı Yolculuğu Activity

| Test Dosyası | Testler | Öncelik |
|--------------|---------|---------|
| `SayiYolculuguActivityPayloadTest.kt` | `initGame` JSON'unda `locale` ve `forceClear` alanları var; `isNewSet=true` → `forceClear=true` | Orta |
| `PollForNewSetTest.kt` | 120 deneme limiti; 5 sn aralık; 10 dk timeout; `attempt >= 120` → error | Orta |

### 4.6 WebView JS — I18N (Node/Jest veya basit JS)

| Test Dosyası | Testler | Öncelik |
|--------------|---------|---------|
| `game-i18n.test.js` | `t('levelBadge', {n:5})` → `"Seviye 5"` (tr) / `"Level 5"` (en); Missing key fallback → `tr`; `setLocale('en')` + `renderUI()` | Düşük |

---

## 5. E2E Test Geliştirme Planı (Faz 3)

### 5.1 `test-e2e.sh` iyileştirmeleri

| Ekleme | Açıklama |
|--------|----------|
| `locale` testi | Telefon dilini `en` yap, uygulama aç, UI İngilizce mi kontrol et |
| Backend health check | `curl -f https://mathlock.com.tr/api/mathlock/health/` |
| Celery worker health | `docker exec mathlock_celery celery inspect ping` |
| Register with locale | Yeni cihaz kaydı `locale=en` → backend'de `ChildProfile.locale='en'` doğrula |

### 5.2 Yeni E2E senaryoları

```bash
# Yeni test modu: ./test-e2e.sh locale
test_locale_switch() {
    # Telefonu İngilizce yap (veya uygulama içinden değiştir)
    # Challenge ekranında "Solve" (en) vs "Çöz" (tr) kontrolü
}

# Yeni test modu: ./test-e2e.sh backend
test_backend_health() {
    curl -sf https://mathlock.com.tr/api/mathlock/health/ || fail
    curl -sf https://mathlock.com.tr/api/mathlock/packages/ || fail
}
```

---

## 6. CI/CD Entegrasyonu Önerisi (Faz 4 — İleri Vade)

### GitHub Actions Workflow (`.github/workflows/test.yml`)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
      redis:
        image: redis:7-alpine
    steps:
      - uses: actions/checkout@v4
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && python manage.py test credits --verbosity=2

  android-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - run: cd projects/mathlock-play && ./gradlew test

  e2e:
    runs-on: self-hosted  # Fiziksel cihaz gerektirir
    steps:
      - uses: actions/checkout@v4
      - run: cd projects/mathlock-play && ./test-e2e.sh all
```

---

## 7. Özet: Yapılacaklar Listesi

### Hemen (Bu hafta) ✅ Tamamlandı
- [x] `.venv`'ye Celery + Redis kurulumu
- [x] `UpdateProgressAutoRenewalTest` → `@patch('credits.views.generate_question_set')`
- [x] `UpdateLevelProgressAutoRenewalTest` → `@patch('credits.views.generate_level_set')`
- [x] `run-tests.sh` 129/129 PASS doğrulandı
- [x] `test_child_report_by_type_categories` regresyonu düzeltildi (`category_improving` → `category_developing`, `category_struggling` → `category_challenging`)
- [x] `CeleryTaskTest` duplicate `@override_settings` temizlendi

### Kısa vade (2 hafta) ✅ Tamamlandı
- [x] `RegisterDeviceLocaleTest` (backend)
- [x] `GetLevelsLocaleTest` (backend)
- [x] `CeleryTaskTest` — success, failure, retry, lock release (backend)
- [x] `JobStatusEndpointTest` (backend)
- [x] `StaleLockCleanupTest` (backend)
- [x] `LocaleHelperTest.kt` (Android) — MockK kullanılamadı (JVM target 1.8 kısıtlaması), simülasyon testi olarak güncellendi
- [x] `PreferenceManagerLocaleTest.kt` (Android) — MockK kullanılamadı, simülasyon testi olarak güncellendi

### Orta vade (1 ay) ✅ Tamamlandı
- [x] `SayiYolculuguPayloadTest.kt` (Android)
- [x] `PollForNewSetLogicTest.kt` (Android) — boundary conditions eklendi
- [ ] `game-i18n.test.js` (WebView) — hâlâ eksik
- [x] E2E locale + backend health check senaryoları
- [x] GitHub Actions backend test workflow — yollar düzeltildi

---

## Ek: Test Çalıştırma Komutları

```bash
# Backend (çalıştırmadan önce Celery kurulumu gerekli)
cd /home/akn/vps/projects/mathlock-play/backend
source .venv/bin/activate
python manage.py test credits --verbosity=2

# Android birim testleri
cd /home/akn/vps/projects/mathlock-play
./gradlew test

# E2E (fiziksel cihaz bağlı olmalı)
cd /home/akn/vps/projects/mathlock-play
./test-e2e.sh all
./test-e2e.sh timer
./test-e2e.sh compliance
```
