# MathLock Onboarding & İzin Akışı İyileştirme Planı

Tarih: 5 Nisan 2026

## Mevcut Durum Analizi

### Kullanıcının gördüğü izin dizisi (ekran görüntülerinden)
1. **Kullanım Erişimi** → Sistem ayarları ekranı
2. **"Tehlike" kırmızı uyarı** → Android sistem uyarısı ("Cihaz kullanımını takip et")
3. **Ekran Üstü Gösterim** → Sistem ayarları ekranı
4. **Xiaomi Kurulum 1/3** → Otomatik Başlatma (Xiaomi'ye özel)
5. **Batarya Optimizasyonu** → Sistem dialog'u

### Kod incelemesi özeti
- `DisclosureActivity`: İlk çalıştırmada tek seferlik kabul ekranı (55 satır)
- `SettingsActivity.checkAndRequestPermissions()`: Sıralı 4 adımlı izin zinciri
  - Adım 1: Usage Stats → `ACTION_USAGE_ACCESS_SETTINGS`
  - Adım 2: Overlay → `ACTION_MANAGE_OVERLAY_PERMISSION`
  - Adım 3: Notifications (API 33+) → `POST_NOTIFICATIONS` runtime
  - Adım 4: Battery → `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` ("Atla" mevcut)
- Tüm izinler tamamlandıktan sonra → `startLockService()`
- Xiaomi cihazlarda ek 3 adımlı wizard (AutoStart → Popup → Background)
- `onResume()` + `permissionCheckPending` flag ile otomatik devam

### 9 manifest izni
| İzin | Gereklili | Ertelenebi |
|------|-----------|------------|
| PACKAGE_USAGE_STATS | Zorunlu (çekirdek) | Hayır |
| SYSTEM_ALERT_WINDOW | Zorunlu (overlay soru) | Hayır |
| FOREGROUND_SERVICE | Otomatik (manifest) | - |
| FOREGROUND_SERVICE_SPECIAL_USE | Otomatik (manifest) | - |
| POST_NOTIFICATIONS | İsteğe bağlı | Evet ✓ |
| RECEIVE_BOOT_COMPLETED | Otomatik (manifest) | - |
| QUERY_ALL_PACKAGES | Zorunlu (uygulama listesi) | - |
| REQUEST_IGNORE_BATTERY_OPTIMIZATIONS | Önerilen | Evet ✓ |
| INTERNET | Otomatik (manifest) | - |

---

## "App Pinning" / Lock Task Mode Değerlendirmesi

Kullanıcının sorduğu "app pinning" konusu araştırıldı:

### Lock Task Mode (Kilit Görevi Modu)
- **Cihaz sahibi (Device Owner)** veya **profil sahibi (Profile Owner)** gerektirir
- DPC kurulumu için fabrika ayarlarına dönüş lazım
- Kiosk/enterprise senaryoları için tasarlanmış
- **Play Store'dan indirilen bir parental control app için UYGUN DEĞİL**

### Screen Pinning (Ekran Sabitleme)
- Kullanıcı tarafından başlatılır (Ayarlar → Güvenlik → Ekran Sabitleme)
- Kullanıcı istediği zaman çıkabilir (Geri + Son tuşlarına basarak)
- MathLock'ın amacına uygun değil (biz başka uygulamaları kilitliyoruz, kendi uygulamamızı sabitleğiz)

### Sonuç
MathLock'ın mevcut mimarisi (UsageStats + Overlay + FGS) Play Store parental control uygulamaları için **doğru ve standart** yaklaşım. Google Family Link, Qustodio, Norton Family gibi uygulamalar da benzer mimari kullanıyor.

**İzin sorulması kaçınılmaz** — çünkü Android bu özel izinleri (Usage Stats, Overlay) programatik olarak vermeye izin vermiyor. Yapabileceğimiz: kullanıcı deneyimini iyileştirmek.

---

## İyileştirme Planı

### Öncelik 1: Rehberli Kurulum Sihirbazı (SetupWizardActivity) — YÜKSEK ETKİ

**Sorun:** Kullanıcı "Korumayı Aç" butonuna bastığında arkasının ne olduğunu bilmedğinden 4-5 defa üst üste farklı ekranlara yönlendiriliyor. Korkutucu.

**Çözüm:** Yeni bir `SetupWizardActivity` oluştur:

```
┌─────────────────────────────────┐
│  MathLock Kurulum Sihirbazı     │
│  ━━━━●━━━━○━━━━○━━━━○           │  ← Progress bar (Adım 1/3)
│                                 │
│  📊 Kullanım Erişimi            │
│                                 │
│  MathLock'ın hangi uygulamanın  │
│  açık olduğunu görebilmesi için │
│  bu izin gereklidir.            │
│                                 │
│  Android sizi ayarlara          │
│  yönlendirecek. MathLock'u      │
│  bulup açın.                    │
│                                 │
│  ┌─────────────────────────┐    │
│  │    İzin Ver →           │    │
│  └─────────────────────────┘    │
│                                 │
│  Toplam 3 adım kaldı           │
└─────────────────────────────────┘
```

**Faydaları:**
- Kullanıcı kaç adım olduğunu **önceden** görür
- Her adımda **neden** gerekli olduğu açıklanır
- İlerleme çubuğu ile motivasyon
- Sistem ayar ekranlarından döndüğünde otomatik sonraki adıma geçer
- Tüm izinler tamamlandığında "Tebrikler! Koruma başladı" ekranı

**Akış:**
```
DisclosureActivity (ilk çalıştırma)
  → MainActivity
    → SettingsActivity ("Korumayı Aç" butonu)
      → SetupWizardActivity
        Adım 1: Usage Stats açıklaması → Sistem ayarları → Dönüş
        Adım 2: Overlay açıklaması → Sistem ayarları → Dönüş
        Adım 3: Batarya (opsiyonel) → Sistem dialog → Dönüş
        → Tamamlandı ekranı
      → Geri SettingsActivity (koruma aktif)
```

### Öncelik 2: POST_NOTIFICATIONS İznini Ertele — ORTA ETKİ

**Sorun:** Bildirim izni çekirdek kilit fonksiyonu için gerekli değil. Gereksiz yere ilk kurulumda soruluyor.

**Çözüm:**
- `checkAndRequestPermissions()` 4 adımlı zincirden bildirim adımını çıkar
- İlk başarılı kilit aktivasyonundan sonra veya SettingsActivity'de ayrı "Bildirimleri Aç" butonu ile sor
- Servis `startForeground()` çağrısında bildirim zaten gösteriyor; izin yoksa bildirim sessizce oluşturulur (API 33+)

**Etki:** İlk kurulumda 4 adım → 3 adım (+ opsiyonel batarya = 2 zorunlu adım)

### Öncelik 3: Batarya Optimizasyonunu Sihirbaz Dışına Taşı — DÜŞÜK-ORTA ETKİ

**Sorun:** Batarya izni zaten "Atla" seçeneği var ama hâlâ zorunlu akışın içinde.

**Çözüm:**
- Bataryayı `SetupWizardActivity`'nin **bonus adımı** yap: "Bazı telefonlarda daha güvenilir çalışma için önerilir. Şimdilik atla mısınız?"
- Veya tamamen `SettingsActivity`'ye taşı: "Koruma bazen kapanıyorsa → Batarya Optimizasyonunu Kapat"

**Etki:** İlk kurulumda zorunlu adım sayısı 2'ye iner (Usage Stats + Overlay)

### Öncelik 4: Xiaomi Sihirbazını İyileştir — DÜŞÜK ETKİ

**Mevcut durumu iyi:** 3 adımlı wizard, her adımda "Sonraki ▸" ile atlama mevcut.

**Küçük iyileştirmeler:**
- Xiaomi wizard'ını SetupWizardActivity'ye entegre et (ayrı dialog yerine)
- Xiaomi algılandığında progress bar'da ek adımları göster

### Öncelik 5: DisclosureActivity + Wizard Birleşimi — İLERİ VADE

**Mevcut:**
```
DisclosureActivity → MainActivity → SettingsActivity → "Korumayı Aç" → İzinler
```

**Önerilen (ileri vade):**
```
DisclosureActivity (disclosure + kabul) → SetupWizardActivity (izinler) → SettingsActivity (hazır)
```

Bu, kullanıcının kurulum sürecini kesintisiz bir akış olarak yaşamasını sağlar.

---

## Sonuç: Etki/Efor Matrisi

| İyileştirme | Kullanıcı Etkisi | Geliştirme Eforu | Öncelik |
|------------|-------------------|-------------------|---------|
| SetupWizardActivity | ⭐⭐⭐⭐⭐ | Orta (yeni Activity + layout) | 1 |
| POST_NOTIFICATIONS erteleme | ⭐⭐⭐ | Düşük (birkaç satır) | 2 |
| Batarya optimizasyonu bonus | ⭐⭐ | Düşük | 3 |
| Xiaomi entegrasyonu | ⭐ | Orta | 4 |
| Disclosure + Wizard birleşimi | ⭐⭐⭐ | Yüksek | 5 (ileri vade) |

---

## Hemen Başlanabilecek Teknik Adımlar

1. **POST_NOTIFICATIONS erteleme** — `checkAndRequestPermissions()`'dan bildirim adımını çıkar (en hızlı kazanım)
2. **SetupWizardActivity iskeleti** — ViewPager + 3 step layout oluştur
3. **Her adım için açıklama metinleri** yaz:
   - "Kullanım Erişimi: Hangi uygulamanın açık olduğunu görmemiz gerekiyor"
   - "Ekran Üstü Gösterim: Matematik sorusunu uygulama üzerinde göstermemiz gerekiyor"
   - "Batarya: Korumanın arka planda çalışmaya devam etmesi için önerilir (opsiyonel)"
