# MathLock AI - Adaptif Matematik Soru Motoru (3. Sınıf, 8-9 yaş)

## 1. Misyon

Bu dosya, 8-9 yaşında ilkokul **3. sınıfa** giden bir çocuk için **adaptif matematik soru seti** üreten AI modelinin çalışma kılavuzudur.

Çocuk telefonunda bir uygulama açmak istediğinde matematik sorusu çözer. Her **50** soruluk set tamamlandığında performans verisi (`stats.json`) VPS'e yüklenir.

**Pedagojik temel:** Vygotsky'nin Yakınsal Gelişim Alanı. Hedef başarı oranı: **%65-80**

**Bu dönemde** 2. sınıfa ek olarak: çarpma tablosu tam (1-10), çok basamaklı işlemler (0-9999), kesir giriş ve problem çözme eklenir.

## 2. Çalışma Ortamı

- Dizin: `/home/akn/vps/projects/mathlock-play/`
- Veri dizini: `data/`
- Dokunulacak dosyalar: SADECE `data/questions.json` ve `data/topics.json`

## 3. Görev Adımları

2. sınıf agent'ıyla aynı — Veri Oku → Analiz → 50 Soru Üret → topics.json Güncelle → Rapor

---

## 4. Adaptif Algoritma (Kalp)

### 4.1 Performans Analizi

2. sınıf agent'ıyla aynı kategori tablosu:

| Kategori | Başarı | Süre | Anlam |
|----------|--------|------|-------|
| USTA | >= %85 | < 5sn | Çok iyi biliyor |
| GÜVENLİ | >= %85 | 5-10sn | Biliyor ama hızlanmadı |
| GELİŞEN | %60-84 | herhangi | İdeal bölge |
| ZORLU | %40-59 | herhangi | Destek gerekli |
| KRİTİK | < %40 | herhangi | Temele dön |

### 4.2-4.3 İpucu/Konu Analizi ve Zorluk Karar Matrisi

2. sınıf agent'ıyla birebir aynı kurallar geçerli.

### 4.4 Soru Dağıtım Algoritması

Her sette **50 soru**:
- GRUP A - Pekiştirme (%40 = 20 soru)
- GRUP B - Gelişim (%35 = 17-18 soru)
- GRUP C - Meydan Okuma (%25 = 12-13 soru)

Sınırlamalar: Tek tipten max **8**, KRİTİK tipten max **5**, tip başına min **2**.

### 4.5 Yeni Tip Tanıtma Sırası

3. sınıf müfredatına göre:

```
Seviye 1: toplama + çıkarma + çarpma + bölme + sıralama + eksik_sayı
          (2. sınıftan gelen çocuk bunları zaten biliyor)
Seviye 2: + kesir        (dört işlemde ortalama başarı >= %70 ise)
Seviye 3: + problem      (kesir dahil tümünde başarı >= %70 ise)
```

**İlk set tanıtımı:** 2. sınıftan gelen çocuğun zaten tüm temel 6 tipi bildiği varsayılır. İlk sette 6 tip + kesir tanıtılır.

### 4.6 Soru Sıralama Algoritması

2. sınıf agent'ıyla aynı (pozisyon 1-3 kolay, 49-50 kolay, ortada karışık).

---

## 5. İlk Set Algoritması

### Dağıtım:
- toplama: 12 soru (6x zorluk 2 + 6x zorluk 3)
- çıkarma: 10 soru (5x zorluk 2 + 5x zorluk 3)
- çarpma: 10 soru (5x zorluk 2 + 5x zorluk 3)
- bölme: 8 soru (5x zorluk 2 + 3x zorluk 3)
- sıralama: 3 soru (3x zorluk 2)
- eksik_sayı: 3 soru (3x zorluk 2)
- kesir: 3 soru (3x zorluk 1 — yeni tip tanıtımı)
- problem: 1 soru (1x zorluk 1 — yeni tip tanıtımı)

### difficultyProfile:
```json
{
  "overall": "developing",
  "avgDifficulty": 2.3,
  "adjustmentReason": "İlk set - 3. sınıf, 2. sınıf konularını bildiği varsayılır"
}
```

