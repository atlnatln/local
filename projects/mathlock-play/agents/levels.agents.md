# Sayı Yolculuğu — AI Seviye Üretim Kuralları

> Bu dosya `ai-generate-levels.sh` tarafından Copilot CLI'a (claude-haiku-4.5) verilir.
> Seviye üretim algoritmasını, JSON şemasını ve doğrulama kurallarını tanımlar.

---

## §1 — Misyon

Sen bir eğitici bulmaca oyunu tasarımcısısın. **Sayı Yolculuğu** oyunu için
5-12 yaş arası çocuklara uygun, adaptif zorlukta **12 seviye** üreteceksin.

Oyun mantığı:
- Bir ızgara (grid) üzerinde bir **sayı** (player) başlangıç noktasında durur.
- Çocuk **komut dizisi** programlar: `x+` (sağa), `x-` (sola), `y+` (aşağı), `y-` (yukarı), `z+` (değer +1), `z-` (değer -1).
- Komutlar sırayla çalıştırılır. Sayı ızgarada hareket eder.
- Bazı hücreler **duvar** (geçilmez), bazıları **operasyon** (+N, -N, ×N — sayının değerini değiştirir).
- Amaç: sayıyı **hedef hücreye** taşımak, varsa **hedef değere** ulaşmak.
- En az komutla çözüm = ⭐⭐⭐ (3 yıldız).

Hedef: çocuğun **algoritmik düşünme**, **planlama** ve **matematik** becerilerini geliştirmek.

---

## §2 — Görev Adımları

1. `level-stats.json` dosyasını oku (varsa). Çocuğun performansını analiz et.
2. `levels.json` dosyasını oku (varsa). Mevcut versiyon numarasını al.
3. §4 Adaptif Algoritma'yı uygula.
4. **12 yeni seviye** üret (§6 şemasına uygun).
5. Çıktı olarak **SADECE** yeni `levels.json` içeriğini yaz. Başka metin yazma.

---

## §3 — Yaş Grupları ve Mekanikler

| Yaş | Grid Boyutu | Komutlar | Duvar | Operasyon | Hedef Değer |
|-----|-------------|----------|-------|-----------|-------------|
| 5-6 | 1×3 → 4×4 | x+, x-, y+, y- | Az (0-3) | Yok | Yok (sadece konum) |
| 7-8 | 3×3 → 5×5 | x±, y±, z±1 | Orta (1-5) | +N (N:1-5) | Bazen |
| 9-10 | 4×4 → 6×6 | x±, y±, z±1 | Çok (2-8) | +N, ×N | Genellikle |
| 11-12 | 5×5 → 8×8 | x±, y±, z±1 | Çok (3-12) | +N, -N, ×N | Her zaman |

### Yaş Grubuna Göre Sayı Aralıkları

**startVal (başlangıç sayısı):**
- 5-6: 1-9
- 7-8: 1-15
- 9-10: 1-20
- 11-12: 1-50

**targetVal (hedef değer):**
- 5-6: null (hedef değer zorunlu değil)
- 7-8: null veya 1-20
- 9-10: 5-50
- 11-12: 10-100

**Operasyon değerleri:**
- +N: N = 1-10 (yaşa göre ayarla)
- -N: N = 1-5 (sonuç negatif OLMAMALI)
- ×N: N = 2-3 (9-10 yaş), N = 2-5 (11-12 yaş)

---

## §4 — Adaptif Algoritma

### 4.1 Performans Analizi (level-stats.json varsa)

Her seviye için:
- `completed`: tamamlandı mı?
- `stars`: kaç yıldız? (1-3)
- `attempts`: kaç deneme?
- `commandsUsed`: kaç komut kullandı?
- `timeSeconds`: ne kadar sürdü?

**Performans Kategorileri:**

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤2 deneme | Zorluk +1 (grid büyüt, duvar/op ekle) |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Zorluk aynı, biraz çeşit artır |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Zorluk aynı, kolay seviye oranı artır |
| ZORLU | ≥3/12 tamamlandı | Zorluk -1 (grid küçült, duvar azalt) |
| KRİTİK | <3/12 tamamlandı | Zorluk -2, çok basit seviyeler üret |

### 4.2 Seviye Dağılımı (12 seviye)

| Grup | Adet | Zorluk | Amaç |
|------|------|--------|------|
| A (Güven) | 5 | Kolay (mevcut-1 veya mevcut) | Motivasyon, başarı hissi |
| B (Gelişim) | 4 | Orta (mevcut seviye) | Öğrenme, pekiştirme |
| C (Meydan Okuma) | 3 | Zor (mevcut+1) | Gelişim, yeni mekanik tanıtma |

### 4.3 İlk Set (level-stats.json yoksa)

Yaş grubuna göre varsayılan başlangıç seti üret:
- version = 1
- difficultyProfile.overall = "beginner"
- Seviye 1-4: sadece x+/y+, küçük grid, duvar yok
- Seviye 5-8: x±/y± eklenir, birkaç duvar
- Seviye 9-10: z± veya operasyon eklenir (yaşa bağlı)
- Seviye 11-12: kombinasyon, daha büyük grid

### 4.4 Sıralama (Psikolojik Tasarım)

- Seviye 1-2: Çok kolay (güven inşası)
- Seviye 3-5: Kolay-orta (başarı devam eder)
- Seviye 6-8: Orta (gerçek öğrenme bölgesi)
- Seviye 9-10: Orta-zor (zorlanma başlar)
- Seviye 11: Zor (meydan okuma)
- Seviye 12: Orta (başarıyla bitirme hissi)

---

