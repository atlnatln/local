#!/bin/bash
# ============================================================================
# MathLock AI — Tam Otomatik Soru Üretim Pipeline
#
# Bu script 50 soru çözüldükten sonra otomatik tetiklenir:
#   1. stats.json analiz edilir
#   2. Copilot (gpt-4.1) yeni 50 soru + konu anlatımları üretir
#   3. validate-questions.py ile doğrulanır (başarısızsa tekrar dener)
#   4. VPS nginx'e data sync edilir
#   5. Telefon yeni soruları indirir
#
# Kullanım:
#   ./ai-generate.sh              # Tam otomasyon
#   ./ai-generate.sh --dry-run    # Sadece durumu göster
#   ./ai-generate.sh --skip-sync  # VPS sync atla (local test)
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$PROJECT_DIR/data"
STATS_FILE="$DATA_DIR/stats.json"
QUESTIONS_FILE="$DATA_DIR/questions.json"
TOPICS_FILE="$DATA_DIR/topics.json"
HISTORY_DIR="$DATA_DIR/history"
VALIDATOR="$PROJECT_DIR/validate-questions.py"
VPS_HOST="akn@89.252.152.222"
VPS_DATA_PATH="/home/akn/vps/projects/mathlock/data"
MAX_RETRIES=2

cd "$PROJECT_DIR"

# ─── Argümanlar ─────────────────────────────────────────────────────────────
DRY_RUN=false
SKIP_SYNC=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)    DRY_RUN=true; shift ;;
        --skip-sync)  SKIP_SYNC=true; shift ;;
        --help)
            echo "Kullanım: $0 [--dry-run] [--skip-sync]"
            echo "  --dry-run    Analiz yap ama Copilot çalıştırma"
            echo "  --skip-sync  VPS sync atla"
            exit 0
            ;;
        *) echo "Bilinmeyen: $1"; exit 1 ;;
    esac
done

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       🧠 MathLock AI — Otomatik Soru Üretimi         ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"

# ─── 0. VPS'ten stats.json çek (telefon oraya yüklüyor) ────────────────────
echo -e "\n${YELLOW}[0/5] 📥 VPS'ten stats.json çekiliyor...${NC}"
if scp -q "${VPS_HOST}:${VPS_DATA_PATH}/stats.json" "$STATS_FILE" 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} stats.json VPS'ten indirildi"
else
    echo -e "${YELLOW}[INFO]${NC} VPS'te stats.json bulunamadı — başlangıç seti üretilecek"
fi

# ─── 1. Mevcut Durumu Göster ─────────────────────────────────────────────────
echo -e "\n${YELLOW}[1/5] 📊 Mevcut durum kontrol ediliyor...${NC}"

CURRENT_VERSION="?"
if [ -f "$QUESTIONS_FILE" ]; then
    CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('$QUESTIONS_FILE'))['version'])" 2>/dev/null || echo "?")
    echo -e "${GREEN}[MEVCUT]${NC} questions.json v${CURRENT_VERSION}"
else
    echo -e "${YELLOW}[UYARI]${NC} questions.json bulunamadı — ilk set üretilecek"
fi

if [ -f "$STATS_FILE" ]; then
    STATS_CORRECT=$(python3 -c "import json; d=json.load(open('$STATS_FILE')); print(d.get('totalCorrect','?'))" 2>/dev/null || echo "?")
    STATS_TOTAL=$(python3 -c "import json; d=json.load(open('$STATS_FILE')); print(d.get('totalShown','?'))" 2>/dev/null || echo "?")
    echo -e "${GREEN}[STATS]${NC} Son performans: ${STATS_CORRECT}/${STATS_TOTAL} doğru"
else
    echo -e "${YELLOW}[INFO]${NC} stats.json yok — başlangıç seti üretilecek"
fi

if [ -f "$TOPICS_FILE" ]; then
    TOPIC_COUNT=$(python3 -c "import json; print(len(json.load(open('$TOPICS_FILE'))))" 2>/dev/null || echo "?")
    echo -e "${GREEN}[TOPICS]${NC} ${TOPIC_COUNT} konu anlatımı mevcut"
