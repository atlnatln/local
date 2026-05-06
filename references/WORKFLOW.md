# local-wiki İş Akışları (Workflows)

Bu doküman, `local-wiki` skill'in çalışma zamanında izlediği 5 ana iş akışını (workflow) tanımlar. Her iş akışı, kullanıcının `wiki ...` ifadesini girmesiyle tetiklenen adım adım prosedürlerden oluşur.

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
| `R` (Renamed/Yeniden adlandırıldı) | Eski sayfayı arşivle (`[STALE]` işaretle, `_archive/` taşı) → yeniden adlandırılmış kaynaktan yeni sayfa oluştur → eski ↔ yeni arasında çapraz bağlanti kur → index'i güncelle |

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
- Pages created: [[sayfa1]], [[sayfa2]]
- Pages updated: [[sayfa3]]
- Pages archived: [[eski-sayfa]]
- Diff özeti: [[ops-bot]]'a systemd servis bölümü eklendi. [[infrastructure]] içinde [[nginx]] ile çapraz bağlanti kuruldu.
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

### Adım 2 — Index'i Oku
`wiki/index.md`'yi oku ve ilgili sayfa yollarını bul.

### Adım 3 — İlgili Sayfaları Oku
Belirlenen sayfaları oku. `[[wikilink]]` bağlantılarını takip ederek ilgili sayfalara ulaş (en fazla 3 hop).

### Adım 4 — Yanıtı Sentezle
Bilgileri birleştir:
- Belirli wiki sayfalarını kaynak göster: "[[ops-bot]]'a göre..."
- İlgili yerlerde kod snippet'leri veya dosya yollarını dahil et
- Bilgi eksik veya çelişkili ise açıkça belirt
- Yanıt wiki'ye değerli bir katkı olacaksa, yeni bir konsept sayfası olarak kaydetmeyi teklif et

### Adım 5 — İsteğe Bağlı: Geri Yazma (File Back)
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

Bu iş akışı, kullanıcının bir mimari kararı kaydetmesini sağlar. Yeni bir Architecture Decision Record (ADR) oluşturur, ilgili proje ve konsept sayfalarına cross-link kurar, index ve log'u günceller.

### Trigger'lar
Kullanıcı şunlardan birini söylediğinde bu workflow'u başlat:
- `wiki karar ekle`, `wiki decision add`, `adr ekle`
- `"X kararını wiki'ye kaydet"`, `"neden Y yaptığımızı not al"`
- Mimari tartışma sonrası `"bunu ADR olarak kaydet"`

### ADR vs Concept: Kesin Ayrım (Kuşku Yok)

**MUTLAKA ADR yaz:**
- Yeni teknoloji/framework/library seçimi (Django, Next.js, Docker, nginx, Certbot, vs.)
- Mimari pattern değişikliği (monolith→microservices, REST→GraphQL, sync→async)
- Altyapı değişikliği (VPS, cloud, CDN, SSL provider, domain, sunucu taşıma)
- Güvenlik kararı (auth mekanizması, JWT vs Session, şifreleme, firewall)
- Performans trade-off'u (caching stratejisi, DB seçimi, pagination yöntemi)
- "6 ay sonra neden böyle yaptık?" sorusuna cevap vermesi gereken durum

**ADR YAZMA — Concept sayfası aç:**
- Bug fix, typo düzeltme, refactor (dışarıdan görünmezse)
- UI/UX değişikliği, renk paleti, font seçimi
- Günlük deploy prosedürü, rutin bakım adımları
- Bilgi notu, nasıl yapılır rehberi

### Adım 1 — Sıradaki ADR Numarasını Bul

```bash
ls wiki/decisions/adr-*.md 2>/dev/null | sort -V | tail -1
```

Eğer hiç ADR yoksa, başlangıç numarası `adr-001`.
Mevcut en yüksek ADR numarasını bul, +1 artır. Format: `adr-NNN` (3 haneli, zero-padded).

### Adım 2 — Dosya Adını Oluştur

```
wiki/decisions/adr-NNN-kisa-baslik.md
```

- `kisa-baslik`: Kebab-case, Türkçe karakterler olmadan, 3-5 kelime.
- Örnek: `adr-004-vps-vs-cloud`, `adr-005-django-nextjs-pattern`

### Adım 3 — EXACT Template'i Doldur

`references/PAGE_TEMPLATES.md` section "3. Decision Page Template"'i oku ve aşağıdaki frontmatter + yapıyı kullan.

