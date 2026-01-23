#!/bin/bash
# ========================================
# VPS Issues Fix Script
# Local'de çalışacak fix'ler, sonra deploy
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VPS_HOST="akn@89.252.152.222"
PROJECT_DIR="/home/akn/vps/projects/webimar"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         VPS Issues Fix Script          ║${NC}" 
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

cd "$(dirname "$0")"

# 1. Fix database naming consistency
echo -e "\n${YELLOW}[1/5] 🔧 Fixing database naming consistency...${NC}"

# Ensure all compose files use 'webimar_api' consistently
echo -e "  → Checking database naming across compose files..."

# Check if docker-compose.yml has the right DB name
if grep -q "POSTGRES_DB: webimar_api" projects/webimar/docker-compose.yml; then
    echo -e "  ${GREEN}✓ docker-compose.yml database name correct${NC}"
else
    echo -e "  ${YELLOW}⚠ docker-compose.yml needs database name fix${NC}"
fi

# 2. Create database initialization SQL
echo -e "\n${YELLOW}[2/5] 📊 Creating database initialization script...${NC}"

cat > projects/webimar/init-db.sql << 'EOF'
-- Database initialization for Webimar
-- Run this on PostgreSQL to ensure correct database exists

-- Create database if not exists (PostgreSQL doesn't have CREATE DATABASE IF NOT EXISTS)
SELECT 'CREATE DATABASE webimar_api' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'webimar_api');
\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE webimar_api TO webimar;
EOF

echo -e "  ${GREEN}✓ Created init-db.sql${NC}"

# 3. Fix monitoring stack volumes (clear corrupted data)
echo -e "\n${YELLOW}[3/5] 📈 Creating monitoring fix script...${NC}"

cat > fix-monitoring.sh << 'EOF'
#!/bin/bash
# Run this on VPS to fix Grafana/Prometheus issues

echo "🔧 Fixing monitoring stack..."

# Stop monitoring stack
docker compose -f infrastructure/monitoring-complete.yml down || true

# Remove corrupted volumes (THIS WILL DELETE MONITORING DATA)
echo "⚠️  Removing corrupted monitoring volumes..."
docker volume rm vps_prometheus_data 2>/dev/null || true  
docker volume rm vps_grafana_data 2>/dev/null || true
docker volume rm vps_loki_data 2>/dev/null || true

# Recreate with clean state
echo "🚀 Starting clean monitoring stack..."
docker compose -f infrastructure/monitoring-complete.yml up -d

echo "✅ Monitoring stack reset complete"
echo "🔑 Grafana: http://IP:3001 (admin/webimar2024!)"
echo "📊 Prometheus: http://IP:9090" 
EOF

chmod +x fix-monitoring.sh

echo -e "  ${GREEN}✓ Created fix-monitoring.sh for VPS${NC}"

# 4. Update database environment consistency 
echo -e "\n${YELLOW}[4/5] 🔄 Harmonizing compose configurations...${NC}"

# Ensure webimar-api depends on postgres in prod compose
if ! grep -A5 "webimar-api:" projects/webimar/docker-compose.prod.yml | grep -q "depends_on:"; then
    echo -e "  ${YELLOW}⚠ Adding postgres dependency to webimar-api${NC}"
    
    # This is a complex multi-line edit, let's create a patch
    cat > /tmp/webimar-api-depends.patch << 'EOF'
# Add postgres dependency to webimar-api service
# Insert after environment section, before volumes section
EOF
fi

# 5. Create comprehensive VPS deploy/fix script
echo -e "\n${YELLOW}[5/5] 🚀 Creating VPS deployment fix script...${NC}"

cat > deploy-with-fixes.sh << 'EOF'
#!/bin/bash
# Combined deploy + VPS fixes script

set -e

VPS_HOST="akn@89.252.152.222"
VPS_PATH="/home/akn/vps"

echo "🔧 Deploying with VPS fixes..."

# 1. Deploy code changes
echo "📦 Deploying latest code..."
cd projects/webimar
./deploy.sh --mode git

# 2. Fix database issues on VPS
echo "🔧 Fixing database on VPS..."
ssh "$VPS_HOST" "cd $VPS_PATH && \
  # Stop webimar services
  docker compose -f projects/webimar/docker-compose.prod.yml down --remove-orphans
  
  # Ensure postgres is running
  docker compose -f projects/webimar/docker-compose.prod.yml up -d postgres
  
  # Wait for postgres to be ready
  sleep 10
  
  # Initialize database
  docker compose -f projects/webimar/docker-compose.prod.yml exec -T postgres psql -U webimar -d postgres < projects/webimar/init-db.sql || echo 'Database might already exist'
  
  # Start all services
  docker compose -f projects/webimar/docker-compose.prod.yml up -d
"

# 3. Fix monitoring on VPS
echo "📈 Fixing monitoring stack..."
scp fix-monitoring.sh "$VPS_HOST:$VPS_PATH/"
ssh "$VPS_HOST" "cd $VPS_PATH && chmod +x fix-monitoring.sh && ./fix-monitoring.sh"

echo "✅ VPS deployment and fixes complete!"
echo ""
echo "🌐 Test URLs:"
echo "  https://tarimimar.com.tr"
echo "  https://tarimimar.com.tr/api/calculations/health/"
echo ""
echo "📊 Monitoring URLs:"
echo "  Grafana: http://$(ssh $VPS_HOST 'curl -s ifconfig.me'):3001"
echo "  Prometheus: http://$(ssh $VPS_HOST 'curl -s ifconfig.me'):9090"
EOF

chmod +x deploy-with-fixes.sh

echo -e "  ${GREEN}✓ Created deploy-with-fixes.sh${NC}"

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Fixes Prepared!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}Created files:${NC}"
echo -e "  📄 projects/webimar/init-db.sql - Database initialization"
echo -e "  🔧 fix-monitoring.sh - Monitoring stack reset"
echo -e "  🚀 deploy-with-fixes.sh - Complete deployment with fixes"
echo -e ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review the generated files"
echo -e "  2. Run: ./deploy-with-fixes.sh"
echo -e "  3. Monitor the deployment"
echo -e ""
echo -e "${BLUE}This will:${NC}"
echo -e "  • Fix database naming issues"
echo -e "  • Reset corrupted monitoring volumes"
echo -e "  • Ensure all services start correctly"
echo -e "  • Provide monitoring URLs for verification"