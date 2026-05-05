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

## [2026-05-02 03:25] lint | 9/10
- Orphan pages: 0
- Broken links: 2
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 64 entries

## [2026-05-02 03:25] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 65 entries

## [2026-05-02 03:35] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 66 entries


## [2026-05-02 03:30] decision | adr-001 | infrastructure
- Type: new-adr
- Page: [[adr-001-monorepo-hybrid-structure]]
- Status: Active
- Scope: infrastructure, git-workflow
- Summary: Monorepo + ayrı repo karışık yapısı kararı. Büyük projeler (ops-bot, webimar) ayrı repo; küçük projeler ve altyapı tek monorepo altında.
## [2026-05-02 03:48] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 68 entries

## [2026-05-02 03:48] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 69 entries

## [2026-05-02 03:54] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 70 entries

## [2026-05-02 12:08] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 71 entries


## [2026-05-02 12:09] ingest | local | e2a6cc7 | 26
- Files: A:9 M:16 D:0 (wiki docs + telegram-kimi code)
- Pages created: [[sayi-yolculugu]], [[telegram-kimi]], [[git-workflow]], [[log-management]], [[monitoring]], [[nginx-routing]], [[ssl-automation]]
- Pages updated: [[index]], [[system-overview]], [[infrastructure]], [[mathlock-play]], [[ops-bot]], [[webimar]], [[proactive-wiki]], [[deployment]], [[README]], [[SCHEMA]]
- Pages archived: —
- Diff summary: Incremental ingest. telegram-kimi bot.py and PLAN.md updated (local/ssh-tt mode, photo support). Wiki concepts and project pages synced from monorepo.
- Lint: 10/10 passing
## [2026-05-02 12:08] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 73 entries

2026-05-02 — concept: [[security-ai-reporting]] eklendi. sec-agent günlük rapor → kimi-cli AI analizi → Telegram bildirim akışı dökümante edildi. (projects/ops-bot.md, index.md güncellendi)
## [2026-05-02 14:13] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 2
- Log size: 74 entries

## [2026-05-02 14:14] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 75 entries


## [2026-05-02 19:31] update | ops-bot | vps-deploy-dizini | runtime
- Sayfa: [[ops-bot]]
- Değişiklik: VPS Dizin Yapısı ve Troubleshooting bölümleri eklendi
- Sebep: `/home/akn/local/ops-bot/` silinmişti, systemd servisi `Result: resources` ile başlayamıyordu
- Çözüm: Eski `local/ops-bot/data/` dosyaları `vps/ops-bot/data/` altına kopyalandı; `/home/akn/local/ops-bot` symlink olarak `/home/akn/vps/ops-bot`'a bağlandı
- Servis: `ops-bot.service` `active (running)` — Telegram token doğrulandı, Application started
- Kaynak: `systemd/ops-bot.service` incelemesi + VPS shell komutları + deploy script davranışı
## [2026-05-02 19:35] lint | 10/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 0
- Unknown tags: 0
- Raw existence: 0
- Log size: 77 entries


## [2026-05-02 19:35] create | sec-agent | yeni-proje-sayfasi
- Sayfa: [[sec-agent]] oluşturuldu
- Sayfa: [[ops-bot]] güncellendi (Security bölümü kısaltıldı, sec-agent wikilink eklendi)
- Sayfa: [[index]] güncellendi (sec-agent Projects tablosuna eklendi)
- İçerik: Pipeline mimarisi, VPS dizin yapısı (deploy vs /opt), components, guardrails, systemd servisleri, resource limits, operations, troubleshooting
- Kaynak: VPS `/opt/sec-agent/` incelemesi, yerel `ops-bot/sec-agent/` yapısı, `move-sec-agent-to-opt.sh`, systemd unit dosyaları
## [2026-05-02 19:42] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 79 entries


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
## [2026-05-02 19:50] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 81 entries


## [2026-05-02 19:50] update | sec-agent | whitelist-yaklasimi-kaldirildi
- Sayfa: [[sec-agent]] güncellendi
- Değişiklik: Troubleshooting bölümünde "Bloklanmaması gereken IP engellendi" case'i yeniden yazıldı
- Prensip eklendi: "Yanlış block'lar whitelist'e çözüm değildir. Root cause sistem ayarlarındadır."
- Normal kullanıcı case'inde "Whitelist'e ekle" adımı kaldırıldı; yerine "Aktif block'u kaldır + config düzelt" önerisi kondu
- Runtime: `config/ignore.yaml`'dan 188.132.132.225/32 kaldırıldı (VPS + yerel repo)
- Kaynak: Kullanıcı geri bildirimi — IP bazlı workaround yerine sistematik düzeltme prensibi
## [2026-05-02 19:53] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 83 entries


