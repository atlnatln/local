# local-wiki İş Akışları (Workflows)

Bu doküman, `local-wiki` skill'in çalışma zamanında izlediği 4 ana iş akışını (workflow) tanımlar. Her iş akışı, kullanıcının `wiki ...` ifadesini girmesiyle tetiklenen adım adım prosedürlerden oluşur.

---

## Workflow 1: Ingest (Veri Alımı)

Bu iş akışı, izlenen projelerdeki kaynak dosyalardaki değişiklikleri tespit eder, analiz eder ve wiki'ye entegre eder.

### Adım 1 — Kapsamı Belirle
Kullanıcı bir proje belirttiyse (örn. `wiki ingest ops-bot`), kapsam = sadece o proje.
Proje belirtilmediyse, izlenen tüm projeler sırasıyla işlenir:
`ops-bot` → `webimar` → `anka` → `mathlock-play` → `telegram-kimi` → `sayi-yolculugu` → `infrastructure`

### Adım 2 — Checkpoint Oku ve Değişiklikleri Tespit Et
Kaydedilmiş SHA değerini `.checkpoints/<isim>.sha` dosyasından oku. Ardından ilgili git diff komutunu çalıştır:

```bash
# Ayrı git reposuna sahip projeler için (ops-bot, webimar):
cd <proje-dizini> && git diff --name-status $(cat <checkpoint-dosyasi>)..HEAD

# Monorepo içinde izlenen projeler için (anka, mathlock-play, telegram-kimi, sayi-yolculugu, infrastructure):
cd /home/akn/local && git diff --name-status $(cat wiki/.checkpoints/local.sha)..HEAD -- <proje-dizini>
```

Checkpoint `HEAD` içeriyorsa (ilk çalıştırma), boş ağaç (empty tree) ile karşılaştır:
```bash
git diff --name-status 4b825dc642cb6eb9a060e54bf8d69288fbee4904..HEAD -- <proje-dizini>
```

### Adım 3 — Her Değişiklik Dosyasını İşle
git diff çıktısını parse et (A/M/D/R durumları):

