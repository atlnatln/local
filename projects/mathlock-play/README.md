# MathLock Play — Google Play Sürümü

Bu proje, MathLock uygulamasının Google Play Store'a uyumlu sürümüdür.

## Orijinal (mathlock) ile Farkları

| Özellik | mathlock (APK) | mathlock-play |
| --- | --- | --- |
| applicationId | com.akn.mathlock | com.akn.mathlock.play |
| Self-update (OTA) | VPS'ten APK | Kaldırıldı |
| REQUEST_INSTALL_PACKAGES | Var | Kaldırıldı |
| KILL_BACKGROUND_PROCESSES | Var | Kaldırıldı |
| HTTP trafik | 89.252.152.222 | Sadece HTTPS |
| Veri endpointleri | http://89.252.152.222 | https://mathlock.com.tr |
| isMonitoringTool beyanı | Yok | child_monitoring |
| Prominent Disclosure | Yok | DisclosureActivity |
| Privacy Policy web | Yok | website/ altında |
| isMinifyEnabled (release) | false | true (R8) |

## Ön Gereksinimler

### VPS Sunucu Kurulumu (Host-based Deployment)

> **29 Nisan 2026'dan itibaren** backend (Django + Celery) konteyner dışında, host üzerinde systemd servisi olarak çalışıyor.  
> Sebep: `kimi-cli` (AI üretim aracı) sadece host'ta kurulu ve konteyner içinden erişilemiyordu.  
> Detaylı bilgi: `docs/HOST_MIGRATION.md`

#### 1. Altyapı Servisleri (Docker)

Sadece PostgreSQL ve Redis konteynerda:

```bash
cd /home/akn/vps/projects/mathlock-play
docker-compose up -d   # mathlock_db + mathlock_redis
```

Portlar host'a açık: `5432` (PostgreSQL), `6379` (Redis).

#### 2. Python Virtual Environment (Host)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Systemd Servisleri (Host)

```bash
sudo cp docs/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mathlock-backend
sudo systemctl enable --now mathlock-celery
```

Servis detayları: `docs/systemd/mathlock-backend.service`, `docs/systemd/mathlock-celery.service`

#### 4. Nginx (Konteyner → Host Unix Socket)

Nginx `vps_nginx_main` konteyneri içinden backend'e **Unix socket** üzerinden erişir:
- Host socket: `/home/akn/vps/projects/mathlock-play/backend/run/gunicorn.sock`
- Container mount: `/var/run/mathlock/gunicorn.sock`
- `proxy_pass http://unix:/var/run/mathlock/gunicorn.sock:/api/mathlock/;`

#### 5. kimi-cli (AI Pipeline)

`kimi-cli` host'ta `uv tool` ile kurulu:
- Yol: `/home/akn/.local/share/uv/tools/kimi-cli/bin/kimi`
- PATH'e eklenmeli (systemd servislerinde tanımlı)
- Login durumu: `~/.kimi/credentials/` altında

#### 6. Domain ve SSL (mathlock.com.tr)

1. DNS propagasyonunun tamamlanmasını bekle
2. nginx config aktif: `infrastructure/nginx/conf.d/mathlock-play.conf`
3. SSL sertifikası: `/home/akn/vps/infrastructure/ssl/mathlock.com.tr/`
4. Web sitesi: `website/*.html` → `/var/www/mathlock/website/`

## Build

```bash
./gradlew assembleDebug    # Debug APK
./gradlew bundleRelease    # AAB (Play Store)
./gradlew assembleRelease  # Release APK (test)
```

## Play Store Yayın Checklist

- [ ] DNS propagasyonu tamamlandı
- [ ] SSL sertifikası alındı
- [ ] Privacy policy sayfası yayında
- [ ] Support sayfası yayında
- [ ] Play Console hesabı doğrulandı
- [ ] Release keystore oluşturuldu
- [ ] Internal test ile smoke test yapıldı
- [ ] Closed testing 12+ tester ile başlatıldı
- [ ] 14 gün continuous opt-in tamamlandı
- [ ] Production access başvurusu yapıldı

---

# MathLock (Orijinal README) - Eğitici Uygulama Kilidi 🔒🧮

Çocuğunuzun telefonunuzdaki uygulamalara erişimini eğitici matematik soruları ve oyunlarla kontrol eden Android uygulaması.

## Özellikler

### � AI Destekli Adaptif Matematik Sistemi
- **VPS'ten JSON soru seti**: 50 soruluk setler sunucudan indirilir
- **6 soru tipi**: Toplama, Çıkarma, Çarpma, Bölme, Sıralama, Eksik Sayı
- **Kademeli zorluk**: 5 zorluk seviyesi, çocuğun performansına göre ayarlanır
- **İpucu sistemi**: Yanlış cevapta önce ipucu, sonra konu anlatımı gösterilir
- **İstatistik takibi**: Her cevap kaydedilir, 50 soru tamamlanınca VPS'e yüklenir
- **AI soru üretimi**: kimi-cli (kimi-for-coding) çocuğun performansına göre yeni set üretir
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
questions.json indir          ←──   Django REST API /api/mathlock/questions/
levels.json indir             ←──   Django REST API /api/mathlock/levels/
topics.json indir             ←──   konu anlatımları

Çocuk 50 matematik sorusu veya 12 bulmaca seviyesi çözer
  ├─ Doğru → kilit açılır
  ├─ Yanlış (1.) → 💡 ipucu
  ├─ Yanlış (2.) → 📚 konu anlatımı
  └─ Yanlış (3.) → doğru cevap gösterilir

stats / level-progress yükle  ──→   performans verisi

                                    credits/use/ veya progress sonrası:
                                    ├─ Kredi varsa (veya ilk set ücretsiz)
                                    ├─ ai-generate.sh / ai-generate-levels.sh çalışır
                                    ├─ kimi-cli yeni soru/seviye üretir
                                    ├─ validate-questions.py / validate-levels.py doğrular
                                    └─ QuestionSet / LevelSet DB'ye kaydeder

Yeni set otomatik indirilir   ←──   API'den yeni set
```

### Kredi Sistemi (Google Play Billing)

| Durum | Matematik (50 soru) | Sayı Yolculuğu (12 seviye) |
|---|---|---|
| İlk set | Ücretsiz | Ücretsiz |
| Set biter + kredi var | `POST /credits/use/` → AI yeni 50 soru üretir | `POST /levels/progress/` → AI yeni 12 seviye üretir |
| Set biter + kredi yok | Aynı sorular tekrar eder (sonsuz döngü) | Aynı seviyeler tekrar eder |
| Satın alma | `BillingManager` → Google Play → kredi ekle | Aynı kredi havuzu kullanılır |

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

AGENTS.md                        # kimi-cli soru üretim kuralları
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
- **Araç:** kimi-cli (`kimi -p "..." --print --final-message-only`)
- **Model:** kimi-code/kimi-for-coding (Kimi-k2.6)
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
