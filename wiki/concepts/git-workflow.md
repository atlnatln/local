---
title: "Git Workflow"
created: "2026-05-01"
updated: "2026-05-06"
type: concept
tags: [meta, git, git-hook, automation]
related:
  - proactive-wiki
  - deployment
  - README
sources:
---

# Git Workflow

Monorepo ve ayrı repo'lar için git stratejisi, commit konvansiyonları ve deploy öncesi kurallar.

---

## Repo Yapısı

| Repo | Tip | Projeler | Git Konumu |
|------|-----|----------|------------|
| `local` (monorepo) | Ana repo | mathlock-play, telegram-kimi, sayi-yolculugu, infrastructure | `/home/akn/local/.git` |
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

## GitHub Sync ve Cross-Machine Development

GitHub = source of truth. Local ve VPS birbirine `git push` / `git pull` üzerinden senkronize olur.

| Makine | Dizin | Amaç |
|---|---|---|
| **Local** | `/home/akn/local/` | Geliştirme + git repo |
| **VPS** | `/home/akn/local/` | Git clone (geliştirme alanı) |
| **VPS** | `/home/akn/vps/` | Deploy alanı (tar.gz çıkarma, production) |

### Session Başı Git Kontrolü

```
1. rm -f ~/.wiki-skip-session
2. timeout 5 git fetch origin 2>/dev/null || true
3. Wiki kontrolü (.pending)
```

### Push Protokolü

Kullanıcı "push yap" dediğinde:
1. `git status --short` → değişiklik özetini göster
2. Zorunlu wiki kontrolü — wiki değişikliği varsa önce ingest yap
3. Commit mesajı iste (`type(scope): description`)
4. `git add -A && git commit -m "..." && git push origin main`
5. Nested repo'ları unutma uyarısı (`ops-bot/`, `projects/webimar/`)

**Kural:** Wiki dosyalarında (`wiki/`, `.checkpoints/`) değişiklik varsa, wiki ingest yapılmadan ve commit edilmeden **push yapılmaz**.

## Related Decisions

- [[adr-001-monorepo-hybrid-structure]] — Monorepo + ayrı repo karışık yapısı kararı
- [[adr-006-github-sync-cross-machine-dev]] — GitHub Sync + Cross-Machine Development

## İlgili Sayfalar

- [[proactive-wiki]] — Git commit sonrası otomatik wiki güncelleme önerisi
- [[deployment]] — Deploy süreçleri ve otomasyon
