---
title: "Monitoring"
created: "2026-05-01"
updated: "2026-05-01"
type: concept
tags: [meta, monitoring, infrastructure, ops-bot, security]
related:
  - infrastructure
  - ops-bot
  - deployment
sources:
  - raw/articles/infrastructure-docker-compose.md
---

# [[Monitoring]]

VPS üzerindeki servislerin sağlık durumunu, metriklerini ve güvenlik olaylarını izleme ve raporlama sistemleri.

## Purpose

Proaktif sorun tespiti, performans takibi ve güvenlik olaylarının merkezi olarak izlenmesi. Hem otomatik alert'ler hem de periyodik raporlar aracılığıyla operasyonel görünürlük sağlar.

## Bileşenler

### 1. Infrastructure Monitoring Stack

| Bileşen | Teknoloji | Port | Durum |
|---------|-----------|------|-------|
| Prometheus | Time-series DB | 9090 | ✅ Aktif |
| Grafana | Görselleştirme | 3000 | ⚠️ Opsiyonel (`--profile monitoring`) |
| Nginx Health Check | HTTP endpoint | 8080 | ✅ Aktif |
| Loki | Log aggregation | 3100 | ⚠️ Hazır, pasif |
| Promtail | Log shipper | — | ⚠️ Hazır, pasif |

Prometheus, nginx ve ops-bot metriklerini toplar. Grafana ve Loki/Promtail `--profile monitoring` ile aktif edilir.

```bash
cd /home/akn/vps/infrastructure
docker compose --profile monitoring up -d
```

### 2. Ops-Bot Monitoring

| Servis | Tip | Periyot | Açıklama |
|--------|-----|---------|----------|
| `sec-agent-metrics.service` | systemd | Sürekli | Prometheus metrik sunucusu (`:9101`) |
| `ops-bot-weekly-security-report.timer` | systemd timer | Haftalık | Güvenlik özet raporu |
| `ops-bot-critical-alert.timer` | systemd timer | 3 saat | Kritik eşik kontrolü |

### 3. sec-agent Sweep

`sec-agent` 3 dakikada bir pasif decay sweep çalıştırır:

- Log toplama: nginx, sshd, auth
- Korelasyon ve skorlama (engine)
- Otomatik yanıt: block, whitelist, alert (actions)
- Metrik export: Prometheus `:9101`

## Health Check Komutları

```bash
# Nginx sağlık kontrolü
curl -f http://localhost:8080/nginx-health

# Prometheus erişimi
curl http://localhost:9090/api/v1/status/targets

# Ops-bot servis durumu
systemctl status ops-bot sec-agent

# Journal log takibi
journalctl -u ops-bot -f
journalctl -u sec-agent -f
```

## Alert Kanalları

| Kanal | Tip | Aktif mi |
|-------|-----|----------|
| Telegram bot mesajı | Anlık alert | ✅ Evet |
| Haftalık güvenlik raporu | Periyodik özet | ✅ Evet |
| Prometheus Alertmanager | Metrik-based | ⚠️ Opsiyonel |

## Dependencies

- [[infrastructure]] — nginx, Docker ağı, Prometheus container'ı
- [[ops-bot]] — sec-agent, telegram bildirimleri

### 2. Grafana Dashboard'ları

| Dashboard | Veri Kaynağı | İçerik |
|-----------|-------------|--------|
| System Overview | Prometheus | CPU, RAM, disk, ağ |
| Nginx Metrics | Prometheus | Request rate, latency, error rate |
| Application Metrics | Prometheus | Django app metrics (webimar-api) |

Varsayılan giriş: `admin` / `.env` içindeki `GRAFANA_ADMIN_PASSWORD`

### 3. Loki Log Sorguları (Aktif Edildiğinde)

```logql
# nginx 5xx hataları
{job="nginx"} |= " 5"

# Rate limit log'ları
{job="nginx"} |= "limiting requests"

# Belirli IP'den gelenler
{job="nginx"} |= "89.252.152.222"
```

## Log ve Rapor Lokasyonları

| Kaynak | Lokasyon |
|--------|----------|
| nginx access/error | `/var/log/nginx/` → sec-agent collectors / Loki |
| auth/ssh | `/var/log/auth.log` → sec-agent collectors |
| ops-bot uygulama | `journalctl -u ops-bot` |
| sec-agent metrik | `http://localhost:9101/metrics` |
| Prometheus TSDB | `infrastructure/prometheus/data/` |
| Grafana data | `infrastructure/grafana_data/` volume |

## Related Systems

- [[system-overview]] — VPS genel mimarisi
- [[deployment]] — Servis restart ve deploy prosedürleri
- [[log-management]] — nginx log rotasyonu ve Loki entegrasyonu
