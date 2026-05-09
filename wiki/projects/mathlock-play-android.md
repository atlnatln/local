---
title: "MathLock Play — Android"
created: 2026-05-07
updated: 2026-05-09
type: project
tags: [mathlock-play, android, kotlin, games, auth]
related:
  - mathlock-play
  - mathlock-play-backend
  - mathlock-play-ai
  - sayi-yolculugu
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

## Crash Prevention (2026-05-02)

v1.0.67 sürümünde stabilite düzeltmeleri:
- **ProGuard:** Billing, Biometric, JS Bridge, MPAndroidChart için `keep` kuralları eklendi — release build R8 kırılmaları önlendi
- **WebView Memory Leak:** `SayiYolculuguActivity`'de `onDestroy()`'da `webView.destroy()` + `removeAllViews()` eklendi
- **Handler Leak:** `pollForNewSet()` recursive polling'i activity-level `Handler`'a taşındı; `onDestroy()`'da `removeCallbacksAndMessages(null)` ile temizleniyor
- **BootReceiver:** Android 14 `ForegroundServiceStartNotAllowedException` riski `try/catch` ile kapatıldı
- **Firebase Crashlytics:** `com.google.firebase:firebase-crashlytics:18.6.4` + Google Services plugin 4.4.4 entegre edildi

## Sayı Hafızası — Yeni Oyun (2026-05-03)

ADR: [[adr-004-memory-game-integration]]

