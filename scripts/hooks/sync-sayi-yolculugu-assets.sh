#!/bin/bash
# ============================================================
# Sayı Yolculuğu → MathLock Play Android Asset Senkronizasyonu
# ============================================================
# Bu script, sayi-yolculugu geliştirme dizinindeki değişiklikleri
# mathlock-play Android asset dizinine kopyalar.
#
# Tetikleyiciler:
#   - Git pre-commit hook (önerilen)
#   - Manuel çalıştırma: bash scripts/hooks/sync-sayi-yolculugu-assets.sh
# ============================================================

set -e

SRC="/home/akn/local/projects/sayi-yolculugu"
DST="/home/akn/local/projects/mathlock-play/app/src/main/assets/sayi-yolculugu"

if [ ! -d "$SRC" ]; then
    echo "HATA: Kaynak dizin bulunamadı: $SRC"
    exit 1
fi

if [ ! -d "$DST" ]; then
    echo "HATA: Hedef dizin bulunamadı: $DST"
    exit 1
fi

CHANGED=0

# ── JS dosyaları ────────────────────────────────────────────
for f in "$SRC"/js/game-*.js "$SRC"/js/android-bridge.js; do
    name=$(basename "$f")
    if [ -f "$f" ]; then
        if [ ! -f "$DST/js/$name" ] || ! diff -q "$f" "$DST/js/$name" >/dev/null 2>&1; then
            cp "$f" "$DST/js/$name"
            echo "  📦 SYNC: js/$name"
            CHANGED=1
        fi
    fi
done

# ── CSS ─────────────────────────────────────────────────────
if [ ! -f "$DST/css/game.css" ] || ! diff -q "$SRC/css/game.css" "$DST/css/game.css" >/dev/null 2>&1; then
    cp "$SRC/css/game.css" "$DST/css/game.css"
    echo "  📦 SYNC: css/game.css"
    CHANGED=1
fi

# ── Audio ───────────────────────────────────────────────────
for f in "$SRC"/audio/*; do
    name=$(basename "$f")
    if [ -f "$f" ]; then
        if [ ! -f "$DST/audio/$name" ] || ! diff -q "$f" "$DST/audio/$name" >/dev/null 2>&1; then
            cp "$f" "$DST/audio/$name"
            echo "  📦 SYNC: audio/$name"
            CHANGED=1
        fi
    fi
done

# ── game.html ───────────────────────────────────────────────
if [ ! -f "$DST/game.html" ] || ! diff -q "$SRC/game.html" "$DST/game.html" >/dev/null 2>&1; then
    cp "$SRC/game.html" "$DST/game.html"
    echo "  📦 SYNC: game.html"
    CHANGED=1
fi

# ── Özet ────────────────────────────────────────────────────
if [ "$CHANGED" = "1" ]; then
    echo ""
    echo "✅ Android asset'leri senkronize edildi."
    echo "   Hedef: $DST"
else
    echo "✅ Android asset'leri zaten güncel."
fi

exit 0
