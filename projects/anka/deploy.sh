#!/bin/bash
# ============================================================================
# Anka Production Deploy Script (Local → VPS)
# Domain: ankadata.com.tr
# Server: 89.252.152.222
# Çalıştırma: local makineden, VPS'e SSH/SCP ile deploy eder.
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Project configuration
PROJECT_NAME="anka"
DOMAIN="ankadata.com.tr"
SERVER_IP="${SERVER_IP:-89.252.152.222}"
VPS_HOST="${VPS_HOST:-akn@${SERVER_IP}}"
VPS_PATH="/home/akn/vps/projects/anka"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"
SSH_CONNECT_TIMEOUT="${SSH_CONNECT_TIMEOUT:-10}"
SSH_OPTS=(
    -o BatchMode=yes
    -o IdentitiesOnly=yes
    -o StrictHostKeyChecking=accept-new
    -o ConnectTimeout="${SSH_CONNECT_TIMEOUT}"
    -o ServerAliveInterval=30
    -o ServerAliveCountMax=3
)

# GitHub (monorepo: /home/akn/vps)
GIT_REMOTE_NAME="origin"
GIT_REMOTE_URL="https://github.com/atlnatln/vps.git"
GIT_BRANCH="main"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              🚀 Anka Production Deploy                        ║${NC}"
echo -e "${CYAN}║              Domain: ${DOMAIN}                   ║${NC}"
echo -e "${CYAN}║              Server: ${SERVER_IP}                ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ─────────────────────── Argument parsing ──────────────────────────
SKIP_BUILD=false
SKIP_VPS=false
SKIP_GITHUB=false
FORCE_RECREATE=false
AUTO_STAGE_GITHUB=false
RUN_VPS_CLEANUP=true
DEPLOY_MODE="package"   # package (default) | git

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)         SKIP_BUILD=true;         shift ;;
        --skip-vps)           SKIP_VPS=true;            shift ;;
        --skip-github)        SKIP_GITHUB=true;         shift ;;
        --auto-stage-github)  AUTO_STAGE_GITHUB=true;   shift ;;
        --force-recreate)     FORCE_RECREATE=true;      shift ;;
        --no-vps-cleanup)     RUN_VPS_CLEANUP=false;    shift ;;
        --mode)
            DEPLOY_MODE="${2:-}"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-build          Skip Docker image building"
            echo "  --skip-vps            Skip VPS deployment"
            echo "  --skip-github         Skip GitHub push"
            echo "  --auto-stage-github   GitHub push öncesi otomatik stage yap (DİKKAT)"
            echo "  --force-recreate      Force recreate all containers"
            echo "  --no-vps-cleanup      Skip deploy sonrası VPS disk temizliği"
            echo "  --mode <package|git>  Deploy mode:"
            echo "        package: build+export images and scp to VPS (default)"
            echo "        git:     VPS repo git pull + docker compose up --build"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ "$DEPLOY_MODE" != "package" && "$DEPLOY_MODE" != "git" ]]; then
    log_error "Invalid --mode: ${DEPLOY_MODE} (use: package|git)"
    exit 1
fi

cd "$PROJECT_DIR"

# ─────────────────────── Preflight: env validation ─────────────────
if [ ! -f ".env.production" ]; then
    log_error ".env.production file not found. Please create it first."
    echo "   Başlangıç için: cp .env.production.example .env.production"
    exit 1
fi

get_env_value() {
    local key="$1"
    local value
    value="$(grep -E "^${key}=" .env.production | tail -n 1 | cut -d'=' -f2- || true)"
    value="${value%\"}"
    value="${value#\"}"
    echo "$value"
}

