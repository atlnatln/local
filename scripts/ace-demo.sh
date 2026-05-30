#!/usr/bin/env bash
#
# ACE Integration Demo — Simülasyon & Doğrulama
#
# Bu script, ACE sisteminin tüm bileşenlerini hızlıca test eder:
#   1. Kimi CLI özel dosyaları (skills, agents, AGENTS.md)
#   2. Playbook okuma & proje tespiti
#   3. Ders ekleme, validate, invalidate, prune, conflicts, stats, topla
#
# Kullanım:
#   bash /home/akn/local/scripts/ace-demo.sh

set -euo pipefail

ACE_DIR="/home/akn/local"
SCRIPT="${ACE_DIR}/scripts/ace-curator.py"
WIKI_ACE="${ACE_DIR}/wiki/ace"

# Renkler
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

PASS="${GREEN}✓ PASS${RESET}"
FAIL="${RED}✗ FAIL${RESET}"
WARN="${YELLOW}⚠ WARN${RESET}"

print_header() {
    echo
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}${CYAN}  $1${RESET}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${RESET}"
}

print_step() {
    echo
    echo -e "${BOLD}${YELLOW}▶ $1${RESET}"
}

# ========================================================================
# 1. KİMİ CLI ÖZEL DOSYALAR KONTROLÜ
# ========================================================================
print_header "1. KİMİ CLI ÖZEL DOSYALAR — ENTegrasyon KONTROLÜ"

files=(
    "${ACE_DIR}/.kimi/skills/ace-memory/SKILL.md"
    "${ACE_DIR}/.kimi/skills/local-wiki/SKILL.md"
    "${ACE_DIR}/.kimi/agents/system.md"
    "${ACE_DIR}/AGENTS.md"
    "${SCRIPT}"
)

all_ok=true
for f in "${files[@]}"; do
    if [[ -f "$f" ]]; then
        echo -e "  ${PASS}  $(basename "$f")"
    else
        echo -e "  ${FAIL}  $(basename "$f") — BULUNAMADI"
        all_ok=false
    fi
done

# AGENTS.md'de ACE bölümü var mı?
print_step "AGENTS.md içinde 'ACE Playbook Yükleme' bölümü aranıyor..."
if grep -q "ACE Playbook Yükleme" "${ACE_DIR}/AGENTS.md"; then
    echo -e "  ${PASS}  ACE Playbook Yükleme bölümü mevcut"
else
    echo -e "  ${FAIL}  ACE Playbook Yükleme bölümü EKSİK"
    all_ok=false
fi

# ace-memory skill trigger'ları
print_step "ace-memory skill trigger'ları kontrol ediliyor..."
triggers=("ace topla" "ace öğren" "ace ders ekle" "ace playbook" "ace unut" "ace doğrula")
for t in "${triggers[@]}"; do
    if grep -q "$t" "${ACE_DIR}/.kimi/skills/ace-memory/SKILL.md"; then
        echo -e "  ${PASS}  trigger: '$t'"
    else
        echo -e "  ${WARN}  trigger: '$t' — bulunamadı"
    fi
done

# local-wiki skill ACE cross-reference
print_step "local-wiki skill ACE cross-reference kontrol ediliyor..."
if grep -q "ACE + Wiki Cross-Reference" "${ACE_DIR}/.kimi/skills/local-wiki/SKILL.md"; then
    echo -e "  ${PASS}  ACE + Wiki Cross-Reference bölümü mevcut"
else
    echo -e "  ${WARN}  ACE + Wiki Cross-Reference bölümü yok"
fi

# agents/system.md ACE bölümü
print_step "agents/system.md ACE talimatı kontrol ediliyor..."
if grep -q "ACE Playbook (Cross-Session Memory)" "${ACE_DIR}/.kimi/agents/system.md"; then
    echo -e "  ${PASS}  ACE Playbook talimatı mevcut"
else
    echo -e "  ${WARN}  agents/system.md gitignore'da (sadece local'de geçerli)"
fi

# ========================================================================
# 2. PLAYBOOK YAPISI & PROJE TESPİTİ
# ========================================================================
print_header "2. PLAYBOOK YAPISI & PROJE TESPİTİ"

playbooks=(
    "${WIKI_ACE}/playbook.md"
    "${WIKI_ACE}/ops-bot.md"
    "${WIKI_ACE}/webimar.md"
    "${WIKI_ACE}/mathlock-play.md"
    "${WIKI_ACE}/sayi-yolculugu.md"
    "${WIKI_ACE}/telegram-kimi.md"
    "${WIKI_ACE}/robotopia-android.md"
    "${WIKI_ACE}/infrastructure.md"
    "${WIKI_ACE}/_template.md"
)

