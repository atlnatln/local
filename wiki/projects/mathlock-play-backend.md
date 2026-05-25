---
title: "MathLock Play — Backend"
created: 2026-05-07
updated: 2026-05-25
type: project
tags: [mathlock-play, django]
related:
  - mathlock-play
  - mathlock-play-android
  - mathlock-play-ai
---

# MathLock Play — Backend

Django REST Framework tabanlı backend. Cihaz kimlik doğrulaması, kredi sistemi, çocuk profili yönetimi ve AI soru seti dağıtımı.

## Kimlik Doğrulama

Backend, cihaz bazlı token ile kimlik doğrulaması yapar.

### `DeviceTokenAuthentication`

DRF `BaseAuthentication` alt sınıfı. `Authorization: Device <signed_token>` header'ını bekler.

```python
# file: projects/mathlock-play/backend/credits/authentication.py
class DeviceTokenAuthentication(BaseAuthentication):
    keyword = 'Device'
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith(self.keyword + ' '):
            return None
        signed_token = auth_header[len(self.keyword) + 1:].strip()
        # TimestampSigner ile unsign
        # Device model'den lookup
        return (device, signed_token)
```

### `DeviceTokenSigner`

Django `TimestampSigner` ile UUID token'ı imzalar. Süre aşımı destekler.

```python
# file: projects/mathlock-play/backend/credits/authentication.py
from django.core.signing import TimestampSigner

class DeviceTokenSigner:
    signer = TimestampSigner()
    
    def sign(self, device_token):
        return self.signer.sign(device_token)
    
    def unsign(self, signed_token, max_age=None):
        return self.signer.unsign(signed_token, max_age=max_age)
```

## Backend Auth Backward Compatibility Fix (2026-05-03)

**Sorun:** Eski app versiyonları `DeviceTokenAuthentication`'da 403 dönüyordu.

**Düzeltme:** `authentication.py`'e query param ve JSON body fallback'leri eklendi. `test_auth.py`'ye 3 yeni test eklendi (query param, JSON body, no token).

## Matematik Soruları child_id Mismatch Fix (2026-05-03)

**Sorun:** `get_questions`/`update_progress` `child_id` mismatch'te sessizce `child=None` ile devam ediyordu.

**Düzeltme:** `views.py`'de explicit `child_id` verilmişse ve bulunamazsa `404 child_not_found` döner. Levels ile questions endpoint'leri arasında tutarlılık sağlar.

## Backend Tests

169 test, 10 modül, tümü passing (~0.4s).

| Modül | Kapsam |
|-------|--------|
| `test_models.py` | Django model testleri |
| `test_auth.py` | DeviceTokenSigner, DeviceTokenAuthentication |
| `test_api_register.py` | Cihaz kaydı, locale, e-posta, health |
| `test_api_credits.py` | Kredi sorgulama, satın alma, istatistik yükleme |
| `test_api_children.py` | Çocuk listesi, detay, raporlama |
| `test_api_questions.py` | Soru seti, ilerleme güncelleme |
| `test_api_levels.py` | Seviye seti, seviye ilerlemesi |
| `test_integration.py` | E2E akışlar, çapraz cihaz izolasyonu, girdi doğrulama |
| `test_unit.py` | Sanitasyon, iade, rapor, kredi düşme/kilit |
| `test_celery.py` | Celery task testleri |

`credits/tests/base.py` ortak `AuthMixin` + `ThrottleMixin` sağlar. Kimlik doğrulama testleri süre aşımı, bozuk imza, eksik header, silinmiş cihaz ve çapraz cihaz izolasyonunu kapsar.

> Android tarafı auth detayları için bkz. [[mathlock-play-android]]

## Cleanup — Dead Endpoints & CreditPackage Removal (2026-05-08)

**Kaldırılanlar:**
- `CreditPackage` modeli (`credits/models.py`) — hiçbir endpoint kullanmıyordu
- `GET /packages/` endpoint + view
- `GET /jobs/<id>/status/` endpoint + view
- `check_url` alanları response'dan kaldırıldı
- Django admin devre dışı bırakıldı (`INSTALLED_APPS`, `urls.py`, `admin.py`)

**Migration:** `0012_remove_creditpackage.py` — tabloyu kaldırır.

**Testler:** 165 test, 1.2s — tümü OK.

## validate-questions.py (2026-05-08)

