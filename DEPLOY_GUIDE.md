# 🚀 Anka Production Deployment Guide

Bu döküman **Anka** projesinin `ankadata.com.tr` domain'i ve `89.252.152.222` IP adresi ile production ortamına deploy edilmesi için hazırlanmıştır.

## 📋 Gereksinimler

- Ubuntu/Debian VPS Server (89.252.152.222)
- Docker ve Docker Compose kurulu
- Domain DNS ayarları yapılmış
- Root/sudo erişimi

## 🏗️ Infrastructure Kurulumu

### 1. VPS Infrastructure Setup

```bash
# Infrastructure dizinine git
cd /home/akn/vps/infrastructure

# Ana reverse proxy'yi kur (SSL ile)
sudo ./setup.sh --ssl --monitoring
```

Bu komut:
- ✅ Ana nginx reverse proxy'yi kurar
- ✅ SSL sertifikalarını oluşturur
- ✅ Monitoring (Prometheus/Grafana) kurar
- ✅ Domain yönlendirmelerini aktifleştirir

### 2. DNS Ayarları

Domain sağlayıcınızda A kayıtları oluşturun:
```
ankadata.com.tr    → 89.252.152.222
www.ankadata.com.tr → 89.252.152.222
```

## 🚀 Anka Project Deployment

### 1. Production Environment Hazırla

```bash
cd /home/akn/vps/projects/anka

# .env.production dosyasını düzenle (güvenlik ayarları)
nano .env.production
```

**Kritik Değişiklikler:**
```bash
# Güçlü secret key oluştur
SECRET_KEY=your-very-strong-secret-key-min-50-chars

# Güvenli database şifresi
DB_PASSWORD=your-secure-database-password

# Email ayarları (production SMTP)
EMAIL_HOST_USER=noreply@ankadata.com.tr
EMAIL_HOST_PASSWORD=your-email-app-password

# Payment keys (production)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

### 2. SSL Sertifikalarını Kontrol Et

```bash
# SSL sertifikaları otomatik oluşmuş mu kontrol et
ls -la ssl/ankadata.com.tr/
# fullchain.pem ve privkey.pem olmalı
```

### 3. Production Deploy

```bash
# Production deployment başlat
./deploy.sh

# Eğer SSL atlanacaksa (HTTP-only)
./deploy.sh --skip-ssl

# Container'ları yeniden oluştur
./deploy.sh --force-recreate
```

## 🌐 Servis URLs

Deploy sonrası erişim noktaları:

| Servis | URL | Açıklama |
|--------|-----|----------|
| **Ana Site** | https://ankadata.com.tr | Next.js frontend |
| **API** | https://ankadata.com.tr/api/ | Django REST API |
| **Admin Panel** | https://ankadata.com.tr/admin/ | Django admin |
| **Health Check** | https://ankadata.com.tr/health/ | Sistem sağlık kontrolü |

## 👤 Default Admin

**İlk giriş bilgileri:**
- Username: `admin`
- Password: `change-this-admin-password`
- Email: `admin@ankadata.com.tr`

> ⚠️ **Güvenlik:** İlk girişten sonra şifreyi değiştirin!

## 🔧 Yönetim Komutları

### Container Yönetimi
```bash
# Durum kontrol
docker-compose -f docker-compose.prod.yml ps

# Logları izle
docker-compose -f docker-compose.prod.yml logs -f

# Sadece backend logları
docker-compose -f docker-compose.prod.yml logs -f backend

# Container'ı yeniden başlat
docker restart anka_backend_prod

# Tüm servisleri durdur
docker-compose -f docker-compose.prod.yml down
```

### Database Yönetimi
```bash
# Database backup
docker exec anka_postgres_prod pg_dump -U anka_user anka_prod > backup.sql

# Migrations çalıştır
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Static files topla
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Django shell
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
```

### SSL Yenileme
```bash
# Manuel SSL yenileme
sudo certbot renew

# Sertifikaları container'lara kopyala
sudo /usr/local/bin/update-anka-certs.sh
```

## 📊 Monitoring

### Prometheus & Grafana
- **Prometheus:** http://89.252.152.222:9090
- **Grafana:** http://89.252.152.222:3000
  - Username: `admin`
  - Password: `change-this-grafana-password`

### Nginx Status
- **Status:** http://89.252.152.222:8080/nginx-status
- **Health:** http://89.252.152.222:8080/nginx-health

## 🔒 Güvenlik Checklist

- [ ] Default admin şifresini değiştir
- [ ] SECRET_KEY'i güçlü yap
- [ ] Database şifresini güvenli yap
- [ ] Email SMTP ayarlarını yap
- [ ] Firewall kurallarını kontrol et (sadece 80, 443, 22)
- [ ] SSL sertifikalarının yenilendiğini kontrol et
- [ ] Backup sistemi kur
- [ ] Log monitoring kur

## 🐛 Sorun Giderme

### SSL Sorunları
```bash
# SSL sertifikası kontrol
openssl s_client -connect ankadata.com.tr:443

# Let's Encrypt logları
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Nginx configuration test
docker exec vps_nginx_main nginx -t
```

### Container Sorunları
```bash
# Tüm container'ları listele
docker ps -a

# Container loglarına bak
docker logs anka_backend_prod
docker logs anka_nginx_prod

# Container içine gir
docker exec -it anka_backend_prod bash
```

### Database Sorunları
```bash
# PostgreSQL bağlantısını test et
docker exec anka_postgres_prod pg_isready -U anka_user

# Database içine gir
docker exec -it anka_postgres_prod psql -U anka_user -d anka_prod
```

## 📞 Destek

Sorun yaşanması durumunda:

1. Logları kontrol edin
2. Container'ların sağlıklı çalıştığını doğrulayın
3. DNS ayarlarını kontrol edin
4. SSL sertifikalarının geçerliliğini kontrol edin

## 🎯 Production Optimizasyon

### Performance
- Redis cache aktif
- Gzip compression aktif
- Static files nginx üzerinden
- Database connection pooling
- Celery background tasks

### Security
- HTTPS zorunlu
- Security headers aktif
- Rate limiting aktif
- CSRF protection aktif
- SQL injection koruması

### Monitoring
- Health check endpoints
- Application logs
- System metrics
- Error tracking

---

✅ **Deploy tamamlandı!** Anka projesi https://ankadata.com.tr adresinde yayında! 🚀