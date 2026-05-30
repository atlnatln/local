---
name: ace-memory
description: |
  Adaptive Cross-session Experience (ACE) playbook manager.
  Handles lesson extraction, playbook updates, and confidence tracking.
  Activate when user says "ace topla", "ace öğren", "ace learn",
  "ace ders ekle", "ace add", "ace playbook", "ace unut", "ace prune",
  "ace validate", "ace durum", "ace status", "ace ingest", "ace güncelle",
  or asks about cross-session memory, learning from mistakes,
  or preventing repeated errors.
---

# ace-memory (Project-Level)

> **Scope:** `/home/akn/local` monorepo'su. Project-level override.

Cross-session memory system. Lessons learned are persisted in `wiki/ace/` and automatically loaded on session start via `AGENTS.md`.

## Commands

| Trigger Phrase | Turkish Alias | Action |
|----------------|---------------|--------|
| `ace topla` | `ace ingest`, `ace güncelle` | **Oturum sonu toplu işlem:** ders çıkar + prune + stats + wiki ingest |
| `ace learn` | `ace öğren`, `ace ders çıkar` | Extract lesson from current session |
| `ace add` | `ace ders ekle`, `ace ekle` | Manually add a lesson |
| `ace playbook` | `ace göster`, `ace listele` | Show current playbook |
| `ace prune` | `ace unut`, `ace temizle` | Archive low-confidence lessons |
| `ace validate ID` | `ace doğrula ID` | Increase confidence of a lesson |
| `ace status` | `ace durum`, `ace özet` | Show stats and recent lessons |

## When to Activate

- User types any "ace ..." phrase
- User says "ace topla", "ace güncelle", "ace ingest"
- User says "unutma", "bir daha yapma", "bundan ders çıkar"
- User says "geçen sefer şunu yanlış yapmıştık"
- User asks "why did we choose X" and the answer is in playbook
- User says "oturum bitti", "ders çıkaralım", "bugün ne öğrendik"

## Orientation Ritual

Always read before any ace command:
1. `wiki/ace/playbook.md` — general lessons
2. `wiki/ace/<current-project>.md` — project-specific lessons (if applicable)

## Workflow 1: Ace Topla (Oturum Sonu Toplu İşlem) — PRIMARY

**Bu workflow, diğer tüm workflow'ları birleştirir.** Kullanıcı "ace topla" dediğinde sırayla:

### Step 1 — Oturum Özeti Çıkar
Oturum geçmişini analiz et:
- Bu oturumda hangi projelerde çalışıldı?
- Kaç dosya değiştirildi?
- Hata döngüsü var mıydı?
- Yeni öğrenilen bir pattern/anti-pattern var mı?

### Step 2 — Ders Çıkar (Workflow 1-A)
Eğer oturumdan çıkarılabilir bir ders varsa:
- Ders taslağı oluştur (aşağıdaki Extract Lesson workflow'nu kullan)
- Kullanıcıya göster, onay al
- Onaylanırsa `scripts/ace-curator.py --learn` ile kaydet

Örnek komut:
```bash
python3 /home/akn/local/scripts/ace-curator.py \
    --learn \
    --title "Ders başlığı" \
    --context "Senaryo açıklaması" \
    --rule "Ne yapılacağı" \
    --rationale "Neden" \
    --source "dosya/yol.py" \
    --scope "proje-adı" \
    --type "pattern"
```

### Step 3 — Prune (Workflow 1-B)
`scripts/ace-curator.py --prune --dry-run` çalıştır:
- Confidence < 0.30 olanları listele
- 6+ ay güncellenmemişleri listele
- Kullanıcıya göster, onay al
- Onaylanırsa `--prune` ile arşivle

### Step 4 — Stats ve Review (Workflow 1-C)
`scripts/ace-curator.py --stats` çalıştır:
- Toplam kaç ders?
- Proje başına dağılım?
- Ortalama confidence?

### Step 5 — Wiki Ingest
ACE dosyaları değişmişse wiki ingest çalıştır:
```bash
python3 /home/akn/local/scripts/wiki-assistant.py --prepare --project ace
```

> **Not:** `ace-curator.py topla` bu adımı otomatik çalıştırır. Manuel kullanımda yukarıdaki komut çalışır.
>
> Fallback (asistan çalışmazsa):
> ```bash
> cd /home/akn/local && python3 scripts/wiki-assistant.py --prepare
> ```

### Step 6 — Commit Öner
Eğer playbook değişmişse:
```bash
git add wiki/ace/
git commit -m "docs(ace): update playbook — $(date +%Y-%m-%d)"
```

> **Not:** `ace topla` = `wiki topla`'nın ACE versiyonu. Kullanıcı tek komutla tüm ACE bakımını halleder.

## Workflow 2: Extract Lesson (ace learn / ace öğren)

### Step 1 — Gather Context
Ask user (or infer from session history):
- What was requested?
- What was the first attempt?
- What went wrong?
- What was the correct solution?
- Which project / file / function?

### Step 2 — Draft Lesson
Draft in this format:
```markdown
## Ders NNN: Title
**Confidence:** 0.80
**Created:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**Validations:** 0
**Source:** file/path.py
**Scope:** project-name
**Type:** pattern|anti-pattern|workflow|pitfall

### Context
...

### Rule
...

### Rationale
...

### Examples
#### ✅ Do
```

#### ❌ Don't
```

### Related
```

### Step 3 — Curator Approval
Run `scripts/ace-curator.py --learn --draft ...` to get next available ID.
Show draft to user. If approved, save. If rejected, edit.

### Step 4 — Wiki Ingest
After saving, run wiki ingest for `wiki/ace/` directory.

## Workflow 3: Manual Add (ace add / ace ders ekle)

User provides lesson directly. Same as Workflow 2 but skip Step 1.

## Workflow 4: Prune (ace prune / ace unut)

Run `scripts/ace-curator.py --prune --dry-run` first.
Show what will be archived. Ask user for confirmation.
Then run without `--dry-run`.

## Workflow 5: Validate (ace validate / ace doğrula)

Run `scripts/ace-curator.py --validate <ID>`.
This increases confidence by +0.05.

## Confidence Rules

- New lesson: 0.80
- Validated (test passed / user approved): +0.05
- Invalidated (error loop / wrong): -0.15
- Not updated for 6 months: -0.10
- Source code changed (git diff): -0.20
- Archive threshold: < 0.30
