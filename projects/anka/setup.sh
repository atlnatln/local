#!/bin/bash
# ========================================
# Anka Platform Setup Script
# Proje kurulumunu hızlandırır
# ========================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   📦 Anka Platform Setup                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Script permissions
chmod +x dev-local.sh dev-docker.sh 2>/dev/null || true

# Backend venv setup
echo -e "${YELLOW}🐍 Backend Virtual Environment Setup...${NC}"
cd services/backend

if [ ! -d "venv" ]; then
    echo -e "  Creating venv..."
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "  ✓ venv activated"

# Upgrade pip
pip install -U pip setuptools wheel > /dev/null 2>&1
echo -e "  ✓ pip upgraded"

# Install requirements
if [ -f "requirements.txt" ]; then
    echo -e "  Installing requirements..."
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "  ✓ requirements installed"
fi

# Django setup
echo -e "\n${YELLOW}🗄️  Database Setup...${NC}"
python manage.py migrate --noinput 2>&1 | tail -3
echo -e "  ✓ migrations applied"

# Create superuser prompt
echo -e "\n${YELLOW}👤 Superuser Setup...${NC}"
read -p "  Create superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
else
    echo "  Skipped. Later: python manage.py createsuperuser"
fi

# Frontend setup
echo -e "\n${YELLOW}📦 Frontend Dependencies...${NC}"
cd "$PROJECT_DIR/services/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "  Installing npm packages..."
    npm install --prefer-offline > /dev/null 2>&1
    echo -e "  ✓ npm packages installed"
else
    echo -e "  ✓ node_modules already exists"
fi

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ Setup Complete!                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Next Steps:${NC}"
echo -e ""
echo -e "  ${GREEN}Local Development:${NC}"
echo -e "    ./dev-local.sh"
echo -e ""
echo -e "  ${GREEN}Docker Development:${NC}"
echo -e "    ./dev-docker.sh"
echo -e ""
echo -e "  ${GREEN}Manual Backend:${NC}"
echo -e "    cd services/backend"
echo -e "    source venv/bin/activate"
echo -e "    python manage.py runserver"
echo -e ""
echo -e "  ${GREEN}Manual Frontend:${NC}"
echo -e "    cd services/frontend"
echo -e "    npm run dev"
echo -e ""
