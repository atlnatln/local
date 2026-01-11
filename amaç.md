# Çoklu Proje Geliştirme Ortamı Kurulum Rehberi

## ⚠️ Bu Dokümanın Rolü (Local vs VPS)

Bu dosya (amaç.md) **yol gösterici** olarak kalacak; birebir “esas kaynak” değildir.

Şu an **local geliştirme** tarafındayız ve gerçek proje dizinleriniz:

Projeleri bu workspace içine kopyalayarak ilerleyeceğiz:

- **webimar**: `projects/webimar/`
- **anka**: `projects/anka/`

Localde iki projeyi tek dizinden yönetmek için bu workspace’te bir “kontrol merkezi” kuruldu:

- Başlangıç ve komutlar: [README.md](README.md)
- Yapılanlar/yapılacaklar takibi: [docs/TAKIP.md](docs/TAKIP.md)
- Yönetim scriptleri: [scripts/](scripts)

VPS tarafındaki hedef mimari (main nginx + proje networkleri + certbot) bölümleri ise **anka canlıya taşınırken** referans olarak kullanılacak.

## 📋 Mevcut Durum Analizi

Şu anda tek bir proje (`webimar`) var ve tüm servisleri tek bir `docker-compose.prod.yml` ile yönetiyorsunuz:
- **webimar-nginx**: Reverse proxy (80, 443 portları)
- **webimar-api**: Django backend
- **webimar-react**: React SPA
- **webimar-nextjs**: Next.js SSG
- **postgres**: Veritabanı
- **redis**: Cache

## 🎯 Hedef Mimari

```
                             INTERNET
                               │
     ┌─────────────────────────────────────────────┐
     │           VPS IP (89.252.152.222)           │
     └─────────────────────────────────────────────┘
                               │
                    [MAIN Nginx (Reverse Proxy)]
                         (Port 80, 443)
                               │
                     ┌─────────┴─────────┐
             tarimimar.com.tr      yeniproje.com
                     │                   │
        ┌────────────┼───────┬──────┐   ┌────────┼───────┬──────┐
        │            │       │      │   │        │       │      │
  [webimar-api] [react]  [next] [db] [api]  [next]   [db]
     (8000)      (3001)  (3000)       (8100)  (3100)
```

## 🏗️ Dizin Yapısı

```
/home/akn/vps/
├── projects/                          # Projeler buraya kopyalanır (2+, 3+ ölçeklenir)
│   ├── webimar/                       # Proje kökü (iç yapı projeye göre değişebilir)
│   │   └── docker-compose.yml         # En az bir compose dosyası (docker-compose.yml/compose.yml)
│   ├── anka/
│   │   └── docker-compose.yml
│   └── <yeni-proje>/
│       └── docker-compose.yml
├── scripts/                           # Tek noktadan yönetim (up/down/status/logs)
└── docs/                              # Takip ve notlar

# Not: "infrastructure/" yapısı local için şart değil.
# VPS tarafında tek reverse-proxy + SSL + çok domain yönetimine geçerken eklenir.
```

## 🔧 Kurulum Adımları

### 1. Dizin Yapısını Oluştur

```bash
cd /home/akn

# Ana dizinleri oluştur
mkdir -p infrastructure/nginx/conf.d
mkdir -p infrastructure/nginx/ssl/{webimar,yeniproje}
mkdir -p infrastructure/certbot
mkdir -p projects/{webimar,yeniproje}
mkdir -p scripts

# Mevcut webimar'ı yeni yapıya taşı (yedek alarak)
cp -r webimar webimar-backup-$(date +%Y%m%d)
# Manuel olarak webimar içeriğini projects/webimar/ altına organize edin
```

### 2. Infrastructure - Ana Nginx Reverse Proxy

**infrastructure/docker-compose.yml**
```yaml
version: '3.8'

services:
  # Ana Nginx Reverse Proxy - Tüm projeleri yönlendirir
  main-nginx:
    image: nginx:alpine
    container_name: main-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./certbot/www:/var/www/certbot:ro
    networks:
      - webimar-network
      - yeniproje-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Certbot - SSL Sertifika Yönetimi
  certbot:
    image: certbot/certbot
    container_name: certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

networks:
  webimar-network:
    name: webimar-network
    external: true
  yeniproje-network:
    name: yeniproje-network
    external: true
```

