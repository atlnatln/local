---
title: "MathLock Play"
created: 2026-05-01
updated: 2026-05-03
type: project
tags: [mathlock-play, android, django, kotlin, python, systemd]
related:
  - infrastructure
  - deployment
  - sayi-yolculugu
sources:
  - raw/articles/mathlock-play-readme.md
---

# [[MathLock-Play]]

Çocukların telefonundaki uygulamalara erişimini eğitici matematik soruları ve oyunlarla kontrol eden Android uygulaması + Django backend.

## Purpose

Ebeveynler çocuklarının telefon kullanımını kilitleyebilir; çocuklar matematik soruları çözerek veya sayı tahmin oyunu oynayarak uygulamaları açabilir. AI destekli adaptif öğrenme sistemi.

## Stack

| Katman | Teknoloji |
|--------|-----------|
| Android App | Kotlin, Material Design 3, Target SDK 35 |
| Kilit Mekanizması | UsageStatsManager + Foreground Service |
| Backend | Django + Django REST Framework |
| Database | PostgreSQL (Docker) |
| Cache/Queue | Redis (Docker) |
| AI Pipeline | [[kimi-code-cli|kimi-cli]] (`kimi-for-coding`) |
| Deploy | systemd servisleri (host-based) |
| Crash Reporting | Firebase Crashlytics 18.6.4 |

## Authentication

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

### Android Tarafı

`AccountManager` cihaz kaydı yapar ve `device_token`'ı imzalı hale getirir. Her `ApiClient` instance'ına `setAuthToken()` ile atanır.

> **Önemli:** `SayiYolculuguActivity` kendi `RealApiClient()` instance'ını oluşturur. Bu instance'a da `apiClient.setAuthToken(accountManager.getAccessToken())` çağrısı yapılmalıdır, aksi halde tüm backend çağrıları `403 Forbidden` döner. Bkz. [[mathlock-play]] Sayı Yolculuğu Auth Fix bölümü.

## AI Soru Döngüsü

```
Telefon ← VPS: questions.json, levels.json, topics.json
Çocuk 50 soru çözer → stats.json VPS'e yüklenir
VPS: AI ([[kimi-code-cli|kimi-cli]]) yeni soru seti üretir → validate → DB
Telefon yeni seti indirir
```

## Entry Points

| Dosya/Dizin | Görev |
|-------------|-------|
| `projects/mathlock-play/app/src/main/...` | Android Kotlin kaynak kodu (Robotopia hariç) |
| `projects/mathlock-play/backend/` | Django backend |
| `projects/mathlock-play/website/` | Privacy policy, support sayfaları |
| `projects/mathlock-play/deploy.sh` | Build + data sync |
| `projects/mathlock-play/ai-generate.sh` | AI soru üretim pipeline'ı |
| `projects/mathlock-play/ai-generate-levels.sh` | AI bulmaca seviye üretim pipeline'ı (Sayı Yolculuğu) |

## Servisler (VPS)

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `mathlock-backend.service` | systemd | Django + Gunicorn (unix socket) |
| `mathlock-celery.service` | systemd | Celery worker |
| `mathlock_db` | Docker | PostgreSQL |
| `mathlock_redis` | Docker | Redis |

## Deploy

Backend host-based (systemd), DB/Redis Docker'da:
```bash
cd projects/mathlock-play/backend
pip install -r requirements.txt
sudo systemctl restart mathlock-backend mathlock-celery
```

## Backend Tests

Test suite'i 169 testten oluşur ve 10 modüle ayrılmıştır (~0.4s çalışma süresi).

### Test Yapısı

