# Geliştirici Test Kılavuzu — Mathlock Play Kredi Sistemi

Gerçek para ödemeden kredi/IAP sistemini test etmenin 3 yöntemi.

---

## Yöntem 1 — Debug Token (EN HIZLI)

Android uygulama `DEBUG` build'de `BillingManager.launchTestPurchase(productId)` metodunu
çağırabilir. Bu, Google Play diyalogu açmadan sahte bir token üretir ve backend'e gönderir.
Backend de `DEBUG_TEST_TOKEN_` prefix'li tokenları (yalnızca `settings.DEBUG=True` iken)
Google Play API'yi çağırmadan kabul eder.

### Android Tarafı

```kotlin
// Activity veya Fragment içinde — SADECE DEBUG BUILD'DE
if (BuildConfig.DEBUG) {
    creditManager.billingManager?.launchTestPurchase("kredi_5")
}
```

Ya da `BillingManager` üzerinden doğrudan:

```kotlin
billingManager.launchTestPurchase("kredi_10")  // 10 kredi = 550 toplam soru
```

### Backend Tarafı

`backend/mathlock_backend/settings.py` içinde `DEBUG = True` olduğundan emin ol
(geliştirme ortamında varsayılan budur). Docker ile çalıştırırken:

```bash
cd projects/mathlock-play
# DEBUG=True zaten settings.py'de default
docker compose up --build
```

### Test Senaryosu

```
1. Uygulamayı debug build ile çalıştır (Android Studio → Run)
2. Ana ekranda "Kredi Satın Al" butonuna değil, test butonuna bas
3. Logcat'te şunu görürsün:
   D/BillingManager: 🧪 DEV TEST PURCHASE: product=kredi_5, token=DEBUG_TEST_TOKEN_kredi_5_1234567890
4. Backend'de credits 5 artar
5. Sonraki 50 soru seti çekilir (ücretsiz set kullanıldıysa)
```

---

## Yöntem 2 — Google Play License Testing (ÜCRETSİZ GERÇEK TOKEN)

Bu yöntemde gerçek Google Play satın alma akışı çalışır (asıl diyalog açılır),
ancak hiç para çekilmez. Backend doğrulaması da gerçek Play token'ı doğrular.

### Adımlar

1. **Play Console** → [play.google.com/console](https://play.google.com/console) → Uygulamayı seç
2. Sol menü → **Setup → License testing**
3. **"Add Gmail account"** → Kendi geliştirici Gmail hesabını ekle
4. **Save** deyin — etkin olması birkaç dakika alabilir

### Sınırlamalar

- Hesap **aynı test cihazına** login olmalı
- Uygulama Play Store'a en az bir kez (Internal Test olarak bile) yüklenmeli veya
  `.apk` directly install edilebilir + hesap Play'de tanımlı olmalı
- İlk 15 dakikada token bazen aktif olmayabilir — ekledikten sonra biraz bekle

### Test Senaryosu

```
1. Test cihazına kendi Gmail hesabınla giriş yap (License Tester olarak eklenmiş)
2. Uygulamada "Kredi Satın Al" → normal akış
3. Ödeme ekranında "TEST (no charge)" veya "Test card, always approves" göreceksin
4. Satın alma tamamlanır, gerçek token üretilir
5. Backend /api/mathlock/purchase/verify/ endpoint'i Play API'yi çağırır → geçerli döner
6. Kredi bakiyene eklenir
```

---

## Yöntem 3 — Internal Test Track (EN GERÇEKÇI TEST)

Uygulamayı Play Console'da Internal Test kanalına yükle. Test grubu üyeleri
sandbox ortamında uygulamayı indirir ve test satın alma yapar.

### Adımlar

1. `./gradlew bundleRelease` veya `./gradlew assembleRelease`
2. Play Console → Testing → **Internal testing** → Create release
3. APK/AAB'yi yükle
4. **Testers** sekmesi → Google Group veya e-posta listesi ekle
5. Test kullanıcıları linki kabul edince sandbox IAP kullanabilir

Bu yöntem en kapsamlı testtir ama en uzun süreyi alır.

---

## Yöntem 4 — Backend'i Doğrudan Test Etme (curl)

Android uygulaması olmadan sadece API endpoint'lerini test et:

```bash
BASE="http://localhost:8003/api/mathlock"

# 1. Cihaz kaydet
TOKEN=$(curl -s -X POST $BASE/register/ \
  -H "Content-Type: application/json" \
  -d '{"installation_id": "test-device-001"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['device_token'])")

echo "Device token: $TOKEN"

# 2. Debug token ile kredi satın al
curl -s -X POST $BASE/purchase/verify/ \
  -H "Content-Type: application/json" \
  -d "{\"device_token\": \"$TOKEN\", \"purchase_token\": \"DEBUG_TEST_TOKEN_kredi_5_12345\", \"product_id\": \"kredi_5\"}" | python3 -m json.tool

# 3. Bakiyeyi kontrol et
curl -s "$BASE/credits/?device_token=$TOKEN" | python3 -m json.tool

# 4. Kredi kullan (soru seti al)
curl -s -X POST $BASE/credits/use/ \
  -H "Content-Type: application/json" \
  -d "{\"device_token\": \"$TOKEN\", \"child_name\": \"Test Çocuk\", \"stats\": {}}" | python3 -m json.tool
```

---

## Hızlı Başlangıç

```bash
# Backend'i başlat
cd projects/mathlock-play
docker compose up -d

# Testleri çalıştır
cd backend
pip install -r requirements.txt
python manage.py test credits -v 2

# Android unit testleri
cd ..
./gradlew test
```

---

## Sık Sorulan Sorular

**S: `launchTestPurchase()` release build'de çalışır mı?**
H: Hayır. `ApplicationInfo.FLAG_DEBUGGABLE` kontrolü yapılır; release build'de sessizce return eder.

**S: Backend'de debug token üretimde kabul edilir mi?**
H: Hayır. `settings.DEBUG=False` olunca `DEBUG_TEST_TOKEN_` prefix'li token'lar 403 döner.

**S: License Testing hesabımı silerseniz ne olur?**
H: Mevcut token'lar geçerliliğini kaybetmez, sadece yeni test satın almaları için bloke edilir.

**S: Kaç adet test satın alması yapabilirim?**
H: License Testing ile sınırsız. Internal Test ile de sınırsız (gerçek para yok).
