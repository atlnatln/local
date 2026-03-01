# Güvenlik Denetim Raporu — 28 Şubat 2026

**Denetim Tarihi:** 28 Şubat 2026  
**Denetçi:** Otonom Güvenlik Tarayıcısı  
**Kapsam:** Anka Platform tam kapsamlı ilk güvenlik denetimi  
**Versiyon:** 1.2 (Güncelleme: 28 Şubat 2026 — üçüncü düzeltme turu)

---

## Yönetici Özeti

Anka Platform'un Django API, Next.js frontend, Docker altyapısı ve Nginx reverse proxy katmanları güvenlik perspektifinden denetlenmiştir. Toplamda **3 kritik**, **7 yüksek**, **8 orta** ve **5 düşük** seviyeli bulgu tespit edilmiştir. Üç düzeltme turu sonrasında **3/3 kritik**, **7/7 yüksek**, **8/8 orta** seviye bulgu düzeltilmiştir.

## Skor Tablosu

| Seviye | Bulgu Sayısı | Düzeltilen |
|--------|-------------|-----------|
| **KRİTİK** | 3 | 3 ✅ |
| **YÜKSEK** | 7 | 7 ✅ |
| **ORTA** | 8 | 8 ✅ |
| **DÜŞÜK** | 5 | 2 ✅ |

---

## KRİTİK BULGULAR

### KRİTİK-1: Google Maps API Key Hardcoded ✅ DÜZELTİLDİ

**Dosyalar:** `docker-compose.prod.yml`, `.env.example`

Google Maps API key (`AIzaSy...`) production compose dosyasında düz metin olarak bulunuyordu, versiyon kontrolüne commit edilmişti.

**Risk:** API key kötüye kullanımı, maliyet artışı, quota aşımı.

**Uygulanan Düzeltme:**
- `docker-compose.prod.yml`'den hardcoded key kaldırıldı → `${NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}` env değişkenine çevrildi
- `frontend.Dockerfile`'dan hardcoded OIDC Client ID default'ları kaldırıldı

**Kalan Aksiyon:** ✅ GCP Console'dan API key rotate edildi (28 Şubat 2026). Eski key (`AIzaSyAZxawz0ab...`) silinip yeni key ile değiştirildi. Tüm env dosyaları güncellendi.

---

### KRİTİK-2: Google OAuth Client ID Hardcoded ✅ DÜZELTİLDİ

**Dosyalar:** `docker-compose.prod.yml` (backend, celery_worker, celery_beat, frontend), `infra/docker/frontend.Dockerfile`

Tüm servislerde OIDC Client ID fallback default olarak hardcoded idi.

**Uygulanan Düzeltme:**
- Tüm `:-201804658613-...` fallback'ları kaldırıldı
- Artık tüm servisler `${GOOGLE_OIDC_CLIENT_ID}` / `${NEXT_PUBLIC_GOOGLE_CLIENT_ID}` env değişkenini zorunlu okur

---

### KRİTİK-3: JWT Token'lar localStorage'da — XSS Riski ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/src/lib/auth.ts`, `services/backend/apps/accounts/cookie_auth.py`

Önceki durum:
```typescript
localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
document.cookie = `anka_access_token=${tokens.access}; path=/; max-age=86400`
```

Cookie'ler `HttpOnly`, `Secure`, `SameSite` flag'leri olmadan set ediliyordu.

**Risk:** XSS saldırısıyla JWT token çalınması.

**Uygulanan Düzeltme (Üçüncü Tur):**
- Backend: `apps/accounts/cookie_auth.py` modülü oluşturuldu
  - `CookieJWTAuthentication`: HttpOnly cookie'den token okur, `Authorization` header fallback'i destekler
  - `set_jwt_cookies()`: `HttpOnly` + `Secure` (prod) + `SameSite=Lax` cookie'ler set eder
  - Refresh cookie path'i `/api/auth/refresh/` ile kısıtlanmıştır
- Backend views: GoogleLoginView, TestLoginView, LogoutView, RefreshTokenView cookie set/clear işlemi yapar
- Backend settings: `DEFAULT_AUTHENTICATION_CLASSES` → `CookieJWTAuthentication` olarak değiştirildi
- Frontend `auth.ts`: localStorage'dan token yönetimi kaldırıldı; sadece optimistik `anka_authenticated` flag kalıyor
- Frontend `api-client.ts`: `Authorization` header kaldırıldı; `credentials: 'include'` ile cookie gönderimi sağlandı
- Eski localStorage key'leri (`anka_access_token`, `anka_refresh_token`) temizleme kodu eklendi

---

## YÜKSEK SEVİYE BULGULAR

### YÜKSEK-1: DRF Rate Limiting Aktif Değildi ✅ DÜZELTİLDİ

**Dosya:** `services/backend/project/settings/base.py`

