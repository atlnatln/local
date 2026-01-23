#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TARGET="${1:-all}"
PID_FILE="$ROOT_DIR/.dev-local.pids"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

check_requirements() {
  local missing=false
  for cmd in python3 node npm; do
    if ! command_exists "$cmd"; then
      echo -e "${RED}❌ Eksik komut: ${cmd}${NC}"
      missing=true
    fi
  done
  if [ "$missing" = true ]; then
    exit 1
  fi
}

cleanup() {
  echo -e "${YELLOW}🛑 Local servisler durduruluyor...${NC}"
  if [ -f "$PID_FILE" ]; then
    while IFS= read -r line; do
      pid="${line#*=}"
      if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null || true
      fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
  fi
  echo -e "${GREEN}✅ Durduruldu.${NC}"
}

start_webimar() {
  echo -e "${BLUE}▶ Webimar (local) başlatılıyor...${NC}"
  (cd "$ROOT_DIR/projects/webimar" && bash ./dev-local.sh --background)
}

start_anka() {
  echo -e "${BLUE}▶ Anka (local) başlatılıyor...${NC}"
  (cd "$ROOT_DIR/projects/anka" && bash ./dev-local.sh) &
  echo "ANKA_DEV_PID=$!" >> "$PID_FILE"
}

check_requirements

if [[ "$TARGET" == "webimar" ]]; then
  start_webimar
  exit 0
fi

if [[ "$TARGET" == "anka" ]]; then
  start_anka
  exit 0
fi

# all: port çakışmaları nedeniyle aynı anda local çalıştırma mümkün değil
# Webimar (8000/3000/3001) ve Anka (8000/3000/3001) çakışıyor.
echo -e "${YELLOW}⚠️  Local modda iki proje aynı anda çalıştırılamaz (port çakışması).${NC}"
echo -e "${YELLOW}   Kullanım: ./dev-local.sh webimar | ./dev-local.sh anka${NC}"
exit 1
