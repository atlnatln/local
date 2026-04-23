# MathLock Google Play Yol Haritası

Durum tarihi: 23 Nisan 2026

> **Güncelleme (23 Nisan 2026):** Phase 1 kritik bugfix'ler tamamlandı. Progress sayımı bug'ı düzeltildi, kredi sistemi Android entegrasyonu tamamlandı, duplicate profil zaten çözülmüştü. kimi-cli migration tamamlandı.
>
> **Güncelleme (5 Nisan 2026):** Internal testing başarıyla tamamlandı! Uygulama Play Console'a yüklendi ve telefondan indirilip test edildi.
>
> **Güncelleme (25 Mart 2026 — akşam):** Kısa vadeli yol haritasının 5.1-5.4 adımları tamamlandı. `projects/mathlock-play` altında Play uyumlu ayrı proje oluşturuldu. Detaylar aşağıda.

## Tamamlanan İşler (5.1 → 5.4 ve Kredi Sistemi)

### ✅ 5.1A — Self-update sistemi kaldırıldı
- `UpdateChecker.kt` tamamen silindi
- `REQUEST_INSTALL_PACKAGES` izni manifestten çıkarıldı
- `MainActivity.kt`'den tüm OTA güncelleme kodu temizlendi
- `BootReceiver`'dan `MY_PACKAGE_REPLACED` tetikleyicisi kaldırıldı
- `FileProvider` manifestten çıkarıldı, `file_provider_paths.xml` silindi

### ✅ 5.1B — HTTP → HTTPS geçişi tamamlandı
- Tüm URL'ler `https://mathlock.com.tr/mathlock/data` adresine güncellendi
- `StatsTracker.kt`, `QuestionManager.kt`, `TopicHelper.kt` güncellendi
- `network_security_config.xml` — cleartext istisnası kaldırıldı, sadece HTTPS
- `mathlock.com.tr` alan adı alındı (DNS propagasyonu bekleniyor)
- Nginx HTTPS config hazırlandı: `website/nginx-mathlock.conf`

### ✅ 5.1C — KILL_BACKGROUND_PROCESSES bağımlılığı kaldırıldı
- `KILL_BACKGROUND_PROCESSES` izni manifestten çıkarıldı
- `AppLockService.kt`'den `killApp()` metodu ve `ActivityManager` import'u silindi
- Timer expire olduğunda artık HOME intent + relock kullanılıyor (uygulama öldürme yok)
- Settings string'i güncellendi: "Uygulamayı kapat" → "Ana ekrana dön ve kilitle"

### ✅ 5.1E — Monitoring app beyanı eklendi
- `AndroidManifest.xml`'e `isMonitoringTool = child_monitoring` meta-data eklendi

### ✅ 5.2 — Kullanıcı verisi ve izin akışı
- `DisclosureActivity.kt` oluşturuldu (Prominent Disclosure ekranı)
- Uygulama listesi, kullanım istatistikleri, overlay ve performans verisi açıkça anlatılıyor
- İlk çalıştırmada otomatik gösteriliyor, kabul etmeden devam edilemiyor
- Gizlilik politikası linki disclosure ekranından erişilebilir

