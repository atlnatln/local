#!/usr/bin/env bash
# ============================================================
# auto-sync.sh — Session başında çalıştırılan git sync script'i
# ============================================================
# Tek kişi, iki ortam (local/VPS) senaryosu için:
#   - Her session açılışında GitHub'daki son değişiklikleri çek
#   - Behind varsa otomatik pull, ahead varsa bilgi ver
#
# Kullanım:
#   bash scripts/auto-sync.sh
#
# Çıktı:
#   - Sync: sessizce devam
#   - Behind: auto-pull yapılır
#   - Ahead: "push bekliyor" uyarısı
#   - Conflict: hata raporu, manuel müdahale gerekli
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPOS=(
    "/home/akn/local:local"
    "/home/akn/local/ops-bot:ops-bot"
    "/home/akn/local/projects/webimar:webimar"
)

PULLED=()
AHEAD=()
SYNC=()

for entry in "${REPOS[@]}"; do
    IFS=':' read -r path name <<< "$entry"
    cd "$path" || continue

    # Fetch (sessiz)
    if ! git fetch origin 2>/dev/null; then
        echo -e "${YELLOW}⚠️  $name: fetch başarısız (offline veya auth hatası)${NC}"
        continue
    fi

    # Behind/Ahead kontrolü
    read -r behind ahead <<< "$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo '0 0')"

    if [[ "$behind" -gt 0 && "$ahead" -gt 0 ]]; then
        # Diverged — hem behind hem ahead (conflict riski)
        echo -e "${RED}❌ $name: DIVERGED — $behind behind, $ahead ahead${NC}"
        echo "   → Manuel çözüm gerekli: cd $path && git status"
    elif [[ "$behind" -gt 0 ]]; then
        # Behind — auto-pull
        echo -e "${BLUE}📥 $name: $behind commit behind — pulling...${NC}"
        if git pull origin main --ff-only 2>/dev/null; then
            PULLED+=("$name ($behind commit)")
            echo -e "${GREEN}✅ $name: pull tamamlandı${NC}"
        else
            echo -e "${RED}❌ $name: pull başarısız (conflict?)${NC}"
            echo "   → Manuel çözüm: cd $path && git pull origin main"
        fi
    elif [[ "$ahead" -gt 0 ]]; then
        # Ahead — push bekliyor
        AHEAD+=("$name ($ahead commit)")
        echo -e "${YELLOW}⬆️  $name: $ahead commit ahead — push bekliyor${NC}"
    else
        SYNC+=("$name")
    fi
done

# Özet
echo ""
echo -e "${BLUE}=== AUTO-SYNC ÖZET ===${NC}"
if [[ ${#PULLED[@]} -gt 0 ]]; then
    echo -e "${GREEN}✅ Pulled:${NC} ${PULLED[*]}"
fi
if [[ ${#AHEAD[@]} -gt 0 ]]; then
    echo -e "${YELLOW}⬆️  Ahead (push gerekli):${NC} ${AHEAD[*]}"
fi
if [[ ${#SYNC[@]} -gt 0 ]]; then
    echo -e "${GREEN}✅ Sync:${NC} ${SYNC[*]}"
fi
if [[ ${#PULLED[@]} -eq 0 && ${#AHEAD[@]} -eq 0 && ${#SYNC[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  Hiçbir repo işlenemedi (offline veya erişim hatası)${NC}"
fi
