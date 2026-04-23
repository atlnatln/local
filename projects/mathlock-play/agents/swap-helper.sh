#!/bin/bash
# ============================================================================
# AGENTS.md Swap Helper — mathlock-play scriptleri için
#
# kimi-cli her zaman CWD'deki AGENTS.md dosyasını okur.
# Birden fazla ajan kullandığımız için (matematik soruları + bulmaca seviyeleri)
# her script kendi ajan dosyasını geçici olarak AGENTS.md'ye kopyalar,
# kimi-cli'yi çalıştırır, sonra temizler/geri yükler.
#
# Kullanım (source ile):
#   source agents/swap-helper.sh
#   agents_swap_in "agents/questions.agents.md"
#   # ... kimi-cli çalıştır ...
#   agents_swap_out
#
# NOT: Eşzamanlı çalışma koruması: lockfile pattern.
# ============================================================================

_AGENTS_MD="AGENTS.md"
_AGENTS_BACKUP="AGENTS.md.swap-backup"
_AGENTS_LOCK="/tmp/mathlock-agents-swap.lock"
_AGENTS_SWAPPED=false
_AGENTS_HAD_BACKUP=false

agents_swap_in() {
    local source_file="$1"

    if [ -z "$source_file" ] || [ ! -f "$source_file" ]; then
        echo -e "\033[0;31m[AGENTS SWAP] Kaynak dosya bulunamadı: $source_file\033[0m"
        return 1
    fi

    # Lock al (eşzamanlı çalışma koruması)
    exec 9>"$_AGENTS_LOCK"
    if ! flock -n 9; then
        echo -e "\033[0;31m[AGENTS SWAP] Başka bir script zaten AGENTS.md kullanıyor. Bekleniyor...\033[0m"
        flock 9  # Blokla ve bekle
    fi

    # Mevcut AGENTS.md'yi yedekle (varsa)
    if [ -f "$_AGENTS_MD" ]; then
        cp "$_AGENTS_MD" "$_AGENTS_BACKUP"
        _AGENTS_HAD_BACKUP=true
        echo -e "\033[0;33m[AGENTS SWAP] Mevcut AGENTS.md yedeklendi → $_AGENTS_BACKUP\033[0m"
    fi

    # Ajan dosyasını AGENTS.md olarak kopyala
    cp "$source_file" "$_AGENTS_MD"
    _AGENTS_SWAPPED=true
    echo -e "\033[0;32m[AGENTS SWAP] $source_file → AGENTS.md ($(wc -l < "$_AGENTS_MD") satır)\033[0m"
}

agents_swap_out() {
    if [ "$_AGENTS_SWAPPED" = false ]; then
        return 0
    fi

    if [ "$_AGENTS_HAD_BACKUP" = true ] && [ -f "$_AGENTS_BACKUP" ]; then
        # Eski AGENTS.md'yi geri yükle
        mv "$_AGENTS_BACKUP" "$_AGENTS_MD"
        echo -e "\033[0;33m[AGENTS SWAP] AGENTS.md geri yüklendi (backup'tan)\033[0m"
    else
        # Kalıcı AGENTS.md yoktu, sil
        rm -f "$_AGENTS_MD"
        rm -f "$_AGENTS_BACKUP"
        echo -e "\033[0;33m[AGENTS SWAP] Geçici AGENTS.md silindi\033[0m"
    fi

    _AGENTS_SWAPPED=false
    _AGENTS_HAD_BACKUP=false

    # Lock bırak
    flock -u 9 2>/dev/null || true
}

# Hata/çıkışta otomatik temizlik (trap)
_agents_cleanup_trap() {
    agents_swap_out
}
trap '_agents_cleanup_trap' EXIT ERR INT TERM
