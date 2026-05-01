---
title: "Nginx Routing"
created: "2026-05-01"
updated: "2026-05-01"
type: concept
tags: [infrastructure, nginx, networking, security]
related:
  - infrastructure
  - ssl-automation
  - log-management
  - monitoring
sources: []
---

# [[Nginx-Routing]]

VPS üzerindeki tüm projelerin domain-based routing, SSL termination, rate limiting ve static file serving yapılandırması.

## Purpose

Tek bir nginx reverse proxy üzerinden 5 farklı domain/projeye trafik yönlendirmek, SSL sonlandırması yapmak, DDoS koruması sağlamak ve static dosyaları servis etmek.

## Genel Yapı

```
[internet] → [nginx:80/443] → [conf.d/*.conf] → [upstream containers]
                                ↓
                        [static files, health checks, rate limits]
```

### nginx.conf Ana Ayarlar

| Ayar | Değer | Amaç |
|------|-------|------|
| `worker_processes` | auto | CPU çekirdeklerine göre ölçeklenme |
| `worker_connections` | 4096 | Yüksek eşzamanlılık |
| `client_max_body_size` | 20m | Dosya upload limiti |
| `resolver` | 127.0.0.11 | Docker DNS çözümlemesi |

## Rate Limiting

| Zone | Oran | Kullanım |
|------|------|----------|
| `global` | 20 req/s | Tüm siteler için temel koruma |
| `web` | 15 req/s | Web uygulamaları (webimar, anka, mathlock) |
| `api` | 5 req/s | API endpoint'leri |
| `admin` | 5 req/s | Admin/panel path'leri |
| `conn_limit_per_ip` | 50 bağlantı | IP başına bağlantı limiti |

Status: `429 Too Many Requests`

## Domain Config'leri

### ankadata.com.tr

| Özellik | Değer |
|---------|-------|
| Upstream | `anka_nginx_prod:443` (HTTPS) |
| Özel | Google auth callback'lerinde redirect loop önleme (`418 I'm a teapot`) |
| WebSocket | ✅ Upgrade/Connection desteği |
| Health | `/health/` → "anka healthy" |

### tarimimar.com.tr

| Özellik | Değer |
|---------|-------|
| Upstream | `webimar-nginx:443` (HTTPS) |
| API | `/api/` → ayrı rate limit (`api` zone) |
| WebSocket | ✅ Upgrade/Connection desteği |
| Health | `/health/` → "webimar healthy" |

### mathlock.com.tr

| Özellik | Değer |
|---------|-------|
| Upstream | Django backend (unix socket: `/var/run/mathlock/gunicorn.sock`) |
| Static | `root /var/www/mathlock/website` (landing, privacy, support) |
| Data | `/mathlock/data/` → JSON dosyaları, DAV upload (stats.json) |
| WebSocket | ❌ Yok |
| Health | `/mathlock/health` → "mathlock ok" |

### mathlock (IP-based)

| Özellik | Değer |
|---------|-------|
| Erişim | `89.252.152.222` (IP ile) |
| Amaç | APK OTA dağıtımı + data endpoint'leri |
| Static | `/mathlock/dist/` → APK ve version.json |
| Data | `/mathlock/data/` → questions.json, topics.json, stats.json |
| Güvenlik | Sadece `.apk` ve `.json` dosyalarına izin, diğerleri 403 |

## Güvenlik Başlıkları

Tüm domain'lerde global olarak:
- `X-Frame-Options: SAMEORIGIN` (global) / `DENY` (domain)
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (HTTPS domain'lerde)

## Performance Özellikleri

| Özellik | Durum |
|---------|-------|
| Gzip compression | ✅ (text, json, js, css, svg, font) |
| FastCGI cache | ✅ `/var/cache/nginx/fastcgi` |
| Proxy cache | ✅ `/var/cache/nginx/proxy` (API yanıtları) |
| Expires header | ✅ Content-type bazlı (html: epoch, css/js: 1y, image: 1M) |
| Server tokens | ❌ Kapalı (güvenlik) |

## Health Check Endpoint'leri

| Endpoint | Yanıt | Lokasyon |
|----------|-------|----------|
| `/nginx-health` | "nginx ok" | `default.conf:8080` (container içi) |
| `/nginx-status` | stub_status | `default.conf:8080` (container içi) |
| `/*/health/` | "{project} healthy" | Her projenin config'inde |

## Dependencies

- [[infrastructure]] — Docker container, volume mount'ları, ağ
- [[ssl-automation]] — Sertifika dosyaları (`/etc/nginx/ssl/`)
- [[log-management]] — Access/error log rotasyonu

## Sorun Giderme

```bash
# Nginx config test
docker exec vps_nginx_main nginx -t

# Config reload (zero-downtime)
docker exec vps_nginx_main nginx -s reload

# Rate limit logları
grep "limiting requests" /var/log/nginx/error.log

# Upstream erişilebilirlik
docker exec vps_nginx_main curl -k https://anka_nginx_prod/health/
```
