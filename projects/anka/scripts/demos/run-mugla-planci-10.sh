#!/usr/bin/env bash
set -euo pipefail

VPS_HOST="${VPS_HOST:-akn@89.252.152.222}"
VPS_PROJECT_ROOT="${VPS_PROJECT_ROOT:-/home/akn/vps/projects/anka}"

CITY="${CITY:-Muğla}"
SECTOR="${SECTOR:-Şehir plancısı}"
LIMIT="${LIMIT:-10}"
MODEL="${MODEL:-gemini-2.5-flash}"

OUTPUT_CSV="${OUTPUT_CSV:-${VPS_PROJECT_ROOT}/services/backend/artifacts/demo/mugla_planci_10.csv}"
DAILY_REQUEST_LIMIT="${DAILY_REQUEST_LIMIT:-10}"
DAILY_TOKEN_LIMIT="${DAILY_TOKEN_LIMIT:-8000}"

SSH_OPTS=(
  -o BatchMode=yes
  -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=accept-new
  -o ConnectTimeout=10
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=3
)

echo "[INFO] Muğla plancı demo çalıştırılıyor (${LIMIT} kayıt sınırı)"
ssh "${SSH_OPTS[@]}" "${VPS_HOST}" \
  CITY="$(printf '%q' "${CITY}")" \
  SECTOR="$(printf '%q' "${SECTOR}")" \
  LIMIT="$(printf '%q' "${LIMIT}")" \
  MODEL="$(printf '%q' "${MODEL}")" \
  OUTPUT_CSV="$(printf '%q' "${OUTPUT_CSV}")" \
  DAILY_REQUEST_LIMIT="$(printf '%q' "${DAILY_REQUEST_LIMIT}")" \
  DAILY_TOKEN_LIMIT="$(printf '%q' "${DAILY_TOKEN_LIMIT}")" \
  VPS_PROJECT_ROOT="$(printf '%q' "${VPS_PROJECT_ROOT}")" \
  'bash -s' <<'REMOTE_SCRIPT'
set -euo pipefail

cd "${VPS_PROJECT_ROOT}"

if [ -f ".env" ]; then
  set -a
  . ./.env
  set +a
fi

if [ -f ".env.production" ]; then
  set -a
  . ./.env.production
  set +a
fi

if [ -z "${GOOGLE_PLACES_API_KEY:-}" ]; then
  echo "[ERROR] GOOGLE_PLACES_API_KEY tanımlı değil" >&2
  exit 1
fi

if [ -z "${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}" ]; then
  echo "[ERROR] GEMINI_API_KEY veya GOOGLE_API_KEY tanımlı değil" >&2
  exit 1
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && [ -f "docker-compose.prod.yml" ]; then
  COMPOSE_FILE="docker-compose.prod.yml"
  CONTAINER_OUTPUT_CSV="${CONTAINER_OUTPUT_CSV:-/app/artifacts/demo/mugla_planci_10.csv}"

  docker compose -f "${COMPOSE_FILE}" up -d postgres redis backend >/dev/null
  docker compose -f "${COMPOSE_FILE}" exec -T backend mkdir -p "$(dirname "${CONTAINER_OUTPUT_CSV}")"

  docker compose -f "${COMPOSE_FILE}" exec -T backend \
    python manage.py run_planner_demo \
      --city "${CITY}" \
      --sector "${SECTOR}" \
      --limit "${LIMIT}" \
      --output "${CONTAINER_OUTPUT_CSV}"

  docker compose -f "${COMPOSE_FILE}" exec -T backend \
    python enrich_websites_with_gemini.py \
      --input "${CONTAINER_OUTPUT_CSV}" \
      --model "${MODEL}" \
      --limit "${LIMIT}" \
      --daily-request-limit "${DAILY_REQUEST_LIMIT}" \
      --daily-token-limit "${DAILY_TOKEN_LIMIT}" \
      --sleep 0.25

  echo "DEMO_DONE:${CONTAINER_OUTPUT_CSV}"
else
  cd "${VPS_PROJECT_ROOT}/services/backend"

  if [ -f "venv/bin/activate" ]; then
    . venv/bin/activate
  fi

  python manage.py run_planner_demo \
    --city "${CITY}" \
    --sector "${SECTOR}" \
    --limit "${LIMIT}" \
    --output "${OUTPUT_CSV}"

  python enrich_websites_with_gemini.py \
    --input "${OUTPUT_CSV}" \
    --model "${MODEL}" \
    --limit "${LIMIT}" \
    --daily-request-limit "${DAILY_REQUEST_LIMIT}" \
    --daily-token-limit "${DAILY_TOKEN_LIMIT}" \
    --sleep 0.25

  echo "DEMO_DONE:${OUTPUT_CSV}"
fi
REMOTE_SCRIPT
