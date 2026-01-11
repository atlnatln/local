#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/config.sh"

mapfile -t projects < <(list_projects)
if [[ ${#projects[@]} -eq 0 ]]; then
	echo "❌ Hiç proje bulunamadı. Projeleri $PROJECTS_DIR altına koyun." >&2
	exit 1
fi

for p in "${projects[@]}"; do
	printf "\n== %s ==\n" "$p"
	run_compose "$p" ps || true
done