GOOGLE_OIDC_CLIENT_ID_VALUE="$(get_env_value "GOOGLE_OIDC_CLIENT_ID")"
NEXT_PUBLIC_GOOGLE_CLIENT_ID_VALUE="$(get_env_value "NEXT_PUBLIC_GOOGLE_CLIENT_ID")"
NEXT_PUBLIC_API_URL_VALUE="$(get_env_value "NEXT_PUBLIC_API_URL")"
NEXT_PUBLIC_SITE_URL_VALUE="$(get_env_value "NEXT_PUBLIC_SITE_URL")"
CORS_ALLOWED_ORIGINS_VALUE="$(get_env_value "CORS_ALLOWED_ORIGINS")"
ENABLE_IYZICO_VALUE="$(get_env_value "ENABLE_IYZICO")"
IYZICO_WEBHOOK_SECRET_VALUE="$(get_env_value "IYZICO_WEBHOOK_SECRET")"
SECRET_KEY_VALUE="$(get_env_value "SECRET_KEY")"
CSRF_TRUSTED_ORIGINS_VALUE="$(get_env_value "CSRF_TRUSTED_ORIGINS")"
REDIS_PASSWORD_VALUE="$(get_env_value "REDIS_PASSWORD")"
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY_VALUE="$(get_env_value "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY")"

if [ -z "$GOOGLE_OIDC_CLIENT_ID_VALUE" ] || [ -z "$NEXT_PUBLIC_GOOGLE_CLIENT_ID_VALUE" ]; then
    log_error "Missing Google OAuth env vars in .env.production"
    log_error "Required: GOOGLE_OIDC_CLIENT_ID and NEXT_PUBLIC_GOOGLE_CLIENT_ID"
    exit 1
fi

