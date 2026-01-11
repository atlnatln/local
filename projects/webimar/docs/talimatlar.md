# 🚀 Webimar Docker Deployment Talimatları

> **Son Güncelleme:** 8 Aralık 2025  
> **Önemli Değişiklik:** URL yapısı `/hesaplama/{yapi-turu}` formatından `/{yapi-turu}` formatına güncellendi.  
> Eski URL'ler otomatik olarak yeni formata redirect ediliyor.

## 📋 Proje Yapısı

```
webimar/
├── docker-compose.prod.yml    # Production Docker Compose
├── docker/
│   ├── Dockerfile.api         # Django API
│   ├── Dockerfile.react       # React SPA
│   ├── Dockerfile.nextjs      # Next.js SSG (Standalone)
│   ├── Dockerfile.nginx       # Nginx Reverse Proxy
│   └── nginx/
│       └── nginx.conf         # Nginx konfigürasyonu
├── ssl/                       # Let's Encrypt sertifikaları
│   ├── fullchain.pem
│   └── privkey.pem
├── webimar-api/               # Django Backend
├── webimar-react/             # React Frontend (Hesaplama)
├── webimar-nextjs/            # Next.js Frontend (Ana sayfa, SEO)
```

## 💻 Geliştirme Akışı (Hibrit Model)

Bu proje, geliştirme hızını artırmak ve deployment güvenliğini sağlamak için 3 aşamalı bir akış kullanır:

### 1. Hızlı Geliştirme (Local Native)
Docker build sürelerini beklemeden, kod değişikliklerini anında görmek için kullanılır.
```bash
./dev-local.sh
```
- **Avantajı:** Hızlı reload (HMR), anlık geri bildirim.
- **Çalışma Şekli:** Django, Next.js ve React servislerini yerel ortamda (native) başlatır.
- **Gereksinim:** Python venv ve Node.js modüllerinin yüklü olması gerekir.

### 2. Test & Önizleme (Local Docker)
Canlı ortama göndermeden önce, uygulamanın Docker içinde nasıl çalıştığını test etmek için kullanılır.
```bash
./dev-docker.sh
```
- **Avantajı:** Production ortamını birebir simüle eder.
- **Kullanım:** Yeni bir paket eklediğinizde veya Dockerfile değiştirdiğinizde mutlaka çalıştırın.

### 3. Canlıya Gönderme (Deploy)
Testleri geçen kodu VPS sunucusuna göndermek için kullanılır.
```bash
./deploy.sh
```
- **İşlevi:** Kodu GitHub'a pushlar, VPS'e bağlanır, pull eder ve container'ları yeniden build eder.

## 🌐 URL Yapısı

### Production (tarimimar.com.tr)
| URL | Servis | Açıklama |
|-----|--------|----------|
| https://tarimimar.com.tr/ | Next.js | Ana sayfa, SEO sayfaları |
| https://tarimimar.com.tr/ciceklenme-takvimi/ | Next.js | Çiçeklenme takvimi haritası |
| https://tarimimar.com.tr/api/ | Django | REST API |
| https://tarimimar.com.tr/admin/ | Django | Admin paneli |
| https://tarimimar.com.tr/{yapi-turu} | React | Hesaplama SPA (örn: /mantar-tesisi, /sera) |
| https://tarimimar.com.tr/hesaplama/* | Redirect | Eski URL'ler yeni formata yönlendirilir |

### Local Development
| URL | Servis |
|-----|--------|
| http://localhost:3000/ | Next.js (Ana sayfa, SEO) |
| http://localhost:3001/ | React SPA (Hesaplama) |
| http://localhost:8000/api/ | Django API |
| http://localhost:8000/admin/ | Django Admin |
| http://localhost/{yapi-turu} | React (Docker/Nginx üzerinden) |

## 🐳 Docker Komutları

### Production Container'larını Başlatma
```bash
# Tüm servisleri başlat
docker compose -f docker-compose.prod.yml up -d

# Belirli servisi başlat
docker compose -f docker-compose.prod.yml up -d nginx

# Logları izle
docker compose -f docker-compose.prod.yml logs -f

# Belirli servisin loglarını izle
docker compose -f docker-compose.prod.yml logs -f webimar-nextjs
```

