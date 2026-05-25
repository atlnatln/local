---
title: "MathLock Play"
created: 2026-05-01
updated: 2026-05-25
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
| Crash Reporting (ACRA) | Firebase Crashlytics 18.6.4 |
| Crash Report Telegram | Django mgmt command + VPS crontab |

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
| `projects/mathlock-play/ai-generate.sh` | ~~AI soru üretim pipeline'ı~~ [STALE — silindi, procedural_questions/ kullanılıyor] |
| `projects/mathlock-play/ai-generate-levels.sh` | ~~AI bulmaca seviye üretim pipeline'ı~~ [STALE — silindi, procedural_levels/ kullanılıyor] |
| `projects/mathlock-play/procedural_levels/` | Procedural seviye üretimi v2 — modüler paket (BFS solver, 13+ desen, 5 op, zorluk planlama) |
| `projects/mathlock-play/procedural-levels.py` | Procedural seviye üretimi (v1 — eski, devre dışı) |
| `projects/mathlock-play/procedural-levels-v2.py` | Procedural seviye üretimi (v2 — eski tek dosya, backup) |
| `projects/mathlock-play/experimental-web/` | React + Vite + Tailwind deneme oyun frontend'i |
| `projects/mathlock-play/procedural_questions/` | Procedural soru üretimi v2 — modüler paket (11 tip, 5 zorluk, deterministik RNG, adaptif dağıtım) |
| `projects/mathlock-play/scripts/validate-questions.py` | Dönem bazlı soru seti doğrulama aracı (tip/zorluk/duplicate/code) |
| `projects/mathlock-play/scripts/upload-play-store.py` | Google Play Store internal track'e AAB upload script'i (draft) |
| `projects/mathlock-play/scripts/upload-to-play-store.py` | Google Play Store internal track'e AAB/APK upload script'i (completed) |

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
| `TELEGRAM_BOT_TOKEN` | ❌ | Crash Report Telegram bildirimleri |
| `TELEGRAM_CHAT_ID` | ❌ | Crash Report Telegram bildirimleri |

> **Not:** Eski tek `MATHLOCK_DB_PASSWORD` değişkeni ayrı `DB_*` değişkenlerine bölündü. `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` path'i `/home/akn/secrets/mathlock-play/...` olarak güncellendi. Telegram değişkenleri ops-bot `.env` ile aynı değerleri kullanır.

## Servisler (VPS)

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `mathlock-backend.service` | systemd | Django + Gunicorn (unix socket) |
| `mathlock-celery.service` | systemd | Celery worker |
| `mathlock_db` | Docker | PostgreSQL |
| `mathlock_redis` | Docker | Redis |
| `crash-report-daily` | crontab | Günlük özet (06:00) |
| `crash-report-realtime` | crontab | Anlık kontrol (her 5 dk) |

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

## Google Play Store Dağıtımı

MathLock Play Google Play Store üzerinden dağıtılır. OTA yok — tüm güncellemeler Play Store kanalıyla yapılır.

### Gereksinimler

- Google Cloud Service Account (JSON key)
- Play Console'da servis hesabına **Release Manager** veya **Admin** rolü
- Keystore: `projects/mathlock-play/keystore.jks` (release imzası)

### Adım Adım Süreç

**1. Release AAB Derleme**
```bash
cd projects/mathlock-play
./deploy.sh --release
# Çıktı: app/build/outputs/bundle/release/app-release.aab
```

**2. Play Store'a Upload (Script ile)**

```bash
# Draft olarak yükle (manuel yayınlama gerektirir)
python3 scripts/upload-play-store.py \
  app/build/outputs/bundle/release/app-release.aab

# Veya doğrudan "completed" olarak yükle (dahili teste anında düşer)
python3 scripts/upload-to-play-store.py \
  --aab app/build/outputs/bundle/release/app-release.aab \
  --service-account /home/akn/secrets/mathlock-play/google-service-account.json \
  --status completed \
  --release-name "Sürüm notu"
```

| Script | Varsayılan Status | Kullanım |
|--------|-------------------|----------|
| `upload-play-store.py` | `draft` | Manuel review gerektirir, Console'dan "Yayınla" yapılması gerekir |
| `upload-to-play-store.py` | `completed` | Dahili teste otomatik düşer, telefon hemen güncelleyebilir |

