#!/bin/bash
# ============================================================================
# Anka Production Deploy Script
# Domain: ankadata.com.tr
# Server: 89.252.152.222
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Project configuration
PROJECT_NAME="anka"
DOMAIN="ankadata.com.tr"
SERVER_IP="89.252.152.222"
VPS_HOST="akn@89.252.152.222"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# GitHub (monorepo: /home/akn/vps)
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"
GIT_REMOTE_NAME="origin"
GIT_REMOTE_URL="https://github.com/atlnatln/vps.git"
GIT_BRANCH="main"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🚀 Anka Production Deploy                       ║${NC}"
echo -e "${BLUE}║                    Domain: ${DOMAIN}                    ║${NC}"
echo -e "${BLUE}║                    Server: ${SERVER_IP}                   ║${NC}"
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

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    log_error "docker-compose.prod.yml not found. Please run this script from the anka project root."
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    log_error ".env.production file not found. Please create it first."
    exit 1
fi

# Parse command line arguments
SKIP_BUILD=false
SKIP_SSL=false
FORCE_RECREATE=false
SKIP_GITHUB=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-ssl)
            SKIP_SSL=true
            shift
            ;;
        --skip-github)
            SKIP_GITHUB=true
            shift
            ;;
        --force-recreate)
            FORCE_RECREATE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-build        Skip Docker image building"
            echo "  --skip-ssl          Skip SSL certificate generation"
            echo "  --skip-github       Skip GitHub push"
            echo "  --force-recreate    Force recreate all containers"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Pre-deployment checks
log_info "Running pre-deployment checks..."

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

log_success "Pre-deployment checks passed"

# Create necessary directories
log_info "Creating necessary directories..."
mkdir -p ssl/ankadata.com.tr
mkdir -p logs
mkdir -p backups
mkdir -p infra/postgres/init

# Set proper permissions
chmod 755 ssl
chmod 755 logs
chmod 755 backups

log_success "Directories created"

# SSL Certificate setup (if not skipping)
if [ "$SKIP_SSL" = false ]; then
    log_info "Setting up SSL certificates..."
    
    if [ ! -f "ssl/ankadata.com.tr/fullchain.pem" ] || [ ! -f "ssl/ankadata.com.tr/privkey.pem" ]; then
        log_warning "SSL certificates not found. Please generate them manually:"
        echo ""
        echo "1. Install certbot on your server:"
        echo "   sudo apt update && sudo apt install certbot"
        echo ""
        echo "2. Generate certificates:"
        echo "   sudo certbot certonly --standalone -d ankadata.com.tr -d www.ankadata.com.tr"
        echo ""
        echo "3. Copy certificates to ssl directory:"
        echo "   sudo cp /etc/letsencrypt/live/ankadata.com.tr/fullchain.pem ssl/ankadata.com.tr/"
        echo "   sudo cp /etc/letsencrypt/live/ankadata.com.tr/privkey.pem ssl/ankadata.com.tr/"
        echo "   sudo chown \$(whoami):\$(whoami) ssl/ankadata.com.tr/*"
        echo ""
        echo "Or run with --skip-ssl to deploy without SSL (HTTP only)"
        exit 1
    else
        log_success "SSL certificates found"
    fi
fi

# Backup existing data (if containers exist)
log_info "Creating backup of existing data..."
if docker ps -a --format '{{.Names}}' | grep -q "anka_.*_prod"; then
    BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker ps --format '{{.Names}}' | grep -q "anka_postgres_prod"; then
        log_info "Backing up PostgreSQL database..."
        docker exec anka_postgres_prod pg_dump -U anka_user anka_prod > "$BACKUP_DIR/database.sql" 2>/dev/null || true
    fi
    
    # Backup media files
    if docker volume ls --format '{{.Name}}' | grep -q "anka_media_files"; then
        log_info "Backing up media files..."
        docker run --rm -v anka_media_files:/source -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/media.tar.gz -C /source . 2>/dev/null || true
    fi
    
    log_success "Backup created in $BACKUP_DIR"
else
    log_info "No existing containers found, skipping backup"
fi

# Stop existing containers
log_info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true
log_success "Existing containers stopped"

# Build images (if not skipping)
if [ "$SKIP_BUILD" = false ]; then
    log_info "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    log_success "Docker images built"
else
    log_info "Skipping Docker image build"
fi

# Deploy containers
log_info "Starting production containers..."

if [ "$FORCE_RECREATE" = true ]; then
    docker-compose -f docker-compose.prod.yml up -d --force-recreate --remove-orphans
else
    docker-compose -f docker-compose.prod.yml up -d --remove-orphans
fi

log_success "Production containers started"

