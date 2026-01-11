#!/bin/bash
# ============================================================================
# SSL Certificate Setup Script for Anka
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

DOMAIN="ankadata.com.tr"
EMAIL="admin@ankadata.com.tr"
SERVER_IP="89.252.152.222"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🔒 SSL Certificate Setup                        ║${NC}"
echo -e "${BLUE}║                    Domain: ${DOMAIN}                    ║${NC}"
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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run this script as root (use sudo)"
    exit 1
fi

# Check if domain points to this server
log_info "Checking domain DNS configuration..."
DOMAIN_IP=$(dig +short $DOMAIN @8.8.8.8 | tail -n1)
if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    log_warning "Domain $DOMAIN does not point to this server IP ($SERVER_IP)"
    log_warning "Current DNS points to: $DOMAIN_IP"
    echo ""
    echo "Please update your DNS records:"
    echo "A record: $DOMAIN → $SERVER_IP"
    echo "A record: www.$DOMAIN → $SERVER_IP"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install certbot if not installed
if ! command -v certbot &> /dev/null; then
    log_info "Installing certbot..."
    apt update
    apt install -y certbot
    log_success "Certbot installed"
else
    log_info "Certbot already installed"
fi

# Stop any services using port 80
log_info "Stopping services on port 80..."
systemctl stop nginx 2>/dev/null || true
docker stop vps_nginx_main 2>/dev/null || true
docker stop webimar-nginx-1 2>/dev/null || true
sleep 2

# Generate SSL certificate
log_info "Generating SSL certificate for $DOMAIN..."
certbot certonly \
    --standalone \
    --agree-tos \
    --no-eff-email \
    --email $EMAIL \
    --expand \
    -d $DOMAIN \
    -d www.$DOMAIN

if [ $? -eq 0 ]; then
    log_success "SSL certificate generated successfully"
else
    log_error "Failed to generate SSL certificate"
    exit 1
fi

# Create SSL directory structure
log_info "Setting up SSL directory structure..."
mkdir -p /home/akn/vps/infrastructure/ssl/ankadata.com.tr
mkdir -p /home/akn/vps/projects/anka/ssl/ankadata.com.tr

# Copy certificates
log_info "Copying certificates..."
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/akn/vps/infrastructure/ssl/ankadata.com.tr/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/akn/vps/infrastructure/ssl/ankadata.com.tr/
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/akn/vps/projects/anka/ssl/ankadata.com.tr/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/akn/vps/projects/anka/ssl/ankadata.com.tr/

# Fix permissions
chown -R akn:akn /home/akn/vps/infrastructure/ssl/
chown -R akn:akn /home/akn/vps/projects/anka/ssl/
chmod 644 /home/akn/vps/infrastructure/ssl/ankadata.com.tr/*
chmod 644 /home/akn/vps/projects/anka/ssl/ankadata.com.tr/*

log_success "Certificates copied and permissions set"

# Set up automatic renewal
log_info "Setting up automatic certificate renewal..."
cat > /etc/cron.d/certbot-renewal << EOF
# Automatic SSL certificate renewal for ankadata.com.tr
0 2 * * * root certbot renew --quiet --post-hook "systemctl reload nginx || docker restart vps_nginx_main"
EOF

log_success "Automatic renewal configured"

# Create certificate renewal script
cat > /usr/local/bin/update-anka-certs.sh << 'EOF'
#!/bin/bash
# Update Anka SSL certificates after renewal

DOMAIN="ankadata.com.tr"

# Copy renewed certificates
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/akn/vps/infrastructure/ssl/ankadata.com.tr/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/akn/vps/infrastructure/ssl/ankadata.com.tr/
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/akn/vps/projects/anka/ssl/ankadata.com.tr/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/akn/vps/projects/anka/ssl/ankadata.com.tr/

# Fix permissions
chown -R akn:akn /home/akn/vps/infrastructure/ssl/
chown -R akn:akn /home/akn/vps/projects/anka/ssl/

# Restart containers
docker restart vps_nginx_main 2>/dev/null || true
docker restart anka_nginx_prod 2>/dev/null || true

echo "SSL certificates updated for $DOMAIN"
EOF

chmod +x /usr/local/bin/update-anka-certs.sh

# Update cron to use the script
cat > /etc/cron.d/certbot-renewal << EOF
# Automatic SSL certificate renewal for ankadata.com.tr
0 2 * * * root certbot renew --quiet --post-hook "/usr/local/bin/update-anka-certs.sh"
EOF

log_success "Certificate update script created"

echo ""
log_success "🎉 SSL Certificate setup completed successfully!"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        📊 SSL Setup Summary                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📜 Certificates:${NC}"
echo -e "   Let's Encrypt: /etc/letsencrypt/live/$DOMAIN/"
echo -e "   Infrastructure: /home/akn/vps/infrastructure/ssl/ankadata.com.tr/"
echo -e "   Anka Project: /home/akn/vps/projects/anka/ssl/ankadata.com.tr/"
echo ""
echo -e "${GREEN}🔄 Auto-renewal:${NC}"
echo -e "   Cron job: /etc/cron.d/certbot-renewal"
echo -e "   Update script: /usr/local/bin/update-anka-certs.sh"
echo -e "   Runs: Daily at 2:00 AM"
echo ""
echo -e "${GREEN}✅ Next Steps:${NC}"
echo -e "   1. Verify DNS: dig $DOMAIN (should return $SERVER_IP)"
echo -e "   2. Test certificate: openssl s_client -connect $DOMAIN:443"
echo -e "   3. Deploy Anka project: cd /home/akn/vps/projects/anka && ./deploy.sh"
echo ""
log_success "SSL setup is ready! 🔒"