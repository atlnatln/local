#!/usr/bin/env bash
set -euo pipefail

TARGET_IP="${TARGET_IP:-89.252.152.222}"

ok() { echo "[OK] $1"; }
warn() { echo "[WARN] $1"; }
fail() { echo "[FAIL] $1"; }

check_sshd_value() {
  local key="$1"
  local expected="$2"
  local actual
  actual="$(sudo awk -v k="$key" 'BEGIN{IGNORECASE=1} $1==k {v=$2} END{print v}' /etc/ssh/sshd_config)"
  if [[ "${actual}" == "${expected}" ]]; then
    ok "${key}=${expected}"
  else
    fail "${key} beklenen=${expected}, mevcut=${actual:-<boş>}"
  fi
}

echo "[INFO] SSHD ayarları kontrolü"
check_sshd_value "PermitRootLogin" "no"
check_sshd_value "PasswordAuthentication" "no"
check_sshd_value "KbdInteractiveAuthentication" "no"
check_sshd_value "PubkeyAuthentication" "yes"
check_sshd_value "MaxAuthTries" "3"

if sudo grep -Eq '^AllowUsers[[:space:]]+.*\bakn\b' /etc/ssh/sshd_config; then
  ok "AllowUsers içinde akn mevcut"
else
  fail "AllowUsers içinde akn bulunamadı"
fi

echo "[INFO] Firewall kontrolü"
UFW_STATUS="$(sudo ufw status | tr -s ' ')"
echo "${UFW_STATUS}" | grep -q "Status: active" && ok "UFW aktif" || fail "UFW aktif değil"

for port in 22 80 443; do
  if echo "${UFW_STATUS}" | grep -Eq "${port}/tcp[[:space:]]+ALLOW"; then
    ok "${port}/tcp izinli"
  else
    fail "${port}/tcp izinli değil"
  fi
done

echo "[INFO] fail2ban kontrolü"
if sudo systemctl is-active --quiet fail2ban; then
  ok "fail2ban aktif"
else
  fail "fail2ban aktif değil"
fi

if sudo fail2ban-client status sshd >/dev/null 2>&1; then
  ok "fail2ban sshd jail aktif"
else
  fail "fail2ban sshd jail aktif değil"
fi

echo "[INFO] Sunucu IP kontrolü"
if hostname -I | tr -s ' ' | grep -qw "${TARGET_IP}"; then
  ok "Sunucu IP (${TARGET_IP}) host üstünde görüldü"
else
  warn "Sunucu IP (${TARGET_IP}) hostname -I çıktısında bulunamadı"
fi

echo "[INFO] Kontrol tamamlandı"
