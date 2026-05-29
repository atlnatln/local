---
title: "Wiki Agent Instructions"
created: "2026-05-10"
updated: "2026-05-24"
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
> 1. `wiki topla` / `wiki ingest` — Proje kodundan `wiki-assistant.py` tarafından otomatik ingest
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

## KIRMIZI ALARM -- Limit Aşımı ve Erken Uyarı

Lint `Page Size` kontrolü otomatik raporlar. Manuel alarm tablosuna gerek yok.

| Seviye | Koşul | Eylem |
|--------|-------|-------|
| 🟢 Normal | < limit %90 | İzleme |
| 🟡 Uyarı | >= limit %90 | Sub-page planla |
| 🔴 Alarm | >= limit | Hemen böl veya indir |
| 🚨 Kritik | >= limit %120 | Acil müdahale |

**Kural:** Dosya şişmişse düzenlenir/indirilir. Büyüme hızı tahmini yapılmaz.

---

## Wiki Sağlık ve Bakım Protokolü

### Manuel Tetik

Bu mekanizma **otomatik değil**.
Kullanıcı "wiki bakım" / "wiki sağlık" / "haftalık bakım" dediğinde çalışır.

Agent session başında wiki sağlık durumunu otomatik kontrol **etmez**.
Sadece kullanıcı açıkça istediğinde lint çalıştırir, rapor üretir, düzeltme yapar.

Kullanıcı "wiki durum nedir" / "wiki ne durumda" dediğinde ise salt okunur özet rapor verilir (değişiklik yapılmaz).

> **Not:** `wiki topla` / `wiki ingest` komutları bu dosyaya ait değildir. Ingest işlemleri için üst dizin `AGENTS.md`'ye bakın. Orada `wiki-assistant.py` asistanlı akış tanımlanmıştır.

---

## `wiki bakım` Komutu

Kullanıcı "wiki bakım" / "wiki sağlık" / "haftalık bakım" dediğinde tek seferde:

| Adım | İşlem |
|------|-------|
| 1 | Git sync kontrolü (fetch + behind/ahead) |
| 2 | Lint Page Size kontrolü (limit aşımı varsa önce raporla) |
| 3 | Lint çalıştır -> sonucu analiz et |
| 3b| wiki/AGENTS.md değişikliği varsa ATLA (bu instruction dosyası, ingest kapsamında değil) |
| 4 | **Kontrollü büyüme kurallarını uygula** (bu bölümün altındaki 6 kural) |
| 5 | Otomatik düzeltme (fix'lenebilen warning'ler) |
| 6 | `.weekly-report` üret |
| 7 | Değişiklik varsa `git add -A && git commit --no-verify -m "chore(wiki): weekly maintenance"` |
| 8 | Push |

---

## Kontrollü Büyüme Protokolü

> Detaylı rehber: [[wiki-growth-protocol|Kontrollü Büyüme Protokolü →]]

## Otomatik Düzeltme Yetenekleri

Agent şu lint sorunlarını otomatik fix'leyebilir:

- **Orphan pages** -> `index.md`'ye wikilink ekle
- **Missing from index** -> İlgili kategoriye ekle
- **Tag audit** -> Bilinmeyen tag'leri `SCHEMA.md`'ye öner veya sayfadan kaldır
- **Oversized** -> TOC ekle, bölüm çıkarma önerisi ver

Manuel müdahale gerektirenler:

- **Broken wikilinks** -> Kaynak sayfayı incele, hedefi düzelt veya arşivle
- **Contradictions** -> `contested: true` işaretle, kullanıcıya sor
- **Stale content** -> Manuel review gerekir

---

## Rapor Formatı (`.weekly-report`)

Agent tarafından üretilen rapor sablonu:

```
Wiki Haftalık Bakım Raporu
Tarih: {YYYY-MM-DD HH:MM}
Makine: LOCAL

--- Lint ---
Sonuç: {X}/{Y}
Warning: {N}
Failure: {N}
Durum: {emoji} {Mükemmel|Kontrol gerekli}

--- Büyüme Metrikleri ---
Toplam sayfa: {N}
Yeni sayfa (bu hafta): {N}
Log giriş sayısı: {N}
Log zincir durumu: {Aktif|Arsivlendi}

--- Alarm ---
{Kırmızı alarm varsa listele, yoksa "Yok"}

--- Otomatik Fix'ler ---
- [FIXED] Orphan: Sayfa-Adı -> index.md'e eklendi
- [FIXED] Tag: unknown-tag -> SCHEMA.md'ye eklendi
- [SKIPPED] Broken: Eski-Sayfa -> hedef bulunamadı
- [PLANNED] Oversized: meb-2024-curriculum... -> sub-page bölünmesi gerekli

--- Sonraki Adımlar ---
- ...
```

---

## Bakım Checklist

### Acil Müdahale (Her `wiki bakım`'da)
- [ ] Lint Page Size kontrolü -- limit aşımı varsa önce sub-page planla
- [ ] log.md giriş sayısı 500+ mi? -> Zincirle
- [ ] Lint sonuçlarını log.md'den log-lint-archive.md'ye taşıyarak temizle

### Haftalık (Pazar veya kullanıcı istediğinde)
- [ ] Lint çalıştır, sonucu analiz et
- [ ] Kontrollü büyüme kurallarını kontrol et (oversized, log zinciri, tag audit)
- [ ] Gereksiz girişleri kaldır
- [ ] `.weekly-report` üret
- [ ] Bakım değişikliklerini commit: `chore(wiki): weekly maintenance`
- [ ] `.weekly-report`'u ayrı commit'le: `docs(wiki): weekly report`
- [ ] Push

### Aylık (Ayın ilk haftası)
- [ ] Raw/ dizini temizliği (6+ ay eski)
- [ ] Stale sayfa kontrolü (3 ay+ güncellenmemiş)
- [ ] Index kategori yapisi kontrolü (50+ sayfa mı?)
- [ ] Arsivde 12+ ay kalan sayfaları tam silme değerlendirmesi

---

## Wiki Editor Davranış Kuralları

- Her wiki sayfası değişikliğinde `updated:` frontmatter'ini güncelle
- Yeni sayfa oluştururken `references/CONVENTIONS.md` ve `references/PAGE_TEMPLATES.md`'ye uy
- Wikilink kullan, URL kullanma
- Kod bloklarında `// file: path/to/file.ext` yorumu zorunlu
- Sayfa limitlerine dikkat et: project 400, concept 350, decision 200 satır
- **Limit aşılıyorsa sayfayı uzatma, yeni sayfa aç** -- yatay büyüme
- **Yeni tag kullanmadan önce SCHEMA.md kontrolü yap** -- gatekeeper kuralı
- **Acele etmeden, adım adım ve kararlı ilerle**; önce dosyayı tam oku, sonra böl, sonra lint çalıştır
- **`.assistant-index.json` cache dosyasına dokunma** — Bu dosya `wiki-assistant.py` tarafından yönetilir, elle silinmemeli
- Kullanıcı wiki kapasitesini veya yapılacakları sorduğunda önce lint Page Size sonuçlarına ve limit aşımlarına bak
- Sub-page çıkarma sonrası mutlaka lint çalıştır; tek kullanımlık tag'leri temizle

---

> Son güncelleme: 2026-05-30
> Aktif mekanizma: kimi-cli proaktif bakım + wiki-assistant.py ingest
> Büyüme modeli: Kontrollü yatay büyüme (dikey sisme yasak)
> Sorumluluk: Sadece wiki bakımı ve temizliği. Ingest (`wiki topla`) üst dizin AGENTS.md'deki asistanlı akışa aittir.
> Log arsivi örneği: [[log-2026-H1]]