### ✅ 5.3 — Veri minimizasyonu
- Uygulama listesi asla sunucuya gönderilmiyor (privacy policy'de belirtildi)
- Stats payload'da kişisel tanımlayıcı yok
- Tüm data safety beyanları dokümante edildi

### ✅ 5.4 — Yayın için dış varlıklar
- **Privacy Policy** sayfası: `website/privacy.html` (mathlock.com.tr/privacy)
- **Support** sayfası: `website/support.html` (mathlock.com.tr/support)
- **Ana sayfa**: `website/index.html` (mathlock.com.tr)
- **Destek e-postası**: support@mathlock.com.tr
- **Store listing taslağı**: `docs/play-store-listing.md`
- **Data Safety form taslağı**: `docs/play-store-listing.md` içinde
- **Reviewer bilgi notu**: `docs/play-store-listing.md` içinde
- **Permission declaration taslağı**: `docs/play-store-listing.md` içinde

### ✅ Kredi Sistemi — Tüketilebilir Ürün (Consumable In-App Purchase)

Hedef: İlk 50 soru ücretsiz; daha fazla isteyince AI devreye girer; 10 kredi = 550 toplam soru.

#### Backend (`backend/`)
- Django REST API — port 8003
- **models.py**: `Device`, `ChildProfile`, `CreditBalance`, `PurchaseRecord`, `QuestionSet`
- **google_play.py**: `verify_purchase()` → Google Play Developer API v3 ile token doğrulama
- **views.py**:
  - `POST /api/mathlock/register/` — Cihaz kaydı
  - `POST /api/mathlock/purchase/verify/` — Satın alma doğrulama + kredi ekleme
  - `GET  /api/mathlock/credits/` — Kredi bakiyesi sorgulama
  - `POST /api/mathlock/credits/use/` — 1 kredi düş, yeni 50 soru döndür (kredi yoksa son set tekrar)
  - `POST /api/mathlock/stats/` — Çocuğun performans istatistikleri kayıt
- **Dockerfile** + **docker-compose.yml**: Hazır (SQLite dev, PostgreSQL prod)
- Çocuk başına kişiselleştirilmiş veri (doğruluk, zorluk seviyesi, tip bazlı istatistikler)

#### Frontend (Android)
- `app/build.gradle.kts` → `billing-ktx:6.2.1` eklendi
- **billing/BillingManager.kt**:
  - `BillingClient` bağlantı + `PurchasesUpdatedListener`
  - `queryProducts()` — Ürün detayları (`kredi_1`, `kredi_5`, `kredi_10`)
  - `launchPurchase(activity, productId)` — Satın alma akışı başlat
  - `consumePurchase(purchaseToken)` — Ürünü tekrar satın alınabilir yap
  - `getProductPrice(productId)` — Google Play fiyatını getir
- **util/MathLockApi.kt**:
  - `registerDevice()`, `verifyPurchase()`, `getCredits()`, `useCredit()`, `uploadStats()`
  - Tüm istekler `https://mathlock.com.tr/api/mathlock/` üzerinden
- **util/CreditManager.kt**:
  - Cihaz kaydı (UUID installation_id), device_token yönetimi
  - `initBilling()` → Satın alma sonucunu backend'e gönder → başarılıysa `consumePurchase()`
  - `launchPurchase(activity, productId)` — UI'dan çağrılacak
- **util/QuestionManager.kt** (genişletildi):
  - `loadFromBackend(questionsJson)` — Backend'den gelen soru setini yükle
  - `startRepeating()` — Kredi bitince son seti döngüye al
  - `nextQuestionOrRepeat()` — Tekrar modunda döngüsel soru verir
  - `isRepeating` property eklendi

#### Kredi Mantığı Özeti
| Durum | Davranış |
| --- | --- |
| İlk kullanım | 50 ücretsiz soru (VPS statik JSON) |
| 50 soru biter + kredi var | Backend `POST /credits/use/` → AI üretir → 50 yeni soru |
| 50 soru biter + kredi yok | Backend son seti döndürür → `startRepeating()` → sonsuz döngü |
| Satın alma | `BillingManager` → PurchaseToken → backend verify → kredi ekle → consume |
| 10 kredi paketi | 10×50 = 500 AI soru + 50 ücretsiz = **550 toplam** |

### ✅ Phase 1 — Kritik Bugfix'ler (23 Nisan 2026)

#### 1A. Progress Sayımı Bug'ı
- `MathChallengeActivity.onDestroy()` içinde `questionManager.uploadProgress()` backup eklendi.
- `unlockAndLaunchApp()`'daki `Thread` + `finish()` kombinasyonunun güvenlik açığı giderildi.

#### 1B. Duplicate Profil Bug'ı
- `backend/credits/views.py` — `register_email()` içinde boş varsayılan "Çocuk" profili otomatik temizleniyor (zaten mevcuttu, doğrulandı).

#### 1C. Kredi Sistemi Android Entegrasyonu
- `CreditApiClient.kt` oluşturuldu (`useCredit()` API çağrısı).
- `MathChallengeActivity.onSetComplete()` içinde `creditClient.useCredit()` entegre edildi.
- `StatsTracker.buildStatsJson()` public yapıldı (kredi API'sine stats göndermek için).

#### Bekleyen Entegrasyon Adımları
1. ~~`MathChallengeActivity.onSetComplete()` içinde `useCredit()` çağrısı~~ ✅ Tamamlandı
2. ~~`StatsTracker.uploadStats()` backend entegrasyonu~~ ✅ Tamamlandı
3. Google Play Console'da ürün ID'lerini tanımla: `kredi_1`, `kredi_5`, `kredi_10` ⏳
4. `google-service-account.json` dosyasını VPS'e yerleştir ⏳
5. Satın alma UI ekranı (SettingsActivity veya ayrı ShopActivity) ⏳

### Play sürümü teknik özet

| Değişiklik | Detay |
| --- | --- |
| Proje | `projects/mathlock-play` |
| applicationId | `com.akn.mathlock.play` |
| versionCode / versionName | 2 / 1.0.1 |
| compileSdk / targetSdk | 35 / 35 |
| Kaldırılan izinler | REQUEST_INSTALL_PACKAGES, KILL_BACKGROUND_PROCESSES |
| Kaldırılan dosyalar | UpdateChecker.kt, file_provider_paths.xml |
| Eklenen | DisclosureActivity.kt, activity_disclosure.xml, isMonitoringTool |
| URL'ler | https://mathlock.com.tr (HTTP yok) |
| R8 (minify) | Release build'de aktif |

## Bekleyen İşler

### 5.5 — Hesap ve test süreci (DNS propagasyonu sonrası)
1. ~~DNS propagasyonunu bekle → SSL sertifikası al → web sitesini deploy et~~ ✅ (mathlock.com.tr yayında)
2. ~~Play Console hesabını ve kimlik doğrulamayı tamamla~~ ✅
3. ~~Release keystore oluştur ve imzalı AAB üret~~ ✅ (keystore.jks, compileSdk=35, targetSdk=35)
4. ~~Internal testing ile smoke test yap~~ ✅ (versionCode=2, internal test track yayında)
5. ~~Phase 1 kritik bugfix'ler~~ ✅ (23 Nisan 2026 — progress bug, duplicate profil, kredi entegrasyonu)
6. Closed testing'i en az 12 tester ile başlat ⏳
7. 14 gün continuous opt-in sürecini tamamla ⏳
8. Production access başvurusunu yap ⏳

#### 5.5 Ek Notlar (5 Nisan 2026)
- **Keystore**: `projects/mathlock-play/keystore.jks` (alias: mathlock-play)
- **Play Console App ID**: 4973393885899325613
- **Internal Test Track ID**: 4701209456522383356
- **Opt-in linki**: `https://play.google.com/apps/internaltest/4701209456522383356`
- **Test edilen cihaz**: Xiaomi (telefondan başarıyla indirildi ve çalıştırıldı)

### 5.6 — Onboarding/İzin akışı iyileştirmesi (YENİ)
1. POST_NOTIFICATIONS iznini ilk kurulumdan ertele (çekirdek fonksiyon için gereksiz)
2. SetupWizardActivity oluştur (rehberli adım adım izin sihirbazı)
3. Batarya optimizasyonunu opsiyonel bonus adıma taşı
4. İlk kurulumda zorunlu adım sayısını 2'ye indir (Usage Stats + Overlay)

Detaylı plan: `docs/ONBOARDING_IYILESTIRME_PLANI.md`

---

Bu doküman, MathLock uygulamasını Google Play'e yükleyip ilk denemede veya mümkün olan en az red döngüsüyle kabul alma hedefi için hazırlanmış kısa, orta ve uzun vadeli yol haritasıdır.

Bu plan iki kaynağın birleşimidir:

- MathLock kod tabanının mevcut durumu
- Google Play'in 25 Mart 2026 itibarıyla güncel yardım ve politika sayfaları

## 1. Yönetici Özeti

MathLock şu haliyle doğrudan Play'e gönderilirse yüksek red riski taşır. Bunun ana sebepleri şunlar:

1. ~~Uygulama kendi APK'sını HTTP üzerinden indirip kurmaya çalışıyor.~~ ✅ Çözüldü
2. Uygulama geniş paket görünürlüğü kullanıyor. (QUERY_ALL_PACKAGES — parental control gerekçelendirildi)
3. ~~Uygulama diğer uygulamaları kapatma davranışına dayanıyor.~~ ✅ Çözüldü
4. ~~Hassas veri için belirgin açıklama ve onay akışı henüz görünmüyor.~~ ✅ Çözüldü
5. ~~Ebeveyn denetimi olarak doğru Play konumlandırması hazır değil.~~ ✅ Çözüldü

En güvenli strateji şu:

- ~~Play için ayrı bir sürüm üret.~~ ✅ `projects/mathlock-play`
- ~~Play sürümünden self-update davranışını kaldır.~~ ✅
- ~~Tüm veri trafiğini HTTPS'e taşı.~~ ✅ mathlock.com.tr
- ~~İzinleri minimuma indir, deklarasyon ve in-app disclosure hazırla.~~ ✅
- ~~Ebeveyn odaklı parental control olarak konumlandır.~~ ✅
- Kapalı test ve production access sürecini yürüt. ⏳ Sırada

## 2. Resmi Olarak Doğrulanan Güncel Gerçekler

### 2.1 Kişisel hesap test şartı artık 20 değil 12 tester

Google'ın güncel yardım sayfasına göre yeni kişisel geliştirici hesaplarında üretime çıkmadan önce:

- en az 12 kapalı test kullanıcısı gerekir
- bu kullanıcıların en az son 14 gün boyunca sürekli opt-in durumda kalması gerekir
- ardından Play Console içinden production access başvurusu yapılır
- başvuru sonrası inceleme genellikle 7 gün veya daha kısa sürer

Önemli sonuç:

- Eski 20 tester notları artık birincil referans olmamalı.
- Yeni kişisel hesap için doğru baz çizgi 12 tester + 14 gün continuous opt-in.

Kaynaklar:

- https://support.google.com/googleplay/android-developer/answer/14151465?hl=en
- https://support.google.com/googleplay/android-developer/answer/16944162?hl=en

### 2.2 Pre-registration herkes için hemen açık değil

Google'ın güncel metninde, yeni kişisel hesaplar için production ve pre-registration özelliklerinin test şartı tamamlanana kadar kapalı olabildiği açıkça belirtiliyor.

Önemli sonuç:

- Eski notlardaki pre-registration stratejisi yeni kişisel hesapta ilk adım olarak garanti değil.
- Önce kapalı test ve production access engelini aşmak gerekir.

### 2.3 QUERY_ALL_PACKAGES yüksek riskli ve deklarasyon gerektiriyor

Google, cihazdaki yüklü uygulama envanterini personal and sensitive user data olarak görüyor.

Kurallar:

- mümkünse targeted package visibility kullanılmalı
- broad visibility sadece çekirdek işlev bunu gerçekten gerektiriyorsa kabul edilebilir
- Play Console'da izin deklarasyonu gerekir
- bu veri reklam veya analitik amaçlı kullanılamaz

Kaynaklar:

- https://support.google.com/googleplay/android-developer/answer/10158779?hl=en
- https://support.google.com/googleplay/android-developer/answer/9888170?hl=en

### 2.4 REQUEST_INSTALL_PACKAGES self-update için kullanılamaz

Google'ın güncel iznine göre bu izin ancak uygulamanın ana işlevi paket gönderme, alma veya kullanıcı başlatmalı APK kurulumu ise kullanılabilir.

Özellikle yasaklanan nokta:

- uygulamanın kendini güncellemesi
- işlevini APK indirerek değiştirmesi

Önemli sonuç:

- MathLock'ın VPS'ten APK indirip kurma yaklaşımı Play sürümünde kaldırılmalıdır.

Kaynaklar:

- https://support.google.com/googleplay/android-developer/answer/12085295?hl=en
- https://support.google.com/googleplay/android-developer/answer/9888170?hl=en

### 2.5 Monitoring uygulamaları için isMonitoringTool işareti önemli

Parental control ve child monitoring çekirdek işlevliyse Google manifest içinde isMonitoringTool metadata kullanımını bekliyor.

Parental control için uygun değer:

- child_monitoring

Kaynak:

- https://support.google.com/googleplay/android-developer/answer/12955211?hl=en

## 3. MathLock'ın Mevcut Teknik Durumu

Kod incelemesine göre mevcut tablo:

| Alan | Mevcut durum | Play riski | Sonuç |
| --- | --- | --- | --- |
| Paket görünürlüğü | QUERY_ALL_PACKAGES manifestte var | Yüksek | Deklarasyon veya mimari daraltma gerekli |
| Uygulama kapatma | KILL_BACKGROUND_PROCESSES manifestte var, servis killBackgroundProcesses çağırıyor | Çok yüksek | Play sürümünde kaldırılması kuvvetle önerilir |
| Self-update | REQUEST_INSTALL_PACKAGES var, UpdateChecker APK indirip kuruyor | Çok yüksek | Play sürümünde tamamen kaldırılmalı |
| Ağ güvenliği | 89.252.152.222 için cleartext HTTP açık | Çok yüksek | HTTPS zorunluya yakın seviyede kritik |
| Veri aktarımı | questions.json, topics.json, stats.json HTTP ile gidip geliyor | Yüksek | Hassas veri politikası ve güvenlik riski |
| Foreground service | specialUse FGS kullanılıyor | Orta-Yüksek | Play listing + deklarasyon + açık gerekçe gerekir |
| Monitoring beyanı | isMonitoringTool yok | Orta-Yüksek | Parental control stratejisi seçilirse eklenmeli |
| Gizlilik varlıkları | Repo içinde yayın hazır privacy policy / support page görünmüyor | Yüksek | Zorunlu yayın öncesi eksik |
| Çocuk verisi stratejisi | Eğitim performansı ve uygulama listesi işleniyor | Yüksek | Veri minimizasyonu ve ebeveyn onayı tasarlanmalı |

## 4. Stratejik Konumlandırma Kararı

MathLock'ı Play'de kabul ettirmenin anahtarı teknik değil sadece konumlandırma da.

### Önerilen ana pozisyon

MathLock, mağazada şu şekilde anlatılmalı:

- ebeveynin kurduğu bir parental control aracı
- belirli uygulamaların açılmasını eğitsel görevle sınırlandıran bir çözüm
- çocuk için değil, ebeveyn tarafından yönetilen aile güvenliği ve eğitim destek aracı

Bu neden önemli:

- Uygulamayı doğrudan child-directed app gibi pazarlamak, Families ve COPPA yükünü ciddi artırır.
- Parental control olarak konumlamak, app monitoring ve broad app visibility gerekçesini daha savunulabilir hale getirir.

### Önerilen ürün ayrımı

İki dağıtım hattı olmalı:

1. Play sürümü
   - self-update yok
   - sadece Play üzerinden güncellenir
   - mümkün olan en az izin
   - politikaya en uyumlu davranış

2. Direkt APK / özel dağıtım sürümü
   - OTA davranışı gerekiyorsa sadece burada kalır
   - Play dışı kullanım için yönetilir

Bu ayrım yapılmadan tek kod tabanıyla hem Play hem özel APK stratejisini yürütmek gereksiz red üretir.

## 5. Kısa Vadeli Yol Haritası (0-2 Hafta)

Bu fazın amacı: "Play'e gönderilebilir aday" üretmek.

### 5.1 Bloklayıcı politika risklerini temizle

#### A. Self-update sistemini Play sürümünden çıkar

Yapılacaklar:

- UpdateChecker akışını Play flavor veya build variant arkasına al
- Play sürümünden REQUEST_INSTALL_PACKAGES iznini kaldır
- mağaza içi güncelleme için Play Core veya sadece Play dağıtım mekanizmasına güven
- deploy.sh içindeki OTA mantığını Play sürümünden ayır

Başarı ölçütü:

- Play manifestinde REQUEST_INSTALL_PACKAGES yok
- uygulama kendi APK'sını indirmiyor veya kurmuyor

#### B. HTTP'yi tamamen kapat, HTTPS'e geç

Yapılacaklar:

- 89.252.152.222 yerine alan adı + TLS kullan
- questions.json, topics.json, stats.json, version endpointleri HTTPS'e taşınsın
- network_security_config içindeki cleartext istisnası kaldır
- tüm veri aktarımı modern TLS ile çalışsın

Başarı ölçütü:

- cleartextTrafficPermitted istisnası yok
- tüm endpointler HTTPS

#### C. KILL_BACKGROUND_PROCESSES bağımlılığını kaldır

Yapılacaklar:

- kilit akışını "uygulamayı kapat" yerine "erişimi overlay / challenge gate ile kes" mantığına sabitle
- Play build'de killBackgroundProcesses çağrısını kaldır
- kullanıcı deneyimini bozmayacak, daha savunulabilir bir akış oluştur

Başarı ölçütü:

- Play sürüm manifestinde KILL_BACKGROUND_PROCESSES yok
- servis akışı bu izne ihtiyaç duymuyor

#### D. QUERY_ALL_PACKAGES kararını ver

Seçenek 1: İzni koru

- uygulama seçimi ekranı gerçekten cihazdaki tüm başlatılabilir uygulamaları göstermeye ihtiyaç duyuyorsa parental control çekirdek işlevi olarak savun
- Play Console permission declaration form hazırla
- privacy policy ve in-app disclosure içinde bunu açıkça anlat

Seçenek 2: İzni kaldır

- targeted package visibility yaklaşımına dön
- kullanıcıya manuel paket seçimi, launcher sorguları veya daha dar kapsamlı görünürlük ver

Öneri:

- İlk yayın kabul ihtimali için önce "gerekçeyi sağlam kur, olmuyorsa daralt" yaklaşımı kullanılmalı.
- Parental control konumlandırması korunacaksa izin için güçlü gerekçe hazırlanmalı.

#### E. Monitoring app beyanını hazırla

Yapılacaklar:

- manifestte isMonitoringTool metadata eklenmesini değerlendirin
- parental control stratejisi korunuyorsa child_monitoring değeriyle uyumlu hale getirin
- mağaza açıklaması ve gizlilik politikasında bunun açık karşılığı yazılsın

Not:

- Bu adım uygulamanın gerçekten izleme / parental control kategorisinde konumlandırılmasıyla birlikte ele alınmalı.

### 5.2 Kullanıcı verisi ve izin akışını düzelt

Yapılacaklar:

- ilk kurulumda tek ekranda değil, bağlamsal disclosure akışı kur
- Usage access için neden gerekli olduğunu açık söyle
- Overlay için neden gerekli olduğunu açık söyle
- Installed apps visibility / uygulama listesi işleme mantığını ebeveyne açıkça anlat
- batarya optimizasyonu muafiyeti isteğini zorlamadan, açıklamalı yönlendirme ile yap
- gizlilik politikasını uygulama içinden erişilebilir yap

Disclosure örneği mantığı:

- "MathLock, ebeveynin seçtiği uygulamaları kilitleyebilmek için cihazdaki uygulama listesini ve kullanım durumunu cihaz üzerinde işler ve asla sunucuya göndermez. Bu bilgiler reklam için de kullanılmaz. Sorular ile alakalı seçili (doğru yanlış oranı, çözme zamanı, kaç defada çözdüğü v.g) istatistikler yalnızca matematik performansını geliştirmek amacıyla güvenli bağlantı üzerinden sunucuya gönderilir."

### 5.3 Veri minimizasyonu kararlarını netleştir

Yapılacaklar:

- sunucuya çocuğun adı, soyadı, konumu gibi veri gitmeyecek
- sadece rastgele kullanıcı kimliği veya installation scoped ID kullanılacak
- stats payload gözden geçirilecek
- uygulama listesi mümkünse sunucuya hiç gönderilmeyecek
- AI kişiselleştirme anlatımı, veri minimizasyonu ile birlikte yazılacak

### 5.4 Yayın için gerekli dış varlıkları tamamla

Hazırlanacaklar:

- public privacy policy sayfası
- support / contact email
- uygulama tanıtım metni
- ekran görüntüleri
- feature graphic
- Google review için demo videosu
- Play reviewer notları

Privacy policy içinde mutlaka yer alması gerekenler:

- hangi veriler toplanıyor
- hangi veriler toplanmıyor
- installed app inventory ne amaçla kullanılıyor
- matematik performans verisi nasıl işleniyor
- veri saklama ve silme politikası
- ebeveyn iletişim ve veri silme kanalı

### 5.5 Hesap ve test sürecini başlat

Kısa vadede operasyonel sıra:

1. Play Console hesabını ve kimlik doğrulamayı tamamla.
2. Uygulamanın Play uyumlu ilk AAB sürümünü hazırla.
3. Internal testing ile hızlı smoke test yap.
4. Closed testing'i en az 12 tester ile başlat.
5. Tester'ları 14 gün continuous opt-in durumunda tut.
6. Test feedback ve bug fix kayıtlarını sakla.

Tester yönetimi için pratik notlar:

- tester'lara net görev listesi ver
- haftada en az 2-3 kez gerçek kullanım iste
- sadece yükleyip bırakmalarına güvenme
- feedback formu veya e-posta adresi ver

### 5.6 Kısa vade çıkış kriterleri

Bu faz bitti sayılmadan önce:

- Play build self-update içermiyor
- tüm ağ trafiği HTTPS
- gizlilik politikası yayında
- izin disclosure ekranları hazır
- kapalı test başlamış durumda
- tester takibi ve feedback kaydı tutuluyor

## 6. Orta Vadeli Yol Haritası (2-6 Hafta)

Bu fazın amacı: "production access ve ilk yayın onayı".

### 6.1 Üretim kalitesine getir

Yapılacaklar:

- APK yerine AAB üretim akışını netleştir
- release signing yapısını kalıcılaştır
- crash, ANR ve startup sorunları için test matrisini genişlet
- düşük RAM, farklı launcher ve farklı Android üreticilerinde davranış test et
- pre-launch report çalıştır ve tüm kritik uyarıları temizle

### 6.2 Play Console içeriklerini eksiksiz doldur

Tamamlanacak alanlar:

- App content
- Data safety
- Target audience and content
- Content rating
- Permissions declarations
- Store listing

Burada stratejik dikkat:

- Target audience cevabında uygulamayı gereksiz yere doğrudan çocuk uygulaması gibi işaretleme
- fakat çocuk verisine temas eden bölümlerde eksik veya yanıltıcı beyan yapma
- mağaza metni ile uygulama davranışı birebir uyumlu olsun

### 6.3 Production access başvurusuna hazırlan

Google senden test süreci hakkında yanıt isteyecek. O yüzden şunları önceden hazırla:

- kaç tester vardı
- ne tür cihazlarda test edildi
- hangi hatalar bulundu
- ne düzeltildi
- neden uygulamanın yayın için hazır olduğu düşünülüyor

Önerilen kanıt paketi:

- changelog
- kapalı test özeti
- tester feedback özeti
- çözülen bug listesi
- reviewer için kısa demo videosu

### 6.4 Store listing'i doğru kur

Metin yaklaşımı:

- "çocuğunuzu zorla kontrol eden uygulama" tonu yerine
- "ebeveynin belirlediği uygulama erişim kuralları" dili kullan
- eğitim faydasını anlat ama ana işlevi gizleme
- broad app visibility ve monitoring işlevinin neden gerekli olduğu mağaza açıklamasında görünür olsun

Kaçınılacak söylemler:

- "telefonu tamamen kontrol eder"
- "uygulamaları zorla kapatır"
- "çocuk kaçamaz"
- "gizli takip"

### 6.5 Production access başvuru ve yayın

Sıra:

1. 12 tester + 14 gün koşulunu tamamla.
2. Production access başvurusu yap.
3. Reviewer notlarına video ve açıklamaları ekle.
4. Onay gelirse önce küçük staged rollout yap.
5. İlk hafta crash, feedback, review ve policy uyarılarını yakından izle.

### 6.6 Orta vade çıkış kriterleri

- production access alınmış
- ilk Play yayını açılmış
- ilk sürüm staged rollout ile güvenli ilerliyor
- policy uyarısı veya red yok

## 7. Uzun Vadeli Yol Haritası (6-16 Hafta)

Bu fazın amacı: "sürdürülebilir, büyüyebilen, ikinci red dalgası üretmeyen ürün".

### 7.1 Ürün mimarisini ikiye ayır

- parental control çekirdeği
- AI destekli eğitim kişiselleştirme katmanı

Amaç:

- Play reviewer ana işlevi net anlasın
- eğitim altyapısı, kilit işlevini gölgeleyip mağaza incelemesini karmaşıklaştırmasın

### 7.2 Çoklu çocuk / çoklu profil yapısını kur

- cihaz bazlı rastgele profil ID
- ebeveynin birden fazla çocuk profili yönetebilmesi
- server tarafında anonim öğrenci profili ayrımı

### 7.3 Ebeveyn paneli ve raporlama ekle

- hangi konu alanında zorlanıyor
- hangi soru tipinde iyileşme var
- hangi uygulamalara erişim denemesi yoğun

Ancak dikkat:

- analytics ile surveillance çizgisi karışmamalı
- veri toplama kapsamı yeni özellik geldikçe yeniden beyan edilmeli

### 7.4 Abonelik modeli düşünülürse sadece Play uyumlu tasarla

İleride premium özellik eklenirse:

- Google Play Billing kullanılmalı
- mağaza metni ve in-app pricing şeffaf olmalı
- subscription ekranları manipülatif olmamalı

### 7.5 Hukuki ve güvenlik sertleşmesi

- veri saklama süreleri yazılı hale gelsin
- veri silme talebi kanalı uygulansın
- ebeveyn onayı akışı hukuk danışmanıyla netleştirilsin
- düzenli policy review checklist oluşturulsun

## 8. Red Riski En Yüksek Maddeler

Yayın öncesi bunlardan biri açıksa başvuru yapılmamalı:

1. ~~Play sürümünde self-update veya APK indirme-kurma akışı varsa~~ ✅ Çözüldü
2. ~~HTTP üzerinden veri aktarımı varsa~~ ✅ Çözüldü (HTTPS zorunlu)
3. QUERY_ALL_PACKAGES için güçlü gerekçe ve disclosure yoksa ⏳ (Play Console declaration girilmeli)
4. ~~KILL_BACKGROUND_PROCESSES kullanımı sürüyorsa~~ ✅ Çözüldü
5. Gizlilik politikası ile gerçek uygulama davranışı uyuşmuyorsa ⏳
6. Monitoring / parental control konumlandırması mağaza metninde net değilse ⏳
7. Data safety formu eksik veya yanıltıcıysa ⏳
8. Tester süreci kağıt üzerinde var ama gerçek engagement yoksa ⏳

## 9. Önerilen 30 Günlük Takvim

### Gün 1-3

- Play sürümü için teknik kapsamı ayır
- self-update kaldırma kararını uygula
- HTTPS planını kesinleştir

### Gün 4-7

- izin minimizasyonu
- disclosure ekranları
- privacy policy yayını
- support email ve store asset hazırlığı

### Gün 8-10

- internal test
- pre-launch report
- son kritik bug düzeltmeleri

### Gün 11

- closed test başlat

### Gün 11-24

- 12 tester aktif kalsın
- feedback topla
- hata düzeltmeleri çıkar
- reviewer video ve açıklamaları hazırla

### Gün 25-27

- production access başvurusu

### Gün 28-30+

- onay gelirse staged rollout
- gelmezse reviewer gerekçesine göre odaklı düzeltme

## 10. Uygulama İçin Tavsiye Edilen Nihai Yayın Stratejisi

En gerçekçi kabul stratejisi şu kombinasyon:

1. Play'de sadece politikaya uyumlu parental control sürümünü yayınla.
2. APK self-update mantığını Play dışı kanala taşı.
3. AI soru üretimini koru ama veri akışını HTTPS + veri minimizasyonu ile sınırla.
4. Mağaza metninde ebeveyn denetimi çekirdeğini açık ve dürüst anlat.
5. Kapalı testten gelen gerçek geri bildirimleri production access başvurusunda kullan.

## 11. Bu Proje İçin Hemen Yapılacak İlk 10 İş

1. Play build flavor tasarla.
2. REQUEST_INSTALL_PACKAGES iznini Play flavor'dan çıkar.
3. UpdateChecker'ı Play sürümünde devre dışı bırak.
4. Tüm HTTP endpointlerini HTTPS'e taşı.
5. network_security_config içindeki cleartext istisnasını kaldır.
6. KILL_BACKGROUND_PROCESSES bağımlılığını Play sürümünden temizle.
7. QUERY_ALL_PACKAGES için kalacak mı kalkacak mı kararını ver.
8. Privacy policy ve in-app disclosure metinlerini yaz.
9. Closed test için 12 gerçek tester listesini hazırla.
10. Reviewer video ve Play listing taslağını oluştur.

## 12. Kaynaklar

- Developer Program Policy
  - https://support.google.com/googleplay/android-developer/answer/16944162?hl=en
- App testing requirements for new personal developer accounts
  - https://support.google.com/googleplay/android-developer/answer/14151465?hl=en
- Permissions and APIs that Access Sensitive Information
  - https://support.google.com/googleplay/android-developer/answer/9888170?hl=en
- QUERY_ALL_PACKAGES policy
  - https://support.google.com/googleplay/android-developer/answer/10158779?hl=en
- REQUEST_INSTALL_PACKAGES policy
  - https://support.google.com/googleplay/android-developer/answer/12085295?hl=en
- isMonitoringTool flag
  - https://support.google.com/googleplay/android-developer/answer/12955211?hl=en

## 13. Net Sonuç

MathLock'ın Play'e kabul edilmesi mümkün, ancak mevcut haliyle değil.

Kabul ihtimalini en çok artıran sıra şudur:

1. Play uyumlu sürüm ayrımı
2. Self-update ve HTTP'nin kaldırılması
3. İzin ve veri kullanımının açık beyanı
4. Parental control / monitoring konumlandırmasının doğru yapılması
5. 12 tester + 14 gün kapalı test + iyi belgelenmiş production access başvurusu

Bu sıraya uyulursa MathLock, "red alması beklenen riskli araç" olmaktan çıkıp "gerekçesi ve davranışı net ebeveyn denetimi uygulaması" sınıfına yaklaşır.