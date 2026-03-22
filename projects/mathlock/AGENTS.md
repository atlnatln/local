# MathLock AI — İlkokul 2. Sınıf Adaptif Matematik Sistemi

## Proje Özeti

MathLock, ilkokul 2. sınıfa giden ve ileride kodlama/yazılım becerileri kazanması amaçlanan bir çocuk için tasarlanmış Android telefon kilidi
uygulamasıdır. Çocuk bir uygulamayı açmak istediğinde matematik sorusu çözer.
Sistem **tamamen otomatik** çalışır:

1. Telefon 50 soruyu sırayla gösterir (her kilit açmada 1 soru)
2. 50 soru tamamlanınca performans verisi (`stats.json`) VPS'e yüklenir
3. VPS'de bu agent çalışır → verileri analiz eder → yeni 50 soru üretir
4. `validate-questions.py` testleri çalışır → sorunsuzsa onaylar
5. Telefon yeni soruları otomatik indirir → döngü tekrarlar

**Hedef kitle:** 7-8 yaş, ilkokul 2. sınıf. Sorular çocuğun seviyesinde başlar,
performansa göre kademeli olarak zorlaşır. Asla sindiremeyeceği kadar zor soru verilmez.

## Çalışma Ortamı

- **Dizin:** `/home/akn/vps/projects/mathlock/`
- **Veri dizini:** `data/`
- **Model:** gpt-4.1

## Veri Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `data/questions.json` | Aktif 50 soruluk set (telefon bunu indirir) |
| `data/topics.json` | Soru tiplerine göre konu anlatımları (telefon bunu indirir) |
| `data/stats.json` | Telefondan gelen son 50 sorunun performans verileri |
| `data/history/` | Eski stats ve questions arşivi |

## Görev

Bu agent `ai-generate.sh` tarafından çağrıldığında **sırasıyla** şu adımları uygular:

### Adım 1 — Analiz
1. `data/stats.json` dosyasını oku
2. Her soru tipinde başarı oranını hesapla
3. Her zorluk seviyesinde başarı oranını hesapla
4. Çocuğun güçlü ve zayıf alanlarını tespit et
5. Ortalama yanıt süresini değerlendir (çocuk için 10sn üstü = zor)

### Adım 2 — Yeni Soru Seti Üretimi
1. Zorluk ayarlama kurallarına göre yeni 50 soru üret
2. `data/questions.json` dosyasına yaz (üzerine yaz)
3. `version` alanını 1 artır

### Adım 3 — Konu Anlatımlarını Güncelle
1. `data/topics.json` dosyasını oku
2. Zayıf alanlardaki konu anlatımlarını gözden geçir
3. Çocuğun zorlandığı tiplere **daha detaylı/basit** anlatım yaz
4. Yeni soru tipleri eklendiyse onların anlatımını da ekle
5. `data/topics.json` dosyasına yaz

### Adım 4 — Rapor
Stdout'a kısa analiz raporu yazdır.

---

## questions.json Şeması

