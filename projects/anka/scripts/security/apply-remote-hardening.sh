#!/usr/bin/env bash
set -euo pipefail

VPS_HOST="${VPS_HOST:-akn@89.252.152.222}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SSH_OPTS=(
  -o BatchMode=yes
  -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=accept-new
  -o ConnectTimeout=10
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=3
)

echo "[INFO] Hardening script VPS üzerinde uygulanıyor: ${VPS_HOST}"
ssh "${SSH_OPTS[@]}" "${VPS_HOST}" 'sudo bash -s' < "${SCRIPT_DIR}/vps-hardening.sh"

echo "[INFO] Hardening check VPS üzerinde çalıştırılıyor"
ssh "${SSH_OPTS[@]}" "${VPS_HOST}" 'bash -s' < "${SCRIPT_DIR}/vps-hardening-check.sh"

echo "[OK] Uzak hardening uygulaması tamamlandı"
