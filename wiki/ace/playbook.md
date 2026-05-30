---
title: "ACE Playbook — Genel"
created: 2026-05-30
updated: 2026-05-30
type: concept
tags: [ace, playbook, meta]
related: [ace-system]
---

# ACE Playbook — Genel

> Cross-project dersler. Her oturumda okunur.
> Proje-spesifik dersler için bkz. ilgili proje playbook'u.

---

## Ders 001: LSP ile kod düzenleme — önce locate, sonra oku

**Confidence:** 0.95
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 2
**Source:** scripts/wiki-assistant.py
**Scope:** genel
**Type:** workflow

### Context
Kimi kod düzenleme isteği aldığında tüm dosyayı okumak yerine LSP kullanarak sembol konumunu bulmalı.

### Rule
Kod düzenleme isteğinde önce `scripts/wiki-assistant.py --locate --file <path> --symbol <name>` çalıştır. Sadece ilgili satır aralığını oku, `StrReplaceFile` ile değişikliği uygula.

### Rationale
Tam dosya okuma ~1000 satır = token israfı. LSP locate ~50 satır = %95 tasarruf.

### Examples

#### ✅ Do
```bash
python3 scripts/wiki-assistant.py --locate --file bot/main.py --symbol handle_message
# Sadece range'i oku, StrReplaceFile ile düzenle
```

#### ❌ Don't
```bash
# Tam dosyayı oku — neden: 800 satır context israfı
cat bot/main.py
```

### Related
- [[wiki-assistant]]
- [[kimi-code-cli]]
- [[ops-bot]]
- [[webimar]]
- [[mathlock-play]]
- [[sayi-yolculugu]]
- [[telegram-kimi]]
- [[robotopia-android]]
- [[infrastructure]]

---

## Ders 002: Git stash kullanımı — pop'tan önce status kontrolü

**Confidence:** 0.85
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 1
**Source:** AGENTS.md
**Scope:** genel
**Type:** workflow

### Context
Birçok kez `git stash pop` çalıştırıldıktan sonra beklenmedik conflict veya untracked dosya sorunları yaşandı.

### Rule
`git stash pop` veya `git stash apply` yapmadan önce mutlaka `git status --short` çalıştır. Working tree temiz değilse önce durumu çöz.

### Rationale
Stash pop conflict'e düşerse cleanup zorlaşır. Önceki durum bilgisi kaybolabilir.

### Examples

#### ✅ Do
```bash
git status --short
# Temizse:
git stash pop
```

#### ❌ Don't
```bash
# Doğrudan pop — neden: conflict riski, kayıp değişiklik
 git stash pop
```

### Related
- [[git-workflow]]

---

## Ders 003: Wiki ingest öncesi her zaman lint çalıştır

**Confidence:** 0.90
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 1
**Source:** wiki/AGENTS.md
**Scope:** genel
**Type:** workflow

### Context
Wiki güncellemeleri bazen lint hatası veriyordu, commit sonrası fark ediliyordu.

### Rule
Her wiki ingest işleminden önce `wiki_lint.py` çalıştır. Lint PASS olmadan commit yapma.

### Rationale
Lint hatası olan wiki sayfaları sonraki agent'lar için sorun yaratır. Pre-commit hook zaten engeller ama wiki ingest akışında da kontrol şart.

### Examples

#### ✅ Do
```bash
cd ~/.kimi/skills/local-wiki/ && python3 scripts/wiki_lint.py /home/akn/local/wiki
# PASS/WARN/FAIL kontrolü yap
```

#### ❌ Don't
```bash
# Doğrudan commit — neden: lint hatası push sonrası fark edilir
git add wiki/ && git commit -m "docs(wiki): ..."
```

### Related
- `local-wiki` skill
- [[wiki-growth-protocol]]

---

## Ders 004: Entegrasyon değişikliklerini ilk implementasyonda test et
**Confidence:** 0.80
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** scripts/wiki-assistant.py
**Scope:** genel
**Type:** anti-pattern

### Context
ACE sistemini wiki'ye entegre ederken wiki-assistant.py ace'yi tanımıyordu ve map_to_wiki yanlış hedefe yönlendiriyordu.

### Rule
Yeni bir alt sistem eklerken (ACE gibi), mevcut otomasyon araçlarının (wiki-assistant.py) onu tanıyıp tanımadığını, dosya eşlemelerinin doğru çalışıp çalışmadığını hemen test et.

### Rationale
Entegrasyon 'teoride çalışır' ama pratikte kırık olabilir. Erken test etmek ileride büyük zaman kaybını ve tutarsızlığı önler.

### Examples
#### ✅ Do
```bash
python3 scripts/wiki-assistant.py --prepare --project ace --pretty
```

#### ❌ Don't
```bash
# Dokümantasyonda 'ace topla' ile wiki ingest çalışır yaz, ama hiç test etme
```

### Related
- [[playbook]]

---

## Ders 005: Wiki query'de asistan birincil kaynak
**Confidence:** 0.80
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** AGENTS.md
**Scope:** genel
**Type:** anti-pattern

### Context
Bu oturumda wiki'den ACRA/Telegram bilgisi ararken doğrudan Grep + ReadFile kullandım. Kullanıcı AGENTS.md'de asistanın birincil kaynak olması gerektiğini hatırlattı.

### Rule
Wiki bilgi aramasında önce python3 scripts/wiki-assistant.py --query '<konu>' kullan. Asistan çalışmazsa veya yetersiz kalırsa Grep / ReadFile fallback'e dön.

### Rationale
Asistan wiki/.assistant-index.json cache'ini kullanır, ilgili sayfaları ve bölümleri JSON olarak sunar. Doğrudan Grep körü körüne arama yapar, gereksiz dosya okumalarına ve token israfına yol açar.

### Examples
#### ✅ Do
```python
python3 scripts/wiki-assistant.py --query 'acra crash telegram'
```

#### ❌ Don't
```python
Grep -r 'acra' wiki/ && ReadFile wiki/projects/mathlock-play.md
```

### Related


---

## Ders 006: LSP static analizdir, debug runtime'tır — kategoriler karıştırılmamalı
**Confidence:** 0.80
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** AGENTS.md
**Scope:** genel
**Type:** pattern

### Context
Kod debug/araştırma task'lerinde LSP'nin birinci kaynak olup olmayacağı tartışıldı. ACRA crash'i logcat'te görünüyordu, LSP bunu asla göremezdi.

### Rule
Static kod yapısı (symbol, reference, tip) için LSP (--locate) birincildir. Runtime davranış (crash, log, network, DB) için adb logcat, journalctl, curl, psql birincildir.

### Rationale
LSP kodun yazılışını gösterir, çalışma zamanını görmez. Bir crash'in nedenini anlamak için logcat gerekir; LSP 'kod doğru görünüyor' dediği halde uygulama çökebilir.

### Examples
#### ✅ Do
```python
adb logcat -d | grep 'FATAL EXCEPTION' # Runtime önce
```

#### ❌ Don't
```python
scripts/wiki-assistant.py --locate --file MathLockApplication.kt --symbol initAcra # Debug'ta LSP yetersiz
```

### Related


---

## Ders 007: LSP desteklemeyen dosya turlerinde locate_in_file fallback'i kullan
**Confidence:** 0.80
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** scripts/wiki-assistant.py
**Scope:** genel
**Type:** workflow

### Context
Kullanici strings.xml'deki app_name'i aramak istedi. wiki-assistant.py --locate cagrildiginda .xml uzantisi LSP tarafindan desteklenmiyordu ve hata dondurdu.

### Rule
.xml, .json, .yaml, .gradle, .kts, .sh, .conf, .toml gibi yapilandirma dosyalarinda sembol ararken wiki-assistant.py --locate otomatik olarak grep-based fallback (locate_in_file) kullanir. LSP client (Pyright, tsserver, kotlin-ls) bu dosya turlerini parse edemez; cagirmak bosuna zaman kaybidir.

