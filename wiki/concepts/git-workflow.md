---
title: "Git Workflow"
created: "2026-05-01"
updated: "2026-05-01"
type: concept
tags: [meta, git, git-hook, automation]
related:
  - proactive-wiki
  - deployment
  - README
sources:
  - raw/articles/AGENTS.md
---

# Git Workflow

Monorepo ve ayrı repo'lar için git stratejisi, commit konvansiyonları ve deploy öncesi kurallar.

---

## Repo Yapısı

| Repo | Tip | Projeler | Git Konumu |
|------|-----|----------|------------|
| `local` (monorepo) | Ana repo | anka, mathlock-play, telegram-kimi, sayi-yolculugu, infrastructure | `/home/akn/local/.git` |
| `ops-bot` | Ayrı repo | ops-bot | `/home/akn/local/ops-bot/.git` |
| `webimar` | Ayrı repo | webimar-api, webimar-nextjs, webimar-react | `/home/akn/local/projects/webimar/.git` |

## Commit Formatı

```
type(scope): description
```

Örnekler:
- `feat(webimar): add new calculation endpoint`
- `fix(ops-bot): handle timeout in agent routing`
- `docs(wiki): update deployment guide`

## Kurallar

1. **Her deploy öncesi commit** atılır.
2. `ops-bot` ve `webimar` için ayrı repo commit'leri atılır.
3. Ardından `local` monorepo'ya commit atılır.
4. `.env` dosyaları asla commit'lenmez.
5. Wiki güncellemeleri `docs(wiki): ...` scope'u ile işaretlenir.

## Git Hooks

- **post-commit**: Commit sonrası `wiki/.pending` marker dosyasına kayıt yazar.
- Konumlar: `local/.git/hooks/post-commit`, `ops-bot/.git/hooks/post-commit`, `webimar/.git/hooks/post-commit`

## İlgili Sayfalar

- [[proactive-wiki]] — Git commit sonrası otomatik wiki güncelleme önerisi
- [[deployment]] — Deploy süreçleri ve otomasyon
