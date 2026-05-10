# Sayı Yolculuğu — AI Seviye Üretim Kuralları (1. Sınıf, 6-7 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye verilir.
> **1. sınıf (6-7 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **6-7 yaşındaki 1. sınıf çocukları** için pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- Yön kavramını kavramış (sağ, sol, yukarı, aşağı)
- 1-20 arası sayıları tanıyor, basit toplama yapabiliyor
- Dikkat süresi artıyor ama hâlâ kısa (10-15 dakika)
- Önceki setlerin üstüne kurulacak yeni mekanikler
- Her seviye **1-3 dakikada** bitebilmeli

Hedef: **2 boyutlu hareket**, **basit planlama** ve **yön-konum** ilişkisini geliştirmek.

---

## §2 — Yaş Grubuna Özgü Kısıtlamalar (KRİTİK)

| Parametre | 1. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 2×2, Max: 4×4 |
| Komutlar | `x+`, `x-`, `y+`, `y-` (4 yön) |
| `z±1` komutu | **YASAK** — sayı değişimi bu sınıfta yok |
| Duvar sayısı | 0-4 (zorluk arttıkça) |
| Operasyon (+N, ×N) | **YASAK** |
| `targetVal` | **YASAK** — sadece konum hedefi |
| `startVal` aralığı | 1-15 |
| `maxCmds` | En fazla 8 |
| Optimum çözüm | 2-6 adım |
| `fingerprint` | Her seviyede zorunlu |

---

## §3 — Komutlar

| Komut | Açıklama |
|-------|----------|
| `x+`  | sağa     |
| `x-`  | sola     |
| `y+`  | aşağı    |
| `y-`  | yukarı   |

---

## §4 — Komut Semantiği (KRİTİK)

Hareket komutu:
- grid dışına çıkamaz
- duvardan geçemez

Invalid move:
- komutu TÜKETİR
- oyuncu yerinde kalır

Örnek: duvara yürümek → komut gider ama pozisyon değişmez

---

## §5 — Operation Türleri ve Sınırlar

Bu yaş grubunda **operasyon yoktur**.

`ops` dizisi her zaman `[]` olmalıdır.

---

## §6 — Adaptif Difficulty

### 6.1 Performans Analizi (`level-stats.json` varsa)

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤2 deneme | Grid büyüt (4×4), duvar +1, daha uzun çözüm yolu |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Aynı zorluk, 1-2 duvar ekle |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, kolay oranı artır |
| ZORLU | ≥3/12 tamamlandı | Grid küçült (2×3), duvar azalt |
| KRİTİK | <3/12 tamamlandı | 2×2 veya 3×2, duvar yok, 3-4 adım |

### 6.2 Seviye Dağılımı (12 seviye)
**Kural:** `lastSetEndDifficulty` varsa (önceki set tamamlanmışsa), yeni setin ilk seviyeleri önceki setin son zorluğundan başlar. Başa sarma (reset) yok.


| Grup | Adet | Açıklama |
|------|------|----------|
| A (Isınma) | 2 | 2×2 veya 2×3 grid, 2-3 adım, duvar yok |
| B (Gelişim) | 5 | 3×3 grid, 3-5 adım, 0-2 duvar |
| C (Zorlaşma) | 4 | 3×4 veya 4×4 grid, 4-6 adım, 2-4 duvar |
| D (Final) | 1 | Zirve zorluğu |



### 6.3 Psikolojik Pacing

| Seviye | Amaç |
|--------|------|
| 1-2 | Önceki setten devam — hafif ısınma, çok kolay değil |
| 3-7 | Orta zorluk — öğrenme bölgesi |
| 8-10 | Zorlaşma başlar |
| 11 | En zor meydan okuma |
| 12 | Zor-orta — başarıyla bitirme hissi |

---

## §7 — Çözülebilirlik Kuralları (KRİTİK)

Her seviye **kesinlikle çözülebilir** olmalıdır.

AI `solution` alanı YAZMAYACAK. Validate script BFS ile optimum çözümü bulup otomatik dolduracak. AI sadece grid, walls, ops, target, commands, maxCmds, stars üretsin.

### 7.1 BFS State Tanımı

State: `(x, y)`

Bu yaş grubunda `value` değişmez (z± yok, ops yok).

### 7.2 Doğrulanması Gerekenler

- **Yol:** Başlangıçtan hedefe ulaşılabilmeli
- **maxCmds:** Optimal çözüm ≤ maxCmds olmalı
- **stars:**
  - `stars[0]` = optimum BFS çözüm uzunluğu (validate script hesaplar)
  - `stars[1]` = optimal + 2-3 adım
- **Grid:** `cols × rows <= 16` (max 4×4)

---

## §8 — Gameplay Variety (KRİTİK)

Aynı hissi veren seviyeler üretme. Sadece title değiştirmek yeterli değildir.

### 8.1 Semantic Variety

Şunlar farklı olmalıdır:
- path shape
- grid boyutu
- duvar yerleşimi
- komut çeşidi

### 8.2 Cognitive Variety

Farklı seviyeler farklı düşünme biçimleri istemelidir:
- corridor navigation
- direction change
- wall avoidance
- shortest route planning

---

## §9 — previousSets Kuralları (KRİTİK)

`previousSets` varsa aşağıdakiler **yasaktır**:

1. **Aynı title** — `previousSets[].titles` içindeki herhangi bir title tekrar edilemez
2. **Aynı gameplay hissi** — `previousSets[]` içindeki seviyelerle "aynı hissi veren" seviye üretilemez
3. **Aynı fingerprint** — `previousSets[].mechanics` içindeki mekanik parmak izi tekrar edilemez
4. **Aynı çözüm yapısı** — `previousSets[]` içindeki seviyelerle aynı komut dizisi + grid boyutu tekrar edilemez

**Örnek:** Önceki sette "Köşeye Git" (`x+`, `y+`, 2×2 grid, duvar yok) varsa, yeni sette "Uzak Köşe" (`x+`, `y+`, 2×2 grid, duvar yok) yapma. Farklı grid boyutu veya duvar ekle.

---

## §10 — JSON Şeması

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
      "stars": [2, 3],
      "fingerprint": {
        "grid": "2x2",
        "pathShape": "L",
        "branching": "none",
        "backtracking": false,
        "valuePlanning": false,
        "wallTopology": "none",
        "ops": 0
      }
    }
  ]
}
```

---

## §11 — Yasaklar

1. `z±1` komutu — YASAK
2. `targetVal` (sayı hedefi) — YASAK
3. Operasyon hücreleri (+N, -N, ×N) — YASAK
4. Grid 4×4 üstü — YASAK
5. 8 komut üstü `maxCmds` — YASAK
6. Duvarı başlangıç veya hedef noktaya koyma
7. Seviye 1-3'te duvar kullanma
8. JSON dışında metin yazma
9. Çıktı SADECE valid JSON olmalıdır
11. `fingerprint` alanı eksik olmamalıdır

---

## §12 — previousSets Dokümantasyonu

`level-stats.json` içinde `previousSets` (varsa) şu yapıdadır:

```json
{
  "previousSets": [
    {
      "version": 1,
      "titles": ["Köşeye Git", "Uzak Köşe", ...],
      "mechanics": ["cmds=x+,y+|grid=2x2|ops=no|walls=no", ...]
    }
  ]
}
```

Yeni set üretirken bu title ve mekanikleri ASLA tekrar etme.

---

## §13 — Örnek Çıktı (6-7 yaş, ilk 2 seviye)

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
      "commands": ["x+", "y+"],
      "maxCmds": 5, "stars": [2, 3],
      "fingerprint": {
        "grid": "2x2", "pathShape": "L", "branching": "none",
        "backtracking": false, "valuePlanning": false,
        "wallTopology": "none", "ops": 0
      }
    },
    {
      "id": 2, "title": "Uzak Köşe", "desc": "En uzak köşeye ulaş!",
      "difficulty": 1, "cols": 3, "rows": 2,
      "startX": 0, "startY": 0, "startVal": 7,
      "targetX": 2, "targetY": 1, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+", "y+"],
      "maxCmds": 6, "stars": [3, 4],
      "fingerprint": {
        "grid": "3x2", "pathShape": "L", "branching": "none",
        "backtracking": false, "valuePlanning": false,
        "wallTopology": "none", "ops": 0
      }
    }
  ]
}
```

*Not: Gerçek çıktıda 12 seviye olmalı.*

## §17 — Üretim Talimatları (KRİTİK)

- Shell tool KULLANMA — sadece ReadFile ve WriteFile ile dosyaları oku/yaz
- Validation hatası alırsan mevcut dosyayı DÜZELTMEYE ÇALIŞMA
- Validation hatası olursa TAMAMEN YENİ 12 seviye üret
- Her seferinde tam 12 seviye, eksik veya fazla OLMAMALI
