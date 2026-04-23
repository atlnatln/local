# Sayı Yolculuğu — AI Seviye Üretim Kuralları (4. Sınıf, 9-10 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye (kimi-for-coding) verilir.
> **4. sınıf (9-10 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **9-10 yaşındaki 4. sınıf çocukları** için
pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- 3. sınıftan gelen, tüm oyun mekaniğini biliyor
- Dört işlem akıcı, çarpma tablosunu biliyor
- Soyut düşünme gelişiyor, 10+ adım planlayabiliyor
- Optimizasyon merakı var ("en az komutla bitireyim")
- Her seviye **3-7 dakikada** bitebilmeli

Hedef: **Karmaşık algoritmik düşünme**, **çok adımlı optimizasyon** ve **matematiksel strateji** geliştirmek.

---

## §2 — Görev Adımları

1. `level-stats.json` dosyasını oku (varsa). Çocuğun performansını analiz et.
2. `levels.json` dosyasını oku (varsa). Mevcut versiyon numarasını al.
3. §4 Adaptif Algoritma'yı uygula.
4. **12 yeni seviye** üret (§6 şemasına uygun).
5. Çıktı olarak **SADECE** yeni `levels.json` içeriğini yaz. Başka metin yazma.

---

## §3 — Yaş Grubuna Özgü Parametreler

| Parametre | 4. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 4×4, Max: 7×7 |
| Komutlar | `x+`, `x-`, `y+`, `y-`, `z+`, `z-` (tüm 6 komut) |
| Duvar sayısı | 3-12 |
| Operasyon | `+N`, `-N`, `×N` (tüm türler) |
| targetVal | **Her seviyede zorunlu** |
| startVal aralığı | 1-30 |
| maxCmds | 8-18 |
| Optimum çözüm | 6-14 adım |

### Operasyon Değer Aralıkları
- `+N`: N = 1-15
- `-N`: N = 1-10 (dikkat: sonuç ≥1 olmalı, hiçbir zaman negatif)
- `×N`: N = 2-5 (çarpma zorlayıcı ama çözülebilir)
- `÷` operasyonu — YASAK (uygulama desteklemiyor)

### Çoklu Operasyon Kullanımı
4. sınıf seviyelerinde zincirleme operasyon olabilir:
- Aynı yolda 2 operasyon hücresi geçilebilir
- Ancak ara değerler de negatif olmamalı

---

## §4 — Adaptif Algoritma

### 4.1 Performans Analizi (level-stats.json varsa)

Her seviye için: `completed`, `stars`, `attempts`, `commandsUsed`, `timeSeconds`

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤1.5 deneme | 7×7 grid, ×N/+N kombinasyonu, 12+ adım çözüm |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Grid büyüt, duvar artır, zincirleme operasyon |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, farklı operasyon türleri |
| ZORLU | ≥3/12 tamamlandı | Duvar azalt, grid küçült (4×4), ×N kaldır |
| KRİTİK | <3/12 tamamlandı | 4×4, 3-5 duvar, sadece +N/-N, kısa çözüm |

### 4.2 Seviye Dağılımı (12 seviye)

| Grup | Adet | Grid | Özellik |
|------|------|------|---------|
| A (Güven) | 3 | 4×4 - 5×4 | 3-5 duvar, +N/-N operasyon, 6-8 adım |
| B (Gelişim) | 5 | 5×5 - 6×5 | 6-9 duvar, +N/-N/×N, 8-11 adım |
| C (Meydan Okuma) | 4 | 6×6 - 7×7 | 9-12 duvar, tüm operasyonlar, 11-14 adım |

### 4.3 İlk Set (level-stats.json yoksa)

- version = 1, ageGroup = "9-10"
- difficultyProfile.overall = "intermediate"
- Seviye 1-3: 4×4 grid, 3-5 duvar, +N/-N, targetVal var, 6-8 adım
- Seviye 4-6: 5×5 grid, 5-7 duvar, +N/-N, targetVal var, 8-10 adım
- Seviye 7-9: 5×5 veya 6×5 grid, 6-9 duvar, +N/-N/×N, 9-12 adım
- Seviye 10-11: 6×6 veya 7×6, 9-12 duvar, tüm operasyonlar, 12-14 adım
- Seviye 12: 5×5, 6-8 adım, orta zorluk bitiriş

### 4.4 Psikolojik Sıralama

- Seviye 1-2: Tanıdık mekanik, kısa çözüm, güven taze tut
- Seviye 3-5: -N operasyonu tanıtılır veya pekiştirilir, orta zorluk
- Seviye 6-8: ×N operasyonu zorunlu olan yollar, stratejik planlama
- Seviye 9-10: Çok duvarlı labirent, zincirleme operasyon
- Seviye 11: En karmaşık — büyük grid, her operasyon türü
- Seviye 12: Orta zorluk, tatmin edici kapanış

---

## §5 — Çözülebilirlik Kuralları

1. BFS ile başlangıçtan hedefe ulaşılabilir yol olmalı (durum: x, y, değer).
2. targetVal **her seviyede** var ve ulaşılabilir olmalı.
3. stars[0] = optimum çözüm adım sayısı
4. stars[1] = optimum + 3-5 adım (geniş tolerans)
5. maxCmds = stars[1] + 3-4 ek adım
6. Duvarlar başlangıç veya hedefi kapatmamalı
7. Operasyonlar ASLA negatif veya sıfır sonuç üretmemeli (ara değerler de dahil)
8. ×N sonucu ≤ 500 olmalı
9. Birden fazla çözüm yolu olabilir (bu avantaj — yaratıcılığı teşvik eder)

---

## §6 — levels.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "9-10",
  "difficultyProfile": {
    "overall": "intermediate",
    "avgDifficulty": 3.5,
    "adjustmentReason": "Türkçe açıklama"
  },
  "levels": [
    {
      "id": 1,
      "title": "Kısa başlık (2-4 kelime)",
      "desc": "Ne yapılacağını anlatan 1 cümle",
      "difficulty": 3,
      "cols": 5,
      "rows": 5,
      "startX": 0,
      "startY": 0,
      "startVal": 6,
      "targetX": 4,
      "targetY": 4,
      "targetVal": 24,
      "walls": [[1,0],[2,2],[3,1],[1,3]],
      "ops": [
        {"x": 2, "y": 0, "type": "×", "val": 2},
        {"x": 3, "y": 3, "type": "+", "val": 6}
      ],
      "commands": ["x+", "x-", "y+", "y-", "z+", "z-"],
      "maxCmds": 14,
      "stars": [8, 11]
    }
  ]
}
```

---

## §7 — Yasaklar

1. `÷` operasyonu — YASAK
2. targetVal boş/null — YASAK (her seviyede zorunlu)
3. Grid 7×7 üstü — YASAK
4. Herhangi bir durumda değer negatif veya sıfır — YASAK
5. ×N için N > 5 — YASAK
6. +N için N > 15 — YASAK
7. Duvarı başlangıç veya hedef noktaya koyma
8. Operasyonu başlangıç noktasına koyma
9. JSON dışında metin yazma
