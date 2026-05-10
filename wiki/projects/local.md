---
title: "local Monorepo"
created: "2026-05-10"
updated: "2026-05-10"
type: project
tags: [meta]
related:
  - system-overview
  - infrastructure
  - ops-bot
  - webimar
  - mathlock-play
---

# local Monorepo

Ana geliştirme monorepo'su. Tüm projelerin kaynak kodu, altyapı konfigürasyonu, agent instruction'ları ve LLM wiki'si burada yaşar.

**GitHub:** `github.com:atlnatln/local.git`

---

## Monorepo Yapısı

```
/home/akn/local/
├── infrastructure/    # nginx, SSL, monitoring (Docker)
├── ops-bot/           # Telegram bot — ayrı git repo
├── projects/
│   ├── webimar/       # Django + Next.js — ayrı git repo
│   └── telegram-kimi/ # Telegram Kimi bot
├── scripts/           # Yardımcı script'ler
├── wiki/              # LLM Wiki (local-wiki skill)
└── ARCHITECTURE.md    # Detaylı mimari doküman
```

`ops-bot/`, `projects/webimar/` ve `projects/mathlock-play/` root repo'da `.gitignore`'dadır; bunlar ayrı GitHub repo'larıdır. `mathlock-play` artık `github.com/atlnatln/mathlock-play` adresinde bağımsız repo olarak yönetiliyor.

---

## Agent Instruction'ları

Agent'lar her session başında `AGENTS.md`'yi okur. Hayati kurallar (ortam tespiti, wiki zorunluluğu, git sync, push protokolü) burada yaşar.

Detaylı komutlar `references/QUICKREF.md`'de, wiki iş akışları `references/WORKFLOW.md`'de, kod kuralları `references/CONVENTIONS.md`'dedir.

### Ortam Ayrımı

| | **LOCAL** (`akn-ub`) | **VPS** (`89.252.152.222`) |
|---|---|---|
| Çalışma Dizini | `/home/akn/local` | `/home/akn/vps` |
| Amaç | Kod yazma, test, build, wiki | Production, monitoring |
| Servisler | `mathlock-backend`, `mathlock-celery` | `ops-bot`, `sec-agent`, `telegram-kimi`, `webimar` |

> **Not:** `mathlock-play` VPS servis listesinden çıkarıldı. Backend (`mathlock-backend`, `mathlock-celery`) local makinede çalışır; Android build ve deploy `mathlock-play` ayrı repo'sundan yönetilir.
>
> Kod local'de yazılır/build edilir, `deploy.sh` ile VPS'e gönderilir. Canlı ortam dosyalarını doğrudan düzenleme.

### Wiki Ingest Kuralı

`AGENTS.md`, `README.md`, `SCHEMA.md`, `wiki/*`, `deploy.sh`, `infrastructure/*`, `scripts/wiki-*` dosyalarından herhangi biri değiştiğinde wiki ingest zorunludur.

**Sıra:** `git diff` → wiki ingest → lint → `git add -A` → commit → push

**Git sync kontrolü:** Her session başında GitHub fetch → behind/ahead kontrolü → sync durumunda wiki kontrolü.

---

## Kaynak Dosyalar

| Dosya | Amaç |
|-------|------|
| `AGENTS.md` | Agent instruction'ları — hayati kurallar |
| `references/QUICKREF.md` | Sık kullanılan komutlar, deploy, test, VPS erişim |
| `references/WORKFLOW.md` | Wiki iş akışları (ingest, query, lint, ADR) |
| `references/CONVENTIONS.md` | Kod stili, dosya adlandırma, git commit formatı |
| `references/PAGE_TEMPLATES.md` | Wiki sayfa şablonları |

---

## Recent Commits

<!-- AUTO-REFRESHED -->
- `78531089` refactor(mathlock-play): extract to separate repo github.com/atlnatln/mathlock-play (2026-05-10)
- `e5ae1fc1` fix(mathlock-play): v1.0.78 — compile fix, test limit, Play Store upload script (2026-05-10)
- `73185046` chore(wiki): clear pending after ingest (2026-05-10)
- `02ce0371` docs(references): refactor AGENTS.md — split into focused rules + QUICKREF.md (2026-05-10)
- `9abf557c` docs(wiki): ingest mathlock-play memory game, overlay, set display fixes (2026-05-10)