---

## 6. questions.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-03-22T14:00:00Z",
  "generatedBy": "ai",
  "educationPeriod": "sinif_3",
  "questionCount": 50,
  "difficultyProfile": { ... },
  "questions": [...]
}
```

| Alan | Tip | Kural |
|------|-----|-------|
| id | int | 1-50 arası benzersiz |
| text | string | `= ?` ile biter |
| answer | int | >= 0 |
| type | string | `toplama`, `çıkarma`, `çarpma`, `bölme`, `sıralama`, `eksik_sayı`, `kesir`, `problem` |
| difficulty | int | 1-5 |
| hint | string | Türkçe, çocuk dili, cevabı vermez |

### Operatör Sembolleri:
- Toplama: `+`, Çıkarma: `-`, Çarpma: `x`, Bölme: `÷`, Eşittir: `=`, Bilinmeyen: `?`

---

## 7. Soru Tipleri ve Zorluk Seviyeleri

### 7.1 Toplama (Çok Basamaklı, 0-9999)

| Zorluk | Sayı Aralığı | Sonuç | Örnek |
|--------|--------------|-------|-------|
| 1 | a: 1-9, b: 1-9 | ≤ 18 | 7 + 8 = ? |
| 2 | a: 10-99, b: 1-20 | ≤ 120 | 45 + 17 = ? |
| 3 | a: 50-200, b: 10-99 | ≤ 300 | 135 + 78 = ? |
| 4 | a: 100-500, b: 50-200 | ≤ 700 | 325 + 178 = ? |
| 5 | a: 200-999, b: 100-500 | ≤ 1500 | 678 + 435 = ? |

### 7.2 Çıkarma (Onluktan Bozmalı, 0-9999)

| Zorluk | Sayı Aralığı | Sonuç | Örnek |
|--------|--------------|-------|-------|
| 1 | a: 2-10, b: 1-(a-1) | ≥ 1 | 9 - 4 = ? |
| 2 | a: 10-99, b: 1-20 | ≥ 1 | 53 - 17 = ? |
| 3 | a: 50-200, b: 10-99 | ≥ 1 | 175 - 89 = ? |
| 4 | a: 200-999, b: 50-200 | ≥ 1 | 534 - 167 = ? |
| 5 | a: 500-2000, b: 200-1000 | ≥ 1 | 1450 - 768 = ? |

### 7.3 Çarpma (1-10 Tablosu Tam)

| Zorluk | Çarpanlar | Sonuç | Örnek |
|--------|-----------|-------|-------|
| 1 | a: 2-5, b: 2-5 | ≤ 25 | 4 x 3 = ? |
| 2 | a: 2-9, b: 2-9 | ≤ 81 | 7 x 8 = ? |
| 3 | a: 10-20, b: 2-5 | ≤ 100 | 15 x 4 = ? |
| 4 | a: 10-50, b: 2-9 | ≤ 450 | 35 x 7 = ? |
| 5 | a: 20-100, b: 2-9 | ≤ 900 | 85 x 9 = ? |

**KURAL:** Zorluk 1-2'de çarpım tablosu içinde kal. Zorluk 3+'te çok basamaklı × tek basamaklı.

### 7.4 Bölme (Tek Basamağa Bölme)

| Zorluk | Sayı Aralığı | Bölüm | Örnek |
|--------|--------------|-------|-------|
| 1 | a ÷ b, b: 2-5, a: b'nin katları, a ≤ 25 | 2-5 | 15 ÷ 3 = ? |
| 2 | a ÷ b, b: 2-9, a: b'nin katları, a ≤ 81 | 2-9 | 42 ÷ 7 = ? |
| 3 | a ÷ b, b: 2-9, a: b'nin katları, a ≤ 100 | 2-20 | 72 ÷ 8 = ? |
| 4 | a ÷ b, b: 2-9, a: b'nin katları, a ≤ 200 | 2-30 | 168 ÷ 8 = ? |
| 5 | a ÷ b, b: 2-9, a: b'nin katları, a ≤ 500 | 2-60 | 450 ÷ 9 = ? |

**KURAL:** Tam bölme (kalan = 0). Sıfıra bölme YASAK.

### 7.5 Sıralama

2. sınıf formatıyla aynı ama sayı aralığı 0-9999.

| Zorluk | Format | Aralık | Örnek |
|--------|--------|--------|-------|
| 1 | Hangisi büyük: A, B = ? | 1-50 | Hangisi büyük: 23, 47 = ? |
| 2 | En küçüğü: A, B, C = ? | 1-100 | En küçüğü hangisi: 45, 12, 78 = ? |
| 3 | En küçüğü: A, B, C, D = ? | 1-500 | En küçüğü hangisi: 123, 456, 89, 234 = ? |
| 4 | En büyüğü: A, B, C, D, E = ? | 1-1000 | En büyüğü hangisi: 345, 890, 123, 567, 234 = ? |
| 5 | X ile Y arası kaç sayı = ? | 1-1000 | 245 ile 252 arasında kaç sayı var = ? |

### 7.6 Eksik Sayı

| Zorluk | Format | Aralık | Örnek |
|--------|--------|--------|-------|
| 1 | ? + a = b | a: 1-10, b: 5-20 | ? + 7 = 15 |
| 2 | a + ? = b | a: 10-30, b: 20-50 | 18 + ? = 35 |
| 3 | ? - a = b | a: 5-20, b: 5-30 | ? - 12 = 23 |
| 4 | a x ? = b | a: 2-9, b: a'nın katı, b ≤ 81 | 6 x ? = 42 |
| 5 | ? ÷ a = b | a: 2-9, b: 2-10 | ? ÷ 7 = 8 |

### 7.7 Kesir (YENİ — 3. sınıf, ÜNİTER kesirler)

**KURAL:** 3. sınıf müfredatında sadece üniter kesirler (pay = 1) vardır. Non-üniter kesirler (2/3, 3/5 vb.) 4. sınıfta tanıtılır.

| Zorluk | Format | Örnek |
|--------|--------|-------|
| 1 | a'nın yarısı (1/2) kaçtır? | 12'nin yarısı kaçtır = ? → answer: 6 |
| 2 | a'nın üçte biri (1/3) kaçtır? | 15'in üçte biri kaçtır = ? → answer: 5 |
| 3 | a'nın çeyreği (1/4) kaçtır? | 20'nin çeyreği kaçtır = ? → answer: 5 |
| 4 | a'nın beşte biri (1/5) kaçtır? | 25'in beşte biri kaçtır = ? → answer: 5 |
| 5 | a'nın sekizde biri (1/8) kaçtır? | 40'ın sekizde biri kaçtır = ? → answer: 5 |

**KURAL:** Kesir sorusu sonucu HER ZAMAN tam sayı. `a` değeri paydanın katı olmalı.

**text formatı:** `{a}'nin {kesir_metin} kaçtır = ?`
**answer:** tam sayı sonuç

### 7.8 Problem (YENİ — 3. sınıf, maksimum 2 işlem)

**KURAL:** 3. sınıf müfredatında problem çözmede maksimum 2 işlem beklenir. 3+ işlemli problemler 4. sınıfta tanıtılır.

| Zorluk | Format | Örnek |
|--------|--------|-------|
| 1 | Tek işlem (toplama/çıkarma) | Ali'nin 25 TL'si var. 12 TL harcadı. Kaç TL kaldı = ? |
| 2 | Tek işlem (çarpma/bölme) | 4 kutudan her birinde 6 kalem var. Toplam kaç kalem var = ? |
| 3 | İki işlem (topla/çıkar) | Ayşe'nin 30 bilyesi var. 8 tane verdi, 5 tane aldı. Kaç bilyesi var = ? |
| 4 | İki işlem (çarp/böl) | 48 çikolata 8 çocuğa eşit paylaştırıldı. Kaçar tane düştü = ? |
| 5 | İki işlem (karışık) | 5 kutu × 8 kalem + 12 kalem = toplam kaç kalem var = ? |

**KURAL:** Problem metni Türkçe, günlük hayat dili, 8-9 yaş seviyesi. Sonuç her zaman >= 0. `text` alanına problemin tamamı ve `= ?` yazılır.

---

## 8. İpucu Tasarım Kuralları

2. sınıf kuralları + ek:

**Kesir:** "Sayıyı paydaya böl, pay ile çarp"
**Problem:** "Problemi adım adım çöz, ilk işlemi yap"

---

## 9. topics.json Şeması

2. sınıf formatı + ek konular:

```json
{
  "kesir": {
    "title": "🍕 Kesir Nedir?",
    "explanation": "Bir bütünü eşit parçalara böldüğümüzde her parça bir kesirdir.",
    "example": "Bir pizzayı 4 eşit parçaya böldün. 1 dilim = 1/4 pizza. 🍕🍕🍕🍕 → Her dilim = çeyrek!",
    "tips": ["Payda = kaç parçaya bölündü", "Pay = kaç parça aldık", "Sayıyı paydaya böl, sonra pay ile çarp"]
  },
  "problem": {
    "title": "🧩 Problem Çözme",
    "explanation": "Problemi oku, ne istendiğini bul, doğru işlemi seç.",
    "example": "Ali'nin 20 TL'si var, 8 TL harcadı → 20 - 8 = 12 TL kaldı!",
    "tips": ["Problemi 2 kere oku", "Ne verilmiş, ne isteniyor bul", "Doğru işlemi seç (+, -, x, ÷)"]
  }
}
```

---

## 10-11. stats.json ve Rapor

2. sınıf agent'ıyla aynı format. Rapor başlığı: "3. Sınıf Matematik Raporu"

---

## 12. Çıktı Gereksinimleri

1-13 arası 2. sınıf ile aynı + ek:
14. `type` geçerli: `toplama`, `çıkarma`, `çarpma`, `bölme`, `sıralama`, `eksik_sayı`, **kesir, problem**
15. Kesir sonucu tam sayı ve SADECE üniter kesirler (pay = 1)
16. Problem metni Türkçe, günlük hayat, maksimum 2 işlem
17. `educationPeriod` = "sinif_3"
18. `questionCount` = 50

## 13. Benzersizlik Garantisi

50 sorunun HER BİRİ farklı bir `text` değerine sahip olmalı.


---

## 14. Performans Raporu Üretimi

Soruları ürettikten sonra `data/report.json` dosyasına bir ebeveyn raporu yaz.

### Rapor Kuralları:
- Dil: Türkçe, sade, ebeveyne yönelik (pedagojik jargon kullanma)
- Olumlu başla, gelişim alanlarını yapıcı ifade et
- Somut öneriler ver (ne yapmalı, nasıl destek olmalı)
- Kıyaslama YAPMA (diğer çocuklarla karşılaştırma yok)

### data/report.json Formatı:
```json
{
  "reportDate": "2026-04-18",
  "summary": "Bu hafta toplam X soru çözüldü. Çarpma tablosu ve üniter kesirlerde çok başarılı (%Y). Problem çözmede gelişim gösteriyor.",
  "strengths": [
    "Çarpma tablosunu (1-10) hızlı ve doğru yapıyor",
    "Üniter kesirleri (1/2, 1/4) somut nesnelerle ilişkilendirebiliyor"
  ],
  "improvementAreas": [
    "Çok basamaklı çıkarmada onluktan bozmada bazen hata yapıyor",
    "Problem çözmede doğru işlemi seçmede zorlanıyor"
  ],
  "recommendation": "Problem çözme becerisini geliştirmek için günlük hayattan basit sorular sormak (market fişi, saat hesabı) faydalı olur.",
  "metrics": {
    "totalQuestionsSolved": 50,
    "averageAccuracy": 78.5,
    "byType": {
      "çarpma": {"accuracy": 92, "trend": "stable"},
      "kesir": {"accuracy": 80, "trend": "improving"},
      "problem": {"accuracy": 65, "trend": "improving"}
    }
  }
}
```

### Rapor Üretim Adımları:
1. `data/stats.json` oku — son performans verilerini analiz et
2. Konu bazlı başarı oranlarını hesapla
3. Güçlü yanları ve gelişim alanlarını belirle
4. Somut, yapıcı öneriler yaz
5. `data/report.json` dosyasına yaz (üzerine yaz)
