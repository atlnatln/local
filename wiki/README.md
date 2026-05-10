---
title: "Wiki Kullanım Kılavuzu"
created: 2026-05-01
updated: 2026-05-01
type: index
tags: [meta, guide, local-wiki]
related: []
---

# local-wiki Kullanım Kılavuzu

`/home/akn/local/wiki` — Kimi CLI tarafından yönetilen, sürekli güncellenen bilgi tabanı.

---

## Hızlı Başlangıç

Kimi CLI `/home/akn/local` dizininde açıldığında wiki skill'i otomatik keşfedilir:

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

Kod değiştikçe wiki'yi güncel tutan komut.

### Ne Zaman Çalıştırılır?

- **Değişiklik sonrası**: yeni modül, refactor, deploy script
- **Yeni proje**: `wiki güncelle <proje>`
- **Haftalık bakım**: `wiki topla`

### Nasıl Çalışır?

1. `git diff --name-status` ile değişen dosyaları tespit eder
2. Wiki sayfalarını günceller, cross-link'leri yeniler
3. `log.md`'ye kayıt atar, checkpoint SHA'sını günceller

### Checkpoint Nedir?

`.checkpoints/` dizinindeki `.sha` dosyaları **local consumer cursor**'dur. Her makine kendi cursor'ünü yönetir, gitignored'dır.

```bash
wiki/.checkpoints/  # gitignored — local cursor
├── local.sha       # /home/akn/local monorepo
├── ops-bot.sha     # ops-bot/ (ayrı git repo)
└── webimar.sha     # projects/webimar/ (ayrı git repo)
```

Cross-machine sync `wiki/.pending` dosyası üzerinden sağlanır.

---

## Query (Sorgu)

Wiki'ye soru sormak için. Ajan önce `index.md`'yi okur, ilgili sayfaları bulur, sentezler ve cevap üretir.

### Örnek Sorular

- `wiki sor "ops-bot hangi servisleri yönetiyor?"`
- `wiki sor "anka'nın 3 aşamalı doğrulama hattı nedir?"`

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

- **Haftalık bakım**, büyük ingest sonrası, veya tuhaf bir durum fark edildiğinde

---

## Obsidian ile Açma

Wiki'yi Obsidian'da vault olarak aç: `/home/akn/local/wiki` → Graph View ile bilgi ağını görselleştir.

---

## Wiki Sayfa Yapısı

Her sayfa YAML frontmatter ile başlar. Detaylı şema: [[SCHEMA]].

Sayfalar arası bağlantı için çift köşeli parantez: `\[\[sayfa-adi\]\]`. Dosya adları `kebab-case.md`; link hedefleri büyük-küçük harf duyarsız çözülür.

---

## Wiki Organizasyon Kuralları

Wiki tutarlılığı için bağlayıcı kurallar.

### 1. Genelden Özele Sıralama (index.md)

`index.md` sırası: **System → Infrastructure & Platform → Concepts → Decisions → Projects**

Kural: Bir sayfa ne kadar çok projeye hizmet ediyorsa, o kadar yukarıda listelenir.

### 2. Sayfa Tipleri

| Tip | Amaç | Max | Bakım |
|-----|------|-----|-------|
| `project` | Proje özet | 200 satır | Agent (ingest) |
| `concept` | Çapraz süreç | 200 satır | Agent / İnsan |
| `decision` | Mimari karar | 150 satır | İnsan |
| `index` | Katalog | 250 satır | Agent + İnsan |
| `log` | İşlem kaydı | 500 giriş | Agent |

### 3. Yeni Sayfa Checklist'i

- [ ] Frontmatter tam, tag'ler `SCHEMA.md`'de var
- [ ] `index.md`'de genelden özele sıraya kondu
- [ ] Cross-link'ler mevcut sayfalara eklendi
- [ ] `log.md`'ye kayıt atıldı, lint 10/10 geçildi

### 4. infrastructure Ayrımı

`[[infrastructure]]` altyapı katmanı olduğu için `index.md`'de projelerden ayrı, "Infrastructure & Platform" bölümünde gösterilir.

---

## Proaktif Güncelleme (Auto-Prompt)

Git commit sonrası kimi-cli bir sonraki açılışında "wiki güncelleyelim mi?" diye sorar.

### Akış

1. `post-commit` hook → `wiki/.pending` marker dosyasına kayıt atar
2. Yeni session'da marker temizlenir (`~/.wiki-skip-session` silinir)
3. Eğer marker doluysa, AI proaktif sorar: "Wiki güncellemesi bekliyor. Ne yapayım?"

### Seçenekler

- **Evet** → `wiki topla`, marker temizlenir
- **Tek proje** → Belirtilen projeyi işler
- **Durum** → `wiki durum`, sonra tekrar sorar
- **Şimdi değil** → Sonraki session'da tekrar sorulacak
- **Bu session sorma** → `~/.wiki-skip-session` oluşturulur

### Git Hook'lar

| Repo | Hook |
|------|------|
| `local` (monorepo) | `.git/hooks/post-commit` |
| `ops-bot` | `ops-bot/.git/hooks/post-commit` |
| `webimar` | `projects/webimar/.git/hooks/post-commit` |

Kaynak: `/home/akn/local/scripts/wiki-post-commit.sh`

> **Not:** `--no-verify` ile atılan commit'lerde hook çalışmaz. Manuel `wiki güncelle` kullanın.

---

## Bakım ve Büyüme Kuralları

Wiki sürdürülebilir büyüme kuralları: [[AGENTS]]

## Sonraki Adımlar

`wiki durum` ile başla, değişiklik yap, commit at, proaktif prompt bekle. Haftalık: `wiki topla && wiki kontrol`.
