---
title: "Proaktif Wiki Yöneticisi"
created: "2026-05-01"
updated: "2026-05-07"
type: concept
tags: [meta, automation, git-hook, local-wiki, sync]
related:
  - README
  - git-workflow
  - deployment
sources:
  - raw/articles/wiki-post-commit.sh
---

# Proaktif Wiki Yöneticisi

Git commit sonrası [[kimi-code-cli|kimi-cli]]'nin bir sonraki açılışında otomatik olarak wiki güncellemesi öneren mekanizma.

---

## Problem

Kod yazarken wiki'yi güncellemeyi unutmak kolay. Commit atıp saatler sonra [[kimi-code-cli|kimi-cli]]'yi açtığında, hangi dosyaların değiştiğini, neyin wiki'ye yansıtılması gerektiğini hatırlamak zor.

## Çözüm: Marker File + AGENTS.md Proactive Check

### Bileşenler

| Bileşen | Görev | Konum |
|---------|-------|-------|
| Git post-commit hook | Commit sonrası marker yazar + otomatik sync commit atar | `scripts/wiki-post-commit.sh` |
| Marker dosyası | Bekleyen commit'leri biriktirir | `wiki/.pending` (tracked, cross-machine sync) |
| AGENTS.md talimatı | Session başında kontrol eder, kullanıcıya sorar | `AGENTS.md` Proaktif Wiki Kontrolü bölümü |
| Skip flag | "Bu session'da sorma" için | `~/.wiki-skip-session` |

### Akış Diyagramı

```
[Git Commit] (mesaj != "docs(wiki):*")
    ↓
[post-commit hook] → wiki/.pending'e satır ekle
    ↓
[post-commit hook] → git add wiki/.pending
    ↓
[post-commit hook] → git commit -m "docs(wiki): auto-sync pending marker"
    ↓
(Bu commit "docs(wiki):" ile başladığı için hook tekrar çalışmaz)
    ↓
[Git Push] → .pending GitHub'a gider
    ↓
[Diğer makine pull eder] → .pending gelir
    ↓
[Saatler sonra...]
    ↓
[kimi açılır]
    ↓
[AGENTS.md: Session Temizliği] → ~/.wiki-skip-session sil
    ↓
[Kullanıcı mesaj yazar]
    ↓
[Eğer wiki/.pending doluysa]
    ↓
[AskUserQuestion] "Wiki güncellemesi bekliyor... Ne yapayım?"
    ↓
    ├─ Evet → wiki topla → marker temizle
    ├─ Tek proje → wiki güncelle <proje> → marker temizle
    ├─ Durum → wiki durum → tekrar sor
    ├─ Şimdi değil → marker koru → devam et
    └─ Bu session sorma → ~/.wiki-skip-session oluştur → devam et
```

### Marker Formatı

Her satır bir commit'i temsil eder:

```
YYYY-MM-DD HH:MM|SHA|repo-name|file1.py,file2.py
```

Örnek:
```
2026-05-01 14:30|a1b2c3d|local|scripts/wiki-post-commit.sh,infrastructure/nginx.conf
```

### Git Hook Kurulumu

Tek kaynak script, üç repo'ya symlink:

```bash
# Ana kaynak
/home/akn/local/scripts/wiki-post-commit.sh

# Symlink'ler
/home/akn/local/.git/hooks/post-commit          # monorepo
/home/akn/local/ops-bot/.git/hooks/post-commit  # ops-bot
/home/akn/local/projects/webimar/.git/hooks/post-commit  # webimar
```

Hook'un çalışması için `chmod +x` gereklidir.

### Skip Koşulları (Hook İçinde)

Proaktif soru **atlanır** eğer:
- Kullanıcı direkt `wiki ...` komutu söylediyse (örn. `wiki durum`)
- `~/.wiki-skip-session` dosyası varsa

Hook **atlar** (marker yazmaz) eğer:
- Commit mesajı `docs(wiki):` ile başlıyorsa — bu zaten bir wiki/cleanup commit'idir

> **Kritik:** `docs(wiki):` prefix'i sonsuz döngüyü engeller. Hook `docs(wiki):` commit'ini atlar; ama hook'un kendi attığı auto-sync commit'i de `docs(wiki):` ile başlar, böylece kendini tekrar tetiklemez.

### Cross-Machine Sync

`.pending` dosyası GitHub üzerinden iki makine arasında senkronize edilir:

| Özellik | Eski | Yeni |
|---------|------|------|
| `.pending` Git'te | `.gitignore`'daydı (sadece local) | Tracked (GitHub'a gider) |
| Sync mekanizması | Manuel — kullanıcı `git add wiki/.pending` yapmalıydı | Otomatik — hook kendisi commit atar |
| Risk | Makine A'da commit atıldı, B bilmiyordu | Her makine `.pending`'i GitHub'dan alır |

### Temizlik Kuralları

| Durum | Marker | Skip Flag |
|-------|--------|-----------|
| İşlem başarılı | Temizlenir (`> wiki/.pending`) | — |
| İşlem başarısız | Korunur (tekrar sorulacak) | — |
| "Şimdi değil" | Korunur | — |
| "Bu session sorma" | Korunur | Oluşturulur |
| Yeni session | — | `rm -f ~/.wiki-skip-session` |

---

## Kararlar

**Neden marker file, neden doğrudan git diff değil?**

`git diff --name-status` checkpoint'ten HEAD'e bakar, ama bu sadece mevcut session'da çalışır. Kullanıcı commit atıp saatler sonra dönerse, hook olmadan bu değişiklikler "görünmez" kalır. Marker file, zamandan bağımsız olarak "commit yapıldı, wiki güncellenmedi" bilgisini korur.

**Neden /tmp değil de wiki/.pending?**

`/tmp` reboot'ta silinir. `wiki/.pending` kalıcıdır, böylece VPS restart sonrası bile wiki güncellemesi hatırlanır.

**Neden AskUserQuestion, neden otomatik ingest?**

Kullanıcı onayı olmadan wiki'ye yazmak riskli olabilir. Her zaman kullanıcı karar vermeli: ne zaman, hangi proje, toplu mu tekli mi.

**Neden `docs(wiki):` auto-sync commit'i?**

`git commit --amend` denendi ama `index.lock` deadlock oluşturdu. Ayrı bir commit atmak:
- Güvenli (lock çatışması yok)
- Şeffaf (log'da görünür)
- Geri alınabilir (`git revert` ile)
- Sonsuz döngü güvenli (`docs(wiki):` prefix hook'u atlar)

---

## İlgili Sayfalar

- [[README]] — Skill tanımı ve komut rehberi
- [[git-workflow]] — Monorepo git stratejisi
- [[deployment]] — Deploy süreçleri ve otomasyon
