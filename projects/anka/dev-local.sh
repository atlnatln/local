#!/bin/bash
# ========================================
# Anka Platform Local Development Script
# Hızlı geliştirme için Docker olmadan servisleri başlatır
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

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 Anka Platform Local Dev Setup      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo -e "📂 Proje: ${PROJECT_DIR}\n"

# Cleanup fonksiyonu
cleanup() {
    echo -e "\n${YELLOW}🛑 Servisler durduruluyor...${NC}"
    
    [ ! -z "$DJANGO_PID" ] && kill $DJANGO_PID 2>/dev/null && echo "  ✓ Django kapatıldı"
    [ ! -z "$CELERY_PID" ] && kill $CELERY_PID 2>/dev/null && echo "  ✓ Celery kapatıldı"
    [ ! -z "$NEXTJS_PID" ] && kill $NEXTJS_PID 2>/dev/null && echo "  ✓ Next.js kapatıldı"

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

# Port temizliği
echo -e "\n${YELLOW}🔍 Port temizliği (8000, 3000, 3001, 5555)...${NC}"
for port in 8000 3000 3001 5555; do
    fuser -k $port/tcp 2>/dev/null && echo "  ✓ Port $port temizlendi" || true
done

# ==========================================
# 1. BACKEND SETUP
# ==========================================
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
PORT=3000 npm run dev > "${PROJECT_DIR}/nextjs.log" 2>&1 &
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
echo -e "  🔧 API:           http://localhost:8000/api"
echo -e "  📊 Admin:         http://localhost:8000/admin"
echo -e "  📖 Docs:          http://localhost:8000/api/docs"
echo -e ""
echo -e "${BLUE}📋 Logs:${NC}"
echo -e "  tail -f django.log"
echo -e "  tail -f nextjs.log"
echo -e ""
echo -e "${BLUE}🛑 Stop: Ctrl+C${NC}\n"

wait
