# MathLock - Eğitici Uygulama Kilidi 🔒🧮

Çocuğunuzun telefonunuzdaki uygulamalara erişimini eğitici matematik soruları ve oyunlarla kontrol eden Android uygulaması.

## Özellikler

### � AI Destekli Adaptif Matematik Sistemi
- **VPS'ten JSON soru seti**: 50 soruluk setler sunucudan indirilir
- **6 soru tipi**: Toplama, Çıkarma, Çarpma, Bölme, Sıralama, Eksik Sayı
- **Kademeli zorluk**: 5 zorluk seviyesi, çocuğun performansına göre ayarlanır
- **İpucu sistemi**: Yanlış cevapta önce ipucu, sonra konu anlatımı gösterilir
- **İstatistik takibi**: Her cevap kaydedilir, 50 soru tamamlanınca VPS'e yüklenir
- **AI soru üretimi**: Copilot (claude-haiku-4.5) çocuğun performansına göre yeni set üretir
- **Otomatik döngü**: Çöz → istatistik yükle → AI yeni set üret → telefon indir
- Hedef seviye: İlkokul 2. sınıf

### 🧮 Klasik Mod (Fallback)
- VPS'e erişilemezse rastgele sorular üretilir
- Toplama, çıkarma, çarpma tablosu, bölme
- Ayarlanabilir soru sayısı (1-50) ve geçiş skoru

### 🎯 Sayı Tahmin Oyunu
- 0-100 arası rastgele sayı tutulur
- "Daha büyük" / "Daha küçük" ipuçları
- Aralık göstergesi ile yardım
- Doğru tahmin = kilit açılır!

### 🔑 Ebeveyn Bypass
- **Parmak İzi** - BiometricPrompt ile hızlı giriş
- **PIN Şifre** - 4-8 haneli sayısal şifre (varsayılan: 1234)
- **Desen Kilidi** - 3x3 grid üzerinde desen çizme

### ⚙️ Ayarlar
- Hangi uygulamaların kilitli olacağını seçme
- AI mod durumu ve ilerleme göstergesi
- Soru sayısı ayarı (1-50 arası)
- Geçiş skoru ayarı
- Kimlik doğrulama yöntemlerini aç/kapat
- PIN ve desen değiştirme

### 📱 OTA Güncelleme
- VPS üzerinden otomatik güncelleme kontrolü
- Yeni sürüm varsa kullanıcıya bildirim
- APK indirme ve kurulum

## Nasıl Çalışır?

1. **Uygulamayı açın** ve korumayı etkinleştirin
2. **Kilitli uygulamaları seçin** (tarayıcı, YouTube vb.)
3. **Ayarlardan** PIN'inizi ve tercihlerinizi belirleyin
4. Çocuğunuz kilitli uygulamayı açmaya çalıştığında:
   - Oyun seçim ekranı açılır
   - Matematik soruları veya sayı tahmin oyunu seçer
   - Başarılı olursa uygulama açılır
   - Başarısız olursa tekrar denemesi gerekir

## AI Soru Döngüsü

```
📱 Telefon                          🖥️ VPS Sunucu
───────────                         ──────────────
questions.json indir          ←──   nginx /mathlock/data/
topics.json indir             ←──   konu anlatımları

Çocuk 50 soru çözer
  ├─ Doğru → kilit açılır
  ├─ Yanlış (1.) → 💡 ipucu
  ├─ Yanlış (2.) → 📚 konu anlatımı
  └─ Yanlış (3.) → doğru cevap gösterilir

stats.json yükle              ──→   performans verisi

                                    ai-generate.sh çalışır:
                                    ├─ stats analiz et
                                    ├─ Copilot yeni 50 soru üret
                                    ├─ validate-questions.py doğrula
                                    └─ questions.json güncelle

Yeni set otomatik indirilir   ←──   yeni questions.json
```

## Gerekli İzinler

