# 🏗️ TARIMIMAR PROJE MIMARISI
## Kuşbakışı Yapı Diyagramı & Geliştirici Rehberi

---

## 📊 GENEL MİMARİ DIYAGRAMI

```
                          ┌─────────────────────────────────────────┐
                          │     INTERNET (Ziyaretçiler)            │
                          │  https://tarimimar.com.tr               │
                          └────────────────┬────────────────────────┘
                                          │
                                          │ PORT 443/80 (HTTPS/HTTP)
                                          ▼
                    ╔═════════════════════════════════════════════╗
                    ║    DOCKER HOST (VPS)                        ║
                    ║    /home/akn/webimar/                       ║
                    ║                                             ║
                    ║  ┌────────────────────────────────────────┐ ║
                    ║  │  🔄 NGINX REVERSE PROXY                │ ║
                    ║  │  (webimar-nginx)                       │ ║
                    ║  │  Container: nginx:alpine               │ ║
                    ║  │  Port: 0.0.0.0:80/443                  │ ║
                    ║  │  File: docker/nginx/nginx.conf         │ ║
                    ║  │  SSL: /etc/nginx/ssl/ (Let's Encrypt)  │ ║
                    ║  └─────┬──────────┬──────────┬────────────┘ ║
                    ║        │          │          │               ║
        ┌───────────┴────────┘          │          │               ║
        │        ┌──────────────────────┘          │               ║
        │        │        ┌─────────────────────────┘               ║
        │        │        │                                        ║
        ▼        ▼        ▼                                        ║
    ╔═══════════════╗ ╔═══════════════╗ ╔════════════════╗       ║
    ║ DJANGO API    ║ ║ REACT SPA     ║ ║ NEXT.JS SSG    ║       ║
    ║ (webimar-api) ║ ║ (web-react)   ║ ║ (webimar-njs)  ║       ║
    ║───────────────║ ║───────────────║ ║────────────────║       ║
    ║ Python 3.11   ║ ║ Node.js       ║ ║ Node.js        ║       ║
    ║ Gunicorn      ║ ║ Build: Webpack║ ║ SSG + SSR      ║       ║
    ║ Port: 8000    ║ ║ Port: 3001    ║ ║ Port: 3000     ║       ║
    ║───────────────║ ║───────────────║ ║────────────────║       ║
    ║ /api/*        ║ ║ /hesaplama/*  ║ ║ /, /bag-evi/   ║       ║
    ║ /admin/       ║ ║ /auth/*       ║ ║ /sera/, ...    ║       ║
    ║ /calculations/║ ║ SPA Routes    ║ ║ SEO Pages      ║       ║
    ╚───────┬───────╝ ╚───────────────╝ ╚────────────────╝       ║
            │                                                      ║
            ▼                                                      ║
    ╔═══════════════════════════════════════════════════════╗    ║
    ║  DATA LAYER                                           ║    ║
    ║  ┌─────────────────────────────────────────────────┐  ║    ║
    ║  │ SQLite Database                                 │  ║    ║
    ║  │ /app/data/db.sqlite3                            │  ║    ║
    ║  │ (Host: /home/akn/webimar/db.sqlite3)            │  ║    ║
    ║  │ - Calculations model                            │  ║    ║
    ║  │ - User accounts                                 │  ║    ║
    ║  │ - Admin data                                    │  ║    ║
    ║  └─────────────────────────────────────────────────┘  ║    ║
    ║                                                        ║    ║
    ║  ┌─────────────────────────────────────────────────┐  ║    ║
    ║  │ Static Files Volume (api_staticfiles)           │  ║    ║
    ║  │ - Django admin CSS/JS                           │  ║    ║
    ║  │ - Served via nginx cache                        │  ║    ║
    ║  └─────────────────────────────────────────────────┘  ║    ║
    ║                                                        ║    ║
    ║  ┌─────────────────────────────────────────────────┐  ║    ║
    ║  │ Media Files Volume (api_media)                  │  ║    ║
    ║  │ - User uploads                                  │  ║    ║
    ║  │ - Reports                                       │  ║    ║
    ║  └─────────────────────────────────────────────────┘  ║    ║
    ║                                                        ║    ║
    ║  ┌─────────────────────────────────────────────────┐  ║    ║
    ║  │ SSL Certificates                                │  ║    ║
    ║  │ /etc/nginx/ssl/                                 │  ║    ║
    ║  │ - fullchain.pem (Let's Encrypt)                │  ║    ║
    ║  │ - privkey.pem                                   │  ║    ║
    ║  └─────────────────────────────────────────────────┘  ║    ║
    ╚═══════════════════════════════════════════════════════╝    ║
                                                                 ║
    ║ DOCKER NETWORK: webimar-network (bridge)                 ║
    ║ Internal DNS: servicename:port (örn: webimar-api:8000)   ║
    ╚═════════════════════════════════════════════════════════╝
```