| Durum | İşlem |
|-------|-------|
| `A` (Added/Eklendi) | Kaynağı oku → yeni wiki sayfası oluştur → çapraz referans ver |
| `M` (Modified/Değiştirildi) | Kaynağı oku → mevcut wiki sayfasını güncelle → çapraz referansları yenile |
| `D` (Deleted/Silindi) | Bu kaynaktan türetilmiş wiki sayfasını bul → `[STALE]` olarak işaretle → `_archive/` dizinine taşı → index.md güncelle (ana bölümlerden kaldır, ## Archived Pages bölümüne ekle) → log güncelle |
| `R` (Renamed/Yeniden adlandırıldı) | Eski sayfayı arşivle (`[STALE]` işaretle, `_archive/` taşı) → yeniden adlandırılmış kaynaktan yeni sayfa oluştur → eski ↔ yeni arasında çapraz bağlantı kur → index'i güncelle |

### Adım 4 — Kaynağı Oku ve Analiz Et
Her A/M/R dosyası için:
- Dosya içeriğini oku
- Türünü belirle: config, kaynak kod, deploy script, dokümantasyon
- Çıkar: amaç, ana fonksiyonlar/bölümler, bağımlılıklar, ilgili dosyalar
- Hangi wiki sayfasının oluşturulması/güncellenmesi gerektiğini belirle

### Adım 5 — Wiki Sayfalarını Yaz
Yazmadan önce, uygun şablon için `references/PAGE_TEMPLATES.md` dosyasını oku.

Her sayfa için:
- Frontmatter'ı doldur (`title`, `created`, `updated`, `type`, `tags`, `related:`)
- Gövdeyi gerçekçi, öz bir üslupla yaz
- İlgili projelere, konseptlere, kararlara `[[wikilink]]` ekle
- Dil etiketleri ve dosya yolu yorumları ile kod snippet'leri ekle
- `sources:` alanında `raw/articles/<dosyaadi>`'na işaret et

Sayfa adlandırma:
- Projeler → `wiki/projects/<kebab-case>.md`
- Konseptler → `wiki/concepts/<kebab-case>.md`
- Kararlar → `wiki/decisions/<kebab-case>.md`

### Adım 6 — Raw Arşiv Kopyası
Wiki sayfası yazıldıktan sonra, orijinal kaynağı `wiki/raw/articles/<dosyaadi>` konumuna kopyala.
Raw kopyalar değiştirilemez (immutable) — asla düzenlenmemelidir.

### Adım 7 — Çapraz Referans Geçişi
Tüm sayfalar yazıldıktan sonra:
- Yeni/güncellenmiş sayfalarda diğer projelerden, teknolojilerden, konseptlerden bahsedip bahsedilmediğini tara
- Eksik `[[...]]` wikilink'lerini ekle
- `wiki/index.md`'yi yeni/güncellenmiş sayfaları yansıtacak şekilde güncelle
- İlgili konsept sayfalarını yeni proje sayfalarına geri bağlantı verecek şekilde güncelle

### Adım 8 — Son Commit'leri Yenile
Proje sayfası için `## Recent Commits` bölümünü güncelle:

```bash
# Ayrı git reposu olan projeler için:
cd <proje-dizini> && git log --oneline -5

# Monorepo içinde izlenen projeler için:
cd /home/akn/local && git log --oneline -5 -- <proje-yolu>
```

Çıktıyı parse et ve markdown listesi olarak yaz:
`- \`a1b2c3d\` Açıklama (YYYY-MM-DD)`

### Adım 9 — Index ve Log'u Güncelle
`wiki/index.md`'yi güncelle: yeni sayfaları uygun bölümlere ekle, "Last Updated" tarihlerini güncelle, "Recently Updated" listesini (son 5) yenile.

`wiki/log.md`'ye ekle:
```markdown
## [YYYY-MM-DD HH:MM] ingest | <proje> | <commit-sha> | <dokunulan-sayfalar>
- Dosyalar: A:3 M:5 D:1
- Oluşturulan sayfalar: [[sayfa1]], [[sayfa2]]
- Güncellenen sayfalar: [[sayfa3]]
- Arşivlenen sayfalar: [[eski-sayfa]]
- Diff özeti: [[ops-bot]]'a systemd servis bölümü eklendi. [[infrastructure]] içinde [[nginx]] ile çapraz bağlantı kuruldu.
- Wiki diff: see `git log --oneline -1 -- wiki/` for the commit hash
```

### Adım 10 — Checkpoint'i Güncelle
Başarılı ingest sonrası checkpoint SHA'sını güncelle:
```bash
# Ayrı git reposu olan projeler için:
cd <proje-dizini> && git rev-parse HEAD > <checkpoint-dosyasi>

# Monorepo içinde izlenen projeler için:
cd /home/akn/local && git rev-parse HEAD > wiki/.checkpoints/local.sha
```

İngest yarıda kesilirse, checkpoint'i GÜNCELLEME.

---

## Workflow 2: Query (Sorgu)

Bu iş akışı, kullanıcının wiki'ye doğal dilde sorduğu soruları yanıtlar.

### Adım 1 — Soruyu Parse Et
Kullanıcının sorusundaki ana varlıkları (proje adları, teknolojiler, konseptler) belirle.

### Adım 2 — ADR Öncelikli Arama (ADR-Aware Query)
Soruda aşağıdaki **mimari karar anahtar kelimeleri** varsa, önce `wiki/index.md`'deki **Active Decisions** tablosuna bak:

| Türkçe Anahtar Kelimeler | İngilizce Anahtar Kelimeler |
|--------------------------|----------------------------|
| neden, niçin, seçtik, tercih, karar, alternatif, trade-off, değiştirelim, kaldıralım, yerine | why, chose, decision, alternative, trade-off, rationale, instead of, rather than, change, replace |

**İşlem:**
1. `wiki/index.md`'deki `## Active Decisions` tablosunu oku.
2. Sorudaki proje/konsept/teknoloji ile eşleşen ADR'leri belirle.
3. Eşleşen ADR'leri **öncelikli olarak** oku (Query'nin diğer sayfalarından önce).
4. ADR'nin `status` alanını kontrol et:
   - `Active` → Karar hâlâ geçerli, kullanıcıya referans ver.
   - `Superseded` → Yeni karar var, kullanıcıya bilgi ver ve yeni ADR'yi göster.
   - `Deprecated` → Karar artık uygulanmıyor, kullanıcıya bildir.

