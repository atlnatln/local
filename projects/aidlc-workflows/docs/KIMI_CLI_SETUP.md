# AI-DLC Kimi CLI Adaptasyonu — Kurulum ve Kullanım

Bu doküman, AI-DLC metodolojisinin Kimi Code CLI ile nasıl kullanılacağını açıklar.

## Hızlı Başlangıç

### 1. Yeni Proje Oluşturma

```bash
# 1. Yeni proje dizini
mkdir ~/projeler/tavukcum-ai && cd ~/projeler/tavukcum-ai

# 2. AI-DLC rule'larını ve Kimi config'ini kopyala
cp -r ~/aidlc-workflows/aidlc-rules ./
cp -r ~/aidlc-workflows/.kimi ./

# 3. Kimi CLI'yi başlat
kimi
```

### 2. Bootstrap (İlk Oturum)

Prompt:
> "Yeni proje: Tavukçum AI. AI-DLC workflow'u başlat."

Kimi (default agent):
1. `aidlc-docs/` dizin yapısını oluşturur
2. `aidlc-state.md` ve `audit.md`'yi başlatır
3. Workspace taraması yapar (greenfield/brownfield)
4. `requirements-analysis`'a başlar

### 3. Execution (Master Orchestrator)

Bootstrap tamamlandıktan sonra:

```bash
kimi --agent-file .kimi/agents/master-orchestrator.yaml
```

Master otomatik olarak:
1. `aidlc-state.md`'yi okur
2. Sıradaki stage'i belirler
3. Uygun sub-agent'ı (inception/construction/operations) çağırır
4. State'i atomik olarak günceller

## Agent Mimarisi

| Agent | Görevi | Çalışma Dizini |
|-------|--------|----------------|
| **master-orchestrator** | Phase koordinasyonu, state yönetimi | `aidlc-docs/` (state + audit) |
| **inception-coder** | Planlama, DDD, requirements | `aidlc-docs/inception/` |
| **construction-coder** | Kod + test (full-stack) | `src/{unit-name}/` + `aidlc-docs/construction/` |
| **operations-coder** | Docker, deployment | `infrastructure/` + `aidlc-docs/operations/` |

## Context Yönetimi

- **Yeni phase = yeni instance** — Her `Agent()` çağrısı temiz context ile başlar (`resume` kullanılmaz)
- **Context %70** → `/compact` (checkpoint sonrası)
- **Context %80** → Session sonlandır, `aidlc-state.md`'den devam et

## Hook Sistemi

`~/.kimi/config.toml`'a ekle:

```toml
[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = ".kimi/hooks/domain-guard.sh"
timeout = 10
```

Bu hook cross-domain yazmayı engeller.

## Dizin Yapısı

```
proje-koku/
├── aidlc-docs/              # AI-DLC kalıcı bellek (sadece markdown)
│   ├── aidlc-state.md
│   ├── audit.md
│   ├── inception/
│   └── construction/
│       └── {unit-name}/
│           └── code/        # Kod özetleri (gerçek kod src/'de)
├── src/                     # Gerçek kaynak kod
│   └── {unit-name}/
├── infrastructure/          # Docker, deployment
├── .kimi/
│   └── agents/              # AI-DLC agent tanımları
└── aidlc-rules/             # AI-DLC rule'ları (orijinal)
```

## Sınırlamalar

- Max 4 paralel background task (varsayılan)
- Sub-agent'lar kendi alt ajanlarını çağıramaz (max 2 seviye: Root → Sub)
- Hook fail-open: Script bulunamazsa yazma engellenmez