Dönem bazlı soru seti doğrulama aracı. `scripts/validate-questions.py`:

| Kontrol | Açıklama |
|---------|----------|
| Tip dağılımı | `OPERATION_WEIGHTS` beklentisine uygunluk (±tolerance) |
| Zorluk aralığı | Döneme özgü min/max zorluk kontrolü |
| Duplicate | Tekrar eden soru metni kontrolü |
| ID/Code çakışması | Benzersizlik kontrolü |
| interactionMode | `text-input`, `tap-to-count`, `pattern-select`, `tap-to-choose` |

Tüm 5 dönem (`okul_oncesi` → `sinif_4`) için **PASS**.

## Backend Credits & Auth Güncellemeleri (2026-05-09)

### Değişen Modüller

| Dosya | Değişiklik |
|-------|------------|
| `credits/models.py` | Kredi modeli güncellemeleri (iade flag, state tracking) |
| `credits/views.py` | 503 response handling, credits refund flag, purchase verify retry desteği |
| `credits/authentication.py` | Raw device_token body/query param desteği (imzalı token ile birlikte) |
| `credits/tasks.py` | Celery task güncellemeleri (async işlem stabilitesi) |

### Yeni Testler

`credits/tests/` altına yeni test dosyaları eklendi:

- `test_credits_refund.py` — 503 durumunda credits refunded flag doğrulama
- `test_purchase_retry.py` — 409 retry loop senaryoları
- `test_device_token_raw.py` — Raw token + signed token dual-auth flow

### Raw Token + Signed Token Dual Auth

Android v1.0.77 ile birlikte backend, hem `Authorization: Device <signed_token>` header'ını hem de body/query param'daki raw `device_token`'ı kabul eder:

```python
# file: projects/mathlock-play/backend/credits/authentication.py
class DeviceTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        signed_token = None
        # 1. Authorization header (imzalı token)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith(self.keyword + ' '):
            signed_token = auth_header[len(self.keyword) + 1:].strip()
        # 2. Body/query param (raw token) — device lookup için
        raw_token = request.data.get('device_token') or request.query_params.get('device_token')
        # ... verify
```

### Deploy (2026-05-09)

VPS'e deploy edildi. `systemd` servisleri restart edildi:

```bash
sudo systemctl restart mathlock-backend mathlock-celery
```

> Son test durumu: 169+ test, tümü OK.
>
> **Repo Durumu:** MathLock Play artık `github.com/atlnatln/mathlock-play` adresinde ayrı repo olarak yönetiliyor. Backend kodu monorepo'dan çıkarıldı, `projects/mathlock-play/` `.gitignore`'a alındı.

## Switchable Level Generator (AI ↔ Procedural) (2026-05-11)

Seviye üretim backend'i artık iki generator arasında geçiş yapabilir. Default: **Procedural** (hızlı, deterministik, dış bağımlılık yok).

### Mimari

```
generate_level_set (dispatcher)
  ├─ LEVEL_GENERATOR=procedural → _generate_level_set_procedural()
  │     └─ python3 procedural-levels-v2.py --stats ... --output ... --version ... --seed ...
  └─ LEVEL_GENERATOR=ai         → _generate_level_set_ai()
        └─ bash ai-generate-levels.sh --vps-mode ...
```

### `procedural-levels-v2.py`

LLM kullanmadan procedural seviye üretimi:
- BFS ile çözülebilirlik garantisi
- 5 zorluk seviyesi, 13 duvar deseni, 5 operatör (`+`, `-`, `×`, `/`, `^`)
- 4 özel mekanik: kilit, teleport, restart, legendary seviyeler
- Cross-set duplicate prevention (fingerprint + title tracking)
- JSON çıktı: 12 seviye + metadata + ASCII harita

### Backend Değişiklikleri

| Dosya | Değişiklik |
|-------|------------|
| `credits/tasks.py` | `generate_level_set` dispatcher yapıldı; `_generate_level_set_procedural` ve `_generate_level_set_ai` ayrıldı |
| `credits/models.py` | `GenerationJob.generator` alanı eklendi (`ai` / `procedural`) |
| `mathlock_backend/settings.py` | `LEVEL_GENERATOR` ortam değişkeni eklendi |
| `credits/views.py` | `_build_level_stats` zenginleştirildi; `USE_PROCEDURAL` sabiti kaldırıldı |

