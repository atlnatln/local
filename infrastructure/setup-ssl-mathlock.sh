#!/bin/bash
# ============================================================================
# MathLock SSL Setup — mathlock.com.tr
# Let's Encrypt sertifikası alır ve nginx reverse proxy'ye entegre eder.
#
# Kullanım (VPS'de root olarak):
#   bash /home/akn/vps/infrastructure/setup-ssl-mathlock.sh
#
# Ön koşullar:
#   - DNS: mathlock.com.tr ve www.mathlock.com.tr → 89.252.152.222
#   - Docker: vps_nginx_main ve vps_certbot container'ları çalışıyor
#   - infrastructure/nginx/conf.d/mathlock-play.conf mevcut
# ============================================================================

set -euo pipefail

DOMAIN="mathlock.com.tr"
EMAIL="admin@ankadata.com.tr"
SERVER_IP="89.252.152.222"

INFRA_DIR="/home/akn/vps/infrastructure"
SSL_DIR="$INFRA_DIR/ssl/$DOMAIN"
NGINX_CONF="$INFRA_DIR/nginx/conf.d/mathlock-play.conf"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }

# ─── 1. DNS kontrolü ────────────────────────────────────────────────────────
log_info "DNS kontrolü..."
DOMAIN_IP=$(dig +short "$DOMAIN" @8.8.8.8 | tail -n1)
WWW_IP=$(dig +short "www.$DOMAIN" @8.8.8.8 | tail -n1)

if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    log_error "$DOMAIN → $DOMAIN_IP (beklenen: $SERVER_IP)"
    echo "DNS henüz propagate olmamış. Lütfen bekleyin veya A kaydını kontrol edin."
    exit 1
fi
log_success "$DOMAIN → $DOMAIN_IP"

if [ "$WWW_IP" != "$SERVER_IP" ]; then
    log_warning "www.$DOMAIN → $WWW_IP (beklenen: $SERVER_IP)"
    log_warning "www subdomain propagasyonu bekleniyor, sadece $DOMAIN ile devam edilecek."
    CERT_DOMAINS="-d $DOMAIN"
else
    log_success "www.$DOMAIN → $WWW_IP"
    CERT_DOMAINS="-d $DOMAIN -d www.$DOMAIN"
fi

# ─── 2. Container kontrolü ──────────────────────────────────────────────────
log_info "Docker container kontrolü..."
if ! docker ps --format '{{.Names}}' | grep -q "vps_nginx_main"; then
    log_error "vps_nginx_main container'ı çalışmıyor!"
    echo "Önce: cd $INFRA_DIR && docker compose up -d"
    exit 1
fi
log_success "vps_nginx_main çalışıyor"

# ─── 3. HTTP-only geçici config (ACME challenge için) ───────────────────────
log_info "Geçici HTTP-only nginx config yazılıyor..."
BACKUP_CONF="${NGINX_CONF}.bak"
cp "$NGINX_CONF" "$BACKUP_CONF"

cat > "$NGINX_CONF" << 'HTTPONLY'
# Geçici HTTP-only config — ACME challenge için
server {
    listen 80;
    server_name mathlock.com.tr www.mathlock.com.tr;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files $uri $uri/ =404;
    }

    location / {
        root /var/www/mathlock/website;
        index index.html;
        try_files $uri $uri.html $uri/ =404;
    }

    location = /mathlock/health {
        access_log off;
        add_header Content-Type text/plain;
        return 200 "mathlock ok (http)\n";
    }
}
HTTPONLY

log_info "Nginx reload (HTTP-only)..."
docker exec vps_nginx_main nginx -t 2>&1 || {
    log_error "Nginx config hatası! Backup geri yükleniyor..."
    cp "$BACKUP_CONF" "$NGINX_CONF"
    docker exec vps_nginx_main nginx -s reload
    exit 1
}
docker exec vps_nginx_main nginx -s reload
log_success "Nginx HTTP-only config aktif"

# ─── 4. HTTP erişim testi ───────────────────────────────────────────────────
log_info "HTTP erişim testi..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/mathlock/health" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    log_success "HTTP erişim OK ($HTTP_CODE)"
else
    log_warning "HTTP erişim kodu: $HTTP_CODE (devam ediliyor...)"
fi

# ─── 5. SSL sertifikası al ──────────────────────────────────────────────────
log_info "Let's Encrypt sertifikası alınıyor..."

# certbot webroot dizinini nginx container'a mount edilmiş dizinden kullan
# nginx, /.well-known/acme-challenge/ isteklerini /var/www/certbot'a yönlendiriyor
# Bu dizin host'ta docker volume olarak yönetiliyor

# Webroot path'i bul (named volume mount point)
CERTBOT_WEBROOT=$(docker inspect vps_nginx_main --format '{{ range .Mounts }}{{ if eq .Destination "/var/www/certbot" }}{{ .Source }}{{ end }}{{ end }}' 2>/dev/null)

