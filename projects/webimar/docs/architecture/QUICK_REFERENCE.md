# 🏗️ TARIMIMAR DOCKER ARCHITECTURE - QUICK REFERENCE
## Geliştirici için Hızlı Rehber

---

## 📊 ONE-PAGE ARCHITECTURE

```
                        🌐 https://tarimimar.com.tr
                                    │
                            HTTPS (TLSv1.3)
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │      VPS Docker Setup    (0.0.0.0:80/443)             │
        │     (/home/akn/webimar)                               │
        ├─────────────────────────────────────────────────────────┤
        │                                                        │
        │  ┌──────────────────────────────────────────────────┐ │
        │  │  🔄 NGINX Reverse Proxy  (nginx:alpine)         │ │
        │  │  ├─ Listen: 0.0.0.0:80/443                     │ │
        │  │  ├─ SSL: /etc/nginx/ssl/ ← Let's Encrypt       │ │
        │  │  ├─ Gzip: Enabled                               │ │
        │  │  └─ Routes:                                     │ │
        │  │     ├─ /api/* → webimar-api:8000               │ │
        │  │     ├─ /hesaplama/* → webimar-react:3001       │ │
        │  │     ├─ / → webimar-nextjs:3000                 │ │
        │  │     └─ /_next/* → webimar-nextjs:3000 (cached) │ │
        │  └─────────┬──────────────┬─────────────┬──────────┘ │
        │            │              │             │            │
        │  ┌─────────▼────┐  ┌──────▼─────┐  ┌───▼────────────┐│
        │  │ DJANGO API   │  │ REACT SPA  │  │ NEXT.JS SSG    ││
        │  │ (Port: 8000) │  │(Port: 3001)│  │ (Port: 3000)   ││
        │  │              │  │            │  │                ││
        │  │ 🐍 Python    │  │ 📦 Node.js  │  │ 📦 Node.js     ││
        │  │ 🚀 Gunicorn  │  │ ⚛️  React   │  │ ▲️ Next.js    ││
        │  │ 🗄️ REST API  │  │ 📱 SPA UI  │  │ 📄 SSG Pages  ││
        │  └─────────┬────┘  └────────────┘  │ 🔍 SEO Ready   ││
        │            │                       └────────────────┘│
        │            │                                        │
        │  ┌─────────▼──────────────────────────────────────┐ │
        │  │  💾 SQLite3 Database                          │ │
        │  │  ├─ File: /app/data/db.sqlite3                │ │
        │  │  ├─ Volume: api_database (persists)           │ │
        │  │  ├─ Tables: calculations, users, sessions     │ │
        │  │  └─ Accessible from: webimar-api container    │ │
        │  └──────────────────────────────────────────────┘ │
        │                                                    │
        │  🔐 SSL/TLS                                       │
        │  ├─ Certificate: /ssl/fullchain.pem               │
        │  ├─ Key: /ssl/privkey.pem                         │
        │  └─ Provider: Let's Encrypt                       │
        │                                                    │
        │  📝 Configuration                                 │
        │  ├─ .env: SECRET_KEY, DATABASE_URL, etc          │
        │  ├─ docker/nginx/nginx.conf: Routing rules        │
        │  └─ docker-compose.yml: Service definitions       │
        │                                                    │
        └──────────────────────────────────────────────────┘
```

---

## 🔀 ROUTING MATRIX

| **URL Path** | **Container** | **Process** | **Response Type** |
|---|---|---|---|
| `/` | webimar-nextjs:3000 | Next.js SSR | HTML page (cached) |
| `/api/*` | webimar-api:8000 | Django REST | JSON |
| `/admin/` | webimar-api:8000 | Django Admin | HTML |
| `/hesaplama/*` | webimar-react:3001 | React SPA | HTML + JS |
| `/auth/*` | webimar-react:3001 | React SPA | HTML + JS |
| `/bag-evi`, `/sera`, etc | webimar-nextjs:3000 | Next.js SSR | HTML page (pre-built) |
| `/_next/static/*` | webimar-nextjs:3000 | Static assets | JS/CSS (cached 365d) |
| `/static/*` | webimar-api:8000 | Django static | CSS/JS (cached 30d) |

---

## 💾 DATABASE SCHEMA (SIMPLIFIED)

