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
if [ -f .env.local.docker ]; then
    ln -sf .env.local.docker .env
    echo -e "${GREEN}📦 Linked .env.local.docker → .env (REACT_APP_API_BASE_URL=$(grep REACT_APP_API_BASE_URL .env.local.docker | cut -d'=' -f2))${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local.docker not found, using defaults${NC}"
fi

# Stop any running containers first
echo -e "\n${YELLOW}🛑 Stopping existing containers...${NC}"
docker compose down --remove-orphans > /dev/null 2>&1 || true

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

    get_code() {
        curl -s -o /dev/null -w "%{http_code}" "$1" 2>/dev/null || echo "000"
    }
    
    while [ $attempt -lt $max_attempts ]; do
        code="$(get_code "$url")"
        case "$code" in
            200|301|302|307|308)
                echo -e "${GREEN}  ✓ $service_name ready ($code)${NC}"
                return 0
                ;;
        esac
        attempt=$((attempt + 1))
        sleep 2
        echo -n "."
    done
    
    echo -e "\n${YELLOW}  ⚠️  $service_name timeout (still starting...)${NC}"
    return 1
}

# Check API health
wait_for_endpoint "http://localhost/api/calculations/health/" "Django API"

# Check Next.js
wait_for_endpoint "http://localhost" "Next.js"

# Check React via nginx routing (test with specific route)
wait_for_endpoint "http://localhost/sera" "React SPA"

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🚀 Docker Environment Ready!       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}Services:${NC}"
echo -e "  🌐 Main site:    http://localhost (Next.js)"
echo -e "  📊 Admin:        http://localhost/admin/ (Django)"
echo -e "  🔧 API:          http://localhost/api/ (Django)"
echo -e "  ⚛️  React SPA:    http://localhost/{yapi-turu} (via nginx routing)"
echo -e ""
echo -e "${BLUE}Test Links:${NC}"
echo -e "  🧪 API Health:   http://localhost/api/calculations/health/"
echo -e "  🏗️ Calculator:   http://localhost/sera"
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
