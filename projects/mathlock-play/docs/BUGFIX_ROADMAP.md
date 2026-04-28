# MathLock Play — Bug Fix Roadmap

> Tarih: 19 Nisan 2026  
> Son güncelleme: 26 Nisan 2026 — Celery, i18n, BaseActivity migration eklendi

---

## Faz 1: Progress Sayımı (P1 — Kritik) ✅ ÇÖZÜLDÜ

**Sorun**: 10 matematik sorusu çözülüyor ama 5 tanesi çözülmüş görünüyor.

**Kök Neden**: Normal modda kilit açılınca (`unlockAndLaunchApp()`) `uploadProgress()` çağrılmıyor. Çözülen sorular SharedPreferences'a `pending_solved` olarak yazılıyor ama sunucuya gönderilmiyor. Ancak bir **sonraki** `MathChallengeActivity` açılışında (`onCreate`) yükleniyor. Birden fazla oturumda pending ID'ler birbirini eziyor.

**Fix**: `unlockAndLaunchApp()` ve `onDestroy()` içinde pending progress'i upload et.

**Dosyalar**:
- `MathChallengeActivity.kt` — `unlockAndLaunchApp()` (satır ~662) + `onDestroy()` (satır ~742)

**Durum**: ✅ Çözüldü — `unlockAndLaunchApp()` içinde `Thread { uploadProgress() }.start()` mevcut, `onDestroy()` içinde backup upload eklendi.

---

## Faz 2: Email ile Kayıtta Duplicate Profil (P1 — Kritik) ✅ ÇÖZÜLDÜ

**Sorun**: Uygulama silinip tekrar yüklendiğinde, email ile kayıt olunca eski çocuk profili aktif olarak geliyor AMA ek olarak boş bir "Çocuk" profili de aktif olarak geliyor.

**Fix**: `register_email()` içinde transfer sonrası boş varsayılan "Çocuk" profili temizleniyor.

**Dosyalar**:
- `backend/credits/views.py` — `register_email()` (satır ~1150)

**Durum**: ✅ Çözüldü — `transferred_children.exists()` kontrolü ile boş `name="Çocuk", total_shown=0, total_correct=0` profili otomatik siliniyor.

---

## Faz 3: İzin Akışı Optimizasyonu (P2 — UX)

**Sorun**: İzin kurulumu çok karmaşık, tekrar eden döngü var. Kullanıcı aynı izinleri 2 kez veriyor (overlay ve usage access tekrar soruluyor).

**Kök Neden**: `onResume()` içinde `permissionCheckPending` ve `xiaomiStepPending` flag'leri koordinesiz çalışıyor. Xiaomi wizard adımları sistem ayarlarına gönderdiğinde, geri dönüşte `onResume` çalışıyor ve her iki flag'i kontrol ediyor. Xiaomi Step 3'te "Uygulama Ayarlarına Git" → geri dönüşte `checkAndRequestPermissions()` baştan çalışıyor → overlay ve usage access tekrar kontrol ediliyor.

**Akış (buggy)**:
```
1. Usage Access → ✓
2. Overlay → ✓
3. Xiaomi Autostart → ayarlara git → geri dön
4. Xiaomi Popup → ayarlara git → geri dön
5. Xiaomi Background → uygulama ayarlarına git → geri dön
6. onResume → checkAndRequestPermissions() TEKRAR çalışır
7. Overlay tekrar soruluyor (döngü)
8. Usage Access tekrar soruluyor (döngü)
```

**Fix — Kısa vadeli**:
1. `onResume()` içinde `xiaomiStepPending > 0` iken `permissionCheckPending` kontrolünü atla (`return` ekle)
2. `startLockService()` çağrıldığında `permissionCheckPending = false` set et
3. Xiaomi Step 3'te ayarlardan dönüşte `checkAndRequestPermissions()` çağrılmasını engelle

**Fix — Uzun vadeli**:
Tüm izin adımlarını bağımsız `SetupWizardActivity` içine taşı. Her adım bittiğinde SharedPreferences'a kaydet. Geri dönüşte sadece tamamlanmamış adımlar gösterilsin.

**Dosyalar**:
- `SettingsActivity.kt` — `onResume()` (satır ~42), `checkAndRequestPermissions()`, `showXiaomiSetupWizard()`

**Durum**: [ ] Yapılacak — Kısa vadeli fix uygulanabilir; uzun vadeli `SetupWizardActivity` ileri vade.

---

## Faz 4: Reliability & i18n (P1 — Kritik) ✅ ÇÖZÜLDÜ

**Sorunlar ve çözümleri:**

### 4.1 RenewalLock TTL 15 dk → 20 dk
**Yer:** `credits/views.py`  
**Açıklama:** AI üretimi ortalama 10 dk sürüyordu; 15 dk TTL yetersizdi. 20 dk'ya çıkarıldı + 2×TTL (40 dk) stale lock cleanup eklendi.  
**Durum:** ✅ Çözüldü

### 4.2 AI Üretimi Thread Crash → Celery
**Yer:** `credits/views.py`, `credits/tasks.py`  
**Açıklama:** `threading.Thread` kullanımı sunucu crash/restart durumunda yeni set üretimini kaybediyordu. `generate_level_set` ve `generate_question_set` Celery task'ları ile Redis broker üzerinden reliable işlem sağlandı. `max_retries=3`, kilit serbest bırakma `finally`'de.  
**Durum:** ✅ Çözüldü

### 4.3 WebView Memory Leak
**Yer:** `SayiYolculuguActivity.kt`  
**Açıklama:** Activity destroy edildiğinde WebView `localStorage` ve `SharedPreferences` temizlenmiyordu. `onDestroy()` override eklendi.  
**Durum:** ✅ Çözüldü

### 4.4 Android i18n (tr/en)
**Yer:** Tüm UI katmanı  
**Açıklama:** `values-en/strings.xml` (138+ string), `PreferenceManager.appLocale`, `LocaleHelper.kt`, `BaseActivity.kt` ile tüm Activity'ler locale-aware oldu. `game.html` `I18N` sözlüğü ile WebView içi de localize edildi.  
**Durum:** ✅ Çözüldü

### 4.5 Backend i18n (gettext_lazy)
**Yer:** `credits/views.py`, `settings.py`  
**Açıklama:** ~80 semantic key `gettext_lazy` ile çevrildi. `.po/.mo` dosyaları tr/en için oluşturuldu. `compilemessages` deploy'da otomatik.  
**Durum:** ✅ Çözüldü

---

## Not: Şifresiz Email Kaydı (Tasarım Kararı)

Email ile kayıt olurken şifre istenmiyor. Bu **kasıtlı bir tasarım**:
- Kimlik doğrulama `device_token` (UUID) bazlı
- Email sadece hesap kurtarma ve kredi satın alma için opsiyonel
- Telefonundaki Google hesabı zaten doğrulanmış

İleri vadede SMS/email OTP doğrulaması düşünülebilir ama şu an için kritik değil.
