#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/config.sh"

target="${1:-all}"

if [[ "$target" == "all" ]]; then
  mapfile -t projects < <(list_projects)
  if [[ ${#projects[@]} -eq 0 ]]; then
    echo "❌ Hiç proje bulunamadı ($PROJECTS_DIR)." >&2
    exit 1
  fi

  # Birden fazla proje için -f takibi tek terminalde pratik değil.
  # Kısa kuyruk gösterip çıkıyoruz.
  for p in "${projects[@]}"; do
    echo "== $p (tail) =="
    run_compose "$p" logs --tail=200 || true
    echo
  done

  echo "İpucu: canlı takip için:"
  echo "  bash scripts/logs.sh <proje-adi>"
  exit 0
fi

run_compose "$target" logs -f --tail=200