## [2026-05-02 19:55] update | adr-002 | host-duzeyi-kimi-cli
- Sayfa: [[adr-002-sec-agent-daily-report-agent-router]] güncellendi
- Değişiklik: Yürütme modeline "kimi-cli host düzeyinde çalışır" kısıtlaması eklendi
- Consequences/Riskler bölümlerine host düzeyinde çalışmanın etkileri eklendi
- VPS doğrulaması: `/home/akn/.local/bin/kimi` ve `/home/akn/.local/bin/kimi-cli` symlink'leri mevcut
- Kaynak: Kullanıcı geri bildirimi — kimi-cli'nin container/izole ortam yerine host düzeyinde çalışması zorunluluğu
## [2026-05-02 20:02] lint | 7/10
- Orphan pages: 1 ([[adr-002-sec-agent-daily-report-agent-router]])
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 2 (ai, sec-agent)
- Raw existence: 0
- Log size: 85 entries

## [2026-05-02 20:02] lint | 7/10
- Orphan pages: 1 ([[adr-002-sec-agent-daily-report-agent-router]])
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 2 (ai, sec-agent)
- Raw existence: 0
- Log size: 86 entries

## [2026-05-02 20:02] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 2 (ai, sec-agent)
- Raw existence: 0
- Log size: 87 entries

## [2026-05-02 20:44] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 2 (ai, sec-agent)
- Raw existence: 0
- Log size: 88 entries


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
## [2026-05-02 23:52] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 2 (ai, sec-agent)
- Raw existence: 0
- Log size: 90 entries

## [2026-05-02 23:46] kimi-cli docs ingest
- Kimi Code CLI docs 23 sayfa okundu: https://www.kimi.com/code/docs/en/kimi-code-cli/
- Yeni sayfalar oluşturuldu:
  - `concepts/kimi-code-cli.md` — Genel bakış, amaç, kurulum, core operations, customisation
  - `concepts/kimi-code-cli-reference.md` — Slash commands, keyboard shortcuts, skills, MCP referansı
  - `raw/articles/kimi-code-cli-docs.md` — Kaynak URL listesi
- `index.md` Concepts bölümüne 2 yeni giriş eklendi
- Projelerde kullanım tablosu: local monorepo, ops-bot, mathlock-play, telegram-kimi

## [2026-05-02 23:52] lint | 9/10
- Yeni sayfalar eklendi: concepts/kimi-code-cli.md, concepts/kimi-code-cli-reference.md
- Tag taxonomy güncellendi: kimi-cli, tool, agent, reference, ai, sec-agent
- Lint: 9/10 passing, 1 warning (sec-agent.md oversized — pre-existing)

## [2026-05-02 23:59] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 6 (agent, ai, kimi-cli, reference, sec-agent, tool)
- Raw existence: 0
- Log size: 93 entries

## [2026-05-02 23:59] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 2 (ai, sec-agent)
- Raw existence: 0
- Log size: 94 entries

## [2026-05-02 23:59] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 95 entries

## [2026-05-03 00:00] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 96 entries

2026-05-03 00:28 | wiki | ops-bot Phase 1 files created (uncommitted) — checkpoint already current
2026-05-03 00:46 | wiki | ops-bot V2 deployed — 6 phase POC complete (48 files, +7953 lines) | checkpoint=28ea20e2
## [2026-05-03 01:30] lint | 9/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 1
- Unknown tags: 0
- Raw existence: 0
- Log size: 97 entries

## [2026-05-03 02:30] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 2
- Unknown tags: 1 (acp)
- Raw existence: 0
- Log size: 98 entries


## 2026-05-03 — Ops-Bot V2 Routing & Timeout Fixes

