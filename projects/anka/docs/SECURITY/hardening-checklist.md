# Sistem Sıkılaştırma Kontrol Listesi (Hardening Checklist)

**Son Güncelleme:** Temmuz 2026  
**Kullanım:** Her production deploy öncesi ve aylık güvenlik kontrolünde

---

## 1. Django / Backend Sıkılaştırma

### Kritik Ayarlar

| # | Kontrol | Beklenen | Dosya | Durum |
|---|---------|----------|-------|-------|
| 1 | `DEBUG = False` | `False` | `prod.py` | ✅ |
| 2 | `SECRET_KEY` env'den okunuyor | Non-default, 50+ karakter | `.env.production` | ✅ |
| 3 | `ALLOWED_HOSTS` kısıtlı | Sadece bilinen domain'ler | `prod.py` | ✅ |
| 4 | `SECURE_SSL_REDIRECT = True` | `True` | `prod.py` | ✅ |
| 5 | `SECURE_HSTS_SECONDS` ≥ 31536000 | 31536000 | `prod.py` | ✅ |
| 6 | `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | `prod.py` | ✅ |
| 7 | `SECURE_HSTS_PRELOAD` | `True` | `prod.py` | ✅ |
| 8 | `SESSION_COOKIE_SECURE` | `True` | `base.py` | ✅ |
| 9 | `SESSION_COOKIE_HTTPONLY` | `True` | `base.py` | ✅ |
| 10 | `CSRF_COOKIE_SECURE` | `True` | `prod.py` | ✅ |
| 11 | `CSRF_COOKIE_HTTPONLY` | `True` | `prod.py` | ✅ |
| 12 | `CSRF_TRUSTED_ORIGINS` tanımlı | Domain listesi | `prod.py` | ✅ |
| 13 | `X_FRAME_OPTIONS = 'DENY'` | `'DENY'` | `base.py` | ✅ |
| 14 | `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | `base.py` | ✅ |
| 15 | `CORS_ALLOW_ALL_ORIGINS` = False (prod) | `False` | `prod.py` | ✅ |
| 16 | Rate limiting aktif | DRF throttle config | `base.py` | ✅ |
| 17 | Token blacklist aktif | `INSTALLED_APPS` | `base.py` | ✅ |
| 18 | Sentry `send_default_pii = False` | `False` | `prod.py` | ✅ |
| 19 | DRF JSON-only renderer (prod) | `JSONRenderer` only | `prod.py` | ✅ |
| 20 | Password validators aktif | 4 validator | `base.py` | ✅ |
| 21 | JWT HttpOnly cookie auth | `CookieJWTAuthentication` | `base.py` | ✅ |
| 22 | PII log maskeleme | `mask_email()`, `mask_username()` | `accounts/views.py` | ✅ |
| 23 | Webhook secret boşken reject | `return False` | `webhooks.py` | ✅ |
| 24 | Google Maps API key rotated | Eski key silinip yeni key uygulandı | GCP Console + env dosyaları | ✅ |
| 25 | Admin email env var'dan | `ANKA_ADMIN_EMAILS` ile yapılandırılabilir | `base.py`, `.env` | ✅ |
| 26 | Auth endpoint ScopedRateThrottle | `auth` (10/dk), `sensitive` (5/dk) | `views.py` | ✅ |
| 27 | Email doğrulama (`not email_verified`) | None/missing güvenli kontrol | `views.py` | ✅ |
| 28 | PATCH `/me/` email validasyonu | Format + benzersizlik kontrolü | `views.py` | ✅ |
| 29 | Google-only kullanıcı şifre koruması | `has_usable_password()` guard | `views.py` | ✅ |
| 30 | CSV formula injection koruması | `sanitizeCSVCell()` — `=+\-@\t\r` | `batch/[id]/page.tsx` | ✅ |
| 31 | `window.open` noopener/noreferrer | Tüm `target="_blank"` bağlantılarında | Frontend geneli | ✅ |

