---
source_url: local
ingested: 2026-05-01
---

[Unit]
Description=OPS Bot (Telegram Operations Bot)
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=akn
Group=akn
WorkingDirectory=/home/akn/local/ops-bot
EnvironmentFile=/home/akn/local/ops-bot/.env

# PATH (kimi-cli için ~/.local/bin gerekli)
Environment=PATH=/home/akn/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# OPS Bot ayarları
Environment=OPS_BOT_REPO_ROOT=/home/akn/local/ops-bot
Environment=OPS_BOT_INSTRUCTIONS_PATH=/home/akn/local/ops-bot/.github/.kimi-instructions.md
Environment=OPS_BOT_USE_SUDO=0

# Agent dosyaları
Environment=AGENT_DIR=/home/akn/local/ops-bot/.github/agents

# User prefs DB path
Environment=OPS_BOT_USER_PREFS_DB_PATH=/home/akn/local/ops-bot/data/user_prefs.db

# Router model (hız için)
Environment=OPS_BOT_ROUTER_MODEL=kimi-code/kimi-for-coding

# Preflight kontrolleri
ExecStartPre=/home/akn/local/ops-bot/systemd/preflight.sh

# Ana bot başlat
ExecStart=/home/akn/local/ops-bot/venv/bin/python /home/akn/local/ops-bot/agent.py
Restart=always
RestartSec=3

# Loglar journalctl'a gider
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ops-bot

[Install]
WantedBy=multi-user.target
