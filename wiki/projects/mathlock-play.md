---
title: "MathLock Play"
created: 2026-05-01
updated: 2026-05-02
type: project
tags: [mathlock-play, android, django, kotlin, systemd]
related:
  - infrastructure
  - deployment
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
| AI Pipeline | kimi-cli (`kimi-for-coding`) |
| Deploy | systemd servisleri (host-based) |
| Crash Reporting | Firebase Crashlytics 18.6.4 |

## AI Soru Döngüsü

```
Telefon ← VPS: questions.json, levels.json, topics.json
Çocuk 50 soru çözer → stats.json VPS'e yüklenir
VPS: AI (kimi-cli) yeni soru seti üretir → validate → DB
Telefon yeni seti indirir
```

## Entry Points

| Dosya/Dizin | Görev |
|-------------|-------|
| `projects/mathlock-play/app/src/main/...` | Android Kotlin kaynak kodu |
| `projects/mathlock-play/backend/` | Django backend |
| `projects/mathlock-play/website/` | Privacy policy, support sayfaları |
| `projects/mathlock-play/deploy.sh` | Build + data sync |
| `projects/mathlock-play/ai-generate.sh` | AI soru üretim pipeline'ı |

## Servisler (VPS)

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `mathlock-backend.service` | systemd | Django + Gunicorn (unix socket) |
| `mathlock-celery.service` | systemd | Celery worker |
| `mathlock_db` | Docker | PostgreSQL |
| `mathlock_redis` | Docker | Redis |

## Deploy

Backend host-based (systemd), DB/Redis Docker'da:
```bash
cd projects/mathlock-play/backend
pip install -r requirements.txt
sudo systemctl restart mathlock-backend mathlock-celery
```

## Dependencies

- [[infrastructure]] — nginx, SSL, mathlock.com.tr domain
- [[deployment]] — VPS deploy

## Crash Prevention (2026-05-02)

v1.0.67 sürümünde stabilite düzeltmeleri:
- **ProGuard:** Billing, Biometric, JS Bridge, MPAndroidChart için `keep` kuralları eklendi — release build R8 kırılmaları önlendi
- **WebView Memory Leak:** `SayiYolculuguActivity` ve `RobotopiaActivity`'de `onDestroy()`'da `webView.destroy()` + `removeAllViews()` eklendi
- **Handler Leak:** `pollForNewSet()` recursive polling'i activity-level `Handler`'a taşındı; `onDestroy()`'da `removeCallbacksAndMessages(null)` ile temizleniyor
- **BootReceiver:** Android 14 `ForegroundServiceStartNotAllowedException` riski `try/catch` ile kapatıldı
- **Firebase Crashlytics:** `com.google.firebase:firebase-crashlytics:18.6.4` + Google Services plugin 4.4.4 entegre edildi

## Recent Commits

- `11df330e` fix(mathlock): crash prevention + Firebase Crashlytics (2026-05-02)
- `9587a67a` chore(mathlock): bump version to 1.0.67 (67) (2026-05-02)
