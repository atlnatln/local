# MathLock AI - Adaptif Matematik Soru Motoru

## 1. Misyon

Bu dosya, 7-8 yasinda ilkokul 2. sinifa giden bir cocuk icin **adaptif matematik soru seti** ureten AI modelinin calisma kilavuzudur.

Cocuk telefonunda bir uygulama acmak istediginde matematik sorusu cozer. Her 50 soruluk set tamamlandiginda performans verisi (`stats.json`) VPS'e yuklenir. Bu dosyadaki algoritma sayesinde AI modeli yeni 50 soruyu cocugun gelisim seviyesine gore uretir.

**Pedagojik temel:** Vygotsky'nin Yakinsal Gelisim Alani (Zone of Proximal Development). Cocuga ne cok kolay ne cok zor sorular verilir. Her soru setinde cocugun "biraz zorlansa da basarabilecegi" seviyeyi hedefleriz.

Hedef basari orani: **%65-80** (bu aralik maksimum ogrenme saglar)

## 2. Calisma Ortami

- Dizin: `/home/akn/vps/projects/mathlock/`
- Veri dizini: `data/`
- Dokunulacak dosyalar: SADECE `data/questions.json` ve `data/topics.json`
- Dokunulmayacak dosyalar: Digerleri (Android kodu, deploy.sh, AGENTS.md, validate-questions.py vb.)

## 3. Gorev Adimlari

`ai-generate.sh` tarafindan cagrildiginda su adimlari SIRASI ILE uygula:

### Adim 1 - Veri Okuma
1. `data/stats.json` oku (yoksa Adim 2'nin "Ilk Set" bolumune git)
2. `data/questions.json` oku (mevcut version numarasini al)
3. `data/topics.json` oku (mevcut konu anlatimlarini gor)

### Adim 2 - Analiz ve Karar
stats.json varsa 4. bolundeki Adaptif Algoritmaya gore analiz et.
stats.json yoksa 5. bolumdeki Ilk Set Algoritmaya gore uret.

### Adim 3 - 50 Soru Uret
6. bolumdeki sema ve kurallara gore `data/questions.json` dosyasina yaz (uzerine yaz).

### Adim 4 - Konu Anlatimlarini Guncelle
7. bolumdeki kurallara gore `data/topics.json` dosyasina yaz.

### Adim 5 - Rapor
11. bolumdeki formatta stdout'a kisa rapor yazdir.

---

## 4. Adaptif Algoritma (Kalp)

Bu bolum AGENTS.md'nin kalbidir. AI modeli bu kurallari **birebir** takip etmelidir.

### 4.1 Performans Analizi

stats.json'daki `byType` verisinden her soru tipi icin:

```
basari_orani = byType[tip].correct / byType[tip].shown * 100
ort_sure_sn = byType[tip].avgTime degerini float'a cevir (virgul varsa noktaya cevir)
```

Her soru tipini su kategorilere ayir:

| Kategori | Basari | Sure | Anlam |
|----------|--------|------|-------|
| USTA | >= %85 | < 5sn | Cocuk bu tipi cok iyi biliyor |
| GUVENLI | >= %85 | 5-10sn | Biliyor ama hizlanmadi |
| GELISEN | %60-84 | herhangi | Ogrenme surecinde, ideal bolge |
| ZORLU | %40-59 | herhangi | Zorlaniyorsa, destek gerekli |
| KRITIK | < %40 | herhangi | Anlamamis, temele don |

### 4.2 Ipucu ve Konu Kullanim Analizi

stats.json'daki `byType` ve `details` verilerinden analiz yap:

| Sinyal | Tespit | Aksiyon |
|--------|--------|---------|
| byType[tip].hintUsed / shown > %50 | Cocuk ipucuna cok bakiyor | O tipte zorlaniyordur, zorluk ARTIRMA |
| byType[tip].topicUsed / shown > %30 | Konu anlatimini aciyor | Konuyu anlamamis, topics.json detaylandir |
| details'te attempts > 2 orani > %40 | Cok fazla yanlis deniyor | Zorluk 1 seviye DUS |
| byType[tip].avgTime > 15 saniye | Cok yavas cevaplayarak dusunuyor | Zorluk ayni kalsin ama basit sayilar ver |
| byType[tip].avgTime < 3 saniye | Cok hizli, dusunmeden yapiyor | Zorluk ARTIR, buyuk sayilara gec |

### 4.3 Zorluk Karar Matrisi

Her soru tipi icin onceki setteki zorluk seviyesini ve performansi birlestir.

**onceki_zorluk hesaplama:** Onceki questions.json'da o tip icin en SIK kullanilan zorluk seviyesi (mode). Esitlik varsa yuksek olani al.

**Minimum orneklem kurali:** Bir tipte shown < 3 ise o tipin kategorisi guvenilir sekilde belirlenemez. onceki_zorluk seviyesinde kal, degistirme.

```
EGER basari >= %85 VE sure < 5sn:
    yeni_zorluk = onceki_zorluk + 1  (max 5)
EGER basari >= %85 VE sure >= 5sn:
    yeni_zorluk = onceki_zorluk      (hizlanmayi bekle)
EGER basari %60-84:
    yeni_zorluk = onceki_zorluk      (ideal bolge, degistirme)
EGER basari %40-59:
    yeni_zorluk = onceki_zorluk - 1  (min 1)
EGER basari < %40:
    yeni_zorluk = MAX(onceki_zorluk - 2, 1)  (sert dusus ama temele ATLAMAZ)
EGER byType[tip].topicUsed / shown > %30:
    yeni_zorluk = MIN(yeni_zorluk, onceki_zorluk)  (asla artirma)
```

**Ek kural:** Zorluk ASLA bir seferde 2'den fazla artmaz. Ornegin zorluk 1'den 3'e atlanamaz.

**Ani dusus korumasi:** Eger bir tipin basarisi onceki sete gore %30'dan fazla dustuyse (ornegin %80 → %40), bu "kotu gun" olabilir. Zorluk en fazla 2 seviye dusurulur ve adjustmentReason'a "ani dusus — kotu gun olabilir" notu eklenir.

### 4.4 Soru Dagitim Algoritmasi

Her sette **50 soru** uretilir. Dagitim 3 gruba ayrilir:

**GRUP A - Pekistirme (%40 = 20 soru):**
ZORLU ve KRITIK olan tiplerden. Zorluk = mevcut veya mevcut-1.
Amac: Cocugun basarili olmasi, guveni gelmesi.

**GRUP A sinirlamalari:**
- Tek bir tipten en fazla **8 soru** (cok tekrar sikici ve yorucu)
- KRITIK (basari < %40) tipten en fazla **5 soru** — cocuk zaten anlamamis, sel gibi soru morali bozar
- Kalan bos kontenjan: cocugun GUVENLI veya USTA oldugu tiplerden **kolay (zorluk 1-2) sorularla** doldur → guven insasi
- GRUP A icin yeterli ZORLU/KRITIK tip yoksa: eksik sorulari en dusuk basarili GELISEN tiplerden al

**GRUP B - Gelisim (%35 = 17-18 soru):**
GELISEN olan tiplerden. Zorluk = mevcut.
Amac: Ogrenme devam etsin, bu bolgede kalsin.

**GRUP C - Meydan Okuma (%25 = 12-13 soru):**
USTA ve GUVENLI olan tiplerden. Zorluk = mevcut+1 (veya farkli formatta sorular).
Amac: Sikici olmasin, ilerlesin.

**GRUP C bos kalirsa (USTA/GUVENLI tip yok):**
En iyi performansli GELISEN tiplerden mevcut_zorluk+1 ile doldur. Cocugun en guclu alani biraz daha ittirmek anlamina gelir.

**Eger tum tipler ayni kategorideyse:**
- Hepsi USTA: Zorluk artir veya yeni tip tanit (4.5'e bak)
- Hepsi KRITIK: Tum sorular zorluk 1, cesaret verici basit sorular (tip basina max 10)

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
    "adjustmentReason": "Turkce, 1 cumle, neden bu zorluk secildi"
  },
  "questions": [
    {
      "id": 1,
      "text": "3 + 4 = ?",
      "answer": 7,
      "type": "toplama",
      "difficulty": 1,
      "hint": "3'ten basla, parmaklarinla 4 tane say"
    }
  ]
}
```

### overall Degerleri:
- `beginner`: ortalama zorluk 1.0-1.5
- `developing`: ortalama zorluk 1.5-2.5
- `intermediate`: ortalama zorluk 2.5-3.5
- `advanced`: ortalama zorluk 3.5+

### Soru Alanlari:

| Alan | Tip | Kural |
|------|-----|-------|
| id | int | 1-50 arasi benzersiz sira numarasi |
| text | string | Sorunun goruntulenecek metni. `= ?` ile biter |
| answer | int | Dogru cevap. Her zaman >= 0 (negatif YASAK) |
| type | string | Gecerli degerler: toplama, cikarma, carpma, bolme, siralama, eksik_sayi |
| difficulty | int | 1-5 arasi |
| hint | string | Yanlis cevapta gosterilen ipucu. Turkce, cocuk dili, cevabi VERMEZ |

### Operator Sembolleri (text alaninda):
- Toplama: `+`
- Cikarma: `-`
- Carpma: `x` (kucuk x, Unicode degil)
- Bolme: `/` (bolme isareti)
- Esittir: `=`

---

## 7. Soru Tipleri ve Zorluk Seviyeleri (Kesin Sayy Araliklari)

Her zorluk seviyesi icin KESIN sayi araliklari. AI modeli bu sinirlar disina CIKAMAZ.

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

**KURAL:** Cikarma sonucu HER ZAMAN >= 0. Negatif sonuc uretme. b < a olmali (veya b + c < a zorluk 5 icin).

### 7.3 Carpma

| Zorluk | Kural | Carpanlar | Sonuc Araligi | Ornek |
|--------|-------|-----------|---------------|-------|
| 1 | a x 2 veya a x 3 = ? | a: 1-5 | 2-15 | 3 x 2 = ? |
| 2 | a x b = ? | a: 2-5, b: 2-5 | 4-25 | 4 x 3 = ? |
| 3 | a x b = ? | a: 2-9, b: 6-9 | 12-81 | 7 x 8 = ? |
| 4 | a x 10 = ? | a: 1-10 | 10-100 | 6 x 10 = ? |
| 5 | a x b = ? | a: 2-10, b: 2-10 | 4-100 | 8 x 9 = ? |

**KURAL:** Carpma tablosu 10x10 sinirini GECEMEZ. Sonuc max 100.

### 7.4 Bolme

| Zorluk | Kural | Sayi Araligi | Bolum | Ornek |
|--------|-------|--------------|-------|-------|
| 1 | a / 2 = ? | a: 2,4,6,8,10 | 1-5 | 8 / 2 = ? |
| 2 | a / b = ? | b: 2-5, a: b'nin katlari, a <= 25 | 2-5 | 15 / 3 = ? |
| 3 | a / b = ? | b: 2-9, a: b'nin katlari, a <= 50 | 2-9 | 42 / 7 = ? |
| 4 | a / b = ? | b: 2-10, a: b'nin katlari, a <= 80 | 2-10 | 63 / 9 = ? |
| 5 | a / b = ? | b: 2-10, a: b'nin katlari, a <= 100 | 2-10 | 90 / 10 = ? |

**KURAL:** Bolme HER ZAMAN tam bolunur (kalan = 0). Sifira bolme YASAK. `a` her zaman `b`nin katlari olmali.

### 7.5 Siralama

| Zorluk | Format | Sayi Araligi | Ornek |
|--------|--------|--------------|-------|
| 1 | Hangisi buyuk: A mi B mi? | 1-20 | Hangisi buyuk: 7 mi 12 mi? |
| 2 | En kucugu hangisi: A, B, C? | 1-30, 3 sayi | En kucugu hangisi: 15, 8, 22? |
| 3 | En kucugu hangisi: A, B, C, D? | 1-50, 4 sayi | En kucugu hangisi: 31, 12, 45, 7? |
| 4 | En buyugu hangisi: A, B, C, D, E | 1-80, 5 sayi | En buyugu hangisi: 23, 67, 41, 55, 12 |
| 5 | X ile Y arasinda kac sayi var? | X, Y: 1-100, Y - X >= 3 | 15 ile 22 arasinda kac sayi var? |

**KURAL siralama icin:**
- `text` icinde sayilar virgullu verilir
- Zorluk 1 icin: buyuk olan sayiyi answer olarak yaz
- Zorluk 2-3 icin: en kucuk sayiyi answer olarak yaz
- Zorluk 4 icin: en buyuk sayiyi answer olarak yaz
- Zorluk 5 icin: aradaki sayi adedi (sinir sayilari haric, yani Y - X - 1)

### 7.6 Eksik Sayi

| Zorluk | Format | Sayi Araligi | Ornek |
|--------|--------|--------------|-------|
| 1 | _ + a = b | a: 1-5, b: 3-10 | _ + 3 = 7 |
| 2 | a + _ = b | a: 5-15, b: 10-25 | 8 + _ = 15 |
| 3 | _ - a = b | a: 3-10, b: 2-15 | _ - 5 = 8 |
| 4 | a x _ = b | a: 2-5, b: a'nin kati, b <= 30 | 4 x _ = 20 |
| 5 | _ / a = b | a: 2-5, b: 2-8 | _ / 3 = 6 |

**KURAL:** `_` isaretli yer bilinmeyen. Cevap her zaman `_` yerine gelecek sayi. Her zaman >= 0.

---

## 8. Ipucu (hint) Tasarim Kurallari

Ipuculari cocugun OGRENME surecinin en onemli parcasi. Rastgele degil, sistematik olmali.

### 8.1 Ipucu Ilkeleri

1. Cevabi ASLA dogrudan verme
2. Cocuga dusunme yolu goster
3. Somut nesneler kullan (parmak, elma, yildiz)
4. Turkce, kisa, 7 yas cocugu anlayacak dilde
5. Her ipucu 15-40 karakter arasi (cok kisa = islevsiz, cok uzun = okunmaz)

### 8.2 Tip Bazli Ipucu Sablonlari

**Toplama:**
- Zorluk 1-2: "Buyuk sayidan basla, kucuk sayiyi parmakla say"
- Zorluk 3-4: "Onluklar ve birlikleri ayri ayri topla"
- Zorluk 5: "Once ilk iki sayiyi topla, sonra ucuncuyu ekle"

**Cikarma:**
- Zorluk 1-2: "Buyuk sayidan geriye dogru say"
- Zorluk 3-4: "Onluklardan onluklari, birliklerden birlikleri cikar"
- Zorluk 5: "Once ilk cikarmayi yap, sonra ikincisini"

**Carpma:**
- Zorluk 1: "Toplama ile dusun: 3 x 2 = 3 + 3"
- Zorluk 2-3: "X'in carpim tablosunu hatirla"
- Zorluk 4: "10 ile carpmak = sona 0 eklemek"
- Zorluk 5: "Carpim tablosundan hatirla"

**Bolme:**
- Zorluk 1: "Esit ikiye bolersen her tarafa kac duser?"
- Zorluk 2-3: "Hangi sayi ile carpinca bu sonucu bulursun?"
- Zorluk 4-5: "Carpma tablosunu tersten dusun"

**Siralama:**
- Zorluk 1: "Hangi sayi daha cok?"
- Zorluk 2-3: "En kucuk sayiyi bul, sonra siradakini"
- Zorluk 4-5: "Sayilari kafanda sirala"

**Eksik Sayi:**
- Zorluk 1-2: "Sonuctan bilinen sayiyi cikar"
- Zorluk 3: "Sonuca bilinen sayiyi ekle"
- Zorluk 4: "Sonucu bilinen sayiya bol"
- Zorluk 5: "Sonuc ile bolen sayiyi carp"

### 8.3 Ipucu Cesitliligi

Ayni tipteki sorularda farkli ipuculari kullan. Tekrar eden ipucu yazmaktan kacin.
Ornek: Toplama icin sadece "X'ten basla Y ekle" yerine:
- "X'ten basla, Y parmak say" (somut)
- "Once onlulari topla, sonra birlikleri" (strateji)
- "Yakin yuvarlak sayidan basla, farki ekle" (zeki yaklasim)

---

## 9. topics.json Semasi

Telefon uygulamasinda cocuk konu anlatimini acabilir. Bu anlatimlar cocugun zorlandigi tipi anlamasina yardimci olur.

```json
{
  "toplama": {
    "title": "Toplama Nasil Yapilir?",
    "explanation": "2-3 cumlelik basit anlatim, 7 yas dili",
    "example": "Gorsel ornek, emoji ile adim adim",
    "tips": ["Ipucu 1", "Ipucu 2", "Ipucu 3"]
  }
}
```

### Konu Alanlari:

| Alan | Kural |
|------|-------|
| title | Konu basligi, emoji ile, cocuga hitap eden |
| explanation | 2-3 cumle, basit Turkce, 7 yas seviyesi |
| example | Emoji kullan (elma, yildiz, top vb). Adim adim cozum goster |
| tips | 2-4 madde, her biri 1 cumle, pratik ve hatirlanir |

### Konu Guncelleme Kurallari:

1. **ZORLU ve KRITIK** tipteki konulari daha detayli yaz (daha basit dil, daha cok ornek)
2. **USTA** tipteki konulari kisa tut (cocuk zaten biliyor)
3. Yeni tanitilan tip icin mutlaka konu anlatimi ekle
4. stats.json'da `sawTopic > %30` ise o konuyu TAMAMEN yeniden yaz (demek ki mevcut anlatim yetersiz)
5. Orneklerde cocugun gercek hayatindan nesneler kullan (elma, top, araba, yildiz)
6. Her tips maddesinde farkli bir yaklasim goster

**Zorluk gecislerinde konu guncellemesi (KRITIK):**
- Toplama d3'e geciste: topics.json'a **elde (onlugu tasima)** kavramini ekle → "3+8=11, birlikler toplaninca 10'u gecince 1'i onluga tasi"
- Cikarma d3'e geciste: topics.json'a **onluktan bozma** kavramini ekle → "34-17: 4'ten 7 cikaramayiz, onluktan 10 al, 14-7=7"
- Bu kavramlar explanation ve example alanlarina eklenmeli, tips'e yeni strateji maddesi eklenmeli

---

## 10. stats.json Semasi (Sadece Okunur)

Bu dosya telefondan gelir, AI modeli bunu SADECE OKUR, degistirmez.

**ONEMLI:** Telefon uygulamasi asagidaki formatta gonderir. Alan adlari ve veri tipleri
tam olarak budur — farkli isimlendirme kullanilmaz.

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

### Alan Aciklamalari:

**Ust seviye:**
- `questionVersion`: int — hangi soru setinin (questions.json version) cozuldugu
- `completedAt`: int — Unix timestamp (saniye cinsinden)
- `totalShown`: int — gosterilen toplam soru sayisi
- `totalCorrect`: int — dogru cevaplanan soru sayisi
- `totalWrong` yok, hesaplanir: totalShown - totalCorrect

**byType (tip bazli ozet):**
- `shown`: int — o tipte gosterilen soru sayisi
- `correct`: int — o tipte dogru cevaplanan
- `avgTime`: string — saniye cinsinden ortalama sure (ornegin "3.1" veya "4,2" — virgul veya nokta olabilir)
- `hintUsed`: int — o tipte ipucu gosterilen soru sayisi
- `topicUsed`: int — o tipte konu anlatimi acilan soru sayisi

**byDifficulty (zorluk seviyesi bazli ozet):**
- `shown`: int — o zorluk seviyesinde gosterilen soru sayisi
- `correct`: int — o zorluk seviyesinde dogru cevaplanan

**details (soru bazli detay dizisi):**
- `questionId`: int — questions.json'daki id
- `correct`: bool — dogru cevaplandi mi
- `attempts`: int — kac deneme yapildi (1 = ilk seferde dogru)
- `time`: string — saniye cinsinden cevaplama suresi (ornegin "2.9")
- `sawHint`: bool — ipucu gosterildi mi (1. yanlis cevapta true olur)
- `sawTopic`: bool — konu anlatimi acildi mi (2. yanlis cevapta true olur)

### Analiz Icin Formul Rehberi:

**Basari orani hesaplama:**
```
tip_basari = byType[tip].correct / byType[tip].shown * 100
```

**Sure hesaplama (string'den float'a cevirme):**
```
avgTime degerini oku → virgul varsa noktaya cevir → float yap
ornegin "4,2" → 4.2 saniye
```

**Ipucu/Konu kullanim orani:**
```
hint_orani = byType[tip].hintUsed / byType[tip].shown * 100
topic_orani = byType[tip].topicUsed / byType[tip].shown * 100
```

**Zorluk tespiti (details dizisinden):**
```
ZORLU soru = attempts > 2 VEYA sawHint == true
KOLAY soru = attempts == 1 VE time < 3 saniye
DUSUNUYOR = attempts == 1 VE time > 15 saniye (biliyor ama yavas)
```

### Duygu/Motivasyon Sinyalleri (dolayli tespit):

Telefon dogrudan duygu verisi gondermez. Ancak mevcut verilerden cikarim yapilabilir:

| Sinyal | Tespit Yontemi | Anlam |
|--------|----------------|-------|
| Hayal kirikligi | attempts > 2 orani > %40 VEYA sawHint > %50 | Cocuk surekli yanlis yapiyor, morali dusuk olabilir |
| Sikinti | Tum sorularda time < 3sn VE basari > %90 | Cok kolay, zorlanmiyor, sikiliyor olabilir |
| Ogrenme | %60-80 basari VE sawHint %20-40 arasi | Ideal zone — zorlanip ogreniyor |
| Kafa karisikligi | sawTopic > %30 | Konuyu anlamamis, temel anlatim yetersiz |
| Guvensizlik | Kolay sorularda bile time > 10sn | Biliyor ama cevapta tereddut ediyor |

---

## 11. Rapor Formati (stdout)

Soru uretimi tamamlandiginda su formatta cikti ver:

```
MathLock AI - 2. Sinif Matematik Raporu
========================================
Onceki set: v{eski} | Basari: %{oran} | Sure: {gun} gun
Guclu: {tipler}
Zayif: {tipler}
Zorluk: {eski_ort:.1f} => {yeni_ort:.1f}
Yeni tanitilan: {varsa tip adi, yoksa "-"}
Konu guncellendi: {tipler veya "-"}
Yeni set: v{yeni} | 50 soru | {kisa dagilim}
```

---

## 12. Cikti Gereksinimleri (Kontrol Listesi)

Soru uretimi tamamlanmadan once su kurallarin TUMUNU kontrol et:

1. Gecerli JSON, trailing comma yok, UTF-8
2. TAM 50 soru (ne eksik ne fazla)
3. Her sorunun `answer` alani DOGRU hesaplanmis (cift kontrol yap)
4. Tekrar eden `text` yok (50 benzersiz soru)
5. `id` alanlari 1-50 arasi siralama
6. `difficulty` alanlari 1-5 arasi
7. `answer` alanlari hep >= 0 (negatif YASAK)
8. `type` alanlari gecerli 6 tipten biri
9. `hint` alanlari bos degil, Turkce, cevabi vermiyor
10. `version` = mevcut version + 1 (yoksa 1)
11. `generatedAt` = uretim ani (ISO 8601)
12. `generatedBy` = "ai"
13. `difficultyProfile.adjustmentReason` Turkce, anlamli, 1 cumle
14. `topics.json`'da sorularda kullanilan TUM tipler icin konu anlatimi var
15. Cikarma sonucu hep >= 0
16. Bolme hep tam bolunur (kalan = 0)
17. Carpma sonucu max 100
18. Operatorler: +, -, x, /, =
19. Siralama sorularinda `answer` kurallara uygun
20. Eksik sayi sorularinda `_` isareti mevcut

## 13. Benzersizlik Garantisi

50 sorunun HER BIRI farkli bir `text` degerine sahip olmali. Ayni soru metni iki kez kullanilamaz.

Eger bir tip icin yeterli benzersiz soru uretilemiyorsa (ornegin carpma zorluk 1 icin max 10 benzersiz soru var), o tipten daha az soru uret ve karsiligi toplama veya cikarmaya dagit.

**Tekrar kontrol yontemi:** Sorulari urettikten sonra tum `text` alanlarini bir listeye koy. Listede tekrar eden varsa, tekrar eden soruyu farkli bir soruyla degistir.

Doğrulama başarısız olursa agent tekrar çalıştırılır.