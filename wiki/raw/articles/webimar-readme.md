---
title: "webimar-readme"
created: 2026-05-01
updated: 2026-05-01
type: raw
tags: [raw]
related: []
---


# Tarım İmar - Tarımsal Yapılaşma Hesaplama Sistemi

Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri sunan modern web uygulaması.

## Özellikler

- 🌾 **Kapsamlı Yapı Türleri**: Bağ evi, sera, hayvan barınağı, depo gibi 20+ farklı tarımsal yapı türü
- 📊 **Akıllı Hesaplamalar**: Bilimsel esaslara dayalı, mevzuata uygun hesaplamalar
- 🏗️ **3D Görselleştirme**: Gübre çukuru gibi yapıların 3D modellemesi
- 📚 **Mevzuat Entegrasyonu**: Güncel tarım mevzuatı ve yönetmelikler
- 🔒 **Güvenli Sistem**: HTML sanitization ve güvenlik önlemleri
- 📱 **Responsive Tasarım**: Mobil uyumlu modern arayüz

## Teknoloji Altyapısı

### Backend (Django).
- Django REST Framework
- PostgreSQL/SQLite veritabanı
- BeautifulSoup4 & Bleach (HTML sanitization)
- JWT authentication
- CORS desteği

### Frontend (Next.js)
- Next.js 15 (App Router)
- TypeScript
- Styled Components
- SEO optimizasyonu
- PWA desteği

### DevOps
- Docker & Docker Compose
- Nginx reverse proxy
- SSL/HTTPS desteği
- CI/CD pipeline

## Kurulum

### Gereksinimler
- Node.js 18+
- Python 3.8+
- Docker & Docker Compose

### Geliştirme Ortamı (Hibrit Akış)

Bu proje, hızlı geliştirme ve güvenli deployment için 3 aşamalı bir akış kullanır:

1. **Hızlı Geliştirme (Local Native):**
   Docker build beklemeden, kod değişikliklerini anında görmek için:
   ```bash
   ./dev-local.sh
   ```
   *Bu komut Django, Next.js ve React servislerini yerel ortamda başlatır.*

2. **Test & Önizleme (Local Docker):**
   Canlı ortama göndermeden önce Docker container'larını test etmek için:
   ```bash
   ./dev-docker.sh
   ```
   *Bu komut production benzeri bir Docker ortamını yerel bilgisayarınızda ayağa kaldırır.*

3. **Canlıya Gönderme (Deploy):**
   Testleri geçen kodu VPS sunucusuna göndermek için:
   ```bash
   ./deploy.sh
   ```

### Manuel Kurulum (Eski Yöntem)
```bash
# Projeyi klonlayın
git clone https://github.com/username/tarim-imar.git
cd tarim-imar

# Backend'i başlatın
cd webimar-api
pip install -r requirements.txt
python manage.py runserver

# Frontend'i başlatın
cd ../webimar-nextjs
npm install
npm run dev
```

## SEO Optimizasyonu

Proje aşağıdaki SEO özellikleriyle donatılmıştır:

- ✅ **Meta Tags**: Open Graph, Twitter Card, canonical URLs
- ✅ **Structured Data**: JSON-LD schema markup
- ✅ **Sitemap.xml**: Arama motoru indekslemesi için
- ✅ **Robots.txt**: Arama motoru yönergeleri
- ✅ **Performance**: Optimized images, lazy loading
- ✅ **Mobile-First**: Responsive tasarım

## Modüler Yapı

Proje modüler ve sürdürülebilir bir yapıya sahiptir:

### Bağ Evi Modülü v2.0 🆕
- **Ayrılmış endpoint**: `/api/calculations/bag-evi-v2/`
- **Backwards compatible**: Mevcut `/api/calculations/bag-evi/` endpoint korunmuştur
- **Test coverage**: Kapsamlı unit ve integration testleri
- **Monitoring**: Dedicated logging ve performance tracking

### API Versiyonlama
- **v1**: Legacy endpoints (tesisler.py)
- **v2**: Modular endpoints (specialized modules)
- **Graceful degradation**: Fallback sistemleri

## Mevzuat Desteği

- 5403 Sayılı Toprak Koruma ve Arazi Kullanımı Kanunu
- 3573 Sayılı Zeytinciliğin Islahı Kanunu
- Tarım Arazileri Kullanımı Genelgesi
- İBB Plan Notları
- Çevre ve Şehircilik Bakanlığı yönetmelikleri

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

- Website: https://tarimimar.com.tr
- Email: info@tarimimar.com.tr
- LinkedIn: [Tarım İmar](https://linkedin.com/company/tarim-imar)