### Container'ları Durdurma
```bash
# Tüm servisleri durdur
docker compose -f docker-compose.prod.yml down

# ÖNEMLİ: `-v/--volumes` kullanmayın.
# Bu komut DB volume'larını (örn: webimar_postgres_data) silebilir ve geri dönüşü yoktur.
```

### Yeniden Build
```bash
# Tüm servisleri yeniden build et
docker compose -f docker-compose.prod.yml build --no-cache

# Belirli servisi yeniden build et
docker compose -f docker-compose.prod.yml build --no-cache webimar-nextjs

# Build ve başlat
docker compose -f docker-compose.prod.yml up -d --build
```

### Container Yönetimi
```bash
# Container durumlarını görüntüle
docker compose -f docker-compose.prod.yml ps

# Container'a shell bağlan
docker exec -it webimar-nextjs sh
docker exec -it webimar-api bash

# Container'ı yeniden başlat
docker compose -f docker-compose.prod.yml restart webimar-nextjs
```

## 🚀 VPS Deployment

### Hızlı Deployment
```bash
# 1. Değişiklikleri commit ve push
git add .
git commit -m "Açıklama"
git push origin main

# 2. VPS'e bağlan ve güncelle
ssh akn@104.247.166.125
cd ~/webimar
git pull origin main

# 3. Gerekli servisi yeniden build et
docker compose -f docker-compose.prod.yml build --no-cache webimar-nextjs
docker compose -f docker-compose.prod.yml up -d

# 4. Durumu kontrol et
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f webimar-nextjs
```

### URL Yapısı Değişikliğinde Deployment (Nginx + React)
```bash
# Nginx config veya React routing değiştiyse
ssh akn@104.247.166.125
cd ~/webimar
git pull origin main

# Nginx ve React'i yeniden build et
docker compose -f docker-compose.prod.yml build --no-cache nginx webimar-react
docker compose -f docker-compose.prod.yml up -d

# Test: Eski URL'ler yeni URL'lere redirect oluyor mu?
curl -I https://tarimimar.com.tr/hesaplama/mantar-tesisi
# Beklenen: HTTP/2 301 → Location: https://tarimimar.com.tr/mantar-tesisi
```

### Tam Deployment (Sıfırdan)
```bash
# VPS'e bağlan
ssh akn@104.247.166.125

# Repo'yu güncelle
cd ~/webimar
git pull origin main

# SSL sertifikalarını kopyala (Let's Encrypt)
sudo cp /etc/letsencrypt/live/tarimimar.com.tr/fullchain.pem ~/webimar/ssl/
sudo cp /etc/letsencrypt/live/tarimimar.com.tr/privkey.pem ~/webimar/ssl/
sudo chown akn:akn ~/webimar/ssl/*.pem

# Tüm servisleri build et ve başlat
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Durumu kontrol et
docker compose -f docker-compose.prod.yml ps
```

## 🔧 Troubleshooting

### 502 Bad Gateway Hatası
```bash
# Container'ların çalıştığını kontrol et
docker compose -f docker-compose.prod.yml ps

# Container'ları yeniden başlat
docker compose -f docker-compose.prod.yml restart

# Nginx loglarını kontrol et
docker logs webimar-nginx --tail 50
```

### React Hydration Hatası
- `webimar-nextjs/next.config.js` dosyasında custom webpack config OLMAMALI
- `output: 'standalone'` mode kullanılmalı
- Container'ı yeniden build et

### GeoJSON/Harita Yüklenmiyor
```bash
# GeoJSON dosyalarının varlığını kontrol et
docker exec webimar-nextjs ls -la /app/public/turkey*.geojson

# Nginx üzerinden erişimi test et
curl -sI https://tarimimar.com.tr/turkey-districts.geojson
```

