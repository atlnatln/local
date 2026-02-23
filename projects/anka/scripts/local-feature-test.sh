#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUN_E2E=0
ALLOW_REMOTE=0

usage() {
  cat <<'EOF'
Usage:
  ./scripts/local-feature-test.sh [--with-e2e] [--allow-remote]

Options:
  --with-e2e      Playwright smoke testini de çalıştırır
  --allow-remote  BACKEND_URL/BASE_URL remote ise güvenlik engelini kaldırır

Varsayılan güvenlik davranışı:
  - Sadece localhost/127.0.0.1 endpointlerine izin verir
  - Yanlışlıkla prod domain/IP'e test trafiği gitmesini engeller
EOF
}

for arg in "$@"; do
  case "$arg" in
    --with-e2e)
      RUN_E2E=1
      ;;
    --allow-remote)
      ALLOW_REMOTE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Bilinmeyen argüman: $arg"
      usage
      exit 1
      ;;
  esac
done

BASE_URL="${BASE_URL:-http://localhost:3100}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8100}"

is_remote_url() {
  local url="$1"
  [[ "$url" =~ ankadata\.com\.tr|89\.252\.152\.222 ]] && return 0
  [[ "$url" =~ localhost|127\.0\.0\.1 ]] && return 1
  return 0
}

if [[ "$ALLOW_REMOTE" -ne 1 ]]; then
  if is_remote_url "$BASE_URL" || is_remote_url "$BACKEND_URL"; then
    echo "[GUARD] Remote endpoint tespit edildi."
    echo "  BASE_URL=$BASE_URL"
    echo "  BACKEND_URL=$BACKEND_URL"
    echo "Güvenlik için durduruldu. Bilinçli olarak remote test istiyorsanız --allow-remote kullanın."
    exit 2
  fi
fi

echo "[INFO] BASE_URL=$BASE_URL"
echo "[INFO] BACKEND_URL=$BACKEND_URL"

echo "[STEP] Docker dev stack ayakta mı kontrol ediliyor..."
if ! docker compose ps --services --filter status=running | grep -q '^backend$'; then
  echo "[INFO] Backend çalışmıyor, dev stack başlatılıyor..."
  ./dev-docker.sh >/dev/null
fi

echo "[STEP] Backend odaklı testler çalıştırılıyor..."
docker compose exec -T backend pytest \
  apps/exports/tests/test_tasks.py \
  apps/batches/tests/test_pipeline.py \
  -q

if [[ "$RUN_E2E" -eq 1 ]]; then
  echo "[STEP] Playwright smoke testi çalıştırılıyor..."
  BASE_URL="$BASE_URL" BACKEND_URL="$BACKEND_URL" npx playwright test tests/e2e/playwright/smoke.spec.ts
fi

echo "[OK] Local feature test tamamlandı."
