#!/bin/bash
# ============================================================================
# SSL Sertifika Yenileme Scripti
# Tüm VPS domainleri: ankadata.com.tr, tarimimar.com.tr, mathlock.com.tr
#
# Kullanım:
#   sudo bash /home/akn/vps/infrastructure/renew-ssl.sh          # normal yenileme
#   sudo bash /home/akn/vps/infrastructure/renew-ssl.sh --force  # zorla yenile
#
# Cron (her gece 02:30):
#   30 2 * * * root bash /home/akn/vps/infrastructure/renew-ssl.sh >> /var/log/ssl-renew.log 2>&1
# ============================================================================

set -euo pipefail

INFRA_DIR="/home/akn/vps/infrastructure"
SSL_DIR="$INFRA_DIR/ssl"
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')] [SSL-RENEW]"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log()    { echo -e "$LOG_PREFIX $1"; }
ok()     { echo -e "${GREEN}$LOG_PREFIX [OK]${NC} $1"; }
warn()   { echo -e "${YELLOW}$LOG_PREFIX [WARN]${NC} $1"; }
err()    { echo -e "${RED}$LOG_PREFIX [ERROR]${NC} $1"; }

FORCE_RENEW="${1:-}"

# ─── Root kontrolü ──────────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    err "Bu script root olarak çalıştırılmalı: sudo bash $0"
    exit 1
fi

# ─── Certbot kurulu mu? ──────────────────────────────────────────────────────
if ! command -v certbot &>/dev/null; then
    log "Certbot bulunamadı, kuruluyor..."
    apt-get update -qq && apt-get install -y -qq certbot
    ok "Certbot kuruldu"
fi

# ─── nginx container çalışıyor mu? ──────────────────────────────────────────
if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "vps_nginx_main"; then
    warn "vps_nginx_main container çalışmıyor — standalone modda devam edilecek"
    CERTBOT_MODE="standalone"
else
    CERTBOT_MODE="webroot"
fi

log "Certbot modu: $CERTBOT_MODE"

# ─── Sertifika yenileme ──────────────────────────────────────────────────────
RENEW_OPTS="--quiet --non-interactive"
if [ "$CERTBOT_MODE" = "webroot" ]; then
    # Renewal config dosyaları doğru webroot_path içeriyor:
    #   /var/lib/docker/volumes/vps_certbot_webroot/_data
    # Bu path nginx container'ına /var/www/certbot olarak mount edilmiş.
    # --webroot-path GEÇİLMİYOR: certbot kendi /etc/letsencrypt/renewal/*.conf'unu kullanır.
    # (Override geçilirse /var/www/certbot → host'ta yok → yenileme sessizce başarısız olur)
    : # webroot için ek flag gerekmez
else
    # Standalone: port 80'i geçici olarak serbest bırak
    docker stop vps_nginx_main 2>/dev/null || true
    sleep 2
    RENEW_OPTS="$RENEW_OPTS --standalone"
fi

if [ "$FORCE_RENEW" = "--force" ]; then
    RENEW_OPTS="$RENEW_OPTS --force-renewal"
    log "Zorla yenileme modu aktif"
fi

log "certbot renew çalıştırılıyor..."
certbot renew $RENEW_OPTS && ok "certbot renew tamamlandı" || warn "certbot renew bir şeyler döndürdü (sertifikalar güncel olabilir)"

# Standalone modda nginx'i yeniden başlat
if [ "$CERTBOT_MODE" = "standalone" ]; then
    log "nginx yeniden başlatılıyor..."
    cd "$INFRA_DIR" && docker compose up -d nginx_proxy 2>/dev/null || true
    sleep 3
fi

