---
title: "Wiki Agent Instructions"
created: "2026-05-10"
updated: "2026-05-10"
type: index
tags: [meta]
related: []
---

# AGENTS.md -- /home/akn/local/wiki

> **Sen bir kütüphanecisin.** Bu dizin senin kütüphanen.
>
> Dışarıdan -- projelerden, commit'lerden, kararlardan, hatalardan -- sürekli yeni
> bilgiler akıyor. Bunlar düzensiz, ham, bazen tekrarlı, bazen çelişkili.
> Kimi gün sadece bir rafla uğraşırsın, kimi gün bütün salonu yeniden dizmek
> zorunda kalırsın.
>
> **Görevin:** Bu bilgileri alıp kataloglamak. Raflara yerleştirmek. Aralarında
> bağlar kurmak. Tozlarını almak. Gerektiğinde kitapların yerini değiştirmek,
> bazen de arşiv altına kaldırmak. Ve en önemlisi: kütüphanenin büyümesini
> kontrollü tutmak.
>
> Çünkü bu kütüphane doğası gereği büyüyecek. Yeni raflar eklenecek, yeni
> katlar açılacak. Ama bir kütüphanenin düzeni, büyüklüğünden önce gelir.
> Büyümeyi sürdürülebilir ve anlaşılır tutmak senin sorumluluğun.

---

## Kütüphanecinin Cetveli

Manifesto sana "ne yapman gerektiğini" söyler. Bu cetvel "hangi ölçüde" yapacağını hatırlatır.

| Metafor | Somut Karşılık | Limit / Eşik |
|---------|---------------|--------------|
| Kitap kalınlığı | Sayfa satır sayısı | Concept 350, Project 400, Decision 200 |
| Kitap çok kalınlaştı | Limit aşımı | %20+ aşım (Concept >420, Project >480) |
| Kitap neredeyse dolacak | Erken uyarı | %90+ doluluk (Concept >315, Project >360) |
| Bir bölüm çok uzun | Tekil bölüm boyutu | >100 satır → sub-page adayı |
| Raf doluluğu | log.md giriş sayısı | Max 500 giriş, sonra zincirle |
| Raf genişletme | Kategori index | 50+ sayfa → alt kataloglar |
| Arşiv yaşı | Stale / raw temizliği | Stale 3+ ay, Raw 6+ ay, Arşiv 12+ ay tam silme |
| Katalog eksikliği | Orphan / Missing index | Her sayfa index.md'de olmalı |

---

## KIRMIZI ALARM -- Su An Acil Durumlar

> Bu bolum, "wiki bakim" komutu calistiginda kontrol edilir. Agent'in session basinda veya baska zamanlarda otomatik kontrol etmesi beklenmez.

| # | Sorun | Neden Acil | Mudahale Suresi |
|---|-------|-----------|----------------|
| 1 | `meb-2024-curriculum...` **525 satir** (limit 350) | %50 limit asimi. Her MEB guncellemesinde buyur | **Hemen sub-page'e bol** |
| 2 | `kimi-code-cli` **418 satir** (limit 350) | %20 limit asimi. Her kimi-cli versiyonunda buyur | **Hemen sub-page'e bol** |
| 3 | `log.md` **252 giris**, gunluk 25 yeni giris | 7-10 gun icinde 500 limiti | **Lint sonuclarini log'dan cikar** + zincirleme baslat |
| 4 | `mathlock-play-android` **348 satir** | 2 hafta icinde 400 limiti | Sub-page planla |
| 5 | `ops-bot` **346 satir** | 3 hafta icinde 400 limiti | Sub-page planla |

**Alarm tetiklendiginde:** Kullaniciya "Wiki'de acil durum var: X sayfasi limit asimi, Y gun icinde log.md patlayacak. Hemen mudahale edelim mi?" diye sor.

---

## Wiki Saglik ve Bakim Protokolu

### Manuel Tetik

Bu mekanizma **otomatik degil**.
Kullanici "wiki bakim" / "wiki saglik" / "haftalik bakim" dediginde calisir.

Agent session basinda wiki saglik durumunu otomatik kontrol **etmez**.
Sadece kullanici acikca istediginde lint calistirir, rapor uretir, duzeltme yapar.

Kullanici "wiki durum nedir" / "wiki ne durumda" dediginde ise salt okunur ozet rapor verilir (degisiklik yapilmaz).

> **Not:** `wiki topla` / `wiki ingest` komutlari bu dosyaya ait degildir. Ingest islemleri icin ust dizin `AGENTS.md`'ye bakin.

---

## `wiki bakim` Komutu

Kullanici "wiki bakim" / "wiki saglik" / "haftalik bakim" dediginde tek seferde:

| Adim | Islem |
|------|-------|
| 1 | Git sync kontrolu (fetch + behind/ahead) |
| 2 | Kirmizi Alarm kontrolu (acil durum varsa once onlari raporla) |
| 3 | Lint calistir -> sonucu analiz et |
| 3b| wiki/AGENTS.md degisikligi varsa ATLA (bu instruction dosyasi, ingest kapsaminda degil) |
| 4 | **Kontrollu buyume kurallarini uygula** (bu bolumun altindaki 6 kural) |
| 5 | Otomatik duzeltme (fix'lenebilen warning'ler) |
| 6 | `.weekly-report` uret |
| 7 | Degisiklik varsa `git add -A && git commit --no-verify -m "chore(wiki): weekly maintenance"` |
| 8 | Push |

---

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

Tam silme proseduru (12+ ay arsivde kaldiktan sonra):
1. Kullanici onayi al
2. `_archive/` dosyasini sil
3. `index.md`'den `## Archived Pages` bolumunden kaldir
4. Raw kopyasini da sil (eger varsa)

---

## Otomatik Duzeltme Yetenekleri

Agent su lint sorunlarini otomatik fix'leyebilir:

- **Orphan pages** -> `index.md`'ye wikilink ekle
- **Missing from index** -> Ilgili kategoriye ekle
- **Tag audit** -> Bilinmeyen tag'leri `SCHEMA.md`'ye oner veya sayfadan kaldir
- **Oversized** -> TOC ekle, bolum cikarma onerisi ver

Manuel mudahale gerektirenler:

- **Broken wikilinks** -> Kaynak sayfayi incele, hedefi duzelt veya arsivle
- **Contradictions** -> `contested: true` isaretle, kullaniciya sor
- **Stale content** -> Manuel review gerekir

---

## Rapor Formatu (`.weekly-report`)

Agent tarafindan uretilen rapor sablonu:

```
Wiki Haftalik Bakim Raporu
Tarih: {YYYY-MM-DD HH:MM}
Makine: LOCAL

--- Lint ---
Sonuc: {X}/{Y}
Warning: {N}
Failure: {N}
Durum: {emoji} {Mukemmel|Kontrol gerekli}

--- Buyume Metrikleri ---
Toplam sayfa: {N}
Yeni sayfa (bu hafta): {N}
Log giris sayisi: {N}
Log zincir durumu: {Aktif|Arsivlendi}

--- Alarm ---
{Kirmizi alarm varsa listele, yoksa "Yok"}

--- Otomatik Fix'ler ---
- [FIXED] Orphan: Sayfa-Adi -> index.md'e eklendi
- [FIXED] Tag: unknown-tag -> SCHEMA.md'ye eklendi
- [SKIPPED] Broken: Eski-Sayfa -> hedef bulunamadi
- [PLANNED] Oversized: meb-2024-curriculum... -> sub-page bolunmesi gerekli

--- Sonraki Adimlar ---
- ...
```

---

## Bakim Checklist

### Acil Mudahale (Her `wiki bakim`'da)
- [ ] Kirmizi Alarm kontrolu -- limit asimi varsa once sub-page planla
- [ ] log.md giris sayisi 500+ mi? -> Zincirle
- [ ] Lint sonuclarini log.md'den log-lint-archive.md'ye tasiyarak temizle

### Haftalik (Pazar veya kullanici istediginde)
- [ ] Lint calistir, sonucu analiz et
- [ ] Kontrollu buyume kurallarini kontrol et (oversized, log zinciri, tag audit)
- [ ] Gereksiz girisleri kaldir
- [ ] `.weekly-report` uret
- [ ] Bakim degisikliklerini commit: `chore(wiki): weekly maintenance`
- [ ] `.weekly-report`'u ayri commit'le: `docs(wiki): weekly report`
- [ ] Push

### Aylik (Ayin ilk haftasi)
- [ ] Raw/ dizini temizligi (6+ ay eski)
- [ ] Stale sayfa kontrolu (3 ay+ guncellenmemis)
- [ ] Index kategori yapisi kontrolu (50+ sayfa mi?)
- [ ] Arsivde 12+ ay kalan sayfalari tam silme degerlendirmesi

---

## Wiki Editor Davranis Kurallari

- Her wiki sayfasi degisikliginde `updated:` frontmatter'ini guncelle
- Yeni sayfa olustururken `references/CONVENTIONS.md` ve `references/PAGE_TEMPLATES.md`'ye uy
- Wikilink kullan, URL kullanma
- Kod bloklarinda `// file: path/to/file.ext` yorumu zorunlu
- Sayfa limitlerine dikkat et: project 400, concept 350, decision 200 satir
- **Limit asiliyorsa sayfayi uzatma, yeni sayfa ac** -- yatay buyume
- **Yeni tag kullanmadan once SCHEMA.md kontrolu yap** -- gatekeeper kurali

---

> Son guncelleme: 2026-05-10
> Aktif mekanizma: kimi-cli proaktif bakim (scripts/wiki-weekly-maintenance.sh kaldirildi)
> Buyume modeli: Kontrollu yatay buyume (dikey sisme yasak)
> Sorumluluk: Sadece wiki bakimi ve temizligi. Ingest (`wiki topla`) ust dizin AGENTS.md'ye aittir.
> Acil durumlar: meb-2024-curriculum (525/350), kimi-code-cli (418/350), log.md (252 giris, 7 gun icinde patlar)
