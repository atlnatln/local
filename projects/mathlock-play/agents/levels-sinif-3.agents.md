# Sayı Yolculuğu — AI Seviye Üretim Kuralları (3. Sınıf, 8-9 yaş)

> Bu dosya `ai-generate-levels.sh` tarafından kimi-cli'ye (kimi-for-coding) verilir.
> **3. sınıf (8-9 yaş)** dönemine özel kuralları tanımlar.

---

## §1 — Misyon

Sen bir eğitici oyun tasarımcısısın. **Sayı Yolculuğu** oyununu **8-9 yaşındaki 3. sınıf çocukları** için
pedagojik olarak uygun 12 seviye üreteceksin.

Bu yaş grubu özellikleri:
- 2 boyutlu hareketi ve z± komutunu kavramış (2. sınıftan geliyor)
- 4 işlem biliyor, basit çarpma-bölme yapabiliyor
- Çok adımlı düşünebiliyor (7-8 adım planlama)
- Dikkat süresi yeterli (15-25 dakika)
- Her seviye **2-5 dakikada** bitebilmeli

Hedef: **Algoritmik planlama**, **matematik operasyonlarını entegre kullanma** ve **optimum yol bulma** becerilerini geliştirmek.

---

## §2 — Görev Adımları

1. `level-stats.json` dosyasını oku (varsa). Çocuğun performansını analiz et.
2. `levels.json` dosyasını oku (varsa). Mevcut versiyon numarasını al.
3. §4 Adaptif Algoritma'yı uygula.
4. **12 yeni seviye** üret (§6 şemasına uygun).
5. Çıktı olarak **SADECE** yeni `levels.json` içeriğini yaz. Başka metin yazma.

---

## §3 — Yaş Grubuna Özgü Parametreler

| Parametre | 3. Sınıf Kuralı |
|-----------|----------------|
| Grid boyutu | Min: 3×3, Max: 6×6 |
| Komutlar | `x+`, `x-`, `y+`, `y-`, `z+`, `z-` (tüm 6 komut) |
| Duvar sayısı | 2-8 |
| Operasyon | `+N` ve `×N` (N = 2-3 çarpma) |
| targetVal | Genellikle var (12 seviyenin ≥8'inde) |
| startVal aralığı | 1-20 |
| maxCmds | 6-14 |
| Optimum çözüm | 4-10 adım |

### Operasyon Değer Aralıkları
- `+N`: N = 1-8
- `-N`: N = 1-5 (dikkat: sonuç ≥1 olmalı)
- `×N`: N = 2-3 (çarpma operasyonu orta zorlukta). **N > 3 YASAK — MEB 3. sınıf çarpım tablosu 2-3 ile sınırlıdır.**
- `÷` operasyonu — YASAK (uygulama desteklemiyor)

---

## §4 — Adaptif Algoritma

### 4.1 Performans Analizi (level-stats.json varsa)

Her seviye için: `completed`, `stars`, `attempts`, `commandsUsed`, `timeSeconds`

| Kategori | Koşul | Karar |
|----------|-------|-------|
| USTA | ≥10/12 tamamlandı, ort. ≥2.5 yıldız, ort. ≤2 deneme | Grid büyüt, duvar/op artır, ×N daha sık |
| GÜVENLİ | ≥8/12 tamamlandı, ort. ≥2 yıldız | Aynı zorluk, çeşit artır |
| GELİŞEN | ≥6/12 tamamlandı, ort. ≥1.5 yıldız | Aynı zorluk, kolay oranı artır |
| ZORLU | ≥3/12 tamamlandı | Duvar -2, operasyon basitleştir, grid küçült |
| KRİTİK | <3/12 tamamlandı | 3×3 grid, az duvar, sadece +N operasyon, kısa çözüm |

### 4.2 Seviye Dağılımı (12 seviye)

| Grup | Adet | Grid | Özellik |
|------|------|------|---------|
| A (Güven) | 4 | 3×3 - 4×4 | 2-4 duvar, +N operasyon, kısa çözüm |
| B (Gelişim) | 5 | 4×4 - 5×5 | 4-6 duvar, +N ve ×N, orta çözüm |
| C (Meydan Okuma) | 3 | 5×5 - 6×6 | 6-8 duvar, karışık operasyon, uzun çözüm |

### 4.3 İlk Set (level-stats.json yoksa)

- version = 1, ageGroup = "8-9"
- difficultyProfile.overall = "developing"
- Seviye 1-3: 3×3 grid, x±/y±/z±, 2-3 duvar, +N, targetVal var, 4-5 adım
- Seviye 4-6: 4×4 grid, tüm komutlar, 3-4 duvar, +N, targetVal var, 5-7 adım
- Seviye 7-9: 4×4 veya 5×5 grid, 4-6 duvar, +N ve ×N operasyon, 6-8 adım
- Seviye 10-11: 5×5 veya 6×6, 6-8 duvar, karışık operasyon, 8-10 adım
- Seviye 12: 4×4, 4-5 adım, kolay bitiriş

### 4.4 Psikolojik Sıralama

- Seviye 1-2: Tanıdık mekanik (+N), kısa çözüm
- Seviye 3-5: ×N operasyon tanıtılır, orta zorluk
- Seviye 6-8: Çok duvarlı, operasyon zincirleme
- Seviye 9-10: Yüksek zorluk, dikkatli planlama
- Seviye 11: En zor seviye
- Seviye 12: Orta zorluk, başarıyla kapanış

---

## §5 — Çözülebilirlik Kuralları

1. BFS ile başlangıçtan hedefe ulaşılabilir yol olmalı (durum: x, y, değer).
2. targetVal belirtilmişse, operasyonları kullanarak değere ulaşılabilmeli.
3. stars[0] = optimum çözüm adım sayısı
4. stars[1] = optimum + 2-4 adım (zorluk toleransı)
5. maxCmds = stars[1] + 2-4 ek adım
6. Duvarlar başlangıç veya hedefi kapatmamalı
7. Operasyonlar negatif veya sıfır sonuç üretmemeli
8. ×N sonucu ≤ 200 olmalı (aşırı büyük sayıları engelle)

---

## §6 — levels.json Şeması

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
      "stars": [6, 8]
    }
  ]
}
```

---

## §7 — Yasaklar

1. `÷` operasyonu — YASAK
2. targetVal bu sınıfta genellikle olmalı (12 seviyenin ≥8'inde)
3. Grid 6×6 üstü — YASAK
4. Operasyon sonucu negatif veya sıfır — YASAK
5. ×N için N > 3 — YASAK
6. Duvarı başlangıç veya hedef noktaya koyma
7. JSON dışında metin yazma