---

## 📂 DOSYA YAPISI & CONTAINER MAPPING

```
/home/akn/webimar/
│
├── 🐳 DOCKER COMPOSE ORKESTRASYONU
│   ├── docker-compose.yml              # Ana compose dosyası (5 servis)
│   ├── .env                            # Environment variables
│   └── docker/
│       ├── nginx/
│       │   └── nginx.conf              # Nginx routing config
│       ├── Dockerfile.api              # Django API image build
│       ├── Dockerfile.react            # React SPA image build
│       └── Dockerfile.nextjs           # Next.js image build
│
├── 💾 BACKEND (Django/Python)
│   ├── webimar-api/                    # Main Django project
│   │   ├── Dockerfile                  # API Dockerfile
│   │   ├── db.sqlite3                  # SQLite Database
│   │   ├── requirements.txt            # Python packages
│   │   ├── manage.py                   # Django CLI
│   │   ├── webimar_api/                # Django settings
│   │   ├── calculations/               # Calculation app
│   │   ├── accounts/                   # User accounts
│   │   ├── static/                     # Static files
│   │   └── templates/                  # Django templates (admin)
│   │
│   └── [CONTAINER: webimar-api]
│       ├── Image: webimar:webimar-api
│       ├── Port: 8000:8001 (host:container)
│       ├── Process: gunicorn (4 workers)
│       ├── Volumes Mount:
│       │   ├── /app/staticfiles        → api_staticfiles volume
│       │   ├── /app/media              → api_media volume
│       │   └── /app/data/db.sqlite3    → api_database volume
│       ├── Network: webimar-network
│       └── Health: curl /api/calculations/health/
│
├── 🎨 FRONTEND - REACT SPA
│   ├── webimar-react/                  # React SPA project
│   │   ├── Dockerfile                  # React image
│   │   ├── public/                     # Static assets
│   │   ├── src/                        # React components
│   │   │   └── pages/hesaplama/        # Calculation pages
│   │   └── package.json                # Dependencies
│   │
│   └── [CONTAINER: webimar-react]
│       ├── Image: webimar:webimar-react
│       ├── Port: 3001 (internal only, exposed via nginx)
│       ├── Process: Node.js dev/prod server
│       ├── Build Args: REACT_APP_API_BASE_URL
│       ├── Network: webimar-network
│       └── Health: wget /health
│
├── 📄 FRONTEND - NEXT.JS SSG
│   ├── webimar-nextjs/                 # Next.js project
│   │   ├── Dockerfile                  # Next.js image
│   │   ├── pages/                      # SSG pages
│   │   │   ├── index.tsx               # / (Home)
│   │   │   ├── [slug].tsx              # /bag-evi, /sera, etc
│   │   │   └── documents/              # /documents/*
│   │   └── package.json
│   │
│   └── [CONTAINER: webimar-nextjs]
│       ├── Image: webimar:webimar-nextjs
│       ├── Port: 3000 (internal only, via nginx)
│       ├── Process: Next.js SSR server
│       ├── Build Args: NEXT_PUBLIC_API_BASE_URL
│       ├── Network: webimar-network
│       └── Health: wget /health
│
├── 🔀 REVERSE PROXY
│   ├── nginx-config-updated.conf       # Old config (backup)
│   │
│   └── [CONTAINER: webimar-nginx]
│       ├── Image: nginx:alpine
│       ├── Ports: 0.0.0.0:80/443       # Public facing
│       ├── Process: nginx
│       ├── Volumes Mount:
│       │   ├── /etc/nginx/nginx.conf   ← docker/nginx/nginx.conf
│       │   ├── /etc/nginx/ssl/         ← /home/akn/webimar/ssl/
│       │   └── /var/www/certbot/       ← /home/akn/webimar/certbot/www/
│       ├── Network: webimar-network
│       ├── Routing:
│       │   ├── /api/*              → webimar-api:8000
│       │   ├── /admin/             → webimar-api:8000
│       │   ├── /hesaplama/*        → webimar-react:3001
│       │   ├── /auth/*             → webimar-react:3001
│       │   ├── /              → webimar-nextjs:3000
│       │   └── /_next/*           → webimar-nextjs:3000
│       └── Health: /health
│
├── 🔐 SSL/SECURITY
│   ├── ssl/
│   │   ├── fullchain.pem            # Let's Encrypt fullchain
│   │   └── privkey.pem              # Private key
│   │
│   └── certbot/
│       └── www/                     # ACME challenge dir
│
└── ⚙️ KONFIGÜRASYON
    ├── .env                         # Environment variables
    └── docker-compose.yml           # Service orchestration
```

