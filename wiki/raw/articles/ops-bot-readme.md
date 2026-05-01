---
source_url: local
ingested: 2026-05-01
---

# Ops-Bot

Ops-Bot, Telegram üzerinden VPS operasyonlarını yöneten bot + sec-agent güvenlik izleme bileşenidir.

## Güncel Durum

- `ops-bot.service` aktif: Telegram komutları ve kimi-cli tabanlı ajan yönlendirme
- `sec-agent.service` aktif: sürekli güvenlik değerlendirme döngüsü
- `sec-agent.timer` aktif: 3 dakikada bir `sec-agent-once.service`
- `sec-agent-metrics.service` aktif: Prometheus metrikleri (`:9101`)
- Düşük gürültü bildirim profili aktif:
  - `ops-bot-weekly-security-report.timer` (haftalık tek özet)
  - `ops-bot-critical-alert.timer` (3 saatte bir kritik eşik kontrolü)
  - `ops-bot-daily.timer` kapalı

## Temel Dizinler

- `agent.py`: Ana Telegram bot uygulaması
- `scripts/`: Raporlama ve yardımcı scriptler
- `systemd/`: Ops-bot ve sec-agent unit/timer dosyaları
- `sec-agent/`: Güvenlik motoru (collector/engine/actions/config)
- `data/`: Bot verileri ve state dosyaları
- `docs/`: Güncel operasyon dokümantasyonu

## Operasyon Komutları

```bash
sudo systemctl status ops-bot sec-agent.service sec-agent.timer sec-agent-metrics.service
sudo systemctl list-timers --all | grep -E 'ops-bot|sec-agent'

sudo journalctl -u ops-bot -f
sudo journalctl -u sec-agent-once.service -f
sudo journalctl -u sec-agent-metrics.service -f
```

## Bildirim Akışı (Düşük Gürültü)

- Haftalık özet: `scripts/weekly_security_digest.py`
- Kritik alarm: `scripts/critical_security_alert.py`
- Amaç: mesaj kutusunu doldurmadan yalnızca yüksek sinyal olayları iletmek

Detaylar için: `docs/CURRENT_SYSTEM.md`