### Zenginleştirilmiş Stats (`_build_level_stats`)

`level-stats.json` artık şunları da içeriyor:
- `questionAccuracy`: Çocuğun genel doğruluk oranı (`child.accuracy`)
- `strongTopics` / `weakTopics`: `stats_json.byType` analizinden çıkarılan konular (≥5 gösterim, ≥%80 doğru = güçlü; <%50 = zayıf)
- `completionRate`: Son setin tamamlama oranı
- `currentDifficulty`: `child.current_difficulty`

### Migration

`0015_generationjob_generator.py` — `GenerationJob` tablosuna `generator` alanı ekler.

---

## AI Üretim Mimarisi (v2 — Async Launcher + Poller)

2026-05-10'da Celery Worker SIGTERM sorununa kalıcı çözüm olarak mimari değişikliği yapıldı.

### Problem
Celery task `generate_level_set` senkron olarak `kimi-cli` çalıştırıyordu. Task 5–15 dk bloklanıyor, bu sürede worker SIGTERM alıyordu. Sonuç: yeni set hiçbir zaman oluşturulmuyordu.

### Çözüm: Fire-and-Forget Launcher + Periodic Poller

```
update_level_progress()
  └─ generate_level_set.delay()      ──► Celery task (5 sn)
        └─ subprocess.Popen()        ──► kimi-cli arka planda
              ├─ PID kaydet → GenerationJob (status='running')
              └─ Task hemen döner

poll_generation_jobs() (her 30 sn)
  └─ GenerationJob.objects.filter(status='running')
        ├─ PID hâlâ çalışıyor? → atla
        └─ PID bitti?
              ├─ output/levels.json oku → LevelSet oluştur
              └─ output yoksa → kredi iade et, status='failed'
```

### Yeni Model: `GenerationJob`

| Alan | Açıklama |
|------|----------|
| `child` | FK → ChildProfile |
| `content_type` | `'levels'` \| `'questions'` |
| `status` | `'pending'` → `'running'` → `'completed'` \| `'failed'` |
| `pid` | Subprocess PID |
| `temp_dir` | Geçici dizin (output JSON burada) |
| `credit_balance_pk` | Kredi iadesi için |
| `is_free` | Ücretsiz yenileme mi |

### Dosya Değişiklikleri

| Dosya | Değişiklik |
|-------|------------|
| `credits/models.py` | `GenerationJob` modeli eklendi |
| `credits/tasks.py` | `generate_level_set` / `generate_question_set` → launcher. `poll_generation_jobs` → poller |
| `credits/views.py` | `get_levels` response'a `generation_in_progress` flag'i eklendi |
| `mathlock_backend/settings.py` | `CELERY_BEAT_SCHEDULE` (30s), `CELERY_TASK_TIME_LIMIT=1800` |
| `SayiYolculuguActivity.kt` | `generation_in_progress` flag'i işleniyor, set tamamlanmışsa "hazırlanıyor" ekranı |

### Test Durumu

177 test, tümü OK. Yeni testler:
- `test_generate_level_set_creates_job`
- `test_poll_generations_completes_level_job`
- `test_poll_generations_refunds_on_failure`
- `test_poll_generations_skips_running_process`
- `test_renewal_actually_creates_new_level_set` (güncellendi)

### Deploy Adımları

```bash
cd /home/akn/local/projects/mathlock-play/backend
.venv/bin/python manage.py migrate
cd /home/akn/vps/projects/mathlock-play/backend
.venv/bin/python manage.py migrate
sudo systemctl restart mathlock-backend mathlock-celery
# Beat scheduler çalışmıyorsa:
sudo systemctl enable --now mathlock-celery-beat
```

> **Not:** `mathlock-celery-beat.service` yeni eklenmelidir (Celery beat için). Eğer yoksa systemd servis dosyası oluşturulmalı.

---

## Puzzles Queue & Throttle İyileştirmeleri (2026-05-25)

### `generate_puzzle_set` Celery Task

Yeni puzzle seti üretimi için ayrı Celery task eklendi. `puzzles` adlı yeni queue kullanılır.

```python
# credits/tasks.py
generate_puzzle_set.delay(child_id, ...)
```

**Celery servis yapılandırması:**
- Worker `--queues=celery,puzzles` ile çalıştırılır
- `mathlock-celery.service`'in `ExecStart` satırı güncellendi

