#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "==> Bringing up Docker stack (backend deps)"
./dev-docker.sh >/dev/null

echo "==> Backend tests (pytest)"
docker compose exec -T backend pytest

echo "==> OpenAPI contract (spectacular validate + diff)"
mkdir -p artifacts
# Generate schema inside container to a writable path, then copy out.
docker compose exec -T backend sh -lc \
  'export DJANGO_SETTINGS_MODULE=project.settings.test && python manage.py spectacular --file /tmp/openapi.generated.yaml --validate --fail-on-warn && cat /tmp/openapi.generated.yaml' \
  > artifacts/openapi.generated.yaml

diff -u docs/API/openapi.yaml artifacts/openapi.generated.yaml

echo "==> Frontend (npm ci + lint + type-check + build)"
cd services/frontend
npm ci
npm run lint
npm run type-check
npm run build

# Optional security gate (kept strict but fast)
npm audit --audit-level=critical

echo "==> OK: All checks passed"
