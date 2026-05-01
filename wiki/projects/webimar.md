---
title: "Webimar"
created: 2026-05-01
updated: 2026-05-02
type: project
tags: [webimar, django, nextjs, react, docker, nginx]
related:
  - infrastructure
  - deployment
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
| Auth | JWT (SimpleJWT) + Google OAuth 2.0 |
| Permissions | DRF `IsAuthenticated` default + explicit `AllowAny` on public endpoints |
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

## Security Hardening (2026-05-02)

Production API güvenlik sıkılaştırması:
- `settings.py`: `DEBUG` default `False`, `SECRET_KEY` default kaldırıldı (zorunlu env), `GOOGLE_OAUTH_CLIENT_ID` default boş string yapıldı
- `settings.py`: `TRACKING_LOG_RESPONSE_BODY` default `False` — varsayılan olarak response body loglama kapalı
- `settings.py`: CORS `http://` production origin'leri (`tarimimar.com.tr`, `tarlada-ruhsat.com.tr`) kaldırıldı
- **Permission flip:** `DEFAULT_PERMISSION_CLASSES` `AllowAny` → `IsAuthenticated`. Tüm public endpoint'lere (hesaplama, health, flowering, maps vb.) explicit `@permission_classes([AllowAny])` eklendi
- **.env cleanup:** Git'te takip edilen `.env` dosyaları (`webimar-react/.env`, `webimar-nextjs/.env.production`, `.env.local.backup`) silindi. Sadece `.env.production.example` şablonu bırakıldı

## Recent Commits

- `e22b7782` security(phase-1): harden defaults, CORS, tracking, add AllowAny to public endpoints (2026-05-02)
- `416474ac` security(phase-2): flip DEFAULT_PERMISSION_CLASSES to IsAuthenticated + cleanup .env files (2026-05-02)
