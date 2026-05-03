---
title: "Ops-Bot"
created: 2026-05-01
updated: 2026-05-03
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
  - ops-bot/AGENTS.md
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
| Agent Executor | `bot/acp_executor.py` — kimi-cli ACP modu ile session persistence |
| ACP Client | `bot/acp_client.py` — JSON-RPC 2.0 over stdio |
| Telegram Handler | `bot/telegram.py` — message routing + reply formatting |
| Router | `bot/router.py` — 3-layer: explicit @agent → embedding → LLM fallback |
| Embedding Router | ~~`router/hybrid.py` + `router/embedding.py`~~ — [REMOVED] Tek beyin, kimi-cli native routing (2026-05-03) |
| Agent Registry | ~~`agents/descriptor_loader.py`~~ — [REMOVED] Kimi-CLI native agent spec kullanılıyor |
| Agent Manager | ~~`agents/manager.py`~~ — [REMOVED] Kimi-CLI kendi lifecycle'ını yönetiyor |
| Memory | `bot/memory.py` — SQLite conversation_memory + V2 agent state |
| MCP Tools | `mcp/tools/` — docker, db, system tool definitions |
| Models | `models/registry.py` — model name resolution |
| Skills | `skills/*/SKILL.md` — 4 skill (docker-troubleshooting, nginx-routing, postgres-query, security-reporting) |
| Security | `sec-agent/` — collector/engine/actions/config |
| Test | `tests/` — pytest + pytest-asyncio, 57 test (49 unit + 8 integration/E2E) |
| Deploy | `./deploy.sh` → VPS `systemd` servisi |

## Entry Points

| Dosya | Görev |
|-------|-------|
| `ops-bot/bot.py` | Ana Telegram bot uygulaması (19 satır entry point) |
| `ops-bot/bot/telegram.py` | Telegram message handler, HTTP timeout (30s), ACK, context footer |
| `ops-bot/bot/router.py` | Tek beyin: sadece explicit `@agent-adı` → yoksa her zaman `general/master` |
| `ops-bot/bot/acp_executor.py` | ACP session yönetimi, tool call streaming, sadece `agents/master/agent.yaml` kullanır |
| `ops-bot/bot/acp_client.py` | JSON-RPC 2.0 ACP client (initialize 30s, session/new 30s, default 60s) |
| `ops-bot/bot/memory.py` | Legacy SQLite conversation memory; context persistence kimi-cli `~/.kimi/sessions/` tarafından sağlanır |
| `ops-bot/bot/config.py` | Env-based config (TELEGRAM_TOKEN, ALLOWED_USER_ID, timeout'lar 180-600s, TEST_MODE) |
| `ops-bot/.env.test` | Test ortamı çevre değişkenleri (`TEST_MODE=true`, `ALLOWED_USER_ID=123456789`) |
| `ops-bot/pytest.ini` | pytest yapılandırması (asyncio_mode=auto, slow marker) |
| `ops-bot/CHANGELOG.md` | Değişiklik kaydı (Keep a Changelog formatı) |
| ~~`ops-bot/router/hybrid.py`~~ | ~~HybridRouter~~ — [REMOVED] |
| ~~`ops-bot/router/embedding.py`~~ | ~~TF-based cosine similarity~~ — [REMOVED] |
| ~~`ops-bot/agents/descriptor_loader.py`~~ | ~~YAML descriptor okuma~~ — [REMOVED] |
| `ops-bot/tests/conftest.py` | pytest fixtures: mocked Telegram Application + Update factories |
| `ops-bot/tests/test_router.py` | 22 unit test: `extract_explicit_agent()` regex parser + `BotRouter.select()` |
| `ops-bot/tests/test_acp_client.py` | 7 unit test: ACP protocol (`ApprovalRequest`/`ToolCallRequest`), permission auto-approve/reject, word-boundary risky matching |
| `ops-bot/tests/test_acp_executor.py` | 17 unit test: ACP executor `_clean_output`, session lifecycle, cancel/reset, tool call buffering |
| `ops-bot/tests/test_telegram_messages.py` | 10 unit test: Telegram message handler formatting, error replies, notification parsing |
| `ops-bot/tests/test_integration.py` | 8 integration/E2E test: smoke + real kimi-cli ACP subprocess |
| `ops-bot/deploy.sh` | VPS deploy script'i (package/git modları) |
| `ops-bot/systemd/ops-bot.service` | systemd unit dosyası |

## Mimari (Tek Evren — Kimi-CLI Native)

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Telegram User  │────▶│ bot/telegram │────▶│  bot/router.py  │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                      │
                           ┌──────────────────────────┘
                           ▼
                   ┌─────────────────┐
                   │ bot/acp_executor│
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

Agent seçimi: `bot/router.py` sadece explicit `@agent-adı` parse eder. Kimi-cli master agent (`agents/master/agent.yaml`) kullanıcının sorusunu analiz eder ve doğru subagent'ı `Agent` tool'u ile çağırır. Tüm routing kararları kimi-cli tarafından verilir. Python katmanı sadece Telegram entegrasyonu ve ACP session yönetimi yapar.

### ACP Executor

`bot/acp_executor.py` her kullanıcı için uzun ömürlü ACP session yönetir. Artık tek master agent spec (`agents/master/agent.yaml`) kullanır:

- `_get_or_create_session()` — yeni session oluşturur, `agents/master/agent.yaml`'ı kimi-cli'ye geçirir
- `run()` → `acp_client.prompt()` → streamed text toplar
- `cancel()` — session cancel
- `reset_session()` — Mevcut session'ı iptal edip discard eder
- `reset_all_sessions()` — Kullanıcının tüm session'larını iptal edip discard eder

**Önemli not:** ACP modu `--yolo`/`--afk` flag desteklemez. Tool kullanımı ACP server tarafında `toolCall`/`toolResult` loop'u ile yönetilir. Bot `_on_notification`'da `tool_call` ve `tool_call_update` event'lerini buffer'a yansıtır (🔧 başlık, ✅/❌ durum).

**Tool call koruması:** 15'ten fazla ardışık tool call otomatik session cancel eder.

**Timeout yapılandırması:**

| Ajan | Maksimum Timeout |
|------|------------------|
| Default | 90s |
| ops-database-agent | 90s |
| ops-incident-agent, ops-docker-agent, ops-monitor-agent, ops-security-agent, ops-ip-query-agent, ops-forensic-agent, ops-seo-agent | 120s |
| ops-fix-agent | 180s |

**Tek master agent (2026-05-03):** `agents/master/agent.yaml` tek kaynak. Subagent'lar `subagents/` dizininde, kimi-cli `Agent` tool'u ile çağrılır. Her subagent kendi `tools` listesiyle yetkilendirilmiştir (güvenlik katmanı 1).

### Güvenlik Kontrolleri (2026-05-03)

Güvenlik iki katmandır:

1. **Birinci katman — Kimi-CLI Agent Spec:** Her subagent'ın `tools` listesiyle sadece gerekli tool'lar aktiftir. `ops-security-agent`'ta `WriteFile` yoksa hiçbir dosya yazılamaz.
2. **İkinci katman — ACP Client:** `bot/acp_client.py` `request` method handler'ında riskli komut filtrelemesi:
   - **Reject edilen kalıplar:** `git`, `rm`, `mv`, `cp`, `chmod`, `chown`, `sudo`, `mkfs`, `dd`, `wget`, `curl`, `nc`, `netcat`, `nmap`
   - **Approve edilenler:** Güvenli read-only ve yönetim komutları
   - Tool call başlığı ilk 200 karaktere bakılarak karar verilir
   - **Word-boundary matching:** `re.findall(r"\b\w+\b", ...)` ile tam kelime eşleşmesi — `"perform"` gibi substring'ler yanlış reject yapmaz (2026-05-03)
   - **Kimi-cli 1.40 uyumluluğu:** Hem yeni `method: "request"` + `type: "ApprovalRequest"` hem eski `session/request_permission` desteklenir

### Context Persistence

- Session-per-user: her kullanıcı kendi session ID'sine sahip
- Session ID'ler `self._sessions` dict'te tutulur
- kimi-cli `~/.kimi/sessions/<md5>/<session_id>/context.jsonl`'da context saklar
- Kimi-cli native context persistence — bot restart sonrası devam eder
- **Context/token kullanım takibi:** `usage_update` ACP notification handler'ı mevcut ancak kimi-cli 1.40.0'da bu bilgi ACP üzerinden iletilmiyor — gösterim deferred (teknik borç)

## Servisler

| Servis | Tip | Açıklama |
|--------|-----|----------|
| `ops-bot.service` | systemd | Ana Telegram bot |
| `sec-agent.service` | systemd | Sürekli güvenlik değerlendirme döngüsü |
| `sec-agent.timer` | systemd timer | 3 dk'da bir `sec-agent-once.service` |
| `sec-agent-metrics.service` | systemd | Prometheus metrikleri (`:9101`) |
| `ops-bot-weekly-security-report.timer` | systemd timer | Haftalık özet |
| `ops-bot-critical-alert.timer` | systemd timer | 3 saatte bir kritik eşik kontrolü |

## Deploy

```bash
cd ops-bot/
./deploy.sh              # package modu (default): tar.gz oluştur, scp et
./deploy.sh --mode git   # git modu: VPS'te git pull + restart
```

Deploy akışı:
1. SSH multiplexing ile rate-limit'ten kaçınma
2. `tar.gz` paketi oluşturma (package modu) veya `git push` (git modu)
3. VPS'te `setup.sh` çalıştırma
4. `systemctl restart ops-bot`

### VPS Dizin Yapısı

| Dizin | Amaç |
|-------|------|
| `/home/akn/vps/ops-bot/` | Deploy hedefi — kod, venv, config |
| `/home/akn/local/ops-bot/` | systemd servisinin beklediği yol (symlink) |

> **Not:** systemd servis dosyası `WorkingDirectory`, `ExecStart` ve çevre değişkenlerinde `/home/akn/local/ops-bot/` yolunu kullanır. Deploy script dosyaları `/home/akn/vps/ops-bot/` altına çıkarır. Bu iki yol arasında senkronizasyon `ln -s /home/akn/vps/ops-bot /home/akn/local/ops-bot` symlink'i ile sağlanır.

## Security (sec-agent)

Detaylı mimari ve operasyon bilgisi: bkz. [[sec-agent]].

Özet:
- `sec-agent/` alt yapısı: collectors, engine, actions, config
- VPS üretimi `/opt/sec-agent/` altında timer tabanlı one-shot çalışır
- Guardrail korumalı otomatik block / ratelimit / alert
- Günlük AI yorumlu rapor: bkz. [[security-ai-reporting]]

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `/iptal` | Tüm ACP session'larını discard eder, hafızayı temizler (legacy + V2), yeni sohbet başlatır |
| `/end` | Legacy hafızayı temizler; ACP session'ı korunur |

## Troubleshooting

### ACP Prompt Timeout

**Belirti:** `⏱️ Zaman aşımı: ACP yanıt vermedi.`

**Neden ve Çözüm:**
1. **ACP prompt timeout:** `bot/acp_executor.py`'de `min(Config.KIMI_TIMEOUT_DEFAULT, 90)` kullanılıyor.
   - *Çözüm:* `.env`'deki değerleri kontrol et: `OPS_BOT_KIMI_TIMEOUT_*_SECONDS`
2. **python-telegram-bot HTTP timeout:** `telegram.py`'de `.read_timeout(30).write_timeout(30).connect_timeout(10)`
3. **ACP client timeout:** initialize 30s, session/new 30s, default request 60s

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
- [[telegram-kimi]] — ACP client implementasyon referansı

## Dokümantasyon

| Dosya | Amaç |
|-------|------|
| `README.md` | Proje tanımı, kurulum, mimari, komutlar, troubleshooting |
| `AGENTS.md` | AI agent'lar için stack, kod stili, güvenlik, deploy checklist |
| `CHANGELOG.md` | V2 rewrite ve sonraki değişiklikler (Keep a Changelog) |
| `docs/CURRENT_SYSTEM.md` | Üretimde çalışan mevcut durum, servis/timer akışı |
| `docs/agent-transformation-plan.md` | Tarihsel: V2 öncesi 12 haftalık plan (arşiv) |

## Recent Commits

- `3304d40` revert(debug): remove prompt result key logging — context usage deferred (2026-05-03)
- `f74b7dd` fix(logging): setup logging before module imports to capture INFO logs (2026-05-03)
- `a72537c` feat(ops-bot): add context usage to Telegram footer (deferred — kimi-cli 1.40 ACP protocol) (2026-05-03)
- `6c43a44` feat(telegram): add /iptal footer to every bot reply (2026-05-03)
- `4493d02` fix(deploy): include *.md files in deployment package (2026-05-03)
- `1f7ea09` fix(ops-bot): use word-boundary matching for risky command filter (2026-05-03)
- `be6be2c` fix(ops-bot): correct ACP ApprovalRequest protocol for kimi-cli 1.40 (2026-05-03)
- `d23644e` test(ops-bot): fix remaining mock issues — 57 test passing (2026-05-03)
- `0741b91` test(ops-bot): fix top-level import breaking env_patch in tests (2026-05-03)
- `63f1f69` fix(ops-bot): apply `_clean_output` to all return paths in executor (2026-05-03)
- `dbdb356` fix(ops-bot): improve logging, error messages, and router caching (2026-05-03)
- `d28a8db` merge(security): unify explain+observe into ops-security-agent.md (2026-05-03)
- `c7d2563` fix(deploy): include missing directories in package mode (2026-05-03)
