# MathLock AI - Adaptif Matematik Soru Motoru

## 1. Misyon

Bu dosya, 7-8 yaşında ilkokul 2. sınıfa giden bir çocuk için **adaptif matematik soru seti** üreten AI modelinin çalışma kılavuzudur.

Çocuk telefonunda bir uygulama açmak istediğinde matematik sorusu çözer. Her 50 soruluk set tamamlandığında performans verisi (`stats.json`) VPS'e yüklenir. Bu dosyadaki algoritma sayesinde AI modeli yeni 50 soruyu çocuğun gelişim seviyesine göre üretir.

**Pedagojik temel:** Vygotsky'nin Yakınsal Gelişim Alanı (Zone of Proximal Development). Çocuğa ne çok kolay ne çok zor sorular verilir. Her soru setinde çocuğun "biraz zorlansa da başarabileceği" seviyeyi hedefleriz.

Hedef başarı oranı: **%65-80** (bu aralık maksimum öğrenme sağlar)

## 2. Çalışma Ortamı

- Dizin: `/home/akn/vps/projects/mathlock/`
- Veri dizini: `data/`
- Dokunulacak dosyalar: SADECE `data/questions.json` ve `data/topics.json`
- Dokunulmayacak dosyalar: Diğerleri (Android kodu, deploy.sh, AGENTS.md, validate-questions.py vb.)

## 3. Görev Adımları

`ai-generate.sh` tarafından çağrıldığında şu adımları SIRASI İLE uygula:

### Adım 1 - Veri Okuma
1. `data/stats.json` oku (yoksa Adım 2'nin "İlk Set" bölümüne git)
2. `data/questions.json` oku (mevcut versiyon numarasını al)
3. `data/topics.json` oku (mevcut konu anlatımlarını gör)

### Adım 2 - Analiz ve Karar
stats.json varsa 4. bölümdeki Adaptif Algoritmaya göre analiz et.
stats.json yoksa 5. bölümdeki İlk Set Algoritmaya göre üret.

### Adım 3 - 50 Soru Üret
6. bölümdeki şema ve kurallara göre `data/questions.json` dosyasına yaz (üzerine yaz).

### Adım 4 - Konu Anlatımlarını Güncelle
7. bölümdeki kurallara göre `data/topics.json` dosyasına yaz.

### Adım 5 - Rapor
11. bölümdeki formatta stdout'a kısa rapor yazdır.

---

## 4. Adaptif Algoritma (Kalp)

Bu bölüm AGENTS.md'nin kalbidir. AI modeli bu kuralları **birebir** takip etmelidir.

### 4.1 Performans Analizi

stats.json'daki `byType` verisinden her soru tipi için:

```
başarı_oranı = byType[tip].correct / byType[tip].shown * 100
ort_süre_sn = byType[tip].avgTime değerini float'a çevir (virgül varsa noktaya çevir)
```

Her soru tipini şu kategorilere ayır:

| Kategori | Başarı | Süre | Anlam |
|----------|--------|------|-------|
| USTA | >= %85 | < 5sn | Çocuk bu tipi çok iyi biliyor |
| GÜVENLİ | >= %85 | 5-10sn | Biliyor ama hızlanmadı |
| GELİŞEN | %60-84 | herhangi | Öğrenme sürecinde, ideal bölge |
| ZORLU | %40-59 | herhangi | Zorlanıyorsa, destek gerekli |
| KRİTİK | < %40 | herhangi | Anlamamış, temele dön |

### 4.2 Ipucu ve Konu Kullanim Analizi

stats.json'daki `byType` ve `details` verilerinden analiz yap:

| Sinyal | Tespit | Aksiyon |
|--------|--------|---------|
| byType[tip].hintUsed / shown > %50 | Çocuk ipucuna çok bakıyor | O tipte zorlanıyordur, zorluk ARTIRMA |
| byType[tip].topicUsed / shown > %30 | Konu anlatımını açıyor | Konuyu anlamamış, topics.json detaylandır |
| details'te attempts > 2 oranı > %40 | Çok fazla yanlış deniyor | Zorluk 1 seviye DÜŞ |
| byType[tip].avgTime > 15 saniye | Çok yavaş cevaplayarak düşünüyor | Zorluk aynı kalsın ama basit sayılar ver |
| byType[tip].avgTime < 3 saniye | Çok hızlı, düşünmeden yapıyor | Zorluk ARTIR, büyük sayılara geç |

### 4.3 Zorluk Karar Matrisi

Her soru tipi için önceki setteki zorluk seviyesini ve performansı birleştir.

**önceki_zorluk hesaplama:** Önceki questions.json'da o tip için en SIK kullanılan zorluk seviyesi (mode). Eşitlik varsa yüksek olanı al.

**Minimum örneklem kuralı:** Bir tipte shown < 3 ise o tipin kategorisi güvenilir şekilde belirlenemez. önceki_zorluk seviyesinde kal, değiştirme.

```
EĞER başarı >= %85 VE süre < 5sn:
  yeni_zorluk = önceki_zorluk + 1  (maksimum 5)
EĞER başarı >= %85 VE süre >= 5sn:
  yeni_zorluk = önceki_zorluk      (hızlanmayı bekle)
EĞER başarı %60-84:
  yeni_zorluk = önceki_zorluk      (ideal bölge, değiştirme)
EĞER başarı %40-59:
  yeni_zorluk = önceki_zorluk - 1  (min 1)
EĞER başarı < %40:
  yeni_zorluk = MAKS(önceki_zorluk - 2, 1)  (sert düşüş ama temele ATLAMAZ)
EĞER byType[tip].topicUsed / shown > %30:
  yeni_zorluk = MİN(yeni_zorluk, önceki_zorluk)  (asla artırma)
```

**Ek kural:** Zorluk ASLA bir seferde 2'den fazla artmaz. Örneğin zorluk 1'den 3'e atlanamaz.

**Ani düşüş koruması:** Eğer bir tipin başarısı önceki sete göre %30'dan fazla düştüyse (örneğin %80 → %40), bu "kötü gün" olabilir. Zorluk en fazla 2 seviye düşürülür ve adjustmentReason'a "ani düşüş — kötü gün olabilir" notu eklenir.

### 4.4 Soru Dagitim Algoritmasi

Her sette **50 soru** üretilir. Dağıtım 3 gruba ayrılır:

**GRUP A - Pekiştirme (%40 = 20 soru):**
ZORLU ve KRİTİK olan tiplerden. Zorluk = mevcut veya mevcut-1.
Amaç: Çocuğun başarılı olması, güveni gelmesi.

**GRUP A sınırlamaları:**
- Tek bir tipten en fazla **8 soru** (çok tekrar sıkıcı ve yorucu)
- KRİTİK (başarı < %40) tipten en fazla **5 soru** — çocuk zaten anlamamış, sel gibi soru morali bozar
- Kalan boş kontenjan: çocuğun GÜVENLİ veya USTA olduğu tiplerden **kolay (zorluk 1-2) sorularla** doldur → güven inşası
- GRUP A için yeterli ZORLU/KRİTİK tip yoksa: eksik soruları en düşük başarılı GELİŞEN tiplerden al

**GRUP B - Gelişim (%35 = 17-18 soru):**
GELİŞEN olan tiplerden. Zorluk = mevcut.
Amaç: Öğrenme devam etsin, bu bölgede kalsın.

**GRUP C - Meydan Okuma (%25 = 12-13 soru):**
USTA ve GÜVENLİ olan tiplerden. Zorluk = mevcut+1 (veya farklı formatta sorular).
Amaç: Sıkıcı olmasın, ilerlesin.

**GRUP C boş kalırsa (USTA/GÜVENLİ tip yok):**
En iyi performanslı GELİŞEN tiplerden mevcut_zorluk+1 ile doldur. Çocuğun en güçlü alanı biraz daha ittirmek anlamına gelir.

**Eğer tüm tipler aynı kategorideyse:**
- Hepsi USTA: Zorluk artır veya yeni tip tanıt (4.5'e bak)
- Hepsi KRİTİK: Tüm sorular zorluk 1, cesaret verici basit sorular (tip başına max 10)

### 4.5 Yeni Tip Tanitma Sirasi

2. sinif mufredatina gore kademeli tanitim. Yeni tip eklemek icin **tum mevcut tiplerde** ortalama basarinin >= %70 olmasi gerekir.

```
Seviye 1: toplama + cikarma
Seviye 2: + carpma        (toplama ve cikarmada basari >= %75 ise)
Seviye 3: + bolme         (carpmada basari >= %70 ise)
Seviye 4: + siralama      (dort islemde basari >= %70 ise)
Seviye 5: + eksik_sayi    (tumunde basari >= %70 ise)
```

Yeni tanitilan tip:
- Her zaman zorluk **1** ile baslar
- O tipten en az **3 soru** verilir (en fazla 5)
- Ilk 3 sorusu setin ilk yarisindan sonra yerlestirilir (cocuk isindiktan sonra)
- topics.json'da o tipin aciklamasi mutlaka eklenir

**ASLA yapilmayacaklar:**
- Cocugun hic gormedigi tipi zorluk 2+ ile tanitma
- Bir sette 2'den fazla yeni tip tanitma
- stats.json'da o tip yokken zorluk 3+ ile verme

**Tip tutma kurali:** Ilk sette (v1) tanitilan tum 6 tip sonraki setlerde de korunur. Bir tip ASLA setten cikarilmaz. KRITIK tipteki soru sayisi azaltilabilir (min 2 soru) ama tip tamamen kaldirilamaz.

### 4.6 Soru Siralama Algoritmasi (Psikolojik Tasarim)

Soruların sirasi cocugun motivasyonunu dogrudan etkiler:

```
Pozisyon 1-3:   KOLAY sorular (cocugun guvenlendigi tip, zorluk 1)
                → "Ben yapabiliyorum" hissi
Pozisyon 4-8:   KOLAY-ORTA karisik (GRUP A'dan)
                → Isindi, basarili devam ediyor
Pozisyon 9-20:  KARISIK (GRUP A + B)
                → Asil ogrenme bolgesi
Pozisyon 21-35: KARISIK (GRUP B + C)
                → Zorlaniyor ama cope with ediyor
Pozisyon 36-45: KARISIK (GRUP A + B + C)
                → Cesitlilik, sikilmasin
Pozisyon 46-48: ORTA zorluk (GRUP B'den)
                → Bilistirin, son hamle
Pozisyon 49-50: KOLAY sorular (GRUP A'dan, zorluk 1-2)
                → "Bitirdim, basariliyim!" hissi
```

**Onemli:** Ayni tipten arka arkaya 3'ten fazla soru koyma. Cesitlilik motivasyonu arttirir.

---

## 5. Ilk Set Algoritmasi (stats.json olmadigi zaman)

stats.json yoksa cocugun seviyesini bilmiyoruz. Guvenli bir baslangic:

**Not:** Ilk set tum 6 tipi tanistirir (§4.5'teki kademeli tanitim sirasi v2+ icin gecerlidir). Ilk setten sonra tipler ASLA cikarilmaz, sadece soru sayilari ve zorluk seviyeleri ayarlanir.

### Dagitim:
- toplama: 22 soru (12x zorluk 1 + 10x zorluk 2)
- cikarma: 16 soru (9x zorluk 1 + 7x zorluk 2)
- carpma: 5 soru (5x zorluk 1, sadece x2 tablosu — 1x2, 2x2, 3x2, 4x2, 5x2)
- bolme: 4 soru (4x zorluk 1, sadece /2 — 2/2, 4/2, 6/2, 8/2)
- siralama: 2 soru (2x zorluk 1)
- eksik_sayi: 1 soru (1x zorluk 1)

### Siralama:
- Pozisyon 1-3: En kolay toplama (3+2, 4+1 gibi)
- Pozisyon 4-5: Kolay cikarma (5-2, 7-3 gibi)
- Pozisyon 6-8: Kolay toplama (2+3, 6+1 gibi)
- Pozisyon 9-10: Kolay cikarma (8-3, 9-4 gibi)
- Pozisyon 11-48: Kalan sorular karisik ama tip tekrari arka arkaya 3'u gecmesin
- Pozisyon 49-50: Kolay toplama (zorluk 1)

### difficultyProfile:
```json
{
  "overall": "beginner",
  "avgDifficulty": 1.3,
  "adjustmentReason": "Ilk set - cocugun seviyesi henuz bilinmiyor, guvenli baslangic"
}
```

### version:
- Eger mevcut questions.json varsa: version = mevcut + 1
- Eger yoksa: version = 1

---

## 6. questions.json Semasi

```json
{
  "version": 1,
  "generatedAt": "2026-03-22T14:00:00Z",
  "generatedBy": "ai",
  "difficultyProfile": {
    "overall": "beginner | developing | intermediate | advanced",
    "avgDifficulty": 1.3,
    "adjustmentReason": "Türkçe, 1 cümle, neden bu zorluk seçildi"
  },
  "questions": [
    {
      "id": 1,
      "text": "3 + 4 = ?",
      "answer": 7,
      "type": "toplama",
      "difficulty": 1,
      "hint": "3'ten başla, parmaklarınla 4 tane say"
    }
  ]
}
```

### overall Değerleri:
- `beginner`: ortalama zorluk 1.0-1.5
- `developing`: ortalama zorluk 1.5-2.5
- `intermediate`: ortalama zorluk 2.5-3.5
- `advanced`: ortalama zorluk 3.5+

### Soru Alanları:

| Alan | Tip | Kural |
|------|-----|-------|
| id | int | 1-50 arası benzersiz sıra numarası |
| text | string | Soru metni. `= ?` ile biter |
| answer | int | Doğru cevap. Her zaman >= 0 (negatif YASAK) |
| type | string | Geçerli değerler: toplama, çıkarma, çarpma, bölme, sıralama, eksik_sayi |
| difficulty | int | 1-5 arası |
| hint | string | Yanlış cevapta gösterilen ipucu. Türkçe, çocuk dili, cevabı VERMEZ |

-### Operatör Sembolleri (text alanında):
- Toplama: `+`
- Cikarma: `-`
- Carpma: `x` (kucuk x, Unicode degil)
- Bolme: `÷`
- Esittir: `=`
- Bilinmeyen sayi: `?`

---

## 7. Soru Tipleri ve Zorluk Seviyeleri (Kesin Sayı Aralıkları)

Her zorluk seviyesi için KESİN sayı aralıkları. AI modeli bu sınırlar dışına ÇIKAMAZ.

### 7.1 Toplama

| Zorluk | Format | Sayi Araligi | Sonuc Araligi | Ornek |
|--------|--------|--------------|---------------|-------|
| 1 | a + b = ? | a: 1-9, b: 1-9 | 2-18 | 3 + 5 = ? |
| 2 | a + b = ? | a: 10-19, b: 1-10 | 11-29 | 12 + 7 = ? |
| 3 | a + b = ? | a: 10-30, b: 10-20 | 20-50 | 23 + 18 = ? |
| 4 | a + b = ? | a: 20-60, b: 10-40 | 30-100 | 45 + 32 = ? |
| 5 | a + b + c = ? | a: 10-40, b: 10-30, c: 5-20 | 25-90 | 25 + 13 + 8 = ? |

### 7.2 Cikarma

| Zorluk | Kural | Sayi Araligi | Sonuc | Ornek |
|--------|-------|--------------|-------|-------|
| 1 | a - b = ? | a: 2-10, b: 1-(a-1) | >= 1 | 7 - 3 = ? |
| 2 | a - b = ? | a: 10-20, b: 1-9 | >= 1 | 15 - 6 = ? |
| 3 | a - b = ? | a: 20-50, b: 5-19 | >= 1 | 34 - 17 = ? |
| 4 | a - b = ? | a: 50-100, b: 10-49 | >= 1 | 73 - 28 = ? |
| 5 | a - b - c = ? | a: 40-80, b: 5-15, c: 3-10 | >= 1 | 50 - 15 - 8 = ? |

**KURAL:** Çıkarma sonucu HER ZAMAN >= 0. Negatif sonuç üretme. b < a olmalı (veya b + c < a zorluk 5 için).

### 7.3 Carpma

| Zorluk | Kural | Carpanlar | Sonuc Araligi | Ornek |
|--------|-------|-----------|---------------|-------|
| 1 | a x 2 veya a x 3 = ? | a: 1-5 | 2-15 | 3 x 2 = ? |
| 2 | a x b = ? | a: 2-5, b: 2-5 | 4-25 | 4 x 3 = ? |
| 3 | a x b = ? | a: 2-9, b: 6-9 | 12-81 | 7 x 8 = ? |
| 4 | a x 10 = ? | a: 1-10 | 10-100 | 6 x 10 = ? |
| 5 | a x b = ? | a: 2-10, b: 2-10 | 4-100 | 8 x 9 = ? |

**KURAL:** Çarpma tablosu 10x10 sınırını GEÇEMEZ. Sonuç maksimum 100.

### 7.4 Bolme

| Zorluk | Kural | Sayi Araligi | Bolum | Ornek |
|--------|-------|--------------|-------|-------|
| 1 | a ÷ 2 = ? | a: 2,4,6,8,10 | 1-5 | 8 ÷ 2 = ? |
| 2 | a ÷ b = ? | b: 2-5, a: b'nin katlari, a <= 25 | 2-5 | 15 ÷ 3 = ? |
| 3 | a ÷ b = ? | b: 2-9, a: b'nin katlari, a <= 50 | 2-9 | 42 ÷ 7 = ? |
| 4 | a ÷ b = ? | b: 2-10, a: b'nin katlari, a <= 80 | 2-10 | 63 ÷ 9 = ? |
| 5 | a ÷ b = ? | b: 2-10, a: b'nin katlari, a <= 100 | 2-10 | 90 ÷ 10 = ? |

**KURAL:** Bölme HER ZAMAN tam bölünür (kalan = 0). Sıfıra bölme YASAK. `a` her zaman `b`nin katları olmalı.


### 7.5 Sıralama

| Zorluk | Format | Sayı Aralığı | Örnek |
|--------|--------|--------------|-------|
| 1 | Hangisi buyuk: A, B | 1-20 | Hangisi buyuk: 7, 12 |
| 2 | En kucugu hangisi: A, B, C | 1-30, 3 sayi | En kucugu hangisi: 15, 8, 22 |
| 3 | En kucugu hangisi: A, B, C, D | 1-50, 4 sayi | En kucugu hangisi: 31, 12, 45, 7 |
| 4 | En buyugu hangisi: A, B, C, D, E | 1-80, 5 sayi | En buyugu hangisi: 23, 67, 41, 55, 12 |
| 5 | X ile Y arasinda kac sayi var? | X, Y: 1-100, Y - X >= 3 | 15 ile 22 arasinda kac sayi var? |

**KURAL sıralama için:**
- `text` içinde sayılar virgüllü verilir
- Zorluk 1 için: büyük olan sayıyı `answer` olarak yaz
- Zorluk 2-3 için: en küçük sayıyı `answer` olarak yaz
- Zorluk 4 için: en büyük sayıyı `answer` olarak yaz
- Zorluk 5 için: aradaki sayı adedi (sınır sayıları hariç, yani Y - X - 1)

### 7.6 Eksik Sayi

| Zorluk | Format | Sayi Araligi | Ornek |
|--------|--------|--------------|-------|
| 1 | ? + a = b | a: 1-5, b: 3-10 | ? + 3 = 7 |
| 2 | a + ? = b | a: 5-15, b: 10-25 | 8 + ? = 15 |
| 3 | ? - a = b | a: 3-10, b: 2-15 | ? - 5 = 8 |
| 4 | a x ? = b | a: 2-5, b: a'nin katı, b <= 30 | 4 x ? = 20 |
| 5 | ? ÷ a = b | a: 2-5, b: 2-8 | ? ÷ 3 = 6 |

**KURAL:** `?` işaretli yer bilinmeyen. Cevap her zaman `?` yerine gelecek sayı. Her zaman >= 0.

---

## 8. Ipucu (hint) Tasarim Kurallari

İpuçları çocuğun ÖĞRENME sürecinin en önemli parçası. Rastgele değil, sistematik olmalı.

### 8.1 İpucu İlkeleri

1. Cevabı ASLA doğrudan verme
2. Çocuğa düşünme yolu göster
3. Somut nesneler kullan (parmak, elma, yıldız)
4. Türkçe, kısa, 7 yaş çocuğu anlayacak dilde
5. Her ipucu 15-40 karakter arası (çok kısa = işlevsiz, çok uzun = okunmaz)

### 8.2 Tip Bazli Ipucu Sablonlari

**Toplama:**
- Zorluk 1-2: "Büyük sayıdan başla, küçük sayıyı parmakla say"
- Zorluk 3-4: "Onluklar ve birlikleri ayrı ayrı topla"
- Zorluk 5: "Önce ilk iki sayıyı topla, sonra üçüncüyü ekle"

**Çıkarma:**
- Zorluk 1-2: "Büyük sayıdan geriye doğru say"
- Zorluk 3-4: "Onluklardan onlukları, birliklerden birlikleri çıkar"
- Zorluk 5: "Önce ilk çıkarmayı yap, sonra ikincisini"

**Çarpma:**
- Zorluk 1: "Toplama ile düşün: 3 x 2 = 3 + 3"
- Zorluk 2-3: "X'in çarpım tablosunu hatırla"
- Zorluk 4: "10 ile çarpmak = sona 0 eklemek"
- Zorluk 5: "Çarpım tablosundan hatırla"

**Bölme:**
- Zorluk 1: "Eşit ikiye bölersen her tarafa kaç düşer?"
- Zorluk 2-3: "Hangi sayı ile çarpınca bu sonucu bulursun?"
- Zorluk 4-5: "Çarpma tablosunu tersten düşün"

**Sıralama:**
- Zorluk 1: "Hangi sayı daha çok?"
- Zorluk 2-3: "En küçük sayıyı bul, sonra sıradakini"
- Zorluk 4-5: "Sayıları kafanda sırala"

**Eksik Sayı:**
- Zorluk 1-2: "Sonuçtan bilinen sayıyı çıkar"
- Zorluk 3: "Sonuca bilinen sayıyı ekle"
- Zorluk 4: "Sonucu bilinen sayıya böl"
- Zorluk 5: "Sonuç ile bölen sayıyı çarp"

### 8.3 Ipucu Cesitliligi

Aynı tipteki sorularda farklı ipuçları kullan. Tekrar eden ipucu yazmaktan kaçın.
Örnek: Toplama için sadece "X'ten başla Y ekle" yerine:
- "X'ten başla, Y parmak say" (somut)
- "Önce onluları topla, sonra birlikleri" (strateji)
- "Yakın yuvarlak sayıdan başla, farkı ekle" (zeki yaklaşım)

---

## 9. topics.json Semasi

Telefon uygulamasında çocuk konu anlatımını açabilir. Bu anlatımlar çocuğun zorlandığı tipi anlamasına yardımcı olur.

```json
{
  "toplama": {
    "title": "Toplama Nasıl Yapılır?",
    "explanation": "2-3 cümlelik basit anlatım, 7 yaş dili",
    "example": "Görsel örnek, emoji ile adım adım",
    "tips": ["Ipucu 1", "Ipucu 2", "Ipucu 3"]
  }
}
```

### Konu Alanlari:

| Alan | Kural |
|------|-------|
| title | Konu başlığı, emoji ile, çocuğa hitap eden |
| explanation | 2-3 cümle, basit Türkçe, 7 yaş seviyesi |
| example | Emoji kullan (elma, yıldız, top vb). Adım adım çözüm göster |
| tips | 2-4 madde, her biri 1 cümle, pratik ve hatırlanır |

### Konu Guncelleme Kurallari:

1. **ZORLU ve KRİTİK** tipteki konuları daha detaylı yaz (daha basit dil, daha çok örnek)
2. **USTA** tipteki konuları kısa tut (çocuk zaten biliyor)
3. Yeni tanıtılan tip için mutlaka konu anlatımı ekle
4. stats.json'da `sawTopic > %30` ise o konuyu TAMAMEN yeniden yaz (demek ki mevcut anlatım yetersiz)
5. Örneklerde çocuğun gerçek hayatından nesneler kullan (elma, top, araba, yıldız)
6. Her tips maddesinde farklı bir yaklaşım göster

**Zorluk geçişlerinde konu güncellemesi (KRİTİK):**
- Toplama d3'e geçişte: topics.json'a **elde (onluğu taşıma)** kavramını ekle → "3+8=11, birlikler toplanınca 10'u geçince 1'i onluğa taşı"
- Çıkarma d3'e geçişte: topics.json'a **onluktan bozma** kavramını ekle → "34-17: 4'ten 7 çıkaramayız, onluktan 10 al, 14-7=7"
- Bu kavramlar explanation ve example alanlarına eklenmeli, tips'e yeni strateji maddesi eklenmeli

---

## 10. stats.json Semasi (Sadece Okunur)

Bu dosya telefondan gelir, AI modeli bunu SADECE OKUR, değistirmez.

**ÖNEMLİ:** Telefon uygulaması aşağıdaki formatta gönderir. Alan adları ve veri tipleri
tam olarak budur — farklı isimlendirme kullanılmaz.

```json
{
  "questionVersion": 1,
  "completedAt": 1774186901,
  "totalShown": 50,
  "totalCorrect": 35,
  "byType": {
    "toplama": { "shown": 20, "correct": 18, "avgTime": "3.1", "hintUsed": 2, "topicUsed": 0 },
    "cikarma": { "shown": 15, "correct": 10, "avgTime": "4.2", "hintUsed": 5, "topicUsed": 3 }
  },
  "byDifficulty": {
    "1": { "shown": 25, "correct": 22 },
    "2": { "shown": 20, "correct": 11 }
  },
  "details": [
    {
      "questionId": 1,
      "correct": true,
      "attempts": 1,
      "time": "2.9",
      "sawHint": false,
      "sawTopic": false
    }
  ]
}
```

### Alan Açıklamaları:

**Üst seviye:**
- `questionVersion`: int — hangi soru setinin (questions.json version) çözüldüğü
- `completedAt`: int — Unix timestamp (saniye cinsinden)
- `totalShown`: int — gösterilen toplam soru sayısı
- `totalCorrect`: int — doğru cevaplanan soru sayısı
- `totalWrong` yok, hesaplanır: totalShown - totalCorrect

**byType (tip bazlı özet):**
- `shown`: int — o tipte gösterilen soru sayısı
- `correct`: int — o tipte doğru cevaplanan
- `avgTime`: string — saniye cinsinden ortalama süre (örneğin "3.1" veya "4,2" — virgül veya nokta olabilir)
- `hintUsed`: int — o tipte ipucu gösterilen soru sayısı
- `topicUsed`: int — o tipte konu anlatımı açılan soru sayısı

**byDifficulty (zorluk seviyesi bazlı özet):**
- `shown`: int — o zorluk seviyesinde gösterilen soru sayısı
- `correct`: int — o zorluk seviyesinde doğru cevaplanan

**details (soru bazlı detay dizisi):**
- `questionId`: int — questions.json'daki id
- `correct`: bool — doğru cevaplandı mı
- `attempts`: int — kaç deneme yapıldı (1 = ilk seferde doğru)
- `time`: string — saniye cinsinden cevaplama süresi (örneğin "2.9")
- `sawHint`: bool — ipucu gösterildi mi (1. yanlış cevapta true olur)
- `sawTopic`: bool — konu anlatımı açıldı mı (2. yanlış cevapta true olur)

### Analiz İçin Formül Rehberi:

**Başarı oranı hesaplama:**
```
tip_başarı = byType[tip].correct / byType[tip].shown * 100
```

**Süre hesaplama (string'den float'a çevirme):**
```
avgTime değerini oku → virgül varsa noktaya çevir → float yap
örneğin "4,2" → 4.2 saniye
```

**İpucu/Konu kullanım oranı:**
```
hint_orani = byType[tip].hintUsed / byType[tip].shown * 100
topic_orani = byType[tip].topicUsed / byType[tip].shown * 100
```

**Zorluk tespiti (details dizisinden):**
```
ZORLU soru = attempts > 2 VEYA sawHint == true
KOLAY soru = attempts == 1 VE time < 3 saniye
DÜŞÜNÜYOR = attempts == 1 VE time > 15 saniye (biliyor ama yavaş)
```

### Duygu/Motivasyon Sinyalleri (dolaylı tespit):

Telefon doğrudan duygu verisi göndermez. Ancak mevcut verilerden çıkarım yapılabilir:

| Sinyal | Tespit Yontemi | Anlam |
|--------|----------------|-------|
| Hayal kırıklığı | attempts > 2 oranı > %40 VEYA sawHint > %50 | Çocuk sürekli yanlış yapıyor, morali düşük olabilir |
| Sıkıntı | Tüm sorularda time < 3sn VE başarı > %90 | Çok kolay, zorlanmıyor, sıkılıyor olabilir |
| Öğrenme | %60-80 başarı VE sawHint %20-40 arası | İdeal bölge — zorlanıp öğreniyor |
| Kafa karışıklığı | sawTopic > %30 | Konuyu anlamamış, temel anlatım yetersiz |
| Güvensizlik | Kolay sorularda bile time > 10sn | Biliyor ama cevapta tereddüt ediyor |

---

## 11. Rapor Formati (stdout)

Soru üretimi tamamlandığında şu formatta çıktı ver:

```
MathLock AI - 2. Sınıf Matematik Raporu
========================================
Önceki set: v{eski} | Başarı: %{oran} | Süre: {gün} gün
Güçlü: {tipler}
Zayıf: {tipler}
Zorluk: {eski_ort:.1f} => {yeni_ort:.1f}
Yeni tanıtılan: {varsa tip adı, yoksa "-"}
Konu güncellendi: {tipler veya "-"}
Yeni set: v{yeni} | 50 soru | {kısa dağılım}
```

---

## 12. Cikti Gereksinimleri (Kontrol Listesi)

Soru uretimi tamamlanmadan once su kurallarin TUMUNU kontrol et:

1. Geçerli JSON, trailing comma yok, UTF-8
2. TAM 50 soru (ne eksik ne fazla)
3. Her sorunun `answer` alanı DOĞRU hesaplanmış (çift kontrol yap)
4. Tekrar eden `text` yok (50 benzersiz soru)
5. `id` alanları 1-50 arası sıralama
6. `difficulty` alanları 1-5 arası
7. `answer` alanları hep >= 0 (negatif YASAK)
8. `type` alanları geçerli 6 tipten biri
9. `hint` alanları boş değil, Türkçe, cevabı vermiyor
10. `version` = mevcut version + 1 (yoksa 1)
11. `generatedAt` = üretim anı (ISO 8601)
12. `generatedBy` = "ai"
13. `difficultyProfile.adjustmentReason` Türkçe, anlamlı, 1 cümle
14. `topics.json`'da sorularda kullanılan TÜM tipler için konu anlatımı var
15. Çıkarma sonucu hep >= 0
16. Bölme hep tam bölünür (kalan = 0)
17. Çarpma sonucu max 100
18. Operatörler: +, -, x, ÷, =
19. Sıralama sorularında `answer` kurallara uygun
20. Eksik sayı sorularında `?` işareti mevcut

## 13. Benzersizlik Garantisi

50 sorunun HER BİRİ farkli bir `text` değerine sahip olmalı. Aynı soru metni iki kez kullanılamaz.

Eğer bir tip için yeterli benzersiz soru üretilemiyorsa (örneğin çarpma zorluk 1 için max 10 benzersiz soru var), o tipten daha az soru üret ve karşılığı toplama veya çıkarmaya dağıt.

**Tekrar kontrol yöntemi:** Soruları ürettikten sonra tüm `text` alanlarını bir listeye koy. Listede tekrar eden varsa, tekrar eden soruyu farklı bir soruyla değiştir.

Doğrulama başarısız olursa agent tekrar çalıştırılır.