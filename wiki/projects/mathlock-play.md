---
title: "MathLock Play"
created: 2026-05-01
updated: 2026-05-24
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
| `projects/mathlock-play/procedural_levels/` | Procedural seviye üretimi v2 — modüler paket (BFS solver, 13+ desen, 5 op, zorluk planlama) |
| `projects/mathlock-play/procedural-levels.py` | Procedural seviye üretimi (v1 — eski, devre dışı) |
| `projects/mathlock-play/procedural-levels-v2.py` | Procedural seviye üretimi (v2 — eski tek dosya, backup) |
| `projects/mathlock-play/experimental-web/` | React + Vite + Tailwind deneme oyun frontend'i |
| `projects/mathlock-play/scripts/validate-questions.py` | Dönem bazlı soru seti doğrulama aracı (tip/zorluk/duplicate/code) |
| `projects/mathlock-play/scripts/upload-play-store.py` | Google Play Store internal track'e AAB upload script'i |

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

> **Repo Durumu:** `projects/mathlock-play/` hem local monorepo'da tracked hem de `github.com/atlnatln/mathlock-play` adresinde ayrı repo olarak yönetiliyor. `.gitignore`'a alınmasına rağmen tracked dosyalar kalmıştır; iki repo arası senkronizasyona dikkat edilmelidir.

## Procedural Levels v2 (2026-05-24)

`procedural_levels/` paketi ile tamamen yeniden yazıldı. Eski `procedural-levels-v2.py` yerine `python3 -m procedural_levels` çalıştırılıyor.

| Bileşen | Görev |
|---------|-------|
| `core/types.py` | `Level`, `LevelSet`, `Wall`, `Command`, `Theme` veri modelleri |
| `core/rng.py` | Deterministik seed bazlı Rng |
| `solver/bfs.py` | State-space BFS — çözülebilirlik, min adım, çözüm yolu |
| `solver/connectivity.py` | UnionFind + flood-fill (bağlılık koruma) |
| `mechanics/operators.py` | `place_ops()` — çözüm yoluna bias'lı op yerleştirme |
| `mechanics/walls/` | 13+ desen (`none`, `single`, `barrier`, `scattered`, `maze`, `pattern`, `directional`) |
| `generator/pipeline.py` | `generate_level()`, `generate_set()` — yapısal üretim |
| `generator/difficulty.py` | `build_difficulty_plan()` — 12 seviyelik zorluk eğrisi |
| `generator/fingerprint.py` | Mekanik fingerprint + duplicate önleme |
| `generator/themes.py` | Tema seçimi + başlık/açıklama üretimi |
| `tests/` | 18 test (pytest) — pipeline + wall connectivity |

**Bilinen sınırlamalar:**
- Directional wall desenleri (`directional-single`, `directional-cross`) `registry.py`'de devre dışı (game.html desteği eklendi ancak açılmadı).
- `game.html` artık hem `[x,y]` hem `{"x":..., "y":..., "type":"directional", "blocks":[...]}` formatını destekliyor.

## Related Decisions

- [[adr-007-mathlock-meb-curriculum-compliance-implantation]] — MEB 2024 müfredat uyum implantasyonu

## Recent Commits

<!-- AUTO-REFRESHED -->
- `3a030f21` feat(mathlock-play): switchable backend AI↔Procedural, `/` `^` op support, enriched stats (2026-05-11)
- `9888d554` docs(wiki): ingest mathlock-play async generation + pending updates (2026-05-10)
- `e5ae1fc1` fix(mathlock-play): v1.0.78 — compile fix, test limit, Play Store upload script (2026-05-10) — v1.0.78
- `681346a3` fix(mathlock-play): 7 critical bug fixes, UI/UX improvements, new tests, v1.0.77 (2026-05-09) — v1.0.77
- `73d9abcb` fix(mathlock-play): revert parent auth to direct biometric prompt, add USE_BIOMETRIC permission (2026-05-09) — v1.0.76
- `5977e94b` feat(mathlock-play): auto-increment version in generate_age_questions.py, sync data to vps (2026-05-08)