# ─── Sertifikaları kopyalama fonksiyonu ─────────────────────────────────────
copy_certs() {
    local DOMAIN="$1"
    local TARGET_DIR="$2"
    local LETSENCRYPT_DIR="/etc/letsencrypt/live/$DOMAIN"

    if [ ! -d "$LETSENCRYPT_DIR" ]; then
        warn "$DOMAIN için /etc/letsencrypt/live/$DOMAIN bulunamadı, atlanıyor"
        return 1
    fi

    mkdir -p "$TARGET_DIR"

    # Sertifika değişti mi kontrol et
    LOCAL_CERT="$TARGET_DIR/fullchain.pem"
    RENEWED_CERT="$LETSENCRYPT_DIR/fullchain.pem"

    if [ -f "$LOCAL_CERT" ] && diff -q "$LOCAL_CERT" "$RENEWED_CERT" &>/dev/null; then
        log "$DOMAIN: Sertifika değişmemiş, kopyalama atlandı"
        return 0
    fi

    cp "$RENEWED_CERT" "$TARGET_DIR/fullchain.pem"
    cp "$LETSENCRYPT_DIR/privkey.pem" "$TARGET_DIR/privkey.pem"
    chmod 644 "$TARGET_DIR/fullchain.pem" "$TARGET_DIR/privkey.pem"
    chown akn:akn "$TARGET_DIR/fullchain.pem" "$TARGET_DIR/privkey.pem"

    # Bitiş tarihini logla
    EXPIRY=$(openssl x509 -enddate -noout -in "$TARGET_DIR/fullchain.pem" | cut -d= -f2)
    ok "$DOMAIN: Sertifika güncellendi (bitiş: $EXPIRY)"
    return 0
}

# ─── Her domain için kopyala ─────────────────────────────────────────────────
CERTS_UPDATED=0

copy_certs "ankadata.com.tr"  "$SSL_DIR/ankadata.com.tr"  && CERTS_UPDATED=$((CERTS_UPDATED+1)) || true
copy_certs "tarimimar.com.tr" "$SSL_DIR/tarimimar.com.tr" && CERTS_UPDATED=$((CERTS_UPDATED+1)) || true
copy_certs "mathlock.com.tr"  "$SSL_DIR/mathlock.com.tr"  && CERTS_UPDATED=$((CERTS_UPDATED+1)) || true

# Anka kendi ssl dizinini de kullanıyorsa senkronize et
ANKA_SSL="/home/akn/vps/projects/anka/ssl/ankadata.com.tr"
if [ -d "$(dirname $ANKA_SSL)" ]; then
    copy_certs "ankadata.com.tr" "$ANKA_SSL" || true
fi

# ─── Nginx yeniden yükle ─────────────────────────────────────────────────────
if [ $CERTS_UPDATED -gt 0 ]; then
    log "Sertifikalar güncellendi ($CERTS_UPDATED domain), nginx yeniden yükleniyor..."
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "vps_nginx_main"; then
        docker exec vps_nginx_main nginx -s reload && ok "nginx başarıyla yeniden yüklendi" || {
            warn "nginx -s reload başarısız, restart deneniyor..."
            docker restart vps_nginx_main && ok "nginx yeniden başlatıldı"
        }
    fi
else
    log "Sertifika değişikliği yok, nginx reload atlandı"
fi

# ─── Güncel sertifika durumunu raporla ──────────────────────────────────────
log "─── Sertifika Durumu ───"
for DOMAIN in ankadata.com.tr tarimimar.com.tr mathlock.com.tr; do
    CERT="$SSL_DIR/$DOMAIN/fullchain.pem"
    if [ -f "$CERT" ]; then
        EXPIRY=$(openssl x509 -enddate -noout -in "$CERT" | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s 2>/dev/null)
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
        if [ $DAYS_LEFT -lt 14 ]; then
            warn "$DOMAIN: $DAYS_LEFT gün kaldı ($EXPIRY)"
        else
            ok "$DOMAIN: $DAYS_LEFT gün kaldı ($EXPIRY)"
        fi
    else
        warn "$DOMAIN: Sertifika dosyası bulunamadı ($CERT)"
    fi
done

log "SSL yenileme işlemi tamamlandı"
