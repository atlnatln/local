---
title: "Log Management"
created: "2026-05-01"
updated: "2026-05-01"
type: concept
tags: [infrastructure, monitoring, nginx, logging, docker]
related:
  - infrastructure
  - nginx-routing
  - monitoring
sources:
  - raw/articles/infrastructure-docker-compose.md
---

# [[Log-Management]]

VPS üzerindeki servis log'larının toplanması, rotasyonu ve analizi.

## Purpose

Operasyonel görünürlük, hata ayıklama, güvenlik olay analizi ve performans izleme için merkezi log yönetimi.

## Bileşenler

### 1. nginx Log'ları

| Log | Lokasyon (container) | Volume |
|-----|----------------------|--------|
| access.log | `/var/log/nginx/access.log` | `vps_nginx_logs` |
| error.log | `/var/log/nginx/error.log` | `vps_nginx_logs` |
| anka_access.log | `/var/log/nginx/anka_access.log` | `vps_nginx_logs` |
| webimar_access.log | `/var/log/nginx/webimar_access.log` | `vps_nginx_logs` |
| mathlock_access.log | `/var/log/nginx/mathlock_access.log` | `vps_nginx_logs` |

**Log formatı** (`main`):
```
$remote_addr - $remote_user [$time_local] "$request"
$status $body_bytes_sent "$http_referer"
"$http_user_agent" "$http_x_forwarded_for"
"$http_cf_connecting_ip"
rt=$request_time uct="$upstream_connect_time"
uht="$upstream_header_time" urt="$upstream_response_time"
cache_status="$upstream_cache_status"
```

### 2. Logrotate Container

```yaml
# docker-compose.yml içinde
logrotate:
  image: alpine:latest
  volumes:
    - nginx_logs:/logs/nginx
    - ./monitoring/logrotate.conf:/etc/logrotate.conf:ro
  command: sh -c "echo '0 2 * * * /usr/sbin/logrotate /etc/logrotate.conf' | crontab - && crond -f"
```

Her gece 02:00'da nginx log'larını rotate eder.

### 3. Loki + Promtail (Hazır, Pasif)

Config dosyaları mevcut ama `docker-compose.yml`'de aktif değil:

| Bileşen | Config | Durum |
|---------|--------|-------|
| Loki | `monitoring/loki/loki-config.yml` | ⚠️ Hazır ama çalışmıyor |
| Promtail | `monitoring/promtail/promtail-config.yml` | ⚠️ Hazır ama çalışmıyor |

**Aktif etmek için:**
```bash
cd /home/akn/vps/infrastructure
docker compose --profile monitoring up -d
```

Loki aktif olduğunda:
- Promtail nginx log'larını okur
- Loki'ye gönderir
- Grafana üzerinden sorgulanabilir

## Log Analizi Komutları

```bash
# Son nginx erişim log'ları
docker exec vps_nginx_main tail -f /var/log/nginx/access.log

# 5xx hataları
docker exec vps_nginx_main grep '" 5[0-9][0-9] ' /var/log/nginx/access.log

# Rate limit log'ları
docker exec vps_nginx_main grep "limiting requests" /var/log/nginx/error.log

# Anka özel log'lar
docker exec vps_nginx_main tail -f /var/log/nginx/anka_access.log

# Host üzerinden volume'dan okuma
docker volume inspect vps_nginx_logs --format '{{ .Mountpoint }}'
```

## Log Lokasyonları Özeti

| Kaynak | Host Lokasyon | Container Lokasyon |
|--------|---------------|-------------------|
| nginx access | Docker volume | `/var/log/nginx/access.log` |
| nginx error | Docker volume | `/var/log/nginx/error.log` |
| ops-bot | journald | `journalctl -u ops-bot` |
| sec-agent | journald | `journalctl -u sec-agent` |
| mathlock backend | journald | `journalctl -u mathlock-backend` |
| SSL renew | `/var/log/ssl-renew.log` | — |
| docker compose | `json-file` driver | `docker logs vps_nginx_main` |

## Dependencies

- [[infrastructure]] — Docker volume'ları, compose yapılandırması
- [[nginx-routing]] — Access/error log üreten nginx config'leri
- [[monitoring]] — Prometheus metrikleri, Grafana görselleştirme

## Eksikler / Gelecek

| İyileştirme | Durum | Fayda |
|-------------|-------|-------|
| Loki/Promtail aktif etme | ⚠️ Hazır, pasif | Merkezi log sorgulama |
| Alertmanager entegrasyonu | ❌ Yok | Log-based alerting |
| Log retention politikası | ⚠️ Basit | Disk yönetimi |
