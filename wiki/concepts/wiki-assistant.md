---
title: "Wiki Asistanı (wiki-assistant.py)"
created: "2026-05-30"
updated: "2026-05-30"
type: concept
tags: [meta, tooling, automation, lsp-style]
related: [local-wiki, wiki-growth-protocol, agents-md]
---

# Wiki Asistani

> `/home/akn/local/scripts/wiki-assistant.py` — Kimi CLI için LSP-felsefesiyle tasarlanmış wiki otomasyon aracı.

## Amac

Kimi'nin `wiki topla` sirasinda dosya karistirma/okuma yukunu alir. Ona sadece "anlam cikarma" ve "yazma" isini birakir. Token tasarrufu hedefi: %70+.

## Mimari Kararlar

| Karar | Neden |
|-------|-------|
| **Ozel script (LSP degil)** | Wiki = programlama dili degil. LSP'nin sembol tablosu, tip cikariri, tanima gitme gibi ozellikleri wiki icin gereksiz. |
| **Git diff + path mapping + regex** | Dil-agnostik. Python, JS, HTML, Docker, Nginx, Shell, Markdown hepsi ayni motorla islenir. |
| **JSON context paketi** | Kimi tek bir Shell komutu ile tum bilgiyi alir. 8-10 ayri ReadFile yerine 1 komut. |
| **L2-style cache** | `wiki/.assistant-index.json` — wiki sayfalarinin baslik yapisi cache'lenir. Degismemis sayfalar icin tekrar parse edilmez. |

## 1. Asama (Tamamlandi): Wiki Ingest

**Kapsam:** Sadece `wiki topla` / `wiki ingest` / `wiki guncelle` komutlari.

**Calisma akisi:**
1. Checkpoint SHA'lari oku
2. Git diff calistir
3. `wiki-assistant.py --prepare` calistir
4. Asistan JSON cikti verir: diff_summary, changed_files[], wiki_targets[]
5. Kimi sadece JSON'u okur, karar verir, StrReplaceFile/WriteFile ile uygular
6. Lint calistir
7. Checkpoint guncelle

**Test sonuclari:**
- Token tasarrufu: ~%70-90
- ReadFile cagrisi: 15-25 → 5-8
- Lint: 10/10 PASS
- Commit: `d484c84a` (main)

## 2. Asama (Devam Ediyor): Kod Duzenleme

**Hedef:** `wiki-assistant.py`'ye `--locate` modu eklenir. Kullanici "su fonksiyona ekleme yap" dediginde:
1. Asistan dosyayi ve fonksiyonu bulur
2. Satir araligini tespit eder
3. Kimi'ye sadece ilgili fonksiyonu sunar

### 2.1 Python (Tamamlandi)

- **LSP Sunucusu:** Pyright (`pyright-langserver --stdio`)
- **Client:** `scripts/lsp-client.py`
- **Komut:** `python3 scripts/wiki-assistant.py --locate --file <path> --symbol <name>`
- **Cikti:** JSON (`range`, `kind`, `snippet`)
- **Test:** `ops-bot/conversation_memory.py` uzerinde dogrulandi

### 2.2 JS/TS (Tamamlandi)

- **LSP Sunucusu:** TypeScript Server (`typescript-language-server --stdio`)
- **Client:** Mevcut `scripts/lsp-client.py` (JS/TS destegi hazirdi)
- **Komut:** `python3 scripts/wiki-assistant.py --locate --file <path> --symbol <name>`
- **Test:** `projects/webimar/webimar-nextjs/middleware.ts` uzerinde dogrulandi

### 2.3 Kotlin/Java (Planlandi)

- `kotlin-language-server` ve JDTLS kurulumu
- Android projelerinde kullanim

## Dosya Yapisi

| Dosya | Rol |
|-------|-----|
| `scripts/wiki-assistant.py` | Ana program |
| `wiki/.assistant-index.json` | Baslik cache'i (gitignore'da) |
| `.kimi/skills/local-wiki/SKILL.md` | Skill talimati (asistanli akis) |
| `AGENTS.md` (root) | Genel prensip (asistan birincil) |
| `wiki/AGENTS.md` | Wiki bakim kurallari + cache koruma |

## Cache Yonetimi

- **Olusum:** Ilk calistirmada otomatik olusur
- **Guncelleme:** Dosya degistiginde (mtime eslesmezse) otomatik guncellenir
- **Temizlik:** `rm wiki/.assistant-index.json` ile silinir, bir sonraki calistirmada yeniden olusur
- **Kural:** Elle duzenlenmemeli. `wiki/AGENTS.md`'de koruma kurali vardir.

## Fallback

Asistan calismazsa (Python hatasi, bos cikti):
1. Hata kullaniciya soylenir
2. Klasik akisa donulur: Checkpoint → Git diff → Dosyalari oku → Wiki guncelle
3. `local-wiki` skill'i ve `AGENTS.md` fallback talimatini icerir

## Baglanti

- [[README|local-wiki skill]] — Skill detaylari
- [[wiki-growth-protocol]] — Buyume kurallari
- [[agents-md]] — Agent davranis kurallari
