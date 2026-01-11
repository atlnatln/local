#!/bin/bash
# ============================================================================
# Development Services Stop Script
# Stops both native (dev-local.sh) and Docker (dev-docker.sh) services
# ============================================================================

set +e  # Don't exit on errors - we want to try stopping everything

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping All Development Services${NC}"
echo "====================================="

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Function to kill process by port
kill_by_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo -e "🔧 Stopping $service_name (PID: $pid, Port: $port)..."
        kill -TERM $pid 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo -e "⚠️  Force killing $service_name..."
            kill -KILL $pid 2>/dev/null
        fi
        echo -e "✅ $service_name stopped"
    else
        echo -e "ℹ️  $service_name not running on port $port"
    fi
}

# Stop Docker services first
echo -e "\n${YELLOW}🐳 Stopping Docker Services...${NC}"
if docker compose ps --services 2>/dev/null | grep -q webimar; then
    docker compose down
    echo -e "✅ Docker services stopped"
else
    echo -e "ℹ️  No Docker services running"
fi

# Stop native services
echo -e "\n${YELLOW}🔧 Stopping Native Services...${NC}"

# Stop Django (port 8000)
kill_by_port 8000 "Django API"

# Stop Next.js (port 3000)
kill_by_port 3000 "Next.js Frontend"

# Stop React (port 3001)
kill_by_port 3001 "React SPA"

# Stop any nginx processes (port 80)
kill_by_port 80 "Nginx"

# Clean up background processes
echo -e "\n${YELLOW}🧹 Cleaning up background processes...${NC}"
pkill -f "python.*manage.py.*runserver" 2>/dev/null && echo "✅ Django processes killed"
pkill -f "npm.*start" 2>/dev/null && echo "✅ Node.js processes killed"
pkill -f "next.*dev" 2>/dev/null && echo "✅ Next.js dev processes killed"

# Remove PID files if any
rm -f "$PROJECT_DIR"/.dev-*.pid 2>/dev/null

# Final port check
echo -e "\n${BLUE}📊 Port Status Check:${NC}"
for port in 3000 3001 8000 80; do
    if lsof -t -i:$port >/dev/null 2>&1; then
        echo -e "⚠️  Port $port still in use"
    else
        echo -e "✅ Port $port available"
    fi
done

echo -e "\n${GREEN}✅ All development services stopped!${NC}"
echo -e "💡 Safe to start new services or deploy to production"