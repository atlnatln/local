# Sayı Yolculuğu — AI Seviye Üretim Kuralları (1. Sınıf, 6-7 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye (kimi-for-coding) verilir.
> **1. sınıf (6-7 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **6-7 yaşındaki 1. sınıf çocukları** için
pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- Yön kavramını kavramış (sağ, sol, yukarı, aşağı)
- 1-20 arası sayıları tanıyor, basit toplama yapabiliyor
- Dikkat süresi artıyor ama hâlâ kısa (10-15 dakika)
- Önceki setlerin üstüne kurulacak yeni mekanikler
- Her seviye **1-3 dakikada** bitebilmeli

Hedef: **2 boyutlu hareket**, **basit planlama** ve **yön-konum** ilişkisini geliştirmek.

---

## §2 — Görev Adımları

1. `level-stats.json` dosyasını oku (varsa). Çocuğun performansını analiz et.
2. `levels.json` dosyasını oku (varsa). Mevcut versiyon numarasını al.
3. §4 Adaptif Algoritma'yı uygula.
4. **12 yeni seviye** üret (§6 şemasına uygun).
5. Çıktı olarak **SADECE** yeni `levels.json` içeriğini yaz. Başka metin yazma.

---

## §3 — Yaş Grubuna Özgü Parametreler

| Parametre | 1. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 2×2, Max: 4×4 |
| Komutlar | `x+`, `x-`, `y+`, `y-` (4 yön) |
| z±1 komutu | **YASAK** — sayı değişimi bu sınıfta yok |
| Duvar sayısı | 0-4 (zorluk arttıkça) |
| Operasyon (+N, ×N) | **YASAK** |
| targetVal | **YASAK** — sadece konum hedefi |
| startVal aralığı | 1-15 |
| maxCmds | En fazla 8 |
| Optimum çözüm | 2-6 adım |

---

## §4 — Adaptif Algoritma

### 4.1 Performans Analizi (level-stats.json varsa)

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤2 deneme | Grid büyüt (4×4), duvar +1, daha uzun çözüm yolu |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Aynı zorluk, 1-2 duvar ekle |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, kolay oranı artır |
| ZORLU | ≥3/12 tamamlandı | Grid küçült (2×3), duvar azalt |
| KRİTİK | <3/12 tamamlandı | 2×2 veya 3×2, duvar yok, 3-4 adım |

### 4.2 Seviye Dağılımı (12 seviye)

| Grup | Adet | Açıklama |
|------|------|----------|
| A (Güven) | 5 | 2×2 veya 2×3 grid, 2-3 adım, duvar yok |
| B (Gelişim) | 4 | 3×3 grid, 3-5 adım, 0-2 duvar |
| C (Meydan Okuma) | 3 | 3×4 veya 4×4 grid, 4-6 adım, 2-4 duvar |

### 4.3 İlk Set (level-stats.json yoksa)

- version = 1, ageGroup = "6-7"
- difficultyProfile.overall = "beginner"
- Seviye 1-3: 2×2 grid, x+/y+ komutları, duvar yok, 2-3 adım
- Seviye 4-6: 2×3 veya 3×2 grid, x±/y± komutları, duvar yok
- Seviye 7-9: 3×3 grid, 4 komut, 1-2 duvar
- Seviye 10-12: 3×4 veya 4×3 grid, 4 komut, 2-3 duvar

### 4.4 Psikolojik Sıralama

- Seviye 1-2: 2 adım, basit (ileri-aşağı)
- Seviye 3-5: 3-4 adım, yön dönüşleri
- Seviye 6-8: 4-5 adım, duvar var, etrafından dolaş
- Seviye 9-10: 5-6 adım, daha geniş grid
- Seviye 11: 6 adım, meydan okuma
- Seviye 12: 3-4 adım, kolay bitiriş

---

## §5 — Çözülebilirlik Kuralları

Her seviye **kesinlikle çözülebilir** olmalıdır:

1. Başlangıçtan hedefe duvarlardan kaçınarak BFS ile ulaşılabilir yol var mı?
2. Optimum çözüm ≤ stars[0] ≤ stars[1] ≤ maxCmds
3. stars[0] = optimum çözüm adım sayısı
4. stars[1] = optimum + 2-3 adım
5. maxCmds = stars[1] + 2 ek adım
6. Duvarlar başlangıç veya hedefi kapatmamalı
7. targetVal null olmalı (bu sınıfta sayı değişimi yok)

---

## §6 — levels.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "6-7",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.5,
    "adjustmentReason": "Türkçe açıklama"
  },
  "levels": [
    {
      "id": 1,
      "title": "Kısa başlık (2-4 kelime)",
      "desc": "Ne yapılacağını anlatan 1 cümle",
      "difficulty": 1,
      "cols": 2,
      "rows": 2,
      "startX": 0,
      "startY": 0,
      "startVal": 5,
      "targetX": 1,
      "targetY": 1,
      "targetVal": null,
      "walls": [],
      "ops": [],
      "commands": ["x+", "y+"],
      "maxCmds": 5,
      "stars": [2, 3]
    }
  ]
}
```

---

## §7 — Yasaklar

1. z±1 komutu — YASAK
2. targetVal (sayı hedefi) — YASAK
3. Operasyon hücreleri (+N, -N, ×N) — YASAK
4. Grid 4×4 üstü — YASAK
5. 8 komut üstü maxCmds — YASAK
6. Duvarı başlangıç veya hedef noktaya koyma
7. Seviye 1-3'te duvar kullanma
8. JSON dışında metin yazma

---

## §8 — Örnek Çıktı (6-7 yaş, ilk 2 seviye)

```json
{
  "version": 1,
  "generatedAt": "2026-04-22T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "6-7",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.5,
    "adjustmentReason": "İlk set. 2 boyutlu hareket tanıtılıyor."
  },
  "levels": [
    {
      "id": 1, "title": "Köşeye Git", "desc": "Sayıyı sağa sonra aşağı götür!",
      "difficulty": 1, "cols": 2, "rows": 2,
      "startX": 0, "startY": 0, "startVal": 3,
      "targetX": 1, "targetY": 1, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+", "y+"], "maxCmds": 5, "stars": [2, 3]
    },
    {
      "id": 2, "title": "Uzak Köşe", "desc": "En uzak köşeye ulaş!",
      "difficulty": 1, "cols": 3, "rows": 2,
      "startX": 0, "startY": 0, "startVal": 7,
      "targetX": 2, "targetY": 1, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+", "y+"], "maxCmds": 6, "stars": [3, 4]
    }
  ]
}
```

*Not: Gerçek çıktıda 12 seviye olmalı.*