---

## 🔄 NGINX REQUEST ROUTING

```
REQUEST: https://tarimimar.com.tr/hesaplama/bag-evi/
         │
         ▼
    PORT 443 (HTTPS)
    SSL Termination
    │
    ▼
NGINX (webimar-nginx:80/443)
    │
    ├─ Match /hesaplama/ ?
    │   ▼ YES
    │   proxy_pass http://webimar-react:3001/
    │   Render React SPA
    │
    ├─ Match /api/* ?
    │   ▼ YES
    │   proxy_pass http://webimar-api:8000/api/
    │   Django REST API
    │
    ├─ Match /admin/ ?
    │   ▼ YES
    │   proxy_pass http://webimar-api:8000/admin/
    │   Django Admin Panel
    │
    ├─ Match /_next/* ?
    │   ▼ YES
    │   proxy_pass http://webimar-nextjs:3000/_next/
    │   Next.js Static Assets (cached 365d)
    │
    ├─ Match /bag-evi, /sera, etc (regex patterns) ?
    │   ▼ YES
    │   proxy_pass http://webimar-nextjs:3000
    │   Next.js SSG Pages
    │
    └─ DEFAULT (/)
        ▼
        proxy_pass http://webimar-nextjs:3000
        OR
        proxy_pass http://webimar-react:3001/
```

---

## 💾 DATABASE ARCHITECTURE

```
SQLITE3 DATABASE
│
├── 📊 TABLES (from Django Models)
│   │
│   ├── calculations_calculation
│   │   ├── id (PK)
│   │   ├── calculation_type (bag-evi, sera, etc)
│   │   ├── parameters (JSON data)
│   │   ├── results (calculated output)
│   │   ├── user (FK to auth_user)
│   │   └── created_at, updated_at
│   │
│   ├── auth_user
│   │   ├── id (PK)
│   │   ├── username
│   │   ├── email
│   │   ├── password (hashed)
│   │   └── groups (permissions)
│   │
│   ├── auth_group
│   │   ├── id (PK)
│   │   └── permissions (admin, user, etc)
│   │
│   ├── accounts_profile
│   │   ├── user (FK)
│   │   └── custom fields
│   │
│   └── django_session
│       ├── session_key
│       ├── session_data (encrypted)
│       └── expire_date
│
├── 📍 VOLUME PERSISTENCE
│   ├── Host Path: /home/akn/webimar/webimar-api/db.sqlite3
│   ├── Docker Volume: api_database
│   └── Container Path: /app/data/db.sqlite3
│       └─ Survives container restarts ✅
│
└── 🔄 MIGRATION FLOW
    ├── Docker build: python manage.py collectstatic
    ├── Container start: python manage.py migrate
    └── Ready: API can process requests
```

---

## 🐳 DOCKER COMPOSE ORKESTRASYONU

