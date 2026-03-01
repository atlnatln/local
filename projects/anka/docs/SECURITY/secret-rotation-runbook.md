# Secret Rotation (Gizli Anahtar Rotasyonu) Runbook

**Son Güncelleme:** 28 Şubat 2026  
**Sahip:** DevOps  
**Rotasyon Periyodu:** 90 gün (kritik anahtarlar), 180 gün (diğerleri)

---

## 1. Secret Envanteri

| Secret | Dosya | Rotasyon Periyodu | Son Rotasyon |
|--------|-------|-------------------|-------------|
| `SECRET_KEY` (Django) | `.env.production` | 90 gün | — |
| `DB_PASSWORD` | `.env.production` | 90 gün | — |
| `REDIS_PASSWORD` | `.env.production` | 180 gün | — |
| `GOOGLE_PLACES_API_KEY` | `.env.production` | İhtiyaç halinde | — |
| `GOOGLE_MAPS_API_KEY` | `.env.production` | İhtiyaç halinde | — |
| `GOOGLE_OIDC_CLIENT_ID` | `.env.production` | İhtiyaç halinde | — |
| `IYZICO_API_KEY` | `.env.production` | 90 gün | — |
| `IYZICO_SECRET_KEY` | `.env.production` | 90 gün | — |
| `IYZICO_WEBHOOK_SECRET` | `.env.production` | 90 gün | — |
| `AWS_ACCESS_KEY_ID` (MinIO) | `.env.production` | 180 gün | — |
| `AWS_SECRET_ACCESS_KEY` (MinIO) | `.env.production` | 180 gün | — |
| `POSTMARK_SERVER_TOKEN` | `.env.production` | 180 gün | — |
| `SENTRY_DSN` | `.env.production` | İhtiyaç halinde | — |
| SSL sertifikaları | `ssl/` | 365 gün (Let's Encrypt: 90 gün) | — |

## 2. Django SECRET_KEY Rotasyonu

> ⚠️ SECRET_KEY değiştirildiğinde tüm mevcut JWT token'lar ve session'lar **geçersiz** olur. Kullanıcılar yeniden giriş yapmalıdır.

### Ön Hazırlık
```bash
# Yeni key oluştur
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Uygulama
```bash
cd /home/akn/vps/projects/anka

# 1. .env.production yedekle
cp .env.production .env.production.bak.$(date +%Y%m%d)

# 2. Yeni SECRET_KEY'i .env.production'a yaz
# SECRET_KEY=<yeni-key>

# 3. Servisleri sıralı restart et
docker compose -f docker-compose.prod.yml restart backend celery_worker celery_beat

# 4. Health check
curl -s https://ankadata.com.tr/api/health/ | jq .

# 5. Eski backup'ı temizle (7 gün sonra)
# rm .env.production.bak.*
```

### Doğrulama
```bash
# Backend log'larında hata yok mu?
docker logs anka_backend_prod --since="5m" | grep -i "error\|exception"

# API yanıt veriyor mu?
curl -s -o /dev/null -w "%{http_code}" https://ankadata.com.tr/api/health/
# Beklenen: 200
```

## 3. Veritabanı Parolası Rotasyonu

> ⚠️ Downtime gerektirir. Bakım penceresi planlayın.

```bash
cd /home/akn/vps/projects/anka

# 1. Yeni parola oluştur
NEW_DB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9!@#$%' | head -c 32)
echo "Yeni parola: $NEW_DB_PASS"

# 2. PostgreSQL'de parolayı değiştir
docker exec -it anka_postgres_prod psql -U anka_user -d anka_prod -c \
  "ALTER USER anka_user WITH PASSWORD '$NEW_DB_PASS';"

# 3. .env.production'ı güncelle
# DB_PASSWORD=<yeni-parola>

# 4. Tüm servisleri restart et (DB bağlantılarını yenile)
docker compose -f docker-compose.prod.yml restart backend celery_worker celery_beat

# 5. Doğrula
docker logs anka_backend_prod --since="2m" | grep -i "database\|connection"
```

## 4. Redis Parolası Rotasyonu

```bash
cd /home/akn/vps/projects/anka

# 1. Yeni parola oluştur
NEW_REDIS_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)

# 2. .env.production'ı güncelle
# REDIS_PASSWORD=<yeni-parola>
# REDIS_URL=redis://:<yeni-parola>@redis:6379/1

# 3. Tüm servisleri restart et
docker compose -f docker-compose.prod.yml restart redis backend celery_worker celery_beat

# 4. Doğrula
docker exec anka_redis_prod redis-cli -a "$NEW_REDIS_PASS" ping
# Beklenen: PONG
```

## 5. Google API Key Rotasyonu

```
1. GCP Console → APIs & Services → Credentials
2. Mevcut key'e "Restrict Key" uygulayın (HTTP Referer kısıtlaması):
   - ankadata.com.tr/*
   - localhost:3000/* (sadece dev key için)
3. Yeni key oluşturun ve kısıtlayın
4. .env.production'ı güncelleyin:
   - GOOGLE_PLACES_API_KEY=<yeni-key>
   - NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=<yeni-key>
5. Frontend'i rebuild edin (build-time env):
   docker compose -f docker-compose.prod.yml build --no-cache frontend
   docker compose -f docker-compose.prod.yml up -d frontend
6. Eski key'i 24 saat sonra GCP'den silin
```

## 6. İyzico API Key Rotasyonu

```
1. İyzico Merchant Panel → API Ayarları
2. Yeni API Key / Secret Key oluşturun
3. .env.production'ı güncelleyin:
   - IYZICO_API_KEY=<yeni-api-key>
   - IYZICO_SECRET_KEY=<yeni-secret-key>
4. Servisleri restart edin:
   docker compose -f docker-compose.prod.yml restart backend celery_worker
5. Test ödeme yapın (sandbox ortamda)
6. Eski key'i İyzico panelinden revoke edin
```

## 7. MinIO (S3) Credential Rotasyonu

```bash
# 1. Yeni credential'lar oluştur
NEW_ACCESS_KEY=$(openssl rand -hex 16)
NEW_SECRET_KEY=$(openssl rand -hex 32)

# 2. MinIO admin'e yeni kullanıcı ekle
docker exec anka_minio_prod mc admin user add local $NEW_ACCESS_KEY $NEW_SECRET_KEY

# 3. Policy ata
docker exec anka_minio_prod mc admin policy attach local readwrite --user=$NEW_ACCESS_KEY

# 4. .env.production'ı güncelle
# AWS_ACCESS_KEY_ID=<yeni-access-key>
# AWS_SECRET_ACCESS_KEY=<yeni-secret-key>

# 5. Servisleri restart et
docker compose -f docker-compose.prod.yml restart backend minio

# 6. Eski kullanıcıyı kaldır (24 saat sonra)
# docker exec anka_minio_prod mc admin user remove local <eski-access-key>
```

## 8. SSL Sertifika Yenileme

```bash
# Let's Encrypt / Certbot ile otomatik yenileme
certbot renew --dry-run  # Test
certbot renew             # Gerçek yenileme

# Manuel yenileme (gerektiğinde)
cd /home/akn/vps/infrastructure
bash setup-ssl.sh

# Nginx reload
docker exec vps_nginx_main nginx -s reload
```

## 9. Rotasyon Takvimi

| Ay | Aksiyon |
|----|---------|
| Mart, Haziran, Eylül, Aralık | SECRET_KEY, DB_PASSWORD, İyzico rotasyonu |
| Mart, Eylül | Redis, MinIO, Postmark rotasyonu |
| Her ay | SSL sertifika kontrol (certbot otomatik) |

## 10. Rotasyon Kaydı

Her rotasyon sonrası bu tabloya kayıt düşün:

| Tarih | Secret | Rotasyon Yapan | Doğrulama | Not |
|-------|--------|---------------|-----------|-----|
| — | — | — | — | — |
