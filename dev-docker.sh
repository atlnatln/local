#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

port_in_use() {
  local port="$1"
  if command_exists lsof; then
    lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  elif command_exists ss; then
    ss -ltnp | awk '{print $4}' | grep -q ":${port}$"
    return $?
  elif command_exists fuser; then
    fuser -n tcp "$port" >/dev/null 2>&1
    return $?
  fi
  return 1
}

free_port() {
  local port="$1"
  if command_exists fuser; then
    fuser -k "$port"/tcp >/dev/null 2>&1 || true
  elif command_exists lsof; then
    local pids
    pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$pids" ]; then
      kill $pids 2>/dev/null || true
    fi
  fi
}

ensure_docker() {
  if ! command_exists docker; then
    echo -e "${RED}❌ Docker bulunamadı.${NC}"
    exit 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker çalışmıyor.${NC}"
    exit 1
  fi
}

ensure_network() {
  local net_name="vps_infrastructure_network"
  if ! docker network inspect "$net_name" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Network yok, oluşturuluyor: ${net_name}${NC}"
    docker network create "$net_name" >/dev/null
  fi
}

stop_local_dev_if_any() {
  echo -e "${YELLOW}🧹 Local dev süreçleri kontrol ediliyor...${NC}"

  local webimar_pid_file="$ROOT_DIR/projects/webimar/.dev-local.pids"
  if [ -f "$webimar_pid_file" ]; then
    echo -e "${YELLOW}⚠️  Webimar local PID dosyası bulundu, süreçler durduruluyor...${NC}"
    while IFS= read -r line; do
      pid="${line#*=}"
      if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null || true
      fi
    done < "$webimar_pid_file"
    rm -f "$webimar_pid_file"
  fi

  local ports=(3000 3001 8000)
  for port in "${ports[@]}"; do
    if port_in_use "$port"; then
      echo -e "${YELLOW}⚠️  Port $port kullanımda, boşaltılıyor...${NC}"
    fi
    free_port "$port"
    sleep 1
  done
}

ensure_ports_free() {
  local required_ports=(80 443 8080 3000 3001 8001 8100 3100 5432 6379)
  local busy=false

  for port in "${required_ports[@]}"; do
    if port_in_use "$port"; then
      echo -e "${RED}❌ Port kullanımda: ${port}${NC}"
      if command_exists lsof; then
        lsof -iTCP:"$port" -sTCP:LISTEN || true
      fi
      busy=true
    fi
  done

  if [ "$busy" = true ]; then
    echo -e "${YELLOW}⚠️  Port çakışması var. Local servisleri kapatıp tekrar deneyin.${NC}"
    exit 1
  fi
}

start_infrastructure() {
  echo -e "${BLUE}▶ Infrastructure başlatılıyor...${NC}"
  (cd "$ROOT_DIR/infrastructure" && docker compose up -d)
}

stop_webimar_existing() {
  echo -e "${YELLOW}🛑 Webimar mevcut container'ları kapatılıyor...${NC}"
  (cd "$ROOT_DIR/projects/webimar" && docker compose -f docker-compose.yml -f docker-compose.infra.yml down --remove-orphans >/dev/null 2>&1 || true)
  docker rm -f webimar-nginx-1 >/dev/null 2>&1 || true
}

start_webimar() {
  echo -e "${BLUE}▶ Webimar (docker) başlatılıyor...${NC}"
  (cd "$ROOT_DIR/projects/webimar" && docker compose -f docker-compose.yml -f docker-compose.infra.yml down --remove-orphans >/dev/null 2>&1 || true)
  (cd "$ROOT_DIR/projects/webimar" && docker compose -f docker-compose.yml -f docker-compose.infra.yml up -d --remove-orphans)
}

start_anka() {
  echo -e "${BLUE}▶ Anka (docker) başlatılıyor...${NC}"
  (cd "$ROOT_DIR/projects/anka" && docker compose up -d --remove-orphans)
}

show_status() {
  echo -e "${GREEN}✅ Tüm servisler başlatıldı.${NC}"
  echo -e "${BLUE}Durum (Infrastructure):${NC}"
  (cd "$ROOT_DIR/infrastructure" && docker compose ps)
  echo -e "${BLUE}Durum (Webimar):${NC}"
  (cd "$ROOT_DIR/projects/webimar" && docker compose -f docker-compose.yml -f docker-compose.infra.yml ps)
  echo -e "${BLUE}Durum (Anka):${NC}"
  (cd "$ROOT_DIR/projects/anka" && docker compose ps)
}

ensure_docker
ensure_network
stop_local_dev_if_any
stop_webimar_existing
ensure_ports_free
start_infrastructure
start_webimar
start_anka
show_status
