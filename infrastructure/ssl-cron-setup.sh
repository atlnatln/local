#!/bin/bash
# ============================================================================
# SSL Otomatik Yenileme Cron Kurulum Scripti
# VPS'de root olarak bir kez çalıştırın:
#   sudo bash /home/akn/vps/infrastructure/ssl-cron-setup.sh
# ============================================================================

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Root olarak çalıştırın: sudo bash $0"
    exit 1
fi

RENEW_SCRIPT="/home/akn/vps/infrastructure/renew-ssl.sh"
CRON_FILE="/etc/cron.d/vps-ssl-renewal"
LOG_FILE="/var/log/ssl-renew.log"

# Script'e çalıştırma izni ver
chmod +x "$RENEW_SCRIPT"
echo "[OK] $RENEW_SCRIPT çalıştırma izni verildi"

# Log dosyası oluştur
touch "$LOG_FILE"
chmod 640 "$LOG_FILE"
echo "[OK] Log dosyası: $LOG_FILE"

# Cron job yaz (her gece 02:30 + her hafta Pazartesi 03:00 kontrolü)
cat > "$CRON_FILE" << EOF
# VPS SSL Sertifika Otomatik Yenileme
# Hedef domainler: ankadata.com.tr, tarimimar.com.tr, mathlock.com.tr
# Her gece 02:30'da çalışır, son 30 günde dolacak sertifikaları yeniler
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

30 2 * * * root bash $RENEW_SCRIPT >> $LOG_FILE 2>&1
EOF

echo "[OK] Cron job oluşturuldu: $CRON_FILE"
cat "$CRON_FILE"

echo ""
echo "=== Kurulum tamamlandı ==="
echo "Manuel çalıştırma: sudo bash $RENEW_SCRIPT"
echo "Zorla yenileme:    sudo bash $RENEW_SCRIPT --force"
echo "Log takibi:        tail -f $LOG_FILE"
