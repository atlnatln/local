---
title: "Sistem Genel Görünümü"
created: 2026-05-01
updated: 2026-05-01
type: concept
tags: [meta, overview, infrastructure]
related:
  - infrastructure
  - deployment
---

# Sistem Genel Görünümü

`/home/akn/local`, VPS üzerindeki merkezi kontrol noktasıdır. Birden fazla projeyi, paylaşılan altyapıyı ve ortak yapılandırmaları tek bir monorepo çatısı altında barındırır.

## Proje Haritası

| Proje | Açıklama |
|-------|----------|
| [[ops-bot]] | Telegram operations bot — Python, systemd, sec-agent |
| [[webimar]] | Tarım İmar — Django + Next.js + React |
| [[anka]] | Anka Data — B2B veri servisi, Django + Next.js |
| [[mathlock-play]] | MathLock Play — Android math game + Django backend |
| [[telegram-kimi]] | Telegram Kimi Bridge — Python, systemd, ACP |
| [[sayi-yolculugu]] | HTML5 matematik eğitim oyunu |
| [[infrastructure]] | Paylaşılan VPS altyapısı — nginx, SSL, Docker |

## Altyapı

- **nginx** — Ters proxy, statik dosya servisi, çoklu proje yönlendirmesi
- **SSL (Certbot)** — Otomatik sertifika yenileme, HTTPS yönlendirmesi
- **Docker** — Container yönetimi (seçili projeler için)
- **systemd** — Servis yönetimi, otomatik başlatma

## Git Yapısı

- Ayrı git repo: `ops-bot`, `webimar`
- Monorepo içinde: `anka`, `mathlock-play`, `telegram-kimi`, `sayi-yolculugu`, `infrastructure`

> **Not:** Bu sayfa ingest işlemleriyle otomatik güncellenecektir.
