# MathLock Play — ADB + Emulator Çalışmaları

**Tarih:** 28 Mart 2026

---

## 1. Android Ortamı

- `adb` yüklendi ve fiziksel cihaz bağlandı: `4fd99276` (Xiaomi, Android 15)
- Fiziksel telefondan **master screenshot seti** alındı → `assets/screenshots/phone/`:
  - `screenshot_01_ana_ekran.png`
  - `screenshot_02_ebeveyn_paneli.png`
  - `screenshot_03_soru_coz.png`
  - `screenshot_04_sayi_oyunu.png`
  - `screenshot_05_kilit_ekrani.png`
- `tablet-7inch/` → fiziksel ekranlar kopyalandı + 4 yeni otomatik çekildi (`7inch_01..05`)
- `tablet-10inch/` → tüm 5 görsel kopyalandı (`10inch_01..05`)

---

## 2. Android Emulator Kurulumu (Linux)

```bash
# Kurulum dizini
~/Android/Sdk/cmdline-tools/latest/

# Yüklenen bileşenler (sdkmanager)
emulator
platform-tools
system-images;android-34;google_apis;x86_64
platforms;android-34

# Oluşturulan AVD'ler (avdmanager)
tablet_7inch   — Nexus 7 2013
tablet_10inch  — Nexus 10
```

---

## 3. Emulator Test

```bash
# AVD başlatma
emulator -avd tablet_7inch

# Bağlantı doğrulama
adb devices          # → emulator-5554
adb shell wm size    # → Physical size: 1200x1920
adb shell wm density # → 320

# APK yükleme
adb install app-debug.apk
```

---

## 4. MathLock App Flow (Emulator)

- `com.akn.mathlock.MainActivity` `am start` ile başlatıldı
- **Kısıt:** `SettingsActivity`, `ParentAuthActivity` vb. `exported=false` → `am start` ile doğrudan açılamaz
- `ParentAuthActivity`: `BiometricPrompt` tabanlı; AVD config'e `hw.fingerprint=yes` eklendi
- Biometric sensör olmadan flow mobil yoldan (fiziksel cihaz) tamamlandı

---

## 5. Ekran Görüntüsü Özeti

| Dizin | Dosyalar | Çözünürlük | Durum |
|-------|----------|-----------|-------|
| `phone/` | 5 adet `screenshot_0X_*.png` | 1080×2400 | ✅ Fiziksel telefon |
| `tablet-7inch/` | 5 adet `7inch_0X_*.png` | 1200×1920 | ✅ Emulator |
| `tablet-10inch/` | 5 adet `10inch_0X_*.png` | 1200×1920 | ✅ Kopya (Play uyumlu) |

> **Not:** Fiziksel telefon 1080×2400, emulator 1200×1920. Her iki boyut da Play Console minimum gereksinimini (320px kısa kenar) karşılar.

---

## 6. Kısıtlar ve Çözümler

| Kısıt | Neden | Çözüm |
|-------|-------|-------|
| `adb shell input tap` engeli | Android 15 `INJECT_EVENTS` kısıtı | Fiziksel el ile etkileşim |
| `adb shell wm size` engeli | `WRITE_SECURE_SETTINGS` gerekiyor | Emulator kullanıldı |
| Non-exported aktiviteler | `am start` ile açılamıyor | Ana ekran üzerinden manuel flow |
| Biometric sensör yok | Emulator donanım sınırı | `hw.fingerprint=yes` + fiziksel cihaz fallback |

---

## 7. Sonuç

Play Console için gereken **3 cihaz tipine ait ekran görüntüsü seti** tamamlandı:
- ✅ Telefon (5 görsel)
- ✅ 7" Tablet (5 görsel)
- ✅ 10" Tablet (5 görsel)
