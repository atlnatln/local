---
type: concept
name: acp-protocol
title: "Agent Client Protocol (ACP)"
description: |
  Editor/Client ↔ AI Agent arası standart iletişim protokolü.
  JSON-RPC 2.0 over stdio. Kimi CLI, Hermes, Devin, Kiro CLI gibi
  araçlar tarafından desteklenir. Ops-bot'un Telegram entegrasyonu
  ile kimi-cli arasındaki haberleşme katmanı.
created: 2026-05-04
updated: 2026-05-04
tags: [concept, acp, protocol, agent, cli, json-rpc]
related:
  - ops-bot
  - kimi-code-cli
  - deployment
sources:
  - raw/articles/acp-sdk-probe.py
---

# [[acp-protocol]]

**Agent Client Protocol (ACP)**, editor/IDE/shell gibi client'ların AI agent'ları (örn. kimi-cli) ile standart bir protokol üzerinden iletişim kurmasını sağlayan açık bir endüstri standardıdır. LSP (Language Server Protocol)'nin editor ↔ language server iletişimine yaptığı şeyi, ACP editor ↔ AI agent iletişimi için yapar.

## Tanım

ACP, JSON-RPC 2.0 over stdio transport kullanır. Client bir subprocess olarak agent'ı başlatır, stdin/stdout üzerinden yapılandırılmış mesajlar gönderir ve alır. Sessions, tool calls, permission requests ve streaming updates bu protokol üzerinden yönetilir.

## Bağlam

Bu sistemde ACP şu projelerde kullanılıyor:

- [[ops-bot]] — Bot, kimi-cli'yi ACP modunda (`kimi acp`) çalıştırır. `bot/acp_client.py` ve `bot/acp_executor.py` ile ACP JSON-RPC mesajlarını yönetir.
- [[kimi-code-cli]] — ACP server modu: `kimi acp` komutu ile ACP-compatible agent olarak çalışır.

## Uygulama

### Ops-Bot'taki ACP Stack

```python
# file: ops-bot/bot/acp_client.py
"""ACP (Agent Client Protocol) JSON-RPC stdio client for kimi-cli."""
```

Ops-bot'ta ACP üç katmanda uygulanır:

| Katman | Dosya | Görev |
|--------|-------|-------|
| Transport | `bot/acp_client.py` | JSON-RPC 2.0 over stdio, threading, select |
| Session | `bot/acp_executor.py` | Session-per-user, buffer, tool call limit, cancel |
| Telegram | `bot/telegram.py` | Async message handler, ACK, footer, chunking |

### Kimi CLI ACP Implementasyonu

```bash
# ACP modunda başlat
kimi --agent-file agents/master/agent.yaml --skills-dir .kimi/skills acp
```

Kimi CLI 1.40.0'da ACP yetenekleri:
- `load_session: True`
- `prompt_capabilities: embedded_context, image`
- `session_capabilities: list, resume`
- Eksik: `close: None`, `fork: None`

### Resmi Python SDK

```bash
pip install agent-client-protocol
```

| Modül | Görev |
|-------|-------|
| `acp.schema` | Pydantic modeller — tip güvenliği |
| `acp.client` | `ClientSideConnection` — async JSON-RPC |
| `acp.contrib` | `SessionAccumulator`, `ToolCallTracker`, `PermissionBroker` |
| `acp.spawn_agent_process` | `asynccontextmanager` — subprocess lifecycle |

## Karşılaştırma: Custom Client vs SDK

| Özellik | Custom (`bot/acp_client.py`) | ACP SDK |
|---------|------------------------------|---------|
| Transport | Manuel `threading` + `select` | `asyncio` native |
| Tip güvenliği | `dict` + manual key access | Pydantic `acp.schema` |
| Session lifecycle | `new_session`, `cancel` (2 method) | `new`, `load`, `resume`, `fork`, `close`, `list` |
| Health check | ❌ Yok | ✅ `list_sessions()` |
| Streaming buffer | `self._buffer: list[str]` | `SessionAccumulator` + `AgentThoughtChunk` ayrımı |
| Tool call tracking | `self._tool_call_count` | `ToolCallTracker` |
| Permission handling | Manuel `if/else` + regex | `PermissionBroker` + typed `PermissionOption` |
| Process lifecycle | `subprocess.Popen` manual kill | `spawn_agent_process` context manager |

## ACP Protokol Mesaj Örnekleri

### Initialize

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "id": 1,
  "params": {
    "protocolVersion": 1,
    "clientInfo": {"name": "ops-bot", "version": "2.0.0"}
  }
}
```

### Prompt

```json
{
  "jsonrpc": "2.0",
  "method": "session/prompt",
  "id": 2,
  "params": {
    "sessionId": "f5e918b5-ef99-49f4-87d1-2728199c3c95",
    "prompt": [{"type": "text", "text": "Merhaba"}]
  }
}
```

### Session Update (Notification)

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "update": {
      "sessionUpdate": "agent_message_chunk",
      "content": {"text": "Merhaba!"}
    }
  }
}
```

## İlişkili Kavramlar

- [[ops-bot]] — ACP client'ı kullanan Telegram bot
- [[kimi-code-cli]] — ACP server olarak çalışan AI kodlama asistanı
- [[mcp-routing]] — MCP (Model Context Protocol) = agent ↔ tool/resource. ACP = client ↔ agent. İkisi farklı protokoller.

## Kaynaklar

| Kaynak | Tür | Açıklama |
|--------|-----|----------|
| `scripts/acp_sdk_probe.py` | Script | SDK deneme script'i — kimi-cli 1.40.0 ile test edildi |
| `bot/acp_client.py` | Kaynak | Ops-bot custom ACP client implementasyonu |
| `bot/acp_executor.py` | Kaynak | Session lifecycle ve streaming buffer yönetimi |
| https://agentclientprotocol.github.io/python-sdk/ | Dokümantasyon | Resmi Python SDK |
| https://pypi.org/project/agent-client-protocol/ | PyPI | `agent-client-protocol` paketi |
