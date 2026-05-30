---
title: "ACE Playbook — Genel"
created: 2026-05-30
updated: 2026-05-30
type: concept
tags: [ace, playbook, meta]
related: [ace-system]
---

# ACE Playbook — Genel

> Cross-project dersler. Her oturumda okunur.
> Proje-spesifik dersler için bkz. ilgili proje playbook'u.

---

## Ders 001: LSP ile kod düzenleme — önce locate, sonra oku

**Confidence:** 0.95
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 2
**Source:** scripts/wiki-assistant.py
**Scope:** genel
**Type:** workflow

### Context
Kimi kod düzenleme isteği aldığında tüm dosyayı okumak yerine LSP kullanarak sembol konumunu bulmalı.

### Rule
Kod düzenleme isteğinde önce `scripts/wiki-assistant.py --locate --file <path> --symbol <name>` çalıştır. Sadece ilgili satır aralığını oku, `StrReplaceFile` ile değişikliği uygula.

### Rationale
Tam dosya okuma ~1000 satır = token israfı. LSP locate ~50 satır = %95 tasarruf.

### Examples

#### ✅ Do
```bash
python3 scripts/wiki-assistant.py --locate --file bot/main.py --symbol handle_message
# Sadece range'i oku, StrReplaceFile ile düzenle
```

#### ❌ Don't
```bash
# Tam dosyayı oku — neden: 800 satır context israfı
cat bot/main.py
```

### Related
- [[wiki-assistant]]
- [[kimi-code-cli]]
- [[ops-bot]]
- [[webimar]]
- [[mathlock-play]]
- [[sayi-yolculugu]]
- [[telegram-kimi]]
- [[robotopia-android]]
- [[infrastructure]]

---

## Ders 002: Git stash kullanımı — pop'tan önce status kontrolü

**Confidence:** 0.85
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 1
**Source:** AGENTS.md
**Scope:** genel
**Type:** workflow

### Context
Birçok kez `git stash pop` çalıştırıldıktan sonra beklenmedik conflict veya untracked dosya sorunları yaşandı.

### Rule
`git stash pop` veya `git stash apply` yapmadan önce mutlaka `git status --short` çalıştır. Working tree temiz değilse önce durumu çöz.

### Rationale
Stash pop conflict'e düşerse cleanup zorlaşır. Önceki durum bilgisi kaybolabilir.

### Examples

#### ✅ Do
```bash
git status --short
# Temizse:
git stash pop
```

#### ❌ Don't
```bash
# Doğrudan pop — neden: conflict riski, kayıp değişiklik
 git stash pop
```

### Related
- [[git-workflow]]

---

## Ders 003: Wiki ingest öncesi her zaman lint çalıştır

**Confidence:** 0.90
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 1
**Source:** wiki/AGENTS.md
**Scope:** genel
**Type:** workflow

### Context
Wiki güncellemeleri bazen lint hatası veriyordu, commit sonrası fark ediliyordu.

### Rule
Her wiki ingest işleminden önce `wiki_lint.py` çalıştır. Lint PASS olmadan commit yapma.

### Rationale
Lint hatası olan wiki sayfaları sonraki agent'lar için sorun yaratır. Pre-commit hook zaten engeller ama wiki ingest akışında da kontrol şart.

### Examples

#### ✅ Do
```bash
cd ~/.kimi/skills/local-wiki/ && python3 scripts/wiki_lint.py /home/akn/local/wiki
# PASS/WARN/FAIL kontrolü yap
```

#### ❌ Don't
```bash
# Doğrudan commit — neden: lint hatası push sonrası fark edilir
git add wiki/ && git commit -m "docs(wiki): ..."
```

### Related
- `local-wiki` skill
- [[wiki-growth-protocol]]

---

## Ders 004: Entegrasyon değişikliklerini ilk implementasyonda test et
**Confidence:** 0.80
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** scripts/wiki-assistant.py
**Scope:** genel
**Type:** anti-pattern

### Context
ACE sistemini wiki'ye entegre ederken wiki-assistant.py ace'yi tanımıyordu ve map_to_wiki yanlış hedefe yönlendiriyordu.

### Rule
Yeni bir alt sistem eklerken (ACE gibi), mevcut otomasyon araçlarının (wiki-assistant.py) onu tanıyıp tanımadığını, dosya eşlemelerinin doğru çalışıp çalışmadığını hemen test et.

### Rationale
Entegrasyon 'teoride çalışır' ama pratikte kırık olabilir. Erken test etmek ileride büyük zaman kaybını ve tutarsızlığı önler.

### Examples
#### ✅ Do
```bash
python3 scripts/wiki-assistant.py --prepare --project ace --pretty
```

#### ❌ Don't
```bash
# Dokümantasyonda 'ace topla' ile wiki ingest çalışır yaz, ama hiç test etme
```

### Related
- [[playbook]]

---
