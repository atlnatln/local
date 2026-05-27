---
title: "İşlem Kaydı"
type: log
tags: [meta, log]
---

> Önceki log: [[log-2026-H1]]

# İşlem Kaydı

> Append-only chronological log. Her giriş zaman damgalı ve değiştirilemez.
> Yeni girişler dosyanın SONUNA eklenir.
> Son 10 işlem: `grep "^## " wiki/log.md | tail -10`

---

## [2026-05-10 15:15] chain | log-2026-H1.md
- Önceki log arşivlendi: `log-2026-H1.md` (893 satır, 2025-05-01 — 2026-05-10)
- Yeni log zinciri başlatıldı

## [2026-05-10 15:27] lint | 4/10
- Orphan pages: 1 ([[log-2026-H1]])
- Broken links: 15
- Missing from index: 1
- Frontmatter errors: 1
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 3 (archive, maintenance, wiki)
- Raw existence: 0
- Log size: 1 entries

## [2026-05-10 15:29] lint | 6/10
- Orphan pages: 1 ([[log-2026-H1]])
- Broken links: 12
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 2 (maintenance, wiki)
- Raw existence: 0
- Log size: 2 entries

## [2026-05-10 15:31] lint | 7/10
- Orphan pages: 1 ([[log-2026-H1]])
- Broken links: 2
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 3 entries

## [2026-05-10 15:33] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 4 entries

## [2026-05-10 15:30] maintenance | Faz 1 hizli kazanmlar tamamlandi
- log.md zincirlendi: 893 satir → log-2026-H1.md (arsiv), yeni log.md baslatildi
- wiki/AGENTS.md sub-page: 343 → 204 satir. Cikarilan: [[wiki-growth-protocol]]
- .pending temizlendi (3 satir AGENTS.md marker)
- index.md guncellendi: log-2026-H1 + wiki-growth-protocol linkleri
- concepts-index.md guncellendi: wiki-growth-protocol eklendi
- Lint: 9/10 passed, 1 warning (page size), 0 failure

## [2026-05-10 15:36] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 6 entries

## [2026-05-10 15:35] maintenance | Faz 2 yapisal duzeltmeler tamamlandi
- Monorepo checkpoint ayrimi: local.sha → anka.sha + telegram-kimi.sha + sayi-yolculugu.sha
- references/WORKFLOW.md guncellendi: dosya-sayfa eslestirme tablosu + limit kontrolu (Adim 9.5)
- references/CONVENTIONS.md guncellendi: cross-link zorunlulugu (Bolum 2.1)
- Lint: 9/10 passed, 1 warning (page size), 0 failure

## [2026-05-10 15:49] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 8 entries

## [2026-05-10 15:58] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 9 entries

## [2026-05-10 16:24] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 1 (release)
- Raw existence: 0
- Log size: 10 entries

## [2026-05-10 15:45] sub-page | mathlock-play-android releases
- projects/mathlock-play-android.md: 348 → 82 satır
- Cikarilan: mathlock-play-android-releases.md (286 satır) — Crash Prevention, Bug Fix'ler, UI/UX, Testler, Sürüm Geçmişi
- Lint: 8/10 passed, 2 warning (page size + tag), 0 failure

## [2026-05-10 19:38] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 12 entries

## [2026-05-10 20:00] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 13 entries


## [2026-05-10 20:05] ingest | mathlock-play
- mathlock-play-backend.md: async AI generation launcher + poller mimarisi eklendi
- GenerationJob modeli, poll_generation_jobs beat task, generation_in_progress flag
- Celery Worker SIGTERM sorununa kalıcı çözüm (subprocess fire-and-forget)
- Android: SayiYolculuguActivity.kt generation_in_progress flag desteği
- 177 test, tümü OK

## [2026-05-11 01:22] ingest | sayi-yolculugu, mathlock-play
- sayi-yolculugu/index.html güncellendi: ~41 KB → ~48 KB
- Mobil optimizasyonlar: viewport max-scale, theme-color, touch highlight, overscroll-behavior
- Splash features ve goal bar eklendi
- mathlock-play/experimental-web/ eklendi: React + Vite + Tailwind deneme oyun frontend'i
- mathlock-play repo durumu güncellendi (local monorepo + ayrı repo dual tracked)
- Checkpoint'ler güncellendi, .pending temizlendi
## [2026-05-11 01:28] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 16 entries

