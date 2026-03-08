#!/bin/bash
# ========================================
# Anka Platform Local Development Script
# Hızlı geliştirme için Docker olmadan servisleri başlatır
#
# Kullanım:
#   ./dev-local.sh              → native (Django + Next.js local)
#   ./dev-local.sh --vps        → tunnel modu: local frontend + VPS backend
#                                 (Google API key IP kısıtı için önerilen)
# ========================================

set +e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Proje dizini
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --vps flag kontrolü
VPS_BACKEND=false
for arg in "$@"; do
    [[ "$arg" == "--vps" ]] && VPS_BACKEND=true
done

# Tunnel portu (secure-vps-tunnel.sh default: 18010)
TUNNEL_PORT="${BACKEND_LOCAL_PORT:-18010}"

if [ "$VPS_BACKEND" = true ]; then
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  🚀 Anka Local Frontend + VPS Backend  ║${NC}"
    echo -e "${BLUE}║      (SSH Tunnel modu)                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
else
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🚀 Anka Platform Local Dev Setup      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
fi
echo -e "📂 Proje: ${PROJECT_DIR}\n"

# Cleanup fonksiyonu
cleanup() {
    echo -e "\n${YELLOW}🛑 Servisler durduruluyor...${NC}"
    
    [ ! -z "$DJANGO_PID" ] && kill $DJANGO_PID 2>/dev/null && echo "  ✓ Django kapatıldı"
    [ ! -z "$CELERY_PID" ] && kill $CELERY_PID 2>/dev/null && echo "  ✓ Celery kapatıldı"
    [ ! -z "$NEXTJS_PID" ] && kill $NEXTJS_PID 2>/dev/null && echo "  ✓ Next.js kapatıldı"
    [ ! -z "$TUNNEL_PID" ] && kill $TUNNEL_PID 2>/dev/null && echo "  ✓ SSH tunnel kapatıldı"

    # Port temizliği
    fuser -k 8000/tcp 2>/dev/null
    fuser -k 3000/tcp 2>/dev/null
    fuser -k 3001/tcp 2>/dev/null
    fuser -k 5555/tcp 2>/dev/null

    echo -e "${GREEN}✅ Tüm servisler kapatıldı.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Docker kontrol ve cleanup
echo -e "${YELLOW}🐳 Docker container'ları kontrol ediliyor...${NC}"
docker compose ps --services --filter "status=running" 2>/dev/null | grep -q . && \
    docker compose down --remove-orphans > /dev/null 2>&1 && echo -e "  ✓ Docker container'ları durduruldu" || echo -e "  ℹ️  Docker container'ları zaten duruyor"

# Workspace seviyesinde tüm projeleri durdur (port çakışmasını önle)
if [ -f "../../scripts/down.sh" ]; then
    echo -e "${YELLOW}⚠️  Workspace projelerini durduruluyor...${NC}"
    (cd ../.. && bash scripts/down.sh > /dev/null 2>&1 || true)
    sleep 1
fi

# Environment setup
if [ -f .env.local.native ]; then
    ln -sf .env.local.native .env
    echo -e "${GREEN}✓ .env.local.native linked${NC}"
else
    cp .env.example .env 2>/dev/null || echo -e "${YELLOW}⚠️  .env created (defaults)${NC}"
fi

# Load Environment Variables into shell
set -a
source .env
set +a
echo -e "${GREEN}✓ Environment variables loaded from .env${NC}"

# Port temizliği
echo -e "\n${YELLOW}🔍 Port temizliği (8000, 3000, 3001, 5555)...${NC}"
for port in 8000 3000 3001 5555; do
    fuser -k $port/tcp 2>/dev/null && echo "  ✓ Port $port temizlendi" || true
done

# ==========================================
# 1. BACKEND SETUP  (VPS modunda atlanır)
# ==========================================
if [ "$VPS_BACKEND" = true ]; then
    echo -e "\n${BLUE}🔒 [1/3] VPS Backend — SSH Tunnel açılıyor (port ${TUNNEL_PORT})...${NC}"
    TUNNEL_SCRIPT="${PROJECT_DIR}/scripts/secure-vps-tunnel.sh"
    if [ ! -f "$TUNNEL_SCRIPT" ]; then
        echo -e "${RED}  ❌ Tunnel scripti bulunamadı: $TUNNEL_SCRIPT${NC}"
        exit 1
    fi
    bash "$TUNNEL_SCRIPT" backend > "${PROJECT_DIR}/tunnel.log" 2>&1 &
    TUNNEL_PID=$!
    echo -e "  PID: $TUNNEL_PID  (log: tail -f tunnel.log)"

    echo -e "${YELLOW}  ⏳ Tunnel sağlık kontrolü (15 saniye)...${NC}"
    TUNNEL_OK=false
    for i in {1..15}; do
        sleep 1
        if curl -s "http://127.0.0.1:${TUNNEL_PORT}/api/health/" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ VPS backend tunnel hazır → http://127.0.0.1:${TUNNEL_PORT}${NC}"
            TUNNEL_OK=true
            break
        fi
        echo -n "."
    done
    if [ "$TUNNEL_OK" != true ]; then
        echo -e "\n${YELLOW}  ⚠️  Tunnel henüz cevap vermiyor (VPS kapalı mı?). Devam ediliyor...${NC}"
        echo -e "${YELLOW}     ssh anka-vps bağlantısını kontrol edin.${NC}"
    fi
    API_URL="http://127.0.0.1:${TUNNEL_PORT}"
else
    echo -e "\n${BLUE}📡 [1/3] Django Backend Kurulumu...${NC}"

    BACKEND_DIR="${PROJECT_DIR}/services/backend"

    # Venv oluştur veya aktifleştir
    if [ ! -d "$BACKEND_DIR/venv" ]; then
        echo -e "${YELLOW}  🐍 Virtual environment oluşturuluyor...${NC}"
        cd "$BACKEND_DIR"
        python3 -m venv venv
        source venv/bin/activate
        pip install -U pip setuptools wheel
        echo -e "${YELLOW}  📦 Dependencies yükleniyor...${NC}"
        pip install -r requirements.txt
    else
        cd "$BACKEND_DIR"
        source venv/bin/activate
        echo -e "${GREEN}  ✓ Venv aktifleştirildi${NC}"
    fi

    # Migrations
    echo -e "${YELLOW}  🔄 Database migrations...${NC}"
    python manage.py migrate --noinput 2>&1 | grep -E "(Applying|OK|No migrations)" || true

    # Django server
    echo -e "${YELLOW}  🚀 Django server başlatılıyor (port 8000)...${NC}"
    python manage.py runserver 0.0.0.0:8000 > "${PROJECT_DIR}/django.log" 2>&1 &
    DJANGO_PID=$!

    # Health check
    echo -e "${YELLOW}  ⏳ API sağlık kontrolü (10 saniye)...${NC}"
    for i in {1..10}; do
        sleep 1
        if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Django API ready (PID: $DJANGO_PID)${NC}"
            DJANGO_OK=true
            break
        elif curl -s http://localhost:8000/ > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Django ready (PID: $DJANGO_PID)${NC}"
            DJANGO_OK=true
            break
        fi
        echo -n "."
    done

    [ "$DJANGO_OK" != true ] && echo -e "${YELLOW}  ⚠️  Still starting... (tail -f django.log)${NC}"
    API_URL="http://localhost:8000"
fi

# ==========================================
# 2. FRONTEND SETUP
# ==========================================
echo -e "\n${BLUE}🏠 [2/3] Next.js Frontend Kurulumu...${NC}"

FRONTEND_DIR="${PROJECT_DIR}/services/frontend"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}  📦 npm install...${NC}"
    cd "$FRONTEND_DIR"
    npm install --prefer-offline