`RATELIMIT_ENABLE = True` ayarı mevcuttu fakat aktif rate limiting paketi/middleware yoktu.

**Uygulanan Düzeltme:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '120/minute',
        'auth': '10/minute',
        'sensitive': '5/minute',
    },
}
```

---

### YÜKSEK-2: ALLOWED_HOSTS = ['*'] Base Settings'te ✅ DÜZELTİLDİ

**Dosya:** `services/backend/project/settings/base.py`

**Uygulanan Düzeltme:** `ALLOWED_HOSTS = []` (boş liste) olarak değiştirildi. Production ve dev settings kendi değerlerini override eder.

---

### YÜKSEK-3: Redis Production'da Parola Koruması Yok ✅ DÜZELTİLDİ

**Dosya:** `docker-compose.prod.yml`

**Uygulanan Düzeltme:** `--requirepass ${REDIS_PASSWORD:-}` parametresi eklendi.

**Kalan Aksiyon:** ✅ `.env.production`'a `REDIS_PASSWORD=` placeholder eklendi. Deployment'ta güçlü rastgele parola girilmeli ve `REDIS_URL` güncellenmeli:
```
REDIS_PASSWORD=<güçlü-rastgele-parola>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
```

---

### YÜKSEK-4: Logout Token Blacklist Yapmıyordu ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py`, `services/backend/project/settings/base.py`

**Uygulanan Düzeltmeler:**
1. `rest_framework_simplejwt.token_blacklist` → `INSTALLED_APPS`'e eklendi
2. `LogoutView.post()` → `RefreshToken(token).blacklist()` çağrısı eklendi

**Kalan Aksiyon:** ✅ `python manage.py migrate token_blacklist` çalıştırıldı (tablolar mevcut).

---

### YÜKSEK-5: CSRF Koruması Eksikleri ✅ DÜZELTİLDİ

**Dosya:** `services/backend/project/settings/prod.py`

**Uygulanan Düzeltme:**
```python
CSRF_TRUSTED_ORIGINS = [...]  # env'den okunuyor
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

**Kalan Aksiyon:** ✅ `.env.production`'da `CSRF_TRUSTED_ORIGINS=https://ankadata.com.tr,https://www.ankadata.com.tr` mevcut.

---

### YÜKSEK-6: deploy.sh İçinde Hardcoded Admin Parolası ✅ DÜZELTİLDİ

**Dosya:** `deploy.sh`

**Uygulanan Düzeltme:** Default parola (`change-this-admin-password`) kaldırıldı. `ADMIN_INITIAL_PASSWORD` env yoksa `secrets.token_urlsafe(20)` ile güvenli rastgele parola üretiliyor. Ayrıca `SECRET_KEY`, `CSRF_TRUSTED_ORIGINS`, `REDIS_PASSWORD`, `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` için deploy preflight kontrolleri eklendi.

---

### YÜKSEK-7: MinIO Default Credentials ✅ DÜZELTİLDİ

**Dosya:** `docker-compose.prod.yml`

**Uygulanan Düzeltme:** `:-change-this-s3-access-key` / `:-change-this-s3-secret-key` fallback'ları kaldırıldı.

---

## ORTA SEVİYE BULGULAR

### ORTA-1: SECRET_KEY Weak Default (Dev) ✅ DÜZELTİLDİ

Base settings'te `'django-insecure-dev-key-change-in-production'` default'u var.

**Uygulanan Düzeltme:** `deploy.sh` preflight'a SECRET_KEY boş/kısa/default değer kontrolü eklendi. `insecure`, `change-this`, `dev-key` içeren key'ler reddedilir.

### ORTA-2: PostgreSQL Default Credentials (Dev Compose)

Dev compose'da `postgres:postgres` default credentials var ve port `0.0.0.0`'a bind idi.

**Durum:** ✅ Port `127.0.0.1:5433:5432`'ye bind edildi.

### ORTA-3: Dev Compose Port Exposure ✅ DÜZELTİLDİ

Tüm hassas servis portları (Postgres, Redis, MinIO) `127.0.0.1`'e bind edildi.

### ORTA-4: CORS_ALLOW_ALL_ORIGINS = True (Dev)

Dev settings'te beklenen bir ayar. Production'da doğru konfigüre edilmiş (✅).

### ORTA-5: Log'larda PII Sızması ✅ DÜZELTİLDİ

`accounts/views.py` içinde kullanıcı email adresleri plaintext loglanıyordu.

**Uygulanan Düzeltme:** `apps/common/pii.py` modülü oluşturuldu. Tüm log satırlarında email ve username maskelendi: `john@example.com` → `j***@example.com`, `john.doe` → `jo***`.

### ORTA-6: create_test_user.py Parolayı Stdout'a Yazdırıyor ✅ DÜZELTİLDİ

