---
title: "Telegram Kimi"
created: "2026-05-01"
updated: "2026-05-03"
type: project
tags: [telegram-kimi, python, telegram-bot, systemd, security]
related:
  - infrastructure
  - deployment
  - ops-bot
sources:
  - raw/articles/telegram-kimi-readme.md
  - raw/articles/telegram-kimi-plan.md
---

# [[Telegram-Kimi]]

VPS'deki [[kimi-code-cli|Kimi Code CLI]]'yi Telegram üzerinden kullanmanızı sağlayan köprü botudur. Yetkili kullanıcılar doğrudan mesajlaşarak kimi ile sohbet edebilir, dosya gönderebilir ve context/token kullanımını izleyebilir.

## Purpose

Telegram botu aracılığıyla [[kimi-code-cli|Kimi CLI]]'ye uzaktan erişim sağlar. Özellikle mobil cihazlardan VPS'teki AI asistanına doğal dilde komut göndermeyi mümkün kılar. Uzun yanıtlar otomatik parçalanır, dosya okuma desteği vardır.

## Stack

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | Python 3, `python-telegram-bot` 20.7 |
| Protocol | ACP (Agent Client Protocol) — JSON-RPC 2.0 over stdio (kimi-cli 1.40.0) |
| Client | `acp_client.py` — async NDJSON stdio client |
| Auth | Telegram user ID whitelist |
| Deploy | `systemd` servisi (VPS) |
| Tunnel | `autossh` reverse SSH tunnel (local → VPS:9876) |

## Entry Points

| Dosya | Görev |
|-------|-------|
| `projects/telegram-kimi/bot.py` | Async Telegram bot (676 satır) |
| `projects/telegram-kimi/acp_client.py` | ACP JSON-RPC stdio client |
| `projects/telegram-kimi/config.py` | Ortam değişkenleri yönetimi |
| `projects/telegram-kimi/systemd/telegram-kimi.service` | systemd unit dosyası |

## ACP Entegrasyonu

Bot, [[kimi-code-cli|Kimi CLI]]'nin `kimi acp` modunu kullanır. Akış:

```
initialize → session/new → session/prompt
session/update streaming: agent_message_chunk, tool_call, usage_update
session/request_permission: InlineKeyboard (✅ Onayla / ❌ Reddet)
```

- Session persistence: Birden fazla mesajda session yaşar
- `session/cancel` desteği
- Permission schema: `{"request_id": "...", "response": "approve"}` (kimi-cli 1.40 format)
- Yeni handler: `method: "request"` + `type: "ApprovalRequest"` (legacy `session/request_permission` backward compatible)

## Bot Komutları

| Komut | Açıklama |
|-------|----------|
| `/start` | Otomatik mod (local açıksa local, kapalıysa VPS) |
| `/start local` | Local bilgisayardaki kimi CLI |
| `/start vps` | VPS'teki kimi CLI |
| `/stop` | Kimi'yi kapat |
| `/cancel` | Aktif işlemi iptal et |
| `/help` | Yardım mesajı |

## Dosya Desteği

- `.txt` dosya okuma (max 1MB / 30K karakter)
- `.xlsx`, `.xlsm`, `.xls` — Sheet isimleri, satır/sütun, ilk 20 satır
- ````vba` blokları otomatik `.vba` dosyası olarak gönderilir
- `.png`, `.jpg` fotoğraflar (caption ile birlikte gönderilir)

## Context & Token Takibi

- **kimi-cli 1.40.0 öncesi:** `context.jsonl` → son `_usage` satırı okunur, `config.toml` → `max_context_size`
- **kimi-cli 1.40.0:** ACP `usage_update` notification'ı artık context bilgisi iletmiyor — token takibi deferred (teknik borç)
- Her yanıt sonunda footer: `📊 Context: 12.3k / 262.1k (4.7%)` (şu an boş gösteriyor)

## Reverse SSH Tunnel

Local PC'den VPS'e güvenli erişim:

```bash
# Local PC'de çalışan systemd servis
autossh -M 0 -N -R 9876:localhost:22 akn@89.252.152.222
```

- SSH server sadece `127.0.0.1` dinler
- Password auth kapalı
- SSH key-based auth (VPS ↔ local)

## Deploy

```bash
cd /home/akn/vps/projects/telegram-kimi
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
sudo cp systemd/telegram-kimi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-kimi
sudo systemctl start telegram-kimi
```

## Bilinen Sınırlamalar

- ACP modu `/help`, `/clear`, `/plan`, `/task` slash komutlarını desteklemiyor
- `ctrl+s` (araya prompt sokma) ve `ctrl+x` (shell mode) desteklenmiyor
- Context/token kullanım bilgisi ACP üzerinden sınırlı görünür

## Dependencies

- [[infrastructure]] — nginx ters proxy, SSL
- [[deployment]] — VPS deploy prosedürleri
- [[ops-bot]] — Aynı VPS üzerinde çalışan diğer Telegram bot

## Recent Commits

- (monorepo içinde izleniyor)