- **Teknoloji:** Native Kotlin + `ObjectAnimator` 3D kart çevirme (`rotationY`)
- **Oyun mantığı:** `MemoryGameEngine.kt` (View'dan bağımsız, unit testli)
- **Kilit açma:** Ebeveyn ayarlı tur sayısı (`memoryGameRequiredRounds`)
- **Zorluk:** Ebeveyn ayarlı kart çifti (`memoryGamePairCount`, 4-20)
- **Backend:** Offline (sunucu bağımlılığı yok)
- **Test:** 27/27 unit test geçti, cihaz testi başarılı

## Sayı Yolculuğu Progress Bug Fix (2026-05-03)

**Sorun:** Kilit aktive olduktan sonra Sayı Yolculuğu baştan başlıyordu.

**Kök Nedenler (4 adet):**
1. `onDestroy()`'da `completedLevelIds` + `cachedLevels` siliniyordu
2. `currentSetId` persist edilmediği için `fetchLevels()` her açılışta "yeni set" olarak algılıyordu
3. `loadLevelsIntoGame()`'de `isNewSet` mantığı `oldSetId=null` iken `true` dönüyordu → `forceClear=true` → WebView progress siliyordu
4. Fallback levels'te `completed_level_ids` inject edilmiyordu

**Düzeltmeler:**
- `onDestroy()`'daki `SecurePrefs.remove()` kaldırıldı
- `currentSetId` `SecurePrefs`'e kaydediliyor (`KEY_CURRENT_SET_ID`)
- `fetchLevels()` ve `loadLevelsIntoGame()`'de `isNewSet` mantığı düzeltildi: `oldSetId != null` şartı eklendi
- Fallback levels'te `injectCompletedIds()` çağrılıyor, `forceClear=false`

## Sayı Yolculuğu Auth Fix (2026-05-03)

**Sorun:** `SayiYolculuguActivity` backend'e istek attığında `403 Forbidden` alıyordu.

**Kök Neden:** `SayiYolculuguActivity` kendi `RealApiClient()` instance'ını oluşturuyordu, ancak bu instance üzerinde `setAuthToken()` çağrılmamıştı. `AccountManager`'ın `apiClient`'ı ayrı bir instance'dı; `SayiYolculuguActivity`'nin client'ı yetkilendirilmemişti.

**Düzeltme:** Tüm ağ çağrıları öncesinde (`onCreate()`, `fetchLevels()`, `uploadLevelProgress()`) token alınıp `apiClient.setAuthToken()` ile atanır:

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/mathlock/.../SayiYolculuguActivity.kt
val accountManager = AccountManager(this)
apiClient.setAuthToken(accountManager.getAccessToken())

// Token refresh sonrası
token = accountManager.getAccessToken()
if (token.isNullOrBlank()) { token = accountManager.getOrRegister() }
apiClient.setAuthToken(token)
```

> Backend `?device_token=<uuid>` query parametresinden `Authorization: Device <signed_token>` header'ına geçmiştir. Android `AccountManager` zaten imzalı token üretiyordu, sadece yeni client instance'ına atanmamıştı.

## AccountManager First-Run Auth Fix (2026-05-03)

**Sorun:** Uygulama ilk kez açıldığında (`getAccessToken()` boşsa) `AccountManager.getOrRegister()` raw `device_token` döndürüyordu. `Authorization: Device <raw_uuid>` header'ı backend tarafından `403 Forbidden` olarak reddediliyordu.

**Kök Neden:** `getOrRegister()` kayıt sonrası `access_token` (imzalı) değerini kaydediyor ama `return token` (raw) yazıyordu.

**Düzeltme:**

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/akn/mathlock/util/AccountManager.kt
val accessToken = response.body.optString("access_token", token)
prefs.edit()
    .putString(KEY_DEVICE_TOKEN, token)
    .putString(KEY_ACCESS_TOKEN, accessToken)
    .apply()
return accessToken  // ← önceki: return token (raw UUID)
```

Bu, `MathChallengeActivity`, `SettingsActivity`, `SayiYolculuguActivity` ve tüm `getOrRegister()` çağıranlar için geçerlidir.

## Android Tip İsimlendirme Fix (2026-05-07)

**Sorun:** `StatsDashboardActivity.kt` ve `PerformanceReportActivity.kt` içindeki `TYPE_LABELS` sözlük anahtarları hâlâ Türkçe karaktersiz isimler (`siralama`, `cikarma`, `carpma`, `bolme`, `eksik_sayi`, `karsilastirma`) kullanıyordu. Bu, backend'den gelen Türkçe karakterli tip isimleriyle (`sıralama`, `çıkarma`, `çarpma`, `bölme`, `eksik_sayı`, `karşılaştırma`) eşleşmiyordu → istatistik ve rapor ekranlarında tip adları boş görünüyordu.

**Düzeltme:** Her iki dosyadaki `TYPE_LABELS` haritası tamamen Türkçe karakterli standartlara çevrildi. Eksik tip anahtarları (`kesir`, `problem`, `örüntü`) eklendi.

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/akn/mathlock/StatsDashboardActivity.kt
private val TYPE_LABELS = mapOf(
    "toplama" to "Toplama",
    "çıkarma" to "Çıkarma",        // ← önceki: "cikarma"
    "çarpma" to "Çarpma",          // ← önceki: "carpma"
    "bölme" to "Bölme",            // ← önceki: "bolme"
    "sıralama" to "Sıralama",      // ← önceki: "siralama"
    "eksik_sayı" to "Eksik Sayı",  // ← önceki: "eksik_sayi"
    "karşılaştırma" to "Karşılaştırma", // ← önceki: "karsilastirma"
    "sayma" to "Sayma",
    "kesir" to "Kesir",            // ← yeni eklendi
    "problem" to "Problem",        // ← yeni eklendi
    "örüntü" to "Örüntü",          // ← yeni eklendi
    ...
)
```

## Sayı Yolculuğu child_id Retry Fix (2026-05-03)

**Sorun:** `fetchLevels()` ve `uploadLevelProgress()` `child_id` mismatch yüzünden 404 alıyordu; retry yoktu. `uploadLevelProgress` hata durumunda callback çağırmıyordu → kullanıcı set bitince yeni set alamıyordu.

**Kök Neden:** Telefonda kayıtlı `child_id` (örn. 67) ile backend'deki cihazın bağlı olduğu `child_id` (örn. 39) farklıydı. App yeniden yüklenince yeni cihaz kaydı oluşuyor, eski `child_id` localde kalıyordu.

**Düzeltmeler:**
- `fetchLevels()`: `child_id` ile 404 alırsa `child_id` olmadan tekrar dener; başarılı olursa local `activeChildId` sıfırlanır
- `uploadLevelProgress()`: Aynı retry mantığı + callback her durumda çağrılır (hata da olsa)

```kotlin
// file: projects/mathlock-play/app/src/main/java/com/akn/mathlock/SayiYolculuguActivity.kt
private fun fetchLevels(): String? {
    fun tryFetch(withChildId: Boolean): String? { ... }
    var result = tryFetch(true)
    if (result == null && childId > 0) {
        result = tryFetch(false)
        if (result != null) prefManager.activeChildId = 0
    }
}
```

---

> Backend auth ve API detayları için bkz. [[mathlock-play-backend]]
