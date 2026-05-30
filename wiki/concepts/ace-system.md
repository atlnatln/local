---
title: "ACE — Adaptive Cross-session Experience"
created: 2026-05-30
updated: 2026-05-30
type: concept
tags: [ace, concept, agent, ai]
related: [ace-simulation, playbook, local-wiki]
---

# ACE — Adaptive Cross-session Experience

> Oturumlar arası kalıcı "yaşayan bellek" sistemi.
> Kimi CLI her oturumda sıfır context ile başlar; ACE bu boşluğu doldurur.

---

## TL;DR

ACE = Hiyerarşik playbook (`wiki/ace/`) + curator script (`scripts/ace-curator.py`) + Kimi skill (`ace-memory`). Her oturumda playbook otomatik okunur, oturum sonunda `ace topla` ile ders çıkarılır + prune + stats + wiki ingest tek komutta yapılır.

---

## Problem

Kimi CLI her oturumda sıfır context ile başlar:
- Önceki oturumdaki hataları "hatırlamaz"
- Aynı araştırmalar yeniden yapılır
- Aynı pattern hataları tekrarlanır
- Token israfı

## Çözüm

**Yarı-otomatik cross-session bellek:**
1. Her oturum başında playbook okunur (`AGENTS.md` entegrasyonu)
2. Kod düzenlerken yüksek-confidence dersler uygulanır
3. Oturum sonunda `ace topla` ile yeni dersler eklenir, eskiler arşivlenir

## Mimari

```
wiki/ace/
├── playbook.md           # Cross-project dersler (5-15 ders)
├── _template.md          # Yeni ders şablonu
├── ops-bot.md            # Python, asyncio, Telegram bot
├── webimar.md            # Django + Next.js
├── mathlock-play.md      # Kotlin/Android + Django backend
├── sayi-yolculugu.md     # Unity/C# + WebView
├── telegram-kimi.md      # Python bot
├── robotopia-android.md  # Kotlin/Android
├── infrastructure.md     # Docker, nginx, SSL
└── .archive/             # Düşük confidence / eski dersler
```

## Ders Formatı

Her ders yapılandırılmış markdown:

```markdown
## Ders <NNN>: <Başlık>
**Confidence:** <0.00-1.00>
**Created:** <YYYY-MM-DD>
**Updated:** <YYYY-MM-DD>
**Validations:** <N>
**Source:** <dosya/komut>
**Scope:** <genel|proje-adı>
**Type:** <pattern|anti-pattern|workflow|pitfall>

### Context
### Rule
### Rationale
### Examples
### Related
```

## Confidence Sistemi

| Confidence | Anlamı | Eylem |
|-----------|--------|-------|
| 0.90-1.00 | Kesin doğru | AGENTS.md'de mutlaka uygula |
| 0.70-0.89 | Güvenilir | Uygula, şüphe varsa doğrula |
| 0.50-0.69 | Yeni ders | Dikkatli uygula, test et |
| 0.30-0.49 | Eski/belki geçersiz | Uygulamadan önce kontrol et |
| < 0.30 | Muhtemelen stale | `.archive/` taşı |

**Güncelleme kuralları:**
- Yeni ders: 0.80
- Doğrulandı: +0.05
- Yanlış çıktı: -0.15
- 6 ay güncellenmedi: -0.10
- Kod kaynağı değişti: -0.20

## AGENTS.md Entegrasyonu

Her oturum başında:
1. Genel playbook'u oku: `wiki/ace/playbook.md`
2. Proje playbook'unu oku (bulunduğun dizine göre)
3. Confidence >= 0.70 olan dersleri **mutlaka** uygula

## Kullanım

| Senaryo | Komut |
|---------|-------|
| Oturum sonu, her şeyi topla | `ace topla` |
| Sadece ders çıkar | `ace öğren` |
| Hızlı ders ekle | `ace ders ekle` |
| Playbook'u gör | `ace playbook` |
| Eski dersleri temizle | `ace unut` |
| Bir dersi doğrula | `ace doğrula 004` |

## Script Referansı

```bash
# İstatistik
python3 scripts/ace-curator.py stats

# Yeni ders ekle
python3 scripts/ace-curator.py learn --title "..." --rule "..." --scope "..."

# Confidence güncelle
python3 scripts/ace-curator.py validate <ID>
python3 scripts/ace-curator.py invalidate <ID>

# Prune (dry-run önce)
python3 scripts/ace-curator.py prune --dry-run
python3 scripts/ace-curator.py prune

# Çakışma kontrolü
python3 scripts/ace-curator.py conflicts

# Oturum sonu toplu işlem
python3 scripts/ace-curator.py topla
```

## Wiki ile ACE Arasındaki Fark

| | Wiki | ACE |
|---|---|---|
| **Güncelleme** | Manuel (`wiki topla`) | Yarı-otomatik (`ace topla`) |
| **Format** | Serbest markdown | Yapılandırılmış dersler |
| **Kapsam** | "Proje nedir, nasıl çalışır" | "Ne işe yaradı / yaramadı" |
| **Okuyan** | Kimi + İnsan | Sadece Kimi (AGENTS.md'de otomatik) |
| **Yaşam süresi** | Uzun | Kısa-orta (prune ile yönetilir) |

## Riskler ve Mitigasyon

| Risk | Mitigasyon |
|------|-----------|
| Playbook çok büyür | Max 50 ders/proje, prune |
| Stale bilgi | Confidence decay, 6 ay timeout |
| Yanlış ders uygulanır | Confidence eşiği >= 0.70 |

## İlgili Sayfalar

- [[playbook]] — Genel cross-project dersler
- [[ops-bot]] — ops-bot playbook
- [[webimar]] — webimar playbook
- [[mathlock-play]] — mathlock-play playbook
- [[sayi-yolculugu]] — sayi-yolculugu playbook
- [[telegram-kimi]] — telegram-kimi playbook
- [[robotopia-android]] — robotopia-android playbook
- [[infrastructure]] — infrastructure playbook
- [[ace-simulation]] — 3 haftalık kurgusal ACE akış simülasyonu
- `local-wiki` skill — Ana wiki sistemi
