---
title: "Kimi Code CLI — Wire Mode"
created: "2026-05-26"
updated: "2026-05-26"
type: concept
tags: [kimi-cli, protocol, json-rpc, integration, api]
related:
  - kimi-code-cli
  - kimi-code-cli-agents
---

# Kimi Code CLI — Wire Mode

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

Kimi Code CLI'nin düşük seviyeli iletişim protokolü. Yapılandırılmış çift yönlü iletişim için kullanılır.

```bash
kimi --wire
```

## Kullanım Alanları

- **Özel UI**: Web, masaüstü veya mobil frontend'ler
- **Uygulama entegrasyonu**: Kimi Code CLI'yi başka uygulamalara gömme
- **Otomatik test**: Agent davranışının programatik testi

::: tip
Basit non-interactive giriş/çıkış için [[kimi-code-cli-print-mode|Print Mode]] daha kolaydır. Wire mode tam kontrol ve çift yönlü iletişim gerektiren senaryolar içindir.
:::

## Protokol

JSON-RPC 2.0 tabanlı protokol. stdin/stdout üzerinden çift yönlü iletişim. Mevcut protokol versiyonu: `1.10`.

### Client → Agent (Request)

| Method | Yön | Tip | Açıklama |
|--------|-----|-----|----------|
| `initialize` | C→A | Request | Handshake — protokol versiyonu, yetenekler, external tool'lar, hook subscription'lar |
| `prompt` | C→A | Request | Kullanıcı input'u gönder, agent turn başlat |
| `replay` | C→A | Request | Session geçmişini tekrar oynat (Wire 1.3+) |
| `steer` | C→A | Request | Aktif turn'a mesaj enjekte et (Wire 1.4+) |
| `set_plan_mode` | C→A | Request | Plan modu durumunu ayarla (Wire 1.4+) |
| `cancel` | C→A | Request | Çalışan turn veya replay'ı iptal et |

### Agent → Client (Notification / Request)

| Method | Yön | Tip | Açıklama |
|--------|-----|-----|----------|
| `event` | A→C | Notification | Agent tarafından emit edilen event'ler (yanıt gerekmez) |
| `request` | A→C | Request | Client'tan yanıt bekleyen istekler (onay, tool çağrısı, soru) |

### Event Tipleri

**Lifecycle:**
- `TurnBegin` / `TurnEnd` — Turn başlangıç/bitiş
- `StepBegin` / `StepInterrupted` / `StepRetry` — Step lifecycle (retry Wire 1.10+)
- `CompactionBegin` / `CompactionEnd` — Context compaction

**İçerik:**
- `ContentPart` — Metin, think, image_url, audio_url, video_url
- `ToolCall` / `ToolCallPart` / `ToolResult` — Tool çağrı ve sonuçları

**Durum:**
- `StatusUpdate` — Context usage, token usage, plan_mode durumu
- `ApprovalResponse` — Onay isteği çözüldü

**Özel:**
- `SubagentEvent` — Subagent event'leri (Wire 1.6+; `parent_tool_call_id`, `agent_id`, `subagent_type`)
- `BtwBegin` / `BtwEnd` — Yan soru (`/btw`) işleme (Wire 1.9+)
- `SteerInput` — Kullanıcı input'u enjekte edildi (Wire 1.5+)
- `PlanDisplay` — Plan modunda plan içeriği gösterimi (Wire 1.7+)
- `HookTriggered` / `HookResolved` — Hook çalıştırma event'leri (Wire 1.7+)

### Request Tipleri

| Tip | Açıklama |
|-----|----------|
| `ApprovalRequest` | Kullanıcı onayı isteği (Wire 1.6+: `source_kind`, `source_id`, `agent_id`, `subagent_type`) |
| `ToolCallRequest` | External tool çağrı isteği (initialize'da kaydedilen tool'lar) |
| `QuestionRequest` | Yapılandırılmış soru isteği (Wire 1.4+; `supports_question` capability gerekli) |
| `HookRequest` | Hook event handler isteği (Wire 1.7+) |

### Hata Kodları

**JSON-RPC 2.0 standart hataları:**

| Kod | Açıklama |
|-----|----------|
| `-32700` | Geçersiz JSON formatı |
| `-32600` | Geçersiz istek |
| `-32601` | Method bulunamadı |
| `-32602` | Geçersiz method parametreleri |
| `-32603` | Dahili hata |

**Uygulama özel hataları:**

| Kod | Açıklama |
|-----|----------|
| `-32000` | Turn zaten devam ediyor / devam eden turn yok / plan mode desteklenmiyor |
| `-32001` | LLM yapılandırılmamış |
| `-32002` | Belirtilen LLM desteklenmiyor |
| `-32003` | LLM servis hatası |

### Capability Negotiation

Client `initialize` isteğinde yeteneklerini bildirir:

```typescript
interface ClientCapabilities {
  supports_question?: boolean      // QuestionRequest handle edebilir
  supports_plan_mode?: boolean     // Plan mode desteği
}
```

Client `supports_question: true` bildirmezse `AskUserQuestion` tool'u LLM'in tool listesinden gizlenir. Benzer şekilde `supports_plan_mode: true` bildirilmezse plan mode tool'ları gizlenir.

### External Tools

`initialize` isteğinde client kendi tool tanımlarını gönderebilir. Agent bu tool'ları çağırdığında `ToolCallRequest` ile client'a istek gönderilir.

