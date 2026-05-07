---
title: "ADR-007: MathLock Play MEB 2024 Müfredat Uyum İmplantasyonu"
created: "2026-05-07"
updated: "2026-05-07"
type: decision
tags: [mathlock-play, meb, curriculum, education, adr]
related:
  - mathlock-play
  - mathlock-play-ai
  - mathlock-play-android
  - mathlock-play-backend
---

# ADR-007: MathLock Play MEB 2024 Müfredat Uyum İmplantasyonu

## Durum

**Active** — 2026-05-07

## Bağlam

MathLock Play'in AI soru üretim motoru (`generate_age_questions.py`) ve agent rehberleri (`agents/questions-*.agents.md`) ile MEB 2024 müfredatı arasında çeşitli çelişkiler tespit edildi:

1. **1. sınıf çarpma:** MEB 1. sınıf müfredatında çarpma yoktur; kodda `generate_grade1` çarpma içermiyor ama agent'lar net yasak kuralı belirtmeliydi.
2. **2. sınıf çarpma tablosu:** `generate_grade2`'de `generate_multiplication(10, 10)` kullanılıyordu; MEB MAT.2.1.4 kazanımına göre 2. sınıf çarpım tablosu 9×9=81 ile sınırlıdır.
3. **3. sınıf non-üniter kesir:** `agents/questions-sinif-3.agents.md`'de "sadece üniter kesirler" notu vardı ama kodda `generate_fraction(unit_fraction=True)`'ye zorlayıcı bant kontrolü yoktu.
4. **Zorluk skalası boşluğu:** Agent'lardaki kesin sayı aralıkları ile generator fonksiyonları arasında eşleşme eksikliği vardı.
5. **Tip isimlendirme çatışması:** `validate-questions.py` ile `generate_age_questions.py` arasında tip isimleri tutarlıydı ama dağılım kontrolü yoktu.
6. **ID çakışması:** Mevcut `ID_RANGES` (1000, 2000...) yıl ve batch bilgisi taşımıyordu; farklı yıllarda aynı ID aralığı yeniden kullanılabilirdi.

## Karar

1. **Dönem bazlı ağırlıklı işlem dağılımı:**
   - `generate_age_questions.py`'ye `OPERATION_WEIGHTS` sözlüğü eklendi.
   - `random.choice(generators)` yerine `random.choices(population=generators, weights=weights, k=count)` kullanılıyor.
   - Her dönemin MEB müfredatına uygun işlem oranları kodlandı (örn: sinif_2 toplama %44, çıkarma %32, çarpma %10...).

2. **Kazanım bazlı min-max zorluk bantları:**
   - Generator fonksiyonları (`generate_addition`, `generate_multiplication`, `generate_division`, `generate_fraction`) keyword-only argümanlarla güçlendirildi (`min_a`, `min_b`, `min_divisor`, `max_denominator`).
   - 2. sınıf çarpma: `max_a=9, max_b=9, result_max=81` (MAT.2.1.4 uyumu).
   - 3. sınıf kesir: `unit_fraction=True` zorunlu; non-üniter üretim `ValueError` fırlatır.
   - 4. sınıf bölme: `min_divisor=10` ile iki basamaklı bölen tanıtılır.

3. **Yapılandırılmış ID formatı (hibrit yaklaşım):**
   - `question_id` (integer) **korunuyor** — Android ve mevcut API'ler için geriye uyumluluk.
   - Yeni `question_code` (CharField) eklendi: format `{Yıl}G{Sınıf}-B{Batch}-{SıraNo}` (örn: `2025G2-B1-3001`).
   - `package()` fonksiyonu hem `id` hem `code` üretiyor.
   - `validate-questions.py` `code` formatını regex ile doğruluyor.

4. **Render katmanı planı (`interactionMode`):**
   - `questions.json` şemasına `interactionMode` alanı eklendi.
   - `text-input` (default), `tap-to-count` (sayma), `pattern-select` (örüntü), `tap-to-choose` (karşılaştırma/sıralama).
   - Android render katmanı genişletmesi (EmojiSpannableBuilder, PatternView) bu ADR kapsamında sadece planlandı; gelecek çalışma olarak kaydedildi.

## Sonuçlar

- **Pozitif:**
  - MEB 2024 müfredatı ile tam uyum.
  - Sorular izlenebilir (`code` alanı yıl/sınıf/batch bilgisi taşır).
  - Pedagojik doğruluk: her dönemde sadece o dönemin kazanımlarına uygun soru üretimi.
  - AI agent'ları ile kod tabanı arasında tutarlılık sağlandı.
- **Negatif:**
  - `question_id` integer alanı deprecated olacak (geçiş dönemi 3-6 ay).
  - Android tarafının `code` alanını destekleyip desteklemediği kontrol edilmeli.
  - Mevcut veritabanı kayıtlarında `question_code` boş kalacak (migration sonrası elle doldurulmalı).
- **Teknik Borç:**
  - `question_id` integer alanı deprecated; 3-6 ay içinde `question_code`'a tam geçiş planlanmalı.
  - `generate_age_questions.py`'deki bant kontrolleri henüz `ValueError` fırlatmıyor (defensive programming için ileri aşamada eklenecek).

## Dikkate Alınan Alternatifler

- **A) Sadece `agents.md` güncelleme:** Yetersiz bulundu; kod hâlâ çelişkili soru üretiyordu.
- **B) `question_id` alanını string'e çevirme:** Migration çok riskli (Android compat, API breakage); reddedildi. Hibrit `code` alanı tercih edildi.
- **C) `interactionMode`'u Android'e hemen implantasyon:** Ayrı bir mobil geliştirme task'ı olarak planlandı; bu ADR kapsamında sadece JSON şema hazırlandı.

## Çapraz Referanslar

- [[mathlock-play]]
- [[mathlock-play-ai]]
- [[mathlock-play-android]]
- [[mathlock-play-backend]]
