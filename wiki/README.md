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

| Komut | Türkçe | Açıklama | Örnek |
|-------|--------|----------|-------|
| `wiki ingest` | `wiki güncelle`, `wiki topla`, `wiki ekle` | Tüm projelerde değişiklik tara, wiki'yi güncelle | `wiki topla` |
| `wiki ingest <proje>` | `wiki güncelle <proje>` | Sadece bir projeyi işle | `wiki güncelle ops-bot` |
| `wiki query "<soru>"` | `wiki sor`, `wiki ara` | Wiki'den cevap ara ve sentezle | `wiki sor "deploy nasıl çalışıyor?"` |
| `wiki lint` | `wiki kontrol`, `wiki tara` | Wiki sağlık kontrolü (10 madde) | `wiki kontrol` |
| `wiki status` | `wiki durum`, `wiki özet` | Checkpoint'leri ve sayfa sayısını göster | `wiki durum` |

---

## Ingest (Veri Alımı)

Kod değiştikçe wiki'yi güncel tutmak için en önemli komut.

### Ne Zaman Çalıştırılır?

- **Bir projede önemli değişiklik yaptıktan sonra**: yeni modül, refactor, deploy script değişikliği
- **Yeni bir proje eklediğinde**: `wiki güncelle <proje>`
- **Haftalık bakım**: tüm projelerin son durumunu yakalamak için `wiki topla`

### Nasıl Çalışır?

1. Ajan her proje için `git diff --name-status` çalıştırır (son checkpoint'ten bu yana)
2. Değişen dosyaları analiz eder (A=eklendi, M=değiştirildi, D=silindi, R=ad değiştirildi)
3. İlgili wiki sayfalarını günceller veya yeni sayfa oluşturur
4. Çapraz referansları (çift köşeli parantez linkleri) yeniler
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

- `wiki sor "ops-bot hangi servisleri yönetiyor?"`
- `wiki sor "webimar'da kaç farklı yapı türü hesaplanıyor?"`
- `wiki sor "anka'nın 3 aşamalı doğrulama hattı nedir?"`
- `wiki sor "mathlock AI soru döngüsü nasıl çalışıyor?"`

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

Wiki dizini standart Markdown + çift köşeli parantez link formatında. Obsidian'da açmak için:

1. Obsidian → "Open folder as vault" → `/home/akn/local/wiki` seç
2. Settings → Files and links → "Use Wikilinks" açık olduğundan emin ol
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

Detaylı şema için bkz. [[SCHEMA]].

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
├── README.md          ← Bu dosya
├── SCHEMA.md          ← Wiki kuralları
├── index.md           ← İçerik kataloğu
├── log.md             ← İşlem kaydı
├── system-overview.md ← VPS mimarisi
├── projects/          ← Proje sayfaları
├── concepts/          ← Çapraz konseptler
├── decisions/         ← Mimari kararlar
├── raw/               ← Kaynak kopyaları
└── .checkpoints/      ← Git checkpoint'leri
```

---

## Sık Sorulan Sorular

**S: Wiki sayfalarını ben mi yazıyorum, ajan mı?**
C: Ajan yazıyor (ingest/query sırasında). Sen komut verip doğruluyorsun.

**S: Manuel düzenleme yapabilir miyim?**
C: Evet. `decisions/` ve `README.md` senin alanınız. `updated` tarihini güncellemeyi unutma.

**S: Yeni proje eklemek istiyorum.**
C: `projects/` altına koy, sonra `wiki ingest <proje>` çalıştır.

**S: log.md çok uzun oldu.**
C: `wiki kontrol` çalıştır. 500 girişi aştığında rotate önerir.

---

## Proaktif Güncelleme (Auto-Prompt)

Git commit attığında kimi-cli bir sonraki açılışında otomatik olarak "wiki güncelleyelim mi?" diye sorar.

### Nasıl Çalışır?

1. **Git hook** (`post-commit`): Her commit sonrası `wiki/.pending` marker dosyasına kayıt atar
2. **Session başlangıcı**: `~/.wiki-skip-session` varsa temizlenir (önceki session'dan kalan)
3. **Kullanıcı mesajı**: Eğer marker doluysa ve kullanıcı `wiki ...` komutu söylemediyse, AI proaktif olarak sorar:
   - "Wiki güncellemesi bekliyor: X proje, Y commit. Ne yapayım?"
4. **Seçenekler:**
   - **Evet, hepsini topla** → `wiki topla` çalıştırır, marker temizlenir
   - **Sadece bir projeyi güncelle** → Belirtilen projeyi işler
   - **Durumu göster** → `wiki durum`, sonra tekrar sorar
   - **Şimdi değil** → Sonraki session'da tekrar sorulacak
   - **Bu session'da tekrar sorma** → Bu session'da atla, sonrakinde sorulacak

### Git Hook'ların Yönetimi

```bash
# Hook'ların kurulu olduğu repo'lar
/home/akn/local/.git/hooks/post-commit          # anka, mathlock, telegram-kimi, sayi-yolculugu, infrastructure
/home/akn/local/ops-bot/.git/hooks/post-commit  # ops-bot
/home/akn/local/projects/webimar/.git/hooks/post-commit  # webimar

# Hook script (tek kaynak)
/home/akn/local/scripts/wiki-post-commit.sh
```

> **Not:** Commit IDE üzerinden veya `--no-verify` ile atılırsa hook çalışmaz. Bu durumda manuel `wiki güncelle` kullanın.

---

## Sonraki Adımlar

1. `kimi` çalıştır
2. `wiki durum` ile mevcut durumu gör
3. Bir projede değişiklik yap ve `git commit` at
4. Yeni `kimi` seansında proaktif prompt bekleyin
5. Obsidian'da `wiki/` dizinini vault olarak aç ve Graph View'i keşfet

> **İpucu:** Her hafta sonu `wiki topla && wiki kontrol` komutlarını çalıştırmak wiki'yi taze ve tutarlı tutar.
