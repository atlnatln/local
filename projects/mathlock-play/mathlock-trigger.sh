#!/bin/bash
# ============================================================================
# MathLock Play — Otomatik Tetikleyici — VPS Cron Tarafından Çalıştırılır
#
# Cron: */5 * * * * /home/akn/vps/projects/mathlock-play/mathlock-trigger.sh
#
# İşleyiş:
#   1. stats.json var mı kontrol et (telefon 50 soru çözünce PUT eder)
#   2. stats.json geçerli ve en az 1 kayıt içeriyor mu?
#   3. Kilitli değilse ai-generate.sh --vps-mode çalıştır
#   4. Log yaz
# ============================================================================

MATHLOCK_DIR="/home/akn/vps/projects/mathlock-play"
VPS_DATA_PATH="/var/www/mathlock/data"
STATS_FILE="$VPS_DATA_PATH/stats.json"
LOCK_FILE="/tmp/mathlock-play-ai-generate.lock"
LOG_FILE="$MATHLOCK_DIR/data/trigger.log"

# Log fonksiyonu
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# Stats.json yoksa çık (henüz 50 soru çözülmemiş)
if [ ! -f "$STATS_FILE" ]; then
    exit 0
fi

# stats.json boş veya geçersizse çık
RECORD_COUNT=$(python3 -c "
import json, sys
try:
    d = json.load(open('$STATS_FILE'))
    # Tüm olası format anahtarlarını destekle
    n = len(d.get('results', d.get('details', d.get('saved_results', []))))
    print(n)
except:
    print(0)
" 2>/dev/null || echo 0)

if [ "$RECORD_COUNT" -lt 1 ]; then
    log "stats.json var ama kayıt yok ($RECORD_COUNT), atlanıyor"
    exit 0
fi

# Zaten çalışıyor mu? (lock dosyası varsa ve süreci hâlâ yaşıyorsa)
if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        log "Zaten çalışıyor (PID=$LOCK_PID), atlanıyor"
        exit 0
    else
        log "Eski lock siliniyor (PID=$LOCK_PID artık yok)"
        rm -f "$LOCK_FILE"
    fi
fi

# Lock al
echo $$ > "$LOCK_FILE"
trap "rm -f '$LOCK_FILE'" EXIT

log "Tetiklendi: $RECORD_COUNT kayıt bulundu, ai-generate.sh başlatılıyor..."

# ai-generate.sh çalıştır (--vps-mode: scp yok, lokal dosyalar)
cd "$MATHLOCK_DIR"
if ./ai-generate.sh --vps-mode >> "$LOG_FILE" 2>&1; then
    log "✅ Tamamlandı başarıyla"
else
    EXIT_CODE=$?
    log "❌ Başarısız (exit=$EXIT_CODE)"
fi

# Log dosyasını küçük tut (son 500 satır)
TMPLOG=$(mktemp)
tail -500 "$LOG_FILE" > "$TMPLOG" && mv "$TMPLOG" "$LOG_FILE"
