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
| `ops-bot/bot/config.py` | Env-based config (V2_ENABLED, EMBEDDING_ROUTER, timeout'lar 180-600s) |
| `ops-bot/bot/orchestrator.py` | V2 agent lifecycle orchestrator |
| ~~`ops-bot/router/hybrid.py`~~ | ~~HybridRouter~~ — [REMOVED] |
| ~~`ops-bot/router/embedding.py`~~ | ~~TF-based cosine similarity~~ — [REMOVED] |
| ~~`ops-bot/agents/descriptor_loader.py`~~ | ~~YAML descriptor okuma~~ — [REMOVED] |
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
- `ops-security-agent` / `ops-security-explain` / `ops-security-observe` — Güvenlik
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
2. **İkinci katman — ACP Client:** `bot/acp_client.py` `session/request_permission` handler'ında riskli komut filtrelemesi:
   - **Reject edilen kalıplar:** `git`, `rm`, `mv`, `cp`, `chmod`, `chown`, `sudo`, `mkfs`, `dd`, `wget`, `curl`, `nc`, `netcat`, `nmap`
   - **Approve edilenler:** Güvenli read-only ve yönetim komutları
   - Tool call başlığı ilk 200 karaktere bakılarak karar verilir

### Context Persistence

- Session-per-user: her kullanıcı kendi session ID'sine sahip
- Session ID'ler `self._sessions` dict'te tutulur
- kimi-cli `~/.kimi/sessions/<md5>/<session_id>/context.jsonl`'da context saklar
- Kimi-cli native context persistence — bot restart sonrası devam eder

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
| `/end` | (Placeholder) |

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

## Recent Commits

- `b4f50d8` deploy: ops-bot update 20260503_034308 — tek beyin, güvenlik filtreleri, tool limit, memory trim (2026-05-03)
- `2809ba3` deploy: ops-bot update 20260503_032155 (2026-05-03)
- `6ebd0f2` deploy: ops-bot update 20260503_031534 (2026-05-03)
- `2c685d6` feat(ops-bot): unify into single kimi-cli native universe — descriptor/zombie silme, skill frontmatter, subagent tools, master system.md değişkenleri (2026-05-03)
- `7afcff0` chore(ops-bot): pre-unification checkpoint (2026-05-03)
- `e36f158` feat(ops-bot): Türkçe routing, keywords_tr, timeout fixes, embedding router aktif (2026-05-03)
- `d443eab` deploy: ops-bot V2 rewrite deploy (2026-05-03)
- `dacaee9` fix(routing): embedding router env timing + syntax error (2026-05-03)
- `b915049` fix(security): use OPS_BOT_REPO_ROOT for ai_analyzer path (2026-05-02)
- `ab28161` chore: sync all local changes before deploy (2025-04-30)
- `ad62f2a` ops-bot: resolve_model_name() bilinmeyen model ID'lerini DEFAULT_MODEL'e düşürür
- `5b8b80c` ops-bot: fallback unknown model IDs to DEFAULT_MODEL in get_user_model()
