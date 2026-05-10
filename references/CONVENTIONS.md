# Agent Davranis Referansi — LLM Wiki Kurallari

> Bu dokuman, ajanin `/home/akn/local/wiki/` altindaki LLM Wiki'yi nasil yazacagini,
> guncelleyecegini ve surdurecegini tanimlar. Wiki yapi tanimi icin bkz. `[[SCHEMA.md|Wiki Yapi Tanimi]]`.

---

## 1. Yazim Stili Kurallari

### 1.1 Ton ve Icerik

- **Factual (gercek temelli), oz, yapilandirilmis.** Hicbir bos laf (fluff) yok.
- Her iddia mutlaka bir kaynak dosyaya izlenebilir olmali.
- Varsayimlar acikca `> Not:` veya `> Varsayim:` ile isaretlenmeli.
- Cikarimlar (`infer`) ile kaynak referansi (`cite`) birbirinden ayri tutulmali.

### 1.2 Wikilink Kullanimi

- Wiki sayfalari arasi capraz referanslarda `[[Sayfa-Adi]]` soz dizimi kullanilir.
- Istege bagli gorunen isim icin: `[[Sayfa-Adi|gorunen metin]]`.
- Hicbir sayfa yalnizca URL ile referans vermemeli; wiki ici baglantilar wikilink ile yapilir.
- Dis kaynaklara referans icin standart Markdown baglantisi `[metin](url)` kullanilir.

### 1.3 Icerik Sunumu

| Durum                    | Kullanim                         |
|--------------------------|----------------------------------|
| Karsilastirma            | Tablo (Markdown table)           |
| Listeleme / Sralama      | Bullet list (`-`, `*`)           |
| Sirali adimlar           | Numarali liste (`1.`, `2.`)      |
| Kod ornegi               | Fenced code block + dil etiketi  |
| Uyari / Dikkat           | Blockquote `> Uyari:`            |

### 1.4 Kod Bloklari

Her kod blogu iki zorunlu bilesen icerir:

```markdown
    ```python
    # file: src/uygulama/modul.py
    def ornek():
        pass
    ```
```

- **Dil etiketi:** Kodun yazildigi programlama dili (`python`, `javascript`, `yaml`, vb.).
- **Dosya yoru:** Ilk satir `# file: <yol>` formatinda kaynak dosya referansi.

---

## 2. Sayfa Yasam Dongusu Kurallari

### 2.1 Ingest Sirasinda

- Yeni kaynak dosyalar icin wiki sayfasi **olusturulur**.
- Mevcut kaynak dosyalarda degisiklik varsa sayfa **guncellenir**.
- Hicbir sayfa **silinmez** — silme yerine arsivleme proseduru uygulanir.
- Yeni sayfa olusturulunca `index.md` + ilgili alt index'e (`concepts-index`, `projects-index`, `decisions-index`, `analysis-index`) ekle.
- Yeni kategori index'i olusturulunca diger tum kategori index'lerine capraz link ekle (orphan olmasin).

### 2.2 Kaynak Dosya Silindiginde (`git diff D`)

```yaml
---
title: Eski Proje Modulu
status: archived
tags: [stale]
---
```

1. Sayfa frontmatter'ina `status: archived` ve `[STALE]` etiketi eklenir.
2. Sayfa `_archive/` dizinine tasinir.
3. Eski konumunda bir yonlendirme notu birakilir: `> Bu sayfa arsivlendi. Guncel versiyon icin bkz. [[Yeni-Sayfa]]`.

### 2.3 Kaynak Dosya Yeniden Adlandirildiginda (`git diff R`)

1. Eski sayfa `_archive/` altina arsivlenir, `status: archived` atanir.
2. Yeni isimle yeni wiki sayfasi olusturulur.
3. Iki sayfa arasinda cift yonlu capraz baglanti (`[[Eski|Yeni]]`) eklenir.

### 2.4 Icerik Celiskisi Oldugunda

Mevcut wiki icerigi ile yeni ingest sonucu celiski varsa:

```yaml
---
title: Proje Karari
contested: true
---
```

1. Frontmatter'da `contested: true` olarak isaretlenir.
2. Iki versiyon da (eski ve yeni) ayni sayfada tutulur, her biri kendi kaynagiyla birlikte.
3. Sessizce uzerine yazma (silent overwrite) **yasaktir**.
4. Celiski, bir karar sayfasi (`type: decision`) ile cozume kavusturulana kadar `contested` kalir.

### 2.5 Git Diff Durumlari (A/M/D/R) — Tam Referans

| Status | Anlami | Wiki Eylemi |
|--------|--------|-------------|
| `A` (Added) | Yeni dosya eklendi | Yeni wiki sayfasi olustur, capraz referans kur |
| `M` (Modified) | Mevcut dosya degisti | Ilgili wiki sayfasini guncelle, capraz referanslari yenile |
| `D` (Deleted) | Dosya silindi | Sayfaya `[STALE]` ekle, `_archive/` tasiyip index'ten cikar |
| `R` (Renamed) | Dosya yeniden adlandirildi | Eski sayfayi arsivle, yenisini olustur, ikisi arasi capraz baglanti kur |

### 2.6 Archive → Index Update Rule

Bir sayfa `_archive/` tasindiginda:

1. `index.md` ana bolumlerinden bu sayfanin baglantisini kaldir.
2. `index.md`'nin `## Archived Pages` bolumune duz metin olarak ekle: `PageName (archived YYYY-MM-DD)`
3. Bu sayfaya wikilink veren diger sayfalari guncelle — `[[PageName]]` yerine duz metin + "(arsivlendi)" yaz.
4. Islemi `log.md`'ye kaydet.

### 2.7 Recent Commits Auto-Refresh

Her ingest sonrasinda, ilgili proje sayfasinin `## Recent Commits` bolumu otomatik yenilenir:

```bash
# Ayri git reposu olan projeler:
cd <proje-dizini> && git log --oneline -5

# Monorepo icindeki projeler:
cd /home/akn/local && git log --oneline -5 -- <proje-yolu>
```

Cikti su formatta yazilir:

```markdown
## Recent Commits
- `a1b2c3d` Description burada (2025-05-01)
- `e4f5g6h` Diger description (2025-04-28)
```

Bu bolum `<!-- AUTO-REFRESHED -->` HTML yorumu ile isaretlenir.

---

## 3. Frontmatter Standartlari

### 3.1 Zorunlu Alanlar

Her wiki sayfasi asagidaki frontmatter alanlarini icermek zorundadir:

```yaml
---
title: "Sayfa Basligi"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
type: "project"      # project | concept | decision | index | log
tags:
  - "tag-bir"
  - "tag-iki"
---
```

| Alan      | Aciklama                                         |
|-----------|--------------------------------------------------|
| `title`   | Sayfanin insan tarafindan okunabilir basligi     |
| `created` | Sayfanin ilk olusturuldugu tarih (`YYYY-MM-DD`)  |
| `updated` | Son guncelleme tarihi (`YYYY-MM-DD`)             |
| `type`    | Sayfa turu: `project`, `concept`, `decision`, `index`, `log` |
| `tags`    | Etiket listesi — mutlaka SCHEMA.md onayli taksonomiden secilir |

### 3.2 Istege Bagli Alanlar

```yaml
---
sources:
  - "raw/articles/kaynak-dosya.py"
  - "raw/articles/konfigurasyon.yaml"
contested: false
status: "active"     # active | stale | archived | needs-review
---
```

| Alan       | Aciklama                                           |
|------------|----------------------------------------------------|
| `sources`  | Ham kopya dosya yollari (`raw/` altindan) listesi  |
| `contested`| Icerik celiskisi varsa `true`, yoksa `false`      |
| `status`   | Sayfa durumu: `active`, `stale`, `archived`, `needs-review` |

### 3.3 Etiket Taksonomisi

- Tum `tags` degerleri `SCHEMA.md` icinde tanimli onayli taksonomiden gelmelidir.
- Yeni etiket ihtiyaci dogarsa once `SCHEMA.md` guncellenir, sonra sayfa etiketlenir.
- Etiketler kebap-case (kisa-cizgili-kucuk-harf) formatinda yazilir.

---

## 4. Capraz Referans Disiplini

### 4.1 Baglanti Kurallari (Sayfa Turune Gore)

| Sayfa Turu  | Baglamasi Gerekenler                                    |
|-------------|----------------------------------------------------------|
| `project`   | Kendi bagimliliklarina (`[[bagimli-proje]]`) ve kendisine bagimli projelere |
| `concept`   | O konsepti kullanan tum `project` sayfalarina            |
| `decision`  | Kararin etkiledigi tum `project` sayfalarina             |
| `index`     | Tum ust-kategori ve alt-sayfalara                        |
| `log`       | Islem goren tum sayfalara (olusturulan, guncellenen, arsivlenen) |

### 4.2 Yetim Sayfa Kurali

- **Yetim sayfa (orphan page) yasaktir** — her sayfa en az bir baska wiki sayfasindan baglanmis olmalidir.
- Iki istisna vardir:
  - `SCHEMA.md` — yapi tanimi dokumani
  - `index.md` — ana dizin sayfasi
  - `log.md` — guncelleme gunlugu

### 4.3 Wikilink Cikintisi Kontrolu

- Her ingest sonrasi, hicbir wikilink'in karsiligi olmayan sayfa olup olmadigi kontrol edilir.
- Bozuk wikilink tespit edilirse `log.md`'ye `[[Hedef-Sayfa]] — baglanti kirigi` notu dusulur.

---

## 5. Guncelleme Gunlugu (Update Logging)

### 5.1 Log Formati

Her basarili ingest isleminden sonra `wiki/log.md` dosyasina asagidaki formatta bir giris **eklenir** (append):

```markdown
## [2024-01-15 14:32] ingest | proje-adi | a1b2c3d | 4 sayfa
- Files: A:3 M:5 D:1
- Pages created: [[yeni-sayfa-bir]], [[yeni-sayfa-iki]]
- Pages updated: [[mevcut-sayfa-uc]]
- Pages archived: [[eski-sayfa-dort]]
```

### 5.2 Log Girisi Bilesenleri

| Bilesen         | Aciklama                                          |
|-----------------|---------------------------------------------------|
| `## [TARIH SAAT]` | ISO formatinda zaman damgasi                     |
| `ingest`        | Islem turu (sabit: `ingest`)                      |
| `<project>`     | Islem yapilan proje adi                           |
| `<commit-sha>`  | Islenen commit'in kisa SHA'si (7 karakter)        |
| `<pages-touched>` | Etkilenen toplam sayfa sayisi                   |
| `A:X M:Y D:Z`   | Eklendigi / Degistirildigi / Silindigi dosyalar |

### 5.3 Kronolojik Siralama

- Girisler **en eskiden en yeniye** siralanir (append-only).
- En yeni giris dosyanin en sonunda olur.
- Hicbir giris silinmez veya yeniden siralanmaz.

---

## 6. Raw Arsiv Konvansiyonu

### 6.1 Ham Kopya Ilkeleri

```
wiki/
  raw/
    articles/
      kaynak-dosya.py       # <- kaynagin tam kopyasi
      konfigurasyon.yaml    # <- kaynagin tam kopyasi
```

- Kaynak dosya ingest edildiginde **mutlaka** `wiki/raw/articles/<filename>` yoluna kopyalanir.
- Ham kopyalar **degismez (immutable)** — uzerinde hicbir duzenleme yapilmaz.
- Ham kopya, wiki sayfasinin "gercek kaynagi" olarak hizmet eder.

### 6.2 Sources Referansi

- Wiki sayfasinin frontmatter `sources` alani, ham kopyanin `raw/` altindaki goreceli yolunu icerir.
- Ornek: `sources: ["raw/articles/src/app/main.py"]`
- Birden fazla kaynak dosya varsa liste halinde hepsi yazilir.

---

## 7. Dizin Bakimi (Index Maintenance)

### 7.1 Ingest Sonrasi Guncelleme

Her ingest tamamlandiktan sonra `wiki/index.md` guncellenir:

- Yeni olusturulan sayfalar dizine eklenir.
- Guncellenen sayfalarin `updated` tarihleri dizinde yansitilir.
- Arsivlenen sayfalar `_archive/` bolumune tasınır veya isaretlenir.
- Silinmis sayfalar dizinden cikarilir (ancak arsiv baglantisi kalir).

### 7.2 Erisilebilirlik Kurali

> **2 Tiklama Kurali:** Wiki'deki her sayfa, `index.md`'den baslayarak en fazla **2 tiklama** ile ulasilabilir olmalidir.

```
index.md
  -> Kategori Sayfasi (1. tiklama)
       -> Hedef Sayfa (2. tiklama)
```

- Duz sayfa listesi yerine kategorik yapilanma kullanilir.
- Her kategori altinda ilgili sayfalar `[[Sayfa-Adi]]` ile listelenir.

---

## 8. Git Checkpoint Yonetimi

### 8.1 Checkpoint Dosyasi Yapisi

Her takip edilen proje icin:

```
.checkpoints/
  proje-adi.sha      # Son basarili ingest'in commit SHA'si
```

- Dosya icerigi yalnizca tek bir satirdan olusur: o projenin son islenen commit SHA'si.
- Ornek: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

### 8.2 Checkpoint Guncelleme Kurallari

| Durum                          | Checkpoint SHA Guncellenir mi? |
|--------------------------------|--------------------------------|
| Ingest basarili tamamlandi     | **Evet** → Mevcut HEAD SHA'ya guncellenir |
| Ingest yarida basarisiz oldu   | **Hayir** — eski SHA korunur, islenmemis degisiklikler bir sonraki cagrida tekrar islenir |
| Hicbir dosya degisikligi yok   | Hayir — SHA zaten guncel       |

### 8.3 Checkpoint Amaci

- Checkpoint, "nerede kaldik" sinirini isaretler.
- Eger ingest yarida kesilirse, bir sonraki `ingest` cagrisi checkpoint SHA'sindan baslayarak kalan degisiklikleri isler.
- Bu mekanizma, **idempotent** (tekrar guvenli) ingest islemi saglar.

---

## 9. Git Strategy (Monorepo + Sub-repos)

| Proje | Git Root | Checkpoint | Tip |
|-------|----------|------------|-----|
| ops-bot | `ops-bot/.git` | `.checkpoints/ops-bot.sha` | Ayri repo |
| webimar | `projects/webimar/.git` | `.checkpoints/webimar.sha` | Ayri repo |
| anka, mathlock-play, telegram-kimi, sayi-yolculugu, infrastructure | `/home/akn/local/.git` | `.checkpoints/local.sha` | Monorepo |

---

## 10. Log Format (Guncel — Diff Summary + Revert)

Her log girisi su formatta:

```markdown
## [YYYY-MM-DD HH:MM] ingest | <project> | <commit-sha> | <pages-touched>
- Files: A:3 M:5 D:1
- Pages created: [[page1]], [[page2]]
- Pages updated: [[page3]]
- Pages archived: [[old-page]]
- Diff summary: Added systemd service section to [[ops-bot]]. Cross-linked [[nginx]] in [[infrastructure]].
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
- Revert: git checkout <previous-commit-sha> -- wiki/
```

**Diff summary:** Ne yapildigini 1-2 cumlede ozetle. "Added X to [[Page]]. Cross-linked [[Y]]."
**Revert:** Eger bir seyler ters giderse, wiki'yi onceki haline dondurmek icin kullanilacak git komutu.

---

## 11. `related:` Frontmatter Kurali

Tum sayfa tiplerinde (`project`, `concept`, `decision`, `index`) `related:` alani zorunludur. Bu alan, sayfanin bagli oldugu diger wiki sayfalarini listeler:

```yaml
---
title: "Proje Adi"
type: project
tags: [project, django, nextjs]
related:
  - django-nextjs-pattern
  - deployment
  - infrastructure
---
```

Kurallar:

- Her sayfa en az 1, tercihen 2-5 `related` baglantisi icermeli.
- `related` hedefleri gercekten var olan (veya planlanan) sayfalara isaret etmeli.
- Concept sayfalarinda kullanan projeler, project sayfalarinda ilgili concept'ler listelenir.

---

## 12. Ozet: Hizli Referans Tablosu

| Kural                    | Kisa Cevap                                    |
|--------------------------|-----------------------------------------------|
| Yazim tonu               | Factual, oz, yapilandirilmis                  |
| Capraz referans          | `[[Wikilink]]` kullan                         |
| Git diff A               | Yeni sayfa olustur, capraz referans kur       |
| Git diff M               | Sayfayi guncelle, capraz referanslari yenile  |
| Git diff D               | `[STALE]` + `status: archived` + `_archive/` + index'ten cikar |
| Git diff R               | Eski arsivlenir, yeni olusturulur, capraz baglanti |
| Icerik celiskisi         | `contested: true`, sessiz uzerine yazma yok   |
| Frontmatter zorunlu      | `title`, `created`, `updated`, `type`, `tags` |
| Frontmatter `related`    | Zorunlu, 2-5 wikilink hedefi                  |
| Yetim sayfa              | Yasak (SCHEMA.md, index.md, log.md haric)     |
| Log formati              | `## [TARIH SAAT] ingest | proje | sha | sayfa` + `Diff summary` + `Revert` |
| Ham kopya                | `raw/articles/<filename>`, degismez           |
| 2 Tiklama kurali         | index.md'den her sayfa en fazla 2 tik         |
| Checkpoint               | Basarili ingest sonrasi HEAD SHA'ya guncelle  |
| Archive → Index          | Baglantiyi kaldir, `## Archived Pages` ekle, wikilink'leri duz metne cevir |
| ADR vs Concept           | ADR = mimari karar (teknik secim, pattern, altyapi, guvenlik). Concept = surec/bilgi notu |
| ADR Superseded           | Eski: `status: Superseded` + `superseded_by`. Yeni: `status: Active` + `supersedes`. Index'te tasima |
| ADR sayfa adi            | `adr-NNN-kisa-baslik.md` formati, 3 haneli zero-padded |
| Recent Commits           | `git log --oneline -5`, `<!-- AUTO-REFRESHED -->` ile isaretle |
| Git strategy             | Ayri repo veya monorepo — tabloya bak         |
| ADR yazim kurali         | Context → Decision → Consequences → Alternatives → Status |
| ADR minimum icerik       | En az 1 alternatif, 1 pozitif, 1 negatif sonuc |
| ADR cross-link           | Proje sayfasina ## Decisions, konsept sayfasina ## Related Decisions |
