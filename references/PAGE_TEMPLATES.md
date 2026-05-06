# Wiki Sayfa Sablonlari (Page Templates)

> Bu dosya, `/home/akn/local/wiki/` altinda yeni sayfa olustururken kullanilan
> referans sablonlardir. Her `type` icin frontmatter alanlari, bolum yapisi ve
> doldurma kurallari asagida tanimlanmistir.

---

## Alan Aciklamalari (Legend)

| Isaret      | Anlami                                                  |
|-------------|----------------------------------------------------------|
| `[REQUIRED]`| Zorunlu alan; sayfa bu alan olmadan kaydedilmemeli       |
| `[OPTIONAL]`| Opsiyonel alan; gerekmedikce bos birakilabilir           |
| `[AUTO]`    | Agent tarafindan otomatik doldurulur; elle degistirilmez |
| `[USER]`    | Kullanici yorumu gerektirir; otomatik doldurulamaz       |
| `[WIKILINK]`| `[[Sayfa Adi]]` formatinda wiki baglantisi icermelidir   |

---

## 1. Project Page Template (`type: project`)

Projeler icin: ops-bot, webimar, anka, mathlock-play, telegram-kimi,
altyapi (infrastructure) vb.

### Kopyala-Yapistir Sablonu

```markdown
---
type: project
name: [REQUIRED] Projenin kisa adi (ornegin: ops-bot)
title: [OPTIONAL] Uzun baslik; belirtilmezse name kullanilir
description: [REQUIRED] 1 cümlelik proje özeti [USER]
created: [AUTO] YYYY-MM-DD formatinda olusturulma tarihi
updated: [AUTO] YYYY-MM-DD formatinda son güncellenme tarihi
tags: [OPTIONAL] [project, backend, frontend, bot, cli, lib]
status: [REQUIRED] active | paused | archived | deprecated
source_dir: [REQUIRED] Kaynak kodun bulundugu dizin yolu (ornegin: /home/akn/code/ops-bot)
repo_url: [OPTIONAL] Git uzak repo URLsi (ornegin: git@github.com:kullanici/proje.git)
related:
  - REQUIRED [WIKILINK] Iliskili kavram ve projeler
  - mimari-karar
  - adr-XXX-ilgili-karar
---

# {{name}}

{{description}}

## Amac [USER]

1 cümle: Bu proje neyi çözer? Kim kullanir?

## Stack

- **Backend:** [USER] (ornegin: Python 3.11, Django 5.0, FastAPI)
- **Frontend:** [USER] (ornegin: Next.js 14, TailwindCSS, React — yoksa "Yok")
- **Altyapi:** [USER] (ornegin: Docker Compose, PostgreSQL 15, Redis, Nginx)
- **Diger:** [OPTIONAL] [USER] (ornegin: Telegram Bot API, systemd, cron)

## Giris Noktalari (Entry Points)

| Dosya / Dizin | Aciklama |
|---------------|----------|
| `{{source_dir}}/main.py` | [USER] Uygulama giris noktasi |
| `{{source_dir}}/docker-compose.yml` | [USER] Konteyner yapilandirmasi |
| `{{source_dir}}/README.md` | [USER] Proje ici dokümantasyon |
| `{{source_dir}}/config/` | [USER] Yapilandirma dosyalari |

## Deploy [USER]

```bash
# [USER] Deployment adimlarini buraya yaz
# Ornek:
cd {{source_dir}}
git pull origin main
docker compose up -d --build
```

## Bagimliliklar [WIKILINK]

- [[proje-adi-1]] — [USER] Neden bagimli?
- [[proje-adi-2]] — [USER]
- [[concept/kavram-adi]] — [USER] Hangi kavrama bagli?

## Kararlar [WIKILINK]

Mimari kararlar (ADR) bu projeyi nasil etkiledi:

- [[decisions/adr-XXX-kisa-baslik]] — [AUTO/USER] Kararin kisa aciklamasi

## Son Commits [AUTO]

<!-- Bu bolum agent tarafindan otomatik güncellenir. Elle düzenleme yapmayin. -->

| Hash | Tarih | Mesaj |
|------|-------|-------|
| `a1b2c3d` | YYYY-MM-DD | [AUTO] Son commit mesaji |
| `e4f5g6h` | YYYY-MM-DD | [AUTO] Onceki commit mesaji |
| `i7j8k9l` | YYYY-MM-DD | [AUTO] ... |
| `m0n1o2p` | YYYY-MM-DD | [AUTO] ... |
| `q3r4s5t` | YYYY-MM-DD | [AUTO] ... |

> Son güncelleme: [AUTO] YYYY-MM-DD HH:MM

## Notlar [USER]

[USER] Serbest bölüm: teknik detaylar, hatirlatmalar, borç (tech debt),
iletişim kurallari, sifrelerin nerede tutuldugu (yalnizca referans — sifre
yazmayin), vb.

```