**infrastructure/nginx/nginx.conf**
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    # SSL ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Include proje-spesifik konfigürasyonlar
    include /etc/nginx/conf.d/*.conf;
}
```

**infrastructure/nginx/conf.d/webimar.conf**
```nginx
# Webimar - tarimimar.com.tr
upstream webimar_api {
    server webimar-api:8000;
}

upstream webimar_react {
    server webimar-react:80;
}

upstream webimar_nextjs {
    server webimar-nextjs:3000;
}

# HTTP -> HTTPS yönlendirme
server {
    listen 80;
    server_name tarimimar.com.tr www.tarimimar.com.tr;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name tarimimar.com.tr www.tarimimar.com.tr;

    ssl_certificate /etc/nginx/ssl/webimar/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/webimar/privkey.pem;

    # API Backend
    location /api/ {
        proxy_pass http://webimar_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeout ayarları
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://webimar_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (API)
    location /static/ {
        proxy_pass http://webimar_api;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        proxy_pass http://webimar_api;
        expires 7d;
        add_header Cache-Control "public";
    }

    # React SPA (/hesaplama)
    location /hesaplama {
        proxy_pass http://webimar_react;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Next.js (Ana site)
    location / {
        proxy_pass http://webimar_nextjs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Next.js için özel ayarlar
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
}
```

**infrastructure/nginx/conf.d/yeniproje.conf**
```nginx
# Yeni Proje - yeniproje.com
upstream yeniproje_api {
    server yeniproje-api:8100;
}

upstream yeniproje_nextjs {
    server yeniproje-nextjs:3100;
}

# HTTP -> HTTPS
server {
    listen 80;
    server_name yeniproje.com www.yeniproje.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yeniproje.com www.yeniproje.com;

    ssl_certificate /etc/nginx/ssl/yeniproje/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/yeniproje/privkey.pem;

    # API Backend
    location /api/ {
        proxy_pass http://yeniproje_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Next.js Frontend
    location / {
        proxy_pass http://yeniproje_nextjs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. Proje Bazlı Docker Compose

**projects/webimar/docker-compose.prod.yml**
```yaml
version: '3.8'

services:
  webimar-api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: webimar-api
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://webimar:password@webimar-postgres:5432/webimar
      - REDIS_URL=redis://webimar-redis:6379/0
    depends_on:
      - webimar-postgres
      - webimar-redis
    networks:
      - webimar-network
    restart: unless-stopped

  webimar-react:
    build:
      context: ./react
      dockerfile: Dockerfile
    container_name: webimar-react
    networks:
      - webimar-network
    restart: unless-stopped

  webimar-nextjs:
    build:
      context: ./nextjs
      dockerfile: Dockerfile
    container_name: webimar-nextjs
    networks:
      - webimar-network
    restart: unless-stopped

  webimar-postgres:
    image: postgres:15-alpine
    container_name: webimar-postgres
    environment:
      POSTGRES_DB: webimar
      POSTGRES_USER: webimar
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - webimar_postgres_data:/var/lib/postgresql/data
    networks:
      - webimar-network
    restart: unless-stopped

  webimar-redis:
    image: redis:7-alpine
    container_name: webimar-redis
    volumes:
      - webimar_redis_data:/data
    networks:
      - webimar-network
    restart: unless-stopped

networks:
  webimar-network:
    name: webimar-network
    driver: bridge

volumes:
  webimar_postgres_data:
    name: webimar_postgres_data
  webimar_redis_data:
    name: webimar_redis_data
```

**projects/yeniproje/docker-compose.prod.yml**
```yaml
version: '3.8'

services:
  yeniproje-api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: yeniproje-api
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://yeniproje:password@yeniproje-postgres:5432/yeniproje
    ports:
      - "8100:8100"  # Farklı port
    depends_on:
      - yeniproje-postgres
    networks:
      - yeniproje-network
    restart: unless-stopped

  yeniproje-nextjs:
    build:
      context: ./nextjs
      dockerfile: Dockerfile
    container_name: yeniproje-nextjs
    ports:
      - "3100:3000"  # Farklı port
    networks:
      - yeniproje-network
    restart: unless-stopped

  yeniproje-postgres:
    image: postgres:15-alpine
    container_name: yeniproje-postgres
    environment:
      POSTGRES_DB: yeniproje
      POSTGRES_USER: yeniproje
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - yeniproje_postgres_data:/var/lib/postgresql/data
    networks:
      - yeniproje-network
    restart: unless-stopped

networks:
  yeniproje-network:
    name: yeniproje-network
    driver: bridge

volumes:
  yeniproje_postgres_data:
    name: yeniproje_postgres_data
```

### 4. Local Geliştirme Ortamı

**projects/webimar/docker-compose.yml** (Development)
```yaml
version: '3.8'

services:
  webimar-api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
    container_name: webimar-api-dev
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://webimar:webimar@webimar-postgres-dev:5432/webimar
    volumes:
      - ./api:/app  # Hot reload
    ports:
      - "8000:8000"
    networks:
      - webimar-dev
    command: python manage.py runserver 0.0.0.0:8000

  webimar-nextjs:
    build:
      context: ./nextjs
      dockerfile: Dockerfile.dev
    container_name: webimar-nextjs-dev
    volumes:
      - ./nextjs:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    networks:
      - webimar-dev
    environment:
      - NODE_ENV=development

  webimar-postgres-dev:
    image: postgres:15-alpine
    container_name: webimar-postgres-dev
    environment:
      POSTGRES_DB: webimar
      POSTGRES_USER: webimar
      POSTGRES_PASSWORD: webimar
    ports:
      - "5432:5432"
    networks:
      - webimar-dev

networks:
  webimar-dev:
    name: webimar-dev
    driver: bridge
```

**projects/yeniproje/docker-compose.yml** (Development)
```yaml
version: '3.8'

services:
  yeniproje-api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
    volumes:
      - ./api:/app
    ports:
      - "8100:8100"  # Farklı port - webimar ile çakışmaz
    networks:
      - yeniproje-dev
    environment:
      - DEBUG=True

  yeniproje-nextjs:
    build:
      context: ./nextjs
      dockerfile: Dockerfile.dev
    volumes:
      - ./nextjs:/app
      - /app/node_modules
    ports:
      - "3100:3000"  # Farklı port - webimar ile çakışmaz
    networks:
      - yeniproje-dev

networks:
  yeniproje-dev:
    name: yeniproje-dev
    driver: bridge
```

## 🚀 Deployment Workflow

### 5. Deploy Scriptleri

**projects/webimar/deploy.sh**
```bash
#!/bin/bash
set -e

PROJECT_NAME="webimar"
VPS_USER="akn"
VPS_HOST="89.252.152.222"
DEPLOY_PATH="/home/akn/projects/${PROJECT_NAME}"

echo "🚀 Deploying ${PROJECT_NAME}..."

# 1. Build images locally
echo "📦 Building Docker images..."
docker compose -f docker-compose.prod.yml build

# 2. Save images to tar
echo "💾 Saving images..."
docker save -o ${PROJECT_NAME}-images.tar \
    ${PROJECT_NAME}-api:latest \
    ${PROJECT_NAME}-react:latest \
    ${PROJECT_NAME}-nextjs:latest

# 3. Create deployment package
echo "📦 Creating deployment package..."
tar -czf ${PROJECT_NAME}-deploy.tar.gz \
    docker-compose.prod.yml \
    .env \
    ${PROJECT_NAME}-images.tar

# 4. Upload to VPS
echo "📤 Uploading to VPS..."
scp ${PROJECT_NAME}-deploy.tar.gz ${VPS_USER}@${VPS_HOST}:${DEPLOY_PATH}/

# 5. Deploy on VPS
echo "🔧 Deploying on VPS..."
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /home/akn/projects/webimar
tar -xzf webimar-deploy.tar.gz
docker load -i webimar-images.tar
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
rm -f webimar-images.tar webimar-deploy.tar.gz
ENDSSH

# 6. Cleanup local
echo "🧹 Cleaning up..."
rm -f ${PROJECT_NAME}-images.tar ${PROJECT_NAME}-deploy.tar.gz

echo "✅ Deployment completed!"
```

**scripts/deploy-project.sh** (Generic)
```bash
#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./deploy-project.sh <project-name>"
    echo "Available projects: webimar, yeniproje"
    exit 1
fi

PROJECT=$1
cd /home/akn/projects/${PROJECT}

if [ ! -f "deploy.sh" ]; then
    echo "❌ deploy.sh not found for project: ${PROJECT}"
    exit 1
fi

bash deploy.sh
```

### 6. SSL Sertifika Alma

**scripts/setup-ssl.sh**
```bash
#!/bin/bash

DOMAIN=$1
PROJECT=$2

if [ -z "$DOMAIN" ] || [ -z "$PROJECT" ]; then
    echo "Usage: ./setup-ssl.sh <domain> <project-name>"
    echo "Example: ./setup-ssl.sh yeniproje.com yeniproje"
    exit 1
fi

cd /home/akn/infrastructure

# Certbot ile sertifika al
docker compose run --rm certbot certonly --webroot \
    -w /var/www/certbot \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    --email admin@${DOMAIN} \
    --agree-tos \
    --no-eff-email

# Sertifikaları proje dizinine kopyala
cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem nginx/ssl/${PROJECT}/
cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem nginx/ssl/${PROJECT}/

# Nginx'i reload et
docker compose exec main-nginx nginx -s reload

echo "✅ SSL certificate installed for ${DOMAIN}"
```

## 📝 Geliştirme İş Akışı

### Local Development (Her proje bağımsız)

```bash
# Webimar üzerinde çalış
cd /home/akn/projects/webimar
docker compose up -d
# http://localhost:3000 (Next.js)
# http://localhost:8000 (API)

# Yeni proje üzerinde çalış (aynı anda olabilir - farklı portlar)
cd /home/akn/projects/yeniproje
docker compose up -d
# http://localhost:3100 (Next.js)
# http://localhost:8100 (API)
```

### Test & Deploy

```bash
# 1. Local'de test et
cd /home/akn/projects/webimar
docker compose up -d
# Test yap...

# 2. Production build test et
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
# Test yap...

# 3. Deploy et
bash deploy.sh

# 4. VPS'de kontrol et
ssh akn@89.252.152.222
cd /home/akn/projects/webimar
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

## 🔍 Monitoring & Debugging

```bash
# Ana nginx logları
docker compose -f /home/akn/infrastructure/docker-compose.yml logs -f main-nginx

# Proje logları
cd /home/akn/projects/webimar
docker compose -f docker-compose.prod.yml logs -f

# Tüm sistemin durumu
docker ps
docker network ls
docker volume ls
```

## ✅ Avantajlar

1. **Bağımsız Geliştirme**: Her proje kendi dizininde, çakışma yok
2. **Port Çakışması Yok**: Her proje farklı portlar kullanıyor
3. **Bağımsız Database**: Her projenin kendi PostgreSQL instance'ı
4. **Kolay Deploy**: Her proje kendi deploy scriptine sahip
5. **Nginx Merkezileştirme**: Tek bir main nginx, tüm projeleri route ediyor
6. **SSL Yönetimi**: Merkezi certbot, her proje için ayrı sertifika
7. **Scalability**: Yeni proje eklemek çok kolay (template kopyala)
8. **Isolation**: Bir projedeki hata diğerini etkilemez

## 🎯 Yeni Proje Ekleme Checklist

- [ ] `projects/yeniproje/` dizini oluştur
- [ ] `docker-compose.yml` (dev) ve `docker-compose.prod.yml` hazırla
- [ ] Port numaralarını unique yap (8100, 3100, vs)
- [ ] `infrastructure/nginx/conf.d/yeniproje.conf` ekle
- [ ] Network oluştur: `docker network create yeniproje-network`
- [ ] SSL sertifikası al: `./setup-ssl.sh yeniproje.com yeniproje`
- [ ] Main nginx'i reload: `docker compose -f infrastructure/docker-compose.yml restart main-nginx`
- [ ] Local test et
- [ ] Deploy et

## 🛡️ Güvenlik Notları

1. **.env dosyaları**: Git'e eklemeyin, her ortam için ayrı .env
2. **Secrets**: Docker secrets veya environment variables kullanın
3. **SSL**: Always use HTTPS in production
4. **Database**: Production database'leri external volume'larda sakla
5. **Firewall**: VPS'de sadece 80 ve 443 portları açık olsun

## 📚 Kaynaklar

- Docker Compose Networks: https://docs.docker.com/compose/networking/
- Nginx Reverse Proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- Certbot: https://certbot.eff.org/
