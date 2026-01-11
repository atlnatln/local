#!/bin/bash
# ========================================
# Webimar Build & Package Script
# Container'ları build edip tek tar dosyası olarak paketler
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${PROJECT_DIR}/build-output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="webimar-${TIMESTAMP}.tar.gz"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Webimar Build & Package Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Create build directory
mkdir -p "${BUILD_DIR}"

# Step 1: Build all containers
echo -e "\n${YELLOW}[1/5] Building Docker containers...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache

# Step 2: Save container images to tar files
echo -e "\n${YELLOW}[2/5] Exporting container images...${NC}"
mkdir -p "${BUILD_DIR}/images"

# Get image names from compose
IMAGES=(
    "webimar-webimar-api:latest"
    "webimar-webimar-react:latest"
    "webimar-webimar-nextjs:latest"
    "webimar-nginx:latest"
)

for IMAGE in "${IMAGES[@]}"; do
    IMAGE_FILE=$(echo "$IMAGE" | tr '/:' '_')
    echo -e "  → Exporting ${IMAGE}..."
    docker save "$IMAGE" -o "${BUILD_DIR}/images/${IMAGE_FILE}.tar"
done

# Step 3: Copy configuration files
echo -e "\n${YELLOW}[3/5] Copying configuration files...${NC}"
mkdir -p "${BUILD_DIR}/config"
cp docker-compose.prod.yml "${BUILD_DIR}/docker-compose.prod.yml"
cp -r docker/nginx "${BUILD_DIR}/config/nginx"
cp .env.production "${BUILD_DIR}/.env.example"

# Create deployment script for VPS
cat > "${BUILD_DIR}/deploy-vps.sh" << 'DEPLOY_SCRIPT'
#!/bin/bash
# VPS Deployment Script
set -e

echo "🚀 Loading Docker images..."
for tar_file in images/*.tar; do
    echo "  → Loading $tar_file..."
    docker load -i "$tar_file"
done

echo "📦 Starting services..."
docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
docker compose -f docker-compose.prod.yml up -d

echo "✅ Deployment complete!"
docker compose -f docker-compose.prod.yml ps
DEPLOY_SCRIPT
chmod +x "${BUILD_DIR}/deploy-vps.sh"

# Step 4: Create the package
echo -e "\n${YELLOW}[4/5] Creating package: ${PACKAGE_NAME}${NC}"
cd "${BUILD_DIR}"
tar -czvf "../${PACKAGE_NAME}" .

# Step 5: Cleanup
echo -e "\n${YELLOW}[5/5] Cleaning up...${NC}"
rm -rf "${BUILD_DIR}"

# Summary
PACKAGE_SIZE=$(du -h "${PROJECT_DIR}/${PACKAGE_NAME}" | cut -f1)
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Package: ${BLUE}${PACKAGE_NAME}${NC}"
echo -e "Size: ${BLUE}${PACKAGE_SIZE}${NC}"
echo -e "Location: ${BLUE}${PROJECT_DIR}/${PACKAGE_NAME}${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Run: ${BLUE}./deploy.sh${NC} to deploy to VPS and push to GitHub"
echo -e "  2. Or manually: ${BLUE}scp ${PACKAGE_NAME} user@vps:/path/${NC}"
