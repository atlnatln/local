---
title: "Kontrollu Buyume Protokolu"
created: "2026-05-10"
updated: "2026-05-10"
type: concept
tags: [meta, local-wiki]
related:
  - AGENTS
  - concepts-index
  - log-2026-H1
---

# Kontrollu Buyume Protokolu

> [[AGENTS|Ana AGENTS.md sayfasina don]]

## Kontrollu Buyume Protokolu

> Wiki buyuyecek -- bu kacinilmaz. Ama **kontrollu** buyumeli: dikeyde sismek yerine yatayda dallanmali, eskiyi yumusakca arsivlemeli, gereksizi terk etmeli.

### Kural 1 -- Yatay Buyume > Dikey Buyume

Bir sayfa uzamasin, yeni sayfa acilsin.

| Durum | Eylem | Ornek |
|-------|-------|-------|
| Concept sayfasi **>420 satir** (%20+ asim) | Hemen sub-page cikar | `meb-2024-curriculum-render.md`, `meb-2024-curriculum-ontoloji.md` |
| Project sayfasi **>480 satir** (%20+ asim) | Hemen sub-page cikar | `mathlock-play-android-games.md`, `mathlock-play-android-auth.md` |
| Project sayfasi **>360 satir** (%90 doluluk) | Sub-page planla, bir sonraki ingest'te bol | `ops-bot-agents.md` |
| Bir bolum **>100 satir** | O bolumu ayri sayfa yap, ana sayfada wikilink birak | `kimi-code-cli-mcp.md` |
| Karar sayfasi **>200 satir** | Gereksiz detayi kisalt, context'i ozle; ADR kisa olmali | `adr-004` 191 satir, sinirda |

**Sub-page cikarma proseduru:**
1. Ana sayfada 100+ satirlik bolumu belirle
2. Yeni sayfa olustur: `wiki/<kategori>/<ana-sayfa>-<bolum>.md`
3. Icerigi tasiy, ana sayfada bolum yerine 3-5 satir ozet + wikilink birak
4. Ana sayfanin `related:` alanina sub-page ekle
5. Sub-page'in `related:` alanina ana sayfa ekle
6. `index.md`'ye sub-page ekle
7. `log.md`'ye giris yap
8. Lint calistir; tek kullanimlik tag'leri temizle, SCHEMA.md'ye gerekirse ekle

---

### Kural 2 -- Log Zincirleme Buyume

`log.md` dikeyde sinirsiz buyumez. Zincirleme log sistemi:

```
log.md (aktif, max 500 giris)
  | 500'e ulasinca
log-2026-H1.md (arsiv, 500 giris)
  | devam
log.md (yeni, ilk giris: "Onceki log: log-2026-H1.md")
```

**Log zincirleme proseduru:**
1. `grep -c "^## \[" wiki/log.md` -> 500+ ise zincirle
2. Yeni dosya: `wiki/log-YYYY-HN.md` (H1 = Ocak-Haziran, H2 = Temmuz-Aralik)
3. Mevcut `log.md`'yi yeni dosyaya kopyala
4. `log.md`'yi sifirla, ilk satir: `> Onceki log: log-YYYY-HN.md`
5. Frontmatter'i koru (`type: log`)
6. `index.md`'nin `## Log` bolumune arsiv linki ekle
7. `log.md` commit'le, arsiv dosyasini da commit'le

**Log giris filtresi (Kritik):**
- log.md'ye YAZILIR: ingest, ADR ekleme, sayfa arsivleme, karar degisikligi, karar ekleme
- log.md'ye YAZILMAZ: lint sonuclari, salt okunur sorgular, otomatik kontroller
- Lint sonuclari sadece `.weekly-report`'ta yasar

**Lint arsivleme proseduru:**
1. `log.md`'deki lint-only girişlerini tespit et: `grep "^## \[" log.md | grep "lint |"`
2. Her lint girişini `wiki/log-lint-archive.md` dosyasına TAŞI (silme, arşivle)
3. `log-lint-archive.md` formatı: `# [TARIH] lint | X/Y | warning:N failure:N`
4. `log.md`'den lint girişlerini kaldır (sadece ingest/ADR/decision/concept kalsın)
5. `index.md`'nin `## Log` bölümüne ekle: `- [[log-lint-archive|Lint Arşivi]]`
6. `log-lint-archive.md` frontmatter: `type: log`, `tags: [meta, archive]`
7. `log.md`'yi ve `log-lint-archive.md`'yi aynı commit'te kaydet

---

### Kural 3 -- Index Kategorik Buyume

Sayfa sayisi arttikca index.md sismez, kategori sayfalari olusturulur.

| Sayfa Sayisi | Yapi | Eylem |
|-------------|------|-------|
| <50 | `index.md` tum sayfalari dogrudan listele | Mevcut durum (~40 sayfa) |
| 50-80 | `wiki/projects/index.md`, `wiki/concepts/index.md` gibi alt kataloglar olustur | **Yaklasiyoruz** |
| 80+ | `index.md` sadece kategori sayfalarina link versin, detay alt sayfalarda | Planla |

**Kategori index olusturma proseduru:**
1. `wiki/projects/index.md` olustur (type: index)
2. Mevcut `index.md`'deki `## Projects` bolumunu buraya tasiy
3. `index.md`'de `## Projects` yerine Projeler kategorisi linki ekle
4. Her kategori index'i kendi `## Recently Updated` bolumunu tasir
5. Tüm kategori index'lerine capraz link ekle; bir anahtar kelime ile `index.md` → alt index → hedef sayfa yolunu takip et. Ust ajanin sezgisel erisimini dogrula

---

### Kural 4 -- Tag = Kontrollu Taksonomi

Yeni tag eklemek = SCHEMA.md'yi degistirmek. Gatekeeper kurali:

Yeni tag ihtiyaci dogdugunda:
1. Once SCHEMA.md'de var mi kontrol et
2. Yoksa: bu tag gercekten gerekli mi? (2+ sayfa kullanacak mi?)
3. Gerekli ise SCHEMA.md'ye ekle, sonra sayfaya yaz
4. Tek kullanimlik ise sayfada kullanma, mevcut tag'lerden birini tercih et

**Tag temizligi proseduru:**
1. Lint `Unknown tags` raporunu al
2. Her unknown tag icin:
   - 2+ sayfada kullaniliyorsa -> SCHEMA.md'ye ekle
   - Tek sayfada kullaniliyorsa -> o sayfadan kaldir, mevcut esdeger tag kullan
3. SCHEMA.md guncellendikten sonra lint tekrar calistir

---

### Kural 5 -- Raw = Gecici Depo

`raw/` dizini git history'nin yerini tutmaz. Sadece "su an aktif" kaynaklar.

| Yas | Eylem |
|-----|-------|
| <6 ay | `raw/articles/` tut, wiki sayfasi `sources:` alaninda referans versin |
| 6-12 ay | Eski raw'lari temizle, git history'de korunur |
| >12 ay | Kesinlikle sil. Gerekiyorsa `git show <commit>:path/to/file` ile bul |

**Raw temizligi proseduru:**
1. `ls -lt wiki/raw/articles/` -> en eski dosyalari belirle
2. Her dosya icin: kaynak wiki sayfasi hala `sources:` ile referans veriyor mu?
3. Referans yoksa ve 6+ ay eskiyse sil
4. Referans varsa ama 12+ ay eskiyse: wiki sayfasindan `sources:` kaldir, sonra raw'u sil

---

### Kural 6 -- Archive = Yumusak Silme

Stale icerik hemen silinmez, yumusak gecis.

Arsivleme proseduru:
1. Sayfa frontmatter'ina `status: archived`, `tags: [stale]` ekle
2. Sayfayi `wiki/_archive/<sayfa-adi>.md` tasiy
3. Eski konumuna yonlendirme notu birak (opsiyonel, kisa)
4. `index.md` ana bolumlerinden bu sayfanin linkini kaldir
5. `index.md`'nin `## Archived Pages` bolumune duz metin ekle: `Sayfa-Adi (archived YYYY-MM-DD)`
6. Bu sayfaya wikilink veren diger sayfalari guncelle -> eski wikilink yerine duz metin + "(arsivlendi)"
7. `log.md`'ye giris yap

> **Kritik not:** `_archive/` dizini lint tarafindan excluded kabul edilir. Arsivlenmis sayfalara `\[\[sayfa-adi\]\]` seklinde wikilink vermek **broken link** olarak gorunur (ornek: ~~`\[\[eski-sayfa\]\]`~~). Bu yuzden arsivlenmis sayfalara hicbir yerden wikilink verme. Sadece duz metin + "(Arsivlendi)" kullan.

Tam silme proseduru (12+ ay arsivde kaldiktan sonra):
1. Kullanici onayi al
2. `_archive/` dosyasini sil
3. `index.md`'den `## Archived Pages` bolumunden kaldir
4. Raw kopyasini da sil (eger varsa)

---