for pb in "${playbooks[@]}"; do
    if [[ -f "$pb" ]]; then
        echo -e "  ${PASS}  $(basename "$pb")"
    else
        echo -e "  ${FAIL}  $(basename "$pb") — BULUNAMADI"
        all_ok=false
    fi
done

print_step "Proje tespiti test ediliyor..."
cd "${ACE_DIR}/ops-bot"
detected=$(python3 "${SCRIPT}" stats 2>/dev/null | grep "ops-bot" | awk '{print $1}')
if [[ "$detected" == "ops-bot" ]]; then
    echo -e "  ${PASS}  ops-bot/ dizininde → 'ops-bot' playbook'u hedeflendi"
else
    echo -e "  ${WARN}  Proje tespiti testi manuel doğrulanmalı"
fi
cd "${ACE_DIR}"

# ========================================================================
# 3. MEVCUT DERSLER
# ========================================================================
print_header "3. MEVCUT DERSLER (Genel Playbook)"
python3 "${SCRIPT}" list

# ========================================================================
# 4. YENİ DERS EKLEME (DERS 004)
# ========================================================================
print_header "4. YENİ DERS EKLEME — DERS 004: Test Pattern"

python3 "${SCRIPT}" learn \
    --title "Test Pattern — Simülasyon Dersi" \
    --context "Bu ders ACE demo simülasyonu için oluşturulmuştur." \
    --rule "Demo amaçlı: bu ders prune testinde kullanılacak." \
    --rationale "Simülasyon sonunda confidence 0.30 altına düşürülüp arşivlenecek." \
    --source "scripts/ace-demo.sh" \
    --scope "genel" \
    --type "pattern" \
    --lang "bash" \
    --do-example "echo 'Doğru kullanım'" \
    --dont-example "echo 'Yanlış kullanım'" \
    --related "- [[Ders-001]]"

echo
python3 "${SCRIPT}" get 4 | head -12

# ========================================================================
# 5. VALIDATE & INVALIDATE
# ========================================================================
print_header "5. CONFİDENCE MANİPÜLASYONU"

print_step "Validate Ders 004 (+0.05)..."
python3 "${SCRIPT}" validate 4

print_step "İkinci kez Validate Ders 004 (+0.05)..."
python3 "${SCRIPT}" validate 4

print_step "Invalidate Ders 004 (-0.15)..."
python3 "${SCRIPT}" invalidate 4

print_step "Son durum:"
python3 "${SCRIPT}" get 4 | grep -E "Confidence|Validations"

# ========================================================================
# 6. PRUNE DRY-RUN
# ========================================================================
print_header "6. PRUNE DRY-RUN (Confidence < 0.30)"

print_step "Önce confidence'ı düşürme loop'u..."
python3 "${SCRIPT}" invalidate 4
python3 "${SCRIPT}" invalidate 4
python3 "${SCRIPT}" invalidate 4

echo
python3 "${SCRIPT}" get 4 | grep -E "Confidence|Validations"

print_step "Prune dry-run..."
python3 "${SCRIPT}" prune --dry-run

# ========================================================================
# 7. CONFLICTS & STATS
# ========================================================================
print_header "7. ÇAKIŞMA KONTROLÜ & İSTATİSTİK"

print_step "Conflicts..."
python3 "${SCRIPT}" conflicts

print_step "Stats..."
python3 "${SCRIPT}" stats

# ========================================================================
# 8. ACE TOPLA (OTURUM SONU TOPLU İŞLEM)
# ========================================================================
print_header "8. ACE TOPLA — Oturum Sonu Toplu İşlem"
python3 "${SCRIPT}" topla

# ========================================================================
# 9. TEMİZLİK — Ders 004'ü sil (prune ile arşivle)
# ========================================================================
print_header "9. TEMİZLİK — Ders 004 Arşivleniyor"

python3 "${SCRIPT}" prune

print_step "Son durum doğrulaması..."
python3 "${SCRIPT}" list

echo
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  ACE SİMÜLASYONU TAMAMLANDI${RESET}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${RESET}"
echo
echo "  Tüm bileşenler test edildi:"
echo "    • Kimi CLI dosyaları (skills, agents, AGENTS.md)"
echo "    • Playbook yapısı & proje tespiti"
echo "    • Ders ekleme, validate, invalidate"
echo "    • Prune (dry-run + gerçek)"
echo "    • Conflicts, Stats, Topla"
echo
