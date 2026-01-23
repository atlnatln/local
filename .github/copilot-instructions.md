# AI coding agent instructions (vps monorepo)

## Repo "big picture"
- Bu repo bir **kontrol merkezi**: `projects/*` altındaki bağımsız projeleri ve ortak VPS altyapısını tek yerden yönetir.
- 3 ana katman:
  - `scripts/`: projeleri **otomatik keşfeder** ve Docker Compose ile toplu yönetir.
  - `projects/webimar/`: Tarım İmar (Django API + Next.js + React SPA).
  - `projects/anka/`: Anka Platform (Django + Next.js; Redis/Celery gibi bileşenler compose ile).
  - `infrastructure/`: ortak **nginx reverse proxy**, SSL ve ops/monitoring.

## Kritik workflow komutları
- Monorepo seviyesinde iki projeyi birlikte çalıştırma:
  - `bash scripts/projects.sh` (keşfedilen projeler)
  - `bash scripts/up.sh` | `bash scripts/down.sh` | `bash scripts/status.sh`
  - `bash scripts/logs.sh` (tümü) veya `bash scripts/logs.sh webimar`
- Infrastructure + iki projeyi docker’da tek komutla başlatma (önerilen):
  - `./dev-docker.sh`
- Native/local geliştirme (port çakışmaları nedeniyle tek tek):
  - `./dev-local.sh webimar`
  - `./dev-local.sh anka`
- Proje içi çalışma (komutlar proje dizininden çalıştırılmalı):
  - Webimar: `./dev-local.sh` (native) | `./dev-docker.sh` (docker) | `./deploy.sh` (prod)
  - Anka: `./deploy.sh` ve compose dosyaları (`docker-compose.yml`, `docker-compose.prod.yml`).

## Docker Compose / isimlendirme konvansiyonu
- `scripts/config.sh` `projects/*` altında şu dosya adlarını "compose" kabul eder: `docker-compose.yml`, `compose.yml`, `docker-compose.dev.yml`.
- Root scriptleri `docker compose -f <dosya>` çağırır (plugin). Altyapıda bazı scriptler `docker-compose` (binary) kullanır.

## Webimar (projects/webimar) mimari notları
- Servis sınırları:
  - `webimar-api/` = Django + DRF (API/hesaplamalar)
  - `webimar-nextjs/` = Next.js 15 (App Router)
  - `webimar-react/` = ayrı React SPA (hesaplayıcılar)
- Health endpoint’ler workflow’larda kullanılır:
  - API: `/api/calculations/health/`
    - native: `http://localhost:8000/api/calculations/health/`
    - docker (doğrudan port): `http://localhost:8001/api/calculations/health/`
    - docker (infra nginx üzerinden): `http://localhost/api/calculations/health/` (routing ayarlıysa)
- API versiyonlama / backwards-compat:
  - Legacy endpoint’ler `webimar-api/calculations/views/tesisler.py` içinde; yeni modüler endpoint’ler `webimar-api/calculations/tarimsal_yapilar/*/views.py` altında.
  - Örnek desen: legacy wrapper `calculate_bag_evi` (tesisler.py) → modül implementasyonu `_calculate_bag_evi_view_impl` (bag_evi/views.py). Yeni endpoint `calculate_bag_evi_view` aynı implementasyonu paylaşır.
    - Bu yaklaşım **double decorator/limit sayımı** gibi sorunları önlemek için kullanılıyor.
- Request tracking:
  - `webimar-api/accounts/request_tracking_middleware.py` `/api/*` isteklerini DB’ye yazar; hassas anahtarları redakte eder ve **asla request akışını bozmamalı** (hata yakalanıp loglanır).

## Env dosyaları ve deploy notları
- Webimar scriptleri `.env` dosyasını çoğu zaman **symlink** olarak yönetir:
  - local docker: `.env.local → .env`
  - local native: `.env.local.native → .env`
  - prod build: `.env.production` ve `webimar-nextjs/.env.production` beklenir; `deploy.sh` build sırasında geçici olarak `.env → .env.production` yapar.
- Prod reverse proxy konfigürasyonu `infrastructure/nginx/conf.d/` altında; Webimar deploy’u `infrastructure/nginx/conf.d/webimar.conf` dosyasını VPS’e kopyalayıp `vps_nginx_main` içinde `nginx -s reload` yapmayı dener.

## Test/Doğrulama (keşfedilebilir olan)
- Webimar Bağ Evi modülü testleri: `projects/webimar/webimar-api/calculations/tarimsal_yapilar/bag_evi/tests/`.
  - Not: `.../tests/run_tests.sh` bazı makinelere özgü hard-coded path içeriyor; genelde doğrudan `projects/webimar/webimar-api` içinde `pytest` çalıştırmak daha taşınabilir.