### Rationale
LSP sunuculari sadece kod dosyalarini (.py, .js, .ts, .kt) anlar. Yapilandirma dosyalarinda basit metin aramasi yeterli ve daha hizlidir.

### Examples
#### ✅ Do
```python
python3 scripts/wiki-assistant.py --locate --file app/src/main/res/values/strings.xml --symbol app_name
```

#### ❌ Don't
```python
python3 scripts/lsp-client.py --language python --file strings.xml --symbol app_name  # Hata: Sembol listesi bos dondu
```

### Related


---

## Ders 008: AGENTS.md'deki komutlar implemente edilmemis olabilir — onceden dogrula
**Confidence:** 0.80
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** AGENTS.md, scripts/wiki-assistant.py
**Scope:** genel
**Type:** anti-pattern

### Context
AGENTS.md'de scripts/wiki-assistant.py --query '<konu>' kullanimi belirtilmisti ama --query parametresi aslinda implemente edilmemisti. Kullanici 'wiki aramasi yapalim' dediginde komut calismadi.

### Rule
AGENTS.md, README veya wiki'de belirtilen bir komut/script kullanmadan once 'script --help' ile mevcut parametreleri kontrol et. Eksikse implemente et, sonra kullan. Dokumantasyon ile kod arasinda tutarsizlik varsa agent yanlis komut calistirir ve fallback'e duser.

### Rationale
Dokumantasyon guncel kalabilir ama kod geride kalabilir (veya tersi). Ozellikle scripts/wiki-*.py gibi hizla evrilen araclarda bu tutarsizlik sik gorulur.

### Examples
#### ✅ Do
```python
python3 scripts/wiki-assistant.py --help  # --query yoksa -> ekle, sonra kullan
```

#### ❌ Don't
```python
python3 scripts/wiki-assistant.py --query 'LSP'  # Hata: unrecognized arguments
```

### Related


---

## Ders 009: Ders ekleme karari — tereddutte kalma, sebep varsa ekle
**Confidence:** 0.65
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Validations:** 0
**Source:** wiki/ace/playbook.md
**Scope:** genel
**Type:** workflow

### Context
Ace topla sirasinda hangi derslerin eklenecegi konusunda tereddutte kalindi. Kullanici 'ikisini mi ucunu mu ekleyeyim, birini mi seceyim' diye sordu.

### Rule
Ace topla / ders cikarma sirasinda bir dersin eklenip eklenmeyecegi konusunda tereddutte kalirsan, eklemek icin somut bir sebep varsa (somut ornek, tekrarlanabilir pattern, zaman kaybi, bug) kullaniciya sorma, dogrudan ekle. Kullanici 'ace topla' dediginde butun bakimi agent'a devretmis olur.

### Rationale
Her ders icin 'ekleyeyim mi?' diye sormak kullaniciyi yorar ve workflow'u yavaslatir. Dusuk confidence (0.50-0.70) dersler zaten prune ile temizlenir. Ekleme kararini agent versin, silme/prune kararini kullanici versin.

### Examples
#### ✅ Do
```python
ace topla sirasinda 2 ders taslagi cikar -> ikisi de somut, test edilmis, tekrarlanabilir -> ikisini de dogrudan ekle, kullaniciya sorma
```

#### ❌ Don't
```python
Her ders icin 'bunu ekleyeyim mi?' diye sormak -> kullanici yorulur, ace topla anlamini yitirir
```

### Related


---

## Ders 010: Android companion object'te getString() kullanılamaz
**Confidence:** 0.80
**Created:** 2026-05-31
**Updated:** 2026-05-31
**Validations:** 0
**Source:** app/src/main/java/com/akn/mathlock/PerformanceReportActivity.kt
**Scope:** mathlock-play
**Type:** anti-pattern

### Context
MathLock Play i18n refactor'ünde PERIOD_LABELS ve TYPE_LABELS map'lerini strings.xml referanslarına çevirmek için companion object içinde getString(R.string...) kullanan fonksiyonlar yazıldı. Derleme sırasında Unresolved reference: getString hatası alındı.

