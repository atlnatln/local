#!/bin/bash
# ============================================================================
# Sayı Yolculuğu — AI Seviye Üretim Pipeline
#
# Bu script level-stats.json analiz edilip 12 yeni seviye üretir:
#   1. level-stats.json analiz edilir (varsa)
#   2. kimi-cli (kimi-for-coding) AGENTS-LEVELS.md ile yeni 12 seviye üretir
#   3. validate-levels.py ile doğrulanır (BFS çözülebilirlik dahil)
#   4. VPS nginx'e sync edilir
#   5. Telefon yeni seviyeleri indirir
#
# Kullanım:
#   ./ai-generate-levels.sh              # Yerel → VPS'e push
#   ./ai-generate-levels.sh --vps-mode   # VPS'te çalışır
#   ./ai-generate-levels.sh --dry-run    # Sadece durumu göster
#   ./ai-generate-levels.sh --skip-sync  # VPS sync atla
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$PROJECT_DIR/data"
STATS_FILE="$DATA_DIR/level-stats.json"
LEVELS_FILE="$DATA_DIR/levels.json"
HISTORY_DIR="$DATA_DIR/history"
VALIDATOR="$PROJECT_DIR/validate-levels.py"
VPS_HOST="akn@89.252.152.222"
VPS_DATA_PATH="/var/www/mathlock/data"
HEALTH_URL="https://mathlock.com.tr/mathlock/data/levels.json"
MAX_RETRIES=2

cd "$PROJECT_DIR"
source agents/swap-helper.sh

# ─── Argümanlar ─────────────────────────────────────────────
DRY_RUN=false
SKIP_SYNC=false
VPS_MODE=false
EDUCATION_PERIOD="sinif_2"
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)    DRY_RUN=true;  shift ;;
        --skip-sync)  SKIP_SYNC=true; shift ;;
        --vps-mode)   VPS_MODE=true; shift ;;
        --period)     EDUCATION_PERIOD="$2"; shift 2 ;;
        --data-dir)   DATA_DIR="$2"; shift 2 ;;
        --help)
            echo "Kullanım: $0 [--dry-run] [--skip-sync] [--vps-mode] [--period <dönem>] [--data-dir <dizin>]"
            echo "  --period   Eğitim dönemi: okul_oncesi|sinif_1|sinif_2|sinif_3|sinif_4"
            echo "  --data-dir level-stats/levels yazılacak dizin (varsayılan: ./data)"
            exit 0
            ;;
        *) echo "Bilinmeyen: $1"; exit 1 ;;
    esac
done

# --data-dir sonrası dosya yollarını yeniden türet
STATS_FILE="$DATA_DIR/level-stats.json"
LEVELS_FILE="$DATA_DIR/levels.json"
HISTORY_DIR="$DATA_DIR/history"

# Eğitim dönemi → agent dosyası eşlemesi
case "$EDUCATION_PERIOD" in
    okul_oncesi) AGENT_FILE="agents/levels-okul-oncesi.agents.md" ;;
    sinif_1)     AGENT_FILE="agents/levels-sinif-1.agents.md" ;;
    sinif_2)     AGENT_FILE="agents/levels-sinif-2.agents.md" ;;
    sinif_3)     AGENT_FILE="agents/levels-sinif-3.agents.md" ;;
    sinif_4)     AGENT_FILE="agents/levels-sinif-4.agents.md" ;;
    *)
        echo -e "${RED}[HATA]${NC} Geçersiz dönem: $EDUCATION_PERIOD"
        echo "Geçerli dönemler: okul_oncesi, sinif_1, sinif_2, sinif_3, sinif_4"
        exit 1
        ;;
esac

if [ ! -f "$AGENT_FILE" ]; then
    echo -e "${RED}[HATA]${NC} Agent dosyası bulunamadı: $AGENT_FILE"
    exit 1
fi

# kimi-cli OAuth ile çalışır; env token gerekmez.
# ~/.kimi/credentials/ altındaki login bilgisi kullanılır.

echo -e "\n${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Sayı Yolculuğu — AI Seviye Üretim Pipeline  ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}\n"

# ─── 1. Stats analizi ───────────────────────────────────────
echo -e "${YELLOW}[1/5] 📊 Durum kontrol ediliyor...${NC}"

if [ "$VPS_MODE" = true ]; then
    echo -e "  📍 VPS modu — lokal dizin kullanılıyor"
    if [ -f "$VPS_DATA_PATH/level-stats.json" ]; then
        cp "$VPS_DATA_PATH/level-stats.json" "$STATS_FILE"
    fi
    if [ -f "$VPS_DATA_PATH/levels.json" ] && [ ! -f "$LEVELS_FILE" ]; then
        cp "$VPS_DATA_PATH/levels.json" "$LEVELS_FILE"
    fi
else
    echo -e "  📥 VPS'ten stats çekiliyor..."
    scp -q "$VPS_HOST:$VPS_DATA_PATH/level-stats.json" "$STATS_FILE" 2>/dev/null || true
fi

# Dönem → yaş grubu eşlemesi (log ve prompt için)
case "$EDUCATION_PERIOD" in
    okul_oncesi) AGE_GROUP="5-6" ;;
    sinif_1)     AGE_GROUP="6-7" ;;
    sinif_2)     AGE_GROUP="7-8" ;;
    sinif_3)     AGE_GROUP="8-9" ;;
    sinif_4)     AGE_GROUP="9-10" ;;
    *)           AGE_GROUP="7-8" ;;
esac

CURRENT_VERSION=0
if [ -f "$LEVELS_FILE" ]; then
    CURRENT_VERSION=$(python3 -c "import json; d=json.load(open('$LEVELS_FILE')); print(d.get('version',0))" 2>/dev/null || echo "0")
fi
NEW_VERSION=$((CURRENT_VERSION + 1))

