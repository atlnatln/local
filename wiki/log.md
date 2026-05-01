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
