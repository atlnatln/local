---
name: play-store-cli
description: |
  Google Play Store API CLI otomasyonu için Kimi skill'i.
  uygulama-gelistir-play projesindeki `scripts/play-cli.py` aracını
  kullanarak store listing senkronizasyonu, AAB release, validate ve
  scaffold işlemlerini yönetir.

  Trigger when user says:
  - "play store sync", "play store senkronize et", "mağaza girişini güncelle"
  - "play store release", "play store'a yükle", "AAB yükle", "release yap"
  - "play store validate", "doğrula", "kontrol et"
  - "play store scaffold", "yeni uygulama ekle", "yeni app oluştur"
  - "play store dry run", "dry run yap"
  - Any variation of Play Store upload, sync, release, validate commands
  related to the uygulama-gelistir-play system.
---

# play-store-cli Skill

## Hızlı Başlangıç

Tüm komutlar şu dizinde çalıştırılır:
```bash
cd /home/akn/local/uygulama-gelistir-play
python scripts/play-cli.py <komut> [args]
```

## Komutlar

### Sync Listing

Kullanıcı "mağaza girişini güncelle" veya "play store sync" dediğinde:

```bash
cd /home/akn/local/uygulama-gelistir-play
python scripts/play-cli.py validate --app <app-id>
# Eğer validate başarılıysa:
python scripts/play-cli.py sync-listing --app <app-id>
```

Dry-run modu:
```bash
python scripts/play-cli.py sync-listing --app <app-id> --dry-run
```

### Release (AAB Upload)

Kullanıcı "release", "AAB yükle", "Play Store'a at" dediğinde:

```bash
cd /home/akn/local/uygulama-gelistir-play
python scripts/play-cli.py release --app <app-id> --aab <aab-path>
```

Varsayılan AAB yolu (mathlock-play için):
```
/home/akn/local/projects/mathlock-play/app/build/outputs/bundle/release/app-release.aab
```

Dry-run modu:
```bash
python scripts/play-cli.py release --app <app-id> --aab <aab-path> --dry-run
```

### Validate

Kullanıcı "doğrula", "kontrol et", "validate" dediğinde:

```bash
cd /home/akn/local/uygulama-gelistir-play
python scripts/play-cli.py validate --app <app-id>
```

### Scaffold (Yeni App)

Kullanıcı "yeni uygulama ekle", "yeni app oluştur" dediğinde:

```bash
cd /home/akn/local/uygulama-gelistir-play
python scripts/play-cli.py scaffold \
  --app <app-id> \
  --package <package-name> \
  --title "<Uygulama Başlığı>" \
  --lang <lang-code>
```

Sonra kullanıcıya şunları söyle:
1. `apps/<app-id>/config.json`'da `serviceAccount` yolunu doldur
2. `metadata/<lang>/title.txt`, `short_description.txt`, `full_description.txt` dosyalarını doldur
3. Görselleri (icon, featureGraphic, screenshots) `metadata/<lang>/images/` altına yerleştir
4. Play Console web'den "Yeni uygulama oluştur" yap (API ile yeni app oluşturulamaz)
5. `validate` çalıştır ve `sync-listing` ile upload et

## Hata Durumları

| Hata | Çözüm |
|------|-------|
| `Config bulunamadı` | `apps/<app-id>/config.json` dosyasının varlığını kontrol et |
| `Service account bulunamadı` | `config.json`'daki `serviceAccount` yolunun doğru olduğunu kontrol et |
| `title.txt boş` | `metadata/<lang>/title.txt` dosyasını doldur (max 30 karakter) |
| `icon.png eksik` | 512×512 PNG ikonu `metadata/<lang>/images/icon/icon.png` yoluna yerleştir |
| `AAB bulunamadı` | AAB dosyasının varlığını ve yolunu kontrol et |
| API hatası | Service account'un Play Console'da `Release Manager` veya `Admin` rolüne sahip olduğunu doğrula |

## Dosya Yolları (Kesin)

| Kaynak | Yol |
|--------|-----|
| CLI script | `/home/akn/local/uygulama-gelistir-play/scripts/play-cli.py` |
| Apps dizini | `/home/akn/local/uygulama-gelistir-play/apps/` |
| Mevcut app (mathlock-play) | `/home/akn/local/uygulama-gelistir-play/apps/mathlock-play/` |
| mathlock-play AAB (varsayılan) | `/home/akn/local/projects/mathlock-play/app/build/outputs/bundle/release/app-release.aab` |

## Önemli Notlar

- Her komut `--dry-run` flag'i ile test edilebilir. Gerçek API çağrısı yapılmaz.
- `sync-listing` mevcut görselleri siler ve yeniden upload eder.
- Yeni uygulama oluşturma (Play Console'da ilk açılış) API ile yapılamaz, web arayüzünden manuel yapılmalıdır.
- `scaffold` sadece dosya yapısı oluşturur, Play Console'da uygulama oluşturmaz.