HAS_STATS=false
if [ -f "$STATS_FILE" ] && [ -s "$STATS_FILE" ]; then
    HAS_STATS=true
    echo -e "  ${GREEN}✅ level-stats.json bulundu${NC}"
    STAT_SUMMARY=$(python3 -c "
import json
d = json.load(open('$STATS_FILE'))
comp = d.get('totalCompleted', 0)
total = d.get('totalLevels', 12)
stars = d.get('totalStars', 0)
print(f'{comp}/{total} tamamlandı, {stars}/{total*3} yıldız')
" 2>/dev/null || echo "parse hatası")
    echo -e "  📈 Performans: ${STAT_SUMMARY}"
else
    echo -e "  ${YELLOW}⚠️ level-stats.json yok — ilk set üretilecek${NC}"
fi

echo -e "  📦 Mevcut versiyon: v${CURRENT_VERSION} → v${NEW_VERSION}"
echo -e "  🎯 Yaş grubu: ${AGE_GROUP}"

if [ "$DRY_RUN" = true ]; then
    echo -e "\n${YELLOW}--dry-run: kimi-cli çalıştırılmadı.${NC}"
    exit 0
fi

# ─── 2. Arşivle ─────────────────────────────────────────────
mkdir -p "$HISTORY_DIR"
if [ -f "$LEVELS_FILE" ]; then
    ARCHIVE_NAME="levels_v${CURRENT_VERSION}_$(date +%Y%m%d_%H%M%S).json"
    cp "$LEVELS_FILE" "$HISTORY_DIR/$ARCHIVE_NAME"
    echo -e "\n${YELLOW}[2/5] 📂 Arşivlendi: $ARCHIVE_NAME${NC}"
fi

# ─── 3. kimi-cli ile üret ──────────────────────────────────
echo -e "\n${YELLOW}[3/5] 🤖 kimi-cli ile 12 yeni seviye üretiliyor...${NC}"

# AGENTS.md swap — dönemine uygun levels agent'ı
agents_swap_in "$AGENT_FILE"

PROMPT="AGENTS.md dosyasındaki tüm kuralları uygula.

ADIMLAR:
1. ${LEVELS_FILE} oku — mevcut version numarasını al
2. ${STATS_FILE} oku (varsa) — oyuncunun performansını analiz et
3. Yeni 12 seviye üret → ${LEVELS_FILE} dosyasına yaz (üzerine yaz)
4. Analiz raporunu stdout'a yazdır

PARAMETRELER:
- Yaş grubu: ${AGE_GROUP}
- Yeni version: ${NEW_VERSION}
- generatedAt: $(date -u +%Y-%m-%dT%H:%M:%SZ)

KRİTİK KURALLAR:
- Sadece ${LEVELS_FILE} değiştir, başka dosyaya dokunma
- Tam 12 seviye, her biri BFS ile çözülebilir olmalı
- version = ${NEW_VERSION}
- Geçerli JSON, UTF-8
- İlk 3 seviye kolay, son 3 zor"

# Retry döngüsü
ATTEMPT=0
SUCCESS=false

while [ $ATTEMPT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo -e "\n${CYAN}[Deneme ${ATTEMPT}/${MAX_RETRIES}]${NC}"

    # kimi-cli çalıştır (VPS'te ~/.local/bin/uv tool install konumu)
    export PATH="$HOME/.local/bin:$PATH"
    KIMI_BIN="$(command -v kimi 2>/dev/null)"
    if [ ! -x "$KIMI_BIN" ]; then
        echo -e "${RED}[HATA]${NC} kimi-cli bulunamadı!"
        exit 1
    fi
    "$KIMI_BIN" -p "$PROMPT" --print --final-message-only --no-thinking --model kimi-code/kimi-for-coding 2>&1

    # ─── 4. Doğrulama ───────────────────────────────────────
    echo -e "\n${YELLOW}[4/5] 🔍 Doğrulama çalıştırılıyor...${NC}"
    if python3 "$VALIDATOR" --file "$LEVELS_FILE"; then
        SUCCESS=true
        echo -e "${GREEN}[OK]${NC} Doğrulama başarılı!"
    else
        echo -e "${RED}[HATA]${NC} Doğrulama başarısız (deneme ${ATTEMPT}/${MAX_RETRIES})"
        if [ $ATTEMPT -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}[TEKRAR]${NC} kimi-cli tekrar çalıştırılacak..."
            if [ -f "$HISTORY_DIR/$ARCHIVE_NAME" ]; then
                cp "$HISTORY_DIR/$ARCHIVE_NAME" "$LEVELS_FILE"
            fi
        fi
    fi
done

if [ "$SUCCESS" = false ]; then
    echo -e "\n${RED}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║     ❌ Seviye üretimi başarısız!               ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════╝${NC}"
    echo -e "${RED}[HATA]${NC} ${MAX_RETRIES} deneme sonrası doğrulama geçilemedi."
    if [ -f "$HISTORY_DIR/$ARCHIVE_NAME" ]; then
        cp "$HISTORY_DIR/$ARCHIVE_NAME" "$LEVELS_FILE"
        echo -e "${YELLOW}[GERİ YÜKLEME]${NC} Eski levels.json geri yüklendi"
    fi
    exit 1
fi

# ─── 4. VPS Sync ───────────────────────────────────────────
if [ "$SKIP_SYNC" = true ] || [ "$VPS_MODE" = true ]; then
    if [ "$VPS_MODE" = true ]; then
        echo -e "\n${YELLOW}[4/5] 📍 VPS modu — dosyalar nginx dizinine kopyalanıyor...${NC}"
        sudo mkdir -p "$VPS_DATA_PATH"
        sudo cp "$LEVELS_FILE" "$VPS_DATA_PATH/levels.json"
        sudo rm -f "$VPS_DATA_PATH/level-stats.json"
        echo -e "  ${GREEN}✅ levels.json → $VPS_DATA_PATH${NC}"
    else
        echo -e "\n${YELLOW}[4/5] ⏭ VPS sync atlandı${NC}"
    fi
else
    echo -e "\n${YELLOW}[4/5] 🚀 VPS'e sync ediliyor...${NC}"
    scp -q "$LEVELS_FILE" "$VPS_HOST:$VPS_DATA_PATH/levels.json"
    # Stats temizle (yeni set yüklendi)
    ssh "$VPS_HOST" "rm -f $VPS_DATA_PATH/level-stats.json" 2>/dev/null || true
    echo -e "  ${GREEN}✅ Sync tamamlandı${NC}"
fi

# ─── 5. Health Check ───────────────────────────────────────
echo -e "\n${YELLOW}[5/5] 🏥 Health check...${NC}"
if [ "$SKIP_SYNC" != true ] && [ "$VPS_MODE" != true ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        REMOTE_VER=$(curl -s "$HEALTH_URL" | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "?")
        echo -e "  ${GREEN}✅ VPS'te v${REMOTE_VER} aktif (HTTP $HTTP_CODE)${NC}"
    else
        echo -e "  ${RED}⚠️ Health check başarısız (HTTP $HTTP_CODE)${NC}"
    fi
else
    echo -e "  ⏭ Atlandı"
fi

# ─── Sonuç ──────────────────────────────────────────────────
echo -e "\n${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Seviye üretimi tamamlandı!               ║${NC}"
echo -e "${GREEN}║  Version: v${NEW_VERSION}  Yaş: ${AGE_GROUP}  Seviye: 12     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}\n"