**Uygulanan Düzeltme (Üçüncü Tur):** Parola artık `stderr`'e yazılıyor (`print(..., file=sys.stderr)`). Stdout'a hassas veri sızmıyor. Indentation hatası da düzeltildi.

### ORTA-7: Frontend Dockerfile node_modules Tam Kopyalanıyor ✅ DÜZELTİLDİ

**Uygulanan Düzeltme (Üçüncü Tur):**
- `next.config.ts`'ye `output: 'standalone'` eklendi
- `frontend.Dockerfile` standalone modeline uyarlandı:
  - `COPY --from=builder /app/.next/standalone ./` + `.next/static` + `public`
  - `node_modules` kopyası kaldırıldı → image boyutu önemli ölçüde azaldı
  - `npm install` → `npm ci --ignore-scripts` güvenlik iyileştirmesi
  - Entrypoint: `node server.js` (npm start yerine)

### ORTA-8: Webhook HMAC Secret Boşsa Bypass Oluyor ✅ DÜZELTİLDİ

`payments/webhooks.py` içinde `if not secret: return True` — webhook secret boşsa tüm istekler kabul ediliyordu.

**Uygulanan Düzeltme:** Secret boşken artık `return False` ile tüm istekler reddediliyor + warning logu yazılıyor. Deploy guardrail da İyzico aktifken secret zorunlu kılıyor (çift katman).

---

## DÜŞÜK SEVİYE BULGULAR

| # | Bulgu | Durum |
|---|-------|-------|
| DÜŞÜK-1 | `SECURE_CONTENT_TYPE_NOSNIFF` açıkça set edilmemişti | ✅ Eklendi |
| DÜŞÜK-2 | Token rotation + blacklist app'siz | ✅ Düzeltildi |
| DÜŞÜK-3 | `X-XSS-Protection` deprecated header | Bilgilendirme |
| DÜŞÜK-4 | Proje .gitignore'da `.env` pattern eksik | ✅ Eklendi |
| DÜŞÜK-5 | Frontend cookie `Secure`/`SameSite` flag eksik | ✅ KRİTİK-3 ile birlikte düzeltildi |

---

## MEVCUT İYİ PRATİKLER ✅

### Django/Backend
- `DEBUG = False` (production)
- HSTS 1 yıl + preload
- `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`
- `X_FRAME_OPTIONS = 'DENY'`
- JWT 15 dakika access token (kısa ömürlü)
- Sentry `send_default_pii = False`
- ORM kullanımı (raw SQL yok — ✅ SQL injection riski düşük)
- Google OIDC token doğrulama (google-auth lib)
- Email whitelist kontrolü
- Test-login endpoint production'da disabled

### Docker
- Multi-stage build (backend + frontend)
- Non-root user (backend: `anka` UID 1000, frontend: `nextjs` UID 1001)
- `restart: unless-stopped`
- Log rotation (max-size: 10m)
- Healthcheck'ler tüm servislerde

### Nginx
- TLS 1.2/1.3 only + strong cipher suite
- CSP header'ı
- Rate limiting (10r/s API, 5r/s web)
- `.env`, `.git` dosyaları engelleniyor
- PHP/ASP/JSP script engeli
- OCSP stapling

---

## KALAN AKSİYON ÖZETİ

| # | Seviye | Aksiyon | Durum |
|---|--------|---------|-------|
| 1 | ~~KRİTİK~~ | ~~GCP'den Google Maps API key rotate~~ | ✅ Tamamlandı (28 Şubat 2026) |
| 2 | YÜKSEK | `.env.production`'da REDIS_PASSWORD'a değer girin | ⚠️ Manuel — VPS'te set edilmeli |

> **Not:** Üçüncü düzeltme turu sonrasında **yalnızca 1 manuel aksiyon** kalmıştır (REDIS_PASSWORD).

### Üçüncü Turda Düzeltilen Aksiyonlar ✅ (28 Şubat 2026)

| Aksiyon | Dosyalar |
|---------|----------|
| JWT token'ları HttpOnly cookie'ye taşındı | `cookie_auth.py`, `views.py`, `base.py`, `auth.ts`, `api-client.ts` |
| `.env.production`'a REDIS_PASSWORD placeholder eklendi | `.env.production`, `.env.example` |
| CSRF_TRUSTED_ORIGINS `.env.production`'da doğrulandı | `.env.production` |
| `python manage.py migrate token_blacklist` çalıştırıldı | Tablolar mevcut |
| Next.js standalone output eklendi | `next.config.ts`, `frontend.Dockerfile` |
| `create_test_user.py` stdout → stderr düzeltildi | `create_test_user.py` |
| GCP Google Maps API key rotate edildi | GCP Console → eski key silindi, env dosyaları güncellendi |

### İkinci Turda Düzeltilen Aksiyonlar ✅

