---
title: "Kimi Code CLI — Agent ve Sub-agent Sistemi"
created: "2026-05-02"
updated: "2026-05-10"
type: concept
tags: [kimi-cli, tool, automation, agent]
related:
  - kimi-code-cli
  - kimi-code-cli-skills
---

# Kimi Code CLI — Agent ve Sub-agent Sistemi

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

## Sub-agents and Agent System

### Built-in Agents

| Agent | Amaç | Aktif Tool'lar |
|-------|------|----------------|
| `default` | Genel kullanım | Agent, AskUserQuestion, SetTodoList, Shell, ReadFile, ReadMediaFile, Glob, Grep, WriteFile, StrReplaceFile, SearchWeb, FetchURL, EnterPlanMode, ExitPlanMode, TaskList, TaskOutput, TaskStop |
| `okabe` | Deneysel | `default` + SendDMail |

Seçim: `kimi --agent default` veya `kimi --agent okabe`

### Custom Agent Files

YAML formatında. `kimi --agent-file /path/to/my-agent.yaml`

```yaml
version: 1
agent:
  name: my-agent
  system_prompt_path: ./system.md
  tools:
    - "kimi_cli.tools.shell:Shell"
    - "kimi_cli.tools.file:ReadFile"
```

**Inheritance (extend):**
```yaml
version: 1
agent:
  extend: default
  system_prompt_path: ./my-prompt.md
  exclude_tools:
    - "kimi_cli.tools.web:SearchWeb"
```

**Alanlar:**

| Alan | Açıklama | Zorunlu |
|------|----------|---------|
| `extend` | Miras alınacak agent (`default` veya relative path) | Hayır |
| `name` | Agent adı | Evet (miras yoksa) |
| `system_prompt_path` | System prompt dosyası (agent dosyasına göre relative) | Evet (miras yoksa) |
| `system_prompt_args` | System prompt'a özel argümanlar (merge edilir) | Hayır |
| `tools` | Tool listesi (`module:ClassName`) | Evet (miras yoksa) |
| `exclude_tools` | Hariç tutulacak tool'lar | Hayır |
| `subagents` | Subagent tanımları | Hayır |

### System Prompt Variables

System prompt Markdown template'dir. `${VAR}` ve Jinja2 `{% include %}` destekler.

| Değişken | Açıklama |
|----------|----------|
| `${KIMI_NOW}` | Şu anki zaman (ISO format) |
| `${KIMI_WORK_DIR}` | Çalışma dizini |
| `${KIMI_WORK_DIR_LS}` | Çalışma dizini dosya listesi |
| `${KIMI_AGENTS_MD}` | Birleştirilmiş `AGENTS.md` içeriği (proje root'tan çalışma dizinine kadar, `.kimi/AGENTS.md` dahil). Detaylar: bkz. [[agents-md]] |
| `${KIMI_SKILLS}` | Yüklenen skill listesi |
| `${KIMI_ADDITIONAL_DIRS_INFO}` | `--add-dir` ile eklenen dizinler |

Özel argümanlar: `system_prompt_args:` ile tanımlanır, `${MY_VAR}` olarak kullanılır.

```yaml
agent:
  system_prompt_args:
    MY_VAR: "custom value"
```

### Defining Subagents

Agent dosyasında `subagents:` bölümü ile tanımlanır:

```yaml
version: 1
agent:
  extend: default
  subagents:
    coder:
      path: ./coder-sub.yaml
      description: "Handle coding tasks"
    reviewer:
      path: ./reviewer-sub.yaml
      description: "Code review expert"
```

Subagent dosyası da standart agent formatıdır, genellikle ana agent'dan miras alır:

```yaml
# coder-sub.yaml
version: 1
agent:
  extend: ./agent.yaml
  system_prompt_args:
    ROLE_ADDITIONAL: |
      You are now running as a subagent...
```

### Built-in Subagent Types

| Tip | Amaç | Aktif Tool'lar |
|-----|------|----------------|
| `coder` | Genel yazılım mühendisliği | Shell, ReadFile, Glob, Grep, WriteFile, StrReplaceFile, SearchWeb, FetchURL |
| `explore` | Hızlı read-only codebase keşfi | Shell, ReadFile, Glob, Grep, SearchWeb, FetchURL (yazma yok) |
| `plan` | Implementasyon planlama ve mimari tasarım | ReadFile, Glob, Grep, SearchWeb, FetchURL (Shell yok, yazma yok) |

**Kural:** Tüm subagent tipleri `Agent` tool'unu kullanamaz (nesting yasak). Sadece root agent `Agent` tool'una sahiptir.

### How Subagents Run

`Agent` tool'u ile başlatılır. İzole context, kendi context history'sini korur. `subagents/<agent_id>/` altında session dizininde saklanır. Resume edilebilir.

Avantajları:
- İzole context, ana agent conversation history'sini kirletmez
- Birden fazla bağımsız görev paralel işlenebilir
- Hedeflenmiş system prompt'lar
- Persistent instance'lar çoklu çağrı arasında context korur

**Agent Tool Parametreleri:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `description` | string | Kısa görev açıklaması (3-5 kelime) |
| `prompt` | string | Detaylı görev tanımı |
| `subagent_type` | string | Built-in tip: `coder`, `explore`, `plan` (varsayılan: `coder`) |
| `model` | string | Opsiyonel model override |
| `resume` | string | Mevcut instance ID ile resume et |
| `run_in_background` | bool | Arka planda çalıştır (varsayılan: false) |