```json
{
  "version": 2,
  "generatedAt": "2026-03-22T02:00:00Z",
  "generatedBy": "ai",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.2,
    "adjustmentReason": "Toplama ve çıkarmada iyi gidiyor, çarpma yeni tanıtılıyor"
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

### Soru Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | int | 1-50 arası benzersiz sıra numarası |
| `text` | string | Sorunun görüntülenen metni, `= ?` ile biter |
| `answer` | int | Doğru cevap (her zaman pozitif tam sayı, ≥ 0) |
| `type` | string | Soru kategorisi |
| `difficulty` | int | 1-5 arası zorluk seviyesi |
| `hint` | string | Yanlış cevapta gösterilecek kısa ipucu. Çocuk dili ile, cevabı direkt vermeden. Türkçe. |

### Soru Tipleri ve Zorluk Seviyeleri

**2. sınıf müfredatına uygun ilerleyiş:**

| Tip | Türkçe | Zorluk 1 | Zorluk 2 | Zorluk 3 | Zorluk 4 | Zorluk 5 |
|-----|--------|----------|----------|----------|----------|----------|
| `toplama` | Toplama | a+b (1-10) | a+b (10-20) | a+b (sonuç ≤50) | a+b (sonuç ≤100) | a+b+c (üç sayı, sonuç ≤100) |
| `cikarma` | Çıkarma | a-b (1-10, sonuç≥0) | a-b (a≤20, sonuç≥0) | a-b (a≤50, sonuç≥0) | a-b (a≤100, sonuç≥0) | a-b-c (sonuç≥0) |
| `carpma` | Çarpma | a×2 (1-5) | a×b (2,3,4,5 çarpım tablosu) | a×b (6,7,8,9 tablosu) | a×10 (1-10) | a×b (karışık, a≤10, b≤10) |
| `bolme` | Bölme | a÷2 (tam, a≤10) | a÷b (2,3,4,5 ile tam bölünen) | a÷b (6-10 ile tam bölünen) | a÷b (a≤50, tam bölünen) | a÷b (a≤100, tam bölünen) |
| `siralama` | Sıralama & Karşılaştırma | Büyük/küçük (1-20) | Sıralama (3 sayı) | Sıralama (4 sayı) | En büyük/küçük bul (5 sayı) | Arasında kaç sayı var |
| `eksik_sayi` | Eksik sayı bul | _ + a = b (1-10) | a + _ = b (10-20) | _ - a = b (1-20) | a × _ = b (kolay) | _ ÷ a = b (kolay) |

**ÖNEMLİ — 2. sınıf kuralları:**
- `answer` her zaman **pozitif tam sayı veya 0** olmalı, **negatif olmaz**
- Çıkarma sonucu her zaman ≥ 0
- Bölme her zaman tam bölünen (kalan yok)
- Çarpma tablosu 10×10'u geçmez
- İlk setlerde sadece `toplama` ve `cikarma`. Çocuk hazır olunca `carpma` ve `bolme` eklenir
- `siralama` ve `eksik_sayi` tipleri destekleyici egzersizler

### Başlangıç Soru Dağılımı (İlk Set)

İlk set (stats.json yokken):
- **toplama:** 20 soru (difficulty 1-2)
- **cikarma:** 15 soru (difficulty 1-2)
- **carpma:** 8 soru (difficulty 1 — sadece ×2 tablosu)
- **bolme:** 4 soru (difficulty 1 — sadece ÷2)
- **siralama:** 2 soru (difficulty 1)
- **eksik_sayi:** 1 soru (difficulty 1)

---

## topics.json Şeması

Her soru tipi için çocuğa gösterilecek konu anlatımı:

```json
{
  "toplama": {
    "title": "Toplama Nasıl Yapılır? ➕",
    "explanation": "Toplama, iki sayıyı birleştirmek demektir...",
    "example": "3 + 2 = ?\n🍎🍎🍎 + 🍎🍎 = 🍎🍎🍎🍎🍎\nCevap: 5",
    "tips": [
      "Büyük sayıdan başla, küçük sayıyı parmakla say",
      "5 + 3 için: 5'ten başla → 6, 7, 8"
    ]
  },
  "cikarma": {
    "title": "Çıkarma Nasıl Yapılır? ➖",
    "explanation": "...",
    "example": "...",
    "tips": ["..."]
  }
}
```

### Topic Alanları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `title` | string | Konu başlığı, emoji ile. Çocuğa hitap eden |
| `explanation` | string | 2-3 cümlelik basit anlatım. **7 yaş çocuk dili** ile |
| `example` | string | Görsel örnek. Emoji kullan (🍎, ⭐, 🔵 vb). Adım adım |
| `tips` | string[] | 2-3 pratik ipucu. Kısa ve hatırlanır |

**Konu anlatımı kuralları:**
- Dil: Çocuğa hitap eden, samimi, teşvik edici Türkçe
- Emoji kullan — çocuklar görsele iyi tepki verir
- Uzun paragraflar yazma, maddeler halinde tut
- Her ipucu 1 cümle
- Zayıf alanlarda topics.json'daki anlatımı daha detaylı/basamaklı yap

---

## stats.json Şeması

Telefon 50 sorunun tamamını gösterdikten sonra bu dosyayı VPS'e yükler:

```json
{
  "questionsVersion": 2,
  "startedAt": "2026-03-22T10:00:00Z",
  "completedAt": "2026-03-22T18:30:00Z",
  "totalShown": 50,
  "totalCorrect": 35,
  "totalWrong": 15,
  "results": [
    {
      "questionId": 1,
      "correct": true,
      "userAnswer": 7,
      "correctAnswer": 7,
      "timeMs": 4200,
      "attempts": 1,
      "sawHint": false,
      "sawTopic": false
    }
  ],
  "summaryByType": {
    "toplama": { "total": 20, "correct": 18, "avgTimeMs": 3100 },
    "cikarma": { "total": 15, "correct": 10, "avgTimeMs": 4200 }
  },
  "summaryByDifficulty": {
    "1": { "total": 25, "correct": 22, "avgTimeMs": 2800 },
    "2": { "total": 20, "correct": 11, "avgTimeMs": 4500 },
    "3": { "total": 5, "correct": 2, "avgTimeMs": 6200 }
  }
}
```

`sawHint`: Çocuk ipucuna baktı mı? `sawTopic`: Konu anlatımını açtı mı?
Bu veriler hangi konuların anlaşılmadığını gösterir.

---

## Zorluk Ayarlama Kuralları

### Çocuk Dostu Prensipler
- **Teşvik edici olmalı** — çoğu soruyu çözebilmeli, kendini başarılı hissetmeli
- Hedef başarı oranı **%65-80** — ne çok kolay ne çok zor
- Çocuk zorlanıyorsa → zorluk düşür, cesaretini kırma
- Çocuk kolayca geçiyorsa → yavaşça artır, hızlı atlama yapma

### Zorluk Geçiş Kuralları

| Durum | Aksiyon |
|-------|---------|
| Tip başarısı **≥ %85** ve ortalama süre **< 8sn** | O tipte zorluk **+1** artır |
| Tip başarısı **%60-85** | Zorluk **aynı** kalsın (ideal bölge) |
| Tip başarısı **%40-60** | Zorluk **-1** düşür, o tipten daha fazla soru ver |
| Tip başarısı **< %40** | Zorluk **1'e** düşür, konu anlatımını detaylandır |
| Tüm tiplerde başarı **≥ %80** | Yeni soru tipi tanıt (örn: çarpma başlat) |
| `sawTopic` oranı **> %50** olan tip var | O tip hâlâ zor anlaşılıyor, zorluk artırma |

### Yeni Tip Tanıtma Sırası
2. sınıf müfredatına göre kademeli tanıtım:

1. **Başla:** toplama + cikarma (difficulty 1)
2. toplama/çıkarmada başarı **≥ %75** olunca → `carpma` ekle (×2 ile başla)
3. çarpmada başarı **≥ %70** olunca → `bolme` ekle (÷2 ile başla)
4. Temel dört işlemde başarı **≥ %70** olunca → `siralama` ekle
5. Tümünde başarı **≥ %70** olunca → `eksik_sayi` ekle

**Asla yapılmaması gerekenler:**
- Çocuğun hiç görmediği bir tipi direkt zorluk 3+ ile tanıtma
- Bir sette 3'ten fazla yeni tip tanıtma
- Zorluk 5'i çocuk zorluk 3-4'te %80+ başarı yakalamadan verme

### Soru Dağılımı Hesaplama

Her sette **50 soru**. Dağılım:

1. **Zayıf alanlar** (başarı <%50): Soruların **%40'ı** (20 soru) — kolay zorluk (1-2)
2. **Orta alanlar** (başarı %50-80): Soruların **%35'i** (17-18 soru) — mevcut zorluk
3. **Güçlü alanlar** (başarı >%80): Soruların **%25'i** (12-13 soru) — zorluk artırılmış

Soru sıralaması: **Karışık ama kolayla başla.** İlk 5 soru kolay olsun (çocuğun morali yükselsin), sonra karışık zorlukta devam etsin. Son 5 soru orta zorlukta olsun (bitirme hissi).

---

## Çıktı Gereksinimleri

1. **Geçerli JSON** — trailing comma yok, UTF-8 encoding
2. **Tam 50 soru** — ne eksik ne fazla
3. Her sorunun `answer` alanı **doğru hesaplanmış** — matematik hatasız
4. **Tekrar eden soru yok** — aynı text iki kez kullanılmamalı
5. `hint` alanları **çocuk dili ile Türkçe**, cevabı vermesin ama yol göstersin
6. `text` operatör sembolleri: `+`, `-`, `×`, `÷`, `=`
7. `version` = mevcut version + 1
8. `adjustmentReason` Türkçe, 1 cümle
9. `answer` her zaman **≥ 0** (negatif sonuç olmaz)
10. `topics.json` güncellenmişse geçerli JSON olmalı

## Analiz Çıktısı (stdout)

```
📊 MathLock AI — 2. Sınıf Matematik Raporu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Önceki set: v{eski} | Başarı: %{oran} | Toplam süre: {gün} gün
👍 Güçlü: {tipler}
👎 Zayıf: {tipler}
📈 Zorluk: {eski_ort:.1f} → {yeni_ort:.1f}
🆕 Yeni tanıtılan: {varsa tip adı, yoksa "—"}
📝 Konu anlatımı güncellendi: {tipler veya "—"}
📦 Yeni set: v{yeni} | {kısa dağılım}
```

## Dikkat — Dokunulacak Dosyalar

- ✅ `data/questions.json` — yeni sorular buraya yazılır
- ✅ `data/topics.json` — konu anlatımları buraya yazılır
- ❌ Başka hiçbir dosyaya dokunma (Android kodu, deploy.sh, AGENTS.md vb.)

## Doğrulama

Agent işini bitirdikten sonra `validate-questions.py` otomatik çalıştırılır.
Bu script şunları kontrol eder:
- JSON geçerliliği
- Tam 50 soru var mı
- Tüm alanlar doğru tipte mi
- Matematik cevapları doğru mu
- Tekrar eden soru var mı
- Zorluk seviyeleri 1-5 arasında mı
- topics.json'da tüm question tipleri var mı

Doğrulama başarısız olursa agent tekrar çalıştırılır.