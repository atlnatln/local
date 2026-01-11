#!/bin/bash
# ========================================
# Webimar Deploy Script
# Tek script ile VPS + GitHub'a deploy
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration - DÜZENLE
VPS_HOST="akn@89.252.152.222"
VPS_PATH="/home/akn/vps/projects/webimar"
SSL_PATH="/etc/letsencrypt"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# GitHub (monorepo: /home/akn/vps)
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"
GIT_REMOTE_NAME="origin"
GIT_REMOTE_URL="https://github.com/atlnatln/vps.git"
GIT_BRANCH="main"

# Parse arguments
SKIP_BUILD=false
SKIP_VPS=false
SKIP_GITHUB=false
DEPLOY_MODE="package"  # package (default) | git

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build) SKIP_BUILD=true; shift ;;
        --skip-vps) SKIP_VPS=true; shift ;;
        --skip-github) SKIP_GITHUB=true; shift ;;
        --mode)
            DEPLOY_MODE="${2:-}"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-build    Skip container build step"
            echo "  --skip-vps      Skip VPS deployment"
            echo "  --skip-github   Skip GitHub push"
            echo "  --mode <package|git>  Deploy mode:"
            echo "       package: build+export images and scp to VPS (default)"
            echo "       git: VPS repo 'git pull' + docker compose up --build"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ "$DEPLOY_MODE" != "package" && "$DEPLOY_MODE" != "git" ]]; then
    echo -e "${RED}❌ Invalid --mode: ${DEPLOY_MODE} (use: package|git)${NC}"
    exit 1
fi

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Webimar Deploy Script v2.0         ║${NC}"
echo -e "${CYAN}║     VPS + GitHub Parallel Deploy       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"

cd "$PROJECT_DIR"

require_file() {
    local path="$1"
    local hint="$2"
    if [ ! -f "$path" ]; then
        echo -e "${RED}❌ Missing required file: ${path}${NC}"
        [ -n "$hint" ] && echo -e "   ${YELLOW}${hint}${NC}"
        exit 1
    fi
}

warn_file() {
    local path="$1"
    local hint="$2"
    if [ ! -f "$path" ]; then
        echo -e "${YELLOW}⚠️  Missing optional file: ${path}${NC}"
        [ -n "$hint" ] && echo -e "   ${YELLOW}${hint}${NC}"
    fi
}

# Preflight: package mode için env dosyaları zorunlu.
if [[ "$DEPLOY_MODE" == "package" ]]; then
    require_file ".env.production" "package mode, VPS'e .env üretmek için .env.production dosyasını kopyalar. Oluştur: cp .env.production.example .env.production (varsa)"
    require_file "webimar-nextjs/.env.production" "Next.js container build/runtime için webimar-nextjs/.env.production bekleniyor."
else
    warn_file ".env" "git mode: VPS tarafında docker compose varsayılan olarak .env dosyasını okur (VPS'de olması gerekir)."
fi

# Ops-bot removed from project

# Step 1: Build containers (if not skipped)
if [ "$SKIP_BUILD" = false ]; then
    echo -e "\n${YELLOW}[1/5] 🔨 Building production Docker containers...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # CRITICAL: Temporarily switch .env to .env.production for correct build args
    if [ -L .env ]; then
        ORIGINAL_ENV_TARGET=$(readlink .env)
        echo -e "${YELLOW}  ⚠️  Unlinking .env symlink (was: ${ORIGINAL_ENV_TARGET})${NC}"
        rm .env
    fi
    
    ln -sf .env.production .env
    echo -e "${GREEN}  ✓ Linked .env → .env.production (NEXT_PUBLIC_REACT_SPA_URL=$(grep NEXT_PUBLIC_REACT_SPA_URL .env.production | cut -d'=' -f2))${NC}"
    
    docker compose -f docker-compose.prod.yml build
    
    # Restore original symlink if it existed
    if [ ! -z "${ORIGINAL_ENV_TARGET:-}" ]; then
        rm .env
        ln -sf "$ORIGINAL_ENV_TARGET" .env
        echo -e "${BLUE}  ↩️  Restored .env → ${ORIGINAL_ENV_TARGET}${NC}"
    fi
