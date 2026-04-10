#!/bin/bash
# ============================================================================
# MathLock Play — Stats Monitor — Otomatik AI Soru Üretim Tetikleyicisi
#
# Bu script LOCAL makinede çalışır (VPS'te değil).
# VPS'teki stats.json'ı izler; çocuk 50 soru çözünce otomatik olarak
# ai-generate.sh tetiklenir → yeni sorular üretilir → telefona sessizce gönderilir.
#
# Kurulum:
#   bash mathlock-monitor.sh --install   # systemd user service olarak kur
#   bash mathlock-monitor.sh --status    # servis durumunu göster
#   bash mathlock-monitor.sh --logs      # logları göster
#   bash mathlock-monitor.sh --run       # doğrudan çalıştır (test için)
# ============================================================================

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VPS_HOST="akn@89.252.152.222"
VPS_DATA_PATH="/var/www/mathlock/data"
VPS_STATS="${VPS_HOST}:${VPS_DATA_PATH}/stats.json"
LOG_FILE="$PROJECT_DIR/data/monitor.log"
LOCK_FILE="/tmp/mathlock-play-ai-generate.lock"
SERVICE_NAME="mathlock-play-monitor"
POLL_INTERVAL=60  # saniye

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ─── Komutlar ───────────────────────────────────────────────────────────────
case "${1:-}" in
    --install)
        echo -e "${CYAN}[KURULUM]${NC} mathlock-play-monitor systemd user service kuruluyor..."
        mkdir -p "$HOME/.config/systemd/user"
        cat > "$HOME/.config/systemd/user/${SERVICE_NAME}.service" << EOF
[Unit]
Description=MathLock Play Stats Monitor — Otomatik AI Soru Üretimi
After=network-online.target

[Service]
Type=simple
ExecStart=${PROJECT_DIR}/mathlock-monitor.sh --run
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
        systemctl --user daemon-reload
        systemctl --user enable "$SERVICE_NAME"
        systemctl --user start "$SERVICE_NAME"
        echo -e "${GREEN}[OK]${NC} Servis başlatıldı."
        systemctl --user status "$SERVICE_NAME" --no-pager
        exit 0
        ;;
    --uninstall)
        systemctl --user stop "$SERVICE_NAME" 2>/dev/null || true
        systemctl --user disable "$SERVICE_NAME" 2>/dev/null || true
        rm -f "$HOME/.config/systemd/user/${SERVICE_NAME}.service"
        systemctl --user daemon-reload
        echo -e "${GREEN}[OK]${NC} Servis kaldırıldı."
        exit 0
        ;;
    --status)
        systemctl --user status "$SERVICE_NAME" --no-pager
        echo ""
        echo "Son log satırları:"
        tail -20 "$LOG_FILE" 2>/dev/null || echo "(log yok)"
        exit 0
        ;;
    --logs)
        tail -f "$LOG_FILE" 2>/dev/null || journalctl --user -u "$SERVICE_NAME" -f
        exit 0
        ;;
    --run|"")
        : # devam et
        ;;
    *)
        echo "Kullanım: $0 [--install|--uninstall|--status|--logs|--run]"
        exit 1
        ;;
esac

# ─── Ana İzleme Döngüsü ─────────────────────────────────────────────────────
mkdir -p "$(dirname "$LOG_FILE")"
log "=== MathLock Play Monitor başlatıldı ==="
log "Proje: $PROJECT_DIR"
log "VPS: $VPS_HOST"
log "VPS data: $VPS_DATA_PATH"
log "Kontrol aralığı: ${POLL_INTERVAL}s"

while true; do
    # ai-generate zaten çalışıyorsa atla
    if [ -f "$LOCK_FILE" ]; then
        sleep "$POLL_INTERVAL"
        continue
    fi

    # VPS'te stats.json var mı ve geçerli mi?
    STATS_OK=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$VPS_HOST" "
python3 -c \"
import json, os, sys
f = '${VPS_DATA_PATH}/stats.json'
if not os.path.exists(f):
    print('no')
    sys.exit()
try:
    d = json.load(open(f))
    total = d.get('totalShown', d.get('total_shown_alltime', 0))
    if total >= 45 and d.get('questionVersion', d.get('version', 0)) is not None:
        print('yes')
    else:
        print('no')
except:
    print('no')
\" 2>/dev/null" 2>/dev/null || echo "no")

    if [ "$STATS_OK" = "yes" ]; then
        log "✅ VPS'te tamamlanmış stats tespit edildi → ai-generate.sh başlatılıyor..."
        touch "$LOCK_FILE"

        # ai-generate.sh arka planda çalıştır
        (
            cd "$PROJECT_DIR"
            if ./ai-generate.sh >> "$LOG_FILE" 2>&1; then
                log "✅ Yeni soru seti başarıyla üretildi ve VPS'e gönderildi"
            else
                log "❌ ai-generate.sh başarısız oldu"
            fi
            rm -f "$LOCK_FILE"
        ) &

        # Bir sonraki kontrol için bekle (generate bitene kadar döngü tekrar tetiklemesin)
        sleep 300
    else
        sleep "$POLL_INTERVAL"
    fi
done
