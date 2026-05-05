---
title: "ADR-004: Hafıza Kartı Eşleştirme Oyununun MathLock Play'e Entegrasyonu"
created: 2026-05-03
updated: 2026-05-03
type: decision
tags: [adr, decision, mathlock-play, android, kotlin, memory-game]
related:
  - mathlock-play
  - sayi-yolculugu
status: Active
---

# ADR-004: Sayı Hafızası Oyununun MathLock Play'e Entegrasyonu

## Durum

Active — Implementasyon Tamamlandı

## Bağlam

MathLock Play şu anda üç oyun barındırıyordu. Robotopia ayrıldıktan sonra (ADR-003) iki oyun + yeni eklenen:

| Oyun | Teknoloji | Backend | Kilit Açma |
|------|-----------|---------|------------|
| Matematik Soruları | Native Kotlin | ✅ AI kredi | ✅ Ana mekanizma |
| Sayı Yolculuğu | WebView (HTML5) | ✅ AI kredi | ✅ Seviye tabanlı |
| Sayı Tahmin | Native Kotlin | ❌ Offline | ❌ Artık yok (pratik) |
| **Sayı Hafızası** | **Native Kotlin** | **❌ Offline** | **✅ Tur bazlı** |

Yeni oyun: **Sayı Hafızası** (Memory Match / Number Memory)
- Demo: `/home/akn/local/İndirilenler/Kimi_Agent_Android Hafıza Oyunu Demo/`
- Mekanik: Kartları çevir, eşleşen sayı çiftlerini bul.

## Kararlar

### Karar 1: Teknoloji — Native Kotlin ✅

| Kriter | Sonuç |
|--------|-------|
| Performans | Native en iyi |
| Kod tutarlılığı | Diğer aktivitelerle aynı pattern (`BaseActivity`, `ViewBinding`) |
| Animasyon | `ObjectAnimator` + `rotationY` ile 3D kart çevirme (150ms × 2) |
| Bellek | Activity düzeyinde, `onDestroy`'da Handler temizliği |