### Rule
Activity companion object'inde Context erişimi yoktur. getString(), getColor(), resources gibi Context-bağımlı çağrılar companion object'te yapılamaz. Bu fonksiyonları class seviyesinde (instance method) tanımla.

### Rationale
Companion object static/ singleton benzeri davranır; Activity instance'ı ve dolayısıyla Context yoktur. Kotlin'de companion object fonksiyonları class instance'ına erişemez.

### Examples
#### ✅ Do
```python

```

#### ❌ Don't
```python

```

### Related


---

## Ders 011: Android strings.xml'de apostrophe karakteri escape edilmeli
**Confidence:** 0.80
**Created:** 2026-05-31
**Updated:** 2026-05-31
**Validations:** 0
**Source:** app/src/main/res/values-en/strings.xml
**Scope:** mathlock-play
**Type:** pitfall

### Context
values-en/strings.xml'e İngilizce çeviriler eklenirken 'Time's up!', 'There's another hint!' gibi string'ler doğrudan yazıldı. Derleme sırasında Invalid unicode escape sequence in string hatası alındı.

### Rule
Android string resources'ta tek tırnak (') karakteri \' olarak escape edilmelidir — ozellikle values-en/strings.xml gibi non-default dil dosyalarinda.

### Rationale
Android AAPT compiler non-default dil string'lerini parse ederken apostrophe'u escape sequence baslangici olarak yorumlayabiliyor. TR (default) dilde bu sorun daha az goruluyor ama EN dosyasinda kesin escape gerekli.

### Examples
#### ✅ Do
```python

```

#### ❌ Don't
```python

```

### Related


---

## Ders 012: Duplicate string key'ler mergeDebugResources hatasi verir
**Confidence:** 0.80
**Created:** 2026-05-31
**Updated:** 2026-05-31
**Validations:** 0
**Source:** app/src/main/res/values/strings.xml
**Scope:** mathlock-play
**Type:** pitfall

### Context
Aşama 1'de activity_settings.xml için btn_test_math ve btn_test_guess string'leri eklenirken ayni key'ler zaten MainActivity için mevcuttu. Farkli degerler ayni key ile tanimlandi. Derleme: Found item String/btn_test_math more than one time.

### Rule
Yeni @string/ referansi eklemeden once values/strings.xml'de ayni key'in olup olmadigini kontrol et. Varsa mevcut key'i yeniden kullan veya farkli bir key adi sec (ornegin settings_btn_test_math).

### Rationale
Android build system'de ayni resource key birden fazla kez tanimlanamaz. Bu hata mergeDebugResources asamasinda yakalanir ve tum build'i durdurur.

### Examples
#### ✅ Do
```python

```

#### ❌ Don't
```python

```

### Related


---

## Ders 013: Util paketi siniflari com.akn.mathlock.R import'u gerektirir
**Confidence:** 0.80
**Created:** 2026-05-31
**Updated:** 2026-05-31
**Validations:** 0
**Source:** app/src/main/java/com/akn/mathlock/util/AccountManager.kt
**Scope:** mathlock-play
**Type:** pitfall

### Context
AccountManager, BillingHelper ve SecurePrefs utility siniflarinda getString(R.string...) kullanilmaya baslandi. Derleme: Unresolved reference: R. Bu siniflar com.akn.mathlock.util paketinde oldugu icin R sinifi otomatik olarak erisilebilir degil.

### Rule
com.akn.mathlock.util (veya diger alt paketlerdeki) Kotlin siniflarinda R.string, R.drawable, R.id vb. kullanilacaksa dosyanin en ustune 'import com.akn.mathlock.R' eklenmelidir.

### Rationale
Android'de R sinifi uygulama paketinin kokunde (com.akn.mathlock) olusturulur. Alt paketlerdeki siniflar icin otomatik import yoktur; manuel import sarttir.

### Examples
#### ✅ Do
```python

```

#### ❌ Don't
```python

```

### Related


---