### Doldurma Kurallari

- `status` alani her güncellemede kontrol edilmeli; proje durumunu dogru
  yansitmali.
- `source_dir` mutlak yol olmali; `~` veya `$HOME` kullanilmamali.
- Giris noktalari tablosu proje yapisi degistikce güncellenmeli.
- Son Commits tablosu en az haftada bir otomatik yenilenmeli.
- Bagimliliklar ve Kararlar bölümleri bos kalabilir ama baslik korunmali.

---

## 2. Concept Page Template (`type: concept`)

Kesişen kavramlar icin: deployment, ssl-certbot, django-nextjs-pattern,
multi-web-project-system vb.

### Kopyala-Yapistir Sablonu

```markdown
---
type: concept
name: [REQUIRED] Kavramin kisa adi (ornegin: ssl-certbot)
title: [OPTIONAL] Uzun baslik; belirtilmezse name kullanilir
description: [REQUIRED] 2-3 cümlelik kavram aciklamasi [USER]
created: [AUTO] YYYY-MM-DD formatinda olusturulma tarihi
updated: [AUTO] YYYY-MM-DD formatinda son güncellenme tarihi
tags: [OPTIONAL] [concept, deployment, security, pattern, infrastructure, networking]
related:
  - REQUIRED [WIKILINK] Bu kavramla iliskili diger kavramlar ve kullanan projeler
  - ilgili-kavram-1
  - kullanan-proje-1
---

# {{name}}

{{description}}

## Tanim [USER]

2-3 cümle: Bu kavram tam olarak nedir? Bu sistemde ne anlama gelir?

[USER] Burada kavramin genel tanimini ve mevcut sistemdeki özel anlamini
aciklayin. Yeni bir kisi okudugunda kavrami anlayabilmeli.

## Baglam [WIKILINK]

Bu kavram su projelerde kullaniliyor:

- proje-adi-1  — [USER] Nerede / nasil kullaniliyor?
- [[projects/proje-adi-2]] — [USER]
- [[concept/diger-kavram]] — [USER] Hangi diger kavramla birlikte?

## Uygulama [USER]

Bu sistemde nasil uygulandi:

### 1. [USER] Adim basligi

```
# Dosya: [AUTO] /tam/dosya/yolu.txt
# [USER] Aciklama

kod veya yapilandirma içeriği buraya...
```

### 2. [USER] Diger adim basligi

```
# Dosya: [AUTO] /tam/dosya/yolu.conf

yapilandirma içeriği buraya...
```

> **Not:** [USER] Kod örnekleri gercek, calisan parçalar olmali.
> Yol bilgisi `[AUTO]` ile isaretlenen kisim agent tarafindan
> güncellenebilir.

## Ilişkili Kavramlar [WIKILINK]

- ilgili-kavram-1  — [USER] Kisa aciklama: neden iliskili?
- [[concept/ilgili-kavram-2]] — [USER]
- [[decisions/adr-XXX-karar]] — [USER] Bu kavramla ilgili bir karar varsa

## Related Decisions [WIKILINK]

Bu kavramla ilgili alinmis mimari kararlar:

- [[decisions/adr-XXX-kisa-baslik]] — [USER] Kararin kisa aciklamasi

## Kaynaklar

| Kaynak | Tür | Açiklama |
|--------|-----|----------|
| `raw/dosya-adi.conf` | [AUTO] Dosya | [USER] Bu kavramla ilgili ham yapilandirma |
| `raw/script-adi.sh` | [AUTO] Script | [USER] Kullanilan otomasyon scripti |
| https://ornek.com/kaynak | [USER] Harici URL | [USER] Referans dokümantasyon |

```

