#!/bin/bash
# ============================================================================
# VPS Infrastructure Setup Script
# Sets up main reverse proxy and shared services
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🏗️  VPS Infrastructure Setup                    ║${NC}"
echo -e "${BLUE}║                    Multi-Project Reverse Proxy                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
ENABLE_MONITORING=false
SETUP_SSL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --monitoring)
            ENABLE_MONITORING=true
            shift
            ;;
        --ssl)
            SETUP_SSL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --monitoring        Enable Prometheus/Grafana monitoring"
            echo "  --ssl              Setup SSL certificates"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Pre-setup checks
log_info "Running pre-setup checks..."

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running. Please start Docker service."
    exit 1
fi

log_success "Pre-setup checks passed"

# Create necessary directories
log_info "Creating directory structure..."
mkdir -p ssl/ankadata.com.tr
mkdir -p ssl/tarimimar.com.tr
mkdir -p monitoring/{prometheus,grafana/{dashboards,datasources}}
mkdir -p logs

# Create default SSL certificates if they don't exist
if [ ! -f "ssl/default/cert.pem" ] || [ ! -f "ssl/default/key.pem" ]; then
    log_info "Creating default SSL certificates..."
    mkdir -p ssl/default
    openssl req -x509 -newkey rsa:2048 -keyout ssl/default/key.pem -out ssl/default/cert.pem -days 365 -nodes -subj "/C=TR/ST=Istanbul/L=Istanbul/O=VPS/OU=IT/CN=default" 2>/dev/null
fi

log_success "Directory structure created"

# Setup SSL certificates if requested
if [ "$SETUP_SSL" = true ]; then
    log_info "Setting up SSL certificates..."
    if [ -f "setup-ssl.sh" ] && [ -x "setup-ssl.sh" ]; then
        sudo ./setup-ssl.sh
    else
        log_warning "SSL setup script not found or not executable. Please run manually:"
        echo "  sudo ./setup-ssl.sh"
    fi
fi

# Create monitoring configuration files
if [ "$ENABLE_MONITORING" = true ]; then
    log_info "Setting up monitoring configuration..."
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx_proxy:8080']
    metrics_path: /nginx-status
    scrape_interval: 5s
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']
EOF

    # Grafana datasource configuration
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
EOF

    log_success "Monitoring configuration created"
fi

# Stop existing infrastructure services
log_info "Stopping existing infrastructure services..."
docker-compose down --remove-orphans || true

# Start infrastructure services
log_info "Starting infrastructure services..."

if [ "$ENABLE_MONITORING" = true ]; then
    docker-compose --profile monitoring up -d
else
    docker-compose up -d
fi

log_success "Infrastructure services started"

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 10

# Check service health
services=("vps_nginx_main")
if [ "$ENABLE_MONITORING" = true ]; then
    services+=("vps_prometheus" "vps_grafana")
fi

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    all_healthy=true
    for service in "${services[@]}"; do
        if ! docker ps --format '{{.Names}} {{.Status}}' | grep "$service" | grep -q "Up"; then
            all_healthy=false
            break
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        break
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

echo ""

if [ $attempt -eq $max_attempts ]; then
    log_warning "Some services may not be fully ready yet. Check with: docker-compose ps"
else
    log_success "All infrastructure services are running"
fi

echo ""
log_success "🎉 VPS Infrastructure setup completed!"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    📊 Infrastructure Summary                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 Services:${NC}"
echo -e "   Main Nginx Proxy:  http://89.252.152.222 (ports 80, 443)"
echo -e "   Health Check:      http://89.252.152.222:8080/nginx-health"
echo -e "   Nginx Status:      http://89.252.152.222:8080/nginx-status"

if [ "$ENABLE_MONITORING" = true ]; then
    echo -e "   Prometheus:        http://89.252.152.222:9090"
    echo -e "   Grafana:           http://89.252.152.222:3000"
fi

echo ""
echo -e "${GREEN}🔧 Management:${NC}"
echo -e "   View logs:         docker-compose logs -f"
echo -e "   Status:            docker-compose ps"
echo -e "   Stop all:          docker-compose down"
echo -e "   Restart nginx:     docker restart vps_nginx_main"

if [ "$ENABLE_MONITORING" = true ]; then
    echo ""
    echo -e "${GREEN}📊 Monitoring:${NC}"
    echo -e "   Grafana Login:     admin / change-this-grafana-password"
fi

echo ""
echo -e "${GREEN}📁 Directory Structure:${NC}"
echo -e "   SSL Certificates:  ./ssl/"
echo -e "   Nginx Config:      ./nginx/"
echo -e "   Logs:              ./logs/"
echo -e "   Monitoring:        ./monitoring/"

echo ""
echo -e "${GREEN}✅ Next Steps:${NC}"
echo -e "   1. Configure DNS records:"
echo -e "      ankadata.com.tr → 89.252.152.222"
echo -e "      www.ankadata.com.tr → 89.252.152.222"
echo -e "   2. Setup SSL certificates: sudo ./setup-ssl.sh"
echo -e "   3. Deploy projects:"
echo -e "      cd ../projects/anka && ./deploy.sh"
echo -e "      cd ../projects/webimar && ./deploy.sh"
echo ""
log_success "Infrastructure is ready! 🚀"