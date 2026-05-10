# Sayı Yolculuğu — AI Seviye Üretim Kuralları (Okul Öncesi, 5-6 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye verilir.
> **Okul öncesi (5-6 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **5-6 yaşındaki çocuklar** için basit, eğlenceli ve pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- Dikkat süresi kısa (5-10 dakika maksimum)
- Yönlü hareket kavramını yeni öğreniyor (sağ, sol, aşağı)
- Sayıları anlıyor ama işlem yapamıyor
- Başarı hissi ve hızlı geri bildirim kritik
- Her seviye **30 saniye - 2 dakikada** bitebilmeli

Hedef: Çocuğun **yön kavramı**, **sıralama mantığı** ve **dikkat** becerilerini oyunla geliştirmek.

---

## §2 — Yaş Grubuna Özgü Kısıtlamalar (KRİTİK)

| Parametre | Okul Öncesi Kuralı |
|-----------|-------------------|
| Grid boyutu | Min: 1×2, Max: 3×3 |
| Komutlar | SADECE `x+`, `x-`, `y+` (sağa, sola, aşağı — 3 komut yeterli) |
| `y-` komutu | Sadece son 3 seviyede kullan |
| `z±1` komutu | **YASAK** — değer değişimi bu yaşta yok |
| Duvar sayısı | İlk 6 seviye: 0, Son 6 seviye: en fazla 2 |
| Operasyon (+N, ×N) | **YASAK** |
| `targetVal` | **YASAK** — sadece konum hedefi |
| `startVal` aralığı | 1-9 (tek basamaklı, tanıdık sayılar) |
| `maxCmds` | En fazla 6 (kısa tuş dizisi) |
| Optimum çözüm | ≤ 4 komut (ilk 8 seviye) |
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
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız | Grid biraz büyüt (max 3×3), `y-` ekle son 2 seviyeye |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Aynı zorluk, 1-2 duvar ekle son 3 seviyeye |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, kolay seviye oranı artır |
| ZORLU | ≥3/12 tamamlandı | Grid küçült (1×3 veya 2×2), duvar sıfırla |
| KRİTİK | <3/12 tamamlandı | En basit: 1×3 grid, sadece `x+`, 2-3 adım |

### 6.2 Seviye Dağılımı (12 seviye)
**Kural:** `lastSetEndDifficulty` varsa (önceki set tamamlanmışsa), yeni setin ilk seviyeleri önceki setin son zorluğundan başlar. Başa sarma (reset) yok.


| Grup | Adet | Açıklama |
|------|------|----------|
| A (Isınma) | 2 | 1×2 veya 1×3 grid, tek komut (`x+` veya `y+`), duvar yok |
| B (Gelişim) | 5 | 2×2 veya 2×3 grid, iki komut (`x+` ve `y+`), 0-1 duvar |
| C (Zorlaşma) | 4 | 3×3 grid, üç komut (`x+`, `x-`, `y+`), 0-2 duvar |
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

Bu yaş grubunda `value` değişmez (z± yok, ops yok), yani state `(x, y)` olarak düşünülebilir.

### 7.2 Doğrulanması Gerekenler

- **Yol:** Başlangıçtan hedefe ulaşılabilmeli
- **maxCmds:** Optimal çözüm ≤ maxCmds olmalı
- **stars:**
  - `stars[0]` = optimum BFS çözüm uzunluğu (validate script hesaplar)
  - `stars[1]` = optimal + 1-2 adım
- **Grid:** `cols × rows <= 9` (max 3×3)

### 7.3 Örnek BFS (1×3 grid, `x+` komutu)

Başlangıç: x=0, hedef: x=2
Adımlar: `x+`, `x+` → optimal=2
`stars=[2, 3]`, `maxCmds=4`

---

## §8 — Gameplay Variety (KRİTİK)

Aynı hissi veren seviyeler üretme. Sadece title değiştirmek yeterli değildir.

### 8.1 Semantic Variety

Şunlar farklı olmalıdır:
- path shape
- grid boyutu
- komut sayısı
- komut çeşidi

### 8.2 Cognitive Variety

Farklı seviyeler farklı düşünme biçimleri istemelidir:
- corridor navigation (koridor takibi)
- direction change (yön değiştirme)
- simple pattern (basit desen)

---

## §9 — previousSets Kuralları (KRİTİK)

`previousSets` varsa aşağıdakiler **yasaktır**:

1. **Aynı title** — `previousSets[].titles` içindeki herhangi bir title tekrar edilemez
2. **Aynı gameplay hissi** — `previousSets[]` içindeki seviyelerle "aynı hissi veren" seviye üretilemez
3. **Aynı fingerprint** — `previousSets[].mechanics` içindeki mekanik parmak izi tekrar edilemez
4. **Aynı çözüm yapısı** — `previousSets[]` içindeki seviyelerle aynı komut dizisi + grid boyutu tekrar edilemez

**Örnek:** Önceki sette "Sağa Git" (`x+`, 3×1 grid, duvar yok) varsa, yeni sette "İleri Adım" (`x+`, 3×1 grid, duvar yok) yapma. Farklı grid şekli veya duvar ekle.

---

## §10 — JSON Şeması

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
      "startVal": 2,
      "targetX": 2,
      "targetY": 0,
      "targetVal": null,
      "walls": [],
      "ops": [],
      "commands": ["x+"],
      "maxCmds": 4,
      "stars": [2, 3],
      "fingerprint": {
        "grid": "3x1",
        "pathShape": "line",
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
3. Operasyon hücreleri (+N, ×N) — YASAK
4. Grid 3×3 üstü — YASAK
5. 6 komut üstü `maxCmds` — YASAK
6. Duvarı başlangıç veya hedef noktaya koyma
7. Seviye 1-6'da duvar kullanma
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
      "titles": ["İlk Adım", "Aşağı İn", ...],
      "mechanics": ["cmds=x+|grid=3x1|ops=no|walls=no", ...]
    }
  ]
}
```

- `titles`: Önceki setteki 12 seviyenin başlıkları
- `mechanics`: Önceki setteki her seviyenin mekanik parmak izi

Yeni set üretirken bu title ve mekanikleri ASLA tekrar etme.

---

## §13 — Örnek Çıktı (5-6 yaş, version 1, ilk 3 seviye)

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
      "commands": ["x+"],
      "maxCmds": 4, "stars": [2, 3],
      "fingerprint": {
        "grid": "3x1", "pathShape": "line", "branching": "none",
        "backtracking": false, "valuePlanning": false,
        "wallTopology": "none", "ops": 0
      }
    },
    {
      "id": 2, "title": "Aşağı Bak", "desc": "Sayıyı aşağı indir!",
      "difficulty": 1, "cols": 1, "rows": 3,
      "startX": 0, "startY": 0, "startVal": 4,
      "targetX": 0, "targetY": 2, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["y+"],
      "maxCmds": 4, "stars": [2, 3],
      "fingerprint": {
        "grid": "1x3", "pathShape": "line", "branching": "none",
        "backtracking": false, "valuePlanning": false,
        "wallTopology": "none", "ops": 0
      }
    },
    {
      "id": 3, "title": "Kısa Yol", "desc": "Sağa git, sonra aşağı!",
      "difficulty": 1, "cols": 2, "rows": 2,
      "startX": 0, "startY": 0, "startVal": 1,
      "targetX": 1, "targetY": 1, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["x+", "y+"],
      "maxCmds": 4, "stars": [2, 3],
      "fingerprint": {
        "grid": "2x2", "pathShape": "L", "branching": "none",
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
