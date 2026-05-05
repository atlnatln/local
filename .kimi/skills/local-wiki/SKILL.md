---
name: local-wiki
description: |
  Persistent LLM Wiki maintainer for /home/akn/local monorepo.
  Handles incremental ingest, query, and lint operations across
  git-tracked and standalone subprojects. Activate when user says
  "wiki ingest", "wiki güncelle", "wiki topla",
  "wiki ekle", "wiki query", "wiki sor", "wiki ara", "wiki lint",
  "wiki kontrol", "wiki tara", "wiki status", "wiki durum", "wiki özet",
  or asks
  about the wiki, documentation, or project knowledge base.
---

# local-wiki (Project-Level)

> **Scope:** Bu skill sadece `/home/akn/local` monorepo'su için çalışır. Project-level override.

Persistent, compounding knowledge base for the `/home/akn/local` VPS monorepo. Active synthesis — not passive RAG. The agent reads source files, writes structured markdown pages, maintains `[[wikilink]]` cross-references, and self-checks for health.

## Commands

| Trigger Phrase | Turkish Alias | Action |
|----------------|---------------|--------|
| `wiki ingest` | `wiki güncelle`, `wiki topla`, `wiki ekle` | Detect changes since last checkpoint, update wiki pages, cross-reference, log |
| `wiki ingest <project>` | `wiki güncelle <proje>` | Ingest only the specified project |
| `wiki query "<question>"` | `wiki sor`, `wiki ara` | Read index → relevant pages → synthesize answer |
| `wiki lint` | `wiki kontrol`, `wiki tara` | Run health check (orphans, broken links, stale pages, tags), append findings to log |
| `wiki status` | `wiki durum`, `wiki özet` | Show last checkpoints, page count, recent log entries |
| `wiki decision add` | `wiki karar ekle`, `adr ekle` | Create a new Architecture Decision Record (ADR), cross-link, update index/log |

## When to Activate

- User types any "wiki ..." phrase (e.g. "wiki ingest", "wiki güncelle", "wiki durum")
- User says "wiki", "belge", "dokumantasyon", "proje dokumanlari"
- User asks questions answerable from accumulated wiki knowledge
- User has just modified code and may need wiki updates
- User says "karar ekle", "adr ekle", "mimari karar", "decision add" → ADR workflow
- User asks "why did we choose X over Y", "neden X yaptık", "X yerine neden Y", "bu kararın gerekçesi" → Query workflow (ADR-aware)
- User proposes a change that may conflict with an existing architectural decision → Proactive ADR Check (CONVENTIONS.md Section 15)

## Orientation Ritual (Before Every Wiki Command)

Always read these files in order:

1. `references/CONVENTIONS.md` — how to behave (git strategy, A/M/D/R, checkpoints, archive rules, ADR vs Concept rules, Proactive ADR Check)
2. `/home/akn/local/wiki/SCHEMA.md` — wiki's structural rules and tag taxonomy
3. `/home/akn/local/wiki/index.md` — what pages exist, what's documented
   > **ADR Snapshot:** While reading `index.md`, pay special attention to the `## Active Decisions` table. Keep a mental snapshot of which ADRs exist and their scope (e.g., adr-001 = monorepo structure). This allows proactive ADR referencing during the session without re-reading the file.
4. Last 5 lines of `/home/akn/local/wiki/log.md` — recent activity

> **ADR Note:** If the user is adding a decision, also read `references/PAGE_TEMPLATES.md` Section 3 (Decision Page Template) before creating the ADR.
> **ADR Query Note:** If the user's question contains decision-related keywords (why, chose, rationale, trade-off, neden, seçtik, karar), apply `Workflow 2` (Query) with `Adım 2 — ADR Öncelikli Arama` activated.

## Progressive Reference Loading

For detailed step-by-step procedures, read `references/WORKFLOW.md`:
- **Ingest workflow** — `references/WORKFLOW.md` section "Workflow: Ingest"
- **Query workflow** — `references/WORKFLOW.md` section "Workflow: Query"
- **Lint workflow** — `references/WORKFLOW.md` section "Workflow: Lint"
- **Status workflow** — `references/WORKFLOW.md` section "Workflow: Status"
- **ADR workflow** — `references/WORKFLOW.md` section "Workflow 5: ADR Ekleme (Decision Add)"

For page templates, read `references/PAGE_TEMPLATES.md`:
- **Project page** — PAGE_TEMPLATES.md section "1. Project Page Template"
- **Concept page** — PAGE_TEMPLATES.md section "2. Concept Page Template"
- **Decision page** — PAGE_TEMPLATES.md section "3. Decision Page Template"
- **Index page** — PAGE_TEMPLATES.md section "4. Index Page Template"

## Tracked Projects

| Project | Git Root | Checkpoint File | Directory |
|---------|----------|-----------------|-----------|
| ops-bot | `ops-bot/.git` | `.checkpoints/ops-bot.sha` | `ops-bot/` |
| webimar | `projects/webimar/.git` | `.checkpoints/webimar.sha` | `projects/webimar/` |
| anka | `/home/akn/local/.git` | `.checkpoints/local.sha` | `projects/anka/` |
| mathlock-play | `/home/akn/local/.git` | `.checkpoints/local.sha` | `projects/mathlock-play/` |
| telegram-kimi | `/home/akn/local/.git` | `.checkpoints/local.sha` | `projects/telegram-kimi/` |
| sayi-yolculugu | `/home/akn/local/.git` | `.checkpoints/local.sha` | `projects/sayi-yolculugu/` |
| infrastructure | `/home/akn/local/.git` | `.checkpoints/local.sha` | `infrastructure/` |

## Script Invocation

Run the linter:
```bash
cd ~/.kimi/skills/local-wiki/ && python3 scripts/wiki_lint.py /home/akn/local/wiki
```

## Writing Conventions (Summary)

Full rules in `references/CONVENTIONS.md`. Key points:
- Factual, concise, structured. No fluff. Every claim traces to a source file.
- Use `[[Wikilink]]` for cross-references. Prefer tables for comparisons, bullets for enumerations.
- Code blocks must include language tag and `// file: path/to/file.ext` comment.
- On conflict: mark `contested: true` — never silently overwrite.
- Deleted sources → mark `[STALE]`, move to `_archive/`, update index.md.
- After every ingest: append to `wiki/log.md`, update `wiki/index.md`.
- On every ingest: refresh `## Recent Commits` section from `git log --oneline -5`.
