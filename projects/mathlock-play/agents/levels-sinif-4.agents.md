# Sayı Yolculuğu — AI Seviye Üretim Kuralları (4. Sınıf, 9-10 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye verilir.
> **4. sınıf (9-10 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **9-10 yaşındaki 4. sınıf çocukları** için pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- 3. sınıftan gelen, tüm oyun mekaniğini biliyor
- Dört işlem akıcı, çarpma tablosunu biliyor
- Soyut düşünme gelişiyor, 10+ adım planlayabiliyor
- Optimizasyon merakı var ("en az komutla bitireyim")
- Her seviye **3-7 dakikada** bitebilmeli

Hedef: **Karmaşık algoritmik düşünme**, **çok adımlı optimizasyon** ve **matematiksel strateji** geliştirmek.

---

## §2 — Yaş Grubuna Özgü Kısıtlamalar (KRİTİK)

| Parametre | 4. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 4×4, Max: 7×7 |
| Komutlar | `x+`, `x-`, `y+`, `y-`, `z+`, `z-` (tüm 6 komut) |
| Duvar sayısı | 3-12 |
| Operasyon | `+N`, `-N`, `×N` (tüm türler) |
| `targetVal` | **Her seviyede zorunlu** |
| `startVal` aralığı | 1-30 |
| `maxCmds` | 8-18 |
| Optimum çözüm | 6-14 adım |
| `fingerprint` | Her seviyede zorunlu |

### Operasyon Değer Aralıkları

- `+N`: N = 1-15
- `-N`: N = 1-10 (dikkat: sonuç ≥1 olmalı, hiçbir zaman negatif)
- `×N`: N = 2-5 (çarpma zorlayıcı ama çözülebilir)
- `÷` operasyonu — YASAK

### Çoklu Operasyon Kullanımı

4. sınıf seviyelerinde zincirleme operasyon olabilir:
- Aynı yolda 2 operasyon hücresi geçilebilir
- Ancak ara değerler de negatif olmamalı

---

## §3 — Komutlar

| Komut | Açıklama |
|-------|----------|
| `x+`  | sağa     |
| `x-`  | sola     |
| `y+`  | aşağı    |
| `y-`  | yukarı   |
| `z+`  | değer +1 |
| `z-`  | değer -1 |

---

## §4 — Komut Semantiği (KRİTİK)

Hareket komutu:
- grid dışına çıkamaz
- duvardan geçemez

Invalid move:
- komutu TÜKETİR
- oyuncu yerinde kalır

`z+` / `z-`:
- konum değiştirmez
- sadece değeri değiştirir

---

## §5 — Operation Türleri ve Sınırlar

### +N
- N = 1-15

### -N
- N = 1-10
- sonuç ≥1 olmalı
- hiçbir zaman negatif

### ×N
- N = 2-5
- sonuç ≤ 500 olmalı

### ÷
- **YASAK**

---

## §6 — Adaptif Difficulty

### 6.1 Performans Analizi (`level-stats.json` varsa)

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤1.5 deneme | 7×7 grid, ×N/+N kombinasyonu, 12+ adım çözüm |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Grid büyüt, duvar artır, zincirleme operasyon |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, farklı operasyon türleri |
| ZORLU | ≥3/12 tamamlandı | Duvar azalt, grid küçült (4×4), ×N kaldır |
| KRİTİK | <3/12 tamamlandı | 4×4, 3-5 duvar, sadece +N/-N, kısa çözüm |

### 6.2 Seviye Dağılımı (12 seviye)
**Kural:** `lastSetEndDifficulty` varsa (önceki set tamamlanmışsa), yeni setin ilk seviyeleri önceki setin son zorluğundan başlar. Başa sarma (reset) yok.


| Grup | Adet | Grid | Özellik |
|------|------|------|---------|
| A (Isınma) | 2 | 4×4 - 5×4 | 3-5 duvar, +N/-N operasyon, 6-8 adım |
| B (Gelişim) | 5 | 5×5 - 6×5 | 6-9 duvar, +N/-N/×N, 8-11 adım |
| C (Zorlaşma) | 4 | 6×6 - 7×7 | 9-12 duvar, tüm operasyonlar, 11-14 adım |
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

State: `(x, y, value)`

### 7.2 Doğrulanması Gerekenler

- **Yol:** Başlangıçtan hedefe duvarlardan kaçınarak ulaşılabilir
- **Değer:** `targetVal` **her seviyede** var ve ulaşılabilir olmalı
- **maxCmds:** Optimal çözüm ≤ maxCmds olmalı
- **stars:**
  - `stars[0]` = optimum BFS çözüm uzunluğu (validate script hesaplar)
  - `stars[1]` = optimal + 3-5 adım (geniş tolerans)
- **Grid:** `cols × rows <= 49` (max 7×7)
- **Negatif değer:** Operasyonlar ASLA negatif veya sıfır sonuç üretmemeli (ara değerler de dahil)
- **×N sonucu:** ≤ 500 olmalı
- **Birden fazla çözüm yolu:** Olabilir (bu avantaj — yaratıcılığı teşvik eder)

---

## §8 — Gameplay Variety (KRİTİK)

Aynı hissi veren seviyeler üretme. Sadece title değiştirmek yeterli değildir.

### 8.1 Semantic Variety

Şunlar farklı olmalıdır:
- path shape
- wall topology
- arithmetic dependency
- decision count
- backtracking need
- solution rhythm

### 8.2 Cognitive Variety

Farklı seviyeler farklı düşünme biçimleri istemelidir:
- corridor navigation
- arithmetic timing
- trap avoidance
- revisit planning
- shortest-route optimization
- multi-step value planning

---

## §9 — previousSets Kuralları (KRİTİK)

`previousSets` varsa aşağıdakiler **yasaktır**:

1. **Aynı title** — `previousSets[].titles` içindeki herhangi bir title tekrar edilemez
2. **Aynı gameplay hissi** — `previousSets[]` içindeki seviyelerle "aynı hissi veren" seviye üretilemez
3. **Aynı fingerprint** — `previousSets[].mechanics` içindeki mekanik parmak izi tekrar edilemez
4. **Aynı çözüm yapısı** — `previousSets[]` içindeki seviyelerle aynı komut dizisi + grid boyutu tekrar edilemez

**Örnek:** Önceki sette "Sağa Git" (`x+`, 3×1 grid, duvar yok, ops yok) varsa, yeni sette "İleri Adım" (`x+`, 3×1 grid, duvar yok, ops yok) yapma. Farklı grid şekli, duvar veya operasyon ekle.

---

## §10 — JSON Şeması

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
      "stars": [8, 11],
      "fingerprint": {
        "grid": "5x5",
        "pathShape": "diagonal",
        "branching": "high",
        "backtracking": false,
        "valuePlanning": true,
        "wallTopology": "maze",
        "ops": 2
      }
    }
  ]
}
```

---

## §11 — Yasaklar

1. `÷` operasyonu — YASAK
2. `targetVal` boş/null — YASAK (her seviyede zorunlu)
3. Grid 7×7 üstü — YASAK
4. Herhangi bir durumda değer negatif veya sıfır — YASAK
5. `×N` için N > 5 — YASAK
6. `+N` için N > 15 — YASAK
7. Duvarı başlangıç veya hedef noktaya koyma
8. Operasyonu başlangıç noktasına koyma
9. JSON dışında metin yazma
10. Çıktı SADECE valid JSON olmalıdır
12. `fingerprint` alanı eksik olmamalıdır

---

## §12 — previousSets Dokümantasyonu

`level-stats.json` içinde `previousSets` (varsa) şu yapıdadır:

```json
{
  "previousSets": [
    {
      "version": 1,
      "titles": ["İlk Adım", "Aşağı İn", ...],
      "mechanics": ["cmds=x+,y+|grid=5x5|ops=yes|walls=yes", ...]
    }
  ]
}
```

Yeni set üretirken bu title ve mekanikleri ASLA tekrar etme.

---

## §13 — Örnek Çıktı (9-10 yaş, ilk 2 seviye)

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "9-10",
  "difficultyProfile": {
    "overall": "intermediate",
    "avgDifficulty": 3.5,
    "adjustmentReason": "4. sınıf. Tüm operasyon türleri ve optimizasyon stratejileri."
  },
  "levels": [
    {
      "id": 1, "title": "Çarpma Kapısı", "desc": "Çarpma hücresinden geçerek hedefe ulaş!",
      "difficulty": 3, "cols": 5, "rows": 5,
      "startX": 0, "startY": 0, "startVal": 3,
      "targetX": 4, "targetY": 4, "targetVal": 24,
      "walls": [[1,0],[2,2],[3,1]],
      "ops": [{"x":2,"y":0,"type":"×","val":2},{"x":3,"y":3,"type":"+","val":6}],
      "commands": ["x+", "x-", "y+", "y-", "z+", "z-"],
      "maxCmds": 12, "stars": [8, 10],
      "fingerprint": {
        "grid": "5x5", "pathShape": "diagonal", "branching": "medium",
        "backtracking": false, "valuePlanning": true,
        "wallTopology": "scattered", "ops": 2
      }
    },
    {
      "id": 2, "title": "Eksilme Yolu", "desc": "Eksilme hücrelerini stratejik kullan!",
      "difficulty": 4, "cols": 6, "rows": 6,
      "startX": 0, "startY": 0, "startVal": 20,
      "targetX": 5, "targetY": 5, "targetVal": 10,
      "walls": [[1,1],[2,3],[3,2],[4,4]],
      "ops": [{"x":1,"y":0,"type":"-","val":5},{"x":4,"y":1,"type":"+","val":3}],
      "commands": ["x+", "x-", "y+", "y-", "z+", "z-"],
      "maxCmds": 14, "stars": [8, 11],
      "fingerprint": {
        "grid": "6x6", "pathShape": "zigzag", "branching": "high",
        "backtracking": false, "valuePlanning": true,
        "wallTopology": "scattered", "ops": 2
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