### Deploy Öncesi Kontrol

```bash
# 1. Settings modülü doğru mu?
grep DJANGO_SETTINGS_MODULE docker-compose.prod.yml
# Beklenen: project.settings.prod

# 2. DEBUG kesinlikle False mu?
docker exec anka_backend_prod python -c "from django.conf import settings; print(settings.DEBUG)"
# Beklenen: False

# 3. SECRET_KEY default değil mi?
docker exec anka_backend_prod python -c "
from django.conf import settings
assert 'insecure' not in settings.SECRET_KEY.lower(), 'DEFAULT SECRET_KEY!'
print('OK: SECRET_KEY güvenli')
"

# 4. ALLOWED_HOSTS kontrol
docker exec anka_backend_prod python -c "
from django.conf import settings
assert '*' not in settings.ALLOWED_HOSTS, 'ALLOWED_HOSTS wildcard!'
print(f'OK: ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}')
"
```

## 2. Docker Sıkılaştırma

| # | Kontrol | Beklenen | Durum |
|---|---------|----------|-------|
| 1 | Non-root user | Backend: `anka` (1000), Frontend: `nextjs` (1001) | ✅ |
| 2 | Multi-stage build | Hem backend hem frontend | ✅ |
| 3 | Log rotation | `max-size: 10m`, `max-file: 3-5` | ✅ |
| 4 | Healthcheck tanımlı | Tüm servislerde | ✅ |
| 5 | `restart: unless-stopped` | Tüm prod servislerde | ✅ |
| 6 | DB/Redis portu expose yok (prod) | Internal network only | ✅ |
| 7 | Dev portlar localhost'a bind | `127.0.0.1:PORT:PORT` | ✅ |
| 8 | Redis `--requirepass` (prod) | Aktif | ✅ |
| 9 | Credential fallback yok (prod) | Default password kaldırılmış | ✅ |
| 10 | Docker image taraması | Trivy/Snyk CI'da | ⚠️ TODO |
| 11 | Frontend standalone output | `output: 'standalone'`, `node server.js` | ✅ |
| 12 | `npm ci --ignore-scripts` | Dockerfile'da `npm install` yerine | ✅ |

### Docker Image Güvenlik Taraması

```bash
# Trivy ile image taraması (CI pipeline'a ekleyin)
trivy image anka_backend_prod --severity HIGH,CRITICAL
trivy image anka_frontend_prod --severity HIGH,CRITICAL
trivy image postgres:14-alpine --severity HIGH,CRITICAL
```

## 3. Nginx / TLS Sıkılaştırma

| # | Kontrol | Beklenen | Durum |
|---|---------|----------|-------|
| 1 | TLS 1.2/1.3 only | `ssl_protocols TLSv1.2 TLSv1.3` | ✅ |
| 2 | Strong cipher suite | Modern cipher'lar | ✅ |
| 3 | HSTS header | 1 yıl + preload | ✅ |
| 4 | `X-Frame-Options: DENY` | Aktif | ✅ |
| 5 | `X-Content-Type-Options: nosniff` | Aktif | ✅ |
| 6 | CSP header | Aktif | ✅ |
| 7 | HTTP → HTTPS redirect | Aktif | ✅ |
| 8 | Rate limiting | API: 10r/s, Web: 5r/s | ✅ |
| 9 | `.env`, `.git` dosya engeli | `deny all` | ✅ |
| 10 | Script dosya engeli (PHP/ASP/JSP) | `deny all` | ✅ |
| 11 | OCSP stapling | Aktif | ✅ |
| 12 | Server version gizleme | `server_tokens off` | ✅ |

### SSL Test

```bash
# SSL Labs test (A+ beklenen)
# https://www.ssllabs.com/ssltest/analyze.html?d=ankadata.com.tr

# Yerel test
openssl s_client -connect ankadata.com.tr:443 -servername ankadata.com.tr </dev/null 2>/dev/null | openssl x509 -noout -dates
```