### `register_device` Throttle Handling

`views.py`'de `register_device` endpoint'ine throttle uyumu eklendi:
- Throttle limit aşımında 429 dönüşü düzgün handle edilir
- Retry-after header'ı client'a iletilir

### `update_level_progress` İyileştirmeleri

- 200 OK + empty body durumunda callback leak düzeltildi (Android tarafı `onResponse` null body kontrolü eklendi)
- `auto_renewal_started` flag'i olmayan response'lar artık `showRenewalError()` ile handle edilir

## Adaptive Difficulty v2 — Sliding Window & Per-Topic Tracking (2026-05-25)

`upload_stats` artık kümülatif yerine son 30 soruluk kayan pencere (`recentDetails`) kullanır.

| Kural | Koşul | Eylem |
|-------|-------|-------|
| Zorluk +1 | Pencerede ≥10 gösterim, ≥%85 doğru | `current_difficulty += 1` |
| Zorluk -1 | Pencerede ≥10 gösterim, <%50 doğru | `current_difficulty -= 1` |

`byTypeDifficulty`: `stats_json` içinde konu başına zorluk takibi. Her konu ≥5 gösterimde kendi zorluğunu bağımsız ayarlar. `_build_child_stats` bu veriyi procedural generator'lara iletir.

Migration: `0021_alter_childprofile_current_difficulty.py` — `ChildProfile.current_difficulty` default `1` → `2`.

```python
# file: projects/mathlock-play/backend/credits/models.py
class ChildProfile(models.Model):
    current_difficulty = models.IntegerField(default=2)
```

## Procedural Generator Updates (2026-05-25)

| Değişiklik | Dosya | Açıklama |
|------------|-------|----------|
| `targetVal` zorunlu | `procedural_levels/generator/pipeline.py` | Zorluk ≥2'de her zaman `targetVal` (eskiden ≥3, %60 ihtimal). |
| 2D override | `procedural_levels/generator/pipeline.py` | `sinif_1`/`sinif_2` zorluk 4'te ZP/ZM yok, sadece 2D komutlar. |
| Fingerprint genişletildi | `procedural_levels/generator/fingerprint.py` | `startPos` + `targetPos` eklendi; zorluk-1 çakışması azaldı. |
| Okul öncesi plan | `procedural_levels/generator/difficulty.py` | `_FIRST_SET_PLANS["okul_oncesi"]` `[1×7, 2×4, 1]` → `[1×3, 2×9]`. |

## Question Set Builder — Period Difficulty Bands (2026-05-25)

`procedural_questions/core/config.py`'e `PERIOD_DIFFICULTY_BANDS` eklendi. Her eğitim dönemi için kolay/orta/zor zorluk listeleri map'lenir.

```python
# file: projects/mathlock-play/procedural_questions/core/config.py
PERIOD_DIFFICULTY_BANDS = {
    "okul_oncesi": {"easy": [1], "medium": [2], "hard": [3]},
    "sinif_1":     {"easy": [1, 2], "medium": [3], "hard": [4, 5]},
    # ... sinif_2 … sinif_4
}
```

`pipeline/builder.py`'deki `build()` artık bu mapping'i kullanır (eskiden `<=2`, `2<diff<=4`, `>=4`).

`procedural_questions/__main__.py`'deki `generate_question_set` fallback zorluk sırası: önce `byTypeDifficulty` (konu özel), sonra global `currentDifficulty`.

## Test Fixes — Obsolete Mock Patches (2026-05-25)

Test dosyalarındaki eski `@patch('credits.views._generate_via_kimi')` mock'ları procedural generator isimlerine güncellendi:

| Dosya | Yeni mock |
|-------|-----------|
| `test_api_credits.py` | `_generate_questions_procedural`, `generate_question_set` |
| `test_integration.py` | `generate_level_set` |

Ayrıca `Question.objects.create()` çift çağrılarından kaynaklanan `IntegrityError` düzeltildi.

---

## Çözülen Sorunlar

### Celery Worker SIGTERM (2026-05-10) ✅ ÇÖZÜLDÜ

**Kök neden:** Celery task senkron `kimi-cli` çalıştırıyordu, worker uzun süre bloklanıyordu.
**Çözüm:** Async launcher + poller mimarisine geçildi (yukarıda detaylı).
**Servis:** `mathlock-celery.service` + `mathlock-celery-beat.service`
