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
| `timeout` | int | Saniye cinsinden timeout (30–3600). Foreground varsayılan sınırsız, background varsayılan 15 dk |

## Built-in Tools List

Kimi Code CLI'nin tüm built-in tool'ları:

| Tool | Path | Açıklama |
|------|------|----------|
| `Agent` | `kimi_cli.tools.agent:Agent` | Subagent başlat/resume et |
| `AskUserQuestion` | `kimi_cli.tools.ask_user:AskUserQuestion` | Yapılandırılmış sorular sun |
| `SetTodoList` | `kimi_cli.tools.todo:SetTodoList` | Todo listesi yönetimi |
| `Shell` | `kimi_cli.tools.shell:Shell` | Shell komutu çalıştır |
| `ReadFile` | `kimi_cli.tools.file:ReadFile` | Metin dosyası oku (max 1000 satır) |
| `ReadMediaFile` | `kimi_cli.tools.file:ReadMediaFile` | Resim/video dosyası oku (max 100MB) |
| `Glob` | `kimi_cli.tools.file:Glob` | Glob pattern ile dosya/dizin ara |
| `Grep` | `kimi_cli.tools.file:Grep` | Regex ile dosya içeriği ara (ripgrep tabanlı) |
| `WriteFile` | `kimi_cli.tools.file:WriteFile` | Dosya yaz (onay gerekir) |
| `StrReplaceFile` | `kimi_cli.tools.file:StrReplaceFile` | String replacement ile dosya düzenle |
| `SearchWeb` | `kimi_cli.tools.web:SearchWeb` | Web araması yap |
| `FetchURL` | `kimi_cli.tools.web:FetchURL` | URL içeriğini çek |
| `Think` | `kimi_cli.tools.think:Think` | Düşünce sürecini kaydet |
| `SendDMail` | `kimi_cli.tools.dmail:SendDMail` | Gecikmeli mesaj gönder (checkpoint rollback) |
| `EnterPlanMode` | `kimi_cli.tools.plan.enter:EnterPlanMode` | Plan moduna gir |
| `ExitPlanMode` | `kimi_cli.tools.plan:ExitPlanMode` | Planı onaya sun |
| `TaskList` | `kimi_cli.tools.background:TaskList` | Arka plan görevlerini listele |
| `TaskOutput` | `kimi_cli.tools.background:TaskOutput` | Arka plan görev çıktısını al |
| `TaskStop` | `kimi_cli.tools.background:TaskStop` | Arka plan görevini durdur |

### Tool Güvenlik Sınırları

- **Workspace scope:** Dosya okuma/yazma çalışma dizini içinde yapılır. Dışındaki dosyalar için absolute path gerekir.
- **Onay mekanizması:** Shell komutu, dosya yazma/düzenleme, MCP tool çağrısı, arka plan görev durdurma her seferinde onay ister.
- **Hassas dosyalar:** `.env`, SSH private key, cloud credential dosyaları her zaman filtrelendir (hatta `include_ignored=true` olsa bile).