```typescript
interface ExternalTool {
  name: string
  description: string
  parameters: JSONSchema
}
```

### Hook Subscription

`initialize` isteğinde client hangi hook event'lerini dinlemek istediğini bildirebilir:

```typescript
interface WireHookSubscription {
  id: string
  event: string           // e.g., 'PreToolUse', 'Stop'
  matcher?: string        // Regex filter, boş = tümü
  timeout?: number        // Client yanıt timeout'u (sn), varsayılan 30
}
```

## Örnek Akış

**1. Handshake:**
```json
{"jsonrpc": "2.0", "method": "initialize", "id": "1", "params": {"protocol_version": "1.10", "client": {"name": "my-ui", "version": "1.0.0"}, "capabilities": {"supports_question": true}}}
```

**2. Prompt:**
```json
{"jsonrpc": "2.0", "method": "prompt", "id": "2", "params": {"user_input": "Hello"}}
```

**3. Event'ler (turn sırasında):**
```json
{"jsonrpc": "2.0", "method": "event", "params": {"type": "TurnBegin", "payload": {"user_input": "Hello"}}}
{"jsonrpc": "2.0", "method": "event", "params": {"type": "StepBegin", "payload": {"n": 1}}}
{"jsonrpc": "2.0", "method": "event", "params": {"type": "ContentPart", "payload": {"type": "text", "text": "Hi!"}}}
```

**4. Approval request (tool çağrısı öncesi):**
```json
{"jsonrpc": "2.0", "method": "request", "id": "3", "params": {"type": "ApprovalRequest", "payload": {"id": "approval-1", "tool_call_id": "tc-1", "sender": "Shell", "action": "run shell command", "description": "Run command `ls`"}}}
```

Client yanıt:
```json
{"jsonrpc": "2.0", "id": "3", "result": {"request_id": "approval-1", "response": "approve"}}
```

**5. Turn sonu:**
```json
{"jsonrpc": "2.0", "method": "event", "params": {"type": "TurnEnd", "payload": {}}}
{"jsonrpc": "2.0", "id": "2", "result": {"status": "finished"}}
```

### DisplayBlock Tipleri

`ToolResult` ve `ApprovalRequest`'in `display` alanında kullanılan görsel blok tipleri:

| Tip | Açıklama |
|-----|----------|
| `brief` | Kısa metin içeriği (`text`) |
| `diff` | Dosya diff'i (`path`, `old_text`, `new_text`) |
| `todo` | Todo listesi (`items`: `title` + `status`) |
| `shell` | Shell komutu (`language`, `command`) |
| (diğer) | Tanınmayan tipler `UnknownDisplayBlock` olarak fallback edilir |

### QuestionResponse Formatı

`QuestionRequest`'e karşılık client `QuestionResponse` döner:

```typescript
interface QuestionResponse {
  request_id: string
  answers: Record<string, string>  // key: soru metni, value: seçilen option label(ları)
}
```

Çoklu seçim (multi-select) durumunda label'lar virgülle ayrılır. Client desteklemiyorsa veya kullanıcı paneli kapatırsa boş `answers: {}` döndürülebilir.

## Kimi Agent (Rust) Wire Server

::: info Deneysel
Kimi Agent şu an deneysel aşamadır. API'ler ve davranışlar gelecek sürümlerde değişebilir.
:::

Kimi Agent (Rust), Kimi Code CLI çekirdeğinin Rust implementasyonudur ve özellikle Wire mode için tasarlanmıştır. Sadece Wire protokol servisi gerekiyorsa daha hafif bir alternatif sunar.

**Özellikler:**
- Tam Wire protokol uyumluluğu (mevcut client'lar değişiklik gerektirmez)
- Daha küçük footprint: Tek statically-linked binary, Python runtime gerekmez
- Daha hızlı başlangıç: Native derleme
- Aynı konfigürasyon: `~/.kimi/config.toml` ve session dizinini kullanır

**Sınırlamalar:**
- Sadece Wire mode (Shell/Print/ACP UI yok)
- Sadece Kimi provider (OpenAI, Anthropic desteklenmez)
- `login`/`logout` yok; API key manuel yapılandırılmalı
- `--prompt` / `--command` desteklenmez
- SSH Kaos desteklenmez
- MCP OAuth depolama yeri farklı: `~/.kimi/credentials/mcp_auth.json` (Python versiyonu `~/.fastmcp/oauth-mcp-client-cache/`)

**Kurulum:**
```bash
# macOS (Apple Silicon)
curl -L https://github.com/MoonshotAI/kimi-agent-rs/releases/latest/download/kimi-agent-aarch64-apple-darwin.tar.gz | tar xz
sudo mv kimi-agent /usr/local/bin/

# Linux (x86_64)
curl -L https://github.com/MoonshotAI/kimi-agent-rs/releases/latest/download/kimi-agent-x86_64-unknown-linux-gnu.tar.gz | tar xz
sudo mv kimi-agent /usr/local/bin/
```

**Kullanım:**
```bash
kimi-agent                          # Wire mode varsayılan
kimi-agent --work-dir /path/to/proj
kimi-agent --continue
kimi-agent --model kimi-for-coding
kimi-agent --yolo
```

## Kaynaklar

- Kimi Code CLI Docs — Wire Mode: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/wire-mode.html