### Doldurma Kurallari

- Tanim bölümü teknik jargon kullanmali ama anlasilir olmali.
- Baglam bölümü en az bir proje baglantisi icermeli; bos kavram sayfasi
  anlamsizdir.
- Uygulama bölümündeki kod örnekleri calisan sistemden alinmali; uydurma
  kod yazilmamali.
- Kaynaklar tablosundaki `raw/` referanslari, `references/` dizinindeki
  dosyalara isaret etmeli.

---

## 3. Decision Page Template (`type: decision`)

Mimari karar kayitlari (ADR) icin. Her ADR, "neden böyle yaptik?" sorusuna
cevap veren, alternatifleri değerlendiren, sonuçlari belgeleyen yapilandirilmis
bir kayittir.

### Kopyala-Yapistir Sablonu

```markdown
---
title: [REQUIRED] "Kisa ve net karar basligi" [USER]
created: [AUTO] YYYY-MM-DD
updated: [AUTO] YYYY-MM-DD
type: decision
tags: [REQUIRED] [decision, adr]
related:
  - REQUIRED [WIKILINK] Etkilenen projeler ve ilgili konseptler
  - [[projects/etkilenen-proje]]
  - [[concept/ilgili-konsept]]
status: [REQUIRED] Active | Superseded | Deprecated
supersedes: [OPTIONAL] [[adr-XXX-eski-baslik]]
superseded_by: [OPTIONAL] [[adr-YYY-yeni-baslik]]
---

# [[adr-NNN-kisa-baslik]]

## Context
[USER] Neden bu kararı almamız gerekti? Hangi problemi çözüyor? Hangi kısıtlar
(bütçe, zaman, mevzuat, ekip bilgisi) vardı?

[USER] 2-4 paragraf. "X yapmak zordu çünkü..." veya "Y yaklaşımı bizi Z
problemini yaşamaya götürdü..." şeklinde yazın.

## Decision
[USER] Ne karar aldık? Tek cümlede, kesin ve net.

[USER] Kararın detayları: ne yapılacak, nasıl yapılacak, hangi araçlar
kullanılacak. Gerekirse kısa bir özet madde listesi:

- [USER] Eylem 1
- [USER] Eylem 2
- [USER] Eylem 3

## Consequences

### ✅ Pozitif [USER]

- [USER] Bu kararın getirdiği avantaj 1
- [USER] Bu kararın getirdiği avantaj 2

### ⚠️ Negatif / Riskler [USER]

- [USER] Bu kararın maliyeti / riski 1
- [USER] Bu kararın maliyeti / riski 2

### 🔄 Teknik Borç [USER]

- [USER] Bu kararla birlikte kabul edilen teknik borç (varsa)

## Alternatives Considered

[USER] En az bir alternatif belgelenmeli. "Başka seçenek düşünmedik" yazmak
yerine, neden öbür seçeneklerin göz ardı edildiği açıklanmalı.

### Alternatif A: [USER] Alternatif adı

- **Açıklama:** [USER] Bu alternatif neydi?
- **Neden reddedildi:** [USER] Neden bu yöne gidilmedi?

### Alternatif B: [USER] Alternatif adı

- **Açıklama:** [USER]
- **Neden reddedildi:** [USER]

## Status

**Mevcut Durum:** `{{status}}`

{% if status == "Superseded" %}
> **Yerini Aldı:** Bu karar şu karar tarafından geçersiz kılındı:
> [[decisions/adr-YYY-yeni-baslik]] — [USER] Yeni kararın kısa açıklaması
{% endif %}

{% if status == "Deprecated" %}
> **Geçersiz:** Bu karar artık uygulanmıyor. [USER] Neden geçersiz
> olduğunu ve neyin kullanıldığını belirtin.
{% endif %}

> Son durum güncellemesi: [AUTO] YYYY-MM-DD

## References

- [[projects/etkilenen-proje]] — [USER] Bu proje bu karardan nasıl etkilendi?
- [[concept/ilgili-konsept]] — [USER]
- `raw/articles/kaynak-dosya.md` — [OPTIONAL] İlgili ham kaynak

```