### SSL Sertifika Hatası
```bash
# Let's Encrypt sertifikalarını yenile
sudo certbot renew

# Sertifikaları Docker'a kopyala
sudo cp /etc/letsencrypt/live/tarimimar.com.tr/*.pem ~/webimar/ssl/
sudo chown akn:akn ~/webimar/ssl/*.pem

# Nginx'i yeniden başlat
docker compose -f docker-compose.prod.yml restart nginx
```

### Service Worker Cache Sorunu
Kullanıcıların eski cache'i temizlemesi için:
1. Tarayıcı DevTools → Application → Service Workers → Unregister
2. Application → Storage → Clear site data
3. Hard refresh: Ctrl+Shift+R

### URL Redirect Çalışmıyor
```bash
# Nginx config'i kontrol et
docker exec webimar-nginx cat /etc/nginx/nginx.conf | grep -A5 "hesaplama"

# Nginx'i yeniden yükle (restart yerine reload - zero downtime)
docker exec webimar-nginx nginx -s reload

# Test et
curl -I https://tarimimar.com.tr/hesaplama/sera
# Beklenen: 301 Moved Permanently
```

### Canonical Tag Sorunları
```bash
# React sayfasında canonical kontrol
curl -s https://tarimimar.com.tr/mantar-tesisi | grep -i canonical
# Beklenen: <link rel="canonical" href="https://tarimimar.com.tr/mantar-tesisi"/>

# Next.js sayfasında canonical kontrol
curl -s https://tarimimar.com.tr/ | grep -i canonical
# Beklenen: <link rel="canonical" href="https://tarimimar.com.tr"/>
```

## 📊 Servis Portları (Internal)

| Servis | Internal Port | External Port |
|--------|---------------|---------------|
| Nginx | 80, 443 | 80, 443 |
| Django API | 8000 | - |
| React | 3001 | - |
| Next.js | 3000 | - |
| PostgreSQL | 5432 | - (optional profile) |

## 🔐 SSL/HTTPS

### Let's Encrypt Otomatik Yenileme
```bash
# Cron job ekle (VPS'te)
sudo crontab -e

# Aylık yenileme ekle:
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/tarimimar.com.tr/*.pem /home/akn/webimar/ssl/ && docker compose -f /home/akn/webimar/docker-compose.prod.yml restart nginx
```

## 📝 Önemli Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `docker-compose.prod.yml` | Production container tanımları |
| `docker/nginx/nginx.conf` | Nginx reverse proxy ayarları |
| `webimar-nextjs/next.config.js` | Next.js konfigürasyonu (standalone mode) |
| `.env` | Django environment variables |
| `ssl/*.pem` | SSL sertifikaları |

## ✅ Checklist - Yeni Deployment

### Kod Deploy
- [ ] Git push yapıldı
- [ ] VPS'te git pull yapıldı
- [ ] Gerekli servisler rebuild edildi
- [ ] Container'lar healthy durumda

### Temel Kontroller
- [ ] HTTPS çalışıyor
- [ ] Ana sayfa yükleniyor (https://tarimimar.com.tr/)
- [ ] Çiçeklenme takvimi haritası çalışıyor
- [ ] API endpoint'leri çalışıyor
- [ ] Admin paneli erişilebilir

### URL Yapısı ve SEO
- [ ] Hesaplama sayfaları temiz URL'lerle açılıyor (örn: /mantar-tesisi)
- [ ] Eski /hesaplama/* URL'leri yeni formata redirect ediliyor
- [ ] Canonical tag'ler doğru (tarayıcı DevTools → Elements → head)
- [ ] 404 hatası olmayan sayfalar var mı kontrol et
- [ ] Sitemap.xml erişilebilir (https://tarimimar.com.tr/sitemap.xml)

### Fonksiyonel Testler
- [ ] Next.js ana sayfadan hesaplama butonları doğru URL'lere yönlendiriyor
- [ ] React SPA'da hesaplama formları çalışıyor
- [ ] Kullanıcı kayıt/giriş işlemleri çalışıyor
- [ ] Kayıtlı hesaplama geçmişi açılıyor
