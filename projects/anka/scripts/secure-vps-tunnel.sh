#!/usr/bin/env bash
set -euo pipefail

VPS_HOST="${VPS_HOST:-akn@89.252.152.222}"
BACKEND_LOCAL_PORT="${BACKEND_LOCAL_PORT:-18010}"
BACKEND_REMOTE_PORT="${BACKEND_REMOTE_PORT:-8100}"
FRONTEND_LOCAL_PORT="${FRONTEND_LOCAL_PORT:-13100}"
FRONTEND_REMOTE_PORT="${FRONTEND_REMOTE_PORT:-3100}"

usage() {
  cat <<'EOF'
Usage:
  secure-vps-tunnel.sh backend
  secure-vps-tunnel.sh frontend
  secure-vps-tunnel.sh all

Environment overrides:
  VPS_HOST, BACKEND_LOCAL_PORT, BACKEND_REMOTE_PORT,
  FRONTEND_LOCAL_PORT, FRONTEND_REMOTE_PORT
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

mode="$1"

ssh_opts=(
  -o BatchMode=yes
  -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=accept-new
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=3
)

case "$mode" in
  backend)
    exec ssh "${ssh_opts[@]}" -N -L "${BACKEND_LOCAL_PORT}:127.0.0.1:${BACKEND_REMOTE_PORT}" "$VPS_HOST"
    ;;
  frontend)
    exec ssh "${ssh_opts[@]}" -N -L "${FRONTEND_LOCAL_PORT}:127.0.0.1:${FRONTEND_REMOTE_PORT}" "$VPS_HOST"
    ;;
  all)
    exec ssh "${ssh_opts[@]}" -N \
      -L "${BACKEND_LOCAL_PORT}:127.0.0.1:${BACKEND_REMOTE_PORT}" \
      -L "${FRONTEND_LOCAL_PORT}:127.0.0.1:${FRONTEND_REMOTE_PORT}" \
      "$VPS_HOST"
    ;;
  *)
    usage
    exit 1
    ;;
esac
