# MathLock AI - Adaptif Matematik Soru Motoru (Okul Öncesi, 5-6 yaş)

## 1. Misyon

Bu dosya, 5-6 yaşında **okul öncesi** dönemde bir çocuk için **adaptif matematik soru seti** üreten AI modelinin çalışma kılavuzudur.

Çocuk telefonunda bir uygulama açmak istediğinde matematik sorusu çözer. Her **30** soruluk set tamamlandığında performans verisi (`stats.json`) VPS'e yüklenir. Bu dosyadaki algoritma sayesinde AI modeli yeni 30 soruyu çocuğun gelişim seviyesine göre üretir.

**Pedagojik temel:** Vygotsky'nin Yakınsal Gelişim Alanı (Zone of Proximal Development). Çocuğa ne çok kolay ne çok zor sorular verilir.

**ÖNEMLİ:** Bu dönemde dikkat süresi kısa olduğundan 50 değil **30 soru** üretilir.

Hedef başarı oranı: **%70-85** (okul öncesi için daha yüksek — güven inşası öncelikli)

## 2. Çalışma Ortamı

- Dizin: `/home/akn/vps/projects/mathlock-play/`
- Veri dizini: `data/`
- Dokunulacak dosyalar: SADECE `data/questions.json` ve `data/topics.json`
- Dokunulmayacak dosyalar: Diğerleri

## 3. Görev Adımları

`ai-generate.sh` tarafından çağrıldığında şu adımları SIRASI İLE uygula:

### Adım 1 - Veri Okuma
1. `data/stats.json` oku (yoksa Adım 2'nin "İlk Set" bölümüne git)
2. `data/questions.json` oku (mevcut versiyon numarasını al)
3. `data/topics.json` oku (mevcut konu anlatımlarını gör)

### Adım 2 - Analiz ve Karar
stats.json varsa 4. bölümdeki Adaptif Algoritmaya göre analiz et.
stats.json yoksa 5. bölümdeki İlk Set Algoritmaya göre üret.

### Adım 3 - 30 Soru Üret
6. bölümdeki şema ve kurallara göre `data/questions.json` dosyasına yaz (üzerine yaz).

### Adım 4 - Konu Anlatımlarını Güncelle
7. bölümdeki kurallara göre `data/topics.json` dosyasına yaz.

### Adım 5 - Rapor
11. bölümdeki formatta stdout'a kısa rapor yazdır.

---

## 4. Adaptif Algoritma (Kalp)

### 4.1 Performans Analizi

stats.json'daki `byType` verisinden her soru tipi için:

```
başarı_oranı = byType[tip].correct / byType[tip].shown * 100
ort_süre_sn = byType[tip].avgTime değerini float'a çevir
```

Her soru tipini şu kategorilere ayır:

| Kategori | Başarı | Süre | Anlam |
|----------|--------|------|-------|
| USTA | >= %90 | < 8sn | Çocuk bu tipi çok iyi biliyor |
| GÜVENLİ | >= %85 | 8-15sn | Biliyor ama yavaş |
| GELİŞEN | %65-84 | herhangi | Öğrenme sürecinde, ideal bölge |
| ZORLU | %45-64 | herhangi | Zorlanıyorsa, destek gerekli |
| KRİTİK | < %45 | herhangi | Anlamamış, temele dön |

**NOT:** Okul öncesi için süre limitleri daha geniş (8sn vs 5sn) ve başarı eşikleri daha yüksek — bu yaşta hızdan çok DOĞRULUK önemli.

### 4.2 İpucu ve Konu Kullanım Analizi

stats.json'daki `byType` ve `details` verilerinden analiz yap:

| Sinyal | Tespit | Aksiyon |
|--------|--------|---------|
| byType[tip].hintUsed / shown > %50 | Çocuk ipucuna çok bakıyor | O tipte zorlanıyordur, zorluk ARTIRMA |
| byType[tip].topicUsed / shown > %30 | Konu anlatımını açıyor | Konuyu anlamamış, topics.json detaylandır |
| details'te attempts > 2 oranı > %40 | Çok fazla yanlış deniyor | Zorluk 1 seviye DÜŞ |
| byType[tip].avgTime > 20 saniye | Çok yavaş | Zorluk aynı kalsın ama çok basit sayılar ver |
| byType[tip].avgTime < 4 saniye | Çok hızlı | Zorluk ARTIR |

### 4.3 Zorluk Karar Matrisi

**KURAL:** Okul öncesinde zorluk ASLA bir seferde 1'den fazla artmaz veya düşmez.

```
EĞER başarı >= %90 VE süre < 8sn:
  yeni_zorluk = önceki_zorluk + 1  (maksimum 5)
EĞER başarı >= %85 VE süre >= 8sn:
  yeni_zorluk = önceki_zorluk      (hızlanmayı bekle)
EĞER başarı %65-84:
  yeni_zorluk = önceki_zorluk      (ideal bölge, değiştirme)
EĞER başarı %45-64:
  yeni_zorluk = önceki_zorluk - 1  (min 1)
EĞER başarı < %45:
  yeni_zorluk = MAKS(önceki_zorluk - 1, 1)  (yumuşak düşüş — okul öncesi)
EĞER byType[tip].topicUsed / shown > %30:
  yeni_zorluk = MİN(yeni_zorluk, önceki_zorluk)
```

### 4.4 Soru Dağıtım Algoritması

Her sette **30 soru** üretilir. Dağıtım 3 gruba ayrılır:

**GRUP A - Pekiştirme (%45 = 13-14 soru):**
ZORLU ve KRİTİK tiplerden. Zorluk = mevcut veya mevcut-1.
Okul öncesinde pekiştirme oranı daha yüksek — güven inşası öncelikli.

**GRUP A sınırlamaları:**
- Tek tipten en fazla **6 soru**
- KRİTİK tipten en fazla **4 soru**
- Kalan boş kontenjan: USTA/GÜVENLİ tiplerden kolay sorularla doldur

**GRUP B - Gelişim (%35 = 10-11 soru):**
GELİŞEN tiplerden. Zorluk = mevcut.

**GRUP C - Meydan Okuma (%20 = 6 soru):**
USTA ve GÜVENLİ tiplerden. Zorluk = mevcut+1.
Okul öncesinde meydan okuma oranı düşük tutulur.

### 4.5 Yeni Tip Tanıtma Sırası

Okul öncesi müfredatına göre kademeli tanıtım:

```
Seviye 1: sayma + toplama
Seviye 2: + çıkarma      (toplama başarısı >= %80 ise)
Seviye 3: + karşılaştırma (toplama ve çıkarmada başarı >= %75 ise)
Seviye 4: + örüntü       (tümünde başarı >= %75 ise)
```

**ASLA yapılmayacaklar:**
- Çarpma ve bölme bu dönemde YASAK
- Bir sette 1'den fazla yeni tip tanıtma
- Negatif sayılar YASAK
- 20'den büyük sayılar (sadece sayma hariç) YASAK

### 4.6 Soru Sıralama Algoritması

```
Pozisyon 1-3:   ÇOOK KOLAY (zorluk 1, en basit tip)
                → "Ben yapabiliyorum!" hissi
Pozisyon 4-8:   KOLAY (GRUP A)
Pozisyon 9-15:  KOLAY-ORTA (GRUP A + B)
Pozisyon 16-25: KARIŞIK (GRUP B + C)
Pozisyon 26-28: ORTA (GRUP B)
Pozisyon 29-30: KOLAY (GRUP A, zorluk 1)
                → "Bitirdim, başarılıyım!" hissi
```

**Aynı tipten arka arkaya 2'den fazla soru koyma.** (50 soruluk setlerde 3 idi, 30'da 2)

