---
title: "Deployment"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [concept, deployment, docker, nginx]
related:
  - infrastructure
  - ops-bot
  - ssl-certbot
---

# Deployment

## Tanım

Deployment, bir yazılım projesinin üretim ortamına (VPS) kurulması, yapılandırılması ve kullanıma alınması sürecidir. Bu süreç kod derleme, bağımlılık kurulumu, ortam değişkenleri ayarı, veritabanı migrasyonu, ters proxy yapılandırması ve servis başlatma adımlarını içerir.

## Bağlam

Bu konsept aşağıdaki projelerde kullanılmaktadır:

- [[ops-bot]] — PM2 ile Node.js process yönetimi (systemd)
- [[webimar]] — Docker image build + nginx ters proxy
- [[anka]] — Docker Compose deploy
- [[infrastructure]] — nginx, SSL ve sistem servisleri yapılandırması

## Notlar

> Bu sayfa ingest ile doldurulacak. Şu an yapılandırma placeholder'idir.
