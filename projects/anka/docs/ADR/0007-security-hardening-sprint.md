# ADR-0007: Security Hardening Sprint (Şubat 2026)

- **Tarih:** 2026-02-28
- **Durum:** Kabul Edildi (Güncelleme: 28.02.2026 — Üçüncü Tur)
- **Karar Vericiler:** Proje ekibi

## Bağlam

Anka Platform ilk kapsamlı güvenlik denetiminden geçirildi. Django API, Next.js frontend, Docker altyapısı ve Nginx katmanları incelenerek 23 bulgu (3 kritik, 7 yüksek, 8 orta, 5 düşük) tespit edildi. Bu ADR, uygulanan güvenlik iyileştirmelerini ve mimari kararları belgelemektedir.

## Karar

Aşağıdaki güvenlik iyileştirmeleri tek sprint'te uygulandı:

### 1. Credential Yönetimi (Kritik)

**Sorun:** Google Maps API key, OAuth Client ID ve MinIO credential'ları `docker-compose.prod.yml` ve `frontend.Dockerfile` içinde hardcoded idi.

**Karar:**
- Tüm secret'lar compose dosyalarından kaldırıldı
- Fallback default'lar (`:-default-value`) production compose'dan çıkarıldı
- Tüm credential'lar **yalnızca** `.env.production` → `${ENV_VAR}` yoluyla okunuyor
- `.gitignore`'a `.env`, `.env.production`, `.env.*.local` pattern'ları eklendi

**Gerekçe:** Hardcoded secret'lar git geçmişine commit edildiğinde geri alınamaz. Env-only yaklaşım, secret'ları code repository'den tamamen ayırır.

### 2. JWT Token Blacklist (Yüksek)

**Sorun:** `rest_framework_simplejwt.token_blacklist` INSTALLED_APPS'te olmadığı için `BLACKLIST_AFTER_ROTATION: True` ayarı etkisizdi ve logout endpoint token'ı geçersiz kılmıyordu.

**Karar:**
- `token_blacklist` app INSTALLED_APPS'e eklendi
- `LogoutView` → `RefreshToken(token).blacklist()` çağrısı eklendi
- Migration çalıştırıldı: `python manage.py migrate token_blacklist` ✅

**Gerekçe:** Çalınan refresh token'ların 7 gün boyunca kullanılabilir olması kabul edilemez risk. Blacklist mekanizması bunu önler.

### 3. DRF Rate Limiting (Yüksek)

**Sorun:** `RATELIMIT_ENABLE = True` ayarı mevcuttu fakat DRF throttle sınıfları tanımlı değildi. Uygulama katmanında sıfır rate limiting.

**Karar:**
- `AnonRateThrottle` (30/dk) ve `UserRateThrottle` (120/dk) eklendi
- `auth` scope (10/dk) ve `sensitive` scope (5/dk) tanımlandı
- Nginx katmanındaki rate limiting (10r/s API, 5r/s web) ile birlikte çift katmanlı koruma sağlandı

**Gerekçe:** Nginx rate limiting IP bazlı; DRF throttling kullanıcı bazlı. Katmanlı yaklaşım her iki tehdidi karşılar.

### 4. CSRF Koruması (Yüksek)

**Sorun:** `CSRF_TRUSTED_ORIGINS`, `CSRF_COOKIE_SECURE`, `CSRF_COOKIE_HTTPONLY` production settings'te tanımlı değildi.