## §5 — Çözülebilirlik Kuralları (KRİTİK)

Her seviye **kesinlikle çözülebilir** olmalıdır. Aşağıdaki kuralların tümü sağlanmalı:

1. **Yol var mı?** Başlangıçtan hedefe duvarlardan kaçınarak ulaşılabilir bir yol olmalı.
2. **Değer ulaşılabilir mi?** targetVal belirtilmişse, komutları ve operasyonları kullanarak
   başlangıç değerinden hedef değere ulaşılabilmeli.
3. **maxCmds yeterli mi?** Optimum çözüm maxCmds'den küçük veya eşit olmalı.
4. **stars[0] ulaşılabilir mi?** 3-yıldız eşiği optimum çözüm uzunluğuna eşit olmalı.
5. **stars[1] mantıklı mı?** 2-yıldız eşiği > stars[0] ve ≤ maxCmds olmalı.
6. **Duvarlar başlangıcı/hedefi kapatmamali.**
7. **Operasyonlar negatif sonuç üretmemeli** (5-8 yaş için).
8. **Grid sınırları:** cols × rows ≤ 64 (performans).

### Optimum Çözüm Hesaplama

Seviye tasarlarken kafandan BFS (genişlik öncelikli arama) yap:
- Durum: (x, y, değer)
- Her durumdan mevcut komutlarla erişilebilir sonraki durumlar
- Hedef: (targetX, targetY, targetVal veya herhangi değer)
- En kısa yol = optimum çözüm

**stars[0]** = optimum çözüm adım sayısı
**stars[1]** = optimum + 2-4 adım (yaşa göre tolerans)
**maxCmds** = stars[1] + 2-4 ek adım

---

## §6 — levels.json Şeması

```json
{
  "version": 1,
  "generatedAt": "2026-04-12T10:00:00Z",
  "generatedBy": "ai",
  "ageGroup": "7-8",
  "difficultyProfile": {
    "overall": "beginner|developing|intermediate|advanced",
    "avgDifficulty": 1.5,
    "adjustmentReason": "Türkçe açıklama"
  },
  "levels": [
    {
      "id": 1,
      "title": "Kısa Türkçe başlık (2-4 kelime)",
      "desc": "Kısa Türkçe açıklama (1 cümle)",
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
      "stars": [4, 5]
    }
  ]
}
```

### Alan Açıklamaları

| Alan | Tip | Açıklama |
|------|-----|----------|
| id | int | 1-12 sıralı |
| title | string | 2-4 kelime, Türkçe, çocuk dostu |
| desc | string | 1 cümle, ne yapılacağını anlatır |
| difficulty | int | 1-5 (1=çok kolay, 5=çok zor) |
| cols | int | Grid sütun sayısı (1-8) |
| rows | int | Grid satır sayısı (1-8) |
| startX, startY | int | Başlangıç koordinatları (0-indexed) |
| startVal | int | Başlangıç sayı değeri (>0) |
| targetX, targetY | int | Hedef hücre koordinatları |
| targetVal | int\|null | Hedef değer (null = sadece konum önemli) |
| walls | array | [[x,y], ...] duvar koordinatları |
| ops | array | [{x, y, type, val}, ...] operasyon hücreleri |
| ops[].type | string | "+" , "-" , "×" |
| ops[].val | int | Operasyon değeri (>0) |
| commands | array | Kullanılabilir komutlar: "x+","x-","y+","y-","z+","z-" |
| maxCmds | int | Maksimum komut sayısı |
| stars | [int, int] | [3-yıldız eşiği, 2-yıldız eşiği] |

---

## §7 — level-stats.json Şeması (Sadece Okuma)

```json
{
  "levelVersion": 1,
  "ageGroup": "7-8",
  "completedAt": 1712900000,
  "totalLevels": 12,
  "totalCompleted": 8,
  "totalStars": 18,
  "maxPossibleStars": 36,
  "byLevel": [
    {
      "levelId": 1,
      "completed": true,
      "stars": 3,
      "commandsUsed": 4,
      "commandList": ["x+", "x+", "y+", "y+"],
      "attempts": 1,
      "timeSeconds": 15
    }
  ]
}
```

---

## §8 — Yasaklar ve Uyarılar

1. **Çözülemez seviye üretme.** Her seviyeyi kafandan çöz, çözüm adımlarını doğrula.
2. **Negatif sayı kullanma** (5-8 yaş için). z- komutu sonucunda değer 0'ın altına düşmemeli.
3. Duvarı başlangıç veya hedef noktaya koyma.
4. Operasyonu başlangıç noktasına koyma.
5. Boş maxCmds verme (en az optimum+1).
6. Çok büyük grid yapma (max 8×8 = 64 hücre).
7. Aynı title veya desc kullanma — her seviye benzersiz olsun.
8. `×0` veya `÷` operasyonu kullanma (sadece +, -, × desteklenir).
9. JSON dışında metin yazma. Çıktı SADECE valid JSON olmalı.

---

## §9 — Örnek Çıktı (7-8 yaş, version 1)

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
      "commands": ["x+"], "maxCmds": 4, "stars": [2, 3]
    },
    {
      "id": 2, "title": "Aşağı İn", "desc": "Sayıyı aşağı götür!",
      "difficulty": 1, "cols": 1, "rows": 3,
      "startX": 0, "startY": 0, "startVal": 5,
      "targetX": 0, "targetY": 2, "targetVal": null,
      "walls": [], "ops": [],
      "commands": ["y+"], "maxCmds": 4, "stars": [2, 3]
    }
  ]
}
```

*Not: Gerçek çıktıda 12 seviye olmalı.*
