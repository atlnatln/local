#!/bin/bash
# repo-status.sh — Tüm repo'ların durumunu tek komutla göster
# Kullanım: bash scripts/repo-status.sh

ROOT="/home/akn/local"

echo "=== local (root) ==="
git -C "$ROOT" status --short

for dir in ops-bot projects/webimar projects/mathlock-play; do
  path="$ROOT/$dir"
  [ -d "$path/.git" ] || continue
  out=$(git -C "$path" status --short)
  [ -n "$out" ] && echo "" && echo "=== $dir ===" && echo "$out"
done
