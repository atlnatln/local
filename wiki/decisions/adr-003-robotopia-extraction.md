---
title: "ADR-003: Robotopia'nın MathLock Play'den Ayrılması"
created: 2026-05-03
updated: 2026-05-03
type: decision
tags: [adr, decision, mathlock-play, robotopia-android, android]
related:
  - mathlock-play
  - robotopia-android
status: Active
---

# ADR-003: Robotopia'nın MathLock Play'den Ayrılması

## Durum

Active

## Bağlam

MathLock Play, çocukların telefon uygulamalarına erişimini kilitleyen ebeveyn kontrol uygulamasıdır. İçinde üç oyun barındırıyordu:

1. Matematik soruları (kilit açma mekanizmasının temeli)
2. Sayı Yolculuğu (bulmaca oyunu, backend bağlantılı)
3. Robotopia (Blockly kodlama oyunu, tamamen offline)

Robotopia'nın MathLock Play içinde kalmasının dezavantajları:
- **APK boyutu:** 2.9 MB assets (toplam assets'in %97'si)
- **Play Store policy:** `child_monitoring` beyanı ve `QUERY_ALL_PACKAGES` izni, sadece bir oyun için ağır koşullar
- **Kod karmaşası:** Kilit mekanizması ile hiçbir bağı olmayan bir oyun, uygulamanın çekirdek işlevselliğine zarar veriyor
- **Dağıtım:** Robotopia'yı güncellemek için tüm MathLock Play'i yeniden yayınlamak gerekiyor

## Karar

Robotopia, `projects/robotopia-android/` altında bağımsız bir Android projesi olarak çıkarılacak.

### Paket ve Kimlik

| Özellik | Değer |
|---------|-------|
| Package name | `com.akn.robotopia` |
| Uygulama adı | `Robotopia Kodlama` |
| Application ID | `com.akn.robotopia` |

### Mimarisi

```
robotopia-android/
├── app/
│   ├── src/main/java/com/akn/robotopia/
│   │   ├── MainActivity.kt          # Tek Activity (eski RobotopiaActivity)
│   │   ├── BaseActivity.kt          # Locale desteği
│   │   └── util/
│   │       ├── LocaleHelper.kt      # Dil değiştirme
│   │       └── LocalePrefs.kt       # Basit SharedPreferences
│   ├── src/main/res/layout/activity_main.xml
│   ├── src/main/assets/robotopia/   # 2.9 MB oyun dosyaları
│   └── build.gradle.kts             # 4 dependency, no Firebase/Billing
```

### MathLock Play'den Çıkarılanlar

- `RobotopiaActivity.kt`
- `assets/robotopia/` (2.9 MB)
- `activity_robotopia.xml`
- AndroidManifest `RobotopiaActivity` declaration
- `PreferenceManager.isRobotopiaEnabled`
- Layout kartları (ana ekran, ayarlar, challenge picker)
- ProGuard keep kuralı
- Test case'ler

## Sonuçlar

### Olumlu

- MathLock Play APK boyutunda ~2.9 MB azalma (debug: 9.4M → 6.5M, release: ~6M → ~3M)
- Robotopia kendi başına bağımsız güncellenebilir
- Play Store policy yükü hafifler (child_monitoring, QUERY_ALL_PACKAGES gerekmez)
- MathLock Play kod tabanı sadeleşir (tek sorumluluk: ebeveyn kontrolü)
- Robotopia offline, izinsiz, servissiz — minimum attack surface

### Olumsuz / Riskler

- İki ayrı proje = iki ayrı build ve release süreci
- MathLock ve Robotopia kullanıcıları ayrı uygulamalar yüklemeli
- Paylaşılan kod (WebView temizliği pattern'i) iki yerde tutulmalı

## Geçersiz Kılan

Yok (bu yeni bir karar).

## Referanslar

- `projects/robotopia-android/` — Yeni proje
- `projects/mathlock-play/` — Temizlenmiş proje
- Commit: (deploy öncesi ana monorepo'ya atılacak)