else
    echo -e "\n${YELLOW}[1/5] ⏭️  Skipping build (--skip-build)${NC}"
fi

# Step 2: Export container images
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [[ "$DEPLOY_MODE" == "package" ]]; then
    echo -e "\n${YELLOW}[2/5] 📦 Exporting container images...${NC}"
    BUILD_DIR="${PROJECT_DIR}/.deploy-tmp"
    rm -rf "$BUILD_DIR" && mkdir -p "$BUILD_DIR/images"

    # Export images
    docker save webimar-webimar-api:latest -o "$BUILD_DIR/images/api.tar" &
    docker save webimar-webimar-react:latest -o "$BUILD_DIR/images/react.tar" &
    docker save webimar-webimar-nextjs:latest -o "$BUILD_DIR/images/nextjs.tar" &
    docker save webimar-nginx:latest -o "$BUILD_DIR/images/nginx.tar" &
    wait

    # Copy configs (nginx config is now baked into image)
    cp docker-compose.prod.yml "$BUILD_DIR/docker-compose.prod.yml"
    cp .env.production "$BUILD_DIR/.env"
    mkdir -p "$BUILD_DIR/webimar-nextjs"
    cp webimar-nextjs/.env.production "$BUILD_DIR/webimar-nextjs/.env.production"
    
    # Agent files removed (ops-bot specific)

    # Create VPS deploy script
    cat > "$BUILD_DIR/setup.sh" << 'SETUP_SCRIPT'
#!/bin/bash
set -e
echo "🚀 Webimar VPS Deployment"