- Timeout sorunları çözüldü: ACP prompt 60s sınırı kaldırıldı, HTTP timeout 30s, embedding router aktifleştirildi
- Türkçe routing desteği: Tüm agent descriptor'lara `keywords_tr` eklendi
- LLM fallback prompt'u Türkçe query eşleştirmesiyle zenginleştirildi
- Tool call event handler'ları eklendi (`tool_call`, `tool_call_update`)
- Agent spec YAML'dan `tools: []` kaldırıldı (extend: default ile çalışıyor)
- `.env.production`'a `OPS_BOT_EMBEDDING_ROUTER=true` eklendi
## [2026-05-03 03:12] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 2
- Unknown tags: 1 (acp)
- Raw existence: 0
- Log size: 99 entries


## 2026-05-03 13:45 — Ingest: ops-bot

- **Trigger:** Auto-prompt (user "Evet, otomatik topla")
- **Projects:** ops-bot (1 project)
- **Commits:** b4f50d8, 2809ba3, 6ebd0f2 (3 commits since e36f158)
- **Files changed:** 6 files
  - `agents/descriptors/ops-security-agent.yaml` — keywords_tr updated (+hack, sızma, güvenlik açığı; -brute force)
  - `bot/acp_client.py` — risky command permission rejection
  - `bot/acp_executor.py` — tool call limit (15), timeout caps (90/120/180), reset_session/reset_all_sessions, always build agent spec
  - `bot/memory.py` — rolling summary removed, only last 1 message in context
  - `bot/router.py` — single-brain: explicit @agent only, else general/master
  - `bot/telegram.py` — /iptal now clears all sessions + memory, tracks last_agent
- **Wiki pages updated:** `projects/ops-bot.md`
  - Stack: embedding router marked DEPRECATED
  - Entry points: router.py, memory.py descriptions updated
  - Agent selection: single-brain architecture documented
  - ACP Executor: tool call guard, timeout table, single master agent note
  - New section: Güvenlik Kontrolleri (risky command filter)
  - New section: Komutlar (/iptal, /end)
  - Recent Commits refreshed
- **Checkpoints updated:** ops-bot → b4f50d80de6d17dfcec3b31c7ffe04b3bf50378b
- **Lint:** Pending
## [2026-05-03 13:49] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 2
- Unknown tags: 1 (acp)
- Raw existence: 0
- Log size: 100 entries

## [2026-05-03 14:03] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 1 (acp)
- Raw existence: 3
- Log size: 101 entries

## [2026-05-03 14:04] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 1 (acp)
- Raw existence: 0
- Log size: 102 entries


## 2026-05-03 13:50 — Ingest: kimi-cli docs

- **Trigger:** User request (fetch + update)
- **Source URLs:**
  - https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/overrides-and-precedence.html
  - https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html
  - https://www.kimi.com/code/docs/en/kimi-code-cli/customization/sub-agents.html