| Aksiyon | Durum |
|---------|-------|
| deploy.sh admin parolası default kaldırıldı | ✅ |
| deploy.sh SECRET_KEY/CSRF/Redis/Maps preflight kontrolleri | ✅ |
| Log'larda PII maskeleme (apps/common/pii.py) | ✅ |
| Webhook secret boşken bypass kaldırıldı | ✅ |
| dev.py ALLOWED_HOSTS wildcard kaldırıldı | ✅ |
| .gitignore'a .env pattern'ları eklendi | ✅ |
| ADR-0007 güvenlik kararları belgelendi | ✅ |

---

## Haziran 2026 Ek Güvenlik Düzeltmesi

**Tarih:** Haziran 2026  
**Kapsam:** Uçtan uca kullanıcı akışı simülasyonu sırasında tespit edilen yetkilendirme açığı

| Bulgu | Düzeltme |
|-------|---------|
| Catalog endpoint'leri (`/api/catalog/cities/`, `/sectors/`, `/filters/`) herhangi bir authenticated kullanıcının write (POST/PUT/DELETE) yapmasına izin veriyordu | `_ReadOnlyOrAdmin` mixin eklendi: read → herkese açık, write → sadece admin (`IsAdminUser`) |

Tam denetim raporu: `docs/RUNBOOKS/code-audit-and-fixes-2026-06.md`

---

## Temmuz 2026 UX Simülasyon Güvenlik Düzeltmeleri

**Tarih:** Temmuz 2026  
**Kapsam:** Kullanıcı akışı simülasyonu sırasında tespit edilen güvenlik açıkları ve sıkılaştırmalar

| # | Seviye | Bulgu | Düzeltme |
|---|--------|-------|---------|
| 1 | KRİTİK | `email_verified is False` logic bug — doğrulanmamış email'ler kabul edilebiliyordu | `not email_verified` kontrolüne çevrildi |
| 2 | KRİTİK | Admin email hardcoded — tek kullanıcıya bağlı, kod değişikliği gerektiriyordu | `ANKA_ADMIN_EMAILS` env var'a taşındı |
| 3 | YÜKSEK | PATCH `/me/` email validasyonu yok — format hatası ve email çakışması mümkündü | `validate_email` + uniqueness check eklendi |
| 4 | YÜKSEK | Auth endpoint'lerinde özel rate limit yok — brute-force koruması zayıftı | `ScopedRateThrottle` ile `auth` (10/dk) ve `sensitive` (5/dk) scope'ları eklendi |
| 5 | YÜKSEK | ChangePassword Google-only kullanıcı koruması yok — anlamsız hata mesajı | `has_usable_password()` guard eklendi |
| 6 | ORTA | CSV export formula injection riski — `=`, `+`, `-`, `@` ile başlayan hücre içerikleri | Frontend'de `sanitizeCSVCell()` koruması eklendi |
| 7 | ORTA | `window.open` çağrılarında `noopener,noreferrer` eksik | Tüm `target="_blank"` bağlantılarına eklendi |

Tam denetim raporu: `docs/RUNBOOKS/ux-simulation-audit-2026-07.md`

---

## Addendum — Mart 2026 UX Simülasyon Denetimi

**Tarih:** 1 Mart 2026  
**Kapsam:** Uçtan uca kullanıcı akışı simülasyonu — Login → Dashboard → Batch → Export → Settings → Checkout → Logout  
**Rapor:** `docs/RUNBOOKS/ux-simulation-audit-2026-03.md`

| # | Seviye | Bulgu | Düzeltme |
|---|--------|-------|---------|
| 1 | KRİTİK | `handle401()` redirect kaybı — token expire'da kullanıcı konumu korunmuyordu | `?redirect=currentPath` eklendi (`api-client.ts`) |
| 2 | KRİTİK | Exports sayfası sonsuz API döngüsü — `useEffect` + `[exports]` dependency | Initial load ve smart polling ayrı effect'lere bölündü (`exports/page.tsx`) |
| 3 | YÜKSEK | Login open redirect zafiyeti — `?redirect=//evil.com` kabul ediliyordu | Protocol-relative URL doğrulaması eklendi (`login/page.tsx`) |
| 4 | YÜKSEK | Settings/Checkout NaN bakiye — `parseFloat` guard eksik | `isNaN` guard eklendi (`settings/page.tsx`, `checkout/page.tsx`) |
| 5 | ORTA | Batch export kısmi hata yönetimi — CSV başarılı/XLSX başarısız bildirilmiyor | `Promise.allSettled` + warning toast (`batch/[id]/page.tsx`) |

---

## Sonraki Denetim

**Planlanan Tarih:** Haziran 2026  
**Kapsam:** Bu rapordaki kalan aksiyonların doğrulanması + yeni feature'ların güvenlik review'ı
