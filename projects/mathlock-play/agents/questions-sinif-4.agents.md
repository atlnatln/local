# MathLock AI - Adaptif Matematik Soru Motoru (4. Sınıf, 9-10 yaş)

## 1. Misyon

Bu dosya, 9-10 yaşında ilkokul **4. sınıfa** giden bir çocuk için **adaptif matematik soru seti** üreten AI modelinin çalışma kılavuzudur.

Çocuk telefonunda bir uygulama açmak istediğinde matematik sorusu çözer. Her **50** soruluk set tamamlandığında performans verisi (`stats.json`) VPS'e yüklenir.

**Pedagojik temel:** Vygotsky'nin Yakınsal Gelişim Alanı. Hedef başarı oranı: **%65-80**

**Bu dönemde** 3. sınıfa ek olarak: çok basamaklı çarpma (3×2 basamak), çok basamaklı bölme (3÷2 basamak), gelişmiş kesirler ve çok adımlı problemler yer alır.

## 2. Çalışma Ortamı

- Dizin: `/home/akn/vps/projects/mathlock-play/`
- Veri dizini: `data/`
- Dokunulacak dosyalar: SADECE `data/questions.json` ve `data/topics.json`

## 3. Görev Adımları

2. sınıf agent'ıyla aynı akış.

---

## 4. Adaptif Algoritma (Kalp)

### 4.1-4.6 Tümü 2. sınıf agent'ıyla aynı kurallar

Tek fark — yeni tip tanıtma sırası:

### 4.5 Yeni Tip Tanıtma Sırası

4. sınıf müfredatına göre:

```
İlk set: toplama + çıkarma + çarpma + bölme + sıralama + eksik_sayı + kesir + problem
         (3. sınıftan gelen çocuk tüm bunları biliyor)
```

Bu dönemde yeni tip eklenmez — mevcut 8 tipin zorluk seviyeleri artar.

---

## 5. İlk Set Algoritması

### Dağıtım:
- toplama: 8 soru (4x zorluk 3 + 4x zorluk 4)
- çıkarma: 8 soru (4x zorluk 3 + 4x zorluk 4)
- çarpma: 8 soru (4x zorluk 3 + 4x zorluk 4)
- bölme: 7 soru (4x zorluk 3 + 3x zorluk 4)
- sıralama: 3 soru (3x zorluk 3)
- eksik_sayı: 4 soru (2x zorluk 3 + 2x zorluk 4)
- kesir: 6 soru (3x zorluk 2 + 3x zorluk 3)
- problem: 6 soru (3x zorluk 2 + 3x zorluk 3)

### difficultyProfile:
```json
{
  "overall": "intermediate",
  "avgDifficulty": 3.2,
  "adjustmentReason": "İlk set - 4. sınıf, 3. sınıf konularını bildiği varsayılır"
}
```

---

## 6. questions.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-03-22T14:00:00Z",
  "generatedBy": "ai",
  "educationPeriod": "sinif_4",
  "questionCount": 50,
  "difficultyProfile": { ... },
  "questions": [...]
}
```

| Alan | Tip | Kural |
|------|-----|-------|
| id | int | 1-50 arası benzersiz (geriye uyumluluk) |
| code | string | Yapılandırılmış ID: `YYYYG{Sınıf}-B{Batch}-{SıraNo}` (örn: `2025G4-B1-5001`) |
| text | string | `= ?` ile biter |
| answer | int | >= 0 |
| type | string | `toplama`, `çıkarma`, `çarpma`, `bölme`, `sıralama`, `eksik_sayı`, `kesir`, `problem` |
| difficulty | int | 1-5 |
| hint | string | Türkçe, çocuk dili, cevabı vermez |
| interactionMode | string | `text-input` (default), `tap-to-count`, `pattern-select`, `tap-to-choose` |

---

## 7. Soru Tipleri ve Zorluk Seviyeleri

### 7.1 Toplama (0-99999)

| Zorluk | Sayı Aralığı | Sonuç | Örnek |
|--------|--------------|-------|-------|
| 1 | a: 10-99, b: 1-20 | ≤ 120 | 45 + 17 = ? |
| 2 | a: 100-999, b: 10-200 | ≤ 1200 | 345 + 178 = ? |
| 3 | a: 500-2000, b: 100-999 | ≤ 3000 | 1250 + 875 = ? |
| 4 | a: 1000-5000, b: 500-2000 | ≤ 7000 | 3450 + 1780 = ? |
| 5 | a + b + c karışık | ≤ 10000 | 2500 + 1300 + 800 = ? |

### 7.2 Çıkarma (0-99999)

| Zorluk | Sayı Aralığı | Sonuç | Örnek |
|--------|--------------|-------|-------|
| 1 | a: 20-99, b: 1-20 | ≥ 1 | 67 - 19 = ? |
| 2 | a: 100-999, b: 10-200 | ≥ 1 | 543 - 178 = ? |
| 3 | a: 500-2000, b: 100-999 | ≥ 1 | 1500 - 867 = ? |
| 4 | a: 1000-5000, b: 500-2000 | ≥ 1 | 4200 - 1750 = ? |
| 5 | a - b - c karışık | ≥ 1 | 5000 - 1200 - 800 = ? |

### 7.3 Çarpma (Çok Basamaklı)

| Zorluk | Çarpanlar | Sonuç | Örnek |
|--------|-----------|-------|-------|
| 1 | a: 2-9, b: 2-9 | ≤ 81 | 7 x 8 = ? |
| 2 | a: 10-50, b: 2-9 | ≤ 450 | 35 x 7 = ? |
| 3 | a: 10-99, b: 10-20 | ≤ 1980 | 45 x 18 = ? |
| 4 | a: 100-200, b: 2-9 | ≤ 1800 | 175 x 8 = ? |
| 5 | a: 50-200, b: 10-50 | ≤ 10000 | 125 x 45 = ? |

**KURAL:** Sonuç 10000'i geçmez.

### 7.4 Bölme (İki Basamağa Bölme)

| Zorluk | Sayı Aralığı | Bölüm | Örnek |
|--------|--------------|-------|-------|
| 1 | a ÷ b, b: 2-9, a ≤ 81 | 2-9 | 56 ÷ 7 = ? |
| 2 | a ÷ b, b: 2-9, a ≤ 200 | 2-30 | 162 ÷ 9 = ? |
| 3 | a ÷ b, b: 10-20, a ≤ 500 | 2-50 | 360 ÷ 12 = ? |
| 4 | a ÷ b, b: 10-25, a ≤ 1000 | 2-100 | 750 ÷ 15 = ? |
| 5 | a ÷ b, b: 10-50, a ≤ 5000 | 2-200 | 2400 ÷ 48 = ? |

**KURAL:** Tam bölme (kalan = 0). `a` her zaman `b`'nin katı.

### 7.5 Sıralama

| Zorluk | Format | Aralık | Örnek |
|--------|--------|--------|-------|
| 1 | Hangisi büyük: A, B = ? | 1-100 | Hangisi büyük: 45, 78 = ? |
| 2 | En küçüğü: A, B, C = ? | 1-1000 | En küçüğü hangisi: 345, 127, 890 = ? |
| 3 | En küçüğü: A, B, C, D = ? | 1-5000 | En küçüğü hangisi: 1234, 987, 3456, 2345 = ? |
| 4 | En büyüğü: A, B, C, D, E = ? | 1-10000 | En büyüğü hangisi: ... = ? |
| 5 | X ile Y arası kaç sayı = ? | 1-10000 | 4567 ile 4575 arasında kaç sayı var = ? |

### 7.6 Eksik Sayı

| Zorluk | Format | Örnek |
|--------|--------|-------|
| 1 | ? + a = b | ? + 35 = 80 |
| 2 | a + ? = b | 125 + ? = 300 |
| 3 | ? - a = b | ? - 150 = 275 |
| 4 | a x ? = b (b: a'nın katı) | 15 x ? = 90 |
| 5 | ? ÷ a = b | ? ÷ 12 = 15 |

### 7.7 Kesir (Gelişmiş)

**KURAL:** 4. sınıfta non-üniter kesirler (pay > 1) ve denk kesirler tanıtılır.

| Zorluk | Format | Örnek |
|--------|--------|-------|
| 1 | a'nın 1/2'si kaçtır? | 24'ün yarısı kaçtır = ? → 12 |
| 2 | a'nın 1/4'ü kaçtır? | 36'nın çeyreği kaçtır = ? → 9 |
| 3 | a'nın 2/5'i kaçtır? | 30'un 2/5'i kaçtır = ? → 12 |
| 4 | a'nın 3/4'ü kaçtır? | 48'in 3/4'ü kaçtır = ? → 36 |
| 5 | a'nın 5/6'sı kaçtır? | 60'ın 5/6'sı kaçtır = ? → 50 |

**KURAL:** Sonuç HER ZAMAN tam sayı. `a` değeri paydanın katı olmalı.

### 7.8 Problem (Çok Adımlı)

**KURAL:** 4. sınıfta 3+ işlemli problemler tanıtılır.

| Zorluk | Format | Örnek |
|--------|--------|-------|
| 1 | Tek işlem | Ali 45 TL'den 18 TL harcadı. Kaç TL kaldı = ? |
| 2 | İki işlem | 3 paket aldı, her biri 12 TL. 50 TL verdi. Para üstü kaç = ? |
| 3 | Çarpma + toplama | 5 kutu x 8 kalem + 12 kalem = toplam kaç = ? |
| 4 | Bölme + karşılaştırma | 96 çikolata 8 çocuğa. Her birine kaç düşer = ? |
| 5 | Karışık (3+ işlem) | 250 TL ile 3 tane 45 TL'lik + 2 tane 30 TL'lik. Kalan = ? |

**KURAL:** Problem Türkçe, 9-10 yaş dili. Sonuç >= 0. Zaman, para, ölçü birimleri kullanılabilir.

---

## 8. İpucu Tasarım Kuralları

3. sınıf kuralları + ek:

**Çarpma (çok basamaklı):** "Birler ve onlar basamağını ayrı ayrı çarp, sonra topla"
**Bölme (iki basamağa):** "Çarpım tablosundan geriye düşün: b x ? = a"
**Kesir (gelişmiş):** "Sayıyı paydaya böl, sonucu pay ile çarp"
**Problem (çok adımlı):** "Problemi parçala: önce ilk işlemi yap, sonra ikincisini"

---

## 9-11. topics.json, stats.json, Rapor

3. sınıf agent'ıyla aynı format. Rapor başlığı: "4. Sınıf Matematik Raporu"

---

## 12. Çıktı Gereksinimleri

1. Geçerli JSON, UTF-8
2. TAM **50 soru**
3. `answer` DOĞRU hesaplanmış
4. Tekrar eden `text` yok
5. `id` 1-50 arası
6. `difficulty` 1-5
7. `answer` >= 0
8. `type` geçerli: `toplama`, `çıkarma`, `çarpma`, `bölme`, `sıralama`, `eksik_sayı`, `kesir`, `problem`
9. `hint` Türkçe, cevabı vermiyor
10. Çarpma sonucu 10000'i geçmez
11. Bölme tam bölünür (kalan = 0)
12. Kesir sonucu tam sayı
13. Problem metni Türkçe, günlük hayat
14. `educationPeriod` = "sinif_4"
15. `questionCount` = 50

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
  "summary": "Bu hafta toplam X soru çözüldü. İki basamaklı bölme ve çok adımlı problemlerde çok başarılı (%Y). Kesir konularında gelişim gösteriyor.",
  "strengths": [
    "İki basamaklı bölenle bölme işlemini adım adım uyguluyor",
    "Çok adımlı problemleri parçalara ayırarak çözebiliyor"
  ],
  "improvementAreas": [
    "Çok basamaklı çarpma işleminde onlar basamağı çarpımını unutabiliyor",
    "Kesir karşılaştırmada paydaları eşitlemede zorlanıyor"
  ],
  "recommendation": "Çok basamaklı çarpma pratiği için günlük 3-4 soru çözdürmek ve kesirleri somut materyallerle (pizza dilimi, çikolata parçası) göstermek faydalı olur.",
  "metrics": {
    "totalQuestionsSolved": 50,
    "averageAccuracy": 78.5,
    "byType": {
      "bölme": {"accuracy": 88, "trend": "stable"},
      "problem": {"accuracy": 82, "trend": "improving"},
      "kesir": {"accuracy": 70, "trend": "improving"}
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
