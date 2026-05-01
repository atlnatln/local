---
title: "Infrastructure"
created: 2026-05-01
updated: 2026-05-01
type: project
tags: [infrastructure, nginx, docker, ssl, monitoring]
related:
  - deployment
  - ssl-certbot
sources:
  - raw/articles/infrastructure-docker-compose.md
  - raw/articles/infrastructure-setup-script.md
---

# [[Infrastructure]]

VPS üzerinde çoklu projeyi tek nginx reverse proxy altında barındıran ortak altyapı.

## Purpose

Tüm projelerin (webimar, anka, mathlock) tek bir VPS'te çalışmasını sağlayan ortak altyapı: nginx reverse proxy, SSL sertifikaları, monitoring, Docker ağı.

## Stack

| Bileşen | Teknoloji |
|---------|-----------|
| Reverse Proxy | Nginx (Docker: `vps_nginx_main`) |
| SSL | Let's Encrypt + Certbot (host cron) |
| Monitoring | Prometheus (opsiyonel, port 9090) |
| Ağ | `vps_infrastructure_network` (Docker) |

## Entry Points

| Dosya/Dizin | Görev |
|-------------|-------|
| `infrastructure/docker-compose.yml` | nginx + prometheus servisleri |
| `infrastructure/nginx/conf.d/` | Domain routing config'leri |
| `infrastructure/setup.sh` | Infrastructure kurulum script'i |
| `infrastructure/renew-ssl.sh` | SSL yenileme |
| `infrastructure/ssl/` | SSL sertifikaları |

## Domain Routing

| Domain | Proje |
|--------|-------|
| `tarimimar.com.tr` | [[webimar]] |
| `ankadata.com.tr` | [[anka]] |
| `mathlock.com.tr` | [[mathlock-play]] |

## SSL

- Sertifikalar: `/etc/letsencrypt/live/`
- Container'a mount: `infrastructure/ssl/`
- Otomatik yenileme: `renew-ssl.sh` (host cron)

## Health Check

```bash
curl -f http://localhost:8080/nginx-health
```

## Dependencies

- [[deployment]] — VPS kurulum prosedürleri
- [[ssl-certbot]] — SSL sertifika yönetimi

## Recent Commits

- (monorepo içinde izleniyor)
