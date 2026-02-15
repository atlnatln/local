# Dev Docker Performans Runbook

Bu doküman `./dev-docker.sh` çalıştırmasının neden bazen uzun sürdüğünü ve nasıl hızlandırılacağını açıklar.

## Belirti

- `./dev-docker.sh` çağrısı özellikle ilk açılışta veya sık rebuild senaryolarında uzun sürer.
- Build aşamasında bekleme yaşanır, servisler geç ready olur.

## Kök Nedenler

1. **Her çalıştırmada zorunlu rebuild**
   - Eski akışta `docker compose up --build -d` koşulsuz çalışıyordu.
   - Bu, kod değişmese bile build süresini tekrar tetikliyordu.

2. **Büyük Docker build context**
   - Frontend tarafında `.dockerignore` yoktu.
   - `services/frontend/node_modules` gibi büyük klasörler context içine girerek build’i yavaşlatıyordu.

3. **Gereksiz dosyaların backend context’e girmesi**
   - `test_env/`, `db.sqlite3`, `artifacts/` gibi dosyalar exclude edilmediğinde context şişiyordu.

4. **Çoklu servis başlatma maliyeti**
   - `postgres`, `redis`, `minio`, `backend`, `frontend`, `celery_worker`, `celery_beat`, `nginx` birlikte kalkıyor.
   - İlk ayağa kalkışta image pull + healthcheck + migration doğal gecikme oluşturur.

## Uygulanan İyileştirmeler

- `dev-docker.sh` artık varsayılan olarak **hızlı mod** çalışır:
  - `docker compose up -d --remove-orphans`
- Zorunlu rebuild ihtiyacı için açık seçenek eklendi:
  - `./dev-docker.sh --build`
- Frontend için `.dockerignore` eklendi.
- Backend `.dockerignore` genişletildi (`test_env/`, `artifacts/`, `db.sqlite3`, vb.).

## Kullanım Önerisi

- Günlük geliştirme:
  - `./dev-docker.sh`
- Sadece dependency / Dockerfile değiştiyse:
  - `./dev-docker.sh --build`

## Hız Ölçümü (opsiyonel)

```bash
time ./dev-docker.sh
time ./dev-docker.sh --build
```

## Sorun Giderme

- Build cache temizliği gerekiyorsa:
  - `docker builder prune -f`
- Tüm stack’i sıfırlamak gerekiyorsa:
  - `docker compose down -v --remove-orphans`
  - `./dev-docker.sh --build`
