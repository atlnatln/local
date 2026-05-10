# Sayı Yolculuğu — AI Seviye Üretim Kuralları (3. Sınıf, 8-9 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye verilir.
> **3. sınıf (8-9 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **8-9 yaşındaki 3. sınıf çocukları** için pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- 2 boyutlu hareketi ve z± komutunu kavramış (2. sınıftan geliyor)
- 4 işlem biliyor, basit çarpma-bölme yapabiliyor
- Çok adımlı düşünebiliyor (7-8 adım planlama)
- Dikkat süresi yeterli (15-25 dakika)
- Her seviye **2-5 dakikada** bitebilmeli

Hedef: **Algoritmik planlama**, **matematik operasyonlarını entegre kullanma** ve **optimum yol bulma** becerilerini geliştirmek.

---

## §2 — Yaş Grubuna Özgü Kısıtlamalar (KRİTİK)

| Parametre | 3. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 3×3, Max: 6×6 |
| Komutlar | `x+`, `x-`, `y+`, `y-`, `z+`, `z-` (tüm 6 komut) |
| Duvar sayısı | 2-8 |
| Operasyon | `+N` ve `×N` (N = 2-3 çarpma) |
| `targetVal` | Genellikle var (12 seviyenin ≥8'inde) |
| `startVal` aralığı | 1-20 |
| `maxCmds` | 6-14 |
| Optimum çözüm | 4-10 adım |
| `fingerprint` | Her seviyede zorunlu |

### Operasyon Değer Aralıkları

- `+N`: N = 1-8
- `-N`: **YASAK** (bu sınıfta yok)
- `×N`: N = 2-3 (**N > 3 YASAK** — MEB 3. sınıf çarpım tablosu 2-3 ile sınırlıdır)
- `÷` operasyonu — YASAK

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
- N = 1-8
- sonuç negatif OLMAMALI

### ×N
- N = 2-3
- sonuç ≤ 200 olmalı (aşırı büyük sayıları engelle)

### -N ve ÷
- **YASAK**

---

## §6 — Adaptif Difficulty

### 6.1 Performans Analizi (`level-stats.json` varsa)

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤2 deneme | Grid büyüt, duvar/op artır, ×N daha sık |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Aynı zorluk, çeşit artır |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, kolay oranı artır |
| ZORLU | ≥3/12 tamamlandı | Duvar -2, operasyon basitleştir, grid küçült |
| KRİTİK | <3/12 tamamlandı | 3×3 grid, az duvar, sadece +N operasyon, kısa çözüm |

### 6.2 Seviye Dağılımı (12 seviye)
**Kural:** `lastSetEndDifficulty` varsa (önceki set tamamlanmışsa), yeni setin ilk seviyeleri önceki setin son zorluğundan başlar. Başa sarma (reset) yok.


| Grup | Adet | Grid | Özellik |
|------|------|------|---------|
| A (Isınma) | 2 | 3×3 - 4×4 | 2-4 duvar, +N operasyon, kısa çözüm |
| B (Gelişim) | 5 | 4×4 - 5×5 | 4-6 duvar, +N ve ×N, orta çözüm |
| C (Zorlaşma) | 4 | 5×5 - 6×6 | 6-8 duvar, karışık operasyon, uzun çözüm |
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
- **Değer:** `targetVal` belirtilmişse, operasyonları kullanarak değere ulaşılabilmeli
- **maxCmds:** Optimal çözüm ≤ maxCmds olmalı
- **stars:**
  - `stars[0]` = optimum BFS çözüm uzunluğu (validate script hesaplar)
  - `stars[1]` = optimal + 2-4 adım
- **Grid:** `cols × rows <= 36` (max 6×6)
- **Negatif değer:** Operasyonlar negatif veya sıfır sonuç üretmemeli
- **×N sonucu:** ≤ 200 olmalı

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
  "ageGroup": "8-9",
  "difficultyProfile": {
    "overall": "developing",
    "avgDifficulty": 2.8,
    "adjustmentReason": "Türkçe açıklama"
  },
  "levels": [
    {
      "id": 1,
      "title": "Kısa başlık (2-4 kelime)",
      "desc": "Ne yapılacağını anlatan 1 cümle",
      "difficulty": 2,
      "cols": 4,
      "rows": 4,
      "startX": 0,
      "startY": 0,
      "startVal": 5,
      "targetX": 3,
      "targetY": 3,
      "targetVal": 8,
      "walls": [[1, 1], [2, 0]],
      "ops": [{"x": 2, "y": 2, "type": "+", "val": 3}],
      "commands": ["x+", "x-", "y+", "y-", "z+", "z-"],
      "maxCmds": 10,
      "stars": [6, 8],
      "fingerprint": {
        "grid": "4x4",
        "pathShape": "L",
        "branching": "medium",
        "backtracking": false,
        "valuePlanning": true,
        "wallTopology": "scattered",
        "ops": 1
      }
    }
  ]
}
```

---

## §11 — Yasaklar

1. `÷` operasyonu — YASAK
2. `targetVal` bu sınıfta genellikle olmalı (12 seviyenin ≥8'inde)
3. Grid 6×6 üstü — YASAK
4. Operasyon sonucu negatif veya sıfır — YASAK
5. `×N` için N > 3 — YASAK
6. Duvarı başlangıç veya hedef noktaya koyma
7. JSON dışında metin yazma
8. Çıktı SADECE valid JSON olmalıdır
10. `fingerprint` alanı eksik olmamalıdır

---

## §12 — previousSets Dokümantasyonu

`level-stats.json` içinde `previousSets` (varsa) şu yapıdadır:

```json
{
  "previousSets": [
    {
      "version": 1,
      "titles": ["İlk Adım", "Aşağı İn", ...],
      "mechanics": ["cmds=x+,y+|grid=4x4|ops=yes|walls=yes", ...]
    }
  ]
}
```

Yeni set üretirken bu title ve mekanikleri ASLA tekrar etme.

---

## §13 — Örnek Çıktı (8-9 yaş, ilk 2 seviye)

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "8-9",
  "difficultyProfile": {
    "overall": "developing",
    "avgDifficulty": 2.8,
    "adjustmentReason": "3. sınıf. Çarpma operasyonu ve daha büyük grid'ler tanıtılıyor."
  },
  "levels": [
    {
      "id": 1, "title": "Toplama Yolu", "desc": "Sayıyı hedefe ulaştır, toplama hücrelerini kullan!",
      "difficulty": 2, "cols": 4, "rows": 4,
      "startX": 0, "startY": 0, "startVal": 2,
      "targetX": 3, "targetY": 3, "targetVal": 10,
      "walls": [[1,1]], "ops": [{"x":2,"y":0,"type":"+","val":3}],
      "commands": ["x+", "x-", "y+", "y-", "z+", "z-"],
      "maxCmds": 8, "stars": [4, 6],
      "fingerprint": {
        "grid": "4x4", "pathShape": "diagonal", "branching": "low",
        "backtracking": false, "valuePlanning": true,
        "wallTopology": "single-center", "ops": 1
      }
    },
    {
      "id": 2, "title": "Çarpma Kapısı", "desc": "Çarpma hücresinden geçerek hedefe ulaş!",
      "difficulty": 3, "cols": 5, "rows": 5,
      "startX": 0, "startY": 0, "startVal": 2,
      "targetX": 4, "targetY": 4, "targetVal": 12,
      "walls": [[1,0],[2,2],[3,1]],
      "ops": [{"x":1,"y":1,"type":"×","val":2},{"x":3,"y":3,"type":"+","val":4}],
      "commands": ["x+", "x-", "y+", "y-", "z+", "z-"],
      "maxCmds": 12, "stars": [6, 9],
      "fingerprint": {
        "grid": "5x5", "pathShape": "zigzag", "branching": "medium",
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
