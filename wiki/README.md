---
title: "Wiki Kullanım Kılavuzu"
created: 2026-05-01
updated: 2026-05-01
type: index
tags: [meta, guide]
related: []
---

# local-wiki Kullanım Kılavuzu

`/home/akn/local/wiki` — Kimi CLI tarafından yönetilen, sürekli güncellenen bilgi tabanı.

---

## Hızlı Başlangıç

Kimi CLI'yi `/home/akn/local` dizininde açtığında ajan otomatik olarak wiki skill'ini keşfeder. Şu komutları kullanabilirsin:

```bash
cd /home/akn/local
kimi
```

### Temel Komutlar

| Komut | Açıklama | Örnek |
|-------|----------|-------|
| `/wiki ingest` | Tüm projelerde değişiklik tara, wiki'yi güncelle | `/wiki ingest` |
| `/wiki ingest <proje>` | Sadece bir projeyi işle | `/wiki ingest ops-bot` |
| `/wiki query "<soru>"` | Wiki'den cevap ara ve sentezle | `/wiki query "deploy nasıl çalışıyor?"` |
| `/wiki lint` | Wiki sağlık kontrolü (10 madde) | `/wiki lint` |
| `/wiki status` | Checkpoint'leri ve sayfa sayısını göster | `/wiki status` |

---

## Ingest (Veri Alımı)

Kod değiştikçe wiki'yi güncel tutmak için en önemli komut.

### Ne Zaman Çalıştırılır?

- **Bir projede önemli değişiklik yaptıktan sonra**: yeni modül, refactor, deploy script değişikliği
- **Yeni bir proje eklediğinde**: `wiki ingest <proje>`
- **Haftalık bakım**: tüm projelerin son durumunu yakalamak için `/wiki ingest`

### Nasıl Çalışır?

1. Ajan her proje için `git diff --name-status` çalıştırır (son checkpoint'ten bu yana)
2. Değişen dosyaları analiz eder (A=eklendi, M=değiştirildi, D=silindi, R=ad değiştirildi)
3. İlgili wiki sayfalarını günceller veya yeni sayfa oluşturur
4. Çapraz referansları (`[[wikilink]]`) yeniler
5. `wiki/log.md`'ye kayıt atar
6. Checkpoint SHA'sını günceller

### Checkpoint Nedir?

`.checkpoints/` dizinindeki `.sha` dosyaları, her projenin son işlendiği git commit hash'ini tutar. Böylece ajan sadece değişen dosyaları işler, her seferinde tüm repoyu baştan taramaz.

```bash
wiki/.checkpoints/
├── local.sha      # /home/akn/local monorepo
├── ops-bot.sha    # ops-bot/ (ayrı git repo)
└── webimar.sha    # projects/webimar/ (ayrı git repo)
```

---

## Query (Sorgu)

Wiki'ye soru sormak için. Ajan önce `index.md`'yi okur, ilgili sayfaları bulur, sentezler ve cevap üretir.

### Örnek Sorular

- `/wiki query "ops-bot hangi servisleri yönetiyor?"`
- `/wiki query "webimar'da kaç farklı yapı türü hesaplanıyor?"`
- `/wiki query "anka'nın 3 aşamalı doğrulama hattı nedir?"`
- `/wiki query "mathlock AI soru döngüsü nasıl çalışıyor?"`

### Cevabı Wiki'ye Kaydetme

Eğer sorduğun sorunun cevabı uzun ve değerliyse, ajan bunu yeni bir **konsept sayfası** olarak kaydetmeyi teklif eder. Onay verirsen `wiki/concepts/` altında yeni bir sayfa oluşturur.

---

## Lint (Sağlık Kontrolü)

Wiki'nin yapısal bütünlüğünü denetler. 10 madde kontrol edilir:

1. **Orphan Pages** — Hiç kimse linklemeyen sayfalar
2. **Broken Wikilinks** — Var olmayan sayfaya link
3. **Index Completeness** — `index.md`'de eksik sayfa
4. **Frontmatter Validation** — Zorunlu alanlar eksik mi?
5. **Stale Content** — 90 günden eski güncelleme
6. **Contradictions** — Çelişkili bilgi flag'lenmiş mi?
7. **Page Size** — 200 satırdan uzun sayfa
8. **Tag Audit** — Tanımlı olmayan etiket kullanımı
9. **Raw Existence** — `sources:` frontmatter'daki dosya mevcut mu?
10. **Log Rotation** — `log.md` 500 girişi aşmış mı?

### Ne Zaman Çalıştırılır?

- **Haftalık bakım** rutininin bir parçası olarak
- **Büyük bir ingest sonrası** (10+ sayfa değiştiğinde)
- **Wiki'de bir şeyler tuhaf göründüğünde**

---

## Obsidian ile Açma

Wiki dizini standart Markdown + `[[wikilink]]` formatında. Obsidian'da açmak için:

1. Obsidian → "Open folder as vault" → `/home/akn/local/wiki` seç
2. Settings → Files and links → "Use [[Wikilinks]]" açık olduğundan emin ol
3. Graph View (Ctrl+G) ile bilgi ağını görselleştir

### Faydalı Obsidian Eklentileri

- **Dataview** — YAML frontmatter üzerinden sorgu (`TABLE tags FROM "projects"`)
- **Graph Analysis** — Merkezi sayfaları ve orphamları görsel tespit

---

## Wiki Sayfa Yapısı

Her sayfa YAML frontmatter ile başlar:

```yaml
---
title: "Sayfa Başlığı"
created: 2026-05-01
updated: 2026-05-01
type: project        # project | concept | decision | index | log
tags: [ops-bot, python, systemd]
related:
  - infrastructure
  - deployment
sources:
  - raw/articles/kaynak-dosya.md
---
```

### Alan Açıklamaları

| Alan | Zorunlu | Açıklama |
|------|---------|----------|
| `title` | Evet | Görünen başlık (60 karakter altı) |
| `created` | Evet | Oluşturma tarihi (`YYYY-MM-DD`) |
| `updated` | Evet | Son güncelleme tarihi |
| `type` | Evet | `project`, `concept`, `decision`, `index`, `log` |
| `tags` | Evet | Etiket dizisi. En az bir proje veya konsept etiketi |
| `related` | Evet | İlgili sayfalar (düz metin, wikilink body'de) |
| `sources` | Hayır | Ham kaynak dosya yolları |
| `contested` | Hayır | `true` = çelişkili bilgi var |
| `status` | Hayır | `active`, `stale`, `archived`, `needs-review` |

### Wikilink Kullanımı

Sayfalar arası bağlantı için çift köşeli parantez:

```markdown
[[ops-bot]] sayfasına git
[[deployment]] konseptini incele
```

Dosya adları `kebab-case.md`; link hedefleri `TitleCase` veya `kebab-case` olabilir, büyük-küçük harf duyarsız çözülür.

---

## Dizin Yapısı

```
wiki/
├── README.md              ← Bu dosya
├── SCHEMA.md              ← Wiki kuralları, etiket taksonomisi
├── index.md               ← İçerik kataloğu (tüm sayfalar burada listelenir)
├── log.md                 ← Kronolojik işlem kaydı (append-only)
├── system-overview.md     ← VPS genel mimarisi
├── projects/              ← Proje sayfaları
│   ├── index.md
│   ├── ops-bot.md
│   ├── webimar.md
│   ├── anka.md
│   ├── mathlock-play.md
│   └── infrastructure.md
├── concepts/              ← Çapraz konseptler
│   └── deployment.md
├── decisions/             ← Mimari kararlar (ADR)
├── raw/                   ← Değişmez kaynak kopyaları (ajana dokunma)
│   └── articles/
└── .checkpoints/          ← Git checkpoint hash'leri
    ├── local.sha
    ├── ops-bot.sha
    └── webimar.sha
```

---

## Sık Sorulan Sorular

**S: Kimi CLI açıldığında wiki skill'i otomatik mi çalışıyor?**  
C: Evet. `~/.kimi/skills/local-wiki/SKILL.md` dosyası otomatik keşfedilir. Sadece `/wiki ...` komutu verdiğinde aktif olur.

**S: Wiki sayfalarını ben mi yazıyorum, ajan mı?**  
C: Ajan yazıyor (ingest/query sırasında). Sen sadece komut veriyorsun, içeriği doğruluyorsun, yönlendiriyorsun.

**S: Manuel düzenleme yapabilir miyim?**  
C: Evet. Özellikle `decisions/` altındaki ADR sayfaları ve `README.md` senin alanın. Ajanın yazdığı sayfaları da düzeltebilirsin — sadece `updated` tarihini güncellemeyi unutma.

**S: Yeni proje eklemek istiyorum.**  
C: Projeyi `projects/` altına koy, sonra `wiki ingest <proje-adi>` komutunu çalıştır. Ajan sayfa oluşturur.

**S: log.md çok uzun oldu.**  
C: `/wiki lint` çalıştır. 500 girişi aştığında ajan otomatik rotate önerir.

---

## Sonraki Adımlar

1. `kimi` çalıştır
2. `/wiki status` ile mevcut durumu gör
3. Bir projede değişiklik yap
4. `/wiki ingest` ile wiki'yi güncelle
5. Obsidian'da `wiki/` dizinini vault olarak aç ve Graph View'i keşfet

> **İpucu:** Her hafta sonu `/wiki ingest && /wiki lint` komutlarını çalıştırmak wiki'yi taze ve tutarlı tutar.
