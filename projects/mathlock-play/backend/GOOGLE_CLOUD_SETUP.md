# Google Play Hizmet Hesabı Kurulum Kılavuzu

Bu kılavuz, Mathlock backend'inin Google Play satın alma doğrulaması yapabilmesi için
gerekli Service Account ve yetkilendirme adımlarını açıklar.

---

## Genel Bakış

```
Uygulama (Android)
    │  purchase_token
    ▼
Backend (Django)
    │  purchases.products.get()
    ▼
Google Play Developer API  ←── Service Account kimlik doğrulaması
```

---

## Adım 1 — Google Cloud Console

1. [console.cloud.google.com](https://console.cloud.google.com) adresine git
2. Üst menüden projeyi seç veya **New Project** → isim: `mathlock-play`
3. Sol menü → **APIs & Services → Library**
4. **"Google Play Android Developer API"** ara → **Enable**

---

## Adım 2 — Hizmet Hesabı Oluştur

1. Sol menü → **APIs & Services → Credentials**
2. **+ Create Credentials → Service Account**
3. Dolduracakların:
   - Service account name: `mathlock-play-backend`
   - Service account ID: (otomatik dolar)
   - Description: `Mathlock Play satın alma doğrulama servisi`
4. **Create and continue**
5. **Role** adımında: `Basic → Viewer` seç (Play Console'da ayrıca yetki vereceğiz)
6. **Done**

---

## Adım 3 — JSON Anahtar Dosyasını İndir

1. Oluşturulan hesabı listeden tıkla
2. **Keys** sekmesi → **Add Key → Create new key → JSON**
3. `.json` dosyası indiriliyor (ör: `mathlock-play-backend-a1b2c3.json`)
4. Bu dosyayı güvenli bir yerde sakla — içeriği kimseyle paylaşma

---

## Adım 4 — Google Play Console'da Yetki Ver

> Bu adım kritik: Google Cloud'da hesabı oluşturdun ama Play API'ye erişim için
> **Play Console** tarafından da yetkilendirme gerekiyor.

1. [play.google.com/console](https://play.google.com/console) adresine git
2. **Setup → API access**
3. **"Link to an existing Google Cloud Project"** seçeneğinde az önce oluşturduğun
   projeyi seç → **Link**
4. **Service accounts** listesinde `mathlock-play-backend@...` görünecek
5. **Grant access** → şu izinleri seç:
   - ✅ View app information and download bulk reports (read-only)
   - ✅ Manage orders and subscriptions
6. **Invite user** → değişikliklerin aktif olması 24 saate kadar sürebilir

---

## Adım 5 — Backend'e Entegre Et

### Seçenek A — JSON dosyasını doğrudan sunucuya koy (geliştirme)

```bash
# Dosyayı backend dizinine kopyala
cp ~/Downloads/mathlock-play-backend-*.json \
   /home/akn/vps/projects/mathlock-play/backend/google-service-account.json

# settings.py zaten bu yolu varsayılan olarak kullanıyor:
# GOOGLE_PLAY_SERVICE_ACCOUNT_JSON = BASE_DIR / 'google-service-account.json'
```

> ⚠️ Bu dosyayı git'e commit ETME. `.gitignore`'a ekle:
> ```
> backend/google-service-account.json
> ```

### Seçenek B — Environment Variable (production, önerilen)

JSON içeriğini tek satır string olarak ortam değişkenine koy:

```bash
# JSON içeriğini tek satıra çevir
export GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=$(cat google-service-account.json | tr -d '\n')
```

`docker-compose.yml`'e ekle:

```yaml
services:
  mathlock_backend:
    environment:
      - GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=${GOOGLE_PLAY_SERVICE_ACCOUNT_JSON}
      - DJANGO_DEBUG=False
```

Veya VPS'te `/etc/environment` ya da systemd unit file'a:

```
Environment="GOOGLE_PLAY_SERVICE_ACCOUNT_JSON={"type":"service_account",...}"
```

### `google_play.py` JSON string desteği

`backend/credits/google_play.py` dosyasında `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`
ortam değişkeni hem dosya yolu hem de JSON **string** olarak desteklenir.
Eğer değer `{` ile başlıyorsa string olarak ayrıştırılır, aksi halde dosya yolu olarak okunur.

---

## Adım 6 — Doğrulama

```bash
# Backend'i başlat
cd /home/akn/vps/projects/mathlock-play
docker compose up -d

# Sağlık kontrolü
curl http://localhost:8003/api/mathlock/health/

# Google Play API bağlantısını test et (gerçek bir token gerekir)
# License Testing ile edinilmiş bir token varsa:
curl -X POST http://localhost:8003/api/mathlock/purchase/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "<device_token>",
    "purchase_token": "<google_play_token>",
    "product_id": "kredi_5"
  }'
```

---

## Sık Karşılaşılan Sorunlar

| Hata | Neden | Çözüm |
|------|-------|-------|
| `FileNotFoundError: google-service-account.json` | Dosya yok | Adım 5A veya 5B'yi takip et |
| `HttpError 403: The caller does not have permission` | Play Console yetkisi verilmemiş | Adım 4'ü tekrar kontrol et; 24 saat bekle |
| `HttpError 404: Purchase not found` | Token geçersiz veya test modunda | License Testing hesabı ile al |
| `HttpError 401: Invalid Credentials` | Service Account JSON bozuk | Yeni key oluştur |
| `Purchase state: 1` (cancelled) | Ödeme iptal edilmiş | Normal; `verify_purchase()` `valid=False` döner |

---

## Güvenlik Kontrol Listesi

- [ ] `google-service-account.json` `.gitignore`'da
- [ ] Production'da `DJANGO_DEBUG=False`
- [ ] Service Account'un minimum yetki prensibine uyması (yalnızca orders okuma)
- [ ] JSON anahtarını düzenli aralıklarla rotate et (IAM → Keys → Add Key → eski anahtarı sil)
- [ ] VPS'te dosya izinleri: `chmod 600 google-service-account.json`