# --- Security preflight checks ---
if [ -z "$SECRET_KEY_VALUE" ] || [ ${#SECRET_KEY_VALUE} -lt 32 ]; then
    log_error "SECRET_KEY is missing or too short (min 32 chars) in .env.production"
    exit 1
fi
if echo "$SECRET_KEY_VALUE" | grep -qi "insecure\|change.this\|dev-key"; then
    log_error "SECRET_KEY appears to contain a development/default value. Use a secure random key."
    exit 1
fi

if [ -z "$NEXT_PUBLIC_GOOGLE_MAPS_API_KEY_VALUE" ]; then
    log_warning "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is not set — Google Maps will not work"
fi

if [ -z "$CSRF_TRUSTED_ORIGINS_VALUE" ]; then
    log_warning "CSRF_TRUSTED_ORIGINS is not set in .env.production — CSRF protection may block requests"
fi

if [ -z "$REDIS_PASSWORD_VALUE" ]; then
    log_warning "REDIS_PASSWORD is not set — Redis has no authentication in production"
fi

if [ -z "$NEXT_PUBLIC_API_URL_VALUE" ]; then
    log_error "Missing NEXT_PUBLIC_API_URL in .env.production"
    exit 1
fi

if [ -z "$NEXT_PUBLIC_SITE_URL_VALUE" ]; then
    log_error "Missing NEXT_PUBLIC_SITE_URL in .env.production"
    exit 1
fi

if [[ "$NEXT_PUBLIC_API_URL_VALUE" == *"localhost"* ]] || [[ "$NEXT_PUBLIC_API_URL_VALUE" == *"127.0.0.1"* ]]; then
    log_error "NEXT_PUBLIC_API_URL cannot point to localhost/127.0.0.1 in production"
    exit 1
fi

if [[ "$NEXT_PUBLIC_SITE_URL_VALUE" == *"localhost"* ]] || [[ "$NEXT_PUBLIC_SITE_URL_VALUE" == *"127.0.0.1"* ]]; then
    log_error "NEXT_PUBLIC_SITE_URL cannot point to localhost/127.0.0.1 in production"
    exit 1
fi

if [ -n "$CORS_ALLOWED_ORIGINS_VALUE" ] && [[ "$CORS_ALLOWED_ORIGINS_VALUE" != *"https://${DOMAIN}"* ]]; then
    log_warning "CORS_ALLOWED_ORIGINS does not include https://${DOMAIN}"
fi

if [ -z "$ENABLE_IYZICO_VALUE" ] || [ "$ENABLE_IYZICO_VALUE" = "True" ] || [ "$ENABLE_IYZICO_VALUE" = "true" ]; then
    if [ -z "$IYZICO_WEBHOOK_SECRET_VALUE" ]; then
        log_error "Missing Iyzico webhook secret in .env.production"
        log_error "Required when ENABLE_IYZICO is true: IYZICO_WEBHOOK_SECRET"
        exit 1
    fi
fi

# ─────────────────────── Pre-deployment checks ─────────────────────
log_info "Running pre-deployment checks..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

log_success "Pre-deployment checks passed"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ─────────────────────── Step 1: Build ─────────────────────────────
if [ "$SKIP_BUILD" = false ]; then
    echo -e "\n${YELLOW}[1/5] 🔨 Building production Docker images...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    docker compose -f docker-compose.prod.yml build --no-cache
    log_success "Docker images built"
else
    echo -e "\n${YELLOW}[1/5] ⏭️  Skipping build (--skip-build)${NC}"
fi

# ─────────────────────── Step 2: Export/Package ─────────────────────
BUILD_DIR="${PROJECT_DIR}/.deploy-tmp"

if [[ "$DEPLOY_MODE" == "package" ]]; then
    echo -e "\n${YELLOW}[2/5] 📦 Exporting container images...${NC}"
    rm -rf "$BUILD_DIR" && mkdir -p "$BUILD_DIR/images"

    # Sadece custom-built image'lar export edilir (backend + frontend).
    # celery_worker ve celery_beat aynı backend image'ını paylaşır.
    echo -e "  → Saving backend image (backend + celery containers)..."
    docker save "anka-backend:latest" -o "$BUILD_DIR/images/backend.tar" &
    echo -e "  → Saving frontend image..."
    docker save "anka-frontend:latest" -o "$BUILD_DIR/images/frontend.tar" &
    wait

    # configs
    cp docker-compose.prod.yml "$BUILD_DIR/docker-compose.prod.yml"
    cp .env.production         "$BUILD_DIR/.env.production"

    mkdir -p "$BUILD_DIR/infra/nginx"
    cp infra/nginx/prod.conf "$BUILD_DIR/infra/nginx/prod.conf"

    if [ -d "infra/postgres/init" ]; then
        mkdir -p "$BUILD_DIR/infra/postgres/init"
        cp -r infra/postgres/init/. "$BUILD_DIR/infra/postgres/init/" 2>/dev/null || true
    fi

    # Django prod settings (container hot-patch için)
    SETTINGS_SRC="services/backend/project/settings/prod.py"
    if [ -f "$SETTINGS_SRC" ]; then
        mkdir -p "$BUILD_DIR/settings"
        cp "$SETTINGS_SRC" "$BUILD_DIR/settings/prod.py"
    fi

    # ─── VPS setup.sh ────────────────────────────────────────────────
    cat > "$BUILD_DIR/setup.sh" << 'SETUP_SCRIPT'
#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🚀 Anka VPS Setup"

if [ ! -f ".env.production" ]; then
    log_error ".env.production bulunamadı. Deploy iptal edildi."
    exit 1
fi

mkdir -p ssl/ankadata.com.tr logs backups infra/postgres/init

# SSL
INFRA_CERT="/home/akn/vps/infrastructure/ssl/ankadata.com.tr"
if [ -f "${INFRA_CERT}/fullchain.pem" ] && [ -f "${INFRA_CERT}/privkey.pem" ]; then
    log_info "Copying SSL certificates from infrastructure/ssl..."
    cp "${INFRA_CERT}/fullchain.pem" ssl/ankadata.com.tr/fullchain.pem
    cp "${INFRA_CERT}/privkey.pem"   ssl/ankadata.com.tr/privkey.pem
    log_success "SSL certificates copied"
elif [ ! -f "ssl/ankadata.com.tr/fullchain.pem" ] || [ ! -f "ssl/ankadata.com.tr/privkey.pem" ]; then
    log_warning "SSL bulunamadı; self-signed sertifika oluşturuluyor..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/ankadata.com.tr/privkey.pem \
        -out    ssl/ankadata.com.tr/fullchain.pem \
        -subj   "/CN=ankadata.com.tr" \
        -addext "subjectAltName=DNS:ankadata.com.tr,DNS:www.ankadata.com.tr" >/dev/null 2>&1
    log_warning "Self-signed sertifika oluşturuldu"
fi

# Backup
if docker ps -a --format '{{.Names}}' | grep -q "anka_.*_prod"; then
    BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    if docker ps --format '{{.Names}}' | grep -q "anka_postgres_prod"; then
        log_info "Backing up PostgreSQL database..."
        docker exec anka_postgres_prod pg_dump -U anka_user anka_prod > "$BACKUP_DIR/database.sql" 2>/dev/null || true
    fi
    if docker volume ls --format '{{.Name}}' | grep -q "anka_media_files"; then
        log_info "Backing up media files..."
        docker run --rm -v anka_media_files:/source -v "$PWD/$BACKUP_DIR":/backup \
            alpine tar czf /backup/media.tar.gz -C /source . 2>/dev/null || true
    fi
    log_success "Backup created in $BACKUP_DIR"
else
    log_info "No existing containers found, skipping backup"
fi

# Shared edge network
docker network inspect vps_infrastructure_network >/dev/null 2>&1 || \
    docker network create vps_infrastructure_network >/dev/null

# Load images
log_info "Loading Docker images..."
for tar_file in images/*.tar; do
    [ -f "$tar_file" ] && docker load -i "$tar_file" && echo "  ✓ $tar_file"
done

# Stop existing
log_info "Stopping existing containers..."
docker compose --env-file .env.production -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

# Start containers
log_info "Starting production containers..."
if [ "${FORCE_RECREATE:-false}" = "true" ]; then
    docker compose --env-file .env.production -f docker-compose.prod.yml up -d --force-recreate --remove-orphans
else
    docker compose --env-file .env.production -f docker-compose.prod.yml up -d --remove-orphans
fi
log_success "Production containers started"

# Sync Django prod settings
if [ -f "settings/prod.py" ]; then
    log_info "Syncing Django production settings..."
    for _container in anka_backend_prod anka_celery_worker_prod anka_celery_beat_prod; do
        if docker ps --format '{{.Names}}' | grep -q "^${_container}$"; then
            docker cp settings/prod.py "${_container}:/app/project/settings/prod.py" 2>/dev/null && \
                log_info "  ✓ ${_container}" || \
                log_warning "  Could not sync settings to ${_container}"
        fi
    done
    unset _container
    log_success "Django production settings synced"
fi

# Wait
log_info "Waiting for services to be ready..."
sleep 15

services=("anka_postgres_prod" "anka_redis_prod" "anka_backend_prod" "anka_frontend_prod" "anka_nginx_prod")
max_attempts=30
attempt=0
all_healthy=true

while [ $attempt -lt $max_attempts ]; do
    all_healthy=true
    for service in "${services[@]}"; do
        if ! docker ps --format '{{.Names}} {{.Status}}' | grep "$service" | grep -q "healthy\|Up"; then
            all_healthy=false
            break
        fi
    done
    [ "$all_healthy" = true ] && break
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done
echo ""
[ "$all_healthy" = true ] && log_success "All services are healthy" || \
    log_warning "Some services may not be fully ready yet."

# Frontend bundle check (no localhost)
if docker ps --format '{{.Names}}' | grep -q '^anka_frontend_prod$'; then
    localhost_hits="$(docker exec anka_frontend_prod sh -lc \
        "grep -rl 'localhost:8000' /app/.next/static/chunks 2>/dev/null | wc -l")"
    if [ "${localhost_hits:-0}" -gt 0 ]; then
        log_error "Detected localhost:8000 in frontend production bundle! NEXT_PUBLIC_API_URL misconfigured."
    else
        log_success "Frontend runtime bundle check passed"
    fi
fi

# Migrate
log_info "Running database migrations..."
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T backend \
    python manage.py migrate --noinput
log_success "Database migrations completed"

# Collectstatic
log_info "Collecting static files..."
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T --user root backend \
    sh -c "mkdir -p /app/staticfiles /app/media && chown -R anka:anka /app/staticfiles /app/media 2>/dev/null || true" || true
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T backend \
    python manage.py collectstatic --noinput --clear
log_success "Static files collected"

# Superuser
log_info "Setting up admin user..."
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T backend python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
admin_password = os.environ.get('ADMIN_INITIAL_PASSWORD', '')
if not admin_password:
    import secrets
    admin_password = secrets.token_urlsafe(20)
    print(f'Generated secure random admin password (store it safely)')
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@ankadata.com.tr', admin_password)
    print('Admin user created')
else:
    print('Admin user already exists')
" 2>/dev/null || log_warning "Could not create admin user automatically"

log_success "🎉 VPS deployment complete!"
docker compose --env-file .env.production -f docker-compose.prod.yml ps
SETUP_SCRIPT
    chmod +x "$BUILD_DIR/setup.sh"

    echo -e "  → Creating deployment package..."
    cd "$BUILD_DIR"
    tar --warning=no-file-changed -czf anka-deploy.tar.gz --exclude='anka-deploy.tar.gz' .
    cd "$PROJECT_DIR"

    log_success "Package created: $(du -sh "$BUILD_DIR/anka-deploy.tar.gz" | cut -f1)"
else
    echo -e "\n${YELLOW}[2/5] ⏭️  Skipping image export (mode=git)${NC}"
fi

# ─────────────────────── Step 3: Deploy to VPS ─────────────────────
if [ "$SKIP_VPS" = false ]; then
    echo -e "\n${YELLOW}[3/5] 🚀 Deploying to VPS...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "$DEPLOY_MODE" == "package" ]]; then
        log_info "Creating remote directory..."
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" "mkdir -p $VPS_PATH"
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" \
            "docker network inspect vps_infrastructure_network >/dev/null 2>&1 || \
             docker network create vps_infrastructure_network >/dev/null"

        echo -e "  → Uploading package to VPS..."
        scp "${SSH_OPTS[@]}" "$BUILD_DIR/anka-deploy.tar.gz" "$VPS_HOST:$VPS_PATH/"

        echo -e "  → Extracting and deploying..."
        FORCE_ENV=""
        [ "$FORCE_RECREATE" = true ] && FORCE_ENV="FORCE_RECREATE=true"
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" \
            "cd $VPS_PATH && tar -xzf anka-deploy.tar.gz && ${FORCE_ENV} bash setup.sh"

    else
        # git mode
        log_info "Running git pull + docker compose on VPS..."
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" "set -euo pipefail
            cd /home/akn/vps
            docker network inspect vps_infrastructure_network >/dev/null 2>&1 || \
                docker network create vps_infrastructure_network >/dev/null
            if [ -n \"\$(git status --porcelain 2>/dev/null)\" ]; then
                git stash 2>/dev/null || true
            fi
            git fetch origin
            git reset --hard origin/main
            cd $VPS_PATH
            if [ ! -f .env.production ]; then
                echo '❌ .env.production missing on VPS. Deploy iptal edildi.'
                exit 1
            fi
            docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build --remove-orphans
            docker compose --env-file .env.production -f docker-compose.prod.yml ps"
    fi

    log_success "VPS deployment complete"

    # ── Container smoke checks ─────────────────────────────────────
    echo -e "\n${YELLOW}[3/5b] 🩺 Container smoke checks...${NC}"
    ssh "${SSH_OPTS[@]}" "$VPS_HOST" bash -s <<'SMOKE'
set -euo pipefail
ok=1

check_container() {
    local name="$1"
    if ! docker ps --format '{{.Names}}' | grep -qx "$name"; then
        echo "$name -> missing"
        ok=0
        return
    fi
    local status attempts=18 sleep_seconds=5 i=1
    status="$(docker inspect --format \
        '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
        "$name" 2>/dev/null || echo unknown)"
    while [ "$i" -lt "$attempts" ] && [ "$status" = "starting" ]; do
        sleep "$sleep_seconds"
        i=$((i + 1))
        status="$(docker inspect --format \
            '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
            "$name" 2>/dev/null || echo unknown)"
    done
    echo "$name -> $status"
    case "$status" in
        healthy|running) : ;;
        *) ok=0 ;;
    esac
}

check_container "anka_postgres_prod"
check_container "anka_redis_prod"
check_container "anka_backend_prod"
check_container "anka_frontend_prod"
check_container "anka_nginx_prod"

if [ "$ok" -ne 1 ]; then
    echo "❌ Container smoke checks FAILED"
    exit 1
fi
echo "✅ Container smoke checks OK"
SMOKE

    # ── Application smoke checks ───────────────────────────────────
    echo -e "\n${YELLOW}[3/5c] 🩺 Application smoke checks...${NC}"
    ssh "${SSH_OPTS[@]}" "$VPS_HOST" bash -s <<'APPSMOKE'
set -euo pipefail
BASE_URL="https://ankadata.com.tr"
ORIGIN="https://ankadata.com.tr"

health_status="$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/api/health/")"
if [ "$health_status" != "200" ]; then
    echo "❌ Health check failed: ${BASE_URL}/api/health/ -> ${health_status}"
    exit 1
fi
echo "✅ Health check OK (${health_status})"

preflight_status="$(curl -s -o /dev/null -w '%{http_code}' \
    -X OPTIONS "${BASE_URL}/api/auth/google/" \
    -H "Origin: ${ORIGIN}" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type")"
if [ "$preflight_status" -lt 200 ] || [ "$preflight_status" -ge 300 ]; then
    echo "❌ CORS preflight failed: ${preflight_status}"
    exit 1
fi
echo "✅ CORS preflight OK (${preflight_status})"

post_status="$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST "${BASE_URL}/api/auth/google/" \
    -H "Content-Type: application/json" \
    -d '{}')"
if [ "$post_status" != "400" ]; then
    echo "❌ Auth validation check failed (expected 400, got ${post_status})"
    exit 1
fi
echo "✅ Auth validation OK (${post_status})"
APPSMOKE

    # ── Infrastructure nginx ───────────────────────────────────────
    echo -e "\n${YELLOW}[3/5d] 🔄 Updating infrastructure nginx...${NC}"
    if [ -f "../../infrastructure/nginx/conf.d/anka.conf" ]; then
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" "mkdir -p /home/akn/vps/infrastructure/nginx/conf.d"
        scp "${SSH_OPTS[@]}" \
            "../../infrastructure/nginx/conf.d/anka.conf" \
            "$VPS_HOST:/home/akn/vps/infrastructure/nginx/conf.d/anka.conf"
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" \
            "docker network inspect vps_infrastructure_network >/dev/null 2>&1 || \
                docker network create vps_infrastructure_network >/dev/null; \
             docker compose -f /home/akn/vps/infrastructure/docker-compose.yml up -d nginx_proxy >/dev/null 2>&1 || true; \
             docker exec vps_nginx_main nginx -t && docker exec vps_nginx_main nginx -s reload" \
            2>/dev/null || log_warning "Infrastructure nginx reload failed"
        log_success "Infrastructure nginx updated"
    else
        log_warning "Infrastructure nginx config not found at ../../infrastructure/nginx/conf.d/anka.conf"
    fi

    # ── Edge smoke checks ──────────────────────────────────────────
    echo -e "\n${YELLOW}[3/5e] 🩺 Edge smoke checks (nginx + domains)...${NC}"
    ssh "${SSH_OPTS[@]}" "$VPS_HOST" bash -s <<'EDGE_SMOKE'
set -euo pipefail

docker exec vps_nginx_main nginx -t >/dev/null

check_domain() {
    local domain="$1"
    local result code effective
    result="$(curl -L --max-redirs 5 --max-time 20 -o /dev/null -s -w "%{http_code} %{url_effective}" "https://${domain}/")"
    code="${result%% *}"
    effective="${result#* }"
    echo "${domain} -> ${code} (${effective})"
    if [ "$code" -lt 200 ] || [ "$code" -ge 400 ]; then
        return 1
    fi
}

check_domain "ankadata.com.tr"
check_domain "tarimimar.com.tr"
EDGE_SMOKE

    log_success "Edge smoke checks passed"

    # ── VPS cleanup ────────────────────────────────────────────────
    if [ "$RUN_VPS_CLEANUP" = true ]; then
        echo -e "\n${YELLOW}[3/5f] 🧹 VPS disk cleanup...${NC}"
        ssh "${SSH_OPTS[@]}" "$VPS_HOST" "set -euo pipefail
            echo '--- Disk before ---'
            df -h / /home
            echo '--- Docker before ---'
            docker system df
            cd $VPS_PATH
            rm -f anka-deploy.tar.gz
            rm -f images/*.tar 2>/dev/null || true
            docker image prune -f >/tmp/anka_prune_images.log
            echo '--- image prune ---'
            cat /tmp/anka_prune_images.log
            echo '--- Disk after ---'
            df -h / /home
            echo '--- Docker after ---'
            docker system df"
        log_success "VPS cleanup complete"
    else
        echo -e "\n${YELLOW}[3/5f] ⏭️  Skipping VPS cleanup (--no-vps-cleanup)${NC}"
    fi
else
    echo -e "\n${YELLOW}[3/5] ⏭️  Skipping VPS deployment (--skip-vps)${NC}"
fi

# ─────────────────────── Step 4: GitHub push ──────────────────────
if [ "$SKIP_GITHUB" = false ]; then
    echo -e "\n${YELLOW}[4/5] 📤 Pushing to GitHub...${NC}"

    cd "$REPO_ROOT"

    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        git init
        git checkout -b "$GIT_BRANCH" >/dev/null 2>&1 || git branch -M "$GIT_BRANCH"
    fi

    if ! git config user.email >/dev/null 2>&1; then git config user.email "deploy@localhost"; fi
    if ! git config user.name  >/dev/null 2>&1; then git config user.name  "Deploy Script";   fi

    if git remote get-url "$GIT_REMOTE_NAME" >/dev/null 2>&1; then
        git remote set-url "$GIT_REMOTE_NAME" "$GIT_REMOTE_URL"
    else
        git remote add "$GIT_REMOTE_NAME" "$GIT_REMOTE_URL"
    fi

    if [ "$AUTO_STAGE_GITHUB" = true ]; then
        echo -e "  ${YELLOW}⚠️  Auto-stage açık: git add -A çalıştırılıyor${NC}"
        git add -A
    else
        echo -e "  ${BLUE}Auto-stage kapalı: yalnızca önceden stage edilmiş değişiklikler push edilecek${NC}"
        echo -e "  ${BLUE}Gerekirse --auto-stage-github ile tekrar çalıştırabilirsiniz${NC}"
    fi

    if git diff --staged --quiet; then
        echo -e "  ${BLUE}No changes to commit${NC}"
    else
        git commit -m "deploy(anka): production update ${TIMESTAMP}"
        git push origin "$GIT_BRANCH"
        log_success "GitHub push complete"
    fi

    cd "$PROJECT_DIR"
else
    echo -e "\n${YELLOW}[4/5] ⏭️  Skipping GitHub push (--skip-github)${NC}"
fi

# ─────────────────────── Step 5: Local cleanup ─────────────────────
echo -e "\n${YELLOW}[5/5] 🧹 Cleaning up local temp files...${NC}"
[[ "$DEPLOY_MODE" == "package" ]] && rm -rf "$BUILD_DIR"

# ─────────────────────── Summary ───────────────────────────────────
echo ""
log_success "🎉 Deployment completed successfully!"
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                     📊 Deployment Summary                     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 URLs:${NC}"
echo -e "   Main Site:   https://ankadata.com.tr"
echo -e "   Admin Panel: https://ankadata.com.tr/admin/"
echo -e "   API:         https://ankadata.com.tr/api/"
echo ""
echo -e "${GREEN}🔧 Management (VPS üzerinde):${NC}"
echo -e "   Logs:   docker compose --env-file .env.production -f docker-compose.prod.yml logs -f"
echo -e "   Status: docker compose --env-file .env.production -f docker-compose.prod.yml ps"
echo -e "   Stop:   docker compose --env-file .env.production -f docker-compose.prod.yml down"
echo ""
echo -e "${GREEN}✅ Steps completed:${NC}"
[ "$SKIP_BUILD"  = false ] && echo -e "   ✅ Docker images built (local)"
[ "$SKIP_VPS"    = false ] && echo -e "   ✅ Deployed to VPS: ${VPS_HOST}:${VPS_PATH}"
[ "$SKIP_VPS"    = false ] && [ "$RUN_VPS_CLEANUP" = true ] && echo -e "   ✅ VPS disk cleanup done"
[ "$SKIP_GITHUB" = false ] && echo -e "   ✅ Pushed to GitHub"
echo ""
log_success "Deployment is ready! 🚀"