fi

echo -e "${YELLOW}  🚀 Next.js dev server başlatılıyor (port 3000)...${NC}"
cd "$FRONTEND_DIR"
PORT=3000 \
NEXT_PUBLIC_GOOGLE_CLIENT_ID="${NEXT_PUBLIC_GOOGLE_CLIENT_ID}" \
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY="${NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}" \
NEXT_PUBLIC_API_URL="${API_URL}" \
NEXT_PUBLIC_API_BASE_URL="${API_URL}/api" \
NEXT_INTERNAL_BACKEND_URL="${API_URL}" \
npm run dev > "${PROJECT_DIR}/nextjs.log" 2>&1 &
NEXTJS_PID=$!

sleep 5
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Next.js ready (PID: $NEXTJS_PID)${NC}"
else
    echo -e "${YELLOW}  ⚠️  Next.js başlanıyor...${NC}"
fi

# ==========================================
# 3. CELERY (Optional)
# ==========================================
echo -e "\n${BLUE}⚙️  [3/3] Celery Worker (Optional)${NC}"
echo -e "${YELLOW}  Not started in dev (manual: cd services/backend && celery -A celery_app worker)${NC}"

# ==========================================
# READY
# ==========================================
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ Development Ready!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}📍 URLs:${NC}"
echo -e "  🏠 Frontend:      http://localhost:3000"
echo -e "  🔧 API:           ${API_URL}/api"
echo -e "  📊 Admin:         ${API_URL}/admin"
echo -e "  📖 Docs:          ${API_URL}/api/docs"
if [ "$VPS_BACKEND" = true ]; then
    echo -e ""
    echo -e "${YELLOW}  ⚡ Mod: local frontend + VPS backend (SSH tunnel :${TUNNEL_PORT})${NC}"
    echo -e "${YELLOW}  📋 Tunnel log: tail -f tunnel.log${NC}"
fi
echo -e ""
echo -e "${BLUE}📋 Logs:${NC}"
echo -e "  tail -f nextjs.log"
[ "$VPS_BACKEND" != true ] && echo -e "  tail -f django.log"
echo -e ""
echo -e "${BLUE}🛑 Stop: Ctrl+C${NC}\n"

wait