if [ -z "$CERTBOT_WEBROOT" ]; then
    # Varsayılan: Docker volume path (vps_ prefix'li)
    CERTBOT_WEBROOT="/var/lib/docker/volumes/vps_certbot_webroot/_data"
fi

if [ -z "$CERTBOT_WEBROOT" ]; then
    log_warning "Webroot volume bulunamadı, standalone mode kullanılıyor..."
    log_info "nginx durduruluyor (standalone mode için port 80 gerekli)..."
    docker stop vps_nginx_main
    sleep 2

    certbot certonly \
        --standalone \
        --agree-tos \
        --no-eff-email \
        --email "$EMAIL" \
        --expand \
        $CERT_DOMAINS \
        --non-interactive 2>&1

    CERT_RESULT=$?
    docker start vps_nginx_main
    sleep 2
else
    log_info "Webroot mode kullanılıyor: $CERTBOT_WEBROOT"
    certbot certonly \
        --webroot \
        --webroot-path="$CERTBOT_WEBROOT" \
        $CERT_DOMAINS \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive 2>&1
    CERT_RESULT=$?
fi

if [ $CERT_RESULT -ne 0 ]; then
    log_error "Certbot başarısız! Backup config geri yükleniyor..."
    cp "$BACKUP_CONF" "$NGINX_CONF"
    docker exec vps_nginx_main nginx -s reload
    exit 1
fi
log_success "SSL sertifikası alındı"

# ─── 6. Sertifikaları kopyala ───────────────────────────────────────────────
log_info "Sertifikalar kopyalanıyor..."
mkdir -p "$SSL_DIR"

# Host'taki certbot dizininden kopyala
cp -L "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp -L "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/privkey.pem"

chown -R akn:akn "$SSL_DIR"
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"
log_success "Sertifikalar: $SSL_DIR/"

# ─── 7. HTTPS nginx config'e geç ───────────────────────────────────────────
log_info "HTTPS nginx config aktifleştiriliyor..."
cp "$BACKUP_CONF" "$NGINX_CONF"
rm -f "$BACKUP_CONF"

docker exec vps_nginx_main nginx -t 2>&1 || {
    log_error "HTTPS nginx config hatası!"
    exit 1
}
docker exec vps_nginx_main nginx -s reload
log_success "HTTPS config aktif"

# ─── 8. Doğrulama ───────────────────────────────────────────────────────────
log_info "HTTPS doğrulanıyor..."
sleep 3

HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/mathlock/health" 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" = "200" ]; then
    log_success "HTTPS health check: $HTTPS_CODE"
else
    log_warning "HTTPS health check: $HTTPS_CODE (sertifika propagasyonu bekleniyor olabilir)"
fi

SITE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/" 2>/dev/null || echo "000")
log_info "Website: https://$DOMAIN/ → $SITE_CODE"

PRIVACY_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/privacy" 2>/dev/null || echo "000")
log_info "Privacy: https://$DOMAIN/privacy → $PRIVACY_CODE"

SUPPORT_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/support" 2>/dev/null || echo "000")
log_info "Support: https://$DOMAIN/support → $SUPPORT_CODE"

# ─── 9. Cert renewal hook ───────────────────────────────────────────────────
log_info "Sertifika yenileme hook'u kuruluyor..."
cat > /usr/local/bin/update-mathlock-certs.sh << 'EOF'
#!/bin/bash
DOMAIN="mathlock.com.tr"
SSL_DIR="/home/akn/vps/infrastructure/ssl/$DOMAIN"
mkdir -p "$SSL_DIR"
cp -L "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp -L "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/privkey.pem"
chown -R akn:akn "$SSL_DIR"
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"
docker exec vps_nginx_main nginx -s reload
EOF
chmod +x /usr/local/bin/update-mathlock-certs.sh

# Mevcut cron'a ekle (duplicate kontrolü)
CRON_LINE='0 3 * * * /usr/local/bin/update-mathlock-certs.sh >> /var/log/mathlock-cert-renewal.log 2>&1'
(crontab -l 2>/dev/null | grep -v "update-mathlock-certs" ; echo "$CRON_LINE") | crontab -

log_success "Günlük sertifika yenileme hook'u kuruldu"

# ─── Sonuç ───────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  mathlock.com.tr SSL kurulumu tamamlandı!"
echo "============================================"
echo ""
echo "  Website:  https://mathlock.com.tr/"
echo "  Privacy:  https://mathlock.com.tr/privacy"
echo "  Support:  https://mathlock.com.tr/support"
echo "  Health:   https://mathlock.com.tr/mathlock/health"
echo "  Data:     https://mathlock.com.tr/mathlock/data/questions.json"
echo ""
echo "  SSL cert: $SSL_DIR/"
echo "  Nginx:    $NGINX_CONF"
echo ""
