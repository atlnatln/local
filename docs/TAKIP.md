# Durum Notları (VPS Monorepo)

Tarih: 23 Ocak 2026

## Amaç

- Infrastructure + birden fazla projeyi tek dizinden yönetmek.
- Docker modunda: iki projeyi aynı anda ayağa kaldırmak.
- Local/native modda: projeleri tek tek geliştirmek (port çakışmaları nedeniyle).

## Mevcut Durum (Özet)

- Docker dev (tek komut): `./dev-docker.sh`
  - Infrastructure (nginx/certbot/ops): `infrastructure/`
  - Webimar: `projects/webimar/` (Next 3000, React 3001, API 8001)
  - Anka: `projects/anka/` (Frontend 3100, Backend 8100)
- Compose keşif scriptleri: `scripts/up.sh`, `scripts/down.sh`, `scripts/status.sh`, `scripts/logs.sh`

## Açık Konular

- Production deploy’lar proje bazlı yürütülüyor (her proje kendi `deploy.sh` / prod compose seti ile).
- Monitoring profili ve kaynak limitleri VPS’e göre ayarlanmalı (gerekirse `infrastructure/` compose profilleriyle).
