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

# Opsiyonel ikinci compose dosyası (ör. infrastructure ağına bağlanma override'ı).
# Varsayılan: kapalı. Açmak için: VPS_WITH_INFRA=1 bash scripts/up.sh
INFRA_COMPOSE_FILE="docker-compose.infra.yml"

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

compose_files_for_dir() {
  local dir="$1"
  local base
  base="$(compose_file_for_dir "$dir")"
  echo "$base"

  if [[ "${VPS_WITH_INFRA:-}" == "1" && -f "$dir/$INFRA_COMPOSE_FILE" ]]; then
    echo "$INFRA_COMPOSE_FILE"
  fi
}

run_compose_dir() {
  local dir="$1"; shift
  local -a files
  mapfile -t files < <(compose_files_for_dir "$dir")

  local -a args
  args=()
  local f
  for f in "${files[@]}"; do
    args+=("-f" "$f")
  done

  (cd "$dir" && docker compose "${args[@]}" "$@")
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
