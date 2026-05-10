---
title: "Deployment"
created: 2026-05-01
updated: 2026-05-05
type: concept
tags: [concept, deployment, docker, nginx, git]
related:
  - infrastructure
  - ops-bot
  - webimar
  - anka
---

# Deployment

VPS (canlı) ortamına kod gönderme süreci. Her projenin kendi deploy yöntemi vardır.

---

## Webimar Deploy

Webimar, yerelde Docker image build edilip VPS'e `tar.gz` olarak gönderilir.

### Komut

```bash
cd /home/akn/local/projects/webimar
./deploy.sh --skip-github
```

> `--skip-github`: GitHub push atlamak için. Sadece yerel build + VPS upload.

### Adımlar

| Adım | Açıklama | Süre |
|------|----------|------|
| 1. Docker build | `webimar-api`, `webimar-nextjs`, `webimar-react`, `nginx` image'ları build edilir | ~5-8 dk |
| 2. Paketleme | `webimar-deploy.tar.gz` oluşturulur | ~1 dk |
| 3. VPS upload | `scp` ile VPS'e gönderilir | ~1 dk |
| 4. VPS setup | DB backup, container down/up, migration | ~1-2 dk |

### Ön Koşullar

- Yerelde **Docker daemon çalışıyor olmalı** (`systemctl is-active docker`)
- `.env.production` dosyası mevcut olmalı (deploy script symlink yapar)
- `NEXT_PUBLIC_*` değişkenleri `.env`'de tanımlı olmalı

### Sık Karşılaşılan Sorunlar

| Sorun | Çözüm |
|-------|-------|
| `Cannot connect to the Docker daemon` | `sudo systemctl start docker` |
| `buildx isn't installed` uyarısı | Uyarıdır, build devam eder (eski builder kullanır) |
| `.env.production.local` eksik uyarısı | Opsiyoneldir, root `.env` yeterlidir |

### VPS Tarafı

VPS'te container'lar `docker compose up` ile başlar. Manuel müdahale gerekiyorsa:

```bash
ssh akn@89.252.152.222
cd /home/akn/vps/projects/webimar
docker compose -f docker-compose.prod.yml up -d
```

---

## Diğer Projeler

| Proje | Deploy Komutu | Not |
|-------|---------------|-----|
| [[ops-bot]] | `cd ops-bot && ./deploy.sh` | Python systemd, tarball + VPS upload |
| ~~Anka~~ | `cd projects/anka && ./deploy.sh` | ~~Docker Compose deploy~~ *(Arşivlendi)* |
| [[mathlock-play]] | Backend: `pip install -r requirements.txt && sudo systemctl restart mathlock-backend mathlock-celery` | Android: `./gradlew bundleRelease` |
| [[infrastructure]] | `cd infrastructure && sudo ./setup.sh --ssl` | nginx, SSL yenileme |

---

## Haftalık Wiki Bakımı

Wiki'nin sağlıklı kalması için haftalık bakım script'i:

```bash
cd /home/akn/local
./scripts/wiki-weekly-maintenance.sh [--notify]
```

Yaptığı işlemler:
1. GitHub'dan en son wiki'yi çek (`git fetch + reset`)
2. Lint çalıştır (10/10 hedefi)
3. Log rotasyonu kontrolü (`log.md` >500 giriş uyarısı)
4. Rapor üret (`wiki/.weekly-report`)
5. `--notify` verildiyse Telegram'dan rapor gönder
6. Değişiklik varsa `git commit + push`

**Çalışma ortamı:** VPS (wiki, lint, telegram token hepsi VPS'te)

---

## Related Systems

- [[system-overview]] — VPS genel mimarisi
- [[infrastructure]] — nginx, SSL, Docker altyapısı
