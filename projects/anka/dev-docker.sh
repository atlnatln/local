#!/bin/bash
# ========================================
# Anka Platform Docker Development
# Docker Compose ile servisleri başlatır
#
# Kullanım:
#   ./dev-docker.sh              → tüm servisler Docker'da
#   ./dev-docker.sh --build      → zorunlu rebuild ile Docker
#   ./dev-docker.sh --vps-backend
#                                → local frontend container + VPS backend (SSH tunnel)
#                                  (Google API key IP kısıtı için önerilen)
# ========================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Flag parsing
BUILD_FLAG=""
VPS_BACKEND=false
for arg in "$@"; do
    case "$arg" in
        --build)        BUILD_FLAG="--build" ;;
        --vps-backend)  VPS_BACKEND=true ;;
    esac
done

TUNNEL_PORT="${BACKEND_LOCAL_PORT:-18010}"

if [ "$VPS_BACKEND" = true ]; then
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  🐳 Anka Docker Frontend + VPS Backend ║${NC}"
    echo -e "${BLUE}║      (SSH Tunnel modu)                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
else
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🐳 Anka Platform Docker Dev Setup     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
fi

# Docker kontrol
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker çalışmıyor. Docker Desktop'ı başlatın.${NC}"
    exit 1
fi

# Environment setup
if [ -f .env.local.docker ]; then
    ln -sf .env.local.docker .env
    echo -e "${GREEN}✓ .env.local.docker linked${NC}"
else
    cp .env.example .env 2>/dev/null || echo -e "${YELLOW}⚠️  .env created (defaults)${NC}"
fi

echo -e ""

# Local dev (dev-local.sh) kontrolü ve temizliği
echo -e "${YELLOW}🧹 Local dev servisleri kontrol ediliyor (8000, 3000, 3001, 5555)...${NC}"
fuser -k 8000/tcp 3000/tcp 3001/tcp 5555/tcp > /dev/null 2>&1 && \
    echo -e "  ✓ Local dev portları temizlendi" || echo -e "  ℹ️  Local dev portları zaten boş"

# Stop existing Anka containers only
echo -e "${YELLOW}🛑 Existing Anka containers durduruluyor...${NC}"
docker compose down --remove-orphans > /dev/null 2>&1 || true
echo -e "${GREEN}  ✓ Anka containerları durduruldu${NC}"

# Not stopping other workspace projects to allow simultaneous running
echo -e "${BLUE}ℹ️  Workspace'deki diğer projeler çalışmaya devam edecek${NC}"
# Build ve start
if [ "$VPS_BACKEND" = true ]; then
    # ── VPS BACKEND MODU ────────────────────────────────────────────────────
    echo -e "\n${BLUE}🔒 SSH Tunnel açılıyor → VPS backend (port ${TUNNEL_PORT})...${NC}"
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
    for i in $(seq 1 15); do
        sleep 1
        if curl -s "http://127.0.0.1:${TUNNEL_PORT}/api/health/" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ VPS backend tunnel hazır → http://127.0.0.1:${TUNNEL_PORT}${NC}"
            TUNNEL_OK=true
            break
        fi
        echo -n "."
    done
    [ "$TUNNEL_OK" != true ] && echo -e "\n${YELLOW}  ⚠️  Tunnel cevap vermiyor; devam ediliyor...${NC}"

    # Frontend container'ını yalnızca VPS URL'leri ile başlat
    echo -e "\n${YELLOW}🔨 Frontend container başlatılıyor (--no-deps)...${NC}"
    NEXT_PUBLIC_API_URL="http://localhost:${TUNNEL_PORT}" \
    NEXT_PUBLIC_API_BASE_URL="http://localhost:${TUNNEL_PORT}/api" \
    NEXT_INTERNAL_BACKEND_URL="http://host.docker.internal:${TUNNEL_PORT}" \
    docker compose up $BUILD_FLAG -d --no-deps frontend
else
    # ── NORMAL MOD ──────────────────────────────────────────────────────────
    echo -e "\n${YELLOW}🔨 Building ve starting services...${NC}"
    docker compose up $BUILD_FLAG -d --remove-orphans

    if [ -z "$BUILD_FLAG" ]; then
        echo -e "${BLUE}ℹ️  Hızlı mod: mevcut image/cache kullanıldı (zorunlu rebuild yok)${NC}"
        echo -e "${BLUE}ℹ️  Zorunlu rebuild için: ./dev-docker.sh --build${NC}"
    fi
fi

# Wait function
wait_for_service() {
    local name="$1"
    local url="$2"
    local max=30
    local attempt=0
    
    echo -n "  ⏳ $name waiting"
    while [ $attempt -lt $max ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "\r  ${GREEN}✓${NC} $name ready            "
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
        echo -n "."
    done
    
    echo -e "\r  ${YELLOW}⚠️ ${NC}$name still starting...  "
    return 1
}

# Check services
echo -e "\n${YELLOW}Sağlık kontrolleri...${NC}"
if [ "$VPS_BACKEND" = true ]; then
    wait_for_service "Next.js (Docker)" "http://localhost:3100"
else
    wait_for_service "Django API" "http://localhost:8100/api/health/"
    wait_for_service "Next.js" "http://localhost:3100"
fi

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ Docker Environment Ready!      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

if [ "$VPS_BACKEND" = true ]; then
    echo -e "${BLUE}📍 URLs:${NC}"
    echo -e "  🏠 Frontend:    http://localhost:3100"
    echo -e "  🔧 API (VPS):   http://127.0.0.1:${TUNNEL_PORT}/api"
    echo -e "  📊 Admin (VPS): http://127.0.0.1:${TUNNEL_PORT}/admin"
    echo -e ""
    echo -e "${YELLOW}  ⚡ Mod: Docker frontend + VPS backend (SSH tunnel :${TUNNEL_PORT})${NC}"
    echo -e "${YELLOW}  📋 Tunnel log: tail -f tunnel.log${NC}"
else
    echo -e "${BLUE}📍 URLs:${NC}"
    echo -e "  🏠 Frontend:    http://localhost:3100"
    echo -e "  🔧 API:         http://localhost:8100/api"
    echo -e "  📊 Admin:       http://localhost:8100/admin"
    echo -e "  📖 Docs:        http://localhost:8100/api/docs"
    echo -e "  🗄️  PostgreSQL:  postgres://postgres:postgres@localhost:5433/anka"
    echo -e "  ⚡ Redis:       redis://localhost:6380"
    echo -e "  💽 MinIO:       http://localhost:9000 (admin) & http://localhost:9001 (console)"
fi
echo -e ""

echo -e "${BLUE}📋 Commands:${NC}"
echo -e "  Logs:    docker compose logs -f frontend"
echo -e "  Status:  docker compose ps"
[ "$VPS_BACKEND" != true ] && echo -e "  Shell:   docker compose exec backend bash"
[ "$VPS_BACKEND" != true ] && echo -e "  Django:  docker compose exec backend python manage.py shell"
echo -e "  Stop:    docker compose down"
echo -e ""

# Services status
echo -e "${BLUE}📊 Services:${NC}"
docker compose ps

echo -e "\n${GREEN}Ready! 🚀${NC}"