> **Örnek:** Kullanıcı "neden webimar ayrı repo?" diye sorarsa → `adr-001-monorepo-hybrid-structure`'ı oku → "Monorepo + ayrı repo karışık yapısı kararı"nı açıkla.

### Adım 3 — Index'i Oku
`wiki/index.md`'yi oku ve ilgili sayfa yollarını bul (ADR'ler hariç, zaten Adım 2'de okunduysa).

### Adım 4 — İlgili Sayfaları Oku
Belirlenen sayfaları oku. `[[wikilink]]` bağlantılarını takip ederek ilgili sayfalara ulaş (en fazla 3 hop).

### Adım 5 — Yanıtı Sentezle
Bilgileri birleştir:
- Belirli wiki sayfalarını kaynak göster: "[[ops-bot]]'a göre..."
- İlgili yerlerde kod snippet'leri veya dosya yollarını dahil et
- Bilgi eksik veya çelişkili ise açıkça belirt
- Yanıt wiki'ye değerli bir katkı olacaksa, yeni bir konsept sayfası olarak kaydetmeyi teklif et

### Adım 6 — İsteğe Bağlı: Geri Yazma (File Back)
Sentezlenen yanıt bir boşluk ortaya çıkarırsa veya faydalı bir özet oluşturursa, yeni bir konsept sayfası oluşturmayı teklif et. Kullanıcı onay verirse, Concept şablonunu takip ederek yaz, index ve log'u güncelle.

---

## Workflow 3: Lint (Kontrol)

Bu iş akışı, wiki'nin yapısal bütünlüğünü ve tutarlılığını denetler.

### Adım 1 — Lint'i Çalıştır
```bash
cd ~/.kimi/skills/local-wiki/ && python3 scripts/wiki_lint.py /home/akn/local/wiki
```

### Adım 2 — Bulguları Raporla
Sonuçları her bir kontrol için PASS/WARN/FAIL olarak sun.

### Adım 3 — Düzeltme Önerileri
Her sorun için somut düzeltme önerisi sun.

### Adım 4 — Log Girişini Onayla
Lint aracının `wiki/log.md`'ye otomatik olarak eklediği girişin yazıldığını doğrula.

---

## Workflow 4: Status (Durum)

Bu iş akışı, wiki'nin mevcut durumunu özetler.

### Adım 1 — Checkpoint'leri Oku
Tüm `.checkpoints/*.sha` dosyalarını oku.

### Adım 2 — Sayfaları Say
`wiki/` altındaki .md dosyalarını say (`log`, `index`, `SCHEMA` hariç).

### Adım 3 — Son Log Girişlerini Oku
`wiki/log.md`'den son 5 girişi oku.

### Adım 4 — Sunum
Tablo formatında göster:

```
| Proje      | Son Ingest | Checkpoint | Durum      |
|------------|------------|------------|------------|
| ops-bot    | 2025-05-01 | a1b2c3d    | ✅ current |
```

---

## Workflow 5: ADR Ekleme (Decision Add)

Bu iş akışı, kullanıcının yeni bir mimari karar kaydı (ADR) oluşturmasını sağlar.

### Adım 1 — Son ADR Numarasını Bul

`wiki/decisions/` dizinini listele ve `wiki/index.md`'deki **Active Decisions** bölümünü oku:

```bash
ls -1 /home/akn/local/wiki/decisions/adr-*.md 2>/dev/null || echo "NONE"
```

En yüksek `adr-NNN` numarasını bul. Hiç ADR yoksa `NNN = 001` olarak başla.

### Adım 2 — Dosya Adı Oluştur

Kullanıcıdan başlığı al, kebab-case'e çevir:

```
wiki/decisions/adr-NNN-kisa-baslik.md
```

### Adım 3 — Template'i Doldur

`references/PAGE_TEMPLATES.md` Section 3'ü (Decision Page Template) oku ve EXACT olarak uygula. Kullanıcıdan aşağıdaki bilgileri topla:

| Alan | Zorunlu | Açıklama |
|------|---------|----------|
| Başlık | Evet | Kararın insan tarafından okunabilir başlığı |
| Etkilenen proje/konsept | Evet | Hangi proje veya konsepti etkiliyor? |
| Context | Evet | Problemin tanımı, kısıtlar, zaman baskısı |
| Decision | Evet | Ne kararlaştırıldı? 1-2 cümle + detaylar |
| Consequences (✅/⚠️/🔄) | Evet | Olumlu, riskler, tarafsız notlar |
| Alternatives Considered | Evet | En az bir alternatif ve neden reddedildiği |
| Status | Evet | `Active` (yeni ADR için sabit) |

Frontmatter kuralları:
- `type: decision`
- `tags:` en az `[decision, adr]` içermeli
- `status: Active`
- `name:` `adr-NNN-kisa-baslik` formatında
- `decision_date:` kararın alındığı tarih (YYYY-MM-DD)

### Adım 4 — Çapraz Referans Kur

Etkilenen proje sayfasını bul (`wiki/projects/<proje>.md`):
- `## Decisions` bölümüne `[[adr-NNN-kisa-baslik]]` ekle (bölüm yoksa oluştur).

Etkilenen konsept sayfasını bul (`wiki/concepts/<konsept>.md`):
- `## Related Decisions` bölümüne geri link ekle.

Yeni ADR sayfasının `related:` frontmatter'ına etkilenen proje/konsepti ekle.

### Adım 5 — `wiki/index.md` Güncelle

`## Active Decisions` tablosuna yeni satır ekle:

```markdown
| [[adr-NNN-kisa-baslik]] | Active | YYYY-MM-DD | [1 cümlelik açıklama] |
```

`## Recently Updated` listesini güncelle.

### Adım 6 — `wiki/log.md`'ye Kaydet

```markdown
## [YYYY-MM-DD HH:MM] decision | adr-NNN | <etkilenen-proje/konsept>
- Type: new-adr
- Page: [[adr-NNN-kisa-baslik]]
- Status: Active
- Scope: <proje veya konsept>
- Summary: [1 cümlelik karar özeti]
```

### Adım 7 — Kullanıcıya Özet Ver

```
✅ ADR oluşturuldu: wiki/decisions/adr-NNN-kisa-baslik.md
📎 Çapraz link: [[<proje>]] sayfasına eklendi
📋 Index güncellendi: Active Decisions tablosuna eklendi
📝 Log kaydedildi.
```

---

### Alt Prosedür: Eski ADR'yi Güncelleme (Superseded)

Bir karar yeni bir ADR ile değiştirildiğinde:

#### Eski ADR'yi Güncelle

```yaml
---
status: Superseded
superseded_by: [[adr-YYY-yeni-karar]]
updated: "YYYY-MM-DD"
---
```

Gövdeye ekle (Status bölümüne):
```markdown
> **Yerini Aldı:** Bu karar şu karar tarafından geçersiz kılındı:
> [[adr-YYY-yeni-karar]] — Yeni kararın kısa açıklaması
```

#### Yeni ADR'yi Güncelle

```yaml
---
status: Active
supersedes: [[adr-XXX-eski-karar]]
---
```

#### Index'i Güncelle

- Eski ADR'yi `## Active Decisions` tablosundan kaldır.
- Eski ADR'yi `## Archived Decisions` tablosuna taşı (`Superseded` durumuyla).
- Yeni ADR'yi `## Active Decisions` tablosuna ekle.

#### Log Kaydet

```markdown
## [YYYY-MM-DD HH:MM] decision | adr-YYY | superseded
- Type: superseded
- New: [[adr-YYY-yeni-karar]]
- Old: [[adr-XXX-eski-karar]]
- Reason: [1 cümlelik gerekçe]
```