```yaml
# docker-compose.yml

services:
  ├─ webimar-nginx (GIRIŞ NOKTASI)
  │  ├─ Image: nginx:alpine
  │  ├─ Ports: 80, 443 (external)
  │  ├─ Volumes: nginx.conf, ssl/, certbot/
  │  └─ Depends on: api, react, nextjs
  │
  ├─ webimar-api (BACKEND)
  │  ├─ Build: ./webimar-api/Dockerfile
  │  ├─ Port: 8000 (internal)
  │  ├─ Env: DEBUG=False, SECRET_KEY, DATABASE_URL
  │  └─ Volumes: api_staticfiles, api_media, api_database
  │
  ├─ webimar-react (FRONTEND - SPA)
  │  ├─ Build: ./webimar-react/Dockerfile
  │  ├─ Port: 3001 (internal)
  │  ├─ Env: REACT_APP_API_BASE_URL
  │  └─ Routes: /hesaplama, /auth
  │
  ├─ webimar-nextjs (FRONTEND - SSG/SSR)
  │  ├─ Build: ./webimar-nextjs/Dockerfile
  │  ├─ Port: 3000 (internal)
  │  ├─ Env: NEXT_PUBLIC_API_BASE_URL
  │  └─ Routes: /, /bag-evi, /sera, /documents
  │
  ├─ postgres (OPTIONAL - disabled)
  │  ├─ Profile: with-postgres
  │  └─ Use: DATABASE_URL=postgresql://...
  │
  └─ redis (OPTIONAL - disabled)
     ├─ Profile: with-cache
     └─ Use: CACHING, SESSIONS

networks:
  └─ webimar-network (internal bridge)

volumes:
  ├─ api_staticfiles (Django static)
  ├─ api_media (User uploads)
  ├─ api_database (SQLite)
  ├─ postgres_data (if enabled)
  └─ redis_data (if enabled)
```

---

## 🚀 CONTAINER YAŞAM DÖNGÜSÜ

```
1. BUILD PHASE (docker compose build)
   └─ Her service için Dockerfile çalıştırılır
      ├─ Dependencies install (pip, npm)
      ├─ Code copy
      ├─ Django collectstatic
      └─ Image hazır

2. START PHASE (docker compose up -d)
   ├─ Network oluştur (webimar-network)
   ├─ Volumes oluştur
   ├─ nginx container başla (DEPENDS on api, react, nextjs)
   ├─ api container başla
   │  ├─ collectstatic çalıştır
   │  ├─ migrate çalıştır
   │  └─ gunicorn başla (8000 port listen)
   ├─ react container başla (build → serve)
   └─ nextjs container başla (build → serve)

3. HEALTHCHECK PHASE (30s interval)
   ├─ nginx: wget /health
   ├─ api: curl /api/calculations/health/
   ├─ react: wget /health
   └─ nextjs: wget /health

4. RUNNING PHASE
   └─ Containers restart: unless-stopped
      (otomatik restart on failure)

5. STOP PHASE (docker compose down)
   ├─ Containers stop (graceful)
   ├─ Network remove
   └─ Volumes persist (docker compose down -v ile silinir)
```

---

## 📡 TRAFFICFLOW - EXAMPLE: API CALL

```
User Browser (local)
    │
    ├─ REQUEST: GET /api/calculations/bag-evi/
    └─ HTTPS (TLS 1.3, Let's Encrypt cert)
        │
        ▼
VPS (tarimimar.com.tr)
    │
    ├─ PORT 443 (nginx-alpine)
    │  ├─ SSL Handshake
    │  ├─ Host header check: tarimimar.com.tr ✅
    │  ├─ Location match: /api/* ✅
    │  └─ Add headers:
    │     ├─ X-Forwarded-For: user_ip
    │     ├─ X-Forwarded-Proto: https
    │     └─ Authorization: token
    │
    ▼
webimar-api:8000 (gunicorn → Django)
    │
    ├─ URL routing: /api/calculations/bag-evi/
    ├─ View: CalculationViewSet
    ├─ Database query: SELECT * FROM calculations WHERE type='bag-evi'
    ├─ Serialize: JSON
    └─ RESPONSE: {"type": "bag-evi", "result": {...}, "status": 200}
        │
        ▼
nginx (proxy_pass response)
    │
    ├─ Headers:
    │  ├─ Content-Encoding: gzip
    │  ├─ Cache-Control: no-cache
    │  ├─ CORS: Access-Control-Allow-Origin: *
    │  └─ HSTS: max-age=63072000
    │
    ▼
User Browser (receive)
    │
    └─ Status: 200 OK
       Body: JSON response
       Time: ~200ms (network + processing)
```

