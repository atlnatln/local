---
title: "SCHEMA"
created: "2026-05-01"
updated: "2026-05-02"
type: index
tags: [meta, guide]
related: []
---

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
│   ├── git-workflow.md
│   ├── proactive-wiki.md
│   └── ...
├── decisions/
│   └── adr-NNN-kisa-baslik.md  # Mimari karar kayitlari (ADR)
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
`ops-bot` `webimar` `anka` `mathlock-play` `robotopia-android` `telegram-kimi` `sayi-yolculugu` `infrastructure` `sec-agent`

Project tags bind a note to a specific codebase or service.

### Stack
`django` `nextjs` `react` `docker` `nginx` `systemd` `android` `flutter` `telegram-bot` `python` `kotlin` `git` `html5` `javascript` `webview` `kimi-cli` `tool` `cli` `json-rpc` `sdk`

Technology tags describe the toolchain a note touches.

### Concepts
`concept` `deployment` `ssl` `monitoring` `networking` `database` `caching` `security` `education` `logging` `agent` `ai` `acp` `agents` `memory-game` `protocol`

Domain tags classify the subject matter independent of any project.

### Meta
`meta` `overview` `decision` `adr` `todo` `stale` `archived` `needs-review` `ai-generated` `guide` `automation` `local-wiki` `git-hook` `certbot` `reference` `coding-conventions` `configuration` `github` `refactor` `sync` `vps`

Lifecycle tags track note maturity and provenance.

**Tag usage rules:**
- Every note must carry at least one project or concept tag.
- Meta tags are optional and may be added or removed as a note evolves.
- Tags are written in frontmatter arrays; never use `#hashtag` syntax in body text.

## Page Size Policy

Lint (`wiki_lint.py`) enforces type-aware line limits. Reference pages are exempt.

| `type` | Max Lines | Rationale |
|--------|-----------|-----------|
| `project` | 400 | Project pages accumulate many subsystems over time |
| `concept` | 350 | Concept pages should be focused; split into sub-concepts if exceeded |
| `decision` | 200 | ADRs must be concise and decision-focused |
| `index` / `log` | 500 | Catalog and chronological pages are inherently long |
| `reference` (via `status`) | exempt | Canonical reference material (e.g., CLI docs, API guides) |

**When a page approaches its limit:**
1. Add a **Table of Contents** (TOC) after the main heading — use anchor links to every `##` section
2. Add a **TL;DR** block right after the page title (2-3 sentences summarizing the entire page)
3. Prefer **wikilink cross-references** over inline repetition — link to sub-pages instead of expanding
4. If a single section grows >100 lines, extract it to a dedicated sub-page and link back

## Update Policy

| Concern | Rule |
|---------|------|
| Who | Primarily AI ingest agents; human edits for decisions and corrections |
| When | After every meaningful code change; at minimum before VPS maintenance |
| How | Markdown files are plain text; edit in-place, append to `log.md`, update frontmatter `updated` |
| Validation | Prefer wikilinks over URLs; all `\[\[PageName\]\]` targets must correspond to existing `.md` files |

## Wikilink Convention

Use double-bracket syntax for internal links:

```markdown
\[\[PageName\]\]           → links to PageName.md
\[\[PageName#Section\]\]   → links to heading within PageName.md
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
| `related` | Yes | Array of `\[\[PageName\]\]` wikilinks to related pages |
| `sources` | No | Paths to raw archived source files |
| `contested` | No | Set `true` when conflicting info exists |
| `status` | No | Page state: `active`, `stale`, `archived`, `needs-review`, `reference`. For `type: decision`: `Active`, `Superseded`, `Deprecated` |
| `supersedes` | No | For ADR only. Wikilink to the decision this replaces. Example: `adr-XXX-old-title` |
| `superseded_by` | No | For ADR only. Wikilink to the decision that replaces this. Example: `adr-YYY-new-title` |