# AGENTS.md — Ops-Bot

> Telegram üzerinden VPS operasyonlarını yöneten bot.  
> Kimi-CLI ACP modu ile çalışır. Tek evren: kimi-cli native agent/subagent/skill.

## Stack

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | Python 3.12 |
| Telegram | python-telegram-bot (30s timeout) |
| AI | kimi-cli (ACP modu) |
| Agent Spec | Kimi-CLI native YAML (`version: 1`) |
| Skills | Kimi-CLI native `SKILL.md` (YAML frontmatter) |
| Deploy | `./deploy.sh` → VPS systemd |

## Mimari (Tek Evren)

```
Telegram User → bot/telegram.py → bot/router.py (@agent parse)
                                    ↓
                           bot/acp_executor.py
                                    ↓
                              kimi-cli (ACP)
                                    ↓
                         agents/master/agent.yaml
                                    ↓
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
               @docker        @security       @monitor
               (subagent)     (subagent)      (subagent)
               tools: [Shell, ReadFile, Glob, Grep]
```

- **Router:** Sadece explicit `@agent-adı` parse eder. Gerisi kimi-cli master agent'e bırakılır.
- **Master agent:** `agents/master/agent.yaml` — coordinator, sadece `Agent` tool kullanır.
- **Subagent'lar:** `agents/master/subagents/*.yaml` — her biri kendi `tools` listesiyle yetkilendirilmiştir.
- **Context:** kimi-cli `~/.kimi/sessions/` altında native persistence sağlar.

## Kod Stili

### Python
- PEP 8, 4-space indentation
- `snake_case` fonksiyon/değişken
- `PascalCase` class
- `UPPER_CASE` constant (Config sınıfı hariç)
- Type hints: `from __future__ import annotations` ile `Optional`, `Dict`, `List`

### Agent YAML
- `version: 1` (integer, tırnak yok)
- `system_prompt_path` relative path
- `tools`: `module:ClassName` formatı
- `system_prompt_args`: dinamik değişkenler (örn: `BOT_VERSION`)

### Skill'ler
- Dizin adı: `kebab-case`
- `SKILL.md`: YAML frontmatter + Markdown içerik
- Frontmatter: `name`, `description` (zorunlu)

## Çalıştırma ve Test

```bash
# Syntax check
cd /home/akn/local/ops-bot
python3 -m py_compile bot/*.py

# Kimi-CLI agent spec doğrulama
cd agents/master
kimi --agent-file agent.yaml --print "test"

# sec-agent testleri
cd sec-agent && pytest

# Deploy (yerelden VPS'ye)
cd /home/akn/local/ops-bot
./deploy.sh              # package modu (default): tar.gz → scp
./deploy.sh --mode git   # git modu: VPS'te git pull + restart
```

## Agent Sistemi Konvansiyonları

### Yeni Subagent Ekleme
1. `agents/master/subagents/<name>.yaml` oluştur
2. `agents/prompts/ops-<name>-agent.md` oluştur
3. `agents/master/agent.yaml`'da `subagents:` bölümüne ekle
4. Subagent `tools` listesini minimal tut (principle of least privilege)

### Yeni Skill Ekleme
1. `skills/<name>/SKILL.md` oluştur (YAML frontmatter + Markdown)
2. `.kimi/skills/` symlink dizinine otomatik yansır
3. Kimi-cli `--skills-dir` parametresiyle yüklenir

## Güvenlik Kuralları

| Katman | Mekanizma |
|--------|-----------|
| 1. Kimi-CLI Spec | Her subagent'ın `tools` listesiyle sadece gerekli tool'lar |
| 2. ACP Client | `bot/acp_client.py` — riskli komut auto-reject |
| 3. System Prompt | `FORBIDDEN_PATTERNS` ve `ALLOWED_COMMANDS` değişkenleri |

**Auto-reject edilenler:** `git`, `rm`, `mv`, `cp`, `chmod`, `chown`, `sudo`, `mkfs`, `dd`, `wget`, `curl`, `nc`, `netcat`, `nmap`

**Tool call limiti:** 15'ten fazla ardışık tool call otomatik session cancel eder.

**Hassas veriler:**
- `.env.production` asla commit'lenmez
- API key'ler sadece `.env` dosyalarında
- `.env.example` şablonu güncel tutulur

## Deploy Öncesi Checklist

- [ ] `python3 -m py_compile bot/*.py` geçiyor
- [ ] `agents/master/agent.yaml` ve subagent YAML'ları syntax doğru
- [ ] `.env.example` güncel
- [ ] `sec-agent/tests/` geçiyor: `cd sec-agent && pytest`
- [ ] Commit formatı: `feat(ops-bot): ...` veya `fix(ops-bot): ...`
- [ ] Nginx config test: `docker exec vps_nginx_main nginx -t`

## Session Yönetimi

| Komut | Açıklama |
|-------|----------|
| `/iptal` | Tüm ACP session'larını iptal et, hafızayı temizle, yeni sohbet başlat |
| `/end` | Sadece hafızayı temizler (legacy SQLite memory). ACP session'ı korunur. |
| `/model` | Aktif modeli göster/değiştir |

> **Not:** `/end` komutu legacy `conversation_memory.py`'yi temizler. ACP session'ı (`~/.kimi/sessions/`) korunur. ACP session'ını tamamen temizlemek için `/iptal` kullanın.

## Bağımlılıklar

- `infrastructure/` — nginx, SSL, Docker
- `sec-agent/` — güvenlik izleme ve raporlama
- `telegram-kimi/` — ACP client implementasyon referansı

## Wiki

- Proje wiki sayfası: `wiki/projects/ops-bot.md`
- Wiki ingest: `wiki topla` (komutu monorepo root'tan çalıştır)
- Genel mimari: `wiki/system-overview.md`
