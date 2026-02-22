#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] Bu script root olarak çalışmalıdır (sudo)." >&2
  exit 1
fi

echo "[INFO] VPS hardening başlatılıyor..."

SSHD_CONFIG="/etc/ssh/sshd_config"
BACKUP_PATH="/etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)"

cp -a "${SSHD_CONFIG}" "${BACKUP_PATH}"
echo "[INFO] sshd_config backup: ${BACKUP_PATH}"

set_sshd_value() {
  local key="$1"
  local value="$2"

  if grep -Eq "^[[:space:]#]*${key}[[:space:]]+" "${SSHD_CONFIG}"; then
    sed -i -E "s|^[[:space:]#]*(${key})[[:space:]]+.*|\1 ${value}|" "${SSHD_CONFIG}"
  else
    printf "%s %s\n" "${key}" "${value}" >> "${SSHD_CONFIG}"
  fi
}

set_sshd_value "PermitRootLogin" "no"
set_sshd_value "PasswordAuthentication" "no"
set_sshd_value "KbdInteractiveAuthentication" "no"
set_sshd_value "ChallengeResponseAuthentication" "no"
set_sshd_value "PubkeyAuthentication" "yes"
set_sshd_value "MaxAuthTries" "3"
set_sshd_value "AllowUsers" "akn"
set_sshd_value "X11Forwarding" "no"
set_sshd_value "AllowTcpForwarding" "yes"
set_sshd_value "ClientAliveInterval" "300"
set_sshd_value "ClientAliveCountMax" "2"

if command -v sshd >/dev/null 2>&1; then
  sshd -t
else
  /usr/sbin/sshd -t
fi

if ! systemctl reload ssh 2>/dev/null; then
  systemctl reload sshd
fi
echo "[INFO] SSH hardening uygulandı ve servis reload edildi"

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ufw fail2ban unattended-upgrades

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "[INFO] UFW kuralları uygulandı"

mkdir -p /etc/fail2ban/jail.d
cat > /etc/fail2ban/jail.d/sshd.local <<'JAIL'
[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = systemd
maxretry = 4
findtime = 10m
bantime = 1h
JAIL

systemctl enable --now fail2ban
systemctl restart fail2ban

if [[ -f /etc/apt/apt.conf.d/20auto-upgrades ]]; then
  sed -i 's|"0";|"1";|g' /etc/apt/apt.conf.d/20auto-upgrades || true
fi
systemctl enable unattended-upgrades || true

echo "[INFO] Hardening tamamlandı"
echo "[INFO] Sonraki adım: scripts/security/vps-hardening-check.sh ile doğrulayın"