**Karar:** `prod.py`'ye eklendi:
```python
CSRF_TRUSTED_ORIGINS = [...]  # env'den
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### 5. PII Log Maskeleme (Orta → KVKK Uyumluluk)

**Sorun:** `accounts/views.py` içinde email ve username'ler plaintext loglanıyordu.

**Karar:**
- `apps/common/pii.py` modülü oluşturuldu: `mask_email()`, `mask_username()`, `hash_pii()`
- Tüm log satırlarında PII maskelendi: `john@example.com` → `j***@example.com`
- Sentry `send_default_pii = False` ayarı korundu

**Gerekçe:** KVKK Md. 12 gereği kişisel verilerin güvenliği sağlanmalı. Log'lar Docker volume'larda persist ediyor ve unauthorized erişime açık olabilir.

### 6. Webhook Güvenliği (Orta)

**Sorun:** İyzico webhook handler'da `IYZICO_WEBHOOK_SECRET` boşsa tüm istekler kabul ediliyordu (`return True`).

**Karar:** Secret boşken `return False` + warning log. Deploy guardrail zaten İyzico aktifken secret zorunlu kılıyor (çift katman).

### 7. Network Güvenliği (Orta)

**Sorun:** Dev compose'da tüm portlar (Postgres, Redis, MinIO) `0.0.0.0`'a bind idi.

**Karar:** Tüm hassas servis portları `127.0.0.1`'e bind edildi. Redis production'a `--requirepass` eklendi.

### 8. Deploy Preflight Sıkılaştırma

**Sorun:** `SECRET_KEY`, `CSRF_TRUSTED_ORIGINS`, `REDIS_PASSWORD`, `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` kontrolü yoktu. Admin parolası zayıf default kullanıyordu.

**Karar:**
- SECRET_KEY: boş/kısa/default değer kontrolü (exit 1)
- CSRF, Redis, Maps key: eksikse warning
- Admin parolası: default kaldırıldı → `ADMIN_INITIAL_PASSWORD` env yoksa `secrets.token_urlsafe(20)` üretilir

### 9. ALLOWED_HOSTS Sıkılaştırma

- `base.py`: `ALLOWED_HOSTS = []` (wildcard kaldırıldı)
- `dev.py`: `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '[::1]']`
- `prod.py`: env'den okunuyor (değişiklik yok)

## Alternatifler (Değerlendirildi / Ertelendi)

| Alternatif | Karar | Neden |
|------------|-------|-------|
| pip-compile --generate-hashes | Ertelendi | CI pipeline kurulduğunda yapılacak |
| Trivy CI entegrasyonu | Ertelendi | GitHub Actions pipeline'ı henüz yok |

### Üçüncü Turda Uygulanan Kararlar (Önceden Ertelenmişti)

#### 10. JWT HttpOnly Cookie (Kritik → Kabul Edildi)

**Sorun:** JWT token'lar `localStorage`'da ve güvenlik flag'siz cookie'lerde saklanıyordu. XSS saldırısıyla token çalınma riski.

**Karar:**
- Backend: `apps/accounts/cookie_auth.py` modülü oluşturuldu
  - `CookieJWTAuthentication`: HttpOnly cookie'den token okur, `Authorization` header fallback destekler (Swagger/curl uyumu)
  - `set_jwt_cookies()`: `HttpOnly=True`, `Secure=True` (prod), `SameSite=Lax`
  - Refresh cookie path'i `/api/auth/refresh/` ile kısıtlanmıştır
- Frontend: `auth.ts`'den localStorage token yönetimi kaldırıldı; `api-client.ts`'de `credentials: 'include'` eklendi
- GoogleLoginView, TestLoginView, LogoutView, RefreshTokenView → cookie set/clear

**Gerekçe:** HttpOnly cookie'ler JavaScript'ten erişilemez, XSS ile token çalınmasını önler. `SameSite=Lax` ile CSRF korunur. Header fallback API istemcileri (Swagger, mobile app, curl) için geriye uyumluluk sağlar.

#### 11. Next.js Standalone Output (Orta → Kabul Edildi)

**Sorun:** Frontend Docker image'da tüm `node_modules` (yüzlerce MB) kopyalanıyordu.

**Karar:**
- `next.config.ts`'ye `output: 'standalone'` eklendi
- `frontend.Dockerfile` standalone modeline uyarlandı: `.next/standalone` + `.next/static` + `public` kopyalanıyor
- `npm install` → `npm ci --ignore-scripts` güvenlik iyileştirmesi
- Entrypoint: `node server.js`

**Gerekçe:** Standalone output yalnızca gerekli dosyaları içerir (∼50-100 MB vs ∼500+ MB). Daha küçük image = daha hızlı deploy + daha az attack surface.

#### 12. create_test_user.py Stdout Güvenliği (Orta → Kabul Edildi)

**Sorun:** Üretilen test parolası `stdout`'a basılıyordu. Docker log'larında veya CI çıktısında expose olabilir.

**Karar:** Parola `stderr`'e yazılıyor (`print(..., file=sys.stderr)`). `stdout`'a yalnızca durum bilgisi gider.

**Gerekçe:** stdout genellikle pipe edilir veya loglanır; stderr ise geçici diagnostic içindir ve görünmezliği daha yüksektir.

## Sonuçlar

- Yeni servis/endpoint eklenirken `docs/SECURITY/api-security-policy.md` kontrol listesi kullanılmalı
- Her deploy öncesi `docs/SECURITY/hardening-checklist.md` gözden geçirilmeli
- Secret rotasyon takvimi `docs/SECURITY/secret-rotation-runbook.md` takip edilmeli
- 3 ayda bir güvenlik denetimi tekrarlanmalı
- Auth flow değişikliği: Tarayıcı oturumları artık HttpOnly cookie ile yönetilir; API istemcileri `Authorization: Bearer` header kullanmaya devam edebilir
- `token_blacklist` migration'ları çalıştırıldı ✅

## İlgili Belgeler

- `docs/SECURITY/` — Tüm güvenlik belgeleri
- `docs/RUNBOOKS/production-readiness-and-deploy-guardrails.md` — Deploy kontroller
- `docs/RUNBOOKS/secure-local-vps-access.md` — VPS erişim güvenliği
