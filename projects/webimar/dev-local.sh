#!/bin/bash
# ========================================
# Webimar Local Development Script
# Hızlı geliştirme için Docker olmadan servisleri başlatır
# ========================================

# Hata durumunda durma, cleanup yapabilmek için
set +e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Proje dizini (Scriptin olduğu yer)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Komut kontrol helper
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Port kontrol helper
port_in_use() {
    local port="$1"
    if command_exists lsof; then
        lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
        return $?
    elif command_exists ss; then
        ss -ltnp | awk '{print $4}' | grep -q ":${port}$"
        return $?
    elif command_exists fuser; then
        fuser -n tcp "$port" >/dev/null 2>&1
        return $?
    fi
    return 1
}

free_port() {
    local port="$1"
    if command_exists fuser; then
        fuser -k "$port"/tcp >/dev/null 2>&1 || true
    elif command_exists lsof; then
        local pids
        pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
        if [ -n "$pids" ]; then
            kill $pids 2>/dev/null || true
        fi
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Webimar Local Dev Environment      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo -e "📂 Proje Dizini: ${PROJECT_DIR}"

# Gerekli komutlar
MISSING=false
for cmd in python3 curl node npm; do
    if ! command_exists "$cmd"; then
        echo -e "${RED}❌ Gerekli komut bulunamadı: ${cmd}${NC}"
        MISSING=true
    fi
done

if [ "$MISSING" = true ]; then
    echo -e "${YELLOW}⚠️  Lütfen eksik bağımlılıkları yükleyip tekrar deneyin.${NC}"
    exit 1
fi

# Cleanup fonksiyonu
cleanup() {
    echo -e "\n${YELLOW}🛑 Servisler durduruluyor...${NC}"
    
    if [ ! -z "$DJANGO_PID" ]; then
        echo "  → Django (PID: $DJANGO_PID) durduruluyor..."
        kill $DJANGO_PID 2>/dev/null
    fi
    
    if [ ! -z "$NEXTJS_PID" ]; then
        echo "  → Next.js (PID: $NEXTJS_PID) durduruluyor..."
        kill $NEXTJS_PID 2>/dev/null
    fi
    
    if [ ! -z "$REACT_PID" ]; then
        echo "  → React (PID: $REACT_PID) durduruluyor..."
        kill $REACT_PID 2>/dev/null
    fi

    # Port temizliği (Garanti olsun)
    fuser -k 8000/tcp 2>/dev/null
    fuser -k 3000/tcp 2>/dev/null
    fuser -k 3001/tcp 2>/dev/null

    echo -e "${GREEN}✅ Tüm servisler kapatıldı.${NC}"
    exit 0
}

# Arka plan modu kontrolü
RUN_IN_BACKGROUND=false
if [[ "$1" == "--background" || "$1" == "-b" ]]; then
    RUN_IN_BACKGROUND=true
fi

# Ctrl+C yakala (arka plan modunda kapanışı engelle)
if [ "$RUN_IN_BACKGROUND" != true ]; then
    trap cleanup SIGINT SIGTERM
fi

# Docker container'ları durdur (eğer çalışıyorsa)
echo -e "\n${YELLOW}🛑 Docker container'ları kontrol ediliyor...${NC}"
if command_exists docker && docker info >/dev/null 2>&1; then
    if docker compose -f docker-compose.prod.yml ps --services --filter "status=running" 2>/dev/null | grep -q .; then
        echo -e "${YELLOW}⚠️  Docker container'ları durduruluyor...${NC}"
        docker compose -f docker-compose.prod.yml down --remove-orphans > /dev/null 2>&1 || true
        sleep 2
    fi

    # Regular docker-compose.yml kontrolü de ekle
    if docker compose ps --services --filter "status=running" 2>/dev/null | grep -q .; then
        echo -e "${YELLOW}⚠️  Regular Docker container'ları durduruluyor...${NC}"
        docker compose down --remove-orphans > /dev/null 2>&1 || true
        sleep 2
    fi
else
    echo -e "${YELLOW}ℹ️  Docker çalışmıyor, container kontrolü atlandı.${NC}"
fi

# Set up environment for native development  
if [ -f .env.local.native ]; then
    ln -sf .env.local.native .env
    echo -e "${GREEN}📦 Linked .env.local.native → .env (REACT_APP_API_BASE_URL=$(grep REACT_APP_API_BASE_URL .env.local.native | cut -d'=' -f2))${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local.native not found, using code defaults${NC}"
fi

# Port kontrolü ve temizliği
echo -e "\n${YELLOW}🔍 Port kontrolü yapılıyor...${NC}"
for port in 8000 3000 3001; do
    if port_in_use "$port"; then
        echo -e "${YELLOW}⚠️  Port $port kullanımda, temizleniyor...${NC}"
        free_port "$port"
        sleep 1
    fi
done

# 1. Django API Başlat
echo -e "\n${BLUE}📡 [1/3] Django API başlatılıyor...${NC}"
cd "${PROJECT_DIR}/webimar-api"

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}  ⚠️  Virtual environment yok, oluşturuluyor...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null 2>&1 || true

