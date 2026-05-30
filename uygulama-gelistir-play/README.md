# uygulama-gelistir-play

Google Play Store'da uygulama yönetimini otomatize eden merkezi sistem.

**API + CLI** ile store listing, görseller, detaylar ve release yönetimini tek komutta yap.
Yeni uygulama eklemek için `scaffold` komutuyla saniyeler içinde template oluştur.

---

## Özellikler

| Özellik | Nasıl? |
|---------|--------|
| Store listing (başlık, açıklama) | ✅ API (`sync-listing`) |
| Ekran görüntüleri, ikon, grafik | ✅ API (`sync-listing`) |
| Uygulama detayları (kategori, iletişim) | ✅ API (`sync-listing`) |
| AAB/APK yükleme + track | ✅ API (`release`) |
| İçerik derecelendirmesi | ❌ Tarayıcı (Tampermonkey) |
| Hedef kitle / Reklam / Data Safety | ❌ Tarayıcı (Tampermonkey) |

---

## Kurulum

### 1. Python Bağımlılıkları

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Service Account

Her uygulamanın `config.json`'unda bir Google Service Account JSON dosyası referansı olmalı.
Play Console → Kurulum → API erişimi → Service Account oluştur → `Release Manager` rolü ver.

---

## Klasör Yapısı

```
uygulama-gelistir-play/
├── apps/
│   └── mathlock-play/
│       ├── config.json              ← Paket adı, service account, track, iletişim
│       └── metadata/
│           └── tr-TR/
│               ├── title.txt              (max 30 karakter)
│               ├── short_description.txt  (max 80)
│               ├── full_description.txt   (max 4000)
│               └── images/
│                   ├── icon/icon.png                (512×512)
│                   ├── featureGraphic.png           (1024×500)
│                   ├── phoneScreenshots/
│                   ├── sevenInchScreenshots/
│                   └── tenInchScreenshots/
│           └── en-US/
│               └── ...
├── scripts/
│   └── play-cli.py          ← Ana CLI (sync-listing, release, scaffold, validate)
├── tampermonkey/
│   └── play-console-autofill.user.js  ← Yedek: Tarayıcı otomasyonu
└── config-editor/
    └── index.html            ← Yedek: Web config editörü
```

---

## Komutlar

### `sync-listing` — Mağaza girişini senkronize et

Tüm diller için metinleri, görselleri ve uygulama detaylarını Play Console'a upload eder.

```bash
python scripts/play-cli.py sync-listing --app mathlock-play
```

### `release` — AAB yükle + track'e ata

```bash
python scripts/play-cli.py release \
  --app mathlock-play \
  --aab /home/akn/local/projects/mathlock-play/app/build/outputs/bundle/release/app-release.aab
```

### `scaffold` — Yeni uygulama template'i oluştur

```bash
python scripts/play-cli.py scaffold \
  --app super-oyun \
  --package com.akn.superoyun \
  --title "Süper Oyun" \
  --lang tr-TR
```

Bu komut `apps/super-oyun/` altında tüm gerekli klasörleri ve boş config dosyalarını oluşturur.

### `validate` — Kontrol et

Metin uzunlukları, görsel varlığı ve config doğruluğunu kontrol eder.

```bash
python scripts/play-cli.py validate --app mathlock-play
```

---

## `config.json` Şeması

```json
{
  "packageName": "com.akn.mathlock.play",
  "serviceAccount": "/home/akn/secrets/mathlock-play/google-service-account.json",
  "track": "internal",
  "defaultLanguage": "tr-TR",
  "details": {
    "defaultLanguage": "tr-TR",
    "contactEmail": "destek@ornek.com",
    "contactWebsite": "https://ornek.com",
    "contactPhone": ""
  },
  "releaseNotes": [
    {"language": "tr-TR", "text": "Genel iyileştirmeler."},
    {"language": "en-US", "text": "General improvements."}
  ]
}
```

| Alan | Açıklama |
|------|----------|
| `packageName` | Google Play'deki paket adı |
| `serviceAccount` | Service Account JSON dosyasının yolu (mutlak veya göreceli) |
| `track` | `internal`, `alpha`, `beta`, `production` |
| `defaultLanguage` | Varsayılan dil kodu |
| `details` | Uygulama detayları (e-posta, web sitesi, telefon) |
| `releaseNotes` | Her release'te kullanılacak release notes |

---

## Yeni Uygulama Ekleme Akışı

1. **Scaffold oluştur:**
   ```bash
   python scripts/play-cli.py scaffold --app yeni-app --package com.sirket.yeniapp --title "Yeni App"
   ```

2. **Service account ayarla:**
   - Play Console'da service account oluştur
   - `config.json`'a `serviceAccount` yolunu yaz

3. **Store listing metinlerini doldur:**
   - `metadata/tr-TR/title.txt`
   - `metadata/tr-TR/short_description.txt`
   - `metadata/tr-TR/full_description.txt`

4. **Görselleri yerleştir:**
   - `metadata/tr-TR/images/icon/icon.png` (512×512)
   - `metadata/tr-TR/images/featureGraphic.png` (1024×500)
   - `metadata/tr-TR/images/phoneScreenshots/*.png` (en az 2 adet)

5. **Doğrula:**
   ```bash
   python scripts/play-cli.py validate --app yeni-app
   ```

6. **API ile upload et:**
   ```bash
   python scripts/play-cli.py sync-listing --app yeni-app
   ```

7. **Play Console'da manuel tamamla:**
   - İçerik derecelendirmesi
   - Hedef kitle & Reklam
   - Data Safety
   - Gizlilik politikası

8. **İlk release'i yap:**
   ```bash
   python scripts/play-cli.py release --app yeni-app --aab path/to/app-release.aab
   ```

---

## Tampermonkey (Yedek)

Eğer API ile bir işlem yapılamazsa veya tarayıcı otomasyonu gerekiyorsa, mevcut `tampermonkey/play-console-autofill.user.js` betiği kullanılabilir. Bu betik:

- Yeni uygulama oluşturma formunu otomatik doldurur
- Mağaza girişi metinlerini otomatik doldurur
- URL parametreleri ile Copilot/agent entegrasyonu sağlar

---

## Notlar

- `sync-listing` her çalıştığında mevcut görselleri siler ve yeniden upload eder. Bu, eski görsellerin kalıntı kalmasını engeller.
- Her API işlemi bir "edit" (taslak) oluşturur, işlemler bitince `commit` edilir. Hata olursa edit iptal edilir (otomatik rollback).
- Service account'un Play Console'da en az `Release Manager` rolüne sahip olması gerekir.
