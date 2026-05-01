---
title: "Sistem Genel Gorunumu"
created: 2025-05-01
updated: 2025-05-01
type: concept
tags: [meta, overview, infrastructure]
related:
  - infrastructure
  - deployment
---

# Sistem Genel Gorunumu

`/home/akn/local`, VPS uzerindeki merkezi kontrol noktasidir. Birden fazla projeyi, paylasilan altyapiyi ve ortak yapilandirmalari tek bir monorepo catisi altinda barindirir.

## Proje Haritasi

| Proje | Aciklama |
|-------|----------|
| [[ops-bot]] | Telegram operations bot — Python, systemd |
| [[webimar]] | Agriculture platform — Django + Next.js + React |
| [[anka]] | Sector analysis platform — Django + Next.js |
| [[mathlock-play]] | Android math game + Django backend |
| [[telegram-kimi]] | Telegram Kimi bot |
| [[sayi-yolculugu]] | Sayi yolculugu projesi |
| [[infrastructure]] | Paylasilan VPS altyapisi — nginx, SSL, Docker, systemd |

## Altyapi

- **nginx** — Ters proxy, statik dosya servisi, coklu proje yonlendirmesi
- **SSL (Certbot)** — Otomatik sertifika yenileme, HTTPS yonlendirmesi
- **Docker** — Container yonetimi (secili projeler icin)
- **systemd** — Servis yonetimi, otomatik baslatma, log rotasyonu

## Git Yapisi

- Bazi projeler kendi `.git` reposuna sahip: `ops-bot`, `webimar`
- Diger projeler ana monorepo icinde izlenmektedir
- `infrastructure` yapilandirmalari ana repo kokundedir

> **Not:** Bu sayfa ingest islemleriyle otomatik guncellenecektir.
