---
title: "Ops-Bot"
created: 2026-05-01
updated: 2026-05-01
type: project
tags: [ops-bot, python, telegram-bot, systemd, security]
related:
  - infrastructure
  - deployment
  - ssl-certbot
sources:
  - raw/articles/ops-bot-readme.md
  - raw/articles/ops-bot-deploy-script.md
---

# [[Ops-Bot]]

Telegram üzerinden VPS operasyonlarını yöneten bot + `sec-agent` güvenlik izleme bileşeni.

## Purpose

Kullanıcıların Telegram üzerinden VPS'ye komut göndermesini, ajanlara soru yönlendirmesini ve güvenlik olaylarını izlemesini sağlar. Düşük gürültü bildirim profili ile mesaj kutusunu doldurmadan yüksek sinyal olayları iletir.

## Stack

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | Python 3, `python-telegram-bot` |
| Agent Router | `routing.py` — heuristic agent seçimi |
| Conversation | `conversation_memory.py` — SQLite tabanlı, rolling summary |
| User Prefs | `user_preferences.py` — model seçimi, kişiselleştirme |
| Security | `sec-agent/` — collector/engine/actions/config |
| Deploy | `./deploy.sh` → VPS `systemd` servisi |

## Entry Points

| Dosya | Görev |
|-------|-------|
| `ops-bot/agent.py` | Ana Telegram bot uygulaması (2399 satır) |
| `ops-bot/routing.py` | Agent seçim mantığı, 10+ uzman ajan |
| `ops-bot/deploy.sh` | VPS deploy script'i (package/git modları) |
| `ops-bot/systemd/ops-bot.service` | systemd unit dosyası |

## Agent Sistemi

`routing.py` içinde tanımlı uzman ajanlar:

- `ops-database-agent` — PostgreSQL/sorgu işlemleri
- `ops-docker-agent` — Container yönetimi
- `ops-monitor-agent` — Sistem izleme (CPU, RAM, disk)
- `ops-incident-agent` — 502/500 gibi olay müdahalesi
- `ops-security-agent` / `ops-security-explain` / `ops-security-observe` — Güvenlik
- `ops-fix-agent` — Otomatik düzeltme önerileri
- `ops-ip-query-agent` — IP/trafik analizi
- `ops-forensic-agent` — Adli inceleme
- `ops-seo-agent` — SEO/performans

Agent seçimi: kullanıcı sorusundaki anahtar kelimelere göre heuristic eşleme.

## Servisler

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `ops-bot.service` | systemd | Ana Telegram bot |
| `sec-agent.service` | systemd | Sürekli güvenlik değerlendirme döngüsü |
| `sec-agent.timer` | systemd timer | 3 dk'da bir `sec-agent-once.service` |
| `sec-agent-metrics.service` | systemd | Prometheus metrikleri (`:9101`) |
| `ops-bot-weekly-security-report.timer` | systemd timer | Haftalık özet |
| `ops-bot-critical-alert.timer` | systemd timer | 3 saatte bir kritik eşik kontrolü |

## Deploy

```bash
cd ops-bot/
./deploy.sh              # package modu (default): tar.gz oluştur, scp et
./deploy.sh --mode git   # git modu: VPS'te git pull + restart
```

Deploy akışı:
1. SSH multiplexing ile rate-limit'ten kaçınma
2. `tar.gz` paketi oluşturma (package modu) veya `git push` (git modu)
3. VPS'te `setup.sh` çalıştırma
4. `systemctl restart ops-bot`

## Security (sec-agent)

`sec-agent/` alt yapısı:
- `collectors/` — Log toplama (nginx, sshd, auth)
- `engine/` — Korelasyon ve skorlama
- `actions/` — Otomatik yanıt (block, whitelist, alert)
- `config/` — Kurallar ve eşikler
- `docs/` — Operasyon dokümantasyonu

## Dependencies

- infrastructure — nginx ters proxy, SSL
- [[deployment]] — VPS deploy prosedürleri

## Recent Commits

- `ab28161` chore: sync all local changes before deploy (2025-04-30)
- `ad62f2a` ops-bot: resolve_model_name() bilinmeyen model ID'lerini DEFAULT_MODEL'e düşürür
- `5b8b80c` ops-bot: fallback unknown model IDs to DEFAULT_MODEL in get_user_model()
- `1971d75` ops-bot: Copilot CLI → kimi-cli migration
- `7eac8f1` sec-agent: passive decay sweep double-counting bug düzeltildi
