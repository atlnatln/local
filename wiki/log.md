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
## [2026-05-01 19:23] lint | 3/10
- Orphan pages: 4 ([[ops-bot-deploy-script]], [[ops-bot-readme]], [[ops-bot-systemd-service]], [[system-overview]])
- Broken links: 16
- Missing from index: 3
- Frontmatter errors: 3
- Stale pages: 1
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 1 (python)
- Raw existence: 0
- Log size: 2 entries

## [2026-05-01 19:24] lint | 5/10
- Orphan pages: 4 ([[ops-bot-deploy-script]], [[ops-bot-readme]], [[ops-bot-systemd-service]], [[system-overview]])
- Broken links: 7
- Missing from index: 3
- Frontmatter errors: 3
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 3 entries


## [2026-05-01 19:30] ingest | webimar | 2eb3dfa | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: [[webimar]]
- Diff summary: Full ingest of webimar project. Agriculture calculation platform with Django + Next.js + React.

## [2026-05-01 19:31] ingest | anka | 4db9944 | 1
- Files: A:0 M:0 D:0 (checkpoint = HEAD, full scan)
- Pages created: [[anka]]
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
## [2026-05-01 19:27] lint | 4/10
- Orphan pages: 9 ([[anka-readme]], [[infrastructure-docker-compose]], [[infrastructure-setup-script]], [[mathlock-play-readme]], [[ops-bot-deploy-script]]...)
- Broken links: 7
- Missing from index: 8
- Frontmatter errors: 8
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 2
- Unknown tags: 1 (kotlin)
- Raw existence: 0
- Log size: 8 entries

## [2026-05-01 19:27] lint | 5/10
- Orphan pages: 9 ([[anka-readme]], [[infrastructure-docker-compose]], [[infrastructure-setup-script]], [[mathlock-play-readme]], [[ops-bot-deploy-script]]...)
- Broken links: 6
- Missing from index: 8
- Frontmatter errors: 8
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 2
- Unknown tags: 0
- Raw existence: 0
- Log size: 9 entries

## [2026-05-01 19:28] lint | 4/10
- Orphan pages: 9 ([[anka-readme]], [[infrastructure-docker-compose]], [[infrastructure-setup-script]], [[mathlock-play-readme]], [[ops-bot-deploy-script]]...)
- Broken links: 6
- Missing from index: 8
- Frontmatter errors: 8
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 1 (raw)
- Raw existence: 0
- Log size: 10 entries

## [2026-05-01 19:28] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 11 entries

## [2026-05-01 20:51] lint | 5/10
- Orphan pages: 1 ([[README]])
- Broken links: 3
- Missing from index: 1
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 1 (guide)
- Raw existence: 0
- Log size: 12 entries

## [2026-05-01 20:52] lint | 8/10
- Orphan pages: 1 ([[README]])
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 13 entries

## [2026-05-01 20:53] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 14 entries

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
## [2026-05-01 22:11] lint | 7/10
- Orphan pages: 1 ([[proactive-wiki]])
- Broken links: 2
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 3 (automation, git-hook, local-wiki)
- Raw existence: 0
- Log size: 17 entries

## [2026-05-01 22:13] lint | 7/10
- Orphan pages: 1 ([[proactive-wiki]])
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 4 (automation, git, git-hook, local-wiki)
- Raw existence: 0
- Log size: 18 entries

## [2026-05-01 22:14] lint | 6/10
- Orphan pages: 0
- Broken links: 4
- Missing from index: 0
- Frontmatter errors: 1
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 4 (automation, git, git-hook, local-wiki)
- Raw existence: 0
- Log size: 19 entries

## [2026-05-01 22:15] lint | 7/10
- Orphan pages: 0
- Broken links: 4
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 4 (automation, git, git-hook, local-wiki)
- Raw existence: 0
- Log size: 20 entries

## [2026-05-01 22:15] lint | 8/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 4 (automation, git, git-hook, local-wiki)
- Raw existence: 0
- Log size: 21 entries

## [2026-05-01 22:16] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 4 (automation, git, git-hook, local-wiki)
- Raw existence: 0
- Log size: 22 entries

## [2026-05-01 22:16] lint | 10/10
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


## [2026-05-01 22:06] ingest | telegram-kimi | first-ingest | telegram-kimi-wiki-olusturuldu

- Project: telegram-kimi
- Type: first-ingest
- Pages created: [[telegram-kimi]]
- Raw sources: raw/articles/telegram-kimi-readme.md, raw/articles/telegram-kimi-plan.md
- Checkpoint: local (monorepo, e8ddf291)
## [2026-05-01 22:34] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 25 entries


## [2026-05-01 22:08] ingest | sayi-yolculugu | first-ingest | sayi-yolculugu-wiki-olusturuldu

- Project: sayi-yolculugu
- Type: first-ingest
- Pages created: [[sayi-yolculugu]]
- Raw sources: raw/articles/sayi-yolculugu-index.html
- Checkpoint: local (monorepo, e8ddf291)
## [2026-05-01 22:37] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 27 entries

## [2026-05-01 22:39] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 28 entries


## [2026-05-01 22:12] cleanup | konsept-silme | placeholder-temizligi | eksik-sayfalar-kaldirildi

- Removed from index: [[django-nextjs-pattern]], [[ssl-certbot]], [[multi-web-project-system]]
- Removed related references: infrastructure.md, ops-bot.md, webimar.md, deployment.md
- Updated: projects/index.md (stale data corrected)
- Reason: Content already covered by infrastructure.md and project pages; YAGNI
## [2026-05-01 22:53] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 30 entries

## [2026-05-01 22:53] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 31 entries


## [2026-05-01 22:15] concept | monitoring | yeni-konsept | monitoring-wiki-olusturuldu

- Concept: [[monitoring]]
- Type: new-concept
- Coverage: Prometheus, nginx health check, sec-agent metrics, systemd timers, alert kanalları
- Sources: raw/articles/infrastructure-docker-compose.md
## [2026-05-01 22:56] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 33 entries


## [2026-05-01 22:20] concept | infrastructure-detaylari | yeni-konseptler | nginx-ssl-log-olusturuldu

- Concepts created: [[nginx-routing]], [[ssl-automation]], [[log-management]]
- Updated: [[monitoring]] (Grafana + Loki eklendi)
- Updated: [[infrastructure]] (cross-link'ler eklendi)
- Updated: [[index.md]] (yeni konseptler listeye eklendi)
- Sources: infrastructure/nginx/conf.d/, infrastructure/renew-ssl.sh, infrastructure/ssl-cron-setup.sh, infrastructure/docker-compose.yml
## [2026-05-01 23:03] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 2 (certbot, logging)
- Raw existence: 3
- Log size: 35 entries

## [2026-05-01 23:04] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 36 entries


## [2026-05-01 22:25] restructure | index-organizasyon | genelden-ozele | index-yeniden-siralandi

- index.md yeniden organize edildi: System → Infrastructure & Platform → Concepts → Decisions → Projects
- infrastructure Projects listesinden cikarildi, Infrastructure & Platform bolumune kondu
- README.md'ye "Wiki Organizasyon Kurallari" eklendi (genelden ozele siralama, sayfa tipleri, checklist)
- Updated: README.md, index.md
## [2026-05-01 23:17] lint | 8/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 38 entries

## [2026-05-01 23:17] lint | 8/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 39 entries

## [2026-05-01 23:18] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 40 entries

## [2026-05-01 23:18] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 41 entries

## [2026-05-01 23:19] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 42 entries

## [2026-05-01 23:19] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 43 entries

## [2026-05-01 23:19] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 44 entries

## [2026-05-01 23:20] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 45 entries

## [2026-05-01 23:20] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 46 entries

## [2026-05-01 23:20] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 47 entries

## [2026-05-01 23:20] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 48 entries

## [2026-05-01 23:21] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 49 entries


## [2026-05-01 22:30] docs | agents-md | guncelleme | AGENTS.md-yenilendi

- AGENTS.md footer guncellendi: 5 proje -> 7 proje, mathlock -> mathlock-play
- Servisler tablosuna sec-agent eklendi
- Wiki Kullanimi bolumu kisaltilip wiki/README.md'ye yonlendirildi
- Reason: Eski bilgiler yanilticiydi, wiki ile bilgi ciftlenmesi azaltiliyor

## [2026-05-01 22:35] docs | agents-md | minimalize | proje-yapisi-kisaltildi

- AGENTS.md proje yapisi agaci kisaltildi (292 -> 258 satir)
- Detaylar wiki/system-overview.md ve wiki/projects/'e yonlendirildi
- Bilgi ciftlenmesi azaltiliyor, kontrol korunuyor
## [2026-05-01 23:49] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 52 entries


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
## [2026-05-02 00:30] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 56 entries

## [2026-05-02 01:04] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 57 entries

## [2026-05-02 01:01] ingest | all | n/a | 0 sayfa
- Files: A:0 M:0 D:0
- Pages created: (none)
- Pages updated: (none)
- Pages archived: (none)
- Diff özeti: Checkpoint'ler zaten güncel (ops-bot: ab281619, webimar: 2eb3dfa2). `.pending` marker'ı temizlendi. Gerçek bir değişiklik tespit edilmedi.
- Lint: 10/10 passing

## [2026-05-02 01:27] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 59 entries

[2026-05-02T01:27:26+03:00] INGEST: No changes detected (all diffs empty). Pending cleared.
## [2026-05-02 01:28] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 60 entries

[2026-05-02T01:28:04+03:00] INGEST: No changes detected (all diffs empty). Pending cleared.
## [2026-05-02 01:33] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 61 entries

[2026-05-02T01:33:43+03:00] INGEST: 1 project updated (ops-bot). 1 file changed (agent.py). Lint 10/10. Checkpoints refreshed.

## [2026-05-02 02:48] ingest | local + webimar + mathlock-play | 3 projects
- **webimar** (`2eb3dfa` → `416474ac`): Security hardening — settings.py defaults tightened, CORS http origins removed, DEFAULT_PERMISSION_CLASSES flipped to IsAuthenticated, .env files cleaned from git
- **mathlock-play** (new commits): Crash prevention — ProGuard rules, WebView memory leak fixes, Handler polling leak fix, BootReceiver try/catch, Firebase Crashlytics 18.6.4 integration
- **local** (monorepo): Plan files for webimar security rollout and mathlock crash fix
- Pages updated: [[webimar]], [[mathlock-play]]
- Pages created: —
- Checkpoints refreshed: local, webimar
## [2026-05-02 02:54] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 63 entries

