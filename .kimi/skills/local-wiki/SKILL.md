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
- User says "ace topla" and wiki ingest is needed as the final step of ACE session wrap-up → Ingest workflow (ACE files in `wiki/ace/` are subject to the same lint/rules as other wiki pages)

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
| ace | `/home/akn/local/.git` | `.checkpoints/local.sha` | `wiki/ace/` |

## Script Invocation

Run the linter:
```bash
cd ~/.kimi/skills/local-wiki/ && python3 scripts/wiki_lint.py /home/akn/local/wiki
```

Run the assistant (token optimization):
```bash
# Prepare context package for a specific project
python3 /home/akn/local/scripts/wiki-assistant.py --prepare --project <project> --pretty

# Prepare context package for all projects
python3 /home/akn/local/scripts/wiki-assistant.py --prepare --pretty

# Locate a symbol in source code (LSP)
python3 /home/akn/local/scripts/wiki-assistant.py --locate --file <path> --symbol <name> --pretty
```

## Code Editing Flow — LSP

When the user asks to modify a function/class/section in code:

| Adım | İşlem | Kim Yapar? |
|------|-------|------------|
| 1 | `wiki-assistant.py --locate --file <path> --symbol <name>` | Kimi çağırır |
| 2 | JSON çıktısındaki `range` (satır aralığı) ve `snippet` (içerik) bilgisini kullan | Kimi |
| 3 | Sadece ilgili satır aralığını gör, karar ver, `StrReplaceFile` ile değişikliği uygula | Kimi |
| 4 | Kod değişikliği sonrası `wiki-assistant.py --prepare --project <proje>` ile wiki güncelle | Kimi |

**Desteklenen diller:** Python (Pyright), JavaScript/TypeScript (TypeScript Server), Kotlin (kotlin-language-server).

## Writing Conventions (Summary)

Full rules in `references/CONVENTIONS.md`. Key points:
- Factual, concise, structured. No fluff. Every claim traces to a source file.
- Use `[[Wikilink]]` for cross-references. Prefer tables for comparisons, bullets for enumerations.
- Code blocks must include language tag and `// file: path/to/file.ext` comment.
- On conflict: mark `contested: true` — never silently overwrite.
- Deleted sources → mark `[STALE]`, move to `_archive/`, update index.md.
- After every ingest: append to `wiki/log.md`, update `wiki/index.md`.
- On every ingest: refresh `## Recent Commits` section from `git log --oneline -5`.

## ACE + Wiki Cross-Reference

ACE (`wiki/ace/`) is part of the wiki and follows the same rules:
- ACE playbook pages are linted together with other wiki pages.
- ACE changes are tracked via the `local` checkpoint (`.checkpoints/local.sha`).
- When `ace topla` triggers wiki ingest, use the same assisted ingest flow below.
- The `ace-memory` skill owns lesson extraction / prune / stats; this skill owns the wiki ingest step.

## Wiki Ingest Flow — Asistanlı (Optimizasyonlu)

Bu akış, mevcut 9 adımlık ingest sürecini **wiki-assistant.py** programıyla birleştirir. Amaç: Kimi'nin okuduğu toplam satır sayısını %70-80 azaltmak.

### Ne Zane Asistan Kullanılır?

Kullanıcı `wiki topla`, `wiki ingest`, `wiki güncelle` veya `ace topla`'nın wiki ingest adımında **her zaman** bu akışı izle.

### Yeni Akış (10 Adım)

| Adım | İşlem | Kim Yapar? |
|------|-------|------------|
| 1 | Checkpoint SHA'ları oku (`wiki/.checkpoints/*.sha`) | Kimi |
| 2 | Git diff çalıştır (`git diff --name-status <checkpoint>..HEAD`) | Kimi |
| **3** | **Asistanı çalıştır: `wiki-assistant.py --prepare`** | **Kimi çağırır, Asistan çalıştırır** |
| 4 | Asistan çıktısını (JSON) analiz et. Diff boş mu kontrol et. | Kimi |
| 5 | Asistanın `changed_files[].snippets` çıktısını oku. Sadece snippet'leri ve yapısal özetleri değerlendir. | Kimi |
| 6 | Asistanın `wiki_targets[].sections` çıktısını kullan. **Sadece ilgili bölümleri** oku, sayfanın tamamını değil. | Kimi |
| 7 | Çapraz referansları yenile. Asistan `wiki_targets` listesinden candidate'ları bil. | Kimi |
| 8 | Lint çalıştır: `wiki_lint.py` | Kimi (veya Asistan çağırır) |
| 9 | Checkpoint'leri güncelle | Kimi |
| 10 | `.pending` temizle, kullanıcıya özet rapor ver | Kimi |

### Asistan Çıktısı (JSON) Nasıl Kullanılır?

Asistan şu yapıda bir JSON döner:

```json
{
  "project": "sayi-yolculugu",
  "diff_summary": {"added": 1, "modified": 3, "deleted": 0},
  "changed_files": [
    {
      "path": "projects/sayi-yolculugu/js/game.js",
      "status": "M",
      "snippets": { "type": "structure", "line_count": 200, "header": "...", "structure": [...] }
    }
  ],
  "wiki_targets": [
    {
      "page": "wiki/projects/sayi-yolculugu.md",
      "relevant_sections": ["JavaScript", "Oyun Motoru"],
      "sections": {
        "type": "sections",
        "matched": {
          "## Oyun Motoru": { "level": 2, "start_line": 45, "content": "..." }
        }
      }
    }
  ],
  "index_needs_update": true,
  "log_needs_update": true
}
```

**Kimi'nin kullanımı:**
- `diff_summary` → kullanıcıya özet raporun ilk cümlesi
- `changed_files[].snippets` → dosyanın ne içerdiğini anlamak için. **Sayfanın tamamını okuma.** Sadece snippet yeterli.
- `wiki_targets[].sections.matched` → wiki sayfasının **sadece ilgili bölümünü** oku. Eşleşme yoksa `type: "outline"` gelir, o zaman sayfa yapısını (başlık listesi) görürsün.
- `index_needs_update` / `log_needs_update` → true ise index.md ve log.md güncellenmeli

### Fallback (Asistan Çalışmazsa)

Eğer `wiki-assistant.py` hata verirse veya çıktı üretmezse:
1. Hatayı kullanıcıya söyle
2. Klasik akışa dön: Checkpoint → Git diff → Dosyaları oku → Wiki güncelle → Lint → Checkpoint güncelle
3. Asistan olmadan devam et

### Cache Mekanizması (L2 Cache)

Asistan `wiki/.assistant-index.json` dosyasında wiki sayfalarının başlık yapısını cache'ler.

- **Cache hit:** Dosya değişmemişse (mtime eşleşiyorsa) headings listesi cache'ten gelir. Dosya **açılmaz**.
- **Cache miss:** Dosya değişmişse veya ilk çalıştırmadaysa headings parse edilir, cache güncellenir.
- **Manuel temizlik:** `rm wiki/.assistant-index.json` ile cache silinir, bir sonraki çalıştırmada yeniden oluşur.

### Token Tasarrufu Hedefi

| Metrik | Klasik Akış | Asistanlı Akış | Hedef |
|--------|-------------|----------------|-------|
| Okunan toplam satır | ~3000-5000 | ~500-800 | %70-80 azalma |
| ReadFile tool call | 15-25 | 5-8 | %60 azalma |

