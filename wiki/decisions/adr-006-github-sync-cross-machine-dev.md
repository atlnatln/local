---
title: "ADR-006: GitHub Sync + Cross-Machine Development"
created: "2026-05-05"
updated: "2026-05-05"
type: decision
tags: [meta, git, github, vps, sync, adr]
related:
  - git-workflow
  - proactive-wiki
  - agents-md
---

# ADR-006: GitHub Sync + Cross-Machine Development

## Durum

**Accepted** — 2026-05-05

## Bağlam

`/home/akn/local` monorepo'su uzun süredir yerel makinede geliştiriliyor ancak GitHub'da `github.com/atlnatln/vps.git` adlı eski bir repoya bağlıydı. VPS'te sadece deploy edilmiş dosyalar var, geliştirme ortamı yok. Kullanıcı hem local'de hem VPS'te aktif geliştirme yapmak, wiki'yi iki makinede senkronize tutmak, ve kod değişikliklerini GitHub üzerinden yönetmek istiyor.

## Karar

1. **Yeni repo:** `github.com/atlnatln/local.git` (eski `vps` arşivlenecek).
2. **Push kapsamı:** Kaynak kod, config, script, wiki, infrastructure. Build artifact, venv, .env, deploy output GitHub'a gitmez.
3. **Nested repo stratejisi:** `ops-bot/` ve `projects/webimar/` root `.gitignore`'dadır, kendi repo'larında ayrı yaşar.
4. **Push trigger:** Kullanıcı "push yap" komutu verdiğinde.
5. **Session başı:** `timeout 5 git fetch origin` kontrolü; behind ise bildir, otomatik pull yok.
6. **Cross-machine sync:** GitHub = source of truth; local ↔ VPS `push`/`pull` ile senkronize.
7. **Wiki sync:** `wiki/` tamamen GitHub'da; `.checkpoints/*.sha` ortak; `.pending` machine-specific.
8. **Dizin yapısı:**
   - Local: `/home/akn/local/` → geliştirme + git repo
   - VPS: `/home/akn/local/` → git clone (geliştirme alanı)
   - VPS: `/home/akn/vps/` → deploy alanı (değişmez)
9. **VPS dev ortamı:** `scripts/setup-vps-dev.sh` ile kurulur.
10. **Deploy akışı korunur:** Local `deploy.sh` → tar.gz → VPS `/home/akn/vps/` (GitHub'dan bağımsız).

## Sonuçlar

- **Pozitif:**
  - İki makinede aynı geliştirme ortamı.
  - Wiki senkronize ve her iki makinede aktif.
  - Kod history'si GitHub'da merkezi ve güvenli.
  - AGENTS.md'lerdeki `/home/akn/local/` yolları her iki makinede de çalışır.
- **Negatif:**
  - 122 dirty file'ın gruplanıp commit edilmesi gerekli.
  - `ops-bot/` ve `projects/webimar/` root repo'dan `git rm --cached` ile çıkarıldı (893 dosya).
  - VPS'te geliştirme ortamı kurulumu zaman alacak.
- **Risk:**
  - İki makinede aynı anda değişiklik → conflict. Session başı `git fetch` kontrolü ile önceden uyarı.
