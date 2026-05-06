---
title: "Anka"
created: 2026-05-01
updated: 2026-05-06
type: project
tags: [anka, django, nextjs, python, docker, archived]
status: archived
related:
  - infrastructure
  - deployment
sources:
  - raw/articles/anka-readme.md
---

# [[Anka]] (Arşivlendi)

> **Durum:** Pasife alındı — 2026-05-06
> **Neden:** Aktif kullanılmıyor, RAM/disk kaynağı serbest bırakıldı
> **Arşiv:** `backups/anka-archive-20260506.tar.gz` (local), `/home/akn/vps/backups/anka-archive/` (VPS)

B2B veri servisi: istediğiniz şehir ve sektörde doğrulanmış firma iletişim bilgilerini tek seferde alın.

## Purpose

Google Maps + Gemini enrichment hattı kullanarak, internetteki firma verilerini üç aşamalı doğrulama sürecinden geçirip temiz, doğrulanmış B2B kayıtlar sunar.

## Stack

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.11, Django 5.2, Django REST Framework |
| Async | Celery + Redis |
| Database | PostgreSQL 14 |
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Shadcn/UI |
| Altyapı | Nginx, Docker Compose |
| Harita | Google Places API (Text Search → Details Pro → Details Enterprise) |

## Core Pipeline (3 Aşamalı Doğrulama)

1. **Aday Havuzu (Tarama)** — Google Places Text Search → ID + İsim (ücretsiz)
2. **Doğrulama (Filtreleme)** — Place Details Pro → Adres + Display Name (kapanmış/taşınmış kayıtlar elenir)
3. **Zenginleştirme (Teslim)** — Place Details Enterprise → Website + Phone (sadece temiz veri için ödeme)

## Entry Points

> **Not:** Proje dizini arşivlendi. Tekrar aktifleştirmek için arşivi çıkarın.

| Dosya/Dizin | Görev |
|-------------|-------|
| `projects/anka/services/backend/` | Django backend |
| `projects/anka/services/frontend/` | Next.js frontend |
| `projects/anka/deploy.sh` | VPS deploy |
| `projects/anka/docker-compose.prod.yml` | Production container'ları |

## Deploy

```bash
# Tekrar aktifleştirmek için:
cd /home/akn/local
tar xzf backups/anka-archive-20260506.tar.gz -C projects/anka/

# VPS'te:
cd /home/akn/vps
tar xzf backups/anka-archive/anka-project.tar.gz -C projects/anka/
# Volume'ları geri yükle (gerekirse)
```

## Güvenlik ve Limitler

- Exponential Backoff (429 hatalarına karşı)
- `ANKA_BATCH_MAX_RECORDS=50` hard limit
- Circuit Breaker: %50'den fazla hata → otomatik durdurma (`PARTIAL` status)

## Dependencies

- [[infrastructure]] — nginx, SSL
- [[deployment]] — VPS deploy

## Recent Commits

- (anka ayrı git reposuna sahip değil, monorepo içinde izleniyor)