fi

# ─── Dry run ─────────────────────────────────────────────────────────────────
if [ "$DRY_RUN" = true ]; then
    echo -e "\n${YELLOW}[DRY-RUN]${NC} Durum gösterildi, çıkılıyor."
    exit 0
fi

# ─── 2. Arşivleme ───────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[2/5] 📁 Mevcut dosyalar arşivleniyor...${NC}"
mkdir -p "$HISTORY_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -f "$QUESTIONS_FILE" ]; then
    cp "$QUESTIONS_FILE" "$HISTORY_DIR/questions_v${CURRENT_VERSION}_${TIMESTAMP}.json"
    echo -e "${GREEN}[OK]${NC} questions arşivlendi"
fi
if [ -f "$STATS_FILE" ]; then
    cp "$STATS_FILE" "$HISTORY_DIR/stats_v${CURRENT_VERSION}_${TIMESTAMP}.json"
    echo -e "${GREEN}[OK]${NC} stats arşivlendi"
fi

# Son 20 arşiv dosyası kalsın
find "$HISTORY_DIR" -name "*.json" -type f | sort | head -n -20 | xargs -r rm -f

# ─── 3. Copilot Çalıştır ────────────────────────────────────────────────────
echo -e "\n${YELLOW}[3/5] 🤖 Copilot ile yeni sorular üretiliyor...${NC}"

PROMPT="Sen MathLock uygulaması için ilkokul 2. sınıf matematik sorusu üreten bir AI'sın.

GÖREV: AGENTS.md dosyasındaki tüm kuralları oku ve uygula. data/stats.json varsa analiz et, yoksa başlangıç seti üret.

ADIMLAR:
1. AGENTS.md dosyasını tamamen oku — şemaları, zorluk kurallarını, 2. sınıf prensiplerini öğren
2. data/stats.json oku (varsa) — çocuğun performansını analiz et
3. data/questions.json oku — mevcut version numarasını al
4. data/topics.json oku — mevcut konu anlatımlarını gör
5. Yeni 50 soru üret → data/questions.json'a yaz (üzerine yaz)
6. Konu anlatımlarını güncelle → data/topics.json'a yaz (zayıf alanları detaylandır)
7. Analiz raporunu stdout'a yazdır (AGENTS.md'deki formatta)

KRİTİK KURALLAR:
- Sadece data/questions.json ve data/topics.json değiştir, başka dosyaya dokunma
- Tam 50 soru, her cevap doğru hesaplanmış
- version = mevcut version + 1
- Cevaplar negatif olamaz (2. sınıf)
- Geçerli JSON, UTF-8
- İlk 5 soru kolay olsun (moral), son 5 soru orta zorlukta (bitirme hissi)"

# Retry döngüsü: başarısızsa tekrar dene
ATTEMPT=0
SUCCESS=false