---

## 🔍 DEVELOPMENT vs PRODUCTION

```
┌─────────────────────────────────────────────────────┐
│ DEVELOPMENT (Local Machine)                         │
├─────────────────────────────────────────────────────┤
│ npm run dev / python manage.py runserver            │
│ No Docker containers                                │
│ SQLite database (webimar-api/db.sqlite3)           │
│ Livereload enabled                                  │
│ DEBUG=True                                          │
│ No SSL/HTTPS                                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ PRODUCTION (VPS with Docker)                        │
├─────────────────────────────────────────────────────┤
│ docker compose up -d                                │
│ 4 services in containers                            │
│ SQLite database (volume mounted)                    │
│ Nginx reverse proxy (port 80/443)                   │
│ DEBUG=False                                         │
│ SSL/HTTPS (Let's Encrypt)                           │
│ Health checks (30s interval)                        │
│ Auto-restart on failure                             │
│ Logs: docker compose logs -f                        │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ TEKNIK DETAYLAR

### GUNICORN Configuration
```
Command: gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 \
         --worker-class gthread --timeout 120 webimar_api.wsgi:application

Breakdown:
├─ --bind 0.0.0.0:8000    # Listen all interfaces, port 8000
├─ --workers 4             # 4 worker processes
├─ --threads 2             # 2 threads per worker (8 threads total)
├─ --worker-class gthread  # Threaded worker class
└─ --timeout 120           # Request timeout 120 seconds
```

### NGINX SSL/TLS
```
SSL Configuration:
├─ Certificate: /etc/nginx/ssl/fullchain.pem (Let's Encrypt)
├─ Private Key: /etc/nginx/ssl/privkey.pem
├─ Protocols: TLSv1.2, TLSv1.3
├─ Ciphers: ECDHE-ECDSA-AES128-GCM-SHA256, etc (modern)
├─ HSTS: max-age=63072000 (2 years)
└─ Session cache: shared:SSL:50m
```

### CORS Headers
```
Added by nginx for /api/*:
├─ Access-Control-Allow-Origin: *
├─ Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
└─ Access-Control-Allow-Headers: Authorization, Content-Type
```

---

## 📊 MEMORY & CPU USAGE

```
Typical Production Load:
├─ nginx (reverse proxy)       ~10MB RAM
├─ webimar-api (Django)        ~300MB RAM (4 workers + 2 threads)
├─ webimar-react (Node.js)     ~150MB RAM
├─ webimar-nextjs (Node.js)    ~150MB RAM
└─ TOTAL                       ~610MB RAM (minimal workload)

Heavy Load (many concurrent users):
└─ Can scale to ~1.5-2GB with auto-restart policies
```

---

## ✅ HEALTH CHECK STRATEGY

```
Service              Endpoint                    Interval  Retries
├─ nginx             /health (200 text/plain)    30s       3
├─ webimar-api       /api/calculations/health/   30s       3 (start: 30s)
├─ webimar-react     /health                     30s       3
└─ webimar-nextjs    /health                     30s       3

If health check fails:
└─ After 3 retries × 30s = 90 seconds → Container marked unhealthy
└─ docker compose configured with restart: unless-stopped
```

---

## 🔐 SECURITY LAYERS

```
1. FIREWALL (VPS Level)
   └─ Port 80/443 open
   └─ Other ports closed

2. NGINX (Application Level)
   ├─ SSL/TLS encryption
   ├─ Security headers (HSTS, X-Frame-Options, etc)
   ├─ Rate limiting (future)
   └─ Request validation

3. DJANGO (Application Level)
   ├─ DEBUG=False
   ├─ SECRET_KEY (must be strong)
   ├─ ALLOWED_HOSTS validation
   ├─ CSRF protection
   ├─ SQL injection prevention (ORM)
   └─ Password hashing (PBKDF2)

4. CONTAINER (Runtime Level)
   ├─ Non-root user (appuser)
   ├─ Read-only filesystem (where possible)
   └─ Resource limits (via docker compose)
```

---

## 🚀 DEPLOYMENT CHECKLIST

```
✅ Pre-Deployment
├─ [ ] Yedek alındı (backup)
├─ [ ] .env dosyası güncellendi
├─ [ ] SSL sertifikaları mevcut
└─ [ ] Docker installed

✅ Deployment
├─ [ ] docker compose build
├─ [ ] docker compose up -d
├─ [ ] Health checks passing
└─ [ ] Logs checked (docker compose logs -f)

✅ Post-Deployment
├─ [ ] HTTPS çalışıyor
├─ [ ] API endpoints responding
├─ [ ] React SPA loading
├─ [ ] Next.js pages rendering
├─ [ ] Database persists
└─ [ ] Auto-restart configured
```

---

## 📝 ÖNEMLI DOSYALAR & YOLLARı

```
VPS File System:
/home/akn/webimar/
├── docker-compose.yml              # Orchestration
├── .env                            # Configuration
├── docker/
│   └── nginx/nginx.conf           # Routing rules
├── ssl/
│   ├── fullchain.pem              # SSL cert
│   └── privkey.pem                # SSL key
├── webimar-api/
│   └── db.sqlite3                 # Database
├── webimar-react/                 # React code
├── webimar-nextjs/                # Next.js code
└── certbot/www/                   # ACME challenge

Container File System:
/app/                              # (webimar-api container)
├── staticfiles/
├── media/
├── data/
│   └── db.sqlite3
├── manage.py
├── webimar_api/
└── calculations/
```

---

## 🎯 QUICK COMMANDS

```bash
# Status
docker compose ps
docker compose logs -f
docker compose logs webimar-api --tail=50

# Restart
docker compose restart
docker compose restart webimar-api

# Update
docker compose pull
docker compose up -d

# Cleanup
docker compose down
docker compose down -v  # Remove volumes

# Shell access
docker compose exec webimar-api bash
docker compose exec webimar-api python manage.py shell

# Database
docker compose exec webimar-api python manage.py migrate
docker compose exec webimar-api python manage.py createsuperuser
```

---

## 📚 LAYER SUMMARY

```
┌─────────────────────────────────────┐
│ REQUEST LAYER                       │  User Browser
├─────────────────────────────────────┤
│ ROUTING LAYER                       │  Nginx (reverse proxy)
├─────────────────────────────────────┤
│ APPLICATION LAYER                   │  Django, React, Next.js
├─────────────────────────────────────┤
│ SERVICE LAYER                       │  Gunicorn, Node processes
├─────────────────────────────────────┤
│ CONTAINER LAYER                     │  Docker containers
├─────────────────────────────────────┤
│ ORCHESTRATION LAYER                 │  Docker Compose
├─────────────────────────────────────┤
│ PERSISTENCE LAYER                   │  Volumes, SQLite
└─────────────────────────────────────┘
```

---

## 🎓 DEVELOPER NOTES

**Production üretim aşaması için önemli notlar:**

1. **Database Migration**: Yeni model eklenirse → `docker compose exec webimar-api python manage.py makemigrations && migrate`

2. **Static Files**: CSS/JS değişirse → `docker compose exec webimar-api python manage.py collectstatic --noinput`

3. **Environment Variables**: `.env` değişirse → `docker compose restart`

4. **Nginx Config**: `docker/nginx/nginx.conf` değişirse → `docker compose restart webimar-nginx`

5. **SSL Renewal**: Let's Encrypt auto-renewal (manual needed if certbot not setup)

6. **Scaling**: PostgreSQL gerekirse → `docker compose --profile with-postgres up -d`

7. **Monitoring**: `docker compose stats` → CPU, RAM kullanımı

8. **Logs Persistence**: `docker compose logs webimar-api > logfile.txt`

---

**Bu mimari, tek VPS'de 3 farklı frontend teknolojisi ve 1 Django backend'i başarıyla çalıştırmaktadır.**

**Production ready, scalable ve secure bir setup. ✅**
