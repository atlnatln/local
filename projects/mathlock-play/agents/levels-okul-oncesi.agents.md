# Sayı Yolculuğu — AI Seviye Üretim Kuralları (Okul Öncesi, 5-6 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye (kimi-for-coding) verilir.
> **Okul öncesi (5-6 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **5-6 yaşındaki çocuklar** için
basit, eğlenceli ve pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- Dikkat süresi kısa (5-10 dakika maksimum)
- Yönlü hareket kavramını yeni öğreniyor (sağ, sol, aşağı)
- Sayıları anlıyor ama işlem yapamıyor (toplama en fazla somut olarak)
- Başarı hissi ve hızlı geri bildirim kritik
- Her seviye **30 saniye - 2 dakikada** bitebilmeli

Hedef: Çocuğun **yön kavramı**, **sıralama mantığı** ve **dikkat** becerilerini oyunla geliştirmek.

---

## §2 — Görev Adımları

1. `level-stats.json` dosyasını oku (varsa). Çocuğun performansını analiz et.
2. `levels.json` dosyasını oku (varsa). Mevcut versiyon numarasını al.
3. §4 Adaptif Algoritma'yı uygula.
4. **12 yeni seviye** üret (§6 şemasına uygun).
5. Çıktı olarak **SADECE** yeni `levels.json` içeriğini yaz. Başka metin yazma.

---

## §3 — Yaş Grubuna Özgü Kısıtlamalar (KRİTİK)

| Parametre | Okul Öncesi Kuralı |
|-----------|-------------------|
| Grid boyutu | Min: 1×2, Max: 3×3 |
| Komutlar | SADECE `x+`, `x-`, `y+` (sağa, sola, aşağı — 3 komut yeterli) |
| z±1 komutu | **YASAK** — değer değişimi bu yaşta yok |
| Duvar sayısı | İlk 6 seviye: 0, Son 6 seviye: en fazla 2 |
| Operasyon (+N, ×N) | **YASAK** |
| targetVal | **YASAK** — sadece konum hedefi |
| startVal aralığı | 1-9 (tek basamaklı, tanıdık sayılar) |
| maxCmds | En fazla 6 (kısa tuş dizisi) |
| Seviye süresi | Optimum çözüm ≤ 4 komut (ilk 8 seviye) |

### Komut Tanımları (Çocuk için basit)
- `x+` → Sağa git (→)
- `x-` → Sola git (←)
- `y+` → Aşağı git (↓)
- `y-` → Yukarı git (↑) — sadece son 3 seviyede kullan

---

## §4 — Adaptif Algoritma

### 4.1 Performans Analizi (level-stats.json varsa)

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız | Grid biraz büyüt (max 3×3), y- ekle son 2 seviyeye |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Aynı zorluk, 1-2 duvar ekle son 3 seviyeye |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, kolay seviye oranı artır |
| ZORLU | ≥3/12 tamamlandı | Grid küçült (1×3 veya 2×2), duvar sıfırla |
| KRİTİK | <3/12 tamamlandı | En basit: 1×3 grid, sadece x+, 2-3 adım |

### 4.2 Seviye Dağılımı (12 seviye)

| Grup | Adet | Açıklama |
|------|------|----------|
| A (Güven) | 5 | 1×2 veya 1×3 grid, tek komut (x+ veya y+), duvar yok |
| B (Gelişim) | 4 | 2×2 veya 2×3 grid, iki komut (x+ ve y+), 0-1 duvar |
| C (Meydan Okuma) | 3 | 3×3 grid, üç komut (x+, x-, y+), 0-2 duvar |

### 4.3 İlk Set (level-stats.json yoksa)

- version = 1, ageGroup = "5-6"
- difficultyProfile.overall = "beginner"
- Seviye 1-4: 1×3 veya 3×1 grid, tek komut, duvar yok, 2-3 adım
- Seviye 5-8: 2×2 veya 2×3 grid, iki komut (x+ ve y+), duvar yok
- Seviye 9-10: 3×3 grid, iki komut, 1 duvar
- Seviye 11-12: 3×3 grid, üç komut (x+, x-, y+), 1-2 duvar

### 4.4 Psikolojik Sıralama

- Seviye 1-2: 1 adımda biten — "Yaptım!" hissi
- Seviye 3-5: 2-3 adım, doğrusal
- Seviye 6-8: 3-4 adım, basit dönüş
- Seviye 9-10: 4-5 adım, küçük bulmaca
- Seviye 11: 5-6 adım, meydan okuma
- Seviye 12: 3-4 adım, kolay bitiriş (zafer hissi)

---

## §5 — Çözülebilirlik Kuralları

Her seviye **kesinlikle çözülebilir** olmalıdır:

1. Başlangıçtan hedefe duvarlardan kaçınarak ulaşılabilir yol var mı?
2. Optimum çözüm ≤ maxCmds mi?
3. stars[0] = optimum çözüm adım sayısı
4. stars[1] = optimum + 1-2 adım
5. maxCmds = stars[1] + 1-2 ek adım
6. Duvarlar başlangıç veya hedefi kapatmamalı
7. targetVal bu yaşta null olmalı

### Örnek BFS (1×3 grid, x+ komutu)
```
Başlangıç: x=0, hedef: x=2
Adımlar: x+, x+  → optimum=2
stars=[2, 3], maxCmds=4
```

---

## §6 — levels.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "5-6",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.2,
    "adjustmentReason": "Türkçe açıklama"
  },
  "levels": [
    {
      "id": 1,
      "title": "Kısa başlık (2-3 kelime)",
      "desc": "Sayıyı hedefe götür!",
      "difficulty": 1,
      "cols": 3,
      "rows": 1,
      "startX": 0,
      "startY": 0,
      "startVal": 3,
      "targetX": 2,
      "targetY": 0,
      "targetVal": null,
      "walls": [],
      "ops": [],
      "commands": ["x+"],
      "maxCmds": 4,
      "stars": [2, 3]
    }
  ]
}
```

---

## §7 — level-stats.json Şeması (Sadece Okuma)

```json
{
  "levelVersion": 1,
  "ageGroup": "5-6",
  "completedAt": 1712900000,
  "totalLevels": 12,
  "totalCompleted": 8,
  "totalStars": 18,
  "byLevel": [
    {
      "levelId": 1,
      "completed": true,
      "stars": 3,
      "commandsUsed": 2,
      "attempts": 1,
      "timeSeconds": 8
    }
  ]
}
```

---

## §8 — Yasaklar

1. z±1 komutu — YASAK
2. targetVal (sayı hedefi) — YASAK
3. Operasyon hücreleri (+N, ×N) — YASAK
4. Grid 3×3 üstü — YASAK
5. 6 komut üstü maxCmds — YASAK
6. Duvarı başlangıç veya hedef noktaya koyma
7. Seviye 1-6'da duvar kullanma
8. JSON dışında metin yazma

---

## §9 — Örnek Çıktı (5-6 yaş, version 1, ilk 3 seviye)

```json
{
  "version": 1,
  "generatedAt": "2026-04-22T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "5-6",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.3,
    "adjustmentReason": "İlk set. Tek yönlü hareketle başlangıç."
  },
  "levels": [
    {
      "id": 1, "title": "İlk Adım", "desc": "Sayıyı sağa götür!",
      "difficulty": 1, "cols": 3, "rows": 1,
      "startX": 0, "startY": 0, "startVal": 2,
      "targetX": 2, "targetY": 0, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+"], "maxCmds": 4, "stars": [2, 3]
    },
    {
      "id": 2, "title": "Aşağı Bak", "desc": "Sayıyı aşağı indir!",
      "difficulty": 1, "cols": 1, "rows": 3,
      "startX": 0, "startY": 0, "startVal": 4,
      "targetX": 0, "targetY": 2, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["y+"], "maxCmds": 4, "stars": [2, 3]
    },
    {
      "id": 3, "title": "Kısa Yol", "desc": "Sağa git, sonra aşağı!",
      "difficulty": 1, "cols": 2, "rows": 2,
      "startX": 0, "startY": 0, "startVal": 1,
      "targetX": 1, "targetY": 1, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+", "y+"], "maxCmds": 4, "stars": [2, 3]
    }
  ]
}
```

*Not: Gerçek çıktıda 12 seviye olmalı.*
