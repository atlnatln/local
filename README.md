# VPS Monorepo (Kontrol Merkezi)

Bu repo, `projects/*` altındaki bağımsız projeleri ve ortak `infrastructure/` bileşenlerini tek yerden yönetmek için tasarlanmış bir “kontrol merkezi”dir.

## Hızlı Başlangıç (Önerilen: Docker)

Tüm sistemi (infrastructure + webimar + anka) tek komutla ayağa kaldırır:

```bash
cd /home/akn/vps
./dev-docker.sh
```

Sık kullanılan URL’ler (docker dev):

- Webimar Next.js: http://localhost:3000/
- Webimar React (hesaplamalar): http://localhost:3001/sera  (örnek)
- Webimar API: http://localhost:8001/api/
- Anka Frontend: http://localhost:3100/
- Anka Backend: http://localhost:8100/
- Infrastructure health: http://localhost:8080/nginx-health

## Alternatif: Sadece Proje Compose’ları (Infrastructure olmadan)

`projects/*` altındaki compose dosyalarını otomatik keşfeder ve ayağa kaldırır:

```bash
bash scripts/up.sh
```

Komutlar:

```bash
bash scripts/projects.sh
bash scripts/status.sh
bash scripts/logs.sh
bash scripts/down.sh
```

## Local (Docker’sız / Native) Geliştirme

Local modda iki projeyi aynı anda çalıştırmak port çakışmaları nedeniyle genelde mümkün değildir. Tek tek çalıştırın:

```bash
./dev-local.sh webimar
./dev-local.sh anka
```

## Yapı ve Konvansiyonlar

- Projeler: `projects/webimar/`, `projects/anka/`
- Compose keşfi: `scripts/config.sh` içindeki `COMPOSE_CANDIDATES` (varsayılan: `docker-compose.yml`, `compose.yml`, `docker-compose.dev.yml`).
- Infra ağı: `vps_infrastructure_network` (docker modunda `./dev-docker.sh` otomatik oluşturur).

Notlar/ipuçları: [docs/LOCAL_COMPOSE_NOTLARI.md](docs/LOCAL_COMPOSE_NOTLARI.md)
Durum notları: [docs/TAKIP.md](docs/TAKIP.md)
Çoklu proje/edge mimarisi: [docs/MULTI_WEB_PROJECT_SYSTEM.md](docs/MULTI_WEB_PROJECT_SYSTEM.md)