| İzin | Neden |
|------|-------|
| `PACKAGE_USAGE_STATS` | Ön plandaki uygulamayı tespit etmek için |
| `FOREGROUND_SERVICE` | Arka planda sürekli çalışmak için |
| `SYSTEM_ALERT_WINDOW` | Kilitli uygulama üzerine ekran göstermek için |
| `POST_NOTIFICATIONS` | Servis bildirimini göstermek için |
| `RECEIVE_BOOT_COMPLETED` | Cihaz açılışında otomatik başlamak için |
| `QUERY_ALL_PACKAGES` | Yüklü uygulamaları listelemek için |

## Kurulum

1. Projeyi **Android Studio** ile açın
2. Gradle sync yapın
3. Connected device veya emulator'a yükleyin
4. İlk açılışta varsayılan PIN: **1234**
5. **Önemli:** Ayarlardan PIN'inizi değiştirin!

## Proje Yapısı

```
app/src/main/java/com/akn/mathlock/
├── MainActivity.kt              # Ana ekran
├── ChallengePickerActivity.kt   # Oyun seçim ekranı (kilit)
├── MathChallengeActivity.kt     # Matematik soruları (JSON + fallback)
├── NumberGuessActivity.kt       # Sayı tahmin oyunu
├── ParentAuthActivity.kt        # Ebeveyn kimlik doğrulama
├── PatternActivity.kt           # Desen kilidi ekranı
├── SettingsActivity.kt          # Ayarlar
├── AppSelectionActivity.kt      # Kilitli uygulama seçimi
├── LockStateManager.kt          # Kilit durumu yönetimi
├── service/
│   └── AppLockService.kt        # Arka plan servisi
├── receiver/
│   └── BootReceiver.kt          # Açılışta servisi başlat
└── util/
    ├── PreferenceManager.kt     # Ayarlar yönetimi
    ├── QuestionManager.kt       # VPS JSON soru yönetimi
    ├── StatsTracker.kt          # İstatistik takibi ve yükleme
    ├── TopicHelper.kt           # Konu anlatımları
    ├── UpdateChecker.kt         # OTA güncelleme kontrolü
    └── MathQuestionGenerator.kt # Fallback: rastgele soru üretici

data/                            # AI soru sistemi verileri
├── questions.json               # 50 soruluk aktif set
├── topics.json                  # Konu anlatımları
└── history/                     # Arşiv (eski setler + stats)

AGENTS.md                        # Copilot soru üretim kuralları
ai-generate.sh                   # AI pipeline: üret → doğrula → sync
validate-questions.py            # JSON doğrulama
deploy.sh                        # Build + OTA deploy
```

## Teknik Detaylar

### Uygulama
- **Min SDK:** 26 (Android 8.0) · **Target SDK:** 34 (Android 14)
- **Dil:** Kotlin · **UI:** Material Design 3
- **Kilit Mekanizması:** UsageStatsManager + Foreground Service
- **Güvenlik:** PIN/Desen SHA-256 hash ile saklanır
- **Cooldown:** Kilit açıldıktan sonra 30 saniye tekrar kilitleme yok

### AI Soru Pipeline
- **Araç:** GitHub Copilot CLI (`gh copilot suggest --yolo`)
- **Model:** claude-haiku-4.5
- **Kural dosyası:** `AGENTS.md` — sınıf seviyesi, soru tipleri, zorluk aralığı
- **Doğrulama:** `validate-questions.py` — şema, matematik doğruluğu, sınırlar
- **Otomasyon:** `ai-generate.sh` — üret → doğrula → retry → VPS sync → stats temizle

### VPS Endpoint'ler
| Endpoint | Method | Açıklama |
|---|---|---|
| `/mathlock/data/questions.json` | GET | Aktif soru seti |
| `/mathlock/data/topics.json` | GET | Konu anlatımları |
| `/mathlock/data/stats.json` | PUT | İstatistik yükleme |
| `/mathlock/dist/version.json` | GET | OTA versiyon bilgisi |
| `/mathlock/dist/mathlock.apk` | GET | En son APK |

## Kaldırma Davranışı

- Uygulama kaldırıldığında MathLock koruması tamamen biter.
- Kilitli uygulamalar normal hale döner; çünkü kilit mantığı Android sistemine değil MathLock servisinin çalışmasına bağlıdır.
- Uygulama ayarları cihaz yedeğinden geri yüklenmesin diye otomatik yedekleme kapatılmıştır.