## 4. VPS / OS Sıkılaştırma

| # | Kontrol | Beklenen | Durum |
|---|---------|----------|-------|
| 1 | SSH Key-only auth | `PasswordAuthentication no` | ✅ |
| 2 | SSH root login disabled | `PermitRootLogin no` | ✅ |
| 3 | UFW firewall aktif | Sadece 22, 80, 443 | ✅ |
| 4 | Fail2ban aktif | SSH + Nginx jails | ⚠️ Kontrol et |
| 5 | Otomatik security updates | `unattended-upgrades` | ⚠️ Kontrol et |
| 6 | Disk şifreleme | LUKS (tercihli) | Opsiyonel |
| 7 | Log forwarding | Centralized logging | ⚠️ TODO |

### UFW Kontrol

```bash
sudo ufw status verbose
# Beklenen:
# 22/tcp    ALLOW IN    Anywhere
# 80/tcp    ALLOW IN    Anywhere
# 443/tcp   ALLOW IN    Anywhere
# Default: deny (incoming)
```

## 5. Bağımlılık Güvenliği

| # | Kontrol | Araç | Sıklık |
|---|---------|------|--------|
| 1 | Python zafiyet taraması | `pip-audit` veya `safety` | Her deploy |
| 2 | Node.js zafiyet taraması | `npm audit` | Her deploy |
| 3 | Docker image taraması | `trivy` | Her deploy |
| 4 | SBOM (Software Bill of Materials) | `syft` | Aylık |

```bash
# Python
pip-audit -r services/backend/requirements.txt

# Node.js
cd services/frontend && npm audit --production

# Docker
trivy image anka_backend_prod
```

## 6. Monitoring / Gözlemleme

| # | Kontrol | Araç | Durum |
|---|---------|------|-------|
| 1 | Error tracking | Sentry | ✅ (opsiyonel DSN) |
| 2 | Infrastructure metrics | Prometheus | ✅ |
| 3 | Log aggregation | Promtail/Loki | ✅ |
| 4 | Uptime monitoring | External ping | ⚠️ TODO |
| 5 | Security alerts | ops-bot/sec-agent | ✅ |

## 7. Backup ve DR (Disaster Recovery)

| # | Kontrol | Beklenen | Durum |
|---|---------|----------|-------|
| 1 | Otomatik DB backup | Günlük | ⚠️ Kontrol et |
| 2 | Backup şifreleme | AES-256 | ⚠️ TODO |
| 3 | Offsite backup | Farklı lokasyon veya S3 | ⚠️ TODO |
| 4 | Restore test | Aylık | ⚠️ TODO |
| 5 | RTO (Recovery Time Objective) | < 4 saat | Belgelenmeli |
| 6 | RPO (Recovery Point Objective) | < 24 saat | Belgelenmeli |

### Backup Doğrulama

```bash
# PostgreSQL backup restore testi
docker exec anka_postgres_prod pg_dump -U anka_user anka_prod > /tmp/test_backup.sql
# Yeni container'da restore test:
# docker run --rm -v /tmp:/backup postgres:14-alpine psql -f /backup/test_backup.sql
```

## 8. Aylık Güvenlik Kontrolü Kontrol Listesi

Her ayın ilk haftasında aşağıdaki kontrolleri yapın:

```
[ ] Django settings kontrolü (yukardaki tablo)
[ ] Docker image güvenlik taraması
[ ] pip-audit / npm audit çalıştırma
[ ] SSL sertifika son kullanma tarihi kontrolü
[ ] UFW kuralları gözden geçirme
[ ] Fail2ban log kontrolü (banned IP'ler)
[ ] Nginx access log anomali kontrolü
[ ] Sentry hata istatistikleri review
[ ] ops-bot/sec-agent rapor gözden geçirme
[ ] Backup restore testi
[ ] Secret rotasyon takvimi kontrolü
```
