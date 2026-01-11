#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/config.sh"

mapfile -t projects < <(list_projects)
if [[ ${#projects[@]} -eq 0 ]]; then
  echo "(proje bulunamadı)" >&2
  exit 1
fi

printf "%s\n" "${projects[@]}"