Karar: **Native Kotlin**. `MemoryGameActivity.kt` + `MemoryGameEngine.kt` (View'dan bağımsız oyun mantığı).

### Karar 2: Backend / AI Kredi Entegrasyonu — Yok ✅

Hafıza oyununun doğası set-tabanlı değil, her oturum bağımsız. Karar: **Tamamen Offline**.
- Yerel skor (hamle sayısı)
- İleride istersen skor sync eklenebilir ama MVP'de gerek yok.

### Karar 3: Kilit Açma Mekanizması — Tur Bazlı ✅

Ebeveyn ayarları:
- `memoryGamePairCount`: Kaç çift kart (4–20, default 6)
- `memoryGameRequiredRounds`: Kaç tam tur oynanınca kilit açılır (1–10, default 2)

Çocuk bir turu bitirince (tüm çiftler eşleşince) tur sayısı artar. `requiredRounds`'a ulaşılınca kilit açılır.

### Karar 4: Zorluk Sistemi — Ebeveyn Ayarlı ✅

Kilit açma modunda ebeveynin belirlediği `memoryGamePairCount` kullanılır.
Pratik/Test modunda kullanıcı 4–20 arası çift seçebilir (Slider).

### Karar 5: UI / Animasyon — 3D Flip ✅

Her kart `FrameLayout` içinde ön/arka `MaterialCardView`:
- `rotationY: 0° → 90°` (ön yüz gizlenir)
- `rotationY: -90° → 0°` (arka yüz gösterilir)
- Eşleşme: yeşil overlay + scale bounce animasyonu
- `cameraDistance = 8000 × density` (3D derinlik etkisi)

### Karar 6: Kart İçeriği — Sadece Sayılar ✅

1'den `pairCount`'a kadar rakamlar. Çiftler `[1,1,2,2,...]` şeklinde oluşturulur, Fisher-Yates shuffle ile karıştırılır.

### Karar 7: Ses Efektleri — Yok ✅

Kullanıcı talebi üzerine ses eklenmedi.

### Karar 8: Zaman Sınırı — Yok ✅

Zamansız oyun.

## Uygulanan Mimari

```
app/src/main/java/com/akn/mathlock/
├── MemoryGameActivity.kt           # Ana Activity (3D flip, kilit açma)
└── util/
    └── MemoryGameEngine.kt         # Oyun mantığı (shuffle, match, state)

app/src/main/res/layout/
├── activity_memory_game.xml        # Setup + Game + Win overlay
└── item_memory_card.xml            # Tek kart (FrameLayout: ön/arka)

app/src/main/res/drawable/
├── dialog_rounded_bg.xml           # Kazanma diyalog arka planı
└── memory_card_matched_bg.xml      # Eşleşmiş kart yeşil overlay
```

### Activity Davranışları

| Mod | Açıklama |
|-----|----------|
| **Kilit Açma** (`locked_package` var) | `memoryGameRequiredRounds` tur tamamlanınca `unlockAndLaunchApp()` |
| **Pratik** (`practice_mode=true`) | Sonsuz oyun, kullanıcı kart sayısı seçer, skor gösterilir |
| **Test** (`test_mode=true`) | Ebeveyn önizleme, tur sonunda diyalog |

### `PreferenceManager` Yeni Alanları

```kotlin
var isMemoryGameEnabled: Boolean        // Ayarlarda açık/kapalı (default true)
var memoryGamePairCount: Int            // 4-20 (default 6)
var memoryGameRequiredRounds: Int       // 1-10 (default 2)
```

### Diğer Değişiklikler

- `ChallengePickerActivity` + `activity_challenge_picker.xml`: Yeni `cardMemory` kartı
- `SettingsActivity` + `activity_settings.xml`:
  - Görev Ayarları kartına 2 yeni slider (`sliderMemoryPairs`, `sliderMemoryRounds`)
  - Test butonları satırına `btnTestMemory` eklendi
  - Oyun Görünürlüğü kartına `switchMemory` eklendi
- `AndroidManifest.xml`: `MemoryGameActivity` declaration (portrait, singleTop)
- `strings.xml`: `settings_memory_pairs`, `settings_memory_rounds`
- `colors.xml`: `card_memory`, `memory_card_back`, `memory_card_front`, `memory_card_matched`

## Sonuçlar

### Olumlu

- Çocuklara görsel-mekansal öğrenme alternatifi
- Hafıza gelişimi + eğlence birleşimi
- Basit implementasyon (tek Activity + Engine class)
- Offline = sunucu bağımlılığı yok
- 3D flip animasyonu çocuklar için etkileyici
- Ebeveyn kontrollü zorluk (kart sayısı + tur sayısı)

### Olumsuz / Riskler

- Yeni Activity = yeni `ProGuard` keep kuralı gerekmez (JS Bridge yok) ama R8 dikkatli izlenmeli
- Kart sayısı fazlaysa (20 çift = 40 kart) küçük ekranlarda sıkışabilir → responsive grid (2/3/4 sütun) ile çözüldü
- 3D animasyon çok düşük API level'de sorun çıkarabilir → minSdk 24, `rotationY` destekleniyor

## Geçersiz Kılan

Yok (bu yeni bir karar).

## Test Sonuçları

### Unit Test — MemoryGameEngineTest

```
Tests run: 27
Failures: 0
Errors: 0
Skipped: 0
Time: 0.022s
```

Test edilen senaryolar:
- Shuffle doğruluğu (kart sayısı, çift teyidi, exception)
- Temel flip (FIRST_CARD, MATCH, NO_MATCH)
- Geçersiz hareketler (açık/eşleşmiş/processing kart)
- `closeUnmatched` davranışı
- Skor sayaçları (moves, matches)
- Oyun tamamlanma (GAME_COMPLETE)
- Grid sütun sayısı (2/3/4)

### Cihaz Testi (Xiaomi — Android 14)

| Senaryo | Sonuç |
|---------|-------|
| Ana ekran → Sayı Hafızası kartı | ✅ Görünür ve tıklanabilir |
| Setup ekranı (kart çifti seçimi) | ✅ Slider 4-20 çalışıyor |
| Kart çevirme (3D flip) | ✅ Animasyon düzgün |
| Eşleşme (yeşil overlay) | ✅ Çalışıyor |
| Eşleşmeme (geri kapanma) | ✅ 800ms sonra kapanıyor |
| Oyun bitiş ekranı | ✅ "Tebrikler!" + hamle sayısı |
| Ayarlar (kart çifti + tur slider) | ✅ Çalışıyor |
| Challenge picker kartı | ✅ Görünür |

## Referanslar

- Demo: `/home/akn/local/İndirilenler/Kimi_Agent_Android Hafıza Oyunu Demo/`
- `projects/mathlock-play/app/src/main/java/com/akn/mathlock/MemoryGameActivity.kt`
- `projects/mathlock-play/app/src/main/java/com/akn/mathlock/util/MemoryGameEngine.kt`
- `projects/mathlock-play/app/src/test/java/com/akn/mathlock/MemoryGameEngineTest.kt`
- Commit: (deploy öncesi ana monorepo'ya atılacak)
