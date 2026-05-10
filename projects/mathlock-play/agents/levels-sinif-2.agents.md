# Sayı Yolculuğu — AI Seviye Üretim Kuralları (2. Sınıf, 7-8 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye verilir.
> **2. sınıf (7-8 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici bulmaca oyunu tasarımcısısın. **Sayı Yolculuğu** oyunu için 7-8 yaş arası çocuklara uygun, adaptif zorlukta **12 seviye** üreteceksin.

Oyun mantığı:
- Bir ızgara (grid) üzerinde bir **sayı** (player) başlangıç noktasında durur.
- Çocuk **komut dizisi** programlar: `x+` (sağa), `x-` (sola), `y+` (aşağı), `y-` (yukarı), `z+` (değer +1), `z-` (değer -1).
- Komutlar sırayla çalıştırılır. Sayı ızgarada hareket eder.
- Bazı hücreler **duvar** (geçilmez), bazıları **operasyon** (+N, -N, ×N — sayının değerini değiştirir).
- Amaç: sayıyı **hedef hücreye** taşımak, varsa **hedef değere** ulaşmak.
- En az komutla çözüm = ⭐⭐⭐ (3 yıldız).

Hedef: çocuğun **algoritmik düşünme**, **planlama** ve **matematik** becerilerini geliştirmek.

---

## §2 — Yaş Grubuna Özgü Kısıtlamalar (KRİTİK)

| Parametre | 2. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 3×3, Max: 5×5 |
| Komutlar | `x+`, `x-`, `y+`, `y-`, `z+`, `z-` (tüm 6 komut) |
| Duvar sayısı | 1-5 (zorluk arttıkça) |
| Operasyon | `+N` (N = 1-5) |
| `targetVal` | null veya 1-20 |
| `startVal` aralığı | 1-15 |
| `maxCmds` | 6-14 |
| Optimum çözüm | 4-10 adım |
| `fingerprint` | Her seviyede zorunlu |

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
- N = 1-5
- sonuç negatif OLMAMALI

### -N ve ×N
- **YASAK** (bu sınıfta yok)

---

## §6 — Adaptif Difficulty

### 6.1 Performans Analizi (`level-stats.json` varsa)

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤2 deneme | Zorluk +1 (grid büyüt, duvar/op ekle) |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Zorluk aynı, biraz çeşit artır |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Zorluk aynı, kolay seviye oranı artır |
| ZORLU | ≥3/12 tamamlandı | Zorluk -1 (grid küçült, duvar azalt) |
| KRİTİK | <3/12 tamamlandı | Zorluk -2, çok basit seviyeler üret |

### 6.2 Seviye Dağılımı (12 seviye)

**Kural:** `lastSetEndDifficulty` varsa (önceki set tamamlanmışsa), yeni setin ilk seviyeleri önceki setin son zorluğundan başlar. Başa sarma (reset) yok.

| Grup | Adet | Zorluk | Amaç |
|------|------|--------|------|
| A (Isınma) | 2 | `lastSetEndDifficulty - 1` veya `lastSetEndDifficulty` | Önceki setten devam, hafif ısınma |
| B (Gelişim) | 5 | `lastSetEndDifficulty` → `lastSetMaxDifficulty` | Öğrenme, pekiştirme |
| C (Zorlaşma) | 4 | `lastSetMaxDifficulty` ve üzeri | Zorluk artışı |
| D (Final) | 1 | Zirve zorluğu | En zor meydan okuma |

İlk set ise (`lastSetEndDifficulty` yok):
| Grup | Adet | Zorluk |
|------|------|--------|
| A (Güven) | 3 | Kolay |
| B (Gelişim) | 5 | Orta |
| C (Meydan Okuma) | 4 | Zor |

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
- **Değer:** `targetVal` belirtilmişse, komutları ve operasyonları kullanarak başlangıç değerinden hedef değere ulaşılabilmeli
- **maxCmds:** Optimal çözüm ≤ maxCmds olmalı
- **stars:**
  - `stars[0]` = optimum BFS çözüm uzunluğu (validate script hesaplar)
  - `stars[1]` = optimal + 2-4 adım
- **Grid:** `cols × rows <= 25` (max 5×5)
- **Negatif değer:** `z-` komutu sonucunda değer 0'ın altına düşmemeli

---

## §8 — Gameplay Variety (KRİTİK)

Aynı hissi veren seviyeler üretme. Sadece title değiştirmek yeterli değildir.

### 8.1 Semantic Variety

Şunlar farklı olmalıdır:
- path shape
- wall topology
- arithmetic dependency
- decision count
- solution rhythm

### 8.2 Cognitive Variety

Farklı seviyeler farklı düşünme biçimleri istemelidir:
- corridor navigation
- arithmetic timing
- wall avoidance
- forced turns
- shortest-route optimization

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
  "ageGroup": "7-8",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.5,
    "adjustmentReason": "Önceki set v{lastVersion} son zorluk={lastSetEndDifficulty}, max={lastSetMaxDifficulty}, ort={lastSetAvgDifficulty}. Set başına reset yok, devam et."
  },
  "levels": [
    {
      "id": 1,
      "title": "Kısa Türkçe başlık (2-4 kelime)",
      "desc": "Kısa Önceki set v{lastVersion} son zorluk={lastSetEndDifficulty}, max={lastSetMaxDifficulty}, ort={lastSetAvgDifficulty}. Set başına reset yok, devam et. (1 cümle)",
      "difficulty": 1,
      "cols": 3,
      "rows": 3,
      "startX": 0,
      "startY": 0,
      "startVal": 3,
      "targetX": 2,
      "targetY": 2,
      "targetVal": null,
      "walls": [[1, 1]],
      "ops": [{"x": 2, "y": 0, "type": "+", "val": 3}],
      "commands": ["x+", "y+"],
      "maxCmds": 6,
      "stars": [4, 5],
      "fingerprint": {
        "grid": "3x3",
        "pathShape": "L",
        "branching": "low",
        "backtracking": false,
        "valuePlanning": false,
        "wallTopology": "single-center",
        "ops": 1
      }
    }
  ]
}
```

---

## §11 — Yasaklar

1. Çözülemez seviye üretme
2. Negatif sayı kullanma (z- komutu sonucunda değer 0'ın altına düşmemeli)
3. Duvarı başlangıç veya hedef noktaya koyma
4. Operasyonu başlangıç noktasına koyma
5. Boş `maxCmds` verme (en az optimum+1)
6. Çok büyük grid yapma (max 5×5 = 25 hücre)
7. Aynı title veya desc kullanma — her seviye benzersiz olsun
8. `×0` veya `÷` operasyonu kullanma
9. JSON dışında metin yazma. Çıktı SADECE valid JSON olmalı
11. `fingerprint` alanı eksik olmamalıdır

---

## §12 — previousSets Dokümantasyonu

`level-stats.json` içinde `previousSets` (varsa) şu yapıdadır:

```json
{
  "previousSets": [
    {
      "version": 1,
      "titles": ["İlk Adım", "Aşağı İn", ...],
      "mechanics": ["cmds=x+,y+|grid=3x3|ops=yes|walls=yes", ...]
    }
  ]
}
```

- `titles`: Önceki setteki 12 seviyenin başlıkları
- `mechanics`: Önceki setteki her seviyenin mekanik parmak izi

Yeni set üretirken bu title ve mekanikleri ASLA tekrar etme.

---

## §13 — Örnek Çıktı (7-8 yaş, version 1, ilk 2 seviye)

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "7-8",
  "difficultyProfile": {
    "overall": "beginner",
    "avgDifficulty": 1.5,
    "adjustmentReason": "İlk set. Temel x/y hareketi ve basit z değişimleri ile tanıştırma."
  },
  "levels": [
    {
      "id": 1, "title": "İlk Adım", "desc": "Sayıyı sağa taşı!",
      "difficulty": 1, "cols": 3, "rows": 1,
      "startX": 0, "startY": 0, "startVal": 3,
      "targetX": 2, "targetY": 0, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+"],
      "maxCmds": 4, "stars": [2, 3],
      "fingerprint": {
        "grid": "3x1", "pathShape": "line", "branching": "none",
        "backtracking": false, "valuePlanning": false,
        "wallTopology": "none", "ops": 0
      }
    },
    {
      "id": 2, "title": "Aşağı İn", "desc": "Sayıyı aşağı götür!",
      "difficulty": 1, "cols": 1, "rows": 3,
      "startX": 0, "startY": 0, "startVal": 5,
      "targetX": 0, "targetY": 2, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["y+"],
      "maxCmds": 4, "stars": [2, 3],
      "fingerprint": {
        "grid": "1x3", "pathShape": "line", "branching": "none",
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
