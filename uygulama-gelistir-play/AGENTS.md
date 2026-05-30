# AGENTS.md — uygulama-gelistir-play

> Google Play Store API otomasyonu ve uygulama yönetim sistemi.
> Bu proje, Play Console web arayüzünden bağımsız olarak store listing, görseller, detaylar ve release işlemlerini CLI ile yönetir.

---

## 🎯 Proje Amacı

- **Play Store API** (Android Publisher API v3) ile otomatize edilebilen tüm işlemleri tek bir merkezi CLI'da toplamak
- Yeni uygulama eklemek için `scaffold` komutuyla saniyeler içinde template oluşturmak
- Birden fazla uygulamayı (mathlock-play, gelecekteki diğerleri) aynı yapı altında yönetmek
- Tarayıcı otomasyonunu (Tampermonkey) yedek/yardımcı olarak tutmak, birincil yöntem API olacak

---

## 📁 Klasör Yapısı

```
uygulama-gelistir-play/
├── AGENTS.md                          ← Bu dosya
├── README.md                          ← Kullanım kılavuzu
├── apps/
│   └── <app-id>/
│       ├── config.json                ← packageName, serviceAccount, track, details
│       └── metadata/
│           └── <lang>/
│               ├── title.txt              (max 30 karakter)
│               ├── short_description.txt  (max 80)
│               ├── full_description.txt   (max 4000)
│               └── images/
│                   ├── icon/icon.png                (512×512)
│                   ├── featureGraphic.png           (1024×500)
│                   ├── phoneScreenshots/
│                   ├── sevenInchScreenshots/
│                   └── tenInchScreenshots/
├── scripts/
│   └── play-cli.py                    ← Ana CLI (sync-listing, release, scaffold, validate)
├── tampermonkey/
│   └── play-console-autofill.user.js  ← Yedek: Tarayıcı otomasyonu
└── config-editor/
    └── index.html                     ← Yedek: Web config editörü
```

---

## 🔧 Komut Referansı

Tüm komutlar `scripts/play-cli.py` üzerinden çalışır.

```bash
cd /home/akn/local/uygulama-gelistir-play
python scripts/play-cli.py <komut> [args]
```

| Komut | Açıklama | Örnek |
|-------|----------|-------|
| `sync-listing` | Store listing, details ve images'i API ile senkronize et | `python scripts/play-cli.py sync-listing --app mathlock-play` |
| `release` | AAB upload + track assignment | `python scripts/play-cli.py release --app mathlock-play --aab /path/to/app.aab` |
| `scaffold` | Yeni app için template klasörü oluştur | `python scripts/play-cli.py scaffold --app yeni-app --package com.ornek.app` |
| `validate` | Metin uzunlukları ve görsel boyutlarını kontrol et | `python scripts/play-cli.py validate --app mathlock-play` |

**Dry-run modu:** Her komuta `--dry-run` eklenebilir. API çağrısı yapmadan ne yapılacağını gösterir.

---

## 📋 Agent Davranış Kuralları

### 1. Yeni Uygulama Ekleme

Kullanıcı "yeni uygulama ekle" dediğinde:
1. `scaffold` komutunu kullan: `python scripts/play-cli.py scaffold --app <id> --package <pkg> --title <t>`
2. Kullanıcıya oluşan dosya yapısını göster
3. `config.json`'da `serviceAccount` yolunun doldurulması gerektiğini hatırlat
4. `metadata/<lang>/title.txt`, `short_description.txt`, `full_description.txt` ve görsellerin (icon, featureGraphic, screenshots) hazırlanması gerektiğini belirt
5. **Önemli:** Play Console web'den manuel olarak "Yeni uygulama oluştur" yapılması gerekir (API ile yeni uygulama oluşturulamaz)

### 2. Store Listing Güncelleme

Kullanıcı "mağaza girişini güncelle" veya "store listing sync" dediğinde:
1. Önce `validate --app <id>` çalıştır
2. Hata varsa düzelt
3. `sync-listing --app <id>` çalıştır
4. Sonucu raporla

### 3. Release (AAB Upload)

Kullanıcı "release", "AAB yükle", "Play Store'a at" dediğinde:
1. AAB dosyasının varlığını doğrula
2. `release --app <id> --aab <path>` çalıştır
3. Track ve versionCode bilgisini raporla

### 4. Dosya Düzenleme

- `config.json` değişikliklerinde JSON şemasını koru
- `.txt` metin dosyalarında karakter limitlerine dikkat et (title: 30, short: 80, full: 4000)
- Görsellerde format ve boyut kurallarını kontrol et (icon: 512×512 PNG, featureGraphic: 1024×500 PNG)

### 5. Güvenlik

- `serviceAccount` JSON dosyaları asla commit'lenmez
- `.env` dosyası yoktur; hassas bilgiler `config.json`'da göreceli yolla referans edilir
- Service account dosyaları genellikle `/home/akn/secrets/<app>/` altında tutulur

---

## 🎨 Kod Stili

- **Python:** PEP 8, type hints tercih edilir
- **JSON:** 2 boşluk indent, `ensure_ascii=False`
- **Dosya adlandırma:** Shell `kebab-case.sh`, Python `snake_case.py`

---

## 🔗 Wiki Cross-Reference

- `[[wiki/play-store-api]]` → Play Store API kullanım detayları
- `[[wiki/android-publisher]]` → Android Publisher API v3 reference
- `[[wiki/uygulama-gelistir-play]]` → Proje özel dokümantasyon
- Bu proje değişikliklerinde `wiki topla` akışı root `AGENTS.md`'ye göre işler.

---

> **Son güncelleme:** 2026-05-30
> **Sistem durumu:** play-cli.py v1.0 (sync-listing, release, scaffold, validate)