---

## 5. İlk Set Algoritması (stats.json olmadığı zaman)

### Dağıtım:
- sayma: 8 soru (8x zorluk 1 — kaç tane var, say)
- toplama: 12 soru (8x zorluk 1 + 4x zorluk 2)
- çıkarma: 6 soru (6x zorluk 1)
- karşılaştırma: 3 soru (3x zorluk 1)
- örüntü: 1 soru (1x zorluk 1)

### Sıralama:
- Pozisyon 1-3: En kolay sayma (kaç elma var: 🍎🍎🍎 = ?)
- Pozisyon 4-5: En kolay toplama (1 + 1 = ?, 1 + 2 = ?)
- Pozisyon 6-28: Karışık ama tip tekrarı arka arkaya 2'yi geçmesin
- Pozisyon 29-30: Kolay toplama (zorluk 1)

### difficultyProfile:
```json
{
  "overall": "beginner",
  "avgDifficulty": 1.1,
  "adjustmentReason": "İlk set - okul öncesi, güvenli başlangıç"
}
```

---

## 6. questions.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-03-22T14:00:00Z",
  "generatedBy": "ai",
  "educationPeriod": "okul_oncesi",
  "questionCount": 30,
  "difficultyProfile": {
    "overall": "beginner | developing | intermediate | advanced",
    "avgDifficulty": 1.1,
    "adjustmentReason": "Türkçe, 1 cümle"
  },
  "questions": [
    {
      "id": 1,
      "text": "1 + 2 = ?",
      "answer": 3,
      "type": "toplama",
      "difficulty": 1,
      "hint": "1'den başla, 2 parmak say: 2, 3!"
    }
  ]
}
```

### Soru Alanları:

| Alan | Tip | Kural |
|------|-----|-------|
| id | int | 1-30 arası benzersiz sıra numarası |
| text | string | Soru metni. İşlem tipleri için `= ?` ile biter. Sayma/örüntü tipleri için soru formatında doğrudan yazılır. |
| answer | int | Doğru cevap. Her zaman >= 0 |
| type | string | Geçerli: `sayma`, `toplama`, `çıkarma`, `karşılaştırma`, `örüntü` |
| difficulty | int | 1-5 arası |
| hint | string | Türkçe, çocuk dili, cevabı VERMEZ, emoji kullan |

### Operatör Sembolleri:
- Toplama: `+`
- Çıkarma: `-`
- Eşittir: `=`
- Bilinmeyen sayı: `?`

---

## 7. Soru Tipleri ve Zorluk Seviyeleri

### 7.1 Sayma

| Zorluk | Format | Aralık | Örnek |
|--------|--------|--------|-------|
| 1 | Kaç tane var: 🍎🍎🍎 = ? | 1-5 nesne | Kaç tane elma var: 🍎🍎🍎 = ? |
| 2 | Kaç tane var: ⭐⭐⭐⭐⭐⭐ = ? | 1-10 nesne | Kaç tane yıldız var: ⭐⭐⭐⭐⭐⭐ = ? |
| 3 | Eksik sayıyı bul: 1, 2, ?, 4, 5 = ? | 1-15 | 1, 2, ?, 4, 5 = ? |
| 4 | 2'şer say: 2, 4, 6, ? = ? | 2-20 | 2, 4, 6, ? = ? |
| 5 | Geriye say: 10, 9, 8, ? = ? | 1-20 | 10, 9, 8, ? = ? |

**KURAL:** Sayma sorularında `text` alanında emoji kullan. `answer` sayısal değer.

### 7.2 Toplama

| Zorluk | Format | Sayı Aralığı | Sonuç | Örnek |
|--------|--------|--------------|-------|-------|
| 1 | a + b = ? | a: 1-3, b: 1-2 | ≤ 5 | 2 + 1 = ? |
| 2 | a + b = ? | a: 1-5, b: 1-3 | ≤ 7 | 3 + 4 = ? |
| 3 | a + b = ? | a: 1-5, b: 1-5 | ≤ 10 | 4 + 5 = ? |
| 4 | a + b = ? | a: 3-7, b: 1-3 | ≤ 10 | 6 + 3 = ? |
| 5 | a + b = ? | a: 5-9, b: 1-5 | ≤ 10 | 7 + 3 = ? |

**KURAL:** Toplama sonucu 10'u ASLA geçmez.

### 7.3 Çıkarma

| Zorluk | Format | Sayı Aralığı | Sonuç | Örnek |
|--------|--------|--------------|-------|-------|
| 1 | a - b = ? | a: 2-5, b: 1 | ≥ 1 | 3 - 1 = ? |
| 2 | a - b = ? | a: 3-7, b: 1-2 | ≥ 1 | 5 - 2 = ? |
| 3 | a - b = ? | a: 5-10, b: 1-3 | ≥ 1 | 8 - 3 = ? |
| 4 | a - b = ? | a: 5-10, b: 2-4 | ≥ 1 | 7 - 4 = ? |
| 5 | a - b = ? | a: 7-10, b: 3-5 | ≥ 1 | 10 - 5 = ? |

**KURAL:** Sonuç HER ZAMAN >= 1 (0 ve negatif YASAK).

### 7.4 Karşılaştırma

| Zorluk | Format | Sayı Aralığı | Örnek |
|--------|--------|--------------|-------|
| 1 | Hangisi büyük: A, B = ? | 1-5, fark belirgin | Hangisi büyük: 2, 5 = ? |
| 2 | Hangisi büyük: A, B = ? | 1-10 | Hangisi büyük: 7, 4 = ? |
| 3 | Hangisi küçük: A, B = ? | 1-10 | Hangisi küçük: 8, 3 = ? |
| 4 | En büyüğü hangisi: A, B, C = ? | 1-10 | En büyüğü hangisi: 3, 7, 5 = ? |
| 5 | En küçüğü hangisi: A, B, C = ? | 1-15 | En küçüğü hangisi: 9, 2, 11 = ? |

**KURAL:** `answer` = doğru cevap sayısal değer.

### 7.5 Örüntü

| Zorluk | Format | Örnek |
|--------|--------|-------|
| 1 | AB: 1, 2, 1, 2, ? = ? | 1, 2, 1, 2, ? = ? → answer: 1 |
| 2 | ABB: 1, 2, 2, 1, 2, 2, ? = ? | answer: 1 |
| 3 | ABC: 1, 2, 3, 1, 2, 3, ? = ? | answer: 1 |
| 4 | +2 artan: 2, 4, 6, ? = ? | answer: 8 |
| 5 | +2 artan: 1, 3, 5, 7, ? = ? | answer: 9 |

---

## 8. İpucu (hint) Tasarım Kuralları

### 8.1 İlkeler
1. Cevabı ASLA verme
2. Somut nesneler kullan (parmak, elma, top, yıldız)
3. Emoji ile destekle
4. 5-6 yaş dili — çok basit, kısa
5. Her ipucu 10-35 karakter arası

### 8.2 Tip Bazlı Şablonlar

**Sayma:**
- "Parmaklarınla tek tek say 🖐️"
- "Bir bir göster ve say"

**Toplama:**
- "Büyük sayıdan başla, küçüğü parmakla say"
- "🍎 elmalarını birleştir ve say"

**Çıkarma:**
- "Büyük sayıdan geriye say ⬇️"
- "Elmaları say, bazılarını al, kaç kaldı?"

**Karşılaştırma:**
- "Hangi sayı daha çok? 🤔"
- "Parmaklarınla karşılaştır"

**Örüntü:**
- "Tekrar eden parçayı bul 🔄"
- "Sıra neyle devam ediyor?"

---

## 9. topics.json Şeması

```json
{
  "sayma": {
    "title": "🔢 Sayma Nasıl Yapılır?",
    "explanation": "Nesneleri tek tek göster ve say. Her nesneye bir sayı söyle.",
    "example": "🍎 bir, 🍎🍎 iki, 🍎🍎🍎 üç! 3 tane elma var!",
    "tips": ["Parmaklarını kullan 🖐️", "Her nesneyi bir kere say", "Yavaş yavaş say"]
  },
  "toplama": {
    "title": "➕ Toplama Nasıl Yapılır?",
    "explanation": "İki grubu birleştir ve hepsini say.",
    "example": "🍎🍎 + 🍎 = 🍎🍎🍎 → 2 + 1 = 3!",
    "tips": ["Büyük sayıdan başla", "Parmaklarınla say", "Birleştirip say"]
  }
}
```

---

## 10. stats.json Şeması (Sadece Okunur)

2. sınıf agent'ıyla aynı format. Tek fark: `totalShown` = 30.

---

## 11. Rapor Formatı

```
MathLock AI - Okul Öncesi Matematik Raporu
========================================
Önceki set: v{eski} | Başarı: %{oran} | Süre: {gün} gün
Güçlü: {tipler}
Zayıf: {tipler}
Zorluk: {eski_ort:.1f} => {yeni_ort:.1f}
Yeni tanıtılan: {varsa tip adı, yoksa "-"}
Konu güncellendi: {tipler veya "-"}
Yeni set: v{yeni} | 30 soru | {kısa dağılım}
```

---

## 12. Çıktı Gereksinimleri (Kontrol Listesi)

1. Geçerli JSON, trailing comma yok, UTF-8
2. TAM **30 soru** (ne eksik ne fazla)
3. Her sorunun `answer` alanı DOĞRU hesaplanmış
4. Tekrar eden `text` yok (30 benzersiz soru)
5. `id` alanları 1-30 arası sıralı
6. `difficulty` alanları 1-5 arası
7. `answer` alanları hep >= 0
8. `type` alanları geçerli 5 tipten biri: `sayma`, `toplama`, `çıkarma`, `karşılaştırma`, `örüntü`
9. `hint` alanları boş değil, Türkçe, cevabı vermiyor, emoji içerir
10. Toplama sonucu 10'u geçmez
11. Çıkarma sonucu 0'dan küçük olmaz
12. Çarpma ve bölme YASAK
13. `educationPeriod` = "okul_oncesi"
14. `questionCount` = 30

## 13. Benzersizlik Garantisi

30 sorunun HER BİRİ farklı bir `text` değerine sahip olmalı.


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
  "summary": "Bu hafta toplam X soru çözüldü. Sayma ve toplama konularında çok başarılı (%Y). Yeni konularda gelişim gösteriyor.",
  "strengths": [
    "Sayma işlemlerinde çok hızlı ve doğru",
    "Toplamada somut nesneleri hayal ederek çözüyor"
  ],
  "improvementAreas": [
    "Çıkarma işlemlerinde parmak kullanarak sayıyor",
    "Yeni örüntülerde bazen takılıyor"
  ],
  "recommendation": "Evde 5-10 arası nesneleri (oyuncak, fındık) sayarak ve gruplara ayırarak pratik yapması önerilir.",
  "metrics": {
    "totalQuestionsSolved": 30,
    "averageAccuracy": 78.5,
    "byType": {
      "sayma": {"accuracy": 92, "trend": "stable"},
      "toplama": {"accuracy": 85, "trend": "improving"}
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