- **Wiki pages updated:**
  - `concepts/kimi-code-cli.md` — Güncellendi: CLI parameters, env vars, config priority, skill discovery/creation/flow skills, custom agents, system prompt variables, subagent types, agent tool parameters
  - `concepts/kimi-code-cli-reference.md` — **Silindi** (kullanıcı slash commands/keyboard shortcuts bilgilerini wiki'den çıkarmak istedi)
- **Wiki pages updated (follow-up):**
  - `index.md` — `kimi-code-cli-reference` çıkarıldı
  - `concepts/kimi-code-cli.md` — Raw URL sources kaldırıldı, "Kaynaklar" bölümü eklendi
- **Lint:** 8/10 passing (2 warnings: page size, tag audit)

## 2026-05-03 14:25 — Ingest: ops-bot tek evren dönüşümü

- **Trigger:** User request (plan modu onaylı)
- **Project:** ops-bot
- **Commits:** 2c685d6 (tek evren dönüşümü)
- **Files changed:** 47 files, +395 -2280 lines
- **Actions:**
  - Deleted: `agents/descriptors/` (11 YAML), `descriptor_loader.py`, `manager.py`, `process.py`, `state.py`, `migrate_v1_to_v2.py`, `router/hybrid.py`, `router/embedding.py`
  - Created skills: `nginx-routing/SKILL.md`, `postgres-query/SKILL.md`, `security-reporting/SKILL.md` (YAML frontmatter)
  - Updated skills: `docker-troubleshooting/SKILL.md` (frontmatter eklendi)
  - Updated subagents: 9 YAML (`version: 1` integer, `tools` listesi, `system_prompt_args`)
  - Updated prompts: 9 MD (`${ALLOWED_COMMANDS}`, `${FORBIDDEN_PATTERNS}`)
  - Updated master: `agent.yaml` (`version: 1`, `system_prompt_args`), `system.md` (`${KIMI_NOW}`, `${KIMI_WORK_DIR}`, `${KIMI_SKILLS}`)
  - Simplified bot: `config.py`, `router.py`, `acp_executor.py`, `memory.py`, `telegram.py`
- **Wiki pages updated:** `projects/ops-bot.md` (19 edits)
- **Checkpoints updated:** ops-bot → 2c685d6
- **Lint:** Pending
## [2026-05-03 14:36] lint | 8/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 1 (acp)
- Raw existence: 0
- Log size: 103 entries


## 2026-05-03 14:45 — Wiki + AGENTS.md güncellemesi

- **Trigger:** User request (fetch 6 URLs + wiki update + AGENTS.md)
- **Source URLs:**
  - https://agents.md
  - https://github.com/MoonshotAI/kimi-cli/blob/main/docs/AGENTS.md
  - https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/agents.md
  - https://github.com/MoonshotAI/kimi-cli/blob/main/src/kimi_cli/agents/default/system.md
  - https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/skills.md
- **Wiki pages created:**
  - `concepts/agents-md.md` — AGENTS.md formatı, konum, hiyerarşi, kimi-cli entegrasyonu, best practices
- **Wiki pages updated:**
  - `index.md` — agents-md eklendi
  - `concepts/kimi-code-cli.md` — `${KIMI_AGENTS_MD}` açıklaması zenginleştirildi
  - `projects/ops-bot.md` — AGENTS.md kaynak referansı eklendi
- **Ops-Bot files created:**
  - `ops-bot/AGENTS.md` — Proje context'i: stack, mimari, kod stili, güvenlik, deploy checklist
  - `ops-bot/.gitignore` — AGENTS.md ignore kaldırıldı
- **Commits:**
  - ops-bot: `7219f80` feat(ops-bot): add AGENTS.md
  - local: `644ef93` docs(wiki): add agents-md concept page
- **Lint:** 8/10 passing (2 warnings: page size, tag audit)
## [2026-05-03 15:08] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 104 entries

## [2026-05-03 15:26] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 105 entries


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
## [2026-05-03 16:11] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 108 entries


## [2026-05-03 17:04] ingest | ops-bot | d23644e | 6
- Files: A:2 M:4 D:0
- Pages created: —
- Pages updated: [[ops-bot]]
- Pages archived: —
- Diff summary: ops-bot test suite expanded to 57 tests. New files: `tests/test_acp_executor.py` (17 tests), `tests/test_telegram_messages.py` (10 tests). Fixes: `_clean_output` applied to all executor return paths; router caching and logging improved; mock/patch issues resolved in test imports.
- Lint: pending
## [2026-05-03 17:13] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 110 entries


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
## [2026-05-03 18:22] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 112 entries

## [2026-05-03 18:22] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3 (pre-existing: kimi-code-cli.md, ops-bot.md, sec-agent.md)
- Unknown tags: 4 (pre-existing: acp, agents, coding-conventions, configuration)
- Raw existence: 4 (pre-existing: agents-md raw URLs + ops-bot/AGENTS.md path mapping)
- Log size: 112 entries


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
## [2026-05-03 18:54] lint | 6/10
- Orphan pages: 1 ([[adr-003-robotopia-extraction]])
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 6 (acp, agents, coding-conventions, configuration, robotopia-android, webview)
- Raw existence: 5
- Log size: 115 entries

## [2026-05-03 18:54] lint | 6/10
- Orphan pages: 1 ([[adr-003-robotopia-extraction]])
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 116 entries


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
## [2026-05-03 19:02] lint | 6/10
- Orphan pages: 1 ([[adr-003-robotopia-extraction]])
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 4 (acp, agents, coding-conventions, configuration)
- Raw existence: 4
- Log size: 118 entries


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
## [2026-05-03 20:13] lint | 5/10
- Orphan pages: 1 ([[adr-003-robotopia-extraction]])
- Broken links: 0
- Missing from index: 1
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 3
- Unknown tags: 5 (acp, agents, coding-conventions, configuration, memory-game)
- Raw existence: 4
- Log size: 120 entries

## [2026-05-03 21:33] ingest | mathlock-play | fc45d056 | 1 sayfa
- Files: A:0 M:0 D:0 (checkpoint = HEAD, manual update from session context)
- Pages created: —
- Pages updated: [[mathlock-play]]
- Pages archived: —
- Diff summary: Auth mekanizması (DeviceTokenAuthentication + DeviceTokenSigner), backend test suite yapısı (169 test / 10 modül, AuthMixin/ThrottleMixin), Sayı Yolculuğu Activity auth fix (403 → setAuthToken) eklendi.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash

## [2026-05-03 21:31] lint | 4/10
- Orphan pages: 1 ([[adr-003-robotopia-extraction]])
- Broken links: 1
- Missing from index: 1
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 5 (acp, agents, coding-conventions, configuration, memory-game)
- Raw existence: 4
- Log size: 122 entries

## [2026-05-03 21:32] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 5 (acp, agents, coding-conventions, configuration, memory-game)
- Raw existence: 4
- Log size: 123 entries

## [2026-05-03 22:34] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 5 (acp, agents, coding-conventions, configuration, memory-game)
- Raw existence: 4
- Log size: 124 entries

## [2026-05-03 22:49] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 5 (acp, agents, coding-conventions, configuration, memory-game)
- Raw existence: 4
- Log size: 125 entries

## [2026-05-03 23:18] lint | 7/10
- Orphan pages: 0
- Broken links: 0
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 5 (acp, agents, coding-conventions, configuration, memory-game)
- Raw existence: 4
- Log size: 126 entries


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
## [2026-05-04 23:02] lint | 5/10
- Orphan pages: 1 ([[adr-005-ops-bot-acp-sdk-migration]])
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 5
- Log size: 131 entries

## [2026-05-04 23:13] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 5
- Log size: 132 entries


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
## [2026-05-05 21:16] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 5
- Log size: 135 entries

## [2026-05-05 21:16] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 4
- Log size: 136 entries


## [2026-05-05 21:22] ingest | ops-bot | d6ddb0f | 1 sayfa
- Files: R:4 A:19 M:5 D:1
- Pages updated: [[ops-bot]]
- Diff summary: VPS senkronizasyonu — bot/router.py silindi, bot/orchestrator.py + agents/ dizini eklendi, eski ACP client/executor archive/legacy'den bot/'a geri tasindi, telegram.py routing kaldirdi, mimari guncellendi.
- Lint: see next entry
- Revert: git checkout c836b86 -- wiki/
## [2026-05-05 21:25] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 4
- Log size: 138 entries

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

## [2026-05-05 22:18] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 4
- Log size: 141 entries

## [2026-05-05 21:46] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 4
- Log size: 141 entries

## [2026-05-05 22:16] lint | 6/10
- Orphan pages: 0
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 10 (acp, agents, cli, coding-conventions, configuration, json-rpc, memory-game, protocol, refactor, sdk)
- Raw existence: 4
- Log size: 143 entries

2026-05-05 23:37 | adr | adr-006 | github-sync-cross-machine-dev | karar alındı
2026-05-05 23:37 | cleanup | stale-raw-agents | security-leak-removed | sudo-password-jst-temizlendi
2026-05-05 23:37 | cleanup | checkpoint | eksik-checkpointler-eklendi | sec-agent, infrastructure
## [2026-05-05 23:40] lint | 5/10
- Orphan pages: 1 ([[adr-006-github-sync-cross-machine-dev]])
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 13 (acp, agents, cli, coding-conventions, configuration, github, json-rpc, memory-game, protocol, refactor...)
- Raw existence: 6
- Log size: 144 entries

## [2026-05-05 23:41] lint | 5/10
- Orphan pages: 1 ([[adr-006-github-sync-cross-machine-dev]])
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 13 (acp, agents, cli, coding-conventions, configuration, github, json-rpc, memory-game, protocol, refactor...)
- Raw existence: 4
- Log size: 145 entries

## [2026-05-05 23:41] lint | 5/10
- Orphan pages: 1 ([[adr-006-github-sync-cross-machine-dev]])
- Broken links: 1
- Missing from index: 0
- Frontmatter errors: 0
- Stale pages: 0
- Contradictions: 0
- Oversized pages: 4
- Unknown tags: 13 (acp, agents, cli, coding-conventions, configuration, github, json-rpc, memory-game, protocol, refactor...)
- Raw existence: 4
- Log size: 146 entries

