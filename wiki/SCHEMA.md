# SCHEMA

## Wiki Purpose

`local-wiki` is the living documentation system for `/home/akn/local/`, a VPS monorepo housing multiple projects under unified infrastructure. It captures architecture decisions, deployment procedures, system configuration, and operational knowledge using Markdown + wikilink semantics.

## Directory Structure

```
~/local/wiki/
├── SCHEMA.md           # This file — structure, taxonomy, conventions
├── index.md            # Master content catalog
├── log.md              # Append-only chronological log
├── system-overview.md  # High-level architecture map
├── projects/
│   ├── index.md        # Project catalog
│   ├── ops-bot.md      # Telegram operations bot — Python, systemd
│   ├── webimar.md      # Agriculture platform — Django + Next.js + React
│   ├── anka.md         # Sector analysis platform — Django + Next.js
│   ├── mathlock-play.md # Android math game + Django backend
│   ├── telegram-kimi.md # Telegram Kimi bot
│   └── infrastructure.md # Shared VPS infra
├── concepts/
│   ├── deployment.md
│   ├── django-nextjs-pattern.md
│   ├── ssl-certbot.md
│   ├── multi-web-project-system.md
│   └── ...
├── decisions/
│   ├── adr-001-vps-rename-local.md
│   ├── adr-002-mathlock-systemd.md
│   └── ...
├── raw/
│   └── articles/       # Unprocessed source material
├── _archive/           # Soft-deleted pages
└── .checkpoints/       # Per-project SHA tracking
    ├── local.sha
    ├── ops-bot.sha
    └── webimar.sha
```

## Tag Taxonomy

All tags are flat strings. Namespaces below are organizational conventions only.

### Projects
`ops-bot` `webimar` `anka` `mathlock-play` `telegram-kimi` `sayi-yolculugu` `infrastructure`

Project tags bind a note to a specific codebase or service.

### Stack
`django` `nextjs` `react` `docker` `nginx` `systemd` `android` `flutter` `telegram-bot` `python`

Technology tags describe the toolchain a note touches.

### Concepts
`concept` `deployment` `ssl` `monitoring` `networking` `database` `caching` `security`

Domain tags classify the subject matter independent of any project.

### Meta
`meta` `overview` `decision` `adr` `todo` `stale` `archived` `needs-review` `ai-generated`

Lifecycle tags track note maturity and provenance.

**Tag usage rules:**
- Every note must carry at least one project or concept tag.
- Meta tags are optional and may be added or removed as a note evolves.
- Tags are written in frontmatter arrays; never use `#hashtag` syntax in body text.

## Update Policy

| Concern | Rule |
|---------|------|
| Who | Primarily AI ingest agents; human edits for decisions and corrections |
| When | After every meaningful code change; at minimum before VPS maintenance |
| How | Markdown files are plain text; edit in-place, append to `log.md`, update frontmatter `updated` |
| Validation | Prefer wikilinks over URLs; all `[[PageName]]` targets must correspond to existing `.md` files |

## Wikilink Convention

Use double-bracket syntax for internal links:

```markdown
[[PageName]]           → links to PageName.md
[[PageName#Section]]   → links to heading within PageName.md
```

Wikilinks are resolved case-insensitively. File names are `kebab-case.md`; link targets use `TitleCase` or `kebab-case` and are normalized at render time.

## Frontmatter Schema

```yaml
---
# Required
title: "Human-readable title"
created: "2025-05-01"   # YYYY-MM-DD
updated: "2025-05-01"   # YYYY-MM-DD
type: concept           # concept | project | decision | index | log
tags: [deployment, docker, ops-bot]
related: []             # List of plain page names (wikilinks stay in body)

# Optional
sources: ["raw/articles/source-file.md"]  # Raw source paths
contested: false       # true if content has conflicting info
status: "active"       # active | stale | archived | needs-review
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Display title; keep under 60 characters |
| `created` | Yes | Creation date (YYYY-MM-DD) |
| `updated` | Yes | Last update date (YYYY-MM-DD) |
| `type` | Yes | Content category; drives template selection |
| `tags` | Yes | Array of taxonomy tags; minimum one project or concept |
| `related` | Yes | Array of [[PageName]] wikilinks to related pages |
| `sources` | No | Paths to raw archived source files |
| `contested` | No | Set `true` when conflicting info exists |
| `st