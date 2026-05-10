---
title: "Kimi Code CLI — Skills Sistemi"
created: "2026-05-02"
updated: "2026-05-10"
type: concept
tags: [kimi-cli, tool, automation]
related:
  - kimi-code-cli
  - kimi-code-cli-agents
---

# Kimi Code CLI — Skills Sistemi

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

## Skills

### Skill Discovery (Keşif Sırası)

**Built-in** → paket içi (`kimi-cli-help`, `skill-creator`).

**User-level** (tüm projelerde geçerli):
- **Brand group** (birbirini dışlar, öncelikli):
  1. `~/.kimi/skills/`
  2. `~/.claude/skills/`
  3. `~/.codex/skills/`
- **Generic group** (birbirini dışlar):
  1. `~/.config/agents/skills/` (önerilen)
  2. `~/.agents/skills/`

İki grup bağımsız aranır, sonuçlar merge edilir. Aynı isimde skill varsa brand group önceliklidir.

`merge_all_available_skills = true` config ile tüm brand dizinleri yüklenir (öncelik: kimi > claude > codex). Generic group etkilenmez.

**Project-level** (sadece o proje):
- Brand group: `.kimi/skills/` → `.claude/skills/` → `.codex/skills/`
- Generic group: `.agents/skills/`

Ek dizin: `--skills-dir /path/to/skills` (birden fazla kez kullanılabilir, auto-discovered dizinleri override eder).

> `KIMI_SHARE_DIR` skill arama yollarını etkilemez. Skill'ler cross-tool yetenek uzantılarıdır (Kimi CLI, Claude, Codex ile uyumlu).

### Creating a Skill

Skill oluşturmak için sadece bir `SKILL.md` dosyası yeterlidir:

```
skills-dir/
└── my-skill/
    ├── SKILL.md          # Zorunlu
    ├── scripts/          # Opsiyonel
    ├── references/       # Opsiyonel
    └── assets/           # Opsiyonel
```

**SKILL.md formatı** — YAML frontmatter + Markdown:
```markdown
---
name: code-style
description: My project's code style guidelines
---

## Code Style

In this project, please follow these conventions:
- Use 4-space indentation
- Variable names use camelCase
```

**Frontmatter alanları:**

| Alan | Açıklama | Zorunlu |
|------|----------|---------|
| `name` | 1-64 karakter, küçük harf/rakam/tire; atlanırsa dizin adı | Hayır |
| `description` | 1-1024 karakter; atlanırsa "No description provided." | Hayır |
| `license` | Lisans adı/dosya | Hayır |
| `compatibility` | Ortam gereksinimleri, max 500 karakter | Hayır |
| `metadata` | Ek key-value | Hayır |

**Best practices:**
- `SKILL.md` 500 satırın altında tut
- Detaylı içerik `scripts/`, `references/`, `assets/` dizinlerine taşı
- Göreceli yollar kullan
- Adım adım talimatlar, input/output örnekleri, edge case açıklamaları

### Flow Skills

`type: flow` frontmatter + Mermaid/D2 diyagramı ile multi-step workflow tanımlanır.

```markdown
---
name: code-review
description: Code review workflow
type: flow
---

```mermaid
flowchart TD
A([BEGIN]) --> B[Analyze code changes]
B --> C{Is code quality acceptable?}
C -->|Yes| D[Generate report]
C -->|No| E[List issues]
E --> B
D --> F([END])
```
```

**D2 formatı:**
```
BEGIN -> B -> C
B: Analyze existing code
C: Review if design doc is detailed enough
C -> B: No
C -> D: Yes
D: Start implementation
D -> END
```

**Çalıştırma:**
- `/flow:<name>` — Flow'u otomatik çalıştırır (BEGIN → END)
- `/skill:<name>` — Sadece SKILL.md içeriğini prompt olarak gönderir (flow çalıştırılmaz)

Flow diyagramlarında bir `BEGIN` ve bir `END` node zorunludur. Decision node'lar `<choice>branch name</choice>` output'u bekler.

## Skills vs Plugins

| Mekanizma | Amaç | Format |
|-----------|------|--------|
| **Skills** | Bilgi tabanlı rehberler | `SKILL.md` — AI okur ve uygular |
| **Plugins** | Çalıştırılabilir araçlar | `plugin.json` — AI doğrudan tool çağrır |

Skills: kod stili, workflow, best practice tanımları için.
Plugins: script, API call, database query wrapper'ları için.