### Doldurma Kurallari

- Dosya adı `adr-NNN-kisa-baslik.md` formatında olmalı; sıralı numara
  kullanılmalı (3 haneli, zero-padded).
- `title` alanı kısa ve net olmalı; 60 karakteri geçmemeli.
- Her ADR mutlaka en az bir `Alternatives Considered` içermeli.
- Kararlar vakumda alınmaz; reddedilenler de belgelenmeli.
- `status` alanı gerçek durumu yansıtmalı. Eski bir kararın hala
  `Active` olarak kalması hata olur.
- `Superseded` durumunda `superseded_by` wikilink'i dolu olmalı; boş bırakılmamalı.
- `tags` alanı en azından `[decision, adr]` içermeli.
- Consequences bölümünde pozitif, negatif ve teknik borç ayrı alt başlıklarda
  belgelenmeli.

---

## 4. Index Page Template (`type: index`)

Katalog sayfalari icin: `index.md`, `projects/index.md`, `concepts/index.md`
vb.

### Kopyala-Yapistir Sablonu

```markdown
---
type: index
name: [REQUIRED] Dizin adi (ornegin: projects-index)
title: [OPTIONAL] Baslik; belirtilmezse dizin adi kullanilir
description: [REQUIRED] 1 cümlelik dizin açiklamasi [USER]
created: [AUTO] YYYY-MM-DD formatinda olusturulma tarihi
updated: [AUTO] YYYY-MM-DD formatinda son güncellenme tarihi
tags: [OPTIONAL] [index, catalog, projects, concepts, decisions]
scope: [REQUIRED] Bu dizinin kapsadigi dizin yolu (ornegin: projects/)
related:
  - REQUIRED [WIKILINK] Ust dizin veya iliskili indeksler
  - index
---

# {{title}}

{{description}}

## İçindekiler

<!-- Bu tablo otomatik oluşturulur ve güncellenir. Elle düzenleme yapmayin. -->

| Sayfa | Tür | Özet | Son Güncelleme |
|-------|-----|------|----------------|
| [[projects/proje-adi-1]] | project | [AUTO] 1 satirlik özet | [AUTO] YYYY-MM-DD |
| [[projects/proje-adi-2]] | project | [AUTO] 1 satirlik özet | [AUTO] YYYY-MM-DD |
| [[concept/kavram-adi-1]] | concept | [AUTO] 1 satirlik özet | [AUTO] YYYY-MM-DD |
| [[decisions/adr-001-baslik]] | decision | [AUTO] 1 satirlik özet | [AUTO] YYYY-MM-DD |
| ... | ... | ... | ... |

> Toplam: [AUTO] N sayfa — Son güncelleme: [AUTO] YYYY-MM-DD HH:MM

## Son Güncellenen Sayfalar [AUTO]

<!-- Bu bölüm otomatik oluşturulur ve güncellenir. Elle düzenleme yapmayin. -->

| Sayfa | Tür | Son Güncelleme |
|-------|-----|----------------|
| [[sayfa-adi-1]] | [AUTO] type | [AUTO] YYYY-MM-DD |
| [[sayfa-adi-2]] | [AUTO] type | [AUTO] YYYY-MM-DD |
| [[sayfa-adi-3]] | [AUTO] type | [AUTO] YYYY-MM-DD |
| [[sayfa-adi-4]] | [AUTO] type | [AUTO] YYYY-MM-DD |
| [[sayfa-adi-5]] | [AUTO] type | [AUTO] YYYY-MM-DD |

## Alt Dizinler [OPTIONAL] [WIKILINK]

- index  — [USER] Alt dizin aciklamasi
- [[alt-dizin-2/index]] — [USER]

```

### Doldurma Kurallari

- Icindekiler tablosu, `scope` ile belirtilen dizin altindaki tüm
  `.md` dosyalarini kapsamali. Alt dizinler icin ayrac kullanilabilir.
- Son Güncellenen Sayfalar bölümü, en son `updated` alani degisen
  5 sayfayi listelemeli; alfabetik sira degil, zaman siralamasi.
