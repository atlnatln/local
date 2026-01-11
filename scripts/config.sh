#!/usr/bin/env bash
set -euo pipefail

# Repo kökü ve projeler dizini
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="${PROJECTS_DIR:-"$ROOT_DIR/projects"}"

# Compose dosyası adı tercih sırası.
# Projelerinizde farklı bir isim varsa buraya ekleyin.
COMPOSE_CANDIDATES=(
  "docker-compose.yml"
  "compose.yml"
  "docker-compose.dev.yml"
)

project_dir() {
  local project="$1"
  echo "$PROJECTS_DIR/$project"
}

list_projects() {
  if [[ ! -d "$PROJECTS_DIR" ]]; then
    return 0
  fi

  local d
  for d in "$PROJECTS_DIR"/*; do
    [[ -d "$d" ]] || continue
    if compose_file_for_dir "$d" >/dev/null 2>&1; then
      basename "$d"
    fi
  done
}

compose_file_for_dir() {
  local dir="$1"
  local candidate
  for candidate in "${COMPOSE_CANDIDATES[@]}"; do
    if [[ -f "$dir/$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

run_compose_dir() {
  local dir="$1"; shift
  local file
  file="$(compose_file_for_dir "$dir")"
  (cd "$dir" && docker compose -f "$file" "$@")
}

run_compose() {
  local project="$1"; shift
  local dir
  dir="$(project_dir "$project")"
  if [[ ! -d "$dir" ]]; then
    echo "❌ Proje dizini yok: $dir" >&2
    return 1
  fi
  run_compose_dir "$dir" "$@"
}