## [2026-05-11 21:20] ingest | mathlock-play, sayi-yolculugu | 3a030f21
- mathlock-play: Switchable backend AI↔Procedural, `tasks.py` dispatcher, `_generate_level_set_procedural`, `GenerationJob.generator`, `LEVEL_GENERATOR` setting, enriched stats
- mathlock-play-android: WebView `game.html`'e `/` ve `^` operatör desteği, bölme bounce mantığı
- sayi-yolculugu: Standalone `index.html`'e `/` ve `^` operatör desteği, bölme bounce mantığı
- Pages updated: [[mathlock-play]], [[mathlock-play-backend]], [[mathlock-play-android]], [[sayi-yolculugu]]
- Index güncellendi, checkpoint'ler güncellenecek

## [2026-05-11 21:24] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 18 entries

## [2026-05-24 16:17] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 19 entries


## [2026-05-24 16:15] ingest | all | —
- Files: A:0 M:0 D:0
- Diff summary: No changes since last checkpoint across all tracked projects.
- Status: up-to-date
- Lint: 9/10 (1 page-size warning)
## [2026-05-24 18:20] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 21 entries


## [2026-05-24 19:30] refactor | mathlock-play procedural_questions v2
- `procedural_questions/` paketi oluşturuldu — 11 tip × 5 zorluk, 6 generator sınıfı
- `core/types.py`: genişletilmiş `Question` dataclass (options, explanation, topic_code, interaction_mode)
- `core/rng.py`: deterministik seed bazlı `Rng` (procedural_levels'den kopya)
- `core/config.py`: tüm dönem zorluk config'leri, ID offset'leri, tip oranları
- `core/curriculum.py`: MEB kazanım mapping (synthetic topic codes)
- `generators/`: `Arithmetic`, `Ordering`, `MissingNumber`, `Fraction`, `Pattern`, `Problem`
- `pipeline/`: `StatsAnalyzer`, `AdaptiveDistributor`, `QuestionSetBuilder`, `themes`
- `validators/math.py`: matematiksel doğrulama
- `tests/`: 192 pytest testi (155 generator + 12 pipeline + 25 integration)
- `backend/credits/tasks.py`: `python3 -m procedural_questions` + `PYTHONPATH`
- `deploy.sh`: `procedural_questions/` rsync eklendi
- Eski `procedural-questions-v2.py` → `.backup`
## [2026-05-24 19:30] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 6
- Unknown tags: 0
- Raw existence: 0
- Log size: 23 entries


## [2026-05-24 20:45] ingest | mathlock-play
- Crash Report Telegram sistemi deploy edildi (VPS)
- Yeni dosyalar: `reporting/telegram.py`, `queries.py`, `thresholds.py`, `formatters.py`, `crash_report_telegram.py`
- `.env.example`: `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` eklendi
- VPS crontab: günlük 06:00 + anlık her 5 dk
- `.venv` yeniden oluşturuldu (shebang bozulması nedeniyle)
- Test: daily + realtime bildirimleri Telegram'a ulaştı
- `models.py`: CrashReport modeli eklendi (önceki commit'te eksik kalmıştı)
## [2026-05-24 20:56] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 25 entries

## [2026-05-24 23:42] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 26 entries

## [2026-05-24 23:49] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 27 entries

## [2026-05-24 23:55] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 28 entries

## [2026-05-24 23:57] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 29 entries

## [2026-05-25 15:32] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 30 entries

## [2026-05-25 15:32] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 31 entries


## [2026-05-25 15:02] ingest | mathlock-play
- SayiYolculuguActivity.kt: kredi hatası (-1 gösterme) düzeltildi, v1.0.94 release
- mathlock-play.md: Google Play Store dağıtım süreci (upload scripts, ADB, dahili test) eklendi
- mathlock-play-android.md: Sayı Yolculuğu set bitiminde kredi hatası fix dökümantasyonu eklendi
- mathlock-play.sha: 6973b89 → 90f892e
- local.sha: 60c781e → 5e5ae3f
- Lint: 9/10 passing, 0 failure

## [2026-05-25 17:06] ingest | mathlock-play, sayi-yolculugu | f4cba014 | 4 pages
- Files: A:~20 M:~15 D:~15
- Pages updated: [[mathlock-play-android]], [[mathlock-play]], [[mathlock-play-backend]], [[sayi-yolculugu]]
- Diff summary: ErrorReporter (PII-filtered non-fatal reporting) added across all Android modules. ai-generate scripts and agents removed. MathQuestionGenerator deleted. sayi-yolculugu modularized. upload timeout fix.
## [2026-05-25 17:58] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 8
- Unknown tags: 0
- Raw existence: 0
- Log size: 34 entries

## [2026-05-25 22:07] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 9
- Unknown tags: 0
- Raw existence: 0
- Log size: 35 entries


## [2026-05-25 23:31] ingest | mathlock-play | 9ec5dc6 | 2 pages
- Files: A:1 M:8 D:0
- Pages updated: [[mathlock-play-backend]], [[mathlock-play]]
- Diff summary: Adaptive Difficulty v2 (sliding window recentDetails, byTypeDifficulty, per-topic tracking); Procedural Generator Updates (targetVal mandatory for diff≥2, sinif_1/2 2D-only override at diff 4, fingerprint startPos/targetPos, okul_oncesi plan change); Period Difficulty Bands in config.py/builder.py; test mock patches _generate_via_kimi → _generate_questions_procedural/generate_question_set/generate_level_set; IntegrityError fix; 169 tests passing.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout 40264bba -- wiki/
## [2026-05-26 00:02] lint | 8/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 9
- Unknown tags: 0
- Raw existence: 0
- Log size: 37 entries

## [2026-05-26 00:03] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 9
- Unknown tags: 0
- Raw existence: 0
- Log size: 38 entries


## [2026-05-25 23:35] adr-review | local | — | 8 pages
- ADR status review: 4 ADRs marked Superseded, 1 new ADR created
- Pages updated (Superseded): [[adr-003-robotopia-extraction]], [[adr-004-memory-game-integration]], [[adr-005-ops-bot-acp-sdk-migration]], [[adr-007-mathlock-meb-curriculum-compliance-implantation]]
- Pages created (Active): [[adr-008-remove-generationjob-poller]]
- Pages updated: [[decisions-index]], [[index]]
- Diff summary: ADR-003/004/005/007 closed as Superseded based on codebase verification. ADR-008 opened for GenerationJob cleanup after procedural migration.
## [2026-05-26 00:17] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 9
- Unknown tags: 2 (backend, technical-debt)
- Raw existence: 0
- Log size: 40 entries

## [2026-05-26 00:18] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 9
- Unknown tags: 2 (backend, technical-debt)
- Raw existence: 0
- Log size: 41 entries

## [2026-05-26 12:46] lint | 7/10
- Orphan pages: 0
- Broken links: 10
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 11
- Unknown tags: 10 (api, backend, beta, ci-cd, extension, hook, integration, mcp, plugin, technical-debt)
- Raw existence: 0
- Log size: 42 entries

## [2026-05-26 12:48] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 11
- Unknown tags: 10 (api, backend, beta, ci-cd, extension, hook, integration, mcp, plugin, technical-debt)
- Raw existence: 0
- Log size: 43 entries

## [2026-05-26 12:49] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 11
- Unknown tags: 10 (api, backend, beta, ci-cd, extension, hook, integration, mcp, plugin, technical-debt)
- Raw existence: 0
- Log size: 44 entries

## [2026-05-26 12:52] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 10 (api, backend, beta, ci-cd, extension, hook, integration, mcp, plugin, technical-debt)
- Raw existence: 0
- Log size: 45 entries

## [2026-05-26 12:55] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 13 (api, backend, beta, ci-cd, data, extension, finance, hook, integration, mcp...)
- Raw existence: 0
- Log size: 46 entries

## [2026-05-27 11:16] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 13 (api, backend, beta, ci-cd, data, extension, finance, hook, integration, mcp...)
- Raw existence: 0
- Log size: 47 entries

## [2026-05-27 16:41] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 13 (api, backend, beta, ci-cd, data, extension, finance, hook, integration, mcp...)
- Raw existence: 0
- Log size: 48 entries


## [2026-05-27 14:48] ingest | sayi-yolculugu + mathlock-play v1.0.100
- sayi-yolculugu: ses, tutorial, ipucu, path preview, undo/redo, achievements, daily set, haptic
- mathlock-play: v1.0.100 Android release, haptic event handler, IAP bridge, release notes
## [2026-05-27 16:48] lint | 7/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 13 (api, backend, beta, ci-cd, data, extension, finance, hook, integration, mcp...)
- Raw existence: 0
- Log size: 50 entries

## [2026-05-27 16:52] lint | 8/10
- Orphan pages: 0
- Broken links: 7
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 0
- Raw existence: 0
- Log size: 51 entries

## [2026-05-27 16:56] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 12
- Unknown tags: 0
- Raw existence: 0
- Log size: 52 entries

## [2026-05-27 16:57] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 53 entries

