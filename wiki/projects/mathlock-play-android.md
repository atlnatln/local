---
title: "MathLock Play — Android"
created: 2026-05-07
updated: 2026-05-10
type: project
tags: [mathlock-play, android, kotlin, security]
related:
  - mathlock-play
  - mathlock-play-backend
  - mathlock-play-ai
  - sayi-yolculugu
  - mathlock-play-android-releases
---

# MathLock Play — Android

Kotlin ile yazılmış Android uygulaması. UsageStatsManager tabanlı kilit mekanizması, çoklu oyun modları ve AI soru seti entegrasyonu.

## Android Authentication

`AccountManager` cihaz kaydı yapar ve `device_token`'ı imzalı hale getirir. Her `ApiClient` instance'ına `setAuthToken()` ile atanır.

> **Önemli:** `SayiYolculuguActivity` kendi `RealApiClient()` instance'ını oluşturur. Bu instance'a da `apiClient.setAuthToken(accountManager.getAccessToken())` çağrısı yapılmalıdır, aksi halde tüm backend çağrıları `403 Forbidden` döner. Bkz. [[mathlock-play]] Sayı Yolculuğu Auth Fix bölümü.

## Parent Authentication (Ebeveyn Doğrulaması)

Ebeveyn ayarlarına erişim için cihazın kendi güvenlik yöntemi kullanılır (`BiometricPrompt` + `DEVICE_CREDENTIAL`).

**Akış:**
1. Kullanıcı ebeveyn girişi butonuna basar veya logoya 5 kez hızlı tıklar
2. Doğrudan sistem `BiometricPrompt`'u açılır (parmak izi / desen / PIN / şifre)
3. Doğrulama başarılı ise `SettingsActivity`'e yönlendirilir

**Önceki hali (kaldırıldı):** `fa6174fc` commit'inde eklenen "Ebeveyn Doğrulaması" bottom sheet (`showParentAuthOptions()`) kaldırıldı. Bottom sheet arada fazladan bir adım oluşturuyordu; doğrudan sistem prompt'u daha hızlı ve net.

**Manifest değişikliği (2026-05-09):**
```xml
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
<uses-permission android:name="android.permission.USE_FINGERPRINT" />
```

**Sınırlamalar:**
- Cihazda herhangi bir güvenlik yöntemi (parmak izi, desen, PIN, şifre) yoksa `Toast` ile "Bu cihazda parmak izi veya desen kilidi bulunamadı" mesajı gösterilir
- Xiaomi MIUI cihazlarda `BIOMETRIC_STRONG or DEVICE_CREDENTIAL` kombinasyonu ile sistem prompt davranışı cihaza bağlıdır

## Android Fallback Üretimi (`MathQuestionGenerator.kt`)

`generate(educationPeriod)` çağrısıyla çalışır. Her yaş grubu için aynı sayı aralıklarını kullanır ama deterministic DEĞİLDİR (`Random.nextInt`). JSON cache yoksa `startFallbackMode()` ile bu generator çalışır.

| Metod | İşlem | Aralık |
|-------|-------|--------|
| `generateGrade1()` | toplama/çıkarma | 1-10 arası, sonuç max 20, çıkarmada onluktan bozma kontrollü |
| `generateGrade2()` | toplama, çıkarma, çarpma, bölme | toplama(50,50), çıkarma(10,99), çarpma(10,10), bölme(10,10) |
| `generateGrade3()` | toplama, çıkarma, çarpma, bölme, kare | toplama(100,100), çıkarma(10,200), çarpma(12,12), bölme(12,12) |
| `generateGrade4()` | toplama, çıkarma, çarpma, bölme, kare | toplama(500,500), çıkarma(50,500), çarpma(15,15), bölme(15,15) |

**Hint ekleme (`HINTS` sözlüğü):**
- Toplama: "Büyük sayıdan başla, küçük sayıyı parmakla say"
- Çıkarma: "Büyük sayıdan geriye doğru say"
- Çarpma: "Çarpım tablosunu hatırla"
- Bölme: "Çarpma tablosunu tersten düşün"

**Önemli sınırlamalar:**
- Çıkarma sonucu her zaman pozitif (`b = random.randint(1, a-1)`)
- Bölme her zaman tam bölünür (`a = b * result`)
- Çarpma sonucu max 100 (Batch 0'da)

## İçindeki Oyunlar

| Oyun | Tip | Backend | Açıklama |
|------|-----|---------|----------|
| Matematik Soruları | Native Kotlin | ✅ AI kredi sistemi | 50 soruluk setler, adaptif zorluk |
| Sayı Tahmin | Native Kotlin | ❌ Offline | 0-100 arası tahmin, tur bazlı |
| [[sayi-yolculugu]] | WebView (HTML5) | ✅ AI kredi sistemi | 12 seviyelik bulmaca setleri, Blockly benzeri mekanik |
| Sayı Hafızası | Native Kotlin | ❌ Offline | Kart eşleştirme, 3D flip animasyon, 4-20 çift |

> Robotopia (Blockly kodlama) artık bu projede değil. Bkz. [[robotopia-android]] ve [[adr-003-robotopia-extraction]].


## Bug Fixes (2026-05-10)

### MemoryGame Kart Hizalaması

**Sorun:** Kartlar sola yaslıydı, grid ortalanmamıştı.

**Kök Neden:** `GridLayout` default davranışı LTR (soldan sağa) akıştı. Türkçe arayüzde kartlar sağdan sola dizilmeliydi.

**Çözüm:** `GridLayout.LayoutParams` ile manuel `columnSpec` hesaplaması. RTL (sağdan sola) akış sağlandı.

```kotlin
val gridLp = GridLayout.LayoutParams(
    GridLayout.spec(index / columnCount),
    GridLayout.spec((columnCount - 1) - (index % columnCount))
)
```

### Sayı Yolculuğu Yükleme UX

**Sorun:** Oyun yüklenirken stilsiz HTML görünüyordu (flash of unstyled content).

**Çözüm:** `ProgressBar` overlay eklendi. `WebView` `INVISIBLE` başlatılıp `initGame()` JavaScript callback'i sonrası `VISIBLE` yapılıyor.

```kotlin
// onCreate
progressBar = findViewById(R.id.progressBar)
webView.visibility = View.INVISIBLE

// loadLevelsIntoGame() → runOnUiThread
webView.evaluateJavascript("initGame('\$escaped');", null)
progressBar.visibility = View.GONE
webView.visibility = View.VISIBLE
```

### Sayı Yolculuğu Set Badge

**Sorun:** Header'da ham `set_id: 49` gösteriliyordu.

**Çözüm:** `data.version` (user-facing set numarası) kullanılıyor. Backend `get_levels()` response'unda `version` alanı zaten mevcut.

```javascript
$('setBadge').textContent = data.version ? ('Set ' + data.version) : '';
```

### Ayarlar Kilit Süresi

**Sorun:** "Sınırsız" seçeneği kullanıcıya kafa karıştırıcı geliyordu.

**Çözüm:** "Sınırsız" kaldırıldı. Slider `valueFrom="1"`, `valueTo="60"`. `PreferenceManager` güncellendi.

```kotlin
var unlockDurationMinutes: Int
    get() = prefs.getInt(KEY_UNLOCK_DURATION, 1)
    set(value) = prefs.edit().putInt(KEY_UNLOCK_DURATION, value.coerceIn(1, 60)).apply()
```

**Label:** `resources.getString(R.string.settings_unlock_duration_minutes, minutes)` → "X dakika"

---

## Release Notları ve Bug Fix'ler

> Detaylı release notları ve tüm bug fix'ler: [[mathlock-play-android-releases]]