# Update infrastructure nginx configuration
log_info "Updating infrastructure nginx configuration..."
if [ -f "../../infrastructure/nginx/conf.d/anka.conf" ]; then
    ssh "$VPS_HOST" "mkdir -p /home/akn/vps/infrastructure/nginx/conf.d"
    scp "../../infrastructure/nginx/conf.d/anka.conf" "$VPS_HOST:/home/akn/vps/infrastructure/nginx/conf.d/anka.conf"
    ssh "$VPS_HOST" "docker exec vps_nginx_main nginx -t && docker exec vps_nginx_main nginx -s reload" 2>/dev/null || log_warning "Infrastructure nginx reload failed (might not be running)"
    log_success "Infrastructure nginx updated"
else
    log_warning "Infrastructure nginx config not found at ../../infrastructure/nginx/conf.d/anka.conf"
fi

# Wait for services to be healthy
log_info "Waiting for services to be ready..."
sleep 10

# Check service health
services=("anka_postgres_prod" "anka_redis_prod" "anka_backend_prod" "anka_frontend_prod" "anka_nginx_prod")
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    all_healthy=true
    for service in "${services[@]}"; do
        if ! docker ps --format '{{.Names}} {{.Status}}' | grep "$service" | grep -q "healthy\|Up"; then
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
    log_warning "Some services may not be fully ready yet. Check with: docker-compose -f docker-compose.prod.yml ps"
else
    log_success "All services are healthy"
fi

# Run database migrations
log_info "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput
log_success "Database migrations completed"

# Collect static files
log_info "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput --clear
log_success "Static files collected"

# Create superuser (if it doesn't exist)
log_info "Setting up admin user..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@ankadata.com.tr', 'change-this-admin-password')
    print('Admin user created')
else:
    print('Admin user already exists')
" 2>/dev/null || log_warning "Could not create admin user automatically"

# Show final status
echo ""
log_success "🎉 Deployment completed successfully!"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        📊 Deployment Summary                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 URLs:${NC}"
if [ "$SKIP_SSL" = false ]; then
    echo -e "   Main Site:     https://ankadata.com.tr"
    echo -e "   Admin Panel:   https://ankadata.com.tr/admin/"
    echo -e "   API:           https://ankadata.com.tr/api/"
else
    echo -e "   Main Site:     http://89.252.152.222:8081"
    echo -e "   Admin Panel:   http://89.252.152.222:8081/admin/"
    echo -e "   API:           http://89.252.152.222:8081/api/"
fi
echo ""
echo -e "${GREEN}🔧 Management:${NC}"
echo -e "   View logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo -e "   Status:        docker-compose -f docker-compose.prod.yml ps"
echo -e "   Stop:          docker-compose -f docker-compose.prod.yml down"
echo ""
echo -e "${GREEN}👤 Default Admin:${NC}"
echo -e "   Username:      admin"
echo -e "   Password:      change-this-admin-password"
echo -e "   Email:         admin@ankadata.com.tr"
echo ""
echo -e "${YELLOW}⚠️  Security Notes:${NC}"
echo -e "   1. Change the default admin password immediately"
echo -e "   2. Update SECRET_KEY in .env.production"
echo -e "   3. Configure your firewall to allow only ports 80 and 443"
echo -e "   4. Set up regular database backups"
echo -e "   5. Monitor logs regularly"
echo ""
echo -e "${GREEN}✅ Next Steps:${NC}"
echo -e "   1. Configure DNS A record: ankadata.com.tr → 89.252.152.222"
echo -e "   2. Test the application thoroughly"
echo -e "   3. Set up monitoring and alerting"
echo -e "   4. Configure regular backups"
echo ""
log_success "Deployment is ready! 🚀"

# Push to GitHub (optional)
if [ "$SKIP_GITHUB" = false ]; then
    log_info "Pushing to GitHub (vps repo)..."

    cd "$REPO_ROOT"

    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_info "Initializing git repo at: ${REPO_ROOT}"
        git init
        git checkout -b "$GIT_BRANCH" >/dev/null 2>&1 || git branch -M "$GIT_BRANCH"
    fi

    if ! git config user.email >/dev/null 2>&1; then
        git config user.email "deploy@localhost"
    fi
    if ! git config user.name >/dev/null 2>&1; then
        git config user.name "Deploy Script"
    fi

    if git remote get-url "$GIT_REMOTE_NAME" >/dev/null 2>&1; then
        git remote set-url "$GIT_REMOTE_NAME" "$GIT_REMOTE_URL"
    else
        git remote add "$GIT_REMOTE_NAME" "$GIT_REMOTE_URL"
    fi

    git add -A
    if git diff --staged --quiet; then
        log_info "No changes to commit"
    else
        ts="$(date +%Y%m%d_%H%M%S)"
        git commit -m "deploy: vps update ${ts}"
        git push "$GIT_REMOTE_NAME" "$GIT_BRANCH"
        log_success "GitHub push complete"
    fi
else
    log_info "Skipping GitHub push (--skip-github)"
fi