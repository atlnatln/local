---
title: "Webimar"
created: 2026-05-01
updated: 2026-05-01
type: project
tags: [webimar, django, nextjs, react, docker, nginx]
related:
  - infrastructure
  - deployment
  - ssl-certbot
sources:
  - raw/articles/webimar-readme.md
---

# [[Webimar]]

Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun hesaplama çözümleri sunan modern web uygulaması.

## Purpose

20+ farklı tarımsal yapı türü (bağ evi, sera, hayvan barınağı, depo vb.) için mevzuata uygun hesaplama aracı. 3D görselleştirme, akıllı hesaplamalar ve mobil uyumlu arayüz.

## Stack

| Katman | Teknoloji |
|--------|-----------|
| Backend | Django + Django REST Framework |
| Frontend | Next.js 15 (App Router) + TypeScript + Styled Components |
| Hesaplamalar | React SPA (ayrı uygulama) |
| Database | PostgreSQL / SQLite |
| Auth | JWT |
| DevOps | Docker Compose, Nginx reverse proxy |

## Entry Points

| Dosya/Dizin | Görev |
|-------------|-------|
| `projects/webimar/webimar-api/` | Django backend (REST API) |
| `projects/webimar/webimar-nextjs/` | Next.js frontend (marketing + hesaplama sayfaları) |
| `projects/webimar/webimar-react/` | React SPA (hesaplama motoru) |
| `projects/webimar/deploy.sh` | VPS deploy script'i |
| `projects/webimar/docker-compose.prod.yml` | Production container'ları |

## Deploy

```bash
cd projects/webimar/
./deploy.sh --skip-github   # Docker image build + VPS upload
```

Deploy akışı:
1. `webimar-api`, `webimar-nextjs`, `webimar-react`, `nginx` image'larını build et
2. `webimar-deploy.tar.gz` oluştur
3. VPS'e scp ile upload et
4. VPS'te `setup.sh` çalıştır (DB backup, SSL, container down/up)

## Mevzuat Desteği

- 5403 Sayılı Toprak Koruma ve Arazi Kullanımı Kanunu
- 3573 Sayılı Zeytinciliğin Islahı Kanunu
- Tarım Arazileri Kullanımı Genelgesi
- İBB Plan Notları

## SEO

Open Graph, Twitter Card, JSON-LD schema, sitemap.xml, robots.txt, lazy loading, mobile-first responsive tasarım.

## Dependencies

- [[infrastructure]] — nginx ters proxy, SSL
- [[deployment]] — VPS deploy prosedürleri

## Recent Commits

- `2eb3dfa` chore: sync all local changes before deploy (2026-04-30)
