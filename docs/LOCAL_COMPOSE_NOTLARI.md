# Local Docker Compose Notları (İki Proje)

Bu repo’nun yaklaşımı: her proje kendi dizinindeki Compose ile çalışır; bu repo sadece tek noktadan orkestrasyon yapar.

## Önerilen akış

- Tam stack (infrastructure + iki proje): `./dev-docker.sh`
- Sadece projeler (infrastructure olmadan): `bash scripts/up.sh`

## Çakışma kontrol listesi

- Host’a publish edilen portlar eşsiz olmalı.
  - Webimar (docker dev): `3000` (Next.js), `3001` (React), `8001` (API)
  - Anka (docker dev): `3100` (frontend), `8100` (backend)
  - Infrastructure: `80/443/8080` (reverse proxy + health)
- Compose içinde hard-coded `container_name:` kullanımı çakışma çıkarabilir.

## İpucu: Compose project name zorlamak

Nadir durumlarda “compose project name” çakışması yaşarsanız manuel çalıştırırken `-p` kullanabilirsiniz:

```bash
cd /home/akn/vps/projects/webimar
docker compose -p webimar up -d

cd /home/akn/vps/projects/anka
docker compose -p anka up -d
```

Repo içindeki `scripts/*` zaten dizin bazlı çalıştığı için çoğu zaman buna gerek kalmaz.
