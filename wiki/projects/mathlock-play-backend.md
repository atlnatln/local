---
title: "MathLock Play — Backend"
created: 2026-05-07
updated: 2026-05-09
type: project
tags: [mathlock-play, backend, django, drf, api, tests]
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

**Sorun:** Eski app versiyonları ve edge case'lerde `DeviceTokenAuthentication` 403 dönüyordu.

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

---

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
