#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/config.sh"

target="${1:-all}"

if [[ "$target" == "all" ]]; then
  mapfile -t projects < <(list_projects)
  if [[ ${#projects[@]} -eq 0 ]]; then
    echo "❌ Hiç proje bulunamadı. Projeleri $PROJECTS_DIR altına koyun ve kökte compose dosyası olduğundan emin olun." >&2
    exit 1
  fi
  for p in "${projects[@]}"; do
    echo "== up: $p =="
    run_compose "$p" up -d
  done
  exit 0
fi

run_compose "$target" up -d
