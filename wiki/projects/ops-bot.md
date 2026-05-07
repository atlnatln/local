---
title: "Ops-Bot"
created: 2026-05-01
updated: 2026-05-07
type: project
tags: [ops-bot, python, telegram-bot, systemd, security, acp, kimi-cli]
related:
  - infrastructure
  - deployment
  - sec-agent
  - telegram-kimi
sources:
  - raw/articles/ops-bot-readme.md
  - raw/articles/ops-bot-deploy-script.md
  - raw/articles/ops-bot-bot-config-py
  - raw/articles/ops-bot-deploy-sh
  - raw/articles/ops-bot-security-agent-md
  - raw/articles/ops-bot-tests-conftest-py
  - raw/articles/ops-bot-tests-test-router-py
  - raw/articles/ops-bot-tests-test-integration-py
  - raw/articles/ops-bot-bot-acp-sdk-client-py
  - raw/articles/ops-bot-bot-acp-sdk-executor-py
  - raw/articles/ops-bot-scripts-acp-sdk-probe-py
  - raw/articles/ops-bot-tests-sdk-test-acp-sdk-executor-py
  - raw/articles/ops-bot-tests-test-telegram-messages-py
---

# [[Ops-Bot]]

Telegram üzerinden VPS operasyonlarını yöneten bot. **V2 rewrite** sonrası 2493 satırlık monolitik `agent.py` yerine modüler mimariye geçti.

## Purpose

Kullanıcıların Telegram üzerinden VPS'ye komut göndermesini, ajanlara soru yönlendirmesini ve güvenlik olaylarını izlemesini sağlar. Düşük gürültü bildirim profili ile mesaj kutusunu doldurmadan yüksek sinyal olayları iletir.

## Stack

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | Python 3.12, `python-telegram-bot` |
| Entry Point | `bot.py` — V2 entry point (eski `agent.py` yerine) |
| ACP Executor | `bot/acp_sdk_executor.py` — resmi ACP SDK (`agent-client-protocol`) ile session persistence |
| ACP Client | `bot/acp_sdk_client.py` — SDK-native `OpsBotAcpClient` protocol implementasyonu |
| Legacy ACP | `bot/acp_executor.py` + `bot/acp_client.py` — JSON-RPC 2.0 over stdio (legacy, hala aktif) |
| Telegram Handler | `bot/telegram.py` — message routing + reply formatting + markdown sanitize |
| Orchestrator | `bot/orchestrator.py` — Agent lifecycle: spawn, cache, resume, cleanup |
| Agent System | `agents/` — descriptor_loader, manager, state, process, YAML descriptors |
| Router | ~~`bot/router.py`~~ — [REMOVED] Tüm routing LLM/master seviyesine bırakıldı (2026-05-05) |
| Memory | `bot/memory.py` — SQLite conversation_memory + V2 agent state |
| MCP Tools | `mcp/tools/` — docker, db, system tool definitions |
| Models | `models/registry.py` — model name resolution |
| Skills | `skills/*/SKILL.md` — 4 skill (docker-troubleshooting, nginx-routing, postgres-query, security-reporting) |
| Security | `sec-agent/` — collector/engine/actions/config |
| Test | `tests/` — pytest + pytest-asyncio, 67+ test (SDK tests `--ignore=tests/sdk`) |
| Deploy | `./deploy.sh` → VPS `systemd` servisi |

## Entry Points

