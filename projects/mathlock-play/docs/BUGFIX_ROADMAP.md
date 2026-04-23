# MathLock Play — Bug Fix Roadmap

> Tarih: 19 Nisan 2026
> Tespit edilen: 4 sorun, 3 faz

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

**Durum**: [ ] Yapılacak

---

## Not: Şifresiz Email Kaydı (Tasarım Kararı)

Email ile kayıt olurken şifre istenmiyor. Bu **kasıtlı bir tasarım**:
- Kimlik doğrulama `device_token` (UUID) bazlı
- Email sadece hesap kurtarma ve kredi satın alma için opsiyonel
- Telefonundaki Google hesabı zaten doğrulanmış

İleri vadede SMS/email OTP doğrulaması düşünülebilir ama şu an için kritik değil.