# Load images (including nginx with embedded config)
echo "📦 Loading Docker images..."
for tar_file in images/*.tar; do
    [ -f "$tar_file" ] && docker load -i "$tar_file"
done

# Copy Next.js environment file
mkdir -p webimar-nextjs
if [ -f "webimar-nextjs/.env.production" ]; then
    echo "📄 Copying Next.js .env.production..."
    cp webimar-nextjs/.env.production webimar-nextjs/.env.production.backup 2>/dev/null || true
fi

# Agent files removed (ops-bot specific)

# Create SSL directory and setup certs
mkdir -p ssl
if [ -d "/etc/letsencrypt/live/tarimimar.com.tr" ]; then
    # Copy real certs (not symlinks, for Docker compatibility)
    cp -L /etc/letsencrypt/live/tarimimar.com.tr/fullchain.pem ssl/fullchain.pem 2>/dev/null || true
    cp -L /etc/letsencrypt/live/tarimimar.com.tr/privkey.pem ssl/privkey.pem 2>/dev/null || true
    echo "✅ SSL certificates copied"
else
    echo "⚠️  SSL certificates not found, creating self-signed..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/privkey.pem -out ssl/fullchain.pem \
        -subj "/CN=localhost" 2>/dev/null
fi

# Stop existing containers
docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
# Eski stack varsa (docker-compose.yml), onu da kapat (volume silme yok).
docker compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true

# Start main services
docker compose -f docker-compose.prod.yml up -d

# Ops-bot removed from project

echo ""
echo "✅ Deployment complete!"
docker compose -f docker-compose.prod.yml ps
SETUP_SCRIPT
    chmod +x "$BUILD_DIR/setup.sh"

    # Create package (nginx config is now baked into nginx image)
    echo -e "  → Creating deployment package..."
    cd "$BUILD_DIR"
    tar -czf webimar-deploy.tar.gz --exclude='webimar-deploy.tar.gz' images .env docker-compose.prod.yml setup.sh webimar-nextjs
    cd "$PROJECT_DIR"
else
    echo -e "\n${YELLOW}[2/5] ⏭️  Skipping image export (mode=git)${NC}"
fi

# Step 3: Deploy to VPS
if [ "$SKIP_VPS" = false ]; then
    echo -e "\n${YELLOW}[3/5] 🚀 Deploying to VPS...${NC}"

    if [[ "$DEPLOY_MODE" == "package" ]]; then
        # Create remote directory
        ssh "$VPS_HOST" "mkdir -p $VPS_PATH"

        # Upload package
        echo -e "  → Uploading package to VPS..."
        scp "$BUILD_DIR/webimar-deploy.tar.gz" "$VPS_HOST:$VPS_PATH/"

        # Extract and deploy
        echo -e "  → Extracting and deploying..."
        ssh "$VPS_HOST" "cd $VPS_PATH && tar -xzf webimar-deploy.tar.gz && ./setup.sh"
    else
        # Repo-based deploy: git pull + docker compose up --build (single source: docker-compose.prod.yml)
        echo -e "  → Running git pull + docker compose on VPS..."
        ssh "$VPS_HOST" "set -euo pipefail; cd $VPS_PATH; \
            if [ ! -d .git ]; then echo '❌ VPS_PATH is not a git repo. Clone the repo to VPS_PATH or use --mode package.'; exit 1; fi; \
            # VPS üzerinde bazen local hotfix / runtime dosyaları repo içine karışabiliyor.
            # Fast-forward pull merge hatasına düşmesin diye: fetch + hard reset.
            # (Gerekirse diff yedeği alır.)
            if [ -n \"$(git status --porcelain)\" ]; then \
                ts=\"$(date +%Y%m%d_%H%M%S)\"; \
                mkdir -p \"$HOME/webimar-backup/predeploy-diffs\" 2>/dev/null || true; \
                git diff > \"$HOME/webimar-backup/predeploy-diffs/predeploy_${ts}.diff\" 2>/dev/null || true; \
            fi; \
            git fetch origin; \
            git reset --hard origin/main; \
            mkdir -p ssl; \
            if [ -d '/etc/letsencrypt/live/tarimimar.com.tr' ]; then \
                cp -L /etc/letsencrypt/live/tarimimar.com.tr/fullchain.pem ssl/fullchain.pem 2>/dev/null || true; \
                cp -L /etc/letsencrypt/live/tarimimar.com.tr/privkey.pem ssl/privkey.pem 2>/dev/null || true; \
            fi; \
            docker compose -f docker-compose.prod.yml up -d --build --remove-orphans; \
            ( [ -f docker-compose.ops.yml ] && docker compose -f docker-compose.ops.yml up -d --build --remove-orphans || true ); \
            docker compose -f docker-compose.prod.yml ps; \
            docker compose -f docker-compose.ops.yml ps 2>/dev/null || true"
    fi

    echo -e "  ${GREEN}✅ VPS deployment complete${NC}"

    # Update infrastructure nginx configuration
    echo -e "  → Updating infrastructure nginx configuration..."
    ssh "$VPS_HOST" "mkdir -p /home/akn/vps/infrastructure/nginx/conf.d"
    INFRA_WEBIMAR_CONF_SRC="${REPO_ROOT}/infrastructure/nginx/conf.d/webimar.conf"
    if [ -f "$INFRA_WEBIMAR_CONF_SRC" ]; then
        scp "$INFRA_WEBIMAR_CONF_SRC" "$VPS_HOST:/home/akn/vps/infrastructure/nginx/conf.d/webimar.conf"
    else
        echo -e "  ${YELLOW}⚠️  Skipping infrastructure nginx conf upload (missing: ${INFRA_WEBIMAR_CONF_SRC})${NC}"
    fi
    ssh "$VPS_HOST" "docker exec vps_nginx_main nginx -t && docker exec vps_nginx_main nginx -s reload" || echo "Infrastructure nginx reload failed (might not be running)"
    echo -e "  ${GREEN}✅ Infrastructure nginx updated${NC}"

        echo -e "\n${YELLOW}[3/5b] 🩺 Running VPS smoke checks...${NC}"
        ssh "$VPS_HOST" bash -s <<'SMOKE'
set -euo pipefail

base="http://127.0.0.1"

get_code() {
    curl -s -o /dev/null -w "%{http_code}" "$1" || echo "000"
}

wait_for_200() {
    url="$1"
    label="$2"
    timeout_seconds="${3:-120}"
    interval_seconds=3

    start_ts="$(date +%s)"
    while true; do
        code="$(get_code "$url")"
        # Nginx http→https redirect (301/302) is acceptable for smoke checks.
        if [ "$code" = "200" ] || [ "$code" = "301" ] || [ "$code" = "302" ]; then
            echo "$label -> $code"
            return 0
        fi

        now_ts="$(date +%s)"
        elapsed=$((now_ts - start_ts))
        if [ "$elapsed" -ge "$timeout_seconds" ]; then
            echo "$label -> $code (timeout ${timeout_seconds}s)"
            return 1
        fi
        sleep "$interval_seconds"
    done
}

ok=1

# API health check - gerçek endpoint kullan
wait_for_200 "$base/api/calculations/yapi-turleri/" "/api/calculations/yapi-turleri/" 120 || ok=0

code_admin="$(get_code "$base/admin/")"
code_root="$(get_code "$base/")"
echo "/admin/ -> $code_admin"
echo "/ -> $code_root"

case "$code_admin" in 200|301|302) : ;; *) ok=0 ;; esac
case "$code_root" in 200|301|302) : ;; *) ok=0 ;; esac

if [ "$ok" -ne 1 ]; then
    echo "❌ Smoke check failed"
    exit 1
fi

echo "✅ Smoke checks OK"
SMOKE
else
    echo -e "\n${YELLOW}[3/5] ⏭️  Skipping VPS deployment (--skip-vps)${NC}"
fi

# Step 4: Push to GitHub
if [ "$SKIP_GITHUB" = false ]; then
    echo -e "\n${YELLOW}[4/5] 📤 Pushing to GitHub...${NC}"

    cd "$REPO_ROOT"

    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo -e "  ${YELLOW}→ Initializing git repo at: ${REPO_ROOT}${NC}"
        git init
        git checkout -b "$GIT_BRANCH" >/dev/null 2>&1 || git branch -M "$GIT_BRANCH"
    fi

    # Ensure git identity exists (local repo config)
    if ! git config user.email >/dev/null 2>&1; then
        git config user.email "deploy@localhost"
    fi
    if ! git config user.name >/dev/null 2>&1; then
        git config user.name "Deploy Script"
    fi

    # Ensure remote points to the new repo
    if git remote get-url "$GIT_REMOTE_NAME" >/dev/null 2>&1; then
        git remote set-url "$GIT_REMOTE_NAME" "$GIT_REMOTE_URL"
    else
        git remote add "$GIT_REMOTE_NAME" "$GIT_REMOTE_URL"
    fi

    # Add changes (respects /home/akn/vps/.gitignore)
    git add -A
    
    # Check if there are changes
    if git diff --staged --quiet; then
        echo -e "  ${BLUE}No changes to commit${NC}"
    else
        # Commit with timestamp
        git commit -m "deploy: vps update ${TIMESTAMP}"

        # Push
        git push "$GIT_REMOTE_NAME" "$GIT_BRANCH"
        
        echo -e "  ${GREEN}✅ GitHub push complete${NC}"
    fi
else
    echo -e "\n${YELLOW}[4/5] ⏭️  Skipping GitHub push (--skip-github)${NC}"
fi

# Step 5: Cleanup
echo -e "\n${YELLOW}[5/5] 🧹 Cleaning up...${NC}"
if [[ "$DEPLOY_MODE" == "package" ]]; then
    rm -rf "$BUILD_DIR"
fi

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Deployment Complete!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}Summary:${NC}"
[ "$SKIP_BUILD" = false ] && echo -e "  ✅ Containers built"
[ "$SKIP_VPS" = false ] && echo -e "  ✅ Deployed to VPS: ${VPS_HOST}"
[ "$SKIP_GITHUB" = false ] && echo -e "  ✅ Pushed to GitHub"
echo -e ""
echo -e "${CYAN}URLs:${NC}"
echo -e "  🌐 Production: https://tarimimar.com.tr"
echo -e "  📊 Admin: https://tarimimar.com.tr/admin/"
echo -e "  🔧 API: https://tarimimar.com.tr/api/"
