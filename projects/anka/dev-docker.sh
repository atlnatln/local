#!/bin/bash
# ========================================
# Anka Platform Docker Development
# Docker Compose ile servisleri başlatır
# ========================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🐳 Anka Platform Docker Dev Setup     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

BUILD_FLAG=""
if [ "${1:-}" = "--build" ]; then
    BUILD_FLAG="--build"
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
echo -e "\n${YELLOW}🔨 Building ve starting services...${NC}"
docker compose up $BUILD_FLAG -d --remove-orphans

if [ -z "$BUILD_FLAG" ]; then
    echo -e "${BLUE}ℹ️  Hızlı mod: mevcut image/cache kullanıldı (zorunlu rebuild yok)${NC}"
    echo -e "${BLUE}ℹ️  Zorunlu rebuild için: ./dev-docker.sh --build${NC}"
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
wait_for_service "Django API" "http://localhost:8100/api/health/"
wait_for_service "Next.js" "http://localhost:3100"

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ Docker Environment Ready!      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}📍 URLs:${NC}"
echo -e "  🏠 Frontend:    http://localhost:3100"
echo -e "  🔧 API:         http://localhost:8100/api"
echo -e "  📊 Admin:       http://localhost:8100/admin"
echo -e "  📖 Docs:        http://localhost:8100/api/docs"
echo -e "  🗄️  PostgreSQL:  postgres://postgres:postgres@localhost:5433/anka"
echo -e "  ⚡ Redis:       redis://localhost:6380"
echo -e "  💽 MinIO:       http://localhost:9000 (admin) & http://localhost:9001 (console)"
echo -e ""

echo -e "${BLUE}📋 Commands:${NC}"
echo -e "  Logs:    docker compose logs -f"
echo -e "  Status:  docker compose ps"
echo -e "  Shell:   docker compose exec backend bash"
echo -e "  Django:  docker compose exec backend python manage.py shell"
echo -e "  Stop:    docker compose down"
echo -e ""

# Services status
echo -e "${BLUE}📊 Services:${NC}"
docker compose ps

echo -e "\n${GREEN}Ready! 🚀${NC}"

