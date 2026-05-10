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
| `.kimi/skills/` | Proje seviyesi skill'ler |

## Kaynaklar

- Kimi Code CLI Docs — Configuration Overrides: https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/overrides-and-precedence.html
- Kimi Code CLI Docs — Skills: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html
- Kimi Code CLI Docs — Sub-agents: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/sub-agents.html

