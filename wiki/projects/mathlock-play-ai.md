---
title: "MathLock Play — AI Soru Pipeline"
created: 2026-05-07
updated: 2026-05-07
type: project
tags: [mathlock-play, ai, pipeline, adaptive-learning, meb]
related:
  - mathlock-play
  - mathlock-play-android
  - mathlock-play-backend
  - kimi-code-cli
---

# MathLock Play — AI Soru Pipeline

AI destekli adaptif matematik soru üretim sistemi. Her 30/40/50 soruluk set tamamlandığında performans verisi (`stats.json`) VPS'e yüklenir ve AI yeni seti çocuğun seviyesine göre üretir.

## AI Soru Döngüsü

```
Telefon ← VPS: questions.json, levels.json, topics.json
Çocuk 50 soru çözer → stats.json VPS'e yüklenir
VPS: AI ([[kimi-code-cli|kimi-cli]]) yeni soru seti üretir → validate → DB
Telefon yeni seti indirir
```

### Batch 0 (Ücretsiz 50 Soru) vs Batch 1+ (Kredi ile)

| Özellik | Batch 0 (Ücretsiz) | Batch 1+ (Kredi) |
|---|---|---|
| Kaynak | `data/questions-<dönem>.json` → DB | `ai-generate.sh` + `kimi-cli` ile anlık üretim |
| Yaş uygunluğu | ✅ 5 ayrı set (okul öncesi / 1-4. sınıf) | ✅ `agents/questions-*.agents.md` ile adaptif |
| Çarpma/bölme | Okul öncesi: yok, 1. sınıf: YOK (MEB uyumu) | Algoritmaya göre adaptif |
| Zorluk | Statik (yaşa göre) | Dinamik (çocuğun performansına göre) |

**Batch 0 dosyaları:**
- `data/questions-okul_oncesi.json` — 30 soru, sadece toplama/çıkarma (1-5 arası)
- `data/questions-sinif_1.json` — 40 soru, sadece toplama/çıkarma (MEB 1. sınıf müfredatında çarpma yoktur)
- `data/questions-sinif_2.json` — 50 soru, mevcut varsayılan seviye
- `data/questions-sinif_3.json` — 50 soru, biraz daha zor
- `data/questions-sinif_4.json` — 50 soru, en zor seviye

**Üretim komutu:**
```bash
cd projects/mathlock-play
python3 scripts/generate_age_questions.py
```

### AI Adaptif Soru Üretim Pipeline

**Trigger:** `POST /api/mathlock/credits/use/` → `use_credit()` → `_generate_via_kimi()`

**Pipeline:**
1. `child.stats_json` → geçici `stats.json`
2. `ai-generate.sh --vps-mode --skip-sync --period <dönem> --data-dir <tmp>`
3. `agents/swap-helper.sh` ile doğru `agents/questions-<dönem>.agents.md` dosyası `AGENTS.md` olarak swap edilir
4. `kimi-cli` çalıştırılır → `questions.json`, `topics.json`, `report.json` üretir
5. `validate-questions.py` doğrulama → başarısızsa retry (max 2)
6. `QuestionSet` olarak DB'ye kaydet

**Agent dosyaları (`agents/`):**

| Dosya | Amaç |
|---|---|
| `questions-okul-oncesi.agents.md` | 30 soru, çarpma/bölme YASAK |
| `questions-sinif-1.agents.md` | 40 soru, çarpma/bölme YASAK (MEB uyumu) |
| `questions-sinif-2.agents.md` | 50 soru, 2. sınıf müfredatı (çarpma giriş, kare YOK) |
| `questions-sinif-3.agents.md` | 50 soru, üniter kesirler, max 2 işlemli problem |
| `questions-sinif-4.agents.md` | 50 soru, gelişmiş kesirler, 3+ işlemli problem |
| `levels-*.agents.md` | Sayı Yolculuğu bulmaca seviyeleri |
| `swap-helper.sh` | AGENTS.md swap/temizlik |

**Adaptif Algoritma Özeti (AGENTS.md §4):**
- **Performans analizi:** `byType` verisinden başarı oranı + süre hesaplanır
- **Kategoriler:** USTA (%85+), GÜVENLİ (%85+ ama yavaş), GELİŞEN (%60-84), ZORLU (%40-59), KRİTİK (%40 altı)
- **Soru dağılımı:** %40 pekiştirme (zayıf alanlar), %35 gelişim, %25 meydan okuma
- **Psikolojik sıralama:** İlk 3 soru kolay (güven), orta zorlukta devam, son 2 kolay (bitirme hissi)
- **Zorluk ayarı:** Başarı ve süreye göre zorluk 1-5 arası dinamik ayarlanır

### Tip İsimlendirme Standardizasyonu (2026-05-07)

Tüm yaş gruplarında tip isimleri Türkçe karakterli olarak standartlaştırılmıştır:

| Tip | Eski (karaktersiz) | Yeni (standart) |
|-----|-------------------|-----------------|
| Toplama | `toplama` | `toplama` (değişmedi) |
| Çıkarma | `cikarma` | `çıkarma` |
| Çarpma | `carpma` | `çarpma` |
| Bölme | `bolme` | `bölme` |
| Sıralama | `siralama` | `sıralama` |
| Eksik Sayı | `eksik_sayi` | `eksik_sayı` |
| Karşılaştırma | `karsilastirma` | `karşılaştırma` (okul öncesi) |
| Örüntü | `oruntu` | `örüntü` (okul öncesi) |

**Teknik etki:** `MathChallengeActivity.kt` içindeki `q.type == "siralama"` kontrolü `q.type == "sıralama"` olarak güncellendi. `StatsDashboardActivity.kt` ve `PerformanceReportActivity.kt` içindeki `TYPE_LABELS` sözlük anahtarları da Türkçe karakterli hale getirildi (`cikarma` → `çıkarma`, `carpma` → `çarpma`, `bolme` → `bölme`, `siralama` → `sıralama`, `eksik_sayi` → `eksik_sayı`, `karsilastirma` → `karşılaştırma`). `generate_age_questions.py` ve `MathQuestionGenerator.kt` zaten Türkçe karakterli üretiyordu; agents.md dosyalarındaki tutarsızlık giderildi.

### MEB Müfredat Uyumu (2026-05-07)

| Sınıf | Değişiklik | Gerekçe |
|-------|-----------|---------|
| 1. Sınıf | Çarpma üretimi %0 (eski: %20) | MEB 1. sınıfta çarpma yoktur |
| 1. Sınıf | Çıkarma: onluktan bozma kontrolü eklendi | `b ≤ (a mod 10)` kuralı ile onluktan bozma engellenir |
| 1. Sınıf | `generate_age_questions.py` + `MathQuestionGenerator.kt` onluktan bozma kontrolü | Batch 0 ve fallback modda 15-8 gibi sorular üretilemiyor |
| 2. Sınıf | Kare tipi kaldırıldı | MEB 2. sınıfta kare sayılar yoktur |
| 2. Sınıf | `data/questions-sinif_2.json` regenerate edildi | Eski dosyada kare tipi kalmıştı, temizlendi |
| 2. Sınıf | Zorluk 5 toplama üst limiti 100 yapıldı | MEB "100'e kadar eldeli toplama" kazanımı |
| 2. Sınıf | `questions-sinif-2.agents.md` zorluk 5 toplama aralığı genişletildi | `a: 10-40` → `a: 10-50`, max sonuç 90 → 100 |
| 3. Sınıf | Kesir: sadece üniter kesirler (pay=1) | MEB 3. sınıfta non-üniter kesirler yoktur |
| 3. Sınıf | `curriculum/sinif_3.json` non-üniter kesir düzeltildi | Zorluk 4-5 `2/3` ve `3/5` → `1/4` ve `1/6` |
| 3. Sınıf | Problem: maksimum 2 işlem | MEB 3. sınıf problem çözmede max 2 işlem |
| 1. Sınıf | `generate_age_questions.py` çıkarma sonucu=0 hatası düzeltildi | `b <= a % 10` kuralına `b < a` garantisi eklendi |
| Tümü | Rapor şablonları yaş grubuna özgü hale getirildi | Kopyala-yapıştır hataları giderildi |
| Tümü | Backend `Question.question_type` help text güncellendi | Türkçe karakterli tip isimleri doğrulandı |

### Batch 0 Üretim Algoritması (`generate_age_questions.py`)

Batch 0, `scripts/generate_age_questions.py` tarafından deterministik (seed=42) üretilir. Her yaş grubu için farklı işlem dağılımı, sayı aralığı ve zorluk skalası uygulanır.

**Ana yapı:**
```python
# Her yaş grubu için: generator(count) → add_hints(questions) → package(questions, period)
def generate_addition(max_a, max_b)     # a + b = ?, difficulty = f(max_a)
def generate_subtraction(min_a, max_a)  # a - b = ?, difficulty = f(max_a)
def generate_multiplication(max_a, max_b)  # a × b = ?, difficulty = f(max_a)
def generate_division(max_divisor, max_result)  # a ÷ b = ?, difficulty = f(max_divisor)
```

**Zorluk hesaplama (heuristic):**
```python
# file: projects/mathlock-play/scripts/generate_age_questions.py
difficulty = 1 if max_a <= 10 else (2 if max_a <= 50 else 3)
```

> **Bilinen uyumsuzluk:** `generate_age_questions.py` zorluk skalasını 1-3 arası üretirken, `agents.md` dosyaları 1-5 skalasını tanımlar. Batch 0'da zorluk 4-5 soruları bulunmaz; bu seviyeler sadece AI pipeline (Batch 1+) tarafından üretilir. Adaptif algoritma zorluk 1-5 arası ayar yapar, ancak batch 0 setinde zorluk 3 ile sınırlıdır.

**ID aralıkları (`ID_RANGES`) — DB unique constraint çakışmasını önler:**
| Dönem | Offset | ID aralığı |
|-------|--------|-----------|
| `okul_oncesi` | 1000 | 1001-1030 |
| `sinif_1` | 2000 | 2001-2040 |
| `sinif_2` | 3000 | 3001-3050 |
| `sinif_3` | 4000 | 4001-4050 |
| `sinif_4` | 5000 | 5001-5050 |

**Yaş grubu başına işlem dağılımı:**

| Dönem | Toplama | Çıkarma | Çarpma | Bölme | Kare | Soru Sayısı |
|-------|---------|---------|--------|-------|------|-------------|
| Okul Öncesi | %50 | %50 | — | — | — | 30 |
| 1. Sınıf | %55 | %45 | — | — | — | 40 |
| 2. Sınıf | %25 | %25 | %25 | %25 | — | 50 |
| 3. Sınıf | %20 | %20 | %20 | %20 | %20 | 50 |
| 4. Sınıf | %20 | %20 | %20 | %20 | %20 | 50 |

---

> Android fallback üretimi ve oyun detayları için bkz. [[mathlock-play-android]]
> Backend API ve auth detayları için bkz. [[mathlock-play-backend]]
