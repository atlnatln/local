---
agent: agent
---
Define the task t
This is a comprehensive code review and optimization task list for the VPS infrastructure.
Each task is actionable and can be implemented directly in VSCode with GitHub Copilot.

---

## 📋 Table of Contents
1. [Security Issues](#security-issues)
2. [Performance Optimizations](#performance-optimizations)
3. [Configuration Improvements](#configuration-improvements)
4. [Code Quality](#code-quality)
5. [Documentation](#documentation)
6. [Monitoring & Observability](#monitoring--observability)

---

## 🔐 Security Issues

### CRITICAL: Django SSL Redirect Warning

**File**: `webimar-api/settings/production.py` or `webimar-api/config/settings.py`

**Issue**: 
```
SECURE_SSL_REDIRECT setting is not set to True
```

**Current State**: Django is not enforcing HTTPS redirects (relies on nginx)

**Required Changes**:
```python
# @file: webimar-api/settings/production.py

# Add these security settings
SECURE_SSL_REDIRECT = False  # Keep False - nginx handles SSL termination
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # ADD THIS
SESSION_COOKIE_SECURE = True  # Ensure session cookies are HTTPS-only
CSRF_COOKIE_SECURE = True     # Ensure CSRF cookies are HTTPS-only

# Security headers (if not already present)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

**Rationale**: 
- SSL termination happens at infrastructure nginx
- But Django needs to know requests are HTTPS via X-Forwarded-Proto header
- Session/CSRF cookies must be secure

---

### HIGH: Default Credentials in docker-compose.prod.yml

**File**: `vps/projects/webimar/docker-compose.prod.yml`

**Issue**:
```yaml
SECRET_KEY=${SECRET_KEY:-change-me-in-production}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-webimar123}
```

**Current State**: Fallback values are weak defaults

**Required Changes**:
```yaml
# @file: vps/projects/webimar/docker-compose.prod.yml

# Replace fallback defaults with error-raising pattern
environment:
  - SECRET_KEY=${SECRET_KEY:?SECRET_KEY not set - check .env file}
  - DATABASE_URL=${DATABASE_URL:?DATABASE_URL not set - check .env file}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set - check .env file}
```

**Also create**: `vps/projects/webimar/.env.example`
```bash
# @file: vps/projects/webimar/.env.example

# Django
SECRET_KEY=your-secret-key-here-generate-with-python-manage-py-shell

# Database
POSTGRES_DB=webimar
POSTGRES_USER=webimar
POSTGRES_PASSWORD=your-strong-password-here

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# OAuth (Optional)
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

---

### MEDIUM: Port 8080 Default Server Missing

**File**: `vps/infrastructure/nginx/conf.d/default.conf` (CREATE NEW)

**Issue**: Port 8080 (health check) serving 404 errors, exposing internal structure

**Current Logs**:
```
[error] "/etc/nginx/html/index.html" is not found
[error] "/etc/nginx/html/_next" failed
[error] "/etc/nginx/html/api" failed
```

**Required Changes**:
```nginx
# @file: vps/infrastructure/nginx/conf.d/default.conf (NEW FILE)

# Default server for port 8080 (health check port)
server {
    listen 8080 default_server;
    server_name _;
    
    # Health check endpoint
    location /nginx-health {
        access_log off;
        add_header Content-Type text/plain;
        return 200 "nginx operational\n";
    }
    
    # Drop all other requests (security)
    location / {
        access_log off;
        return 444;  # Close connection without response
    }
}

# Default HTTPS server (catch-all for unknown domains)
server {
    listen 443 ssl http2 default_server;
    server_name _;
    
    # Use default self-signed cert
    ssl_certificate /etc/nginx/ssl/default/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/default/key.pem;
    
    # Return 404 for all requests
    return 404;
}
```

After creating, reload nginx:
```bash
docker compose -f vps/infrastructure/docker-compose.yml exec nginx_proxy nginx -s reload
```

---

### MEDIUM: Exposed Postgres Port in Development

**File**: `vps/projects/webimar/docker-compose.yml`

**Issue**: Development compose may expose PostgreSQL port 5432 publicly

**Check and Fix**:
```yaml
# @file: vps/projects/webimar/docker-compose.yml

postgres:
  image: postgres:15-alpine
  # Remove if present:
  # ports:
  #   - "5432:5432"  # ❌ REMOVE - publicly exposes database
  
  # Keep internal network only:
  networks:
    - webimar-dev
  
  # Health check is fine
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U webimar"]
```

Same check for Redis:
```yaml
redis:
  image: redis:7-alpine
  # Remove if present:
  # ports:
  #   - "6379:6379"  # ❌ REMOVE
  networks:
    - webimar-dev
```

---

## ⚡ Performance Optimizations

### HIGH: Docker Image Sizes Too Large

**Current State**:
```
webimar-api:      2.66GB  ❌ Too large
webimar-nextjs:   874MB   ⚠️  Can be optimized
webimar-react:    290MB   ✅ OK
```

**Issue**: API image is 2.66GB (should be <500MB)

#### Fix 1: Multi-stage Build for API

**File**: `vps/projects/webimar/docker/Dockerfile.api`

**Current Pattern** (likely):
```dockerfile
# Anti-pattern
FROM python:3.11
COPY . /app
RUN pip install -r requirements.txt
```

**Optimized Pattern**:
```dockerfile
# @file: vps/projects/webimar/docker/Dockerfile.api

# Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY webimar-api/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY webimar-api/ .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/calculations/health/ || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]
```

**Expected Result**: Image size reduced from 2.66GB to ~400MB

---

#### Fix 2: Next.js Image Optimization

**File**: `vps/projects/webimar/docker/Dockerfile.nextjs`

**Add .dockerignore**:
```dockerignore
# @file: vps/projects/webimar/webimar-nextjs/.dockerignore

node_modules
.next
.git
.vscode
*.log
npm-debug.log*
.env*.local
README.md
```

**Optimize Dockerfile**:
```dockerfile
# @file: vps/projects/webimar/docker/Dockerfile.nextjs

FROM node:18-alpine AS deps
WORKDIR /app
COPY webimar-nextjs/package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY webimar-nextjs/ .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
```

**Also add to `next.config.js`**:
```js
// @file: vps/projects/webimar/webimar-nextjs/next.config.js

module.exports = {
  output: 'standalone',  // Enable standalone output for Docker
  // ... other config
}
```

**Expected Result**: Image size reduced from 874MB to ~200MB

---

### MEDIUM: Nginx Worker Processes Not Optimized

**File**: `vps/infrastructure/nginx/nginx.conf`

**Current**:
```nginx
worker_processes auto;
```

**Issue**: May spawn too many workers for VPS resources

**Check CPU cores**:
```bash
nproc  # Returns number of CPU cores
```

**Optimize**:
```nginx
# @file: vps/infrastructure/nginx/nginx.conf

# For 2-core VPS
worker_processes 2;
worker_rlimit_nofile 8192;

events {
    worker_connections 2048;  # Increase from 1024
    use epoll;
    multi_accept on;
}
```

---

### MEDIUM: Missing Nginx Caching

**File**: `vps/infrastructure/nginx/conf.d/webimar.conf`

**Issue**: No static asset caching configured

**Add before server blocks**:
```nginx
# @file: vps/infrastructure/nginx/conf.d/webimar.conf

# Cache configuration
proxy_cache_path /var/cache/nginx/webimar levels=1:2 keys_zone=webimar_cache:10m max_size=100m inactive=60m use_temp_path=off;

upstream webimar_project {
    server webimar-nginx:80 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# ... existing server blocks ...

server {
    listen 443 ssl http2;
    server_name tarimimar.com.tr www.tarimimar.com.tr;
    
    # ... existing SSL config ...
    
    # Add caching for static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://webimar_project;
        proxy_cache webimar_cache;
        proxy_cache_valid 200 30d;
        proxy_cache_valid 404 1m;
        add_header X-Cache-Status $upstream_cache_status;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # ... rest of config ...
}
```

**Also update docker-compose.yml**:
```yaml
# @file: vps/infrastructure/docker-compose.yml

nginx_proxy:
  volumes:
    - nginx_cache:/var/cache/nginx  # ADD THIS
    
volumes:
  nginx_cache:
    name: vps_nginx_cache  # ADD THIS
```

---

## 🔧 Configuration Improvements

### HIGH: Missing Backup Automation

**File**: `vps/scripts/backup-volumes.sh` (CREATE NEW)

**Create backup script**:
```bash
# @file: vps/scripts/backup-volumes.sh

#!/bin/bash
set -euo pipefail

BACKUP_DIR="/home/akn/vps/backups"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup at $(date)"

# Backup Webimar PostgreSQL
echo "📦 Backing up webimar database..."
docker exec webimar-postgres pg_dump -U webimar webimar | gzip > \
  "$BACKUP_DIR/webimar-db-$DATE.sql.gz"

# Backup Anka PostgreSQL (if running)
if docker ps --format '{{.Names}}' | grep -q anka_postgres; then
    echo "📦 Backing up anka database..."
    docker exec anka_postgres_prod pg_dump -U anka_user anka_prod | gzip > \
      "$BACKUP_DIR/anka-db-$DATE.sql.gz"
fi

# Cleanup old backups
echo "🧹 Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Disk usage report
echo "💾 Backup directory size: $(du -sh $BACKUP_DIR | cut -f1)"
ls -lh "$BACKUP_DIR" | tail -5

echo "✅ Backup completed at $(date)"
```

**Make executable and add to cron**:
```bash
chmod +x vps/scripts/backup-volumes.sh

# Add to crontab (run daily at 2 AM)
# crontab -e
# Add line:
# 0 2 * * * /home/akn/vps/scripts/backup-volumes.sh >> /home/akn/vps/backups/backup.log 2>&1
```

---

### HIGH: Certbot Auto-Renewal Not Active

**File**: `vps/infrastructure/docker-compose.yml`

**Current**:
```yaml
certbot:
  profiles:
    - ssl-generation  # ❌ Only runs manually
```

**Fix**:
```yaml
# @file: vps/infrastructure/docker-compose.yml

certbot:
  image: certbot/certbot:latest
  container_name: vps_certbot
  volumes:
    - certbot_certs:/etc/letsencrypt
    - certbot_webroot:/var/www/certbot
  command: >
    sh -c "
      trap exit TERM;
      while :; do
        certbot renew --webroot --webroot-path=/var/www/certbot --quiet;
        sleep 12h & wait $${!};
      done
    "
  restart: unless-stopped
  networks:
    - vps_network
  # Remove profiles - always run
  # profiles:
  #   - ssl-generation
```

**Deploy**:
```bash
cd vps/infrastructure
docker compose up -d certbot
docker compose logs -f certbot  # Verify it's running
```

---

### MEDIUM: Environment Variables Not Validated

**File**: `vps/projects/webimar/.env.validation.sh` (CREATE NEW)

**Create validation script**:
```bash
# @file: vps/projects/webimar/.env.validation.sh

#!/bin/bash
set -euo pipefail

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found"
    exit 1
fi

echo "🔍 Validating $ENV_FILE..."

# Required variables
REQUIRED_VARS=(
    "SECRET_KEY"
    "POSTGRES_PASSWORD"
    "POSTGRES_USER"
    "POSTGRES_DB"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" "$ENV_FILE"; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing required variables:"
    printf '  - %s\n' "${MISSING_VARS[@]}"
    exit 1
fi

# Check for default/weak values
if grep -q "SECRET_KEY=change-me" "$ENV_FILE"; then
    echo "⚠️  WARNING: SECRET_KEY is set to default value"
fi

if grep -q "POSTGRES_PASSWORD=webimar123" "$ENV_FILE"; then
    echo "⚠️  WARNING: POSTGRES_PASSWORD is using default value"
fi

echo "✅ Environment validation passed"
```

**Use in deploy script**:
```bash
# @file: vps/projects/webimar/deploy.sh

# Add before deployment
bash .env.validation.sh .env.production || exit 1
```

---

### MEDIUM: No Health Check for Main Nginx

**File**: `vps/infrastructure/docker-compose.yml`

**Current**: Nginx has healthcheck but not comprehensive

**Improve**:
```yaml
# @file: vps/infrastructure/docker-compose.yml

nginx_proxy:
  healthcheck:
    test: |
      sh -c '
        wget --no-verbose --tries=1 --spider http://localhost:8080/nginx-health &&
        wget --no-verbose --tries=1 --spider --no-check-certificate https://localhost/health/ || exit 1
      '
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 10s
```

---

## 📝 Code Quality

### MEDIUM: Inconsistent Dockerfile Naming

**Current State**:
```
docker/Dockerfile.api        ✅
docker/Dockerfile.nginx      ✅
docker/Dockerfile.nextjs     ✅
docker/Dockerfile.react      ✅

BUT ALSO:
webimar-api/Dockerfile       ❌ Duplicate
webimar-nextjs/Dockerfile    ❌ Duplicate
webimar-react/Dockerfile     ❌ Duplicate
```

**Action**: Remove duplicate Dockerfiles, use only `docker/Dockerfile.*`

```bash
# @terminal

cd vps/projects/webimar
rm -f webimar-api/Dockerfile
rm -f webimar-nextjs/Dockerfile
rm -f webimar-nextjs/Dockerfile.production
rm -f webimar-react/Dockerfile

# Verify docker-compose.prod.yml uses correct paths
grep "dockerfile:" docker-compose.prod.yml
```

---

### MEDIUM: Missing .dockerignore Files

**Create for each service**:

```dockerignore
# @file: vps/projects/webimar/webimar-api/.dockerignore

__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.log
*.db
*.sqlite3
.git
.gitignore
.env
.env.*
README.md
tests/
.pytest_cache/
.coverage
htmlcov/
```

```dockerignore
# @file: vps/projects/webimar/webimar-react/.dockerignore

node_modules
build
.git
.env
.env.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
README.md
```

---

### LOW: Docker Compose Override Pattern

**File**: `vps/projects/webimar/docker-compose.override.yml` (CREATE NEW)

**Purpose**: Allow local overrides without modifying main files

```yaml
# @file: vps/projects/webimar/docker-compose.override.yml
# This file is for local development overrides
# Add to .gitignore

version: '3.8'

services:
  webimar-api:
    environment:
      - DEBUG=True
    ports:
      - "8000:8000"  # Expose for debugging
    
  postgres:
    ports:
      - "5432:5432"  # Expose for local tools
```

**Add to .gitignore**:
```gitignore
# @file: vps/projects/webimar/.gitignore

docker-compose.override.yml
.env.local
```

---

## 📊 Monitoring & Observability

### HIGH: Missing Application Metrics

**File**: `vps/projects/webimar/docker-compose.prod.yml`

**Add Prometheus exporter for Django**:

```yaml
# @file: vps/projects/webimar/docker-compose.prod.yml

services:
  webimar-api:
    environment:
      - PROMETHEUS_METRICS_EXPORT_PORT=8001  # Add metrics endpoint
```

**In Django app**:
```python
# @file: webimar-api/requirements.txt
# Add:
django-prometheus==2.3.1
```

```python
# @file: webimar-api/config/settings.py

INSTALLED_APPS = [
    # ...
    'django_prometheus',  # Add at top
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # First
    # ... other middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',   # Last
]
```

```python
# @file: webimar-api/config/urls.py

from django.urls import path, include

urlpatterns = [
    path('', include('django_prometheus.urls')),  # Metrics at /metrics
    # ... other urls ...
]
```

**Update Prometheus config**:
```yaml
# @file: vps/infrastructure/monitoring/prometheus.yml

scrape_configs:
  - job_name: 'webimar-api'
    static_configs:
      - targets: ['webimar-api:8000']
    metrics_path: '/metrics'
```

---

### MEDIUM: No Log Aggregation

**File**: `vps/infrastructure/docker-compose.yml`

**Add Loki for log aggregation**:

```yaml
# @file: vps/infrastructure/docker-compose.yml

services:
  loki:
    image: grafana/loki:latest
    container_name: vps_loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    restart: unless-stopped
    networks:
      - vps_network
    profiles:
      - monitoring

volumes:
  loki_data:
    name: vps_loki_data
```

**Create Loki config**:
```yaml
# @file: vps/infrastructure/monitoring/loki-config.yml

auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

---

### MEDIUM: Missing Container Resource Monitoring

**File**: `vps/infrastructure/docker-compose.yml`

**Add cAdvisor for container metrics**:

```yaml
# @file: vps/infrastructure/docker-compose.yml

services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: vps_cadvisor
    ports:
      - "8081:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    restart: unless-stopped
    networks:
      - vps_network
    profiles:
      - monitoring
```

**Update Prometheus to scrape cAdvisor**:
```yaml
# @file: vps/infrastructure/monitoring/prometheus.yml

scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

---

## 📚 Documentation

### MEDIUM: Missing Architecture Diagram

**File**: `vps/ARCHITECTURE.md` (CREATE NEW)

**Create architecture documentation**:

```markdown
# @file: vps/ARCHITECTURE.md

# VPS Infrastructure Architecture

## Network Topology

```
Internet (80/443)
    ↓
[vps_nginx_main] - SSL Termination
    ↓
[Domain Router]
    ├── tarimimar.com.tr → webimar-nginx:80
    └── ankadata.com.tr → anka-nginx:80
         ↓                        ↓
    [Webimar Services]      [Anka Services]
         ├── API                  ├── Backend
         ├── Next.js              ├── Frontend
         ├── React                ├── Celery Worker
         ├── PostgreSQL           ├── Celery Beat
         └── Redis                ├── PostgreSQL
                                  ├── Redis
                                  └── MinIO
```

## Volumes

### Webimar
- `webimar_postgres_data` - PostgreSQL database (66MB)
- `webimar_redis_data` - Redis cache
- `webimar_api_staticfiles` - Static files
- `webimar_api_media` - User uploads

### Infrastructure
- `vps_nginx_logs` - Nginx logs
- `vps_prometheus_data` - Metrics
- `vps_grafana_data` - Dashboards

## Resource Usage

| Container | CPU | Memory | Limit |
|-----------|-----|--------|-------|
| webimar-api | 0.06% | 177MB | 1GB |
| webimar-nginx | 0.00% | 3MB | 256MB |
| webimar-nextjs | 0.00% | 57MB | 512MB |
| vps_nginx_main | 0.00% | 10MB | - |
| vps_prometheus | 0.75% | 40MB | - |

## Security

- SSL: Let's Encrypt (auto-renewal via certbot)
- SSL Termination: Infrastructure nginx only
- Internal: HTTP (no SSL overhead)
- Secrets: Environment variables (not in git)

## Backup Strategy

- Database: Daily pg_dump at 2 AM
- Retention: 7 days
- Location: `/home/akn/vps/backups/`
```

---

### LOW: Add README to Each Project

**File**: `vps/projects/webimar/README.md` (CREATE NEW)

```markdown
# @file: vps/projects/webimar/README.md

# Webimar Project

## Quick Start

### Development
```bash
docker compose up -d
# Services:
# - API: http://localhost:8000
# - Next.js: http://localhost:3000
# - React: http://localhost:3001
```

### Production Deployment
```bash
bash deploy.sh
```

## Project Structure

```
webimar/
├── webimar-api/         - Django backend
├── webimar-nextjs/      - Next.js SSG
├── webimar-react/       - React SPA
├── docker/              - Dockerfiles
│   ├── Dockerfile.api
│   ├── Dockerfile.nginx
│   ├── Dockerfile.nextjs
│   └── Dockerfile.react
├── docker-compose.yml        - Development
├── docker-compose.prod.yml   - Production
└── deploy.sh                 - Deploy script
```

## Environment Variables

See `.env.example` for required variables.

## Troubleshooting

### Container won't start
```bash
docker compose logs <service-name>
docker compose ps
```

### Database issues
```bash
docker exec -it webimar-postgres psql -U webimar -d webimar
```

### Clear cache
```bash
docker compose exec redis redis-cli FLUSHALL
```
```

---

## 🎯 Implementation Priority

### Immediate (Week 1)
1. ✅ Fix Django SSL redirect settings
2. ✅ Add default server for port 8080
3. ✅ Enable certbot auto-renewal
4. ✅ Create backup automation script

### Short-term (Week 2-3)
5. ⚠️ Optimize Docker images (multi-stage builds)
6. ⚠️ Add .dockerignore files
7. ⚠️ Add environment validation
8. ⚠️ Configure nginx caching

### Medium-term (Month 1)
9. 📊 Add application metrics (django-prometheus)
10. 📊 Set up log aggregation (Loki)
11. 📊 Add cAdvisor for container monitoring
12. 🔒 Review and strengthen default credentials

### Long-term (Ongoing)
13. 📚 Complete documentation
14. 🧹 Code cleanup (remove duplicates)
15. ⚡ Performance tuning based on metrics
16. 🔄 CI/CD pipeline setup

---

## 📝 Testing Checklist

After implementing changes:

```bash
# 1. Validate environment
bash vps/projects/webimar/.env.validation.sh

# 2. Test build
cd vps/projects/webimar
docker compose -f docker-compose.prod.yml build

# 3. Check image sizes
docker images | grep webimar

# 4. Start services
docker compose -f docker-compose.prod.yml up -d

# 5. Health checks
docker compose ps
curl http://localhost/health
curl -k https://tarimimar.com.tr

# 6. Check logs
docker compose logs --tail=50

# 7. Verify backups
ls -lh /home/akn/vps/backups/

# 8. Check metrics
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
```

---

## 🤖 Copilot Usage Tips

When implementing these changes:

1. **Open the file mentioned in each task**
2. **Select the code block to modify**
3. **Use Copilot Chat**: Ask "Implement the changes from the prompt"
4. **Review the suggestions** before accepting
5. **Test immediately** after each change
6. **Commit incrementally** with clear messages

Example Copilot prompts:
- "Add multi-stage build to this Dockerfile to reduce image size"
- "Create a .dockerignore file for this Next.js project"
- "Add Django prometheus middleware configuration"
- "Optimize this nginx configuration for caching"
o achieve, including specific requirements, constraints, and success criteria.