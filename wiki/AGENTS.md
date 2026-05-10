---
title: "Wiki Agent Instructions"
created: "2026-05-10"
updated: "2026-05-10"
type: index
tags: [meta]
related: []
---

<!-- ⚠️ KRİTİK HATIRLATMA: Bu dizin (/home/akn/local/wiki) için bu dosya EN ÖNCELİKLİ AGENTS.md'dir. Üst dizindeki (/home/akn/local/AGENTS.md) kuralları ile çakışma durumunda, wiki/AGENTS.md'deki yönergeler geçerlidir. Wiki işlemlerinde (sayfa düzenleme, sub-page çıkarma, log zincirleme, tag audit, arşivleme vb.) önce bu dosyaya bak. -->

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
> **Bilgi giriş kanalları:**
> 1. `wiki topla` / `wiki ingest` — Proje kodundan otomatik/wiki-agent tarafından
> 2. Manuel ADR/concept ekleme — Karar/ analiz sonrası agent veya insan tarafından
> 3. `wiki bakım` — Bakım agent'ı tarafından yapılan düzenleme ve temizlik
>
> Her giriş bir sistem/düzen dahilinde yapılır. Sen bu düzeni koruyan kişisin.
> Düzenli bir arşiv, dışarıdan arama yapan diğer ajanların aradığını kolayca bulmasını sağlar.

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
| Index linkleri | Inbound link sayımı | `index.md` lint'te excluded'dur; sub-index'ler birbirine cross-link vermeli |

---

## KIRMIZI ALARM -- Su An Acil Durumlar

> Bu bolum, "wiki bakim" komutu calistiginda kontrol edilir. Agent'in session basinda veya baska zamanlarda otomatik kontrol etmesi beklenmez.

| # | Sorun | Neden Acil | Mudahale Suresi |
|---|-------|-----------|----------------|
| 1 | `analysis/meb-2024-curriculum...` **525 satir** (limit 350) | %50 limit asimi. Her MEB guncellemesinde buyur | **Hemen sub-page'e bol** |
| 2 | `concepts/kimi-code-cli` **418 satir** (limit 350) | %20 limit asimi. Her kimi-cli versiyonunda buyur | **Hemen sub-page'e bol** |
| 3 | `projects/mathlock-play-android` **348 satir** | 2 hafta icinde 400 limiti | Sub-page planla |
| 4 | `projects/ops-bot` **346 satir** | 3 hafta icinde 400 limiti | Sub-page planla |

**Alarm tetiklendiginde:** Kullaniciya "Wiki'de acil durum var: X sayfasi limit asimi. Hemen mudahale edelim mi?" diye sor.

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

> Detayli rehber: [[wiki-growth-protocol|Kontrollu Buyume Protokolu →]]

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
- **Acele etmeden, adim adim ve kararli ilerle**; once dosyayi tam oku, sonra bol, sonra lint calistir
- Kullanici wiki kapasitesini veya yapilacaklari sordugunda once Kirmizi Alarmlara ve limit asimlarina bak
- Sub-page cikarma sonrasi mutlaka lint calistir; tek kullanimlik tag'leri temizle

---

> Son guncelleme: 2026-05-10
> Aktif mekanizma: kimi-cli proaktif bakim (scripts/wiki-weekly-maintenance.sh kaldirildi)
> Buyume modeli: Kontrollu yatay buyume (dikey sisme yasak)
> Sorumluluk: Sadece wiki bakimi ve temizligi. Ingest (`wiki topla`) ust dizin AGENTS.md'ye aittir.
> Log arsivi ornegi: [[log-2026-H1]]
> Acil durumlar: mathlock-play-android (348/400), ops-bot (346/400), sec-agent (343/400)
