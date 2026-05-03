---
title: "Security AI Reporting"
created: "2026-05-02"
updated: "2026-05-02"
type: concept
tags: [security, monitoring, ops-bot, automation, telegram-bot]
related:
  - ops-bot
  - monitoring
  - log-management
  - adr-002-sec-agent-daily-report-agent-router
sources: []
---

# [[Security-AI-Reporting]]

`sec-agent` günlük raporunun `kimi-cli` tabanlı AI analizinden geçirilmesi ve sonucun Telegram üzerinden kullanıcıya iletilmesi akışı.

## Purpose

Güvenlik olaylarının yalnızca ham sayılarla değil, yapay zeka yorumlamasıyla birlikte sunulması. Böylece kullanıcı hem ne olduğunu hem de neden önemli olduğunu tek mesajda anlar.

## Flow

```
┌─────────────────────┐     ┌──────────────────────────┐     ┌─────────────────┐
│ sec-agent collector │────▶│ critical_security_alert  │────▶│  Telegram (1)   │
│   (events.jsonl)    │     │      .py (daily mode)    │     │  Daily Digest   │
└─────────────────────┘     └────────────┬─────────────┘     └─────────────────┘
                                         │
                    ┌────────────────────┘
                    │ anomaly detection
                    ▼
         ┌──────────────────────┐
         │ ai_security_analyzer │  ← subprocess, kimi-cli tabanlı
         │       .py            │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  🤖 AI Güvenlik      │  ← Telegram (2)
         │     Analizi          │
         └──────────────────────┘
```

## Components

| Bileşen | Dosya | Görev |
|---------|-------|-------|
| Günlük özet üretici | `ops-bot/scripts/critical_security_alert.py` | `events.jsonl` + `ip_state.json` okur, özet mesaj oluşturur |
| AI analiz motoru | `ops-bot/scripts/ai_security_analyzer.py` | Anomaly listesini kimi-cli üzerinden yorumlar |
| Telegram gönderici | `critical_security_alert.py` içinde `_send_telegram()` | `api.telegram.org/bot{TOKEN}/sendMessage` çağrısı |
| Zamanlayıcı | `ops-bot/systemd/ops-bot-critical-alert.timer` | Günde 1 kez 08:00'de tetikler (`DAILY_DIGEST_MODE=true`) |

## Execution Conditions

AI analizi çalışması için **tümü** sağlanmalı:

1. `DAILY_DIGEST_MODE=true` (günlük özet modu aktif)
2. `AI_ANALYZER_AVAILABLE=true` (`ai_security_analyzer.py` import edilebiliyor)
3. Anomaly listesinde en az bir `critical` veya `high` severity kayıt var
4. `CRITICAL_ALERT_COOLDOWN_MINUTES` (varsayılan 360 dk) süresi dolmuş

## Telegram Message Format

### Mesaj 1 — Günlük Özet

```
📊 Günlük Güvenlik Özeti (02.05.2026)
━━━━━━━━━━━━━━━━━━━━━━━
⚙️ Mod: enforce | 📏 Pencere: 24 saat
🎚️ Tehdit seviyesi: 🟢 DÜŞÜK

📈 Son 24 Saat İstatistikleri:
  Toplam event: 12,450
  Kritik event (skor≥90): 3
  Tekil IP: 45 (3 kritik)
  Kaynak: HTTP: 12,000 | SSH: 450

🧱 Aksiyonlar:
  BLOCK: 1 | RATELIMIT: 2
  Aktif blok: 1 | Aktif ratelimit: 2

🎯 Top Kritik IP'ler:
- 192.0.2.1: 2 event

🔒 Kalıcı Saldırganlar (skor≥1000 VEYA aktif blok):
- yok

♻️ Tekrar Edenler (72 saat):
- yok

📊 IP State: 245 kayıtlı IP
```

### Mesaj 2 — AI Analizi (koşullu)

Sadece critical/high anomaly varsa gönderilir:

```
🤖 AI GÜVENLİK ANALİZİ
━━━━━━━━━━━━━━━━━━━━━━

[ai_security_analyzer.py çıktısı]
```

## Environment Variables

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `DAILY_DIGEST_MODE` | `false` | `true` olduğunda günde 1 özet raporu üretir |
| `CRITICAL_WINDOW_MINUTES` | `15` | Rapor penceresi (günlük modda 24 saat = 1440 dk önerilir) |
| `CRITICAL_SCORE_THRESHOLD` | `90` | Kritik event skor eşiği |
| `CRITICAL_ALERT_COOLDOWN_MINUTES` | `360` | Aynı alarmın tekrar gönderilmeme süresi |
| `TELEGRAM_BOT_TOKEN` | — | Telegram Bot API token |
| `TELEGRAM_CHAT_ID` | — | Hedef kullanıcı/chat ID |

## Dependencies

- [[ops-bot]] — Telegram bot altyapısı ve systemd servisleri
- [[monitoring]] — Prometheus metrikleri ve health check
- [[log-management]] — nginx/auth log kaynakları

## Notes

- `ops-bot-daily.timer` sistemde **kapalıdır** (düşük gürültü politikası). Günlük raporlama `ops-bot-critical-alert.timer` üzerinden `DAILY_DIGEST_MODE=true` ile yapılır.
- AI analizi ikinci mesaj olarak gönderilir; ilk mesaj başarısız olursa ikincisi de atlanmaz ama state kaydedilmez.
- `ai_security_analyzer.py` kimi-cli'yi subprocess olarak çağırır, doğrudan python kütüphanesi olarak entegre değildir.
