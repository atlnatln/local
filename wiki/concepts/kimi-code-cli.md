---
title: "Kimi Code CLI"
created: 2026-05-02
updated: "2026-05-10"
type: concept
tags: [kimi-cli, tool, automation, agent, local-wiki]
related:
  - proactive-wiki
  - deployment
  - git-workflow
  - kimi-code-cli-skills
  - kimi-code-cli-agents
  - kimi-code-cli-wire-mode
  - kimi-code-cli-print-mode
  - kimi-code-cli-plugins
  - kimi-code-cli-mcp
  - kimi-code-cli-hooks
sources:
  - raw/articles/kimi-code-cli-docs.md
status: reference
---

# [[Kimi Code CLI]]

Terminal tabanlı AI kodlama asistanı. Projelerde kod yazma, wiki yönetimi, deploy otomasyonu ve agent bazlı görev yönlendirme için kullanılır.

> **TL;DR:** Kimi CLI = terminalden çalışan AI asistanı. Kod yazar, wiki günceller, deploy eder, agent spawn eder. Config: `~/.kimi/config.yaml`. Context: `[[proactive-wiki]]` ile birlikte çalışır.

## İçindekiler

| Bölüm | Açıklama |
|-------|----------|
| [Purpose](#purpose) | Kimi CLI'nin monorepo'daki rolü |
| [Installation](#installation) | Kurulum ve güncelleme |
| [Configuration](#configuration) | `config.yaml`, model, provider, timeout ayarları |
| [Core Operations](#core-operations) | Kod yazma, test, wiki, deploy |
| [Skills](#skills) | `SKILL.md` sistemi ve kullanımı |
| [Code Style](#code-style) | Agent davranış kalıpları |
| [Sub-agents and Agent System](#sub-agents-and-agent-system) | `Agent` tool'u, `agent.yaml`, subagent lifecycle |
| [Customization](#customization) | `.kimi/` dizini, custom skills |
| [Usage in Projects](#usage-in-projects) | Proje bazlı kullanım |
| [Data Locations](#data-locations) | Cache, sessions, logs |

## Purpose

Monorepo ve alt projelerde:
- Kod değişiklikleri, refactor ve yeni özellik
- [[proactive-wiki|Wiki ingest]] ve güncelleme (`wiki topla`, `wiki güncelle`)
- Shell komutları ve otomasyon
- Agent bazlı görev yönlendirme ve routing

## Installation

```bash
# Linux / macOS
curl -LsSf https://code.kimi.com/install.sh | bash

# uv ile (önerilen)
uv tool install --python 3.13 kimi-cli
```

Python 3.12–3.14 destekler. İlk çalıştırmada `/login` ile OAuth yapılandırılır.

## Configuration

### Overrides and Precedence

Config öncelik sırası (yüksekten düşüğe):

1. **Environment variables** — Geçici override'lar, CI/CD
2. **CLI parameters** — Başlangıçta belirtilen parametreler
3. **Configuration file** — `~/.kimi/config.toml` veya `--config-file` ile belirtilen

### CLI Parameters

| Parameter | Açıklama |
|-----------|----------|
| `--config <TOML/JSON>` | Config içeriğini doğrudan geçir |
| `--config-file <PATH>` | Config dosyası yolu (varsayılan yerine) |
| `--model, -m <NAME>` | Model adı belirt |
| `--thinking` | Thinking mode aç |
| `--no-thinking` | Thinking mode kapat |
| `--yolo, --yes, -y` | Tüm operasyonları otomatik onayla |
| `--plan` | Plan modunda başla |
| `--agent <NAME>` | Built-in agent seç (`default`, `okabe`) |
| `--agent-file <PATH>` | Custom agent YAML dosyası yükle |
| `--skills-dir <PATH>` | Ek skill dizini ekle (birden fazla kez kullanılabilir) |

`--config` ve `--config-file` birlikte kullanılamaz.

`--thinking` / `--no-thinking` son session'dan kaydedilen thinking state'i override eder. Belirtilmezse son session'ın durumu kullanılır.

`--plan` yeni session'larda plan modu açar. Mevcut session resume edilirken force plan modu yapar. Config dosyasında `default_plan_mode = true` ile varsayılan plan modu ayarlanabilir.

### Environment Variables

| Provider Tipi | Env Değişkenleri |
|---------------|------------------|
| `kimi` | `KIMI_API_KEY`, `KIMI_BASE_URL`, `KIMI_MODEL_NAME` |
| `openai_legacy` / `openai_responses` | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, … |

Diğer provider tiplerinde env override desteklenmez.

Örnek:
```bash
KIMI_API_KEY="sk-xxx" KIMI_MODEL_NAME="kimi-for-coding" kimi
```

### Config Priority Örneği

Varsayım: `~/.kimi/config.toml` şu şekilde:
```toml
default_model = "kimi-for-coding"

[providers.kimi-for-coding]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = "sk-config"

[models.kimi-for-coding]
provider = "kimi-for-coding"
model = "kimi-for-coding"
max_context_size = 262144
```

| Senaryo | `base_url` | `api_key` | `model` |
|---------|-----------|-----------|---------|
| `kimi` | Config file | Config file | Config file |
| `KIMI_API_KEY=sk-env kimi` | Config file | **Env** | Config file |
| `kimi --model other` | Config file | Config file | **CLI param** |
| `KIMI_MODEL_NAME=kimi-for-coding kimi` | Config file | Config file | **Env** |

## Core Operations

| Mod | Açıklama |
|-----|----------|
| Agent | AI'a gönder, varsayılan mod |
| Shell | Terminal komutları doğrudan (`Ctrl-X`) |
| Plan | Sadece okuma, plan yazma (`Shift-Tab`) |
| Print | Non-interactive, script/CI (`--print`) |

**Onaylar ve YOLO**: Dosya değişikliği ve shell komutları onay ister. `--yolo` tümünü otomatik onaylar.

**Background Tasks**: Uzun komutlar arka planda çalışır (`run_in_background=true`). `/task` ile yönetilir.

**Context**: Session devam ettirme (`--continue`, `-r`), export/import, compact/clear.

## Skills

> Detaylı rehber: [[kimi-code-cli-skills|Skills Sistemi →]]

## Sub-agents and Agent System

> Detaylı rehber: [[kimi-code-cli-agents|Agent ve Sub-agent Sistemi →]]


- **MCP**: Harici araçlar (`kimi mcp add`). Config: `~/.kimi/mcp.json`.
- **Hooks**: Shell komut öncesi/sonrası betikler (beta).
- **Plugins**: `plugin.json` ile çalıştırılabilir araçlar (beta).

## Usage in Projects

| Proje | Kullanım |
|-------|----------|
| `local` monorepo | Wiki ingest, proje yönetimi |
| `ops-bot` | Kod değişiklikleri, agent routing |
| `mathlock-play` | Backend geliştirme |
| `telegram-kimi` | Bot geliştirme |

## Data Locations

| Dizin | İçerik |
|-------|--------|
| `~/.kimi/` | Config, sessions, logs |
| `~/.kimi/sessions/` | Oturum geçmişi |
| `~/.kimi/skills/` | Kullanıcı seviyesi skill'ler |
| `~/.kimi/mcp.json` | MCP sunucu yapılandırması |
| `~/.kimi/plugins/` | Yüklenen plugin'ler |
| `.kimi/skills/` | Proje seviyesi skill'ler |
| `.kimi/hooks/` | Hook betikleri (proje seviyesi) |

## Print Mode

Non-interactive çalışma modu. Script ve otomasyon senaryoları için uygundur.

```bash
# Komut satırından
kimi --print -p "List all Python files in the current directory"

# Stdin'den
echo "Explain this code" | kimi --print
```

Özellikleri:
- **Auto-exit**: İşlem bittiğinde otomatik çıkar
- **Auto-approval**: `--afk` modunu implicit olarak etkinleştirir, tüm tool çağrıları otomatik onaylanır
- **Text output**: AI yanıtları stdout'a yazılır

**`--quiet`** = `--print --output-format text --final-message-only` kısayoludur.

**JSON format:**
```bash
kimi --print -p "Hello" --output-format=stream-json
```

**Exit kodları:**

| Kod | Anlamı |
|-----|--------|
| `0` | Başarılı |
| `1` | Başarısız (tekrar denenmez) — config hatası, auth failure, quota |
| `75` | Başarısız (tekrar denenebilir) — 429 rate limit, 5xx, timeout |

Detaylar: [[kimi-code-cli-print-mode|Print Mode Detayları →]]

## Wire Mode

Kimi Code CLI'nin düşük seviyeli iletişim protokolü. JSON-RPC 2.0 tabanlı, çift yönlü stdin/stdout iletişimi sağlar. Özel UI'ler, IDE entegrasyonları ve otomatik testler için kullanılır.

```bash
kimi --wire
```

**Protokol versiyonu:** `1.10`

**Temel method'lar:** `initialize`, `prompt`, `replay`, `steer`, `set_plan_mode`, `cancel`

**Event tipleri:** `TurnBegin`, `TurnEnd`, `StepBegin`, `StepRetry`, `StatusUpdate`, `ContentPart`, `ToolCall`, `SubagentEvent`, `PlanDisplay`, `HookTriggered`, `HookResolved`

**Request tipleri:** `ApprovalRequest`, `ToolCallRequest`, `QuestionRequest`, `HookRequest`

Detaylar: [[kimi-code-cli-wire-mode|Wire Mode Detayları →]]

## MCP (Model Context Protocol)

Harici araç ve veri kaynaklarıyla güvenli etkileşim için açık protokol. Kimi Code CLI MCP sunucularına bağlanarak yeteneklerini genişletebilir.

```bash
# HTTP sunucu ekle
kimi mcp add --transport http context7 https://mcp.context7.com/mcp

# stdio sunucu ekle
kimi mcp add --transport stdio chrome-devtools -- npx chrome-devtools-mcp@latest

# Listele
kimi mcp list

# Test et
kimi mcp test context7
```

**Config:** `~/.kimi/mcp.json` (diğer MCP client'larla uyumlu)

**Güvenlik:** MCP tool çağrıları da onay ister. YOLO/AFK modunda otomatik onaylanır. Güvenilmeyen kaynaklardan MCP sunucusu kullanmayın.

Detaylar: [[kimi-code-cli-mcp|MCP Detayları →]]

## Hooks (Beta)

Agent yaşam döngüsündeki kritik noktalarda özel komutlar çalıştırma mekanizması. Otomasyon, güvenlik kontrolü, bildirim ve formatlama için kullanılır.

13 desteklenen event:

| Event | Tetikleyici |
|-------|-------------|
| `PreToolUse` | Tool çağrısı öncesi |
| `PostToolUse` | Başarılı tool sonrası |
| `PostToolUseFailure` | Başarısız tool sonrası |
| `UserPromptSubmit` | Kullanıcı input'u işlenmeden önce |
| `Stop` | Agent turn sonunda |
| `StopFailure` | Hata ile turn sonunda |
| `SessionStart` / `SessionEnd` | Session başlangıç/bitiş |
| `SubagentStart` / `SubagentStop` | Subagent başlangıç/bitiş |
| `PreCompact` / `PostCompact` | Context compaction öncesi/sonrası |
| `Notification` | Bildirim iletildiğinde |

**Config:** `~/.kimi/config.toml` içinde `` `[[ hooks ]]` `` array syntax:

```toml
[[ hooks ]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = ".kimi/hooks/protect-env.sh"
timeout = 10
```

**Exit kodları:** `0` = izin ver, `2` = engelle, diğer = izin ver (stderr loglanır).

Detaylar: [[kimi-code-cli-hooks|Hooks Detayları →]]

## Official Plugins

Kimi Code CLI tarafından resmi olarak sağlanan plugin'ler. Mevcutta **kimi-datasource** (Beta) bulunur — finansal piyasalar, makroekonomik göstergeler ve akademik literatür verilerine doğal dil ile erişim sağlar.

```bash
kimi plugin install https://cdn.kimi.com/kimi-code-plugins/kimi-datasource.zip
```

Detaylar: [[kimi-code-cli-official-plugins|Official Plugins →]]

## Plugins (Beta)

Plugin sistemi, AI'a özel çalıştırılabilir araçlar eklemenizi sağlar. Skill'lerden farklı olarak doğrudan tool çağrısı yapılabilir.

**Skill vs Plugin:**

| | Skill | Plugin |
|---|---|--------|
| Amaç | Bilgi tabanlı rehber | Çalıştırılabilir araç |
| Format | `SKILL.md` | `plugin.json` + script'ler |
| Etkileşim | AI okur ve uygular | AI doğrudan çağırır |

**Kurulum:**
```bash
kimi plugin install /path/to/my-plugin
kimi plugin install https://github.com/user/repo.git
kimi plugin list
kimi plugin remove my-plugin
```

**Plugin dizini:** `~/.kimi/plugins/`

Detaylar: [[kimi-code-cli-plugins|Plugins Detayları →]]

## Kaynaklar

- Kimi Code CLI Docs — Configuration Overrides: https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/overrides-and-precedence.html
- Kimi Code CLI Docs — Skills: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html
- Kimi Code CLI Docs — Sub-agents: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/sub-agents.html
- Kimi Code CLI Docs — Print Mode: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/print-mode.html
- Kimi Code CLI Docs — Wire Mode: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/wire-mode.html
- Kimi Code CLI Docs — MCP: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html
- Kimi Code CLI Docs — Hooks: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/hooks.html
- Kimi Code CLI Docs — Plugins: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html

