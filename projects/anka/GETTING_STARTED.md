# 🚀 Anka Platform - Kurulum & Başlangıç Rehberi

## ✅ Tamamlandı!

Proje başarıyla kuruldu. Django backend ve Next.js frontend şu anda çalışıyor!

### 📍 Erişim Noktaları

| Servis | URL | Amaç |
|--------|-----|------|
| **Frontend** | http://localhost:3000 | Next.js ön yüz |
| **API** | http://localhost:8000/api | Django REST API |
| **Admin** | http://localhost:8000/admin | Django yönetim paneli |
| **API Docs** | http://localhost:8000/api/docs | Swagger/OpenAPI dokümantasyonu |
| **Health** | http://localhost:8000/api/health/ | API sağlık kontrolü |

---

## 📦 Kurulum Özeti

### 1. Virtual Environment
✅ Python 3.12 virtual environment oluşturuldu: `services/backend/venv`

### 2. Dependencies
✅ Tüm Python paketleri kuruldu:
- Django 6.0
- Django REST Framework 3.14
- drf-spectacular (OpenAPI schema)
- Celery 5.3 (async tasks)
- Redis, PostgreSQL client, vb.

### 3. Database
✅ SQLite database oluşturuldu (`db.sqlite3`)
✅ Tüm migrations uygulandı

### 4. Frontend
✅ npm packages kuruldu
✅ Next.js 15.5.9 dev server çalışıyor

---

## 🚀 Proje Başlatma

### Local Development (Recommended)
```bash
./dev-local.sh
```

Bu komut otomatik olarak:
- Backend (Django) port 8000'de başlar
- Frontend (Next.js) port 3000'de başlar
- Log dosyaları oluşturur (django.log, nextjs.log)

### Docker Development
```bash
./dev-docker.sh
```

Bütün servisleri (PostgreSQL, Redis, MinIO, vb.) containerda çalıştırır.

---

## ✅ Tek Komut Doğrulama

Repo root’ta uçtan uca hızlı doğrulama (backend test + OpenAPI contract + frontend lint/type-check/build):

```bash
chmod +x verify.sh
./verify.sh
```

### Manual Backend
```bash
cd services/backend
source venv/bin/activate
python manage.py runserver
```

### Manual Frontend
```bash
cd services/frontend
npm run dev
```

---

## 📋 Dosya Yapısı

```
/home/akn/anka/
├── services/
│   ├── backend/              # Django API
│   │   ├── venv/             # Virtual environment
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── project/settings/  # Django settings
│   │   ├── apps/             # Django apps (models, views, etc)
│   │   └── db.sqlite3        # Development database
│   │
│   └── frontend/             # Next.js Frontend
│       ├── app/              # App Router pages
│       ├── src/lib/          # Utilities, API client
│       └── package.json
│
├── dev-local.sh              # Local development starter
├── dev-docker.sh             # Docker development starter
├── setup.sh                  # Initial setup script
├── docker-compose.yml        # Docker services definition
└── .env.example              # Environment template
```

---

## 🔧 İlk Adımlar

### 1. Django Admin Paneli Erişim
```bash
# Admin user oluştur
cd services/backend
source venv/bin/activate
python manage.py createsuperuser
```

Sonra: http://localhost:8000/admin/

### 2. API Dokümantasyonu
http://localhost:8000/api/docs/ (Swagger/OpenAPI)

### 3. Database Model Kontrolü
```bash
cd services/backend
source venv/bin/activate
python manage.py shell
>>> from apps.accounts.models import User, Organization
>>> User.objects.all()
>>> Organization.objects.all()
```

### 4. Next.js Sayfaları
- http://localhost:3000 - Ana sayfa
- http://localhost:3000/login - Giriş sayfası
- http://localhost:3000/register - Hesap oluşturma
- http://localhost:3000/dashboard - Gösterge paneli (kimlik doğrulamadan sonra)

---

## 📊 Database

### Local Development
- **SQLite**: `services/backend/db.sqlite3`
- Dosya tabanlı, kurulum gerektirmez

### Production / Docker
- **PostgreSQL 14**: Container'da çalışır
- User: postgres
- Password: postgres
- Database: anka_db

`.env` dosyasını düzenleyerek değiştirebilirsiniz.

---

## 🛑 Servisleri Durdurma

### dev-local.sh ile başladıysa:
```bash
# Terminal'de Ctrl+C tuşuna basın
```

### Elle başladıysa:
```bash
# Backend
pkill -f "manage.py runserver"

# Frontend
pkill -f "npm run dev"
```

---

## 🐳 Docker ile Başlatma

```bash
# Başlat
./dev-docker.sh

# Logları göster
docker compose logs -f

# Status kontrol
docker compose ps

# Shell erişimi
docker compose exec backend bash
docker compose exec backend python manage.py shell

# Durdur
docker compose down
```

---

## 🔍 Troubleshooting

### Port 8000/3000 zaten kullanımda
```bash
# Port'u serbest bırak
fuser -k 8000/tcp
fuser -k 3000/tcp
```

### Virtual environment problem
```bash
cd services/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database errors
```bash
cd services/backend
rm db.sqlite3
python manage.py migrate --noinput
```

### Next.js port conflict
```bash
PORT=3001 npm run dev
```

---

## 📚 Sonraki Adımlar

1. **Model & Serializer**: DRF serializer'ları oluştur
2. **API Endpoints**: Django view'ları ve endpoints'leri implement et
3. **Frontend Integration**: Next.js'ten API'ye fetch çağrıları
4. **Authentication**: Session ve permission implementasyonu
5. **Testing**: Unit ve integration testleri yaz
6. **Celery Tasks**: Async job'ları configure et (opsiyonel)
7. **Production Deployment**: Gunicorn, Nginx, PostgreSQL setup

---

## 🔗 Referanslar

- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Next.js Docs](https://nextjs.org/docs)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [Project Architecture](./docs/ADR/0001-architecture-api-frontend-split.md)

---

## 💬 Destek

Proje klasöründe çalışırken:
```bash
# Django interactive shell
cd services/backend && source venv/bin/activate && python manage.py shell

# Database düzeyi operations
# SQLite viewer (VSCode extension önerilir)
```

---

**Tarih**: 10 Ocak 2026  
**Versiyon**: MVP-0  
**Durum**: ✅ Ready for Development
