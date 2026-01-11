# Google OAuth Kurulum Rehberi

## ❗ Önemli Not
Google OAuth **opsiyoneldir**. Sistem Google girişi olmadan da tam çalışır:
- ✅ Normal kullanıcı kaydı/girişi çalışır
- ✅ Tüm hesaplama özellikleri kullanılabilir
- ⚠️ Sadece "Google ile Giriş" butonu çalışmaz

## 🚀 Google OAuth Kurulumu (İsteğe Bağlı)

### 1. Google Cloud Console'da Proje Oluşturma

1. [Google Cloud Console](https://console.cloud.google.com/) adresine gidin
2. Yeni proje oluşturun veya mevcut projeyi seçin
3. Sol menüden **APIs & Services** > **Credentials** seçin

### 2. OAuth 2.0 Client ID Oluşturma

1. **Create Credentials** > **OAuth client ID** seçin
2. Application type: **Web application**
3. Authorized JavaScript origins:
   ```
   http://localhost
   https://tarimimar.com.tr
   ```
4. Authorized redirect URIs:
   ```
   http://localhost/api/accounts/google/callback/
   https://tarimimar.com.tr/api/accounts/google/callback/
   ```
5. **Create** butonuna tıklayın
6. Client ID ve Client Secret'i kopyalayın

### 3. Credentials'ı Projeye Ekleme

#### Development (.env.local)
```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
```

#### Production (VPS)
```bash
# VPS'e bağlan
ssh akn@104.247.166.125

# .env dosyasını düzenle
cd ~/webimar
nano .env

# Şu satırları güncelle:
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here

# Kaydet (Ctrl+O, Enter, Ctrl+X)

# Container'ları restart et
docker compose -f docker-compose.prod.yml restart webimar-api
```

### 4. Test Etme

1. **Development:**
   ```bash
   ./dev-local.sh
   # veya
   ./dev-docker.sh
   ```

2. Tarayıcıda http://localhost açın
3. **Giriş Yap** > **Google ile Giriş** butonuna tıklayın
4. Google hesabınızı seçin
5. İzinleri onaylayın

## 🔧 Sorun Giderme

### "Google OAuth Client ID tanımlanmamış" Hatası

**Sebep:** Environment variable ayarlanmamış veya container restart edilmemiş

**Çözüm:**
```bash
# .env dosyasını kontrol et
cat .env | grep GOOGLE_OAUTH

# Boşsa yukarıdaki adımları takip et
# Dolu ise container'ı restart et
docker compose restart webimar-api
```

### 500 Internal Server Error

**Sebep:** Redirect URI ayarları yanlış

**Çözüm:**
1. Google Cloud Console > Credentials
2. OAuth 2.0 Client'i düzenle
3. Authorized redirect URIs'yi kontrol et:
   - ✅ Doğru: `https://tarimimar.com.tr/api/accounts/google/callback/`
   - ❌ Yanlış: `https://tarimimar.com.tr/accounts/google/callback/` (api/ eksik)

### Callback Sayfa Bulunamadı

**Sebep:** Django URL routing problemi

**Çözüm:**
```bash
# API loglarını kontrol et
docker compose logs webimar-api | grep google

# Django admin'den Social App ayarlarını kontrol et
# http://localhost/admin/ veya https://tarimimar.com.tr/admin/
# Sites: "example.com" yerine "tarimimar.com.tr" olmalı
```

## 📚 Detaylı Dokümantasyon

- [Google OAuth Resmi Dokümantasyonu](docs/google%20kayıt.md)
- [OAuth Sorun Çözümü](docs/GOOGLE_OAUTH_SORUN_COZUMU.md)

## ⚡ Hızlı Başlangıç (OAuth Olmadan)

Google OAuth kurmak istemiyorsanız:

1. Normal kullanıcı kaydı yapın: http://localhost/auth/register
2. Email ve şifre ile giriş yapın
3. Tüm özellikleri kullanmaya başlayın ✅

**Not:** Google ile giriş sadece kullanıcı kolaylığı için ekstra bir seçenektir, zorunlu değildir.
