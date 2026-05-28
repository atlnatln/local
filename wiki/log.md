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

## [2026-05-10 15:30] maintenance | Faz 1 hizli kazanmlar tamamlandi
- log.md zincirlendi: 893 satir → log-2026-H1.md (arsiv), yeni log.md baslatildi
- wiki/AGENTS.md sub-page: 343 → 204 satir. Cikarilan: [[wiki-growth-protocol]]
- .pending temizlendi (3 satir AGENTS.md marker)
- index.md guncellendi: log-2026-H1 + wiki-growth-protocol linkleri
- concepts-index.md guncellendi: wiki-growth-protocol eklendi
- Lint: 9/10 passed, 1 warning (page size), 0 failure

## [2026-05-10 15:35] maintenance | Faz 2 yapisal duzeltmeler tamamlandi
- Monorepo checkpoint ayrimi: local.sha → anka.sha + telegram-kimi.sha + sayi-yolculugu.sha
- references/WORKFLOW.md guncellendi: dosya-sayfa eslestirme tablosu + limit kontrolu (Adim 9.5)
- references/CONVENTIONS.md guncellendi: cross-link zorunlulugu (Bolum 2.1)
- Lint: 9/10 passed, 1 warning (page size), 0 failure

## [2026-05-10 15:45] sub-page | mathlock-play-android releases
- projects/mathlock-play-android.md: 348 → 82 satır
- Cikarilan: mathlock-play-android-releases.md (286 satır) — Crash Prevention, Bug Fix'ler, UI/UX, Testler, Sürüm Geçmişi
- Lint: 8/10 passed, 2 warning (page size + tag), 0 failure

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

## [2026-05-11 21:20] ingest | mathlock-play, sayi-yolculugu | 3a030f21
- mathlock-play: Switchable backend AI↔Procedural, `tasks.py` dispatcher, `_generate_level_set_procedural`, `GenerationJob.generator`, `LEVEL_GENERATOR` setting, enriched stats
- mathlock-play-android: WebView `game.html`'e `/` ve `^` operatör desteği, bölme bounce mantığı
- sayi-yolculugu: Standalone `index.html`'e `/` ve `^` operatör desteği, bölme bounce mantığı
- Pages updated: [[mathlock-play]], [[mathlock-play-backend]], [[mathlock-play-android]], [[sayi-yolculugu]]
- Index güncellendi, checkpoint'ler güncellenecek

## [2026-05-24 16:15] ingest | all | —
- Files: A:0 M:0 D:0
- Diff summary: No changes since last checkpoint across all tracked projects.
- Status: up-to-date
- Lint: 9/10 (1 page-size warning)

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

## [2026-05-24 20:45] ingest | mathlock-play
- Crash Report Telegram sistemi deploy edildi (VPS)
- Yeni dosyalar: `reporting/telegram.py`, `queries.py`, `thresholds.py`, `formatters.py`, `crash_report_telegram.py`
- `.env.example`: `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` eklendi
- VPS crontab: günlük 06:00 + anlık her 5 dk
- `.venv` yeniden oluşturuldu (shebang bozulması nedeniyle)
- Test: daily + realtime bildirimleri Telegram'a ulaştı
- `models.py`: CrashReport modeli eklendi (önceki commit'te eksik kalmıştı)

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

## [2026-05-25 23:31] ingest | mathlock-play | 9ec5dc6 | 2 pages
- Files: A:1 M:8 D:0
- Pages updated: [[mathlock-play-backend]], [[mathlock-play]]
- Diff summary: Adaptive Difficulty v2 (sliding window recentDetails, byTypeDifficulty, per-topic tracking); Procedural Generator Updates (targetVal mandatory for diff≥2, sinif_1/2 2D-only override at diff 4, fingerprint startPos/targetPos, okul_oncesi plan change); Period Difficulty Bands in config.py/builder.py; test mock patches _generate_via_kimi → _generate_questions_procedural/generate_question_set/generate_level_set; IntegrityError fix; 169 tests passing.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout 40264bba -- wiki/

## [2026-05-25 23:35] adr-review | local | — | 8 pages
- ADR status review: 4 ADRs marked Superseded, 1 new ADR created
- Pages updated (Superseded): [[adr-003-robotopia-extraction]], [[adr-004-memory-game-integration]], [[adr-005-ops-bot-acp-sdk-migration]], [[adr-007-mathlock-meb-curriculum-compliance-implantation]]
- Pages created (Active): [[adr-008-remove-generationjob-poller]]
- Pages updated: [[decisions-index]], [[index]]
- Diff summary: ADR-003/004/005/007 closed as Superseded based on codebase verification. ADR-008 opened for GenerationJob cleanup after procedural migration.

## [2026-05-27 14:48] ingest | sayi-yolculugu + mathlock-play v1.0.100
- sayi-yolculugu: ses, tutorial, ipucu, path preview, undo/redo, achievements, daily set, haptic
- mathlock-play: v1.0.100 Android release, haptic event handler, IAP bridge, release notes

## [2026-05-27 18:30] ingest | mathlock-play | a5e041c | [[mathlock-play]]
- Dosyalar: A:0 M:7 D:0
- Pages created: 
- Pages updated: [[mathlock-play]]
- Pages archived: 
- Diff özeti: v1.0.101 release build, Google Play internal track upload (versionCode 101), Sayı Yolculuğu game engine asset sync (game-audio.js, game-command-system.js, game-execution-engine.js, game-main.js), play-console.json ve upload-play-store.py release notes güncellendi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash

## [2026-05-27 19:00] ingest | sayi-yolculugu | 8cc818a3 | [[sayi-yolculugu]]
- Dosyalar: A:29 M:1 D:0
- Pages created: 
- Pages updated: [[sayi-yolculugu]]
- Pages archived: 
- Diff özeti: Oyun motoru tamamen yenilendi: 15+ JS modül (game-audio, game-command-system, game-execution-engine, game-main, game-store, game-i18n, game-level-manager, game-ui-overlays, game-utils, game-grid-renderer, editor.js, android-bridge.js), ses efektleri (audio/bgm.wav, click.wav, success.wav, bump.wav), editor.html, AGENTS.md, test raporları ve dokümantasyon.

## [2026-05-27 19:00] ingest | ops-bot | 50ec258 | [[ops-bot]]
- Dosyalar: A:3 M:10 D:0
- Pages created: 
- Pages updated: [[ops-bot]]
- Pages archived: 
- Diff özeti: sec-agent multi-site support: engaged_paths.json, engaged_sites.yaml, sync_engaged_paths.py; flags.py ve scorer.py robustness improvements; deploy.sh __pycache__ cleanup.

## [2026-05-27 19:00] ingest | webimar | 8e5b502 | [[webimar]]
- Dosyalar: A:1 M:2 D:0
- Pages created: 
- Pages updated: [[webimar]]
- Pages archived: 
- Diff özeti: Token abuse report management command eklendi (auto-revoke); analytics throttle ve IP anomaly detection middleware eklendi sonra revert edildi.

## [2026-05-27 19:00] ingest | local | 8cc818a3 | [[hooks]]
- Dosyalar: A:1 M:1 D:0
- Pages created: [[hooks]]
- Pages updated: 
- Pages archived: 
- Diff özeti: wiki/hooks.md yeni sayfa oluşumu; wiki_lint.py güncellendi.

## [2026-05-27 20:21] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 1
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 1 (archive)
- Raw existence: 0
- Log size: 20 entries

## [2026-05-27 20:22] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 21 entries

## [2026-05-27 20:23] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 22 entries

## [2026-05-27 20:23] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 23 entries

## [2026-05-27 20:25] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 24 entries


## [2026-05-28 21:50] ingest | mathlock-play, sayi-yolculugu
- sayi-yolculugu/js/game-execution-engine.js: JS motoru Python BFS ile senkronize edildi (lock persistence, switch persistence, switch timing, value boundary prune, targetVal fallback removal)
- mathlock-play/validate_1000_levels.py: parse_level switches desteği + re-validation eklendi
- mathlock-play/validate-levels.py: VALID_OP_TYPES `/` ve `^` eklendi
- mathlock-play v1.1.0 (versionCode 103) release build + Google Play internal track upload
- Log size: 25 entries
## [2026-05-28 21:53] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 26 entries

