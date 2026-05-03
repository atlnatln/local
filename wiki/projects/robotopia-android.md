---
title: "Robotopia Android"
created: 2026-05-03
updated: 2026-05-03
type: project
tags: [robotopia-android, android, kotlin, html5, webview]
related:
  - mathlock-play
sources:
  - projects/robotopia-android/app/src/main/java/com/akn/robotopia/MainActivity.kt
---

# [[Robotopia-Android]]

Blockly tabanlı kodlama oyunu. Robotları programlayarak görevleri tamamlayan çocuklara yönelik bağımsız Android uygulaması.

## Purpose

Çocuklar görsel bloklar kullanarak temel programlama kavramlarını (sıralama, döngü, koşul) öğrenir. HTML5 oyun motoru WebView içinde çalışır, tamamen offline'dır.

## Stack

| Katman | Teknoloji |
|--------|-----------|
| Android App | Kotlin, AppCompat, Material 3 |
| Oyun Motoru | HTML5 + Blockly + Canvas (WebView) |
| Min/Target SDK | 26 / 35 |
| Build | Gradle 8.2, Kotlin 1.9.20 |
| Minify | R8 (`isMinifyEnabled = true`) |

## Entry Points

| Dosya | Görev |
|-------|-------|
| `projects/robotopia-android/app/src/main/java/com/akn/robotopia/MainActivity.kt` | Tek Activity — WebView başlatma, JS Bridge |
| `projects/robotopia-android/app/src/main/assets/robotopia/game.html` | Oyun giriş noktası |
| `projects/robotopia-android/app/src/main/assets/robotopia/bundle.js` | Oyun motoru (1.4 MB) |
| `projects/robotopia-android/app/src/main/assets/robotopia/blockly/` | Blockly kütüphanesi ve TR/EN mesajlar |

## Özellikler

- **Offline:** Hiçbir izin, internet bağlantısı veya backend gerektirmez
- **Dil Desteği:** TR + EN (`LocaleHelper` + `LocalePrefs`)
- **WebView Memory Management:** `onDestroy()`'da `webView.destroy()` + `removeAllViews()`
- **JS Bridge:** `Android.onGameEvent(event, data)` — seviye tamamlama, oyun bitişi
- **Chrome DevTools:** Debug build'de `WebView.setWebContentsDebuggingEnabled(true)`

## Build

```bash
cd projects/robotopia-android
./gradlew assembleDebug    # Debug APK
./gradlew assembleRelease  # Release APK (R8 + shrinkResources)
```

## Dependencies

- [[mathlock-play]] — Orijinal olarak MathLock Play içindeydi (2026-05-03'te ayrıldı)

## History

- **2026-05-03:** MathLock Play'den ayrıldı. `RobotopiaActivity.kt` bağımsız `MainActivity.kt` oldu.
