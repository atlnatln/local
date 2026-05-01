---
title: "mathlock-play-readme"
created: 2026-05-01
updated: 2026-05-01
type: raw
tags: [raw]
related: []
---


# MathLock Play — Google Play Sürümü

Bu proje, MathLock uygulamasının Google Play Store'a uyumlu sürümüdür.

## Orijinal (mathlock) ile Farkları

| Özellik | mathlock (APK) | mathlock-play |
| --- | --- | --- |
| applicationId | com.akn.mathlock | com.akn.mathlock.play |
| Self-update (OTA) | VPS'ten APK | Kaldırıldı |
| REQUEST_INSTALL_PACKAGES | Var | Kaldırıldı |
| KILL_BACKGROUND_PROCESSES | Var | Kaldırıldı |
| HTTP trafik | 89.252.152.222 | Sadece HTTPS |
| Veri endpointleri | http://89.252.152.222 | https://mathlock.com.tr |
| isMonitoringTool beyanı | Yok | child_monitoring |
| Prominent Disclosure | Yok | DisclosureActivity |
| Privacy Policy web | Yok | website/ altında |
| isMinifyEnabled (release) | false | true (R8) |

## Ön Gereksinimler

### VPS Sunucu Kurulumu (Host-based Deployment)

> **29 Nisan 2026'dan itibaren** backend (Django + Celery) konteyner dışında, host üzerinde systemd servisi olarak çalışıyor.  
> Sebep: `kimi-cli` (AI üretim aracı) sadece host'ta kurulu ve konteyner içinden erişilemiyordu.  
> Detaylı bilgi: `docs/HOST_MIGRATION.md`

#### 1. Altyapı Servisleri (Docker)

Sadece PostgreSQL ve Redis konteynerda:

```bash
cd /home/akn/vps/projects/mathlock-play
docker-compose up -d   # mathlock_db + mathlock_redis
```

Portlar host'a açık: `5432` (PostgreSQL), `6379` (Redis).

#### 2. Python Virtual Environment (Host)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Systemd Servisleri (Host)

```bash
sudo cp docs/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mathlock-backend
sudo systemctl enable --now mathlock-celery
```

Servis detayları: `docs/systemd/mathlock-backend.service`, `docs/systemd/mathlock-celery.service`

#### 4. Nginx (Konteyner → Host Unix Socket)

Nginx `vps_nginx_main` konteyneri içinden backend'e **Unix socket** üzerinden erişir:
- Host socket: `/home/akn/vps/projects/mathlock-play/backend/run/gunicorn.sock`
- Container mount: `/var/run/mathlock/gunicorn.sock`
- `proxy_pass http://unix:/var/run/mathlock/gunicorn.sock:/api/mathlock/;`

#### 5. kimi-cli (AI Pipeline)

`kimi-cli` host'ta `uv tool` ile kurulu:
- Yol: `/home/akn/.local/share/uv/tools/kimi-cli/bin/kimi`
- PATH'e eklenmeli (systemd servislerinde tanımlı)
- Login durumu: `~/.kimi/credentials/` altında

#### 6. Domain ve SSL (mathlock.com.tr)

1. DNS propagasyonunun tamamlanmasını bekle
2. nginx config aktif: `infrastructure/nginx/conf.d/mathlock-play.conf`
3. SSL sertifikası: `/home/akn/vps/infrastructure/ssl/mathlock.com.tr/`
4. Web sitesi: `website/*.html` → `/var/www/mathlock/website/`

## Build

```bash
./gradlew assembleDebug    # Debug APK
./gradlew bundleRelease    # AAB (Play Store)
./gradlew assembleRelease  # Release APK (test)
```

## Play Store Yayın Checklist

- [ ] DNS propagasyonu tamamlandı
- [ ] SSL sertifikası alındı
- [ ] Privacy policy sayfası yayında
- [ ] Support sayfası yayında
- [ ] Play Console hesabı doğrulandı
- [ ] Release keystore oluşturuldu
- [ ] Internal test ile smoke test yapıldı
- [ ] Closed testing 12+ tester ile başlatıldı
- [ ] 14 gün continuous opt-in tamamlandı
- [ ] Production access başvurusu yapıldı