while [ $ATTEMPT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo -e "\n${CYAN}[Deneme ${ATTEMPT}/${MAX_RETRIES}]${NC}"

    # Copilot CLI çalıştır
    # --allow-all = --allow-all-tools + --allow-all-paths + --allow-all-urls
    # Otomasyon için gerekli: tool/path/URL onay promptlarını atlar
    COPILOT_BIN="$(command -v copilot 2>/dev/null || echo "$HOME/.config/Code/User/globalStorage/github.copilot-chat/copilotCli/copilot")"
    if [ ! -x "$COPILOT_BIN" ]; then
        echo -e "${RED}[HATA]${NC} Copilot CLI bulunamadı!"
        exit 1
    fi
    "$COPILOT_BIN" -p "$PROMPT" --model gpt-4.1 --allow-all --autopilot 2>&1

    # ─── 4. Doğrulama ───────────────────────────────────────────────────────
    echo -e "\n${YELLOW}[4/5] 🔍 Doğrulama çalıştırılıyor...${NC}"
    if python3 "$VALIDATOR"; then
        SUCCESS=true
        echo -e "${GREEN}[OK]${NC} Doğrulama başarılı!"
    else
        echo -e "${RED}[HATA]${NC} Doğrulama başarısız (deneme ${ATTEMPT}/${MAX_RETRIES})"
        if [ $ATTEMPT -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}[TEKRAR]${NC} Copilot tekrar çalıştırılacak..."
            # Arşivden geri yükle
            if [ -f "$HISTORY_DIR/questions_v${CURRENT_VERSION}_${TIMESTAMP}.json" ]; then
                cp "$HISTORY_DIR/questions_v${CURRENT_VERSION}_${TIMESTAMP}.json" "$QUESTIONS_FILE"
            fi
        fi
    fi
done

if [ "$SUCCESS" = false ]; then
    echo -e "\n${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║          ❌ Soru üretimi başarısız!                    ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo -e "${RED}[HATA]${NC} ${MAX_RETRIES} deneme sonrası doğrulama geçilemedi."
    echo "  Eski soru seti korunuyor, telefon mevcut soruları kullanmaya devam eder."
    # Arşivden geri yükle
    if [ -f "$HISTORY_DIR/questions_v${CURRENT_VERSION}_${TIMESTAMP}.json" ]; then
        cp "$HISTORY_DIR/questions_v${CURRENT_VERSION}_${TIMESTAMP}.json" "$QUESTIONS_FILE"
    fi
    exit 1
fi

# ─── 5. VPS Sync ────────────────────────────────────────────────────────────
if [ "$SKIP_SYNC" = false ]; then
    echo -e "\n${YELLOW}[5/5] 🚀 VPS'e senkronize ediliyor...${NC}"

    # data/ dizinini VPS'e kopyala
    ssh "$VPS_HOST" "mkdir -p ${VPS_DATA_PATH}"
    scp "$QUESTIONS_FILE" "${VPS_HOST}:${VPS_DATA_PATH}/questions.json"
    scp "$TOPICS_FILE" "${VPS_HOST}:${VPS_DATA_PATH}/topics.json"
    echo -e "${GREEN}[OK]${NC} questions.json ve topics.json VPS'e yüklendi"

    # stats.json'ı temizle (yeni döngü başlıyor)
    if [ -f "$STATS_FILE" ]; then
        rm "$STATS_FILE"
        ssh "$VPS_HOST" "rm -f ${VPS_DATA_PATH}/stats.json"
        echo -e "${GREEN}[OK]${NC} stats.json temizlendi (yeni 50 soru döngüsü başlıyor)"
    fi

    # Sağlık kontrolü
    sleep 1
    HEALTH=$(ssh "$VPS_HOST" "curl -sf http://89.252.152.222/mathlock/data/questions.json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f\"v{d[\\\"version\\\"]} — {len(d[\\\"questions\\\"])} soru\")' 2>/dev/null || echo 'FAIL'")
    if [ "$HEALTH" != "FAIL" ]; then
        echo -e "${GREEN}[OK]${NC} VPS endpoint çalışıyor: ${HEALTH}"
    else
        echo -e "${YELLOW}[UYARI]${NC} VPS endpoint yanıt vermedi — nginx config kontrol edin"
    fi
else
    echo -e "\n${YELLOW}[5/5] ⏭️  VPS sync atlandı${NC}"
fi

# ─── Sonuç ───────────────────────────────────────────────────────────────────
NEW_VERSION=$(python3 -c "import json; print(json.load(open('$QUESTIONS_FILE'))['version'])" 2>/dev/null || echo "?")
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        ✅ Yeni soru seti hazır!                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  📦 Versiyon: v${CURRENT_VERSION} → v${NEW_VERSION}"
echo -e "  📱 Telefon uygulamayı açtığında yeni soruları otomatik indirecek"
echo ""
echo -e "${CYAN}Tam Döngü:${NC}"
echo -e "  Çocuk 50 soru çözer → stats VPS'e yüklenir → bu script çalışır"
echo -e "  → AI yeni 50 soru üretir → doğrulanır → telefon güncellenir"