**3. Dahili Test Kullanıcısı Olarak İndirme**
- Google Play Store uygulamasını aç
- MathLock Play sayfasına git
- "Güncelle" butonu görünür (internal track `completed` release'leri için)
- Veya: Profil → Uygulamalar ve cihazlar → Güncellemeleri yönet

### Script Parametreleri (`upload-to-play-store.py`)

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `--aab` | — | AAB dosya yolu |
| `--apk` | — | APK dosya yolu (alternatif) |
| `--track` | `internal` | `internal`, `alpha`, `beta`, `production` |
| `--status` | `completed` | `draft`, `inProgress`, `halted`, `completed` |
| `--release-name` | `""` | Sürüm notu (tr-TR dilinde gösterilir) |
| `--service-account` | `backend/google-service-account.json` | Servis hesabı JSON key |

### ADB ile Direkt Kurulum (Debug/Test)

Release AAB aynı keystore ile imzalandığı için `bundletool` ile APK üretilip ADB ile kurulabilir. Ancak debug APK (`app-debug.apk`) farklı imza kullanır — Play Store imzasıyla uyumlu değildir, üzerine yazamaz.

```bash
# Debug APK (farklı imza — Play Store sürümünün üzerine yazamaz)
./deploy.sh --adb

# Release AAB → APK dönüşümü (bundletool gerekli)
bundletool build-apks --bundle=app-release.aab --output=app-release.apks --ks=keystore.jks
bundletool install-apks --apks=app-release.apks
```

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

## Procedural Questions v2 (2026-05-24)

`procedural_questions/` paketi ile `procedural-questions-v2.py` monolitik dosyası modüler yapıya taşındı. Backend `tasks.py` artık `python3 -m procedural_questions` çalıştırıyor.

| Bileşen | Görev |
|---------|-------|
| `core/types.py` | `Question`, `QuestionSet`, `QuestionType`, `DifficultyConfig`, `PeriodConfig` veri modelleri |
| `core/rng.py` | Deterministik seed bazlı `Rng` (procedural_levels'den kopya) |
| `core/config.py` | Tüm dönem (okul_oncesi … sinif_4) zorluk config'leri, ID offset'leri, tip oranları |
| `core/curriculum.py` | MEB kazanım mapping (synthetic topic codes) |
| `generators/` | 6 generator sınıfı: `Arithmetic`, `Ordering`, `MissingNumber`, `Fraction`, `Pattern`, `Problem` |
| `generators/registry.py` | `get_generator()` / `allowed_types()` — tip → sınıf haritası |
| `pipeline/analyzer.py` | `StatsAnalyzer` — performans kategorisi (USTA…KRITIK) + zorluk ayarı |
| `pipeline/distributor.py` | `AdaptiveDistributor` — A/B/C grup dağılımı |
| `pipeline/builder.py` | `QuestionSetBuilder` — psikolojik sıralama + dedup + ID atama |
| `pipeline/themes.py` | Hint ve topic (konu anlatımı) üretimi |
| `validators/math.py` | Matematiksel doğrulama (toplama, çıkarma, çarpma, bölme, sıralama, kesir, eksik_sayı) |
| `tests/` | 192 test (pytest) — generator (155), pipeline (12), integration (25) |

**Backend entegrasyonu:**
- `backend/credits/tasks.py`: `sys.executable -m procedural_questions` + `PYTHONPATH`
- `deploy.sh`: `procedural_questions/` rsync eklendi
- Eski `procedural-questions-v2.py` → `procedural-questions-v2.py.backup`

## Related Decisions

- [[adr-007-mathlock-meb-curriculum-compliance-implantation]] — MEB 2024 müfredat uyum implantasyonu

## Android ErrorReporter (2026-05-25)

Non-fatal business hataların merkezi raporlanması. PII filtreleme ile Firebase Crashlytics'e gönderilir. Bkz. [[mathlock-play-android]] ErrorReporter bölümü.

## Crash Report Telegram Notifications (2026-05-24)

ACRA çökme raporlarını Telegram üzerinden günlük özet + anlık kritik bildirim olarak gönderen sistem.

| Bileşen | Dosya | Görev |
|---------|-------|-------|
| `reporting/telegram.py` | `backend/credits/reporting/telegram.py` | Telegram `sendMessage` helper (4096 karakter limit, truncate) |
| `reporting/queries.py` | `backend/credits/reporting/queries.py` | ORM sorguları — daily summary, realtime candidates, type stats |
| `reporting/thresholds.py` | `backend/credits/reporting/thresholds.py` | Anlık bildirim kuralları (kritik sınıf, spike, yeni tip) |
| `reporting/formatters.py` | `backend/credits/reporting/formatters.py` | Günlük ve anlık rapor metin formatlayıcı |
| Management Command | `backend/credits/management/commands/crash_report_telegram.py` | Entry point — `--mode daily|realtime`, `--dry-run`, `--hours`, `--minutes` |

**Threshold kuralları:**
- `java.lang.NullPointerException`, `OutOfMemoryError`, `SQLiteException` → her zaman bildir
- Aynı crash tipi saatte ≥5 kez → spike bildirimi
- İlk kez görülen crash tipi → yeni tip bildirimi
- `is_resolved=True` olanlar atlanır

**VPS crontab:**
```bash
0 6 * * *   cd /home/akn/vps/projects/mathlock-play/backend && .venv/bin/python manage.py crash_report_telegram --mode daily
*/5 * * * * cd /home/akn/vps/projects/mathlock-play/backend && .venv/bin/python manage.py crash_report_telegram --mode realtime
```

## Recent Commits

<!-- AUTO-REFRESHED -->
- `f4cba014` feat(mathlock-play): ErrorReporter (PII-filtered non-fatal reporting), ACRA LOGCAT removal, v1.0.97 (2026-05-25) — v1.0.97
- `90f892e` fix(mathlock-play): SayiYolculugu kredi hatasi (-1 gosterme), versiyon 1.0.94 (2026-05-25) — v1.0.94
- `6973b89` feat(backend): crash report telegram daily & realtime notifications (2026-05-24)
- `3a030f21` feat(mathlock-play): switchable backend AI↔Procedural, `/` `^` op support, enriched stats (2026-05-11)
- `9888d554` docs(wiki): ingest mathlock-play async generation + pending updates (2026-05-10)
- `e5ae1fc1` fix(mathlock-play): v1.0.78 — compile fix, test limit, Play Store upload script (2026-05-10) — v1.0.78
- `681346a3` fix(mathlock-play): 7 critical bug fixes, UI/UX improvements, new tests, v1.0.77 (2026-05-09) — v1.0.77
- `73d9abcb` fix(mathlock-play): revert parent auth to direct biometric prompt, add USE_BIOMETRIC permission (2026-05-09) — v1.0.76
- `5977e94b` feat(mathlock-play): auto-increment version in generate_age_questions.py, sync data to vps (2026-05-08)