```
SQLite3: db.sqlite3
│
├── calculations_calculation
│   ├── id (int, PK)
│   ├── type (char: bag-evi, sera, etc)
│   ├── parameters (JSON: input data)
│   ├── results (JSON: output data)
│   ├── user_id (FK → auth_user)
│   └── created_at, updated_at (datetime)
│
├── auth_user
│   ├── id (int, PK)
│   ├── username (char, unique)
│   ├── email (char, unique)
│   ├── password (varchar, hashed)
│   └── is_staff, is_superuser (bool)
│
└── django_session
    ├── session_key (varchar, PK)
    ├── session_data (text, encrypted)
    └── expire_date (datetime)
```

---

## 🚀 KEY COMMANDS

```bash
# Status & Logs
docker compose ps                          # List containers
docker compose logs -f                     # Follow all logs
docker compose logs webimar-api -f --tail=100  # Follow API logs

# Management
docker compose up -d                       # Start all
docker compose restart                     # Restart all
docker compose down                        # Stop all (keep volumes)
docker compose down -v                     # Stop all (delete volumes)

# Debugging
docker compose exec webimar-api bash       # Shell into API
docker compose exec webimar-api python manage.py shell  # Django shell
docker compose exec webimar-api python manage.py migrate  # Run migrations

# Database
docker compose exec webimar-api python manage.py createsuperuser
docker compose exec webimar-api python manage.py collectstatic --noinput

# Health
curl https://tarimimar.com.tr/health       # Nginx health
curl https://tarimimar.com.tr/api/calculations/health/  # API health
```

---

## 📈 CONTAINER HEALTH CHECKS

```
Container         Endpoint                          Frequency  Failure Action
─────────────────────────────────────────────────────────────────────────────
webimar-nginx     /health                           30s        Wait & retry
webimar-api       /api/calculations/health/         30s        Wait & retry
webimar-react     /health                           30s        Wait & retry
webimar-nextjs    /health                           30s        Wait & retry

Failure Threshold: 3 consecutive failures (90 seconds) → Mark unhealthy
Restart Policy: unless-stopped → Auto-restart if container exits
```

---

## 🔐 SECURITY LAYERS

**Layer 1 - Network**
- Firewall: Ports 80/443 only
- Docker Network: Internal bridge (webimar-network)

**Layer 2 - SSL/TLS**
- Protocol: TLSv1.2 + TLSv1.3
- Certificate: Let's Encrypt (auto-renew)
- HSTS: 2-year policy

**Layer 3 - Application**
- Django DEBUG: False
- SECRET_KEY: Required in .env
- CSRF Protection: Enabled
- SQL Injection: ORM prevents

**Layer 4 - Container**
- Non-root user: appuser
- No privileged mode
- Resource limits: Optional

---

## 🔄 REQUEST FLOW (EXAMPLE)

```
USER BROWSER
    ↓ (HTTPS Request)
    ↓ GET /api/calculations/bag-evi/
    ↓
NGINX (Port 443)
    ↓ SSL Termination
    ↓ Path matching: /api/* → webimar-api:8000
    ↓ Add X-Forwarded-For header
    ↓
DJANGO API (Port 8000)
    ↓ Route: calculations/views.py
    ↓ View: CalculationViewSet.retrieve()
    ↓ Database: SELECT calculations WHERE id=1
    ↓ Serialize: CalculationSerializer
    ↓ Response: 200 OK + JSON
    ↓
NGINX (Port 443)
    ↓ Add security headers
    ↓ Gzip compression
    ↓ SSL encryption
    ↓
USER BROWSER
    ↓ Parse JSON
    ↓ Display results
```

---

## 📁 DIRECTORY MAPPING

```
HOST MACHINE               DOCKER CONTAINER
────────────────────────────────────────────

/home/akn/webimar/
    ├── docker-compose.yml  (not mounted, read-only)
    ├── .env                ← /app/.env
    │
    ├── webimar-api/
    │   ├── db.sqlite3      ← api_database:/app/data/db.sqlite3
    │   ├── staticfiles/    ← api_staticfiles:/app/staticfiles/
    │   ├── media/          ← api_media:/app/media/
    │   └── webimar_api/
    │       └── settings.py (DATABASE_URL from .env)
    │
    ├── docker/
    │   └── nginx/
    │       └── nginx.conf  ← /etc/nginx/nginx.conf
    │
    ├── ssl/
    │   ├── fullchain.pem   ← /etc/nginx/ssl/fullchain.pem
    │   └── privkey.pem     ← /etc/nginx/ssl/privkey.pem
    │
    └── certbot/www/        ← /var/www/certbot/
```

