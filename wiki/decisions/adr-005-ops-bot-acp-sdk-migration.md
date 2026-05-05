---
type: decision
name: adr-005-ops-bot-acp-sdk-migration
title: "Ops-Bot ACP Client'ını Resmi SDK'ya Geçirmek"
description: |
  Custom ACP client/executor yerine resmi `agent-client-protocol` Python SDK'sını
  kullanma kararı. Tip güvenliği, process lifecycle, session management ve
  maintenance overhead avantajları nedeniyle.
created: 2026-05-04
updated: 2026-05-04
decision_date: 2026-05-04
tags: [decision, adr, ops-bot, acp, sdk, refactor]
status: Active
deciders: akn
related:
  - ops-bot
  - acp-protocol
  - kimi-code-cli
---

# adr-005-ops-bot-acp-sdk-migration: Ops-Bot ACP Client'ını Resmi SDK'ya Geçirmek

## Context

Ops-bot, kimi-cli'yi ACP (Agent Client Protocol) modunda çalıştırarak Telegram üzerinden AI asistanı sunuyor. Mevcut implementasyon `bot/acp_client.py` (custom JSON-RPC stdio client) ve `bot/acp_executor.py` (session lifecycle) üzerine kurulu.

Mevcut stack'te karşılaşılan sorunlar:

1. **`_tool_call_count` hiç resetlenmiyordu** — İlk session'da 15'i aşınca sonraki tüm session'lar otomatik cancel ediliyordu.
2. **`/iptal` ACP process'ini öldürmüyordu** — `cancel()` + `_sessions.pop()` yapıyordu ama kimi-cli subprocess zombie kalıyordu.
3. **Boş yanıt handling'i eksikti** — ACP'den `{"result":{"content":""}}` gelince kullanıcıya hiçbir şey göstermiyordu, sadece footer kalıyordu.
4. **Tip güvenliği yok** — `dict` üzerinden manual key access, kimi-cli güncellemelerinde kırılma riski.
5. **Health check yok** — Process'in sağlıklı olup olmadığını anlamanın yolu yok.
6. **Streaming buffer primitive** — `list[str]` + manual join; thinking block ayrımı regex ile yapılıyor.

Bu sorunlar 2026-05-04'te bir IP analizi sırasında bot'un tamamen kilitlenmesine yol açtı.

## Decision

**Karar:** Ops-bot'un ACP katmanını (`acp_client.py` + `acp_executor.py`) resmi `agent-client-protocol` Python SDK'sına (`acp` paketi, PyPI) kademeli olarak geçireceğiz.

**Fazlar:**

| Faz | Süre | İçerik |
|-----|------|--------|
| Faz 1 | 2 gün | `SdkAcpExecutor` adapter'ı yazılır, mevcut `AcpExecutor` ile aynı interface'i korur |
| Faz 2 | 1 gün | `telegram.py` async adaptasyonu — `run_in_executor` yerine direkt `await` |
| Faz 3 | 1 gün | `PermissionBroker` entegrasyonu — riskli komut filtresi SDK katmanına taşınır |
| Faz 4 | 1 gün | Health check + auto-retry — `list_sessions()` ile periyodik kontrol |

**Agent spec yükleme stratejisi:**
SDK'nın `new_session` method'unda `agentFile` parametresi yok. Ancak kimi-cli `--agent-file` CLI flag'i ACP modunda çalışıyor. Deneme sonucu: `kimi --agent-file agents/master/agent.yaml acp` komutuyla agent spec doğru şekilde yükleniyor ve subagent'lar aktif oluyor.

## Consequences

### ✅ Olumlu

- **Tip güvenliği:** Pydantic modeller (`acp.schema`) ile runtime validation
- **Process lifecycle:** `spawn_agent_process` context manager — process otomatik temizlenir
- **Session management:** `new`, `load`, `resume`, `fork`, `close`, `list` method'ları
- **Streaming ayrımı:** `AgentMessageChunk` vs `AgentThoughtChunk` — thinking temizliği native
- **Tool call tracking:** `ToolCallTracker` — production-tested, sayaç bug'ı çözülür
- **Maintenance:** SDK her ACP release'e uyumlu, upstream tarafından sürdürülür
- **Test edilebilirlik:** Typed mock'lar ve fixture'lar daha kolay

### ⚠️ Riskler / Maliyetler

- **4-5 günlük refactor** — mevcut testlerin bir kısmı değişebilir
- **SDK bağımlılığı** — upstream breaking change riski (mitigasyon: pip pin + test)
- **Async migration** — `loop.run_in_executor` kaldırılacak, bazı sync kısımlar adaptasyon gerektirebilir
- **Kimi-cli `closeSession` eksikliği** — `session_capabilities.close=None`, cleanup hala `cancel` + process kill ile yapılacak
- **Hybrid dönem:** Eski ve yeni executor bir süre paralel durabilir (teknik borç)

### 🔄 Tarafsız / Notlar

- SDK'ya geçiş tamamlanana kadar mevcut custom client'a **acil hotfix'ler** uygulandı (2026-05-04): `_tool_call_count` reset, `/iptal` process kill, boş yanıt guard, reader loop EOF cleanup.
- Bu hotfix'ler geçiş sırasında kararlılığı korur.
- SDK deneme branch'i (`feature/acp-sdk-exploration`) korunacak.

## Alternatives Considered

### Alternatif 1: Mevcut custom client'ı güçlendir

- **Açıklama:** `_tool_call_count` bug'ını fix'le, health check ekle, typed dataclass'lar kullan, process lifecycle'ı iyileştir.
- **Neden reddedildi:** Aynı sonuca ulaşmak için SDK'nin yaptığı her şeyi yeniden implemente etmek gerekir. JSON-RPC transport, Pydantic validation, session accumulator, permission broker — hepsi wheel reinvention. SDK zaten production'da test edilmiş ve kimi-cli, Zed, Gemini CLI gibi araçlar tarafından kullanılıyor.

### Alternatif 2: MCP (Model Context Protocol) kullan

- **Açıklama:** Anthropic'in MCP standardına geçiş.
- **Neden reddedildi:** MCP = agent ↔ tool/resource. ACP = client ↔ agent. Ops-bot bir **client** (Telegram entegrasyonu), kimi-cli bir **agent**. ACP doğru abstraction seviyesi. MCP, kimi-cli'nin tool call'larını yönetmek için değil, client'ın agent'ı orchestrate etmesi için kullanılır.

### Alternatif 3: Başka bir AI agent'ına geç

- **Açıklama:** Hermes, Devin veya Claude Code gibi ACP-compatible başka bir agent kullan.
- **Neden reddedildi:** Kimi-cli zaten ops-bot'un core AI motoru. Sadece **iletişim protokol katmanı** değişiyor, agent'ın kendisi değil.

## Status

**Mevcut Durum:** `Active`

> Son durum güncellemesi: 2026-05-04
