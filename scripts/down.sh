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
  for p in "${projects[@]}"; do
    echo "== down: $p =="
    run_compose "$p" down
  done
  exit 0
fi

run_compose "$target" down