- Alt Dizinler bölümü sadece hiyerarsik yapi olan index sayfalarinda
  kullanilmali; düz dizinlerde kaldirilabilir.
- Tablolar otomatik güncellendiginde, el ile eklenen satirlar korunmali
  ve otomatik satirlar ayirt edilebilmeli (ornegin `<!-- AUTO -->`
  yorumu ile).

---

## Frontmatter Referansi: Tüm Alanlar

Asagidaki tablo tüm sayfa tiplerindeki frontmatter alanlarini bir arada
özetler:

| Alan         | project | concept | decision | index | Aciklama                           |
|-------------|:-------:|:-------:|:--------:|:-----:|------------------------------------|
| `type`      |    R    |    R    |    R     |   R   | Sayfa tipi                         |
| `name`      |    R    |    R    |    —     |   R   | Kisa, dosya adi uyumlu isim        |
| `title`     |    O    |    O    |    R     |   O   | Uzun baslik (yoksa name kullanilir) |
| `description`|   R    |    R    |    —     |   R   | 1 cümlelik özet                    |
| `created`   |    A    |    A    |    A     |   A   | Olusturulma tarihi (YYYY-MM-DD)    |
| `updated`   |    A    |    A    |    A     |   A   | Son güncelleme tarihi              |
| `tags`      |    O    |    O    |    R     |   O   | Etiket listesi                       |
| `status`    |    R    |    —    |    R     |   —   | Durum (tipa göre degisir)          |
| `source_dir`|    R    |    —    |    —     |   —   | Proje kaynak dizini                |
| `repo_url`  |    O    |    —    |    —     |   —   | Uzak repo URLsi                    |
| `scope`     |    —    |    —    |    —     |   R   | Dizin kapsami                      |
| `related`   |    R    |    R    |    R     |   R   | Iliskili sayfalar [WIKILINK]       |
| `supersedes`|    —    |    —    |    O     |   —   | Bu kararin yerini aldigi ADR       |
| `superseded_by`| —    |    —    |    O     |   —   | Bu karari gecersiz kilan ADR       |

**R** = [REQUIRED]  |  **O** = [OPTIONAL]  |  **A** = [AUTO]  |  **—** = Kullanilmaz

---

## Wikilink Kullanim Kurallari

```
[[hedef-sayfa]]                  # Ayni dizin icinde kisa referans
[[dizin/hedef-sayfa]]            # Alt dizine mutlak referans
[[../ust-dizin/hedef-sayfa]]     # Üst dizine göreli referans
[[hedef-sayfa|Görünen Metin]]    # Özel görünen metin ile
```

- Wikilink hedefleri mutlaka var olan veya planlanan sayfalara isaret
  etmeli. Kirik baglanti (`[[yok-sayfa]]`) bilerek birakilmamali.
- Kavram sayfalarinda `[[concept/kavram-adi]]` formati kullanilmali.
- Karar sayfalarinda `[[decisions/adr-NNN-baslik]]` formati kullanilmali.
- Proje sayfalarinda `[[projects/proje-adi]]` formati kullanilmali.

---

## Etiket Rehberi (Tag Guide)

Asagidaki etiketler, tüm sayfa tiplerinde ortak olarak kullanilabilir.
Etiketlerde büyük/küçük harf birligi saglanmali; hepsi küçük harf.

| Etiket Grubu   | Kullanilabilir Degerler                                    |
|----------------|------------------------------------------------------------|
| Sayfa tipi     | `project`, `concept`, `decision`, `index`                  |
| Teknik alan    | `backend`, `frontend`, `infrastructure`, `database`, `api` |
| Araç / Platform| `docker`, `nginx`, `systemd`, `telegram`, `nextjs`, `django`|
| Güvenlik       | `ssl`, `auth`, `security`                                  |
| Süreç          | `deployment`, `monitoring`, `testing`                      |
| Durum          | `active`, `archived`, `deprecated`, `draft`                |
| Özel           | `adr`, `bot`, `cli`, `lib`, `pattern`                      |

---

> Bu referans dosyasi `[AUTO] YYYY-MM-DD` tarihinde olusturuldu.
> Yeni sayfa tipleri eklendiginde güncellenmeli.