Kullanıcıdan aşağıdaki bilgileri topla (AskUserQuestion veya inline prompt):
- **Başlık:** Kararın kısa ve net başlığı
- **Etkilenen proje/konsept:** Bu karar hangi proje/konsepti etkiliyor?
- **Context:** Neden bu kararı almamız gerekti? Hangi problemi çözüyor? Hangi kısıtlar vardı?
- **Decision:** Ne karar aldık? Tek cümlede, kesin ve net.
- **Consequences:** Pozitif, negatif/risk, teknik borç
- **Alternatives Considered:** En az bir alternatif ve neden reddedildiği

Oluşturulan dosya:
```markdown
---
title: "Kısa ve net karar başlığı"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: decision
tags: [decision, adr]
related:
  - [[etkilenen-proje]]
  - [[etkilenen-konsept]]
status: Active
supersedes:
superseded_by:
---

# [[adr-NNN-kisa-baslik]]

## Context
Neden bu kararı almamız gerekti? Hangi problemi çözüyor? Hangi kısıtlar (bütçe, zaman, mevzuat, ekip bilgisi) vardı?

## Decision
Ne karar aldık? Tek cümlede, kesin ve net.

## Consequences
- ✅ Pozitif: ...
- ⚠️ Negatif / Risk: ...
- 🔄 Teknik borç: ...

## Alternatives Considered
- Alternatif A: Neden reddedildi?
- Alternatif B: Neden reddedildi?

## Status
Active

## References
- [[etkilenen-proje]]
- [[etkilenen-konsept]]
```

### Adım 4 — Cross-Reference Kur (Zorunlu)

- Etkilenen proje sayfasının `## Decisions` bölümüne `[[adr-NNN-kisa-baslik]]` ekle. Eğer `## Decisions` bölümü yoksa oluştur.
- Etkilenen konsept sayfasının `## Related Decisions` bölümüne geri link ekle. Eğer bölüm yoksa oluştur.
- Yeni ADR'nin `related:` frontmatter'ına karşılık gelen sayfaları yaz.

### Adım 5 — index.md Güncelle

`wiki/index.md`'deki `## Active Decisions` bölümüne ekle:
```markdown
| [[adr-NNN-kisa-baslik]] | Active | YYYY-MM-DD | Kısa açıklama |
```

### Adım 6 — log.md Kaydet

```markdown
## [YYYY-MM-DD HH:MM] decision | adr-NNN | <proje-veya-konsept>
- Status: Active
- Pages created: [[adr-NNN-kisa-baslik]]
- Pages updated: [[proje]], [[konsept]]
- Trigger: Kullanıcı "X kararını kaydet" dedi
```

### Adım 7 — Kullanıcıya Özet Ver

"ADR-NNN kaydedildi: `adr-NNN-kisa-baslik.md`. [[proje]] ve [[konsept]] sayfalarına cross-link kuruldu. Lint: 10/10."

---

### Eski ADR'yi Güncelleme (Superseded)

Eğer kullanıcı "eski ADR'yi güncelle" veya "bu karar değişti" derse:

1. **Eski ADR'yi aç:**
   - `status: Active` → `status: Superseded`
   - `superseded_by: [[adr-YYY-yeni-baslik]]`
   - `updated: YYYY-MM-DD` (bugün)

2. **Yeni ADR aç:**
   - Adım 1-3'ü takip et
   - `supersedes: [[adr-XXX-eski-baslik]]`
   - `status: Active`

3. **Index'i güncelle:**
   - Eski ADR'yi `## Active Decisions` tablosundan çıkar
   - Eski ADR'yi `## Archived Decisions` tablosuna ekle (Superseded, tarih)
   - Yeni ADR'yi `## Active Decisions` tablosuna ekle

4. **Proje/konsept sayfalarını güncelle:**
   - Eski proje sayfasındaki link'i güncelle (eski yerine yeni ADR'yi göster, veya ikisini birden listele)

5. **Log kaydet:**
   ```markdown
   ## [YYYY-MM-DD HH:MM] decision | adr-YYY | superseded
   - Supersedes: [[adr-XXX]]
   - Pages created: [[adr-YYY]]
   - Pages updated: [[adr-XXX]], [[proje]]
   ```

---

### Örnek Senaryolar

**Senaryo A (Interaktif):**
- Kullanıcı: `wiki karar ekle`
- Ajan: Son ADR numarasını bulur, kullanıcıya AskUserQuestion ile başlık, etkilenen proje, context sorar
- Bilgileri toplayıp EXACT template ile dosyayı oluşturur
- Cross-link'leri kurar, index ve log'u günceller

**Senaryo B (Kısa Prompt):**
- Kullanıcı: `wiki karar ekle "neden VPS'te kaldığımızı not al"`
- Ajan: adr-NNN numarasını belirler, kısa başlık üretir
- Kullanıcıdan sadece eksik detayları ister (context, alternatifler)
- Template'i doldurur, cross-link kurar
