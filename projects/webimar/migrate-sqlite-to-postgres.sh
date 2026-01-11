#!/usr/bin/env bash
set -euo pipefail

# Webimar SQLite -> Postgres one-time migration helper
# - Runs on the host that has this repo + docker compose
# - Uses the existing api_database volume (/app/data) to stage the dump

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.prod.yml}
DUMP_PATH_IN_VOLUME=${DUMP_PATH_IN_VOLUME:-/app/data/sqlite_dump.json}

echo "[1/5] Postgres ayağa kaldırılıyor"
docker compose -f "$COMPOSE_FILE" up -d postgres

echo "[2/5] (Öneri) API yazmasını durdurmak için webimar-api stop"
docker compose -f "$COMPOSE_FILE" stop webimar-api || true

echo "[3/5] SQLite'dan dump alınıyor -> ${DUMP_PATH_IN_VOLUME}"
docker compose -f "$COMPOSE_FILE" run --rm \
  -e DATABASE_URL="sqlite:////app/data/db.sqlite3" \
  webimar-api sh -c "python manage.py dumpdata --exclude contenttypes --exclude auth.permission --exclude admin.logentry --indent 2 > '${DUMP_PATH_IN_VOLUME}'"

echo "[4/5] Postgres migrate uygulanıyor"
docker compose -f "$COMPOSE_FILE" run --rm webimar-api sh -c "python manage.py migrate --noinput"

echo "[5/5] Dump Postgres'e yükleniyor"
docker compose -f "$COMPOSE_FILE" run --rm webimar-api sh -c "python manage.py loaddata '${DUMP_PATH_IN_VOLUME}'"

echo "Tamam: SQLite verisi Postgres'e aktarıldı. Şimdi 'docker compose -f $COMPOSE_FILE up -d' çalıştırabilirsiniz."