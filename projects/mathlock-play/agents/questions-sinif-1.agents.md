# MathLock AI - Adaptif Matematik Soru Motoru (1. Sınıf, 6-7 yaş)

## 1. Misyon

Bu dosya, 6-7 yaşında ilkokul **1. sınıfa** giden bir çocuk için **adaptif matematik soru seti** üreten AI modelinin çalışma kılavuzudur.

Çocuk telefonunda bir uygulama açmak istediğinde matematik sorusu çözer. Her **40** soruluk set tamamlandığında performans verisi (`stats.json`) VPS'e yüklenir. Bu dosyadaki algoritma sayesinde AI modeli yeni 40 soruyu çocuğun gelişim seviyesine göre üretir.

**Pedagojik temel:** Vygotsky'nin Yakınsal Gelişim Alanı. Hedef başarı oranı: **%65-80**

**ÖNEMLİ:** Bu dönemde **40 soru** üretilir. Çarpma ve bölme bu dönemde YOKTUR.

## 2. Çalışma Ortamı

- Dizin: `/home/akn/vps/projects/mathlock-play/`
- Veri dizini: `data/`
- Dokunulacak dosyalar: SADECE `data/questions.json` ve `data/topics.json`

## 3. Görev Adımları

`ai-generate.sh` tarafından çağrıldığında şu adımları SIRASI İLE uygula:

### Adım 1 - Veri Okuma
1. `data/stats.json` oku (yoksa "İlk Set" bölümüne git)
2. `data/questions.json` oku (mevcut versiyon numarasını al)
3. `data/topics.json` oku (mevcut konu anlatımlarını gör)

### Adım 2 - Analiz ve Karar
stats.json varsa 4. bölümdeki Adaptif Algoritmaya göre analiz et.
stats.json yoksa 5. bölümdeki İlk Set Algoritmaya göre üret.

### Adım 3 - 40 Soru Üret
6. bölümdeki şema ve kurallara göre `data/questions.json` dosyasına yaz.

### Adım 4 - Konu Anlatımlarını Güncelle
7. bölümdeki kurallara göre `data/topics.json` dosyasına yaz.

### Adım 5 - Rapor
11. bölümdeki formatta stdout'a rapor yazdır.

---

## 4. Adaptif Algoritma (Kalp)

### 4.1 Performans Analizi

| Kategori | Başarı | Süre | Anlam |
|----------|--------|------|-------|
| USTA | >= %85 | < 6sn | Çok iyi biliyor |
| GÜVENLİ | >= %85 | 6-12sn | Biliyor ama yavaş |
| GELİŞEN | %60-84 | herhangi | Öğrenme sürecinde |
| ZORLU | %40-59 | herhangi | Destek gerekli |
| KRİTİK | < %40 | herhangi | Temele dön |

### 4.2 İpucu ve Konu Kullanım Analizi

| Sinyal | Tespit | Aksiyon |
|--------|--------|---------|
| hintUsed / shown > %50 | İpucuna çok bakıyor | Zorluk ARTIRMA |
| topicUsed / shown > %30 | Konuyu açıyor | topics.json detaylandır |
| attempts > 2 oranı > %40 | Çok yanlış | Zorluk 1 seviye DÜŞ |
| avgTime > 18 saniye | Çok yavaş | Zorluk aynı, basit sayılar ver |
| avgTime < 3 saniye | Çok hızlı | Zorluk ARTIR |

### 4.3 Zorluk Karar Matrisi

```
EĞER başarı >= %85 VE süre < 6sn:
  yeni_zorluk = önceki_zorluk + 1  (maksimum 5)
EĞER başarı >= %85 VE süre >= 6sn:
  yeni_zorluk = önceki_zorluk
EĞER başarı %60-84:
  yeni_zorluk = önceki_zorluk
EĞER başarı %40-59:
  yeni_zorluk = önceki_zorluk - 1  (min 1)
EĞER başarı < %40:
  yeni_zorluk = MAKS(önceki_zorluk - 2, 1)
EĞER topicUsed / shown > %30:
  yeni_zorluk = MİN(yeni_zorluk, önceki_zorluk)
```

**Ek kural:** Zorluk ASLA bir seferde 2'den fazla artmaz.

### 4.4 Soru Dağıtım Algoritması

Her sette **40 soru**. Dağıtım:

**GRUP A - Pekiştirme (%40 = 16 soru):**
ZORLU ve KRİTİK tiplerden. Tek tipten max **7 soru**, KRİTİK tipten max **4 soru**.

**GRUP B - Gelişim (%35 = 14 soru):**
GELİŞEN tiplerden. Zorluk = mevcut.

**GRUP C - Meydan Okuma (%25 = 10 soru):**
USTA ve GÜVENLİ tiplerden. Zorluk = mevcut+1.

### 4.5 Yeni Tip Tanıtma Sırası

1. sınıf müfredatına göre:

```
Seviye 1: toplama + cikarma
Seviye 2: + siralama       (toplama ve çıkarmada başarı >= %75 ise)
Seviye 3: + eksik_sayi     (tümünde başarı >= %70 ise)
```

**ASLA yapılmayacaklar:**
- Çarpma ve bölme bu dönemde YASAK
- Bir sette 1'den fazla yeni tip tanıtma
- Toplama sonucu 20'yi geçme (eldesiz)
- Onluktan bozma gerektiren çıkarma YASAK

### 4.6 Soru Sıralama Algoritması

```
Pozisyon 1-3:   KOLAY (zorluk 1, en güvenli tip)
Pozisyon 4-8:   KOLAY-ORTA (GRUP A)
Pozisyon 9-18:  KARISIK (GRUP A + B)
Pozisyon 19-32: KARISIK (GRUP B + C)
Pozisyon 33-38: KARISIK (GRUP A + B + C)
Pozisyon 39-40: KOLAY (GRUP A, zorluk 1)
```

Aynı tipten arka arkaya **3'ten fazla** soru koyma.

---

## 5. İlk Set Algoritması

### Dağıtım:
- toplama: 18 soru (12x zorluk 1 + 6x zorluk 2)
- cikarma: 14 soru (10x zorluk 1 + 4x zorluk 2)
- siralama: 5 soru (5x zorluk 1)
- eksik_sayi: 3 soru (3x zorluk 1)

### difficultyProfile:
```json
{
  "overall": "beginner",
  "avgDifficulty": 1.2,
  "adjustmentReason": "İlk set - 1. sınıf, güvenli başlangıç"
}
```

---

## 6. questions.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-03-22T14:00:00Z",
  "generatedBy": "ai",
  "educationPeriod": "sinif_1",
  "questionCount": 40,
  "difficultyProfile": {
    "overall": "beginner | developing | intermediate | advanced",
    "avgDifficulty": 1.2,
    "adjustmentReason": "Türkçe, 1 cümle"
  },
  "questions": [...]
}
```

### Soru Alanları:

| Alan | Tip | Kural |
|------|-----|-------|
| id | int | 1-40 arası benzersiz |
| text | string | `= ?` ile biter |
| answer | int | >= 0 |
| type | string | toplama, cikarma, siralama, eksik_sayi |
| difficulty | int | 1-5 |
| hint | string | Türkçe, çocuk dili, cevabı vermez |

---

## 7. Soru Tipleri ve Zorluk Seviyeleri

### 7.1 Toplama (Eldesiz, 0-20)

| Zorluk | Format | Sayı Aralığı | Sonuç | Örnek |
|--------|--------|--------------|-------|-------|
| 1 | a + b = ? | a: 1-5, b: 1-5 | ≤ 10 | 3 + 4 = ? |
| 2 | a + b = ? | a: 1-9, b: 1-9 | ≤ 18 | 6 + 8 = ? |
| 3 | a + b = ? | a: 10-15, b: 1-5 | ≤ 20 | 12 + 5 = ? |
| 4 | a + b + c = ? | a: 1-5, b: 1-5, c: 1-3 | ≤ 13 | 3 + 4 + 2 = ? |
| 5 | a + b = ? | a: 10-19, b: 1-9 | ≤ 20 | 14 + 6 = ? |

**KURAL:** Toplama sonucu 20'yi GEÇEMEZ. Elde gerektiren toplama YASAK (birler toplanınca 10'u geçmez: 12+5 tamam, 12+9 YASAK çünkü 2+9=11).

### 7.2 Çıkarma (Onluktan Bozmasız, 0-20)

| Zorluk | Format | Sayı Aralığı | Sonuç | Örnek |
|--------|--------|--------------|-------|-------|
| 1 | a - b = ? | a: 2-5, b: 1-2 | ≥ 1 | 4 - 2 = ? |
| 2 | a - b = ? | a: 5-10, b: 1-4 | ≥ 1 | 8 - 3 = ? |
| 3 | a - b = ? | a: 10-15, b: 1-5 | ≥ 1 | 13 - 4 = ? |
| 4 | a - b = ? | a: 10-20, b: 1-9 | ≥ 1 | 17 - 6 = ? |
| 5 | a - b = ? | a: 15-20, b: 5-9 | ≥ 1 | 18 - 7 = ? |

**KURAL:** Onluktan bozma gerektiren çıkarma YASAK (15-8 YASAK çünkü 5 < 8). Sonuç HER ZAMAN >= 0.

### 7.3 Sıralama

| Zorluk | Format | Sayı Aralığı | Örnek |
|--------|--------|--------------|-------|
| 1 | Hangisi büyük: A, B | 1-20 | Hangisi büyük: 7, 12 |
| 2 | En küçüğü hangisi: A, B, C | 1-30 | En küçüğü hangisi: 15, 8, 22 |
| 3 | En büyüğü hangisi: A, B, C | 1-50 | En büyüğü hangisi: 31, 12, 45 |
| 4 | 4 sayı, en küçüğünü yaz | 1-50 | En küçüğü hangisi: 23, 8, 41, 15 |
| 5 | A ile B arasında kaç sayı var | 1-50 | 15 ile 20 arasında kaç sayı var? |

### 7.4 Eksik Sayı

| Zorluk | Format | Sayı Aralığı | Örnek |
|--------|--------|--------------|-------|
| 1 | ? + a = b | a: 1-3, b: 3-7 | ? + 3 = 7 |
| 2 | a + ? = b | a: 1-5, b: 5-10 | 3 + ? = 8 |
| 3 | ? - a = b | a: 1-3, b: 1-5 | ? - 3 = 4 |
| 4 | ? + a = b | a: 3-8, b: 8-15 | ? + 5 = 12 |
| 5 | a + ? = b | a: 5-10, b: 10-20 | 8 + ? = 15 |

**KURAL:** Çarpma ve bölme içeren eksik sayı YASAK.

---

## 8. İpucu Tasarım Kuralları

### 8.1 İlkeler
1. Cevabı ASLA verme
2. Somut nesnelerle anlatım (parmak, elma, top)
3. Türkçe, kısa, 6-7 yaş dili
4. 10-40 karakter arası

### 8.2 Tip Bazlı Şablonlar

**Toplama:** "Büyük sayıdan başla, küçüğü parmakla say"
**Çıkarma:** "Büyük sayıdan geriye doğru say"
**Sıralama:** "Sayıları kafanda sırala, en küçüğünü bul"
**Eksik Sayı:** "Sonuçtan bilinen sayıyı çıkar"

---

## 9. topics.json Şeması

2. sınıf formatıyla aynı. 1. sınıfa uygun dil ve örnekler kullan.

---

## 10. stats.json Şeması (Sadece Okunur)

2. sınıf agent'ıyla aynı format. `totalShown` = 40.

---

## 11. Rapor Formatı

```
MathLock AI - 1. Sınıf Matematik Raporu
========================================
Önceki set: v{eski} | Başarı: %{oran} | Süre: {gün} gün
Güçlü: {tipler}
Zayıf: {tipler}
Zorluk: {eski_ort:.1f} => {yeni_ort:.1f}
Yeni tanıtılan: {varsa tip adı, yoksa "-"}
Konu güncellendi: {tipler veya "-"}
Yeni set: v{yeni} | 40 soru | {kısa dağılım}
```

---

## 12. Çıktı Gereksinimleri

1. Geçerli JSON, UTF-8
2. TAM **40 soru**
3. `answer` DOĞRU hesaplanmış
4. Tekrar eden `text` yok
5. `id` alanları 1-40 arası
6. `difficulty` 1-5 arası
7. `answer` >= 0
8. `type` geçerli: toplama, cikarma, siralama, eksik_sayi
9. `hint` Türkçe, cevabı vermiyor
10. Toplama sonucu 20'yi geçmez (eldesiz)
11. Çıkarma onluktan bozmasız
12. Çarpma ve bölme YASAK
13. `educationPeriod` = "sinif_1"
14. `questionCount` = 40

## 13. Benzersizlik Garantisi

40 sorunun HER BİRİ farklı bir `text` değerine sahip olmalı.


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
  "summary": "Bu hafta toplam X soru çözüldü. Toplama ve çıkarma konularında çok başarılı (%Y). Z konusunda gelişim gösteriyor.",
  "strengths": [
    "Toplama işlemlerinde çok hızlı ve doğru",
    "İpucu kullanma oranı düşük — özgüveni yüksek"
  ],
  "improvementAreas": [
    "Bölme işlemlerinde zorlanıyor",
    "3. zorluk seviyesinde süre artıyor"
  ],
  "recommendation": "Bölme konusunda somut örneklerle pratik yapması önerilir.",
  "metrics": {
    "totalQuestionsSolved": 50,
    "averageAccuracy": 78.5,
    "byType": {
      "toplama": {"accuracy": 92, "trend": "stable"},
      "cikarma": {"accuracy": 85, "trend": "improving"}
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
