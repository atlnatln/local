---
title: "İşlem Kaydı"
type: log
tags: [meta, log]
---

# İşlem Kaydı

> Append-only chronological log. Her giriş zaman damgalı ve değiştirilemez.
> Yeni girişler dosyanın SONUNA eklenir.
> Son 10 işlem: `grep "^## " wiki/log.md | tail -10`

---

## [2025-05-01 00:00] init | local-wiki | bootstrap | wiki-olusturuldu
- Wiki dizini oluşturuldu
- Skill: local-wiki
- Checkpoint dosyaları hazırlandı
- Bir sonraki adım: `/wiki ingest ops-bot` ile ilk pilot ingest'i çalıştır

## [2025-05-01 19:25] ingest | ops-bot | ab28161 | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: [[ops-bot]]
- Pages updated: —
- Pages archived: —
- Diff summary: Full ingest of ops-bot project. Created project page with stack, agent system, services, deploy flow, and sec-agent architecture.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
## [2026-05-01 19:30] ingest | webimar | 2eb3dfa | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: [[webimar]]
- Diff summary: Full ingest of webimar project. Agriculture calculation platform with Django + Next.js + React.

## [2026-05-01 19:31] ingest | anka | 4db9944 | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: Anka (arşiv sayfası)
- Diff summary: Full ingest of anka project. B2B data service with 3-stage verification pipeline.

## [2026-05-01 19:32] ingest | mathlock-play | 4db9944 | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: [[mathlock-play]]
- Diff summary: Full ingest of mathlock-play project. Android math game with AI-powered question generation.

## [2026-05-01 19:33] ingest | infrastructure | 4db9944 | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: [[infrastructure]]
- Diff summary: Full ingest of infrastructure. Shared VPS reverse proxy, SSL, and Docker network.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
## [2026-05-01 21:57] ingest | local | f33ae5a9 | 4
- Files: A:1 M:3 D:0
- Pages created: [[proactive-wiki]]
- Pages updated: [[README]], [[index]], [[log]]
- Diff summary: Proaktif Wiki Yöneticisi (Auto-Prompt) implementasyonu — git post-commit hooks, marker file (wiki/.pending), AGENTS.md proactive check, skip-session flag
- Components: scripts/wiki-post-commit.sh, 3 repo hooks (local, ops-bot, webimar)
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash


## [2026-05-01 21:58] ingest | local | f33ae5a | 1 sayfa
- Files: A:2 M:1 D:0
- Pages created: 
- Pages updated: [[proactive-wiki]]
- Pages archived: 
- Diff summary: AGENTS.md ve wiki-post-commit.sh raw arşivine eklendi. proactive-wiki sources alanı güncellendi. .gitignore'da wiki/.pending eklendi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout 4db9944234eda3c61604b1ccb595388adf5aa59a -- wiki/
## [2026-05-01 22:06] ingest | telegram-kimi | first-ingest | telegram-kimi-wiki-olusturuldu

- Project: telegram-kimi
- Type: first-ingest
- Pages created: [[telegram-kimi]]
- Raw sources: raw/articles/telegram-kimi-readme.md, raw/articles/telegram-kimi-plan.md
- Checkpoint: local (monorepo, e8ddf291)
## [2026-05-01 22:08] ingest | sayi-yolculugu | first-ingest | sayi-yolculugu-wiki-olusturuldu

- Project: sayi-yolculugu
- Type: first-ingest
- Pages created: [[sayi-yolculugu]]
- Raw sources: raw/articles/sayi-yolculugu-index.html
- Checkpoint: local (monorepo, e8ddf291)
## [2026-05-01 22:12] cleanup | konsept-silme | placeholder-temizligi | eksik-sayfalar-kaldirildi

- Removed from index: [[django-nextjs-pattern]], [[ssl-certbot]], [[multi-web-project-system]]
- Removed related references: infrastructure.md, ops-bot.md, webimar.md, deployment.md
- Updated: projects/index.md (stale data corrected)
- Reason: Content already covered by infrastructure.md and project pages; YAGNI
## [2026-05-01 22:15] concept | monitoring | yeni-konsept | monitoring-wiki-olusturuldu

- Concept: [[monitoring]]
- Type: new-concept
- Coverage: Prometheus, nginx health check, sec-agent metrics, systemd timers, alert kanalları
- Sources: raw/articles/infrastructure-docker-compose.md
## [2026-05-01 22:20] concept | infrastructure-detaylari | yeni-konseptler | nginx-ssl-log-olusturuldu

- Concepts created: [[nginx-routing]], [[ssl-automation]], [[log-management]]
- Updated: [[monitoring]] (Grafana + Loki eklendi)
- Updated: [[infrastructure]] (cross-link'ler eklendi)
- Updated: [[index.md]] (yeni konseptler listeye eklendi)
- Sources: infrastructure/nginx/conf.d/, infrastructure/renew-ssl.sh, infrastructure/ssl-cron-setup.sh, infrastructure/docker-compose.yml
## [2026-05-01 22:25] restructure | index-organizasyon | genelden-ozele | index-yeniden-siralandi

- index.md yeniden organize edildi: System → Infrastructure & Platform → Concepts → Decisions → Projects
- infrastructure Projects listesinden cikarildi, Infrastructure & Platform bolumune kondu
- README.md'ye "Wiki Organizasyon Kurallari" eklendi (genelden ozele siralama, sayfa tipleri, checklist)
- Updated: README.md, index.md
## [2026-05-01 22:30] docs | agents-md | guncelleme | AGENTS.md-yenilendi

- AGENTS.md footer guncellendi: 5 proje -> 7 proje, mathlock -> mathlock-play
- Servisler tablosuna sec-agent eklendi
- Wiki Kullanimi bolumu kisaltilip wiki/README.md'ye yonlendirildi
- Reason: Eski bilgiler yanilticiydi, wiki ile bilgi ciftlenmesi azaltiliyor

## [2026-05-01 22:35] docs | agents-md | minimalize | proje-yapisi-kisaltildi

- AGENTS.md proje yapisi agaci kisaltildi (292 -> 258 satir)
- Detaylar wiki/system-overview.md ve wiki/projects/'e yonlendirildi
- Bilgi ciftlenmesi azaltiliyor, kontrol korunuyor
## [2026-05-01 23:00] infra | hooks | kurulum | kimi-cli-hooks-aktif

- Hooks configured in ~/.kimi/config.toml:
  1. PreToolUse (WriteFile|StrReplaceFile) → protect-env.sh — blocks .env edits
  2. PostToolUse (WriteFile|StrReplaceFile) → wiki-auto-pending.sh — adds marker on file change
  3. Stop → wiki-lint-on-stop.sh — runs wiki lint on session end
- Scripts: /home/akn/local/scripts/hooks/

## [2026-05-01 23:05] infra | flow-skill | kurulum | wiki-ingest-flow-olusturuldu

- Flow skill: wiki-ingest
- Location: ~/.kimi/skills/wiki-ingest/SKILL.md
- Type: flow (mermaid diagram)
- Steps: git diff analysis -> page update -> cross-link refresh -> lint -> checkpoint update
- Usage: /flow:wiki-ingest

## [2026-05-01 23:10] infra | skill-scope | project-level | local-wiki-tasindi

- local-wiki skill moved from user-level to project-level
- User-level: ~/.kimi/skills/local-wiki/ (fallback)
- Project-level: /home/akn/local/.kimi/skills/local-wiki/ (primary)
- Scope note added to project-level SKILL.md
- Priority: Project > User (kimi-cli resolves project-level first when in /home/akn/local)
## [2026-05-02 01:01] ingest | all | n/a | 0 sayfa
- Files: A:0 M:0 D:0
- Pages created: (none)
- Pages updated: (none)
- Pages archived: (none)
- Diff özeti: Checkpoint'ler zaten güncel (ops-bot: ab281619, webimar: 2eb3dfa2). `.pending` marker'ı temizlendi. Gerçek bir değişiklik tespit edilmedi.
- Lint: 10/10 passing

## [2026-05-02 02:48] ingest | local + webimar + mathlock-play | 3 projects
- **webimar** (`2eb3dfa` → `416474ac`): Security hardening — settings.py defaults tightened, CORS http origins removed, DEFAULT_PERMISSION_CLASSES flipped to IsAuthenticated, .env files cleaned from git
- **mathlock-play** (new commits): Crash prevention — ProGuard rules, WebView memory leak fixes, Handler polling leak fix, BootReceiver try/catch, Firebase Crashlytics 18.6.4 integration
- **local** (monorepo): Plan files for webimar security rollout and mathlock crash fix
- Pages updated: [[webimar]], [[mathlock-play]]
- Pages created: —
- Checkpoints refreshed: local, webimar
## [2026-05-02 03:30] decision | adr-001 | infrastructure
- Type: new-adr
- Page: [[adr-001-monorepo-hybrid-structure]]
- Status: Active
- Scope: infrastructure, git-workflow
- Summary: Monorepo + ayrı repo karışık yapısı kararı. Büyük projeler (ops-bot, webimar) ayrı repo; küçük projeler ve altyapı tek monorepo altında.
## [2026-05-02 12:09] ingest | local | e2a6cc7 | 26
- Files: A:9 M:16 D:0 (wiki docs + telegram-kimi code)
- Pages created: [[sayi-yolculugu]], [[telegram-kimi]], [[git-workflow]], [[log-management]], [[monitoring]], [[nginx-routing]], [[ssl-automation]]
- Pages updated: [[index]], [[system-overview]], [[infrastructure]], [[mathlock-play]], [[ops-bot]], [[webimar]], [[proactive-wiki]], [[deployment]], [[README]], [[SCHEMA]]
- Pages archived: —
- Diff summary: Incremental ingest. telegram-kimi bot.py and PLAN.md updated (local/ssh-tt mode, photo support). Wiki concepts and project pages synced from monorepo.
- Lint: 10/10 passing
## [2026-05-02 19:31] update | ops-bot | vps-deploy-dizini | runtime
- Sayfa: [[ops-bot]]
- Değişiklik: VPS Dizin Yapısı ve Troubleshooting bölümleri eklendi
- Sebep: `/home/akn/local/ops-bot/` silinmişti, systemd servisi `Result: resources` ile başlayamıyordu
- Çözüm: Eski `local/ops-bot/data/` dosyaları `vps/ops-bot/data/` altına kopyalandı; `/home/akn/local/ops-bot` symlink olarak `/home/akn/vps/ops-bot`'a bağlandı
- Servis: `ops-bot.service` `active (running)` — Telegram token doğrulandı, Application started
- Kaynak: `systemd/ops-bot.service` incelemesi + VPS shell komutları + deploy script davranışı
## [2026-05-02 19:35] create | sec-agent | yeni-proje-sayfasi
- Sayfa: [[sec-agent]] oluşturuldu
- Sayfa: [[ops-bot]] güncellendi (Security bölümü kısaltıldı, sec-agent wikilink eklendi)
- Sayfa: [[index]] güncellendi (sec-agent Projects tablosuna eklendi)
- İçerik: Pipeline mimarisi, VPS dizin yapısı (deploy vs /opt), components, guardrails, systemd servisleri, resource limits, operations, troubleshooting
- Kaynak: VPS `/opt/sec-agent/` incelemesi, yerel `ops-bot/sec-agent/` yapısı, `move-sec-agent-to-opt.sh`, systemd unit dosyaları
## [2026-05-02 19:45] update | sec-agent | normal-kullanici-false-positive
- Sayfa: [[sec-agent]] güncellendi
- Değişiklik: Configuration tablosuna scoring ve thresholds satırları eklendi; Troubleshooting bölümüne "Normal kullanıcı yüksek skorla engellendi" case'i eklendi
- Runtime düzeltmeleri:
  - `config/scoring.yaml`: high_volume_threshold 500→5000, high_volume 2→0.5
  - `config/agent.yaml`: decay.points_per_hour 10.0→50.0
  - `config/thresholds.yaml`: persistence_score_threshold 500→2000
  - `config/ignore.yaml`: 188.132.132.225/32 eklendi
  - UFW + iptables'dan 188.132.132.225 kaldırıldı
- Sebep: 62,398 event atanmış normal kullanıcı, tüm flag'ler false iken skor 9750+ olmuştu. scorer.py high_volume mantığı event sayısına bakıyordu, flag'e değil.
- Kaynak: VPS `/opt/sec-agent/` incelemesi, events.jsonl analizi, engine/scorer.py kod incelemesi
## [2026-05-02 19:50] update | sec-agent | whitelist-yaklasimi-kaldirildi
- Sayfa: [[sec-agent]] güncellendi
- Değişiklik: Troubleshooting bölümünde "Bloklanmaması gereken IP engellendi" case'i yeniden yazıldı
- Prensip eklendi: "Yanlış block'lar whitelist'e çözüm değildir. Root cause sistem ayarlarındadır."
- Normal kullanıcı case'inde "Whitelist'e ekle" adımı kaldırıldı; yerine "Aktif block'u kaldır + config düzelt" önerisi kondu
- Runtime: `config/ignore.yaml`'dan 188.132.132.225/32 kaldırıldı (VPS + yerel repo)
- Kaynak: Kullanıcı geri bildirimi — IP bazlı workaround yerine sistematik düzeltme prensibi
## [2026-05-02 19:55] update | adr-002 | host-duzeyi-kimi-cli
- Sayfa: [[adr-002-sec-agent-daily-report-agent-router]] güncellendi
- Değişiklik: Yürütme modeline "kimi-cli host düzeyinde çalışır" kısıtlaması eklendi
- Consequences/Riskler bölümlerine host düzeyinde çalışmanın etkileri eklendi
- VPS doğrulaması: `/home/akn/.local/bin/kimi` ve `/home/akn/.local/bin/kimi-cli` symlink'leri mevcut
- Kaynak: Kullanıcı geri bildirimi — kimi-cli'nin container/izole ortam yerine host düzeyinde çalışması zorunluluğu
## [2026-05-02 20:40] update | sec-agent | scorer-guard-dinamik-ip-prensipleri
- Sayfa: [[sec-agent]] güncellendi
- Değişiklikler:
  - Yeni "Kritik Prensipler" bölümü eklendi: dinamik IP realitesi, coğrafi konum ≠ güven, behavior > volume > coğrafya
  - Configuration tablosu güncellendi: decay 100, high_volume 0, max_ip_score 5000
  - Engine tablosu güncellendi: scorer.py explicit guard (`added == 0.0` ise skor artmaz)
  - Store bölümü güncellendi: SQLite yapısı (`key`, `value_json`, `updated_at`), ip_state.json root sahipliği
  - Operations bölümüne "Skor Reset (Manuel)" prosedürü eklendi
  - Troubleshooting güncellendi: kök çözüm detayları (high_volume 0, decay 100, max_ip_score 5000, scorer guard)
- Runtime değişiklikler:
  - `engine/scorer.py`: Explicit guard eklendi (flag=false ise skor artmaz)
  - `config/scoring.yaml`: high_volume 0, max_ip_score 5000
  - `config/agent.yaml`: decay.points_per_hour 100
  - `188.132.132.225` skoru manuel sıfırlandı (sec_agent.db + ip_state.json)
- Kaynak: VPS `engine/scorer.py` kod incelemesi, config dosya analizi, runtime testleri
## [2026-05-02 23:46] kimi-cli docs ingest
- Kimi Code CLI docs 23 sayfa okundu: https://www.kimi.com/code/docs/en/kimi-code-cli/
- Yeni sayfalar oluşturuldu:
  - `concepts/kimi-code-cli.md` — Genel bakış, amaç, kurulum, core operations, customisation
  - `concepts/kimi-code-cli-reference.md` — Slash commands, keyboard shortcuts, skills, MCP referansı
  - `raw/articles/kimi-code-cli-docs.md` — Kaynak URL listesi
- `index.md` Concepts bölümüne 2 yeni giriş eklendi
- Projelerde kullanım tablosu: local monorepo, ops-bot, mathlock-play, telegram-kimi

## [2026-05-03 15:45] ingest | ops-bot | 47a2a6d | 8
- Files: A:1 M:6 D:1 (README, .env.example, AGENTS.md, CHANGELOG.md, requirements.txt, agent-transformation-plan, bot.py, orchestrator)
- Pages updated: [[ops-bot]]
- Diff summary: Industry-standard documentation overhaul. README rewritten with architecture/setup/usage. .env.example synced to V2 ACP reality. AGENTS.md fixed /end command and added test step. CHANGELOG.md created (Keep a Changelog format). agent-transformation-plan.md marked as historical archive.
- Lint: 7/10 passing, 3 warnings (page size, tag audit, raw existence — pre-existing)
## [2026-05-03 16:10] ingest | ops-bot | d28a8db | 1
- Files: A:5 M:3 R:2 (.env.test, pytest.ini, tests/*, bot/config.py, deploy.sh, agents/prompts/ops-security-agent.md, ops-security-explain.md → _archive, ops-security-observe.md → _archive)
- Pages updated: [[ops-bot]]
- Diff summary: Security prompt unified (explain+observe → single ops-security-agent.md, ~40KB data recovery). Deploy script fixed to include bot/, agents/, tests/, docs/. Test suite added (30 tests, pytest-asyncio). Raw archive updated with 8 new source snapshots.
- Lint: 7/10 passing, 3 warnings (pre-existing: page size ×3, unknown tags ×4, raw existence ×4)
- Revert: git checkout 644ef939 -- wiki/
## [2026-05-03 17:04] ingest | ops-bot | d23644e | 6
- Files: A:2 M:4 D:0
- Pages created: —
- Pages updated: [[ops-bot]]
- Pages archived: —
- Diff summary: ops-bot test suite expanded to 57 tests. New files: `tests/test_acp_executor.py` (17 tests), `tests/test_telegram_messages.py` (10 tests). Fixes: `_clean_output` applied to all executor return paths; router caching and logging improved; mock/patch issues resolved in test imports.
- Lint: pending
## [2026-05-03 18:20] ingest | ops-bot + telegram-kimi | 3304d40 | 8
- Files (ops-bot): A:1 M:6 D:0
- Files (local): A:0 M:1 D:0 (`projects/telegram-kimi/bot.py`)
- Files (webimar): A:0 M:0 D:0
- Pages updated: [[ops-bot]], [[telegram-kimi]]
- Pages archived: —
- Diff summary:
  - ops-bot: ACP protocol fix for kimi-cli 1.40 (`ApprovalRequest`/`ToolCallRequest`), word-boundary risky command matching, `/iptal` footer, context usage deferred, deploy script `*.md` include fix, 7 new `test_acp_client.py` tests
  - telegram-kimi: SSH command refactored (`script -q -c` → direct `ssh`), `_context_footer` switched to ACP `usage_update` values (also broken in 1.40)
- Lint: pending
## [2026-05-03 18:52] refactor | robotopia-extraction | mathlock-play → robotopia-android

- **MathLock Play'den çıkarılanlar:**
  - `RobotopiaActivity.kt` silindi
  - `assets/robotopia/` (2.9 MB) silindi
  - `activity_robotopia.xml` silindi
  - `AndroidManifest.xml`'den declaration kaldırıldı
  - `MainActivity.kt`, `ChallengePickerActivity.kt`, `SettingsActivity.kt`, `PreferenceManager.kt`'den Robotopia referansları temizlendi
  - `proguard-rules.pro`'dan Robotopia keep kuralı kaldırıldı
  - `colors.xml`'den `card_robotopia` rengi kaldırıldı
  - `ChallengePickerUnlockPolicyTest.kt`'den ROBOTOPIA testleri kaldırıldı
  - Layout'lar: `activity_main.xml`, `activity_settings.xml`, `activity_challenge_picker.xml`'den kartlar kaldırıldı
- **Yeni proje:** `projects/robotopia-android/`
  - Package: `com.akn.robotopia`
  - App name: `Robotopia Kodlama`
  - 4 Kotlin dosyası: `MainActivity.kt`, `BaseActivity.kt`, `LocaleHelper.kt`, `LocalePrefs.kt`
  - Assets: `robotopia/` (2.9 MB) kopyalandı
  - Dependencies: core-ktx, appcompat, material, constraintlayout (4 adet)
  - No Firebase, no Billing, no Internet permission
  - Dead code temizliği: `AppLockService`, `LockStateManager`, kilit modu değişkenleri kaldırıldı
- **Build sonuçları:**
  - mathlock-play: `BUILD SUCCESSFUL` (debug + release)
  - robotopia-android: `BUILD SUCCESSFUL` (debug + release)
  - Release APK: mathlock-play 3.0M, robotopia-android 2.9M
- **Wiki güncellemeleri:**
  - `projects/mathlock-play.md` güncellendi (Robotopia notu eklendi)
  - `projects/robotopia-android.md` oluşturuldu
  - `decisions/adr-003-robotopia-extraction.md` oluşturuldu
  - `index.md` güncellendi (yeni proje + ADR + recently updated)
- Log size: 113 entries
## [2026-05-03 19:15] update | sayi-yolculugu | wiki-genisleme | detayli-dokumantasyon

- **Wiki sayfası genişletildi:** `wiki/projects/sayi-yolculugu.md`
  - Önceki: Sadece standalone HTML5 oyunu (~41 KB, statik hosting)
  - Yeni: MathLock Play entegrasyonu da eklendi
    - `SayiYolculuguActivity.kt` (490 satır) — WebView + JS Bridge
    - Backend endpoint'leri: `GET /levels/`, `POST /levels/progress/`
    - AI seviye üretim pipeline'ı: `ai-generate-levels.sh` → kimi-cli → validate → DB
    - Kredi sistemi entegrasyonu: `auto_renewal_started`, `credits_remaining`
    - Cache & offline davranış: `SecurePrefs`, `fallback-levels/{tr,en}.json`
    - Polling mekanizması: `pollForNewSet()` (5sn, max 120 deneme)
    - WebView memory leak fix detayları
  - Veri akışı diyagramı eklendi
  - Senaryo tablosu eklendi (ilk açılış, tekrar açılış, offline, vs.)
- **mathlock-play.md güncellendi:**
  - "İçindeki Oyunlar" bölümü eklendi
  - `ai-generate-levels.sh` entry point'i listeye eklendi
  - `related` alanına `sayi-yolculugu` eklendi
- Log size: 114 entries
## [2026-05-03 20:00] ingest | local | mathlock-play | yeni-oyun + bug-fix
- **Sayı Hafızası (Memory Game) eklendi:**
  - ADR: `wiki/decisions/adr-004-memory-game-integration.md`
  - Yeni dosyalar: `MemoryGameActivity.kt`, `MemoryGameEngine.kt`, 2 layout, 2 drawable
  - Native Kotlin + `ObjectAnimator` 3D flip animasyonu
  - Offline, kilit açma destekli (tur bazlı)
  - Ebeveyn ayarları: `memoryGamePairCount` (4-20), `memoryGameRequiredRounds` (1-10)
  - 27/27 unit test geçti, cihaz testi başarılı
- **Sayı Yolculuğu progress bug fix (3 kök neden):**
  - `onDestroy()`'da `completedLevelIds` + `cachedLevels` siliniyordu → kaldırıldı
  - `currentSetId` persist edilmediği için her açılışta "yeni set" algılanıyordu → `SecurePrefs`'e kaydediliyor
  - `loadLevelsIntoGame()`'de `isNewSet` mantığı `oldSetId=null` iken `true` dönüyordu → `forceClear=true` WebView progress siliyordu → düzeltildi
  - Fallback levels'te `completed_level_ids` inject edilmiyordu → `injectCompletedIds()` eklendi
- **Güncellenen wiki sayfaları:** `wiki/projects/mathlock-play.md`
- Log size: 119 entries
## [2026-05-03 21:33] ingest | mathlock-play | fc45d056 | 1 sayfa
- Files: A:0 M:0 D:0 (checkpoint = HEAD, manual update from session context)
- Pages created: —
- Pages updated: [[mathlock-play]]
- Pages archived: —
- Diff summary: Auth mekanizması (DeviceTokenAuthentication + DeviceTokenSigner), backend test suite yapısı (169 test / 10 modül, AuthMixin/ThrottleMixin), Sayı Yolculuğu Activity auth fix (403 → setAuthToken) eklendi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash

## [2026-05-03 23:17] ingest | 7/10
- mathlock-play: version bump 1.0.73→1.0.74 (build.gradle.kts)
- sec-agent: AGENTS.md v2.1 revizyonu (SOURCE OF TRUTH, BENIGN CEILING, sembolik kurallar)
- ops-bot: AGENTS.md deploy edildi (VPS /opt/sec-agent güncellendi)
- webimar: no changes

## [2026-05-04 22:50] wiki-pages | acp-protocol + adr-005
- Pages created: [[acp-protocol]], [[adr-005-ops-bot-acp-sdk-migration]]
- Pages updated: [[index]], [[ops-bot]] (cross-links)
- Diff summary: ACP protokolü konsept sayfası ve SDK geçiş ADR'si eklendi.

## [2026-05-04 22:30] ops-bot | acp-hotfixes | 0d6008b
- Files changed: bot/acp_client.py, bot/acp_executor.py, bot/telegram.py, tests/test_acp_executor.py
- Fixes: _tool_call_count reset, /iptal kills ACP process, empty response guard, reader loop EOF cleanup
- Features: structured logging, /durum diagnostic command
- Tests: 66/66 passing
- Diff summary: ACP session poisoning ve zombie process sorunları giderildi. Telegram handler'a msg_in/msg_out/duration logları eklendi.

## [2026-05-04 22:15] research | acp-sdk-exploration | feature/acp-sdk-exploration
- Package installed: agent-client-protocol==0.9.0
- Tested: spawn_agent_process, initialize, new_session, prompt, cancel with kimi-cli 1.40.0
- Key finding: --agent-file flag works in ACP mode, agent spec loads correctly
- SDK modules reviewed: acp.schema, acp.client, acp.contrib (SessionAccumulator, ToolCallTracker, PermissionBroker)
- Diff summary: ACP SDK feasibility proven. agentFile blocker resolved via --agent-file CLI flag.
## [2026-05-04 23:11] ingest | ops-bot | 0d6008b | 1 sayfa
- Files: M:4 (bot/acp_client.py, bot/acp_executor.py, bot/telegram.py, tests/test_acp_executor.py)
- Pages updated: [[ops-bot]]
- Diff summary: ACP fix'leri — tool_call_count reset on run(), empty response guard, reset_all_sessions kills ACP process, reader loop EOF cleanup, structured logging (msg_in/msg_out/duration), /durum command, get_diagnostics().
- Lint: 6/10 passing (0 failures, 4 pre-existing warnings: broken mcp-routing link, 4 oversized pages, 10 unknown tags, 5 missing raw files)

## [2026-05-05 21:11] ingest | ops-bot | c836b86 | 1 sayfa
- Files: R:4 A:4 M:5
- Pages updated: [[ops-bot]]
- Diff summary: ACP SDK migration tamamlandi — bot/acp_sdk_client.py + bot/acp_sdk_executor.py eklendi, eski ACP client/executor arsivlendi, OpsBotAcpClient file I/O sandboxing + terminal execution eklendi, telegram.py markdown sanitize + context footer guncellendi, tests/sdk/ eklendi (10 unit test), pytest.ini --ignore=tests/sdk.
- Lint: see next entry
- Revert: git checkout 31c9a1db -- wiki/
## [2026-05-05 21:22] ingest | ops-bot | d6ddb0f | 1 sayfa
- Files: R:4 A:19 M:5 D:1
- Pages updated: [[ops-bot]]
- Diff summary: VPS senkronizasyonu — bot/router.py silindi, bot/orchestrator.py + agents/ dizini eklendi, eski ACP client/executor archive/legacy'den bot/'a geri tasindi, telegram.py routing kaldirdi, mimari guncellendi.
- Lint: see next entry
- Revert: git checkout c836b86 -- wiki/
## [2026-05-05 21:40] ingest | webimar | 29c2c8a | 1 sayfa
- Files: A:4 M:20
- Pages updated: [[webimar]]
- Diff summary: OAuth hash fragment redirect, /me/ error handling, token abuse middleware, admin token blacklist eklendi. Google OAuth token log leakage fix.
- Lint: see next entry
- Revert: git checkout cb0d8be -- wiki/

## [2026-05-05 22:17] ingest | webimar | fc83c03 | 1 sayfa
- Files: M:1
- Pages updated: [[webimar]]
- Diff summary: middleware_token_abuse.py set() → list() cache fix eklendi. Her API isteğinde 500 atan JSON serialization hatası giderildi.
- Lint: see next entry
- Revert: git checkout b74b3ac -- wiki/

## [2026-05-06 00:42] archive | anka | pasife-alindi
- Anka projesi hem local'de hem VPS'de pasife alındı
- Sebep: Aktif kullanılmıyor, RAM/disk kaynağı serbest bırakıldı
- Local arşiv: backups/anka-archive-20260506.tar.gz (178MB)
- VPS arşiv: /home/akn/vps/backups/anka-archive/ (175MB: proje + 8 Docker volume)
- VPS işlemler: 8 container durduruldu, 8 volume silindi, nginx anka.conf kaldırıldı, reload edildi
- AGENTS.md güncellendi: anka referansları kaldırıldı
- Wiki güncellendi: anka.md archived, index.md güncellendi


## [2026-05-06 19:42] ingest | local | fa7dc69 | 4 sayfa
- Files: A:19 M:3 D:347 R:3
- Pages created: [[_archive/anka|Anka (Arşiv)]], [[projects/anka|Anka (Yönlendirme)]]
- Pages updated: [[mathlock-play]], [[git-workflow]], [[index]], [[system-overview]]
- Pages archived: Anka → `_archive/anka.md`
- Diff summary: Anka projesi tamamen arşivlendi (`projects/anka/` silindi). MathLock Play `.env.example` yapılandırması güncellendi (DB config ayrıldı, Celery/Redis eklendi). AGENTS.md'ye GitHub Sync + Cross-Machine Development bölümü eklendi. `.gitignore` genişletildi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout 0b893b02 -- wiki/
## [2026-05-06 21:11] ingest | 3 projects
- **local:** `AGENTS.md` (ortam tespiti bölümü eklendi), `projects/mathlock-play/deploy.sh` (VPS uyumluluğu)
- **ops-bot:** `deploy.sh` (VPS uyumluluğu, SSH multiplexing / local cp ayrımı)
- **webimar:** `deploy.sh` (VPS uyumluluğu, docker save atlaması), `docker-compose.prod.yml` (`image:` tag'leri)
- **Pages updated:** `projects/mathlock-play.md`, `projects/ops-bot.md`, `projects/webimar.md`
- **Note:** `is_vps()` fonksiyonu tüm deploy script'lerine eklendi. Aynı komutlar hem local'den hem VPS'ten çalışabilir.

## [2026-05-06 22:10] lint-fix | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: entries
- **Note:** Lint script upgraded: `status: archived` support in index completeness, type-aware page size limits (`project`: 400, `concept`: 350, `reference` exempt), SCHEMA.md updated with Page Size Policy

## [2026-05-06 22:38] ingest | AGENTS.md + weekly maintenance
- **AGENTS.md:** Ortam tespiti uyarısı eklendi (VPS/Local ayrımı için is_vps() talimatı)
- **concepts/agents-md.md:** "Ortam Tespiti (Çoklu Makine)" bölümü eklendi
- **concepts/deployment.md:** "Haftalık Wiki Bakımı" bölümü eklendi (scripts/wiki-weekly-maintenance.sh)
- **Pages updated:** concepts/agents-md.md, concepts/deployment.md
- **Note:** Deploy öncesi wiki ingest kuralına uygun olarak toplandı

## [2026-05-06 22:50] ingest | AGENTS.md wiki rule + hooks
- **AGENTS.md:** "KATI KURAL: Commit/Push ÖNCESİ Wiki TOPLANMALIDIR" bölümü eklendi
- **concepts/agents-md.md:** "Commit Öncesi Wiki Kuralı" ve best practices'e wiki ingest maddeesi eklendi
- **scripts/hooks/:** pre-commit + pre-push hook'lar oluşturuldu (wiki ingest guard)
- **Pages updated:** concepts/agents-md.md, AGENTS.md
- **Note:** Bu ingest kural ihlali sonrası yapılan düzeltme ve koruma önlemidir

## [2026-05-06 23:05] ingest | AGENTS.md dynamic environment detection
- **AGENTS.md:** "SEN NEREDESIN?" bölümü eklendi — agent kendisi ortam tespiti yapar
- **AGENTS.md:** Ortam ayrımı tablosu "LOCAL'deysem / VPS'teysem" olarak yeniden yazıldı
- **concepts/agents-md.md:** "Coklu Makine Destegi (VPS / Local)" bölümü eklendi
- **Pages updated:** concepts/agents-md.md, AGENTS.md
- **Note:** Agent'in AGENTS.md'yi okudugunda once komutu calistirip ciktiya gore davranmasi saglandi

## [2026-05-06 23:21] ingest | local + ops-bot + webimar | 3 proje

- **local** (`ecdfb06` → `e2b7e8f`): AGENTS.md güncellendi — "SEN NEREDESİN?" bölümü eklendi, ortam tespiti her açılışta zorunlu hale getirildi, LOCAL/VPS tablosu detaylandırıldı
- **ops-bot** (`d093d94` → `d05f0b6`): `.gitignore` güncellendi — `.venv/`, `venv/` ve `data/sec-agent-*.json` eklendi
- **webimar** (`cdb21b89` → `5b6a274`): `.gitignore` güncellendi — `__pycache__` izleme durduruldu, `deploy.sh`'ta domain check VPS modunda `-k` flag'i ve `000` fallback eklendi
- Pages updated: [[agents-md]], [[ops-bot]], [[webimar]], [[index]]
- Checkpoints refreshed: local, ops-bot, webimar
## [2026-05-07 00:06] ingest | ops-bot | deploy path fix

- **ops-bot** (`d05f0b6` → `8618166`): `systemd/ops-bot.service` ve `.env.production` path'leri `local` → `vps` düzeltildi; deploy akışı tek dizin (vps) üzerinden çalışır hale getirildi
- Pages updated: [[ops-bot]]
- Checkpoints refreshed: ops-bot
## [2026-05-06 23:45] ingest | webimar | disable su tahsis checks

- **webimar** (`5b6a274` → `33b6574`): 11 tarımsal yapı türü için YAS kapalı alanında su tahsis belgesi zorunluluğu geçici olarak kaldırıldı
  - `kanatli.py`: 5 kanatlı türü (yumurtacı, etçi, gezen, hindi, kaz/ördek)
  - `buyukbas.py`: süt & besi sığırcılığı
  - `kucukbas.py`: ağıl (küçükbaş)
  - `evcil_hayvan.py`, `hara.py`, `ana_modul.py` (yıkama tesisi)
- Pages updated: [[webimar]]
- Checkpoints refreshed: webimar
## [2026-05-07 12:52] ingest | ops-bot | 2956c27 | 3 sayfa
- Files: M:3
- Pages updated: [[ops-bot]], [[sec-agent]], [[security-ai-reporting]]
- Diff summary: ops-bot AI analiz koşulları medium severity’ye genişletildi, token_abuse_detector auth endpoint listesi güncellendi, systemd service state path sabitlendi.

## [2026-05-07 13:10] ingest | ops-bot | 4a37ea0 | 1 sayfa
- Files: M:1
- Pages updated: [[ops-bot]]
- Diff summary: acp_sdk_client.py git read-only komutlarına (log, status, diff) izin verdi, yazma komutları (push, commit, reset) reject listesine alındı.
## [2026-05-07 13:22] cleanup | ops-bot | — | 1 sayfa
- Files: D:1 (VPS)
- Pages updated: [[ops-bot]]
- Diff summary: Eski `logs/router_debug.jsonl` silindi (router.py kaldırıldığı için artık güncellenmiyordu).
## [2026-05-07 13:30] cleanup | ops-bot | 8ceee1c | 2 sayfa
- Files: M:1 (local), D:2 (VPS)
- Pages updated: [[ops-bot]]
- Diff summary: `docs/CURRENT_SYSTEM.md` Mayıs 2026ya güncellendi, `agent_state.db` ve `router_debug.jsonl` legacy temizliği yapıldı.
## [2026-05-07 18:45] checkpoint-sync | all | cross-machine sync
- Ops-bot: 8618166 → 8ceee1c (3 commit pulled from GitHub)
- Webimar: 5b6a274 → 33b6574 (1 commit pulled from GitHub)
- Local: d6d0f9c (1 commit ahead, post-commit fix + SSH remote switch)
- Reason: VPS'ten geliştirme sonrası cross-machine sync
- Actions: SSH remotes activated, redundant github remote removed, pre-commit hook disabled
## [2026-05-08 10:15] ingest | local + webimar | hizli checkpoint sync
- Checkpoint'ler senkronize edildi:
  - local: d648d303 → 0b42e9b2
  - ops-bot: 8ceee1c (degisiklik yok)
  - webimar: 33b6574 → 4cb13b0b5
- Yeni eklenen kaynaklar:
  - scripts/auto-sync.sh (cross-machine git sync)
  - projects/webimar/ENVIRONMENT.md (.env dokumantasyonu)
  - scripts/wiki-weekly-maintenance.sh (ff-only pull duzeltmesi)
- AGENTS.md guncellendi: Session basi git kontrolu, auto-sync.sh referansi
- Detayli wiki sayfa guncellemeleri sonraki session'a birakildi
## [2026-05-07 19:45] ingest | local | 903450e8 | 1 sayfa
- Files: A:0 M:1 D:0
- Pages updated: [[proactive-wiki]]
- Diff summary: [[proactive-wiki]]'ye auto-sync davranışı, cross-machine sync, `docs(wiki):` sonsuz döngü koruması eklendi. `wiki/.pending` artık `.gitignore`'da değil.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout 0b42e9b2d72ee0d852a02d38628429714c45c0aa -- wiki/
## [2026-05-07 21:00] ingest | mathlock-play | manual | 1 sayfa
- Files: A:0 M:1 D:0
- Pages updated: [[mathlock-play]]
- Diff summary: Batch 0 (ücretsiz 50 soru) yapısı eklendi: 5 yaş grubuna özgü soru setleri (okul öncesi/1-4. sınıf), `generate_age_questions.py` üretim scripti, `ai-generate.sh` pipeline detayları, adaptif algoritma özeti.
- Android: MemoryGameActivity restartGame() kart değeri fix, ChallengePickerActivity/MainActivity ebeveyn desen desteği, SettingsActivity kart yapısı yeniden düzenlendi, MathQuestionGenerator yaş uygun soru üretimi.
- Backend: Question.education_period alanı, load_questions.py --period parametresi, get_questions endpoint filtrelemesi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
## [2026-05-07 23:10] ingest | mathlock-play | manual | 1 sayfa
- Files: A:0 M:11 D:0
- Pages updated: [[mathlock-play]]
- Diff summary: MEB 2024 müfredat uyumu + tip isimlendirme standardizasyonu:
  - `generate_age_questions.py`: 1. sınıf çarpma kaldırıldı (%20→0), 2. sınıf kare tipi kaldırıldı
  - `MathQuestionGenerator.kt`: 1. sınıf çarpma kaldırıldı, 2. sınıf kare kaldırıldı
  - `MathChallengeActivity.kt`: `siralama` → `sıralama` tip kontrolü düzeltildi
  - 5 agents.md dosyası tip isimleri Türkçe karakterli olarak standartlaştırıldı (`çıkarma`, `çarpma`, `bölme`, `sıralama`, `eksik_sayı`, `karşılaştırma`, `örüntü`)
  - 1. sınıf: çıkarmada onluktan bozma kontrolü eklendi (`b ≤ a mod 10`)
  - 2. sınıf: zorluk 5 toplama üst limiti 100 yapıldı (MEB "100'e kadar eldeli toplama")
  - 3. sınıf: kesir sadece üniter (pay=1), problem max 2 işlem
  - 4. sınıf: rapor şablonları yaş grubuna özgü hale getirildi
  - 5 curriculum JSON dosyası tip isimleriyle güncellendi
  - Kopyala-yapıştır rapor şablonu hataları giderildi
## [2026-05-07 23:25] ingest | mathlock-play | manual | 1 sayfa
- Files: A:0 M:1 D:0
- Pages updated: [[mathlock-play]]
- Diff summary: Batch 0 Üretim Algoritması bölümü eklendi: `generate_age_questions.py` yapısı, zorluk hesaplama heuristic'i, ID_RANGES offset tablosu, yaş grubu başına işlem dağılımı, Android `MathQuestionGenerator.kt` fallback üretim mantığı, hint ekleme mekanizması.
## [2026-05-07 23:44] ingest | mathlock-play | a85334a | 3 sayfa
- Dosyalar: M:10 (agents/curriculum/sinif_3.json, agents/questions-sinif-2.agents.md, StatsDashboardActivity.kt, PerformanceReportActivity.kt, generate_age_questions.py, data/questions-*.json × 5)
- Pages created: —
- Pages updated: [[mathlock-play-ai]], [[mathlock-play-android]], [[mathlock-play]]
- Pages archived: —
- Diff özeti: MEB uyum düzeltmeleri eklendi: curriculum/sinif_3.json non-üniter kesir fix, generate_age_questions.py grade1 çıkarma=0 fix, questions-sinif-2.agents.md zorluk 5 toplama 100'e genişletildi. Android TYPE_LABELS Türkçe karakter standardizasyonu tamamlandı.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout a85334a^ -- wiki/

## [2026-05-07 23:55] decision | adr-007 | mathlock-play | meb-curriculum-compliance-implantation
- Type: new-adr
- Page: [[adr-007-mathlock-meb-curriculum-compliance-implantation]]
- Status: Active
- Scope: mathlock-play, mathlock-play-ai, mathlock-play-android, mathlock-play-backend
- Summary: MEB 2024 müfredat uyum implantasyonu — 4 eksiklik giderildi:
  1. Ağırlıklı işlem dağılımı (OPERATION_WEIGHTS + random.choices)
  2. Kazanım bazlı min-max bantlar (generator keyword-only args, 9×9 çarpma, üniter kesir zorunlu)
  3. Yapılandırılmış ID (question_code CharField, structured_id(), geriye uyumlu id korundu)
  4. interactionMode (tap-to-count, pattern-select, tap-to-choose, text-input)
- Files changed: generate_age_questions.py, validate-questions.py, backend/credits/models.py, agents/questions-*.agents.md (6 dosya)
- Wiki: index.md güncellendi, log.md güncellendi
## [2026-05-08 11:50] ingest | mathlock-play-meb-analysis
- Yeni: analysis/meb-2024-curriculum-technical-alignment.md (MEB 2024 uyum analizi, 5 bölüm)
- Güncelleme: index.md (analysis sayfası eklendi)
- Güncelleme: projects/mathlock-play.md (cross-reference eklendi)
- Log size: 223 entries


## 2026-05-08 — MathLock Play ingest (batch-0 validation, CreditPackage removal, version auto-increment)

- Yeni: `scripts/validate-questions.py` — dönem bazlı doğrulama aracı
- Güncelleme: `generate_age_questions.py` — zorluk 4-5, versiyon artırma (`data/.version`)
- Güncelleme: `backend/credits/models.py` — `CreditPackage` kaldırıldı
- Güncelleme: `backend/credits/views.py` — `CreditPackage` import temizliği
- Yeni: `backend/credits/migrations/0012_remove_creditpackage.py`
- Güncelleme: Batch 0 JSON'ları regenerate edildi (versiyon 5)
- Data sync: `/var/www/mathlock/data/questions.json` versiyon 5'e yükseltildi
- Deploy: VPS'te 0011 + 0012 migration uygulandı, 220 soru backfill edildi
- Sayfa güncellemeleri: `projects/mathlock-play.md`, `projects/mathlock-play-backend.md`, `projects/mathlock-play-ai.md`
## 2026-05-08 — Webimar ana sayfa duyurusu ve bağ evi max alan bilgisi

- Yeni: Ana sayfa duyuru banner'ı — hayvancılık ve yıkama tesisleri için su tahsis belgesi aranmayacak
- Güncelleme: `webimar-nextjs/pages/index.tsx` + `styles/HomePage.module.css` — duyuru banner'ı ve responsive stil
- Güncelleme: `webimar-react/src/modules/BagEvi/utils/calculator.ts` — success mesajlarına max 30 m² taban / 60 m² toplam alan notu eklendi
- Sayfa güncellemeleri: `projects/webimar.md`

## [2026-05-09 11:00] ingest | system-audit | hook-fix | checkpoint-sync

- AGENTS.md güncellendi (tarih: 2026-05-09, lint: 8/10, GitHub push: verified)
- VPS hook sistemi tamamlandı: git hooks + kimi-cli hooks (protect-env, wiki-auto-pending, wiki-lint-on-stop)
- Checkpoint SHA'ları düzeltildi (local, webimar, mathlock-play, infrastructure, sec-agent)
- `scripts/setup-vps-dev.sh` felaket senaryosuna hazır: git hooks + kimi-cli hooks otomatik kurulum
- `wiki/concepts/agents-md.md` updated: 2026-05-09
- Pages updated: [[agents-md]], [[git-workflow]], [[proactive-wiki]]

## [2026-05-09 12:14] ingest | local | f4230fd | 1
- Files: A:0 M:1 D:0
- Pages created: (none)
- Pages updated: [[proactive-wiki]]
- Pages archived: (none)
- Diff summary: wiki/concepts/proactive-wiki.md değişikliği — proaktif wiki yöneticisi konsept sayfası güncellendi.
- Lint: 8/10 passing (2 warnings: pre-existing)

## [2026-05-09 13:43] ingest | local | 73d9abcb | 4
- Files: A:0 M:4 D:0
- Pages created: (none)
- Pages updated: [[mathlock-play]], [[mathlock-play-android]]
- Pages archived: (none)
- Diff summary: Parent auth bottom sheet kaldırıldı — doğrudan BiometricPrompt. AndroidManifest.xml'e USE_BIOMETRIC + USE_FINGERPRINT eklendi. AGENTS.md wiki filtreleme kuralı eklendi. v1.0.76 release build.
- Lint: 8/10 passing (2 warnings: pre-existing)
## [2026-05-09 15:01] ingest | mathlock-play | 681346a3 | 3
- Files: A:3 M:4 D:0
- Pages created: (none)
- Pages updated: [[mathlock-play]], [[mathlock-play-android]], [[mathlock-play-backend]]
- Pages archived: (none)
- Diff summary: 7 critical Android bug fixes (StatsTracker idempotency, AccountManager 403 re-register, CreditApiClient 503 parsing, 409 retry loop, raw device token, LockStateManager thread-safety, SecurePrefs hard fail). UI/UX improvements (ChallengePickerActivity BIOMETRIC_STRONG or DEVICE_CREDENTIAL, btnNext sizing, parent card styling). New tests: AccountManagerTest, StatsTrackerTest, LockStateManagerTest. Conscrypt test fix. Backend credits/auth updates + VPS deploy. v1.0.77.
- Lint: pending
## [2026-05-09 18:54] ingest | mathlock-play | c603c9ee | mathlock-play-android
- Dosyalar: M:4
- Pages updated: [[mathlock-play-android]]
- Diff özeti: ChildProfilesActivity, StatsDashboardActivity, PerformanceReportActivity ve AccountActivity'e `Authorization: Device <signed_token>` header eklendi. AccountActivity email kaydında `getOrRegister()` çağrısı eklendi. Backend `DeviceTokenAuthentication` imzalı token beklediği için raw UUID ile `403 Forbidden` dönüyordu.
## [2026-05-09 19:15] ingest | mathlock-play | 33e003a2 | mathlock-play-android
- Dosyalar: M:11
- Pages updated: [[mathlock-play-android]]
- Diff özeti: Memory Game preview + dynamic card size, AppLockService overlay bypass, MathChallenge set/batch display, SayiYolculugu cache fix, Settings preview slider.
## [2026-05-10 02:10] ingest | local | 02ce0371 | 3 sayfa
- Files: A:2 M:2
- Pages created: [[local]]
- Pages updated: [[index]], [[log]]
- Diff summary: AGENTS.md refactor edildi (499→167 satır). references/QUICKREF.md oluşturuldu. WORKFLOW.md'ye wiki filtreleme ve içerik iddiası kuralları eklendi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout 73185046 -- wiki/
## [2026-05-10 10:28] ingest | mathlock-play | f60cd6e9 | mathlock-play-android
- Files: A:3 M:30+ (Android activity, service, util, layout, tests; backend API, models, tasks, migrations)
- Pages updated: [[mathlock-play-android]]
- Diff summary: v1.0.78 release — AppLockService derleme hatası düzeltildi (unclosed lambda). MemoryGameEngine pair limit 4-20→4-30. AccountManagerTest/StatsTrackerTest eklendi. Play Store upload script (upload-play-store.py) oluşturuldu.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout f60cd6e9 -- wiki/
## [2026-05-10 11:37] ingest | local | 7853108 | 4 sayfa
- Files: A:1 M:10 D:3
- Pages created: 
- Pages updated: [[local]], [[mathlock-play]], [[mathlock-play-android]], [[mathlock-play-backend]]
- Pages archived: 
- Diff summary: MathLock Play monorepo'dan ayrı repo'ya çıkarıldı (github.com/atlnatln/mathlock-play). AGENTS.md, QUICKREF.md, setup-vps-dev.sh, pre-push güncellendi. v1.0.78 derleme fix, upload-play-store.py eklendi. .gitignore'a eklendi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout e5ae1fc1 -- wiki/

## [2026-05-10 13:38] lint | 4/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 11
- Missing from index: 2
- Frontmatter errors: 1
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 16 (adaptive-learning, agent-instructions, alignment, analysis, api, archive, auth, backend, curriculum, drf...)
- Raw existence: 0
- Log size: 79 entries

## [2026-05-10 13:41] lint | 5/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 11
- Missing from index: 12
- Frontmatter errors: 1
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 80 entries

## [2026-05-10 13:43] lint | 5/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 2
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 1 (agent-instructions)
- Raw existence: 0
- Log size: 81 entries

## [2026-05-10 13:44] lint | 5/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 2
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 1 (agent-instructions)
- Raw existence: 0
- Log size: 82 entries

## [2026-05-10 13:44] lint | 6/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 2
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 83 entries

## [2026-05-10 13:45] lint | 6/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 2
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 84 entries

## [2026-05-10 13:45] lint | 6/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 1
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 85 entries

## [2026-05-10 13:46] lint | 6/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 1
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 86 entries

## [2026-05-10 13:48] lint | 7/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 0
- Missing from index: 12
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 87 entries

## [2026-05-10 13:50] lint | 6/10
- Orphan pages: 2 ([[AGENTS]], [[local]])
- Broken links: 3
- Missing from index: 11
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 88 entries

## [2026-05-10 13:54] lint | 5/10
- Orphan pages: 3 ([[concepts-index]], [[decisions-index]], [[projects-index]])
- Broken links: 1
- Missing from index: 1
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 2 (index, projects)
- Raw existence: 0
- Log size: 89 entries

## [2026-05-10 13:55] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 1
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 1 (project)
- Raw existence: 0
- Log size: 90 entries

## [2026-05-10 13:56] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 7
- Unknown tags: 0
- Raw existence: 0
- Log size: 91 entries

