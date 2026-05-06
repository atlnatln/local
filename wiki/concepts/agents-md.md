---
title: "AGENTS.md"
created: 2026-05-03
updated: 2026-05-03
type: concept
tags: [kimi-cli, agents, configuration, coding-conventions]
related:
  - kimi-code-cli
  - git-workflow
sources: []
---

# [[AGENTS.md]]

AI coding agent'lar için proje context'i ve instruction'ları içeren Markdown dosyası. **README for agents** olarak düşünülebilir.

> **Amaç:** README.md insanlar içindir; AGENTS.md agent'lar içindir. Build adımları, test komutları, kod stili, güvenlik kuralları gibi agent'ların bilmesi gereken detayları içerir.

## Neden AGENTS.md?

| README.md | AGENTS.md |
|-----------|-----------|
| İnsanlar için hızlı başlangıç | Agent'lar için context ve instructions |
| Proje tanıtımı | Build steps, tests, conventions |
| Contribution guidelines | Kod stili, security gotchas |

Ayrı dosya olmasının nedeni:
- Agent'lar için tahmin edilebilir bir yer (`AGENTS.md`)
- README'leri insanlar için sade tutar
- Mevcut dokümantasyonu tamamlar, yerini almaz

## Format

Standart Markdown. Zorunlu alan yok. Önerilen bölümler:

```markdown
# AGENTS.md

## Project Overview
Kısa proje tanımı ve stack.

## Setup Commands
- Install deps: `pnpm install`
- Start dev: `pnpm dev`
- Run tests: `pnpm test`

## Code Style
- TypeScript strict mode
- Single quotes, no semicolons
- Line length limit: 100

## Testing Instructions
- CI plan: `.github/workflows/`
- Run all tests before commit
- Add/update tests for changed code

## Security Considerations
- `.env` dosyaları asla commit'lenmez
- API key'ler sadece production `.env`'de

## Deployment
- Staging: `./deploy.sh --staging`
- Production: `./deploy.sh --production`
```

## Konum ve Hiyerarşi

AGENTS.md dosyaları proje dizin ağacının herhangi bir yerinde bulunabilir:

```
/home/akn/local/
├── AGENTS.md          # Monorepo root — tüm projeler için genel kurallar
├── projects/
│   └── ops-bot/
│       └── AGENTS.md  # Ops-bot özel kurallar (root'u override eder)
└── .kimi/
    └── AGENTS.md      # Kimi-cli özel context
```

**Override kuralı:** Düzenlenen dosyaya en yakın AGENTS.md geçerlidir. Alt dizindeki dosya üsttekini override eder. Kullanıcının doğrudan chat prompt'u her zaman en yüksek önceliğe sahiptir.

## Kimi-CLI Entegrasyonu

Kimi-cli system prompt'unda `${KIMI_AGENTS_MD}` değişkeni ile proje root'tan çalışma dizinine kadar olan tüm `AGENTS.md` dosyalarının birleştirilmiş içeriğini otomatik inject eder:

```markdown
# My Agent System Prompt

Working directory: ${KIMI_WORK_DIR}

${KIMI_AGENTS_MD}

## Additional Instructions
...
```

Kimi-cli aşağıdaki yerlerde AGENTS.md arar:
1. Proje root (`/home/akn/local/AGENTS.md`)
2. Çalışma dizini ve üst dizinler
3. `.kimi/AGENTS.md`

## Best Practices

- **Canlı doküman:** Kod değişiklikleriyle birlikte güncelle
- **Kısa tut:** 200-300 satır ideal; detaylar `docs/` veya wiki'ye taşınabilir
- **Komutlar çalıştırılabilir olsun:** Agent test komutlarını otomatik çalıştırabilir
- **Monorepo:** Her alt proje kendi AGENTS.md'sini taşıyabilir (örn: `ops-bot/AGENTS.md`)
- **Güvenlik:** Hassas bilgileri (API key, şifre) asla ekle

## Ekosistem Uyumluluğu

AGENTS.md açık bir formattır ve birden fazla agent/tool tarafından desteklenir:
- Kimi Code CLI (`${KIMI_AGENTS_MD}`)
- OpenAI Codex
- Cursor
- Aider (`.aider.conf.yml` ile yapılandırılabilir)
- Gemini CLI (`.gemini/settings.json` ile yapılandırılabilir)

## Kaynaklar

- [agents.md](https://agents.md) — Resmi site ve spec
- [Kimi CLI Docs — Agents](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/sub-agents.html)
