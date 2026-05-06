---
title: "Webimar"
created: 2026-05-01
updated: 2026-05-06
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
| `projects/webimar/docker-compose.prod.yml` | Production container'ları (her servise `image:` tag'i atanmış) |
| `projects/webimar/webimar-api/accounts/middleware_token_abuse.py` | Token abuse detection middleware |
| `projects/webimar/webimar-api/accounts/admin_token_blacklist.py` | Admin token blacklist helpers |
| `projects/webimar/webimar-api/accounts/validators.py` | Custom validators |
| `projects/webimar/webimar-api/accounts/views/google_auth_views.py` | Google OAuth + JWT views |
| `projects/webimar/webimar-api/accounts/views/main_views.py` | User profile /me/ endpoint |
| `projects/webimar/webimar-api/accounts/serializers.py` | User serializers |

## Deploy

### Komut

```bash
cd /home/akn/local/projects/webimar
./deploy.sh --skip-github   # Yerel build + VPS upload, GitHub push atlanır
```

Deploy script'i **ortam tespiti** yapar (`is_vps` — `/home/akn/vps` dizini varsa VPS'tedir):
- **Local'den:** Docker build → `docker save` → `tar.gz` → `scp` ile VPS'ye upload
- **VPS'ten:** Docker build yapar ancak `docker save`/`tar.gz` export adımını atlar (aynı makinede çalıştığı için); `ssh`/`scp` yerel `bash`/`cp` ile override edilir

### Adımlar

| # | Adım | Süre | VPS'te |
|---|------|------|--------|
| 1 | Docker build (api, nextjs, react, nginx) | ~5-8 dk | ✅ |
| 2 | `docker save` + `tar.gz` oluştur | ~1 dk | ⏭️ Atlanır |
| 3 | VPS'e `scp` ile upload | ~1 dk | ⏭️ Atlanır |
| 4 | VPS'te `setup.sh` (DB backup, container down/up, migration) | ~1-2 dk | ✅ |

### Ön Koşullar

- Yerel makinede **Docker daemon çalışıyor olmalı** (`systemctl is-active docker`). Çalışmıyorsa: `sudo systemctl start docker`
- `.env.production` dosyası root'ta olmalı. Deploy script otomatik symlink yapar.
- `buildx isn't installed` uyarısı korkutucu değil, build devam eder.

### Sık Sorunlar

| Hata | Çözüm |
|------|-------|
| `Cannot connect to the Docker daemon` | `sudo systemctl start docker` |
| `[eslint] import/first` | React SPA'da import'lar dosya en üstünde olmalı. Fonksiyon/const tanımlamaları import'lardan sonra gelmeli. |
| `Missing .env.production.local` | Opsiyonel, root `.env` yeterlidir. |

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

## OAuth & Token Security (2026-05-05)

Günlük güvenlik raporunda tespit edilen token sızıntısı ve `/api/accounts/me/` 500 hataları giderildi:

- **Hash fragment redirect:** `google_auth_views.py` artık JWT token'ları URL fragment/hash (`#access=xxx&refresh=yyy`) içinde gönderiyor. Fragment sunucuya iletilmez, nginx access loglarına düşmez.
- **State bypass kaldırıldı:** `settings.DEBUG` ile OAuth state kontrolünü bypass eden kod kaldırıldı.
- **Print leak temizliği:** Tüm `print()` ifadeleri `logger.debug()` ile değiştirildi.
- **`/me/` robustness:** `main_views.py` GET handler'ına try/except eklendi; `update_user_session` ve profil hataları 500 yerine loglanıp devam ediyor.
- **Profile guard:** `UserDetailSerializer` artık eksik `UserProfile`'ı `None` olarak döndürüyor (500 yerine graceful degrade).
- **Token abuse middleware:** Yeni `middleware_token_abuse.py` eklendi.
- **Admin blacklist:** `admin_token_blacklist.py` ile admin panelden token revoke desteği eklendi.
- **Token abuse cache fix (2026-05-05):** `middleware_token_abuse.py`'de saatlik IP counter cache'e `set()` yazılıyordu; JSON serializer bunu serialize edemiyordu ve her API isteğinde 500 hatası fırlatıyordu. `set()` → `list()` çevrildi, eski cache verisi `isinstance` kontrolü ile migrate ediliyor.

## Su Tahsis Belgesi Kontrolü (Geçici Durum)

2026-05-06 itibariyle 11 tarımsal yapı türü için **YAS (Yeraltı Suyu Koruma Alanı) kapalı alanında su tahsis belgesi zorunluluğu geçici olarak kaldırıldı**:

- **Kanatlı:** Yumurtacı, Etçi (Broiler), Gezen Tavuk, Hindi, Kaz/Ördek (`kanatli.py`)
- **Büyükbaş:** Süt Sığırcılığı, Besi Sığırcılığı (`buyukbas.py`)
- **Küçükbaş:** Ağıl (`kucukbas.py`)
- **Diğer:** Hara (`hara.py`), Evcil Hayvan (`evcil_hayvan.py`), Tarımsal Ürün Yıkama Tesisi (`ana_modul.py`)

Kod blokları `# GEÇİCİ: ... devre dışı (2026-05-06)` başlığıyla yorum satırına alındı; ileride tek hamlede geri açılabilir. Yıkama tesisi için YAS kontrolü (`yas_var_mi`) hâlâ aktif.

## Recent Commits

- `33b6574ea` feat(api): temporarily disable su tahsis belgesi checks for 11 structures (2026-05-06)
- `cdb21b895` fix(deploy): fix ssh() override for multi-line commands in VPS mode (2026-05-06)
- `cb8eef36b` feat(deploy): add VPS environment detection and fix image tags (2026-05-06)
- `fc83c038a` fix(accounts): replace set() with list() in token abuse middleware cache (2026-05-05)
- `29c2c8a8e` fix(accounts): secure OAuth redirect with hash fragment, harden /me/ error handling (2026-05-05)