| Dosya | Görev |
|-------|-------|
| `ops-bot/bot.py` | Ana Telegram bot uygulaması (19 satır entry point) |
| `ops-bot/bot/telegram.py` | Telegram message handler, HTTP timeout (30s), ACK, context footer, markdown code-block sanitize |
| `ops-bot/bot/orchestrator.py` | Agent lifecycle: spawn, cache, resume, cleanup. Kimi-cli Agent tool'una karşılık |
| `ops-bot/bot/acp_sdk_executor.py` | SDK-based ACP session yönetimi, accumulator snapshot, tool call limit, context usage |
| `ops-bot/bot/acp_sdk_client.py` | `OpsBotAcpClient` — permission broker, file I/O sandboxing, terminal execution, accumulator/tracker |
| `ops-bot/bot/acp_executor.py` | Legacy ACP session yönetimi, tool call streaming (JSON-RPC over stdio) |
| `ops-bot/bot/acp_client.py` | Legacy JSON-RPC 2.0 ACP client (initialize 30s, session/new 30s, default 60s) |
| `ops-bot/bot/memory.py` | Legacy SQLite conversation memory; context persistence kimi-cli `~/.kimi/sessions/` tarafından sağlanır |
| `ops-bot/bot/config.py` | Env-based config (TELEGRAM_TOKEN, ALLOWED_USER_ID, timeout'lar 180-600s, TEST_MODE) |
| `ops-bot/.env.test` | Test ortamı çevre değişkenleri (`TEST_MODE=true`, `ALLOWED_USER_ID=123456789`) |
| `ops-bot/pytest.ini` | pytest yapılandırması (asyncio_mode=auto, slow marker, `--ignore=tests/sdk`) |
| `ops-bot/CHANGELOG.md` | Değişiklik kaydı (Keep a Changelog formatı) |
| ~~`ops-bot/bot/router.py`~~ | ~~BotRouter~~ — [REMOVED] Explicit `@agent` parse kaldırıldı (2026-05-05) |
| ~~`ops-bot/router/hybrid.py`~~ | ~~HybridRouter~~ — [REMOVED] |
| ~~`ops-bot/router/embedding.py`~~ | ~~TF-based cosine similarity~~ — [REMOVED] |
| ~~`ops-bot/agents/descriptor_loader.py`~~ | ~~YAML descriptor okuma~~ — [REMOVED] |
| ~~`ops-bot/agents/manager.py`~~ | ~~Agent lifecycle~~ — [REMOVED] |
| `ops-bot/tests/conftest.py` | pytest fixtures: mocked Telegram Application + Update factories + `sdk_executor` fixture |
| `ops-bot/tests/test_router.py` | 22 unit test: `extract_explicit_agent()` regex parser + `BotRouter.select()` |
| `ops-bot/tests/test_acp_client.py` | 7 unit test: ACP protocol (`ApprovalRequest`/`ToolCallRequest`), permission auto-approve/reject |
| `ops-bot/tests/test_acp_executor.py` | 17 unit test: ACP executor `_clean_output`, session lifecycle, cancel/reset, tool call buffering |
| `ops-bot/tests/sdk/test_acp_sdk_executor.py` | 10 unit test: SDK-based executor init, diagnostics, health check, close, run (timeout/empty/error), reset |
| `ops-bot/tests/test_telegram_messages.py` | 10 unit test: Telegram message handler formatting, error replies, notification parsing, chunking, footer |
| `ops-bot/tests/test_integration.py` | 8 integration/E2E test: smoke + real kimi-cli ACP subprocess |
| `ops-bot/scripts/acp_sdk_probe.py` | Standalone ACP SDK probe script — initialize, session, prompt, accumulator snapshot |
| `ops-bot/deploy.sh` | VPS deploy script'i (package/git modları) |
| `ops-bot/systemd/ops-bot.service` | systemd unit dosyası |

## Mimari (Tek Evren — Kimi-CLI Native)

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Telegram User  │────▶│ bot/telegram │────▶│bot/orchestrator │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                      │
                           ┌──────────────────────────┘
                           ▼
                   ┌─────────────────┐
                   │bot/acp_sdk_executor│
                   └─────────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ kimi-cli    │
                   │ (acp mode)  │
                   │  master     │
                   │  agent.yaml │
                   └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        @docker      @security      @monitor
        (subagent)   (subagent)     (subagent)
        tools: [Shell, ReadFile, Glob, Grep]
```

### Agent Sistemi (V2)

`agents/descriptors/*.yaml` + `agents/prompts/*.md` ile tanımlı:

- `ops-database-agent` — PostgreSQL/sorgu işlemleri
- `ops-docker-agent` — Container yönetimi
- `ops-monitor-agent` — Sistem izleme (CPU, RAM, disk)
- `ops-incident-agent` — 502/500 gibi olay müdahalesi
- `ops-security-agent` — Güvenlik (explain + observe birleşik, bot detection, risk skor, IP karar açıklama)
- `ops-fix-agent` — Otomatik düzeltme önerileri
- `ops-ip-query-agent` — IP/trafik analizi
- `ops-forensic-agent` — Adli inceleme
- `ops-seo-agent` — SEO/performans

**Routing (2026-05-05):** `bot/router.py` kaldırıldı. Tüm mesajlar `agent_name=None` olarak `master` ajanına yönlendirilir. Routing kararları tamamen kimi-cli master agent (`agents/master/agent.yaml`) seviyesinde verilir. Python katmanı sadece Telegram entegrasyonu, ACP session yönetimi ve orchestrator lifecycle yapar.

### Orchestrator

`bot/orchestrator.py` agent lifecycle'ı yönetir:

- `AgentStateStore` — State persistence (resume için)
- `AgentManager` — Agent process spawn/cache/cleanup
- `handle_message()` — AgentProcess.handle() çağrısına eşdeğer, kimi-cli sub-agent çağrısı
- `_load_tools_for_agent()` — Descriptor'daki tools listesini döndürür
- `get_stats()` — Agent manager istatistikleri

### ACP Executor (SDK-Based)

`bot/acp_sdk_executor.py` her kullanıcı için uzun ömürlü ACP session yönetir. Artık resmi `agent-client-protocol` SDK kullanır:

- `_ensure_connection(agent_name)` — `acp.spawn_agent_process()` ile persistent ACP process başlatır, agent değişiminde connection recycle eder
- `_get_or_create_session()` — `conn.new_session()` ile session oluşturur, `user_id:agent_name` key ile reuse eder
- `run()` → `conn.prompt()` → `SessionAccumulator.snapshot()` sonucunu toplar; her `run()` başlangıcında accumulator reset + tool_call_count = 0
- `cancel()` / `reset_session()` — session cancel + dictionary cleanup
- `reset_all_sessions()` — Tüm session'ları iptal eder, ACP process'i kill eder, connection cleanup (zombie process önlemi)
- `get_diagnostics()` — ACP ready state, PID, session count, tool call count, context usage döndürür (troubleshooting)
- `health_check()` — `conn.list_sessions()` ile hızlı canlılık kontrolü
- `close()` — Synchronous close, process kill + state reset

**Önemli not:** ACP modu `--yolo`/`--afk` flag desteklemez. Tool kullanımı ACP server tarafında `toolCall`/`toolResult` loop'u ile yönetilir.

**Accumulator pattern (2026-05-05):** `acp.contrib.SessionAccumulator` ACP session update'lerini toplar. `run()` sonunda `snapshot()` ile `agent_messages` listesinden metin parçaları birleştirilir. Prompt sonrası 1 saniyelik `asyncio.sleep(1.0)` trailing session_update chunk'larının gelmesi için bekler.

**Tool call koruması:** 15'ten fazla ardışık tool call otomatik session cancel eder. `run()` başlangıcında sayaç sıfırlanır, log'a `Tool call count=N` yazılır.

**Timeout sonrası cleanup (2026-05-05):** `asyncio.TimeoutError` yakalandığında session explicit `cancel` edilir ve stale session dictionary'den silinir. Böylece bir sonraki mesaj taze session alır.

**Boş yanıt guard'ı (2026-05-04):** Accumulator snapshot sonucu boş kalırsa kullanıcıya `⚠️ Bot boş yanıt üretti... /iptal yazıp tekrar deneyin` mesajı gösterilir.

**Timeout yapılandırması:**

| Ajan | Maksimum Timeout |
|------|------------------|
| Default | 90s |
| ops-database-agent | 90s |
| ops-incident-agent, ops-docker-agent, ops-monitor-agent, ops-security-agent, ops-ip-query-agent, ops-forensic-agent, ops-seo-agent | 120s |
| ops-fix-agent | 180s |

**Tek master agent (2026-05-03):** `agents/master/agent.yaml` tek kaynak. Subagent'lar `subagents/` dizininde, kimi-cli `Agent` tool'u ile çağrılır. Her subagent kendi `tools` listesiyle yetkilendirilmiştir (güvenlik katmanı 1).

### Güvenlik Kontrolleri (2026-05-05)

Güvenlik üç katmandır:

1. **Birinci katman — Kimi-CLI Agent Spec:** Her subagent'ın `tools` listesiyle sadece gerekli tool'lar aktiftir. `ops-security-agent`'ta `WriteFile` yoksa hiçbir dosya yazılamaz.
2. **İkinci katman — OpsBotAcpClient:** `bot/acp_sdk_client.py` `request_permission` method'unda riskli komut filtrelemesi:
   - **Reject edilen kalıplar:** `git`, `rm`, `mv`, `cp`, `chmod`, `chown`, `sudo`, `mkfs`, `dd`, `wget`, `curl`, `nc`, `netcat`, `nmap`
   - **Approve edilenler:** Güvenli read-only ve yönetim komutları
   - Tool call başlığı ilk 200 karaktere bakılarak karar verilir
   - **Word-boundary matching:** `re.findall(r"\b\w+\b", ...)` ile tam kelime eşleşmesi — `"perform"` gibi substring'ler yanlış reject yapmaz
3. **Üçüncü katman — File I/O Sandboxing:** `write_text_file` ve `read_text_file`:
   - **Path sandboxing:** `os.path.realpath()` ile repo root (`Config.REPO_ROOT`) dışına çıkış engellenir
   - **Sensitive file block:** `.env`, `.env.production`, `.env.local`, `id_rsa`, `id_ed25519`, `authorized_keys` dosyalarına erişim engellenir
4. **Terminal execution:** `create_terminal` `subprocess.run()` ile gerçek komut çalıştırır, `cwd=Config.REPO_ROOT`, `timeout=30s`

### Context Persistence

- Session-per-user: her kullanıcı kendi session ID'sine sahip
- Session ID'ler `self._sessions` dict'te tutulur
- kimi-cli `~/.kimi/sessions/<md5>/<session_id>/context.jsonl`'da context saklar
- Kimi-cli native context persistence — bot restart sonrası devam eder
- **Context/token kullanım takibi:** `session_update` handler'ı `usage_update` type'ını yakalar; `get_context_usage()` ve footer'da gösterilir

## Servisler

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `ops-bot.service` | systemd | Ana Telegram bot |
| `sec-agent.service` | systemd | Sürekli güvenlik değerlendirme döngüsü |
| `sec-agent.timer` | systemd timer | 3 dk'da bir `sec-agent-once.service` |
| `sec-agent-metrics.service` | systemd | Prometheus metrikleri (`:9101`) |
| `ops-bot-weekly-security-report.timer` | systemd timer | Haftalık özet |
| `ops-bot-critical-alert.timer` | systemd timer | Günde 1 kez 08:00'de günlük özet (eski: 3 saatte bir kritik eşik) |

## Deploy

```bash
cd ops-bot/
./deploy.sh              # package modu (default): tar.gz oluştur, scp et
./deploy.sh --mode git   # git modu: VPS'te git pull + restart
```

Deploy script'i **ortam tespiti** yapar (`is_vps` — `/home/akn/vps` dizini varsa VPS'tedir):
- **Local'den:** SSH multiplexing ile tek TCP bağlantı üzerinden `scp`/`ssh` kullanır (UFW rate-limit koruması)
- **VPS'ten:** `ssh`/`scp` fonksiyonları yerel `bash`/`cp` ile override edilir; doğrudan `/home/akn/vps/ops-bot/` altına yazar

Deploy akışı:
1. Ortam tespiti (`is_vps`) → local SSH veya VPS direct mode seçimi
2. `tar.gz` paketi oluşturma (package modu) veya `git push` (git modu)
3. VPS'te `setup.sh` çalıştırma
4. `systemctl restart ops-bot`

### VPS Dizin Yapısı

| Dizin | Amaç |
|-------|------|
| `/home/akn/vps/ops-bot/` | Deploy hedefi — kod, venv, config |
| `/home/akn/local/ops-bot/` | Geliştirme/git kaynağı |

> **Not:** systemd servis dosyası `WorkingDirectory`, `ExecStart` ve çevre değişkenlerinde `/home/akn/vps/ops-bot/` yolunu kullanır. Deploy script dosyaları da `/home/akn/vps/ops-bot/` altına çıkarır. `local` dizini yalnızca geliştirme ve git kaynağıdır; canlı servis `vps` dizininden çalışır.

## Security (sec-agent)

Detaylı mimari ve operasyon bilgisi: bkz. [[sec-agent]].

Özet:
- `sec-agent/` alt yapısı: collectors, engine, actions, config
- VPS üretimi `/opt/sec-agent/` altında timer tabanlı one-shot çalışır
- Guardrail korumalı otomatik block / ratelimit / alert
- Günlük AI yorumlu rapor: bkz. [[security-ai-reporting]]
- `ops-bot-critical-alert.service` `OPS_BOT_CRITICAL_STATE_PATH` env ile state dosyası yolunu sabitler (VPS dizinine yazar)

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `/iptal` | Tüm ACP session'larını discard eder, ACP process'ini öldürür, hafızayı temizler, yeni sohbet başlatır |
| `/end` | Legacy hafızayı temizler; ACP session'ı korunur |
| `/durum` | Bot ve ACP durumunu gösterir: ACP ready/PID, session sayısı, tool call sayacı, context usage |
| `/model` | Aktif modeli göster veya değiştir |
| `/start` | Bot tanıtımı ve komut listesi (agent listesi kaldırıldı, 2026-05-05) |

## Troubleshooting

### Boş Yanıt (Bot Cevap Vermiyor)

**Belirti:** Bot ACK gönderiyor ama yanıt gelmiyor veya `⚠️ Bot boş yanıt üretti.`

**Neden:**
1. **ACP process kilitlenmesi:** Process returncode non-None olabilir, `_ensure_connection` yeni process başlatır
2. **Zombie subprocess:** Önceki `/iptal` process'i kapanmamış olabilir

**Çözüm:**
```bash
# Session'ları ve process'leri temizle
rm -rf ~/.kimi/sessions/*
pkill -f "kimi-cli.*acp"

# Bot'u restart
sudo systemctl restart ops-bot
```

### ACP Prompt Timeout

**Belirti:** `⏱️ Zaman aşımı: ACP yanıt vermedi.`

**Neden ve Çözüm:**
1. **ACP prompt timeout:** `bot/acp_sdk_executor.py`'de `min(Config.KIMI_TIMEOUT_DEFAULT, 90)` kullanılıyor.
   - *Çözüm:* `.env`'deki değerleri kontrol et: `OPS_BOT_KIMI_TIMEOUT_*_SECONDS`
2. **python-telegram-bot HTTP timeout:** `telegram.py`'de `.read_timeout(30).write_timeout(30).connect_timeout(10)`
3. **ACP client/SDK timeout:** initialize 30s, session/new 30s, default request 60s

**Kalıcı çözüm:**
```bash
# Session'ları temizle
rm -rf ~/.kimi/sessions/*

# Bot'u restart
sudo systemctl restart ops-bot
```

### Servis `activating (auto-restart)` döngüsünde

**Belirti:** `systemctl status ops-bot` `Result: resources` gösterir, journalctl'de `Application started` log'u yok.

**Neden:** `/home/akn/local/ops-bot/` dizini silinmiş veya bot.py, venv gibi kritik dosyalar eksik.

**Çözüm:**
```bash
sudo rm -rf /home/akn/local/ops-bot
ln -s /home/akn/vps/ops-bot /home/akn/local/ops-bot
sudo systemctl daemon-reload
sudo systemctl restart ops-bot
```

## Dependencies

- infrastructure — nginx ters proxy, SSL
- [[deployment]] — VPS deploy prosedürleri
- [[acp-protocol]] — Ops-bot'un kullandığı Agent Client Protocol
- [[telegram-kimi]] — ACP client implementasyon referansı

## Decisions

- [[adr-005-ops-bot-acp-sdk-migration]] — ACP client'ının resmi SDK'ya geçiş kararı

## Dokümantasyon

| Dosya | Amaç |
|-------|------|
| `README.md` | Proje tanımı, kurulum, mimari, komutlar, troubleshooting |
| `AGENTS.md` | AI agent'lar için stack, kod stili, güvenlik, deploy checklist |
| `CHANGELOG.md` | V2 rewrite ve sonraki değişiklikler (Keep a Changelog) |
| `docs/CURRENT_SYSTEM.md` | Üretimde çalışan mevcut durum, servis/timer akışı |
| `docs/SESSION_CONTEXT_2026_05_04.md` | ACP SDK geçiş session context'i (teknik detaylar) |
| `docs/agent-transformation-plan.md` | Tarihsel: V2 öncesi 12 haftalık plan (arşiv) |

<!-- AUTO-REFRESHED -->
## Recent Commits

- `2956c27` fix(sec-agent): AI analizi medium anomaly'de de tetiklensin, auth endpoint listesi genişletilsin, state path sabitlensin (2026-05-07)
- `d05f0b6` fix(gitignore): add .venv/ and sec-agent runtime state (2026-05-06)
- `d093d94` fix(deploy): fix ssh() override for multi-line commands in VPS mode (2026-05-06)
- `2414268` feat(deploy): add VPS environment detection (2026-05-06)
- `d6ddb0f` sync(vps): senkronize VPS'ten local'e — router.py silindi, orchestrator.py eklendi, agents/ dizini eklendi, eski ACP client/executor bot/'a geri taşındı (2026-05-05)
- `c836b86` fix(acp-sdk): wait 1s after prompt for trailing session_update chunks (2026-05-05)
- `5294c78` feat(telegram): remove agent list from /start, add accumulator debug logs (2026-05-05)
