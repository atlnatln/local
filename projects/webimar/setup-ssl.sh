#!/bin/bash
# ========================================
# SSL Certificate Setup
# Self-signed for development, Let's Encrypt for production
# ========================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="${PROJECT_DIR}/ssl"

mkdir -p "$SSL_DIR"

echo "🔐 Setting up SSL certificates..."

# Check if Let's Encrypt certs exist (production)
if [ -d "/etc/letsencrypt/live/tarimimar.com.tr" ]; then
    echo "✅ Found Let's Encrypt certificates"
    ln -sf /etc/letsencrypt/live/tarimimar.com.tr/fullchain.pem "$SSL_DIR/fullchain.pem"
    ln -sf /etc/letsencrypt/live/tarimimar.com.tr/privkey.pem "$SSL_DIR/privkey.pem"
    echo "  → Linked to $SSL_DIR/"
elif [ -f "$SSL_DIR/fullchain.pem" ] && [ -f "$SSL_DIR/privkey.pem" ]; then
    echo "✅ SSL certificates already exist"
else
    echo "📝 Generating self-signed certificate for development..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/privkey.pem" \
        -out "$SSL_DIR/fullchain.pem" \
        -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Webimar/CN=localhost" \
        2>/dev/null
    echo "✅ Self-signed certificate created"
fi

echo ""
echo "SSL files location: $SSL_DIR/"
ls -la "$SSL_DIR/"