| Modül | Test Sayısı | Kapsam |
|-------|-------------|--------|
| `credits/tests/test_models.py` | — | Django model testleri |
| `credits/tests/test_auth.py` | — | `DeviceTokenSigner`, `DeviceTokenAuthentication` — süre aşımı, bozuk imza, eksik header, `AllowAny` bypass |
| `credits/tests/test_api_register.py` | — | Cihaz kaydı, locale, e-posta, health, paketler |
| `credits/tests/test_api_credits.py` | — | Kredi sorgulama, satın alma doğrulama, kredi kullanma, istatistik yükleme |
| `credits/tests/test_api_children.py` | — | Çocuk listesi, detay, raporlama |
| `credits/tests/test_api_questions.py` | — | Soru seti, ilerleme güncelleme (normal + otomatik yenileme) |
| `credits/tests/test_api_levels.py` | — | Seviye seti, seviye ilerlemesi (normal + otomatik yenileme) |
| `credits/tests/test_integration.py` | — | E2E akışlar (tam soru + seviye döngüleri), çapraz cihaz yetkilendirme izolasyonu, girdi doğrulama (XSS/SQLi/sanitasyon) |
| `credits/tests/test_unit.py` | — | Sanitasyon birim testi, iade ve rapor birim testleri, eski kilit temizliği, kredi düşme/kilit, yenileme kilidi serbest bırakma, throttle yapılandırma |
| `credits/tests/test_celery.py` | — | Celery task testleri |

### Paylaşılan Test Altyapısı

`credits/tests/base.py` ortak kullanım alanını sağlar:

```python
# file: projects/mathlock-play/backend/credits/tests/base.py
class AuthMixin:
    def _auth_client(self, device):
        signer = DeviceTokenSigner()
        signed = signer.sign(str(device.device_token))
        self.client.credentials(HTTP_AUTHORIZATION=f'Device {signed}')

class ThrottleMixin:
    def setUp(self):
        # DRF cache/SimpleRateThrottle cache temizliği
        cache.clear()
        # ...

NO_THROTTLE = {'DEFAULT_THROTTLE_CLASSES': [], 
               'DEFAULT_THROTTLE_RATES': {}}
```

Tüm kimlik doğrulama gerektiren API testleri `AuthMixin`'den miras alır ve `setUp`'ta `self._auth_client(self.device)` çağrır. `Device.credits` ilişkisi test setup'ında `CreditBalance` ile birlikte oluşturulur.

### Test Deseni: `DeviceTokenAuthentication`

Kimlik doğrulama testleri şu senaryoları kapsar:
- **Süre aşımı:** `max_age` sınırını aşan imzalı token → `403 Forbidden`
- **Bozuk imza:** `TimestampSigner` tarafından reddedilen token → `403 Forbidden`
- **Eksik header:** `Authorization` header'ı yoksa → anonim (izin verilen endpoint'lerde `AllowAny`)
- **Silinmiş cihaz:** `Device` veritabanından silinmişse → `403 Forbidden`
- **Çapraz cihaz izolasyonu:** Cihaz A'nın token'ı Cihaz B'nin kaynaklarına erişemez

## Dependencies

- [[infrastructure]] — nginx, SSL, mathlock.com.tr domain
- [[deployment]] — VPS deploy

## İçindeki Oyunlar

| Oyun | Tip | Backend | Açıklama |
|------|-----|---------|----------|
| Matematik Soruları | Native Kotlin | ✅ AI kredi sistemi | 50 soruluk setler, adaptif zorluk |
| Sayı Tahmin | Native Kotlin | ❌ Offline | 0-100 arası tahmin, tur bazlı |
| [[sayi-yolculugu]] | WebView (HTML5) | ✅ AI kredi sistemi | 12 seviyelik bulmaca setleri, Blockly benzeri mekanik |
| Sayı Hafızası | Native Kotlin | ❌ Offline | Kart eşleştirme, 3D flip animasyon, 4-20 çift |

> Robotopia (Blockly kodlama) artık bu projede değil. Bkz. [[robotopia-android]] ve [[adr-003-robotopia-extraction]].

## Crash Prevention (2026-05-02)

v1.0.67 sürümünde stabilite düzeltmeleri:
- **ProGuard:** Billing, Biometric, JS Bridge, MPAndroidChart için `keep` kuralları eklendi — release build R8 kırılmaları önlendi
- **WebView Memory Leak:** `SayiYolculuguActivity`'de `onDestroy()`'da `webView.destroy()` + `removeAllViews()` eklendi
- **Handler Leak:** `pollForNewSet()` recursive polling'i activity-level `Handler`'a taşındı; `onDestroy()`'da `removeCallbacksAndMessages(null)` ile temizleniyor
- **BootReceiver:** Android 14 `ForegroundServiceStartNotAllowedException` riski `try/catch` ile kapatıldı
- **Firebase Crashlytics:** `com.google.firebase:firebase-crashlytics:18.6.4` + Google Services plugin 4.4.4 entegre edildi