# Requirements kontrolü ve kurulumu
if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}  ⚠️  Python paketleri eksik, yükleniyor...${NC}"
    pip install -r requirements.txt
fi

# Django migrations kontrol
echo -e "${YELLOW}  🔄 Django migrations kontrol ediliyor...${NC}"
python manage.py migrate --run-syncdb > /dev/null 2>&1 || true

# Django'yu python ile çalıştır (detaylı log için)
echo -e "${YELLOW}  🚀 Django server başlatılıyor...${NC}"
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# API'nin başladığını kontrol et (daha uzun bekleme)
echo -e "${YELLOW}  ⏳ API sağlık kontrolü (10 saniye)...${NC}"
for i in {1..10}; do
    sleep 1
    if curl -s -f http://localhost:8000/api/calculations/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Django API sağlıklı (PID: $DJANGO_PID) -> http://localhost:8000${NC}"
        API_READY=true
        break
    fi
    echo -n "."
done

if [ "$API_READY" != true ]; then
    echo -e "\n${RED}  ❌ Django API sağlık kontrolü başarısız!${NC}"
    echo -e "${YELLOW}     Django loglarını kontrol edin. Manuel test: curl http://localhost:8000/api/calculations/health/${NC}"
    # API başarısız olsa da diğer servisleri başlat
fi

# 2. Next.js Başlat
echo -e "\n${BLUE}🏠 [2/3] Next.js başlatılıyor...${NC}"
cd "${PROJECT_DIR}/webimar-nextjs"

# Node modules kontrolü
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}  📦 npm install çalıştırılıyor...${NC}"
    npm install || npm install --legacy-peer-deps
fi

# Next.js'i geliştirme modunda başlat
echo -e "${YELLOW}  🚀 Next.js dev server başlatılıyor...${NC}"
HOST=0.0.0.0 PORT=3000 npm run dev &
NEXTJS_PID=$!

# Next.js sağlık kontrolü
echo -e "${YELLOW}  ⏳ Next.js sağlık kontrolü (5 saniye)...${NC}"
sleep 5
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Next.js sağlıklı (PID: $NEXTJS_PID) -> http://localhost:3000${NC}"
else
    echo -e "${YELLOW}  ⚠️  Next.js sağlık kontrolü beklemede...${NC}"
fi

# 3. React SPA Başlat
echo -e "\n${BLUE}⚛️  [3/3] React SPA başlatılıyor...${NC}"
cd "${PROJECT_DIR}/webimar-react"

# Node modules kontrolü
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}  📦 npm install çalıştırılıyor...${NC}"
    npm install || npm install --legacy-peer-deps
fi

# React'i başlat
echo -e "${YELLOW}  🚀 React dev server başlatılıyor...${NC}"
BROWSER=none PORT=3001 npm start &
REACT_PID=$!

# React sağlık kontrolü
echo -e "${YELLOW}  ⏳ React sağlık kontrolü (5 saniye)...${NC}"
sleep 5
if curl -s -f http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ React sağlıklı (PID: $REACT_PID) -> http://localhost:3001${NC}"
else
    echo -e "${YELLOW}  ⚠️  React sağlık kontrolü beklemede...${NC}"
fi

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🚀 Development Environment Ready    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}URLs:${NC}"
echo -e "  🏠 Next.js (Homepage):     http://localhost:3000"
echo -e "  ⚛️  React SPA (Calculators): http://localhost:3001"
echo -e "  🔧 Django API:             http://localhost:8000/api/"
echo -e "  📊 Django Admin:           http://localhost:8000/admin/"
echo -e ""
echo -e "${BLUE}Test Links:${NC}"
echo -e "  🧪 API Health:             http://localhost:8000/api/calculations/health/"
echo -e "  🏗️ Calculator Example:     http://localhost:3001/sera"
echo -e ""
echo -e "${YELLOW}💡 Servis loglarını görmek için ayrı terminalde:${NC}"
echo -e "   Django: cd webimar-api && tail -f nohup.out"
echo -e "   React:  cd webimar-react && npm start"
echo -e ""
echo -e "${YELLOW}🛑 Çıkmak için Ctrl+C'ye basın${NC}"

# Arka plan modunda PID'leri yaz ve çık
if [ "$RUN_IN_BACKGROUND" = true ]; then
    PID_FILE="${PROJECT_DIR}/.dev-local.pids"
    echo "DJANGO_PID=${DJANGO_PID}" > "$PID_FILE"
    echo "NEXTJS_PID=${NEXTJS_PID}" >> "$PID_FILE"
    echo "REACT_PID=${REACT_PID}" >> "$PID_FILE"
    echo -e "${GREEN}✅ Arka plan modu aktif. PID dosyası: ${PID_FILE}${NC}"
    exit 0
fi

# Scriptin kapanmasını engelle ve processleri bekle
wait