---

## ⚙️ ENVIRONMENT VARIABLES (.env)

```bash
# Database
DATABASE_URL=sqlite:////app/data/db.sqlite3

# Django Security
DEBUG=False
SECRET_KEY=your-secret-key-here-at-least-50-chars

# Allowed Domains
ALLOWED_HOSTS=localhost,127.0.0.1,tarimimar.com.tr,www.tarimimar.com.tr

# API Endpoints (for frontend)
REACT_APP_API_BASE_URL=https://tarimimar.com.tr/api
NEXT_PUBLIC_API_BASE_URL=https://tarimimar.com.tr/api

# CORS
CORS_ALLOWED_ORIGINS=https://tarimimar.com.tr,http://localhost

# OAuth (if using)
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

---

## 🛠️ NGINX CONFIGURATION HIGHLIGHT

```nginx
# Upstream servers (internal DNS via Docker network)
upstream api_backend {
    server webimar-api:8000;  # Container name:port
}
upstream react_frontend {
    server webimar-react:3001;
}
upstream nextjs_frontend {
    server webimar-nextjs:3000;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name tarimimar.com.tr;
    
    # SSL Certificates
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # Route API requests
    location /api/ {
        proxy_pass http://api_backend/api/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header Access-Control-Allow-Origin *;
    }
    
    # Route SPA requests
    location /hesaplama/ {
        proxy_pass http://react_frontend/;
    }
    
    # Route landing pages
    location / {
        proxy_pass http://nextjs_frontend/;
    }
}
```

---

## 📊 MONITORING & TROUBLESHOOTING

**Check service status:**
```bash
docker compose ps
```

**Follow logs in real-time:**
```bash
docker compose logs -f
```

**Check specific container:**
```bash
docker compose logs webimar-api -f --tail=50
```

**Access database shell:**
```bash
docker compose exec webimar-api python manage.py dbshell
```

**Verify network connectivity:**
```bash
docker compose exec webimar-nginx ping webimar-api
docker compose exec webimar-api ping webimar-nextjs
```

---

## ✅ PRODUCTION CHECKLIST

- [ ] `.env` has strong `SECRET_KEY`
- [ ] Database is backed up
- [ ] SSL certificates configured
- [ ] All 4 containers running healthy
- [ ] Health checks passing (30s interval)
- [ ] HTTPS working (curl -I https://...)
- [ ] API responding (curl https://.../api/health/)
- [ ] React app loading (/hesaplama/)
- [ ] Next.js pages rendering (/)
- [ ] Logs checked (docker compose logs)

---

## 📞 COMMON ISSUES

| **Issue** | **Cause** | **Solution** |
|---|---|---|
| "Connection refused" | Container not running | `docker compose up -d` |
| "502 Bad Gateway" | Backend not responding | Check `docker compose logs webimar-api` |
| "SSL certificate error" | Cert path wrong | Verify `/ssl/` files exist |
| "Database locked" | SQLite access issue | Ensure volume mounted correctly |
| "Health check failing" | Endpoint not responding | Check container app is running |

---

## 🎯 ARCHITECTURE SUMMARY

✅ **4 Containers** orchestrated via Docker Compose  
✅ **3 Frontends** (Nginx reverse proxy, React SPA, Next.js SSG)  
✅ **1 Backend** (Django REST API with Gunicorn)  
✅ **1 Database** (SQLite with volume persistence)  
✅ **SSL/HTTPS** with Let's Encrypt  
✅ **Health Checks** with auto-restart  
✅ **Production Ready** configuration  

**Total RAM Usage:** ~600MB idle, ~1-2GB under load

---

**Last Updated:** 2025-12-05  
**Status:** ✅ Fully Operational  
**Deployment:** Docker Compose v2.39.4  
**Nginx Version:** nginx:alpine  