## Sayı Hafızası — Yeni Oyun (2026-05-03)

ADR: [[adr-004-memory-game-integration]]

- **Teknoloji:** Native Kotlin + `ObjectAnimator` 3D kart çevirme (`rotationY`)
- **Oyun mantığı:** `MemoryGameEngine.kt` (View'dan bağımsız, unit testli)
- **Kilit açma:** Ebeveyn ayarlı tur sayısı (`memoryGameRequiredRounds`)
- **Zorluk:** Ebeveyn ayarlı kart çifti (`memoryGamePairCount`, 4-20)
- **Backend:** Offline (sunucu bağımlılığı yok)
- **Test:** 27/27 unit test geçti, cihaz testi başarılı

## Sayı Yolculuğu Progress Bug Fix (2026-05-03)

**Sorun:** Kilit aktive olduktan sonra Sayı Yolculuğu baştan başlıyordu.

**Kök Nedenler (4 adet):**
1. `onDestroy()`'da `completedLevelIds` + `cachedLevels` siliniyordu
2. `currentSetId` persist edilmediği için `fetchLevels()` her açılışta "yeni set" olarak algılıyordu
3. `loadLevelsIntoGame()`'de `isNewSet` mantığı `oldSetId=null` iken `true` dönüyordu → `forceClear=true` → WebView progress siliyordu
4. Fallback levels'te `completed_level_ids` inject edilmiyordu

**Düzeltmeler:**
- `onDestroy()`'daki `SecurePrefs.remove()` kaldırıldı
- `currentSetId` `SecurePrefs`'e kaydediliyor (`KEY_CURRENT_SET_ID`)
- `fetchLevels()` ve `loadLevelsIntoGame()`'de `isNewSet` mantığı düzeltildi: `oldSetId != null` şartı eklendi
- Fallback levels'te `injectCompletedIds()` çağrılıyor, `forceClear=false`

## Sayı Yolculuğu Auth Fix (2026-05-03)

**Sorun:** `SayiYolculuguActivity` backend'e istek attığında `403 Forbidden` alıyordu.

**Kök Neden:** `SayiYolculuguActivity` kendi `RealApiClient()` instance'ını oluşturuyordu, ancak bu instance üzerinde `setAuthToken()` çağrılmamıştı. `AccountManager`'ın `apiClient`'ı ayrı bir instance'dı; `SayiYolculuguActivity`'nin client'ı yetkilendirilmemişti.

**Düzeltme:** Tüm ağ çağrıları öncesinde (`onCreate()`, `fetchLevels()`, `uploadLevelProgress()`) token alınıp `apiClient.setAuthToken()` ile atanır:

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/mathlock/.../SayiYolculuguActivity.kt
val accountManager = AccountManager(this)
apiClient.setAuthToken(accountManager.getAccessToken())

// Token refresh sonrası
token = accountManager.getAccessToken()
if (token.isNullOrBlank()) { token = accountManager.getOrRegister() }
apiClient.setAuthToken(token)
```

> Backend `?device_token=<uuid>` query parametresinden `Authorization: Device <signed_token>` header'ına geçmiştir. Android `AccountManager` zaten imzalı token üretiyordu, sadece yeni client instance'ına atanmamıştı.

## Backend Auth Backward Compatibility Fix (2026-05-03)

**Sorun:** Eski app versiyonları ve edge case'lerde `DeviceTokenAuthentication` 403 döndürüyordu.

**Kök Neden:** `DeviceTokenAuthentication` sadece `Authorization: Device <token>` header'ını okuyordu. Eski app versiyonları query param (`?device_token=...`) veya POST body (`{"device_token":...}`) ile token gönderiyordu.

**Düzeltme:** `DeviceTokenAuthentication`'a fallback mekanizmaları eklendi:

```python
# file: projects/mathlock-play/backend/credits/authentication.py
class DeviceTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        signed_token = None
        # 1. Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith(self.keyword + ' '):
            signed_token = auth_header[len(self.keyword) + 1 :].strip()
        # 2. Query param fallback
        if not signed_token:
            signed_token = request.query_params.get('device_token', '').strip()
        # 3. JSON body fallback
        if not signed_token:
            try:
                body = json.loads(request.body)
                signed_token = body.get('device_token', '').strip()
            except Exception:
                pass
        # ... verify token
```

**Test:** `test_auth.py`'ye 4 yeni test eklendi:
- `test_query_param_token_fallback`
- `test_json_body_token_fallback`
- `test_no_token_returns_403`

## Matematik Soruları child_id Mismatch Fix (2026-05-03)

**Sorun:** `get_questions` ve `update_progress` endpoint'leri `child_id` mismatch durumunda sessizce `child=None` olarak devam ediyordu. AI soru setleri kayboluyor, progress yetim kaydediliyordu.

**Kök Neden:** Levels endpoint'leri (`get_levels`, `update_level_progress`) 404 dönerken, questions endpoint'leri `ChildProfile.objects.filter(...).first()` kullanıyordu — bulunamayınca `None` dönüyordu.

**Düzeltme:** Her iki endpoint de artık explicit `child_id` verilmiş ama bulunamazsa `404 child_not_found` döner:

```python
# file: projects/mathlock-play/backend/credits/views.py
child_id = request.query_params.get('child_id')
if child_id:
    try:
        child = device.children.get(id=child_id)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_not_found')}, status=404)
else:
    child = device.children.filter(is_active=True).first() or device.children.first()
```

Bu, levels ile questions endpoint'leri arasında tutarlılık sağlar.

## AccountManager First-Run Auth Fix (2026-05-03)

**Sorun:** Uygulama ilk kez açıldığında (`getAccessToken()` boşsa) `AccountManager.getOrRegister()` raw `device_token` döndürüyordu. `Authorization: Device <raw_uuid>` header'ı backend tarafından `403 Forbidden` olarak reddediliyordu.

**Kök Neden:** `getOrRegister()` kayıt sonrası `access_token` (imzalı) değerini kaydediyor ama `return token` (raw) yazıyordu.

**Düzeltme:**

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/akn/mathlock/util/AccountManager.kt
val accessToken = response.body.optString("access_token", token)
prefs.edit()
    .putString(KEY_DEVICE_TOKEN, token)
    .putString(KEY_ACCESS_TOKEN, accessToken)
    .apply()
return accessToken  // ← önceki: return token (raw UUID)
```

Bu, `MathChallengeActivity`, `SettingsActivity`, `SayiYolculuguActivity` ve tüm `getOrRegister()` çağıranlar için geçerlidir.

## Sayı Yolculuğu child_id Retry Fix (2026-05-03)

**Sorun:** `fetchLevels()` ve `uploadLevelProgress()` `child_id` mismatch yüzünden 404 alıyordu; retry yoktu. `uploadLevelProgress` hata durumunda callback çağırmıyordu → kullanıcı set bitince yeni set alamıyordu.

**Kök Neden:** Telefonda kayıtlı `child_id` (örn. 67) ile backend'deki cihazın bağlı olduğu `child_id` (örn. 39) farklıydı. App yeniden yüklenince yeni cihaz kaydı oluşuyor, eski `child_id` localde kalıyordu.

**Düzeltmeler:**
- `fetchLevels()`: `child_id` ile 404 alırsa `child_id` olmadan tekrar dener; başarılı olursa local `activeChildId` sıfırlanır
- `uploadLevelProgress()`: Aynı retry mantığı + callback her durumda çağrılır (hata da olsa)

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/akn/mathlock/SayiYolculuguActivity.kt
private fun fetchLevels(): String? {
    fun tryFetch(withChildId: Boolean): String? { ... }
    var result = tryFetch(true)
    if (result == null && childId > 0) {
        result = tryFetch(false)
        if (result != null) prefManager.activeChildId = 0
    }
}
```

## Recent Commits

- `31c9a1db` chore(mathlock): bump version to 1.0.74 (74) (2026-05-03)
- `7153815b` fix(mathlock): retry levels/progress without child_id on 404, always invoke callback (2026-05-03)
- `d943f405` fix(mathlock): backward-compat auth for old app versions (query param + body token fallback) (2026-05-03)
- `fc45d056` feat(robotopia-android): create standalone project extracted from mathlock-play (2026-05-03)
- `9587a67a` chore(mathlock): bump version to 1.0.67 (67) (2026-05-02)
