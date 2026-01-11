#!/bin/bash
# ========================================
# Webimar Local Development with Docker
# Development ortamı için compose
# ========================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🐳 Webimar Docker Dev Environment     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Set up environment for Docker development
if [ -f .env.local ]; then
    ln -sf .env.local .env
    echo -e "${GREEN}📦 Linked .env.local → .env (REACT_APP_API_BASE_URL=$(grep REACT_APP_API_BASE_URL .env.local | cut -d'=' -f2))${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local not found, using defaults${NC}"
fi

# Stop any running containers first (workspace aware)
echo -e "\n${YELLOW}🛑 Stopping existing containers...${NC}"
docker compose down --remove-orphans > /dev/null 2>&1 || true

# Stop other workspace projects to avoid port conflicts
if [ -f "../../scripts/down.sh" ]; then
    echo -e "${YELLOW}⚠️  Workspace projelerini durduruluyor...${NC}"
    (cd ../.. && bash scripts/down.sh > /dev/null 2>&1 || true)
    sleep 2
fi

# Build and start
echo -e "\n${YELLOW}🔨 Building and starting containers...${NC}"
docker compose up --build -d --remove-orphans

# Wait for services to be ready
echo -e "\n${YELLOW}⏳ Waiting for services to be ready...${NC}"

# Function to wait for HTTP endpoint
wait_for_endpoint() {
    local url="$1"
    local service_name="$2"
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ $service_name ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
        echo -n "."
    done
    
    echo -e "\n${YELLOW}  ⚠️  $service_name timeout (still starting...)${NC}"
    return 1
}

# Check API health via nginx proxy
wait_for_endpoint "http://localhost/api/calculations/health/" "Django API"

# Check Next.js via nginx proxy  
wait_for_endpoint "http://localhost" "Next.js"

# Check React direct port first (nginx routing may take longer)
wait_for_endpoint "http://localhost:3001" "React SPA (direct)"

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🚀 Docker Environment Ready!       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}Services:${NC}"
echo -e "  🌐 Main site:    http://localhost (Next.js via nginx)"
echo -e "  📊 Admin:        http://localhost/admin/ (Django via nginx)"
echo -e "  🔧 API:          http://localhost/api/ (Django via nginx)"
echo -e "  ⚛️  React SPA:    http://localhost/hesaplama (React via nginx)"
echo -e ""
echo -e "${BLUE}Test Links:${NC}"
echo -e "  🧪 API Health:   http://localhost/api/health/"
echo -e "  🏗️ Next.js:      http://localhost:3000 (direct)"
echo -e "  ⚛️  React SPA:    http://localhost:3001 (direct)"
echo -e ""
echo -e "${BLUE}Commands:${NC}"
echo -e "  📋 Logs:   docker compose logs -f"
echo -e "  🛑 Stop:   docker compose down --remove-orphans"
echo -e "  📊 Status: docker compose ps"

# Show container status
echo -e "\n${YELLOW}📊 Container Status:${NC}"
docker compose ps

# Housekeeping: remove unused images and build cache to save disk
echo -e "\n${YELLOW}🧹 Local cleanup: pruning unused images and build cache...${NC}"
docker image prune -a -f > /dev/null 2>&1 || true
docker builder prune -f > /dev/null 2>&1 || true

echo -e "\n${GREEN}✅ Development environment is ready!${NC}"
