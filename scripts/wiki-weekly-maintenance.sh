#!/bin/bash
# ============================================================
# wiki-weekly-maintenance.sh — Haftalık wiki bakım ve rapor
# ============================================================
# Çalışma ortamı: VPS (wiki, git, lint, telegram token hepsi VPS'te)
# Kullanım: ./scripts/wiki-weekly-maintenance.sh [--notify]
#
# Yaptığı işlemler:
#   1. GitHub'dan en son wiki'yi çek (git fetch + reset)
#   2. Lint çalıştır (10/10 hedefi)
#   3. Log rotasyonu kontrolü (500+ giriş varsa arşivle)
#   4. Rapor üret ve (opsiyonel) Telegram'dan gönder
#   5. Bakım değişikliği varsa commit + push
# ============================================================

set -euo pipefail

WIKI_ROOT="/home/akn/local/wiki"
REPO_ROOT="/home/akn/local"
LINT_SCRIPT="${HOME}/.kimi/skills/local-wiki/scripts/wiki_lint.py"
REPORT_FILE="${WIKI_ROOT}/.weekly-report"
LOG_FILE="${WIKI_ROOT}/log.md"

# Telegram config (ops-bot .env'sinden oku)
TELEGRAM_TOKEN=""
ALLOWED_USER_ID=""
NOTIFY=false

# Argüman parse
for arg in "$@"; do
    case "$arg" in
        --notify) NOTIFY=true ;;
    esac
done

# ---------------------------------------------------------------------------
# Renkler
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------------------------------------------------------------------------
# 0. Telegram token oku
# ---------------------------------------------------------------------------
read_telegram_config() {
    local env_file="/home/akn/vps/ops-bot/.env"
    if [[ -f "$env_file" ]]; then
        TELEGRAM_TOKEN=$(grep "^TELEGRAM_TOKEN=" "$env_file" | cut -d'=' -f2- || true)
        ALLOWED_USER_ID=$(grep "^ALLOWED_USER_ID=" "$env_file" | cut -d'=' -f2- || true)
    fi

    if [[ -z "$TELEGRAM_TOKEN" || -z "$ALLOWED_USER_ID" ]]; then
        log_warn "Telegram config bulunamadı. Rapor sadece dosyaya yazılacak."
        NOTIFY=false
    fi
}

# ---------------------------------------------------------------------------
# 1. Git senkronizasyonu
# ---------------------------------------------------------------------------
sync_wiki() {
    log_info "GitHub senkronizasyonu kontrol ediliyor..."
    cd "$REPO_ROOT"

    git fetch origin main 2>/dev/null || {
        log_error "git fetch başarısız"
        return 1
    }

    local behind
    behind=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

    if [[ "$behind" -gt 0 ]]; then
        log_info "Wiki $behind commit geride, senkronize ediliyor..."
        if git pull origin main --ff-only; then
            log_ok "Wiki senkronize edildi."
        else
            log_error "Wiki senkronizasyonu başarısız (conflict veya diverged)."
            return 1
        fi
    else
        log_ok "Wiki zaten güncel."
    fi
}

# ---------------------------------------------------------------------------
# 2. Lint çalıştır
# ---------------------------------------------------------------------------
run_lint() {
    log_info "Lint çalıştırılıyor..."

    if [[ ! -f "$LINT_SCRIPT" ]]; then
        log_error "Lint script bulunamadı: $LINT_SCRIPT"
        return 1
    fi

    local lint_out
    lint_out=$(python3 "$LINT_SCRIPT" "$WIKI_ROOT" 2>&1) || true

    local passed total warnings failures
    passed=$(echo "$lint_out" | grep "SUMMARY:" | sed -E 's/.*SUMMARY: ([0-9]+)\/([0-9]+).*/\1/')
    total=$(echo "$lint_out" | grep "SUMMARY:" | sed -E 's/.*SUMMARY: ([0-9]+)\/([0-9]+).*/\2/')
    warnings=$(echo "$lint_out" | grep "SUMMARY:" | sed -E 's/.*([0-9]+) warning.*/\1/')
    failures=$(echo "$lint_out" | grep "SUMMARY:" | sed -E 's/.*([0-9]+) failure.*/\1/')

    # Varsayılan değerler
    passed=${passed:-0}
    total=${total:-10}
    warnings=${warnings:-0}
    failures=${failures:-0}

    echo ""
    echo "$lint_out"
    echo ""

    if [[ "$passed" -eq "$total" && "$warnings" -eq 0 && "$failures" -eq 0 ]]; then
        log_ok "Lint 10/10 ✅"
    else
        log_warn "Lint $passed/$total (warning: $warnings, failure: $failures)"
    fi

    LINT_PASSED=$passed
    LINT_TOTAL=$total
    LINT_WARNINGS=$warnings
    LINT_FAILURES=$failures
}

# ---------------------------------------------------------------------------
# 3. Log rotasyonu kontrolü
# ---------------------------------------------------------------------------
check_log_rotation() {
    log_info "Log rotasyonu kontrol ediliyor..."

    local count
    count=$(grep -c "^## \[" "$LOG_FILE" 2>/dev/null || echo "0")

    if [[ "$count" -gt 500 ]]; then
        log_warn "log.md $count giriş (>500). Rotasyon gerekli."
        ROTATION_NEEDED=true
        LOG_COUNT=$count
    else
        log_ok "log.md $count giriş (<500). Rotasyon gerekli değil."
        ROTATION_NEEDED=false
        LOG_COUNT=$count
    fi
}

# ---------------------------------------------------------------------------
# 4. Rapor hazırla
# ---------------------------------------------------------------------------
generate_report() {
    local now
    now=$(date '+%Y-%m-%d %H:%M')

    cat > "$REPORT_FILE" << EOF
📊 Wiki Haftalık Bakım Raporu
Tarih: ${now}
Makine: VPS

--- Lint ---
Sonuç: ${LINT_PASSED}/${LINT_TOTAL}
Warning: ${LINT_WARNINGS}
Failure: ${LINT_FAILURES}
Durum: $([[ "$LINT_PASSED" -eq 10 && "$LINT_WARNINGS" -eq 0 ]] && echo "✅ Mükemmel" || echo "⚠️ Kontrol gerekli")

--- Log ---
Giriş sayısı: ${LOG_COUNT}
Rotasyon: $([[ "$ROTATION_NEEDED" == true ]] && echo "⚠️ Gerekli (>500)" || echo "✅ Normal (<500)")

--- Git ---
Wiki senkronize: ✅

--- Sonraki Adımlar ---
$([[ "$LINT_PASSED" -lt 10 ]] && echo "• Lint sorunlarını düzelt" || echo "• Her şey yolunda")
$([[ "$ROTATION_NEEDED" == true ]] && echo "• log.md rotasyonu yap" || echo "")
EOF

    log_ok "Rapor hazırlandı: $REPORT_FILE"
}

# ---------------------------------------------------------------------------
# 5. Telegram bildirimi
# ---------------------------------------------------------------------------
send_telegram() {
    if [[ "$NOTIFY" != true ]]; then
        log_info "Telegram bildirimi atlandı (--notify verilmedi)"
        return 0
    fi

    if [[ -z "$TELEGRAM_TOKEN" || -z "$ALLOWED_USER_ID" ]]; then
        log_warn "Telegram config eksik, bildirim gönderilemiyor."
        return 1
    fi

    local message
    message=$(cat "$REPORT_FILE")

    log_info "Telegram bildirimi gönderiliyor..."

    local response
    response=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${ALLOWED_USER_ID}" \
        -d "text=${message}" \
        -d "parse_mode=Markdown" 2>/dev/null) || true

    if echo "$response" | grep -q '"ok":true'; then
        log_ok "Telegram bildirimi gönderildi. ✅"
    else
        log_warn "Telegram bildirimi başarısız."
        echo "$response" | head -1
    fi
}

# ---------------------------------------------------------------------------
# 6. Değişiklik varsa commit + push
# ---------------------------------------------------------------------------
commit_changes() {
    log_info "Değişiklik kontrolü..."
    cd "$REPO_ROOT"

    if git diff --cached --quiet && git diff --quiet; then
        log_ok "Değişiklik yok, commit gerekli değil."
        return 0
    fi

    git add -A
    git commit -m "chore(wiki): weekly maintenance ($(date +%Y-%m-%d))" || true

    if git push origin main 2>/dev/null; then
        log_ok "Değişiklikler GitHub'a push edildi."
    else
        log_warn "Push başarısız (muhtemelen çakışma var)."
    fi
}

# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
main() {
    echo "========================================"
    echo "  Wiki Haftalık Bakım"
    echo "  $(date)"
    echo "========================================"
    echo ""

    read_telegram_config
    sync_wiki
    run_lint
    check_log_rotation
    generate_report
    send_telegram
    commit_changes

    echo ""
    echo "========================================"
    log_ok "Haftalık bakım tamamlandı."
    echo "========================================"
}

# Değişkenler
LINT_PASSED=0
LINT_TOTAL=10
LINT_WARNINGS=0
LINT_FAILURES=0
ROTATION_NEEDED=false
LOG_COUNT=0

main "$@"
