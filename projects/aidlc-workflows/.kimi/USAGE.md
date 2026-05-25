# Kimi CLI ile Çalışma

Bu proje, [Kimi Code CLI](https://moonshotai.github.io/kimi-cli/) için özel
agent, skill ve subagent tanımları içerir.

## Başlatma

Proje özel agent'ı ile başlatmak için:

```bash
kimi --agent-file .kimi/agent.yaml
```

Kısayol olarak shell alias tanımlayabilirsiniz:

```bash
alias kimi-aidlc="kimi --agent-file .kimi/agent.yaml"
```

## Mevcut Skill'ler

| Skill            | Komut                      | Amaç                                              |
| ---------------- | -------------------------- | ------------------------------------------------- |
| pr-conventions   | `/skill:pr-conventions`    | PR contributor statement ve kurallar              |
| aidlc-rules      | `/skill:aidlc-rules`       | aidlc-rules/ yazım ve güncelleme rehberi          |
| security-scans   | `/skill:security-scans`    | Güvenlik tarayıcılarını çalıştırma                |
| markdown-style   | `/skill:markdown-style`    | Markdown stil ve lint kuralları                   |
| scripts-guide    | `/skill:scripts-guide`     | Evaluator, design-reviewer, traceability          |

Skill'ler otomatik olarak keşfedilir; manuel çağrı isteğe bağlıdır.

## Subagent Kullanımı

Ana agent, `.kimi/subagents/` altındaki rol şablonlarını referans alarak
`Agent` tool'u ile alt görevler başlatabilir. Kimi CLI'de `subagent_type`
parametresi yalnızca built-in türler (`coder`, `explore`, `plan`) için
gerekir. Custom roller için `coder` kullanıp prompt'ta rolü belirtin.

| Rol              | Ne Zaman Kullanılır                                    | Örnek prompt öneki                                     |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------ |
| rule-writer      | aidlc-rules/ dosyalarını düzenlerken                   | "You are a rule-writing specialist for AI-DLC..."      |
| evaluator        | Evaluator testleri çalıştırırken                       | "You are an evaluation runner..."                      |
| design-reviewer  | Design review raporu üretirken                         | "You are a design review runner..."                    |
| security-auditor | Güvenlik taraması yaparken                             | "You are a security audit specialist..."               |

Örnek:

```text
Agent tool ile:
- description: "Run evaluator tests"
- prompt: |
    You are an evaluation runner for the AIDLC framework.
    Navigate to scripts/aidlc-evaluator/ and run all unit tests.
    Report pass/fail status clearly.
- subagent_type: coder
```

## Hooks (Beta)

> ⚠️ Hooks sistemi Beta aşamasındadır. Detaylar ileride değişebilir.

Proje, `.kimi/hooks/` altında kimi-cli lifecycle hook'larını barındırır.
Bu hook'lar `~/.kimi/config.toml`'daki `[[hooks]]` bölümüne eklenerek
aktif hale getirilir.

Mevcut hook'lar:

| Hook            | Event         | Amaç                                                           |
| --------------- | ------------- | ---------------------------------------------------------------|
| `markdown-lint` | `PostToolUse` | Markdown dosyası düzenlendikten sonra otomatik lint çalıştır   |
| `protect-rules` | `PreToolUse`  | Kural dizinlerindeki dosyaları (rename/move/delete) koru       |
| `check-todos`   | `Stop`        | Session bitmeden tamamlanmamış todo varsa uyarı ver            |

Kurulum:

```toml
# ~/.kimi/config.toml
[[hooks]]
event = "PostToolUse"
matcher = "WriteFile|StrReplaceFile"
command = ".kimi/hooks/markdown-lint.sh"
timeout = 30

[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = ".kimi/hooks/protect-rules.sh"
timeout = 10

[[hooks]]
event = "Stop"
command = ".kimi/hooks/check-todos.sh"
timeout = 10
```

## MCP Entegrasyonu

Detaylı kurulum için bkz. `.kimi/MCP.md`.

Hızlı başlangıç:

```bash
# Context7 — aidlc-rules dokümanlarını sorgulamak için
kimi mcp add --transport http context7 https://mcp.context7.com/mcp

# GitHub — PR ve issue yönetimi için
kimi mcp add --transport http --auth oauth github https://mcp.github.com/mcp
```

## Önerilen Kimi Config

Aşağıdaki ayarlar bu projede çalışırken önerilir (`~/.kimi/config.toml`):

```toml
# Tüm skill dizinlerini birleştir (Claude/Codex skills'leri de varsa)
merge_all_available_skills = true

[loop_control]
# Büyük dokümantasyon içeriği için daha fazla bağlam rezerve et
reserved_context_size = 60000
compaction_trigger_ratio = 0.80

[background]
# Evaluator gibi uzun süren görevler için arka plan timeout'u
agent_task_timeout_s = 1800
```

## Dizin Yapısı

```text
.kimi/
├── AGENTS.md              # Kimi CLI'ye özel agent talimatları
├── agent.yaml             # Proje özel custom agent tanımı
├── USAGE.md               # Bu dosya
├── MCP.md                 # MCP entegrasyon rehberi
├── hooks/                 # Lifecycle hook script'leri (Beta)
│   ├── markdown-lint.sh
│   ├── protect-rules.sh
│   └── check-todos.sh
├── skills/
│   ├── pr-conventions/
│   ├── aidlc-rules/
│   ├── security-scans/
│   ├── markdown-style/
│   └── scripts-guide/
└── subagents/
    ├── rule-writer.yaml
    ├── evaluator.yaml
    ├── design-reviewer.yaml
    └── security-auditor.yaml
```
