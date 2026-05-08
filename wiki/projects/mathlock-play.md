---
title: "MathLock Play"
created: 2026-05-01
updated: 2026-05-07
type: project
tags: [mathlock-play, android, django, kotlin, python, systemd]
related:
  - infrastructure
  - deployment
  - sayi-yolculugu
  - mathlock-play-ai
  - mathlock-play-android
  - mathlock-play-backend
sources:
  - raw/articles/mathlock-play-readme.md
---

# [[MathLock-Play]]

Çocukların telefonundaki uygulamalara erişimini eğitici matematik soruları ve oyunlarla kontrol eden Android uygulaması + Django backend.

## Purpose

Ebeveynler çocuklarının telefon kullanımını kilitleyebilir; çocuklar matematik soruları çözerek veya sayı tahmin oyunu oynayarak uygulamaları açabilir. AI destekli adaptif öğrenme sistemi.

## Stack

| Katman | Teknoloji |
|--------|-----------|
| Android App | Kotlin, Material Design 3, Target SDK 35 |
| Kilit Mekanizması | UsageStatsManager + Foreground Service |
| Backend | Django + Django REST Framework |
| Database | PostgreSQL (Docker) |
| Cache/Queue | Redis (Docker) |
| AI Pipeline | [[kimi-code-cli|kimi-cli]] (`kimi-for-coding`) |
| Deploy | systemd servisleri (host-based) |
| Crash Reporting | Firebase Crashlytics 18.6.4 |

## Alt Sayfalar

| Sayfa | İçerik |
|-------|--------|
| [[mathlock-play-ai]] | AI soru üretim pipeline'ı, adaptif algoritma, MEB uyumu, batch sistemi |
| [[mathlock-play-android]] | Android oyunları, crash önleme, Android auth, Sayı Yolculuğu fix'leri |
| [[mathlock-play-backend]] | Django backend, API testleri, backend auth, child_id düzeltmeleri |
| [[meb-2024-curriculum-technical-alignment]] | MEB 2024 müfredat uyum analizi — kazanım haritası, render katmanı, ontoloji, adaptif zorluk, raporlama |

## Entry Points

| Dosya/Dizin | Görev |
|-------------|-------|
| `projects/mathlock-play/app/src/main/...` | Android Kotlin kaynak kodu (Robotopia hariç) |
| `projects/mathlock-play/backend/` | Django backend |
| `projects/mathlock-play/website/` | Privacy policy, support sayfaları |
| `projects/mathlock-play/deploy.sh` | Build + data sync |
| `projects/mathlock-play/ai-generate.sh` | AI soru üretim pipeline'ı |
| `projects/mathlock-play/ai-generate-levels.sh` | AI bulmaca seviye üretim pipeline'ı (Sayı Yolculuğu) |

## Environment Variables

`.env.example` yapısı (2026-05-06 güncellemesi):

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `DJANGO_SECRET_KEY` | ✅ | 50+ karakter rastgele string |
| `DJANGO_DEBUG` | ✅ | `False` (production) |
| `DJANGO_ALLOWED_HOSTS` | ✅ | `localhost,127.0.0.1,mathlock.com.tr` |
| `DB_NAME` | ✅ | PostgreSQL veritabanı adı (`mathlock`) |
| `DB_USER` | ✅ | PostgreSQL kullanıcı adı |
| `DB_PASSWORD` | ✅ | PostgreSQL şifresi |
| `DB_HOST` | ✅ | `localhost` |
| `DB_PORT` | ✅ | `5432` |
| `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | ❌ | IAP doğrulama için JSON dosya yolu |
| `CELERY_BROKER_URL` | ❌ | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | ❌ | `redis://localhost:6379/0` |

> **Not:** Eski tek `MATHLOCK_DB_PASSWORD` değişkeni ayrı `DB_*` değişkenlerine bölündü. `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` path'i `/home/akn/secrets/mathlock-play/...` olarak güncellendi.

## Servisler (VPS)

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `mathlock-backend.service` | systemd | Django + Gunicorn (unix socket) |
| `mathlock-celery.service` | systemd | Celery worker |
| `mathlock_db` | Docker | PostgreSQL |
| `mathlock_redis` | Docker | Redis |

## Deploy

Backend host-based (systemd), DB/Redis Docker'da.

Deploy script'i **ortam tespiti** yapar (`is_vps` — `/home/akn/vps` dizini varsa VPS'tedir):
- **Local'den:** `ssh`/`rsync` ile VPS'ye gönderir, Android derleme + ADB kurulumu yapar
- **VPS'ten:** Doğrudan `cp` ile yerel dizinlere yazar; Android derleme ve ADB adımları atlanır

```bash
cd projects/mathlock-play
./deploy.sh [debug|release] [--skip-adb] [--deploy-backend] [--skip-backend]
```

| Adım | Local | VPS |
|------|-------|-----|
| Android derleme (AAB/APK) | ✅ Gradle çalıştırır | ⏭️ Atlanır (SDK yok) |
| ADB kurulum | ✅ Telefona yükler | ⏭️ Atlanır (USB yok) |
| Backend sync | `rsync` ile uzak sunucuya | `cp` ile yerel hedefe |
| Systemd restart | `ssh` ile uzaktan | Doğrudan `systemctl` |

## Dependencies

- [[infrastructure]] — nginx, SSL, mathlock.com.tr domain
- [[deployment]] — VPS deploy

## Related Decisions

- [[adr-007-mathlock-meb-curriculum-compliance-implantation]] — MEB 2024 müfredat uyum implantasyonu

## Recent Commits

<!-- AUTO-REFRESHED -->
- `90d86baf` fix(mathlock-play): MEB uyum düzeltmeleri — curriculum JSON, generate script, agents.md (2026-05-07)
- `582ff046` fix(agents): MEB müfredat uyumu + tip isimlendirme standardizasyonu (2026-05-07)
- `fa6174fc` feat(mathlock): age-appropriate questions, parent auth, settings UI, memory game fixes (2026-05-06)
- `3dc2e3db` chore(wiki): lint fixes, add page size policy, update archived handling (2026-05-06)
- `78015644` fix(deploy): increase celery wait time from 3s to 5s (2026-05-06)
