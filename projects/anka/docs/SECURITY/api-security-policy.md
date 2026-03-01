# API Güvenlik Politikası

**Son Güncelleme:** 28 Şubat 2026  
**Sahip:** Backend Geliştirme Ekibi  
**Kapsam:** Anka Platform REST API (`/api/*`)

---

## 1. Kimlik Doğrulama (Authentication)

### 1.1 Token Akışı

```
Kullanıcı → POST /api/auth/google/ (id_token) → Backend doğrular → JWT (access + refresh) döner
```

| Token | Ömür | Kullanım |
|-------|------|----------|
| Access Token | 15 dakika | API istekleri (`Authorization: Bearer <token>`) |
| Refresh Token | 7 gün | Access token yenileme (`POST /api/auth/token/refresh/`) |

### 1.2 Token Yaşam Döngüsü

1. **Oluşturma:** Google OIDC doğrulama sonrası
2. **Yenileme:** Refresh token ile (rotation aktif — her refresh'te yeni token çifti)
3. **İptal:** Logout'ta refresh token blacklist'e alınır
4. **Otomatik geçersizlik:** SECRET_KEY değiştiğinde tüm token'lar geçersiz olur

### 1.3 Kurallar

- ✅ Sadece Google OIDC login kabul edilir (MVP)
- ✅ Email whitelist kontrolü (`ANKA_ALLOWED_GOOGLE_EMAILS`)
- ✅ Google email doğrulama zorunlu (`email_verified: true`)
- ✅ Test-login endpoint production'da devre dışı
- ✅ Google-only kullanıcılar için `set_unusable_password()`
- ⚠️ **TODO:** JWT token'ları HttpOnly cookie'ye taşınmalı (XSS koruması)

## 2. Yetkilendirme (Authorization)

### 2.1 Varsayılan Politika

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}
```

Tüm endpoint'ler varsayılan olarak **kimlik doğrulaması gerektirir**. Public endpoint'ler açıkça `AllowAny` ile işaretlenmelidir.

### 2.2 Permission Sınıfları

| Sınıf | Kullanım |
|-------|----------|
| `IsAuthenticated` | Varsayılan — giriş yapmış kullanıcı |
| `AllowAny` | Sadece auth endpoint'leri (login, health) |
| `IsAdminUser` | Sadece admin panel |

### 2.3 Kural: Yeni Endpoint Ekleme

```python
# ✅ DOĞRU — Açık permission belirtilmiş
class MyView(APIView):
    permission_classes = [IsAuthenticated]

# ❌ YANLIŞ — Public endpoint permission belirtilmemiş (default kullanılır ama açık olmalı)
class PublicView(APIView):
    permission_classes = [AllowAny]  # ← bunu mutlaka yazın
```

## 3. Rate Limiting (Hız Sınırlaması)

### 3.1 Katmanlı Koruma

| Katman | Uygulama | Limitler |
|--------|----------|---------|
| Nginx (L7) | `limit_req` directive | API: 10 req/s, Web: 5 req/s |
| DRF (App) | `DEFAULT_THROTTLE_CLASSES` | Anon: 30/dk, User: 120/dk |
| Endpoint-özel | Custom throttle scope | Auth: 10/dk, Sensitive: 5/dk |

### 3.2 DRF Throttle Konfigürasyonu

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',       # Anonim kullanıcılar
        'user': '120/minute',      # Giriş yapmış kullanıcılar
        'auth': '10/minute',       # Login/register endpoint'leri
        'sensitive': '5/minute',   # Parola değişikliği, token refresh
    },
}
```

### 3.3 Özel Throttle Kullanımı

Hassas endpoint'lere özel throttle scope uygulanması:

```python
from rest_framework.throttling import ScopedRateThrottle

class GoogleLoginView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'
```

## 4. Input Validation (Girdi Doğrulama)

### 4.1 Temel Kurallar

- ✅ Tüm API girdileri DRF serializer'lardan geçmelidir
- ✅ `CharField` için `max_length` zorunlu
- ✅ Numeric alanlar için `min_value` / `max_value`
- ❌ Raw SQL kullanmayın — sadece Django ORM
- ❌ `request.data`'yı doğrudan model'e aktarmayın

### 4.2 Örnek Doğrulama

```python
# ✅ DOĞRU
class BatchCreateSerializer(serializers.Serializer):
    sector_id = serializers.IntegerField(min_value=1)
    city = serializers.CharField(max_length=100)
    districts = serializers.ListField(
        child=serializers.CharField(max_length=100),
        max_length=20  # Maksimum 20 ilçe
    )

# ❌ YANLIŞ — Doğrulama yok
data = request.data
Batch.objects.create(**data)  # Asla bunu yapmayın!
```

### 4.3 File Upload Kuralları

- Desteklenen formatlar: `.xlsx`, `.csv`, `.json` (explicit whitelist)
- Maksimum dosya boyutu: 10 MB
- MIME type doğrulama (sadece extension'a güvenmeyin)
- Upload dizini web root dışında olmalı
- Yüklenen dosya adını sanitize edin (`django.utils.text.get_valid_filename`)

## 5. CORS Politikası

### 5.1 Production

```python
# prod.py
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
# .env.production: CORS_ALLOWED_ORIGINS=https://ankadata.com.tr
```

### 5.2 Development

```python
# dev.py
CORS_ALLOW_ALL_ORIGINS = True  # Sadece geliştirme ortamında!
```

### 5.3 Kural

- Production'da `CORS_ALLOW_ALL_ORIGINS` **ASLA** `True` olmamalıdır
- Yeni domain eklemek için `.env.production`'a ekleyin

## 6. CSRF Koruması

### 6.1 Konfigürasyon (Production)

```python
CSRF_TRUSTED_ORIGINS = [...]  # .env.production'dan
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### 6.2 İstisna: Webhook Endpoint'leri

```python
@csrf_exempt  # Webhook'lar CSRF'ten muaf — HMAC ile korunur
def iyzico_webhook_handler(request):
    if not verify_hmac_signature(request):
        return HttpResponseForbidden()
```

CSRF exempt endpoint'ler **mutlaka** alternatif doğrulama mekanizması (HMAC, API key) kullanmalıdır.

## 7. Hassas Veri Yönetimi

### 7.1 Loglanmaması Gereken Veriler

- Kullanıcı parolaları (hash dahil)
- JWT token değerleri
- API key'ler
- Kredi kartı bilgileri
- Tam email adresleri (maskelenmeli: `a***@example.com`)

### 7.2 Log Maskeleme Örnegi

```python
import hashlib

def mask_email(email: str) -> str:
    """a***@example.com formatında maskele"""
    if '@' not in email:
        return '***'
    local, domain = email.split('@', 1)
    return f"{local[0]}***@{domain}"

def hash_pii(value: str) -> str:
    """PII için tek yönlü hash (log correlation için)"""
    return hashlib.sha256(value.encode()).hexdigest()[:12]
```

### 7.3 Sentry (Error Tracking)

```python
sentry_sdk.init(
    send_default_pii=False,  # Kullanıcı IP, cookie, request body gönderME
)
```

## 8. HTTP Güvenlik Header'ları

| Header | Değer | Kaynak |
|--------|-------|--------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Django + Nginx |
| `X-Frame-Options` | `DENY` | Django |
| `X-Content-Type-Options` | `nosniff` | Django + Nginx |
| `Content-Security-Policy` | Konfigüre edilmiş | Nginx |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Nginx |

## 9. API Versiyonlama ve Deprecation

- API versiyonu URL prefix ile (`/api/v1/`, `/api/v2/`)
- Deprecated endpoint'ler 6 ay boyunca `Sunset` header'ı ile çalışır
- Breaking change'ler yeni versiyon altında yayınlanır

## 10. Güvenlik Review Checklist (Yeni Endpoint)

Yeni bir API endpoint eklerken:

```
[ ] Permission class açıkça belirtilmiş
[ ] Input validation serializer ile yapılıyor
[ ] Rate limiting scope uygun
[ ] Hassas veri loglanmıyor
[ ] SQL injection riski yok (raw SQL kullanılmıyor)
[ ] CORS policy uyumlu
[ ] Error response'larda internal detay sızmıyor
[ ] OpenAPI schema güncellenmiş (drf-spectacular)
[ ] Test yazılmış (happy path + edge case + unauthorized)
[ ] Redirect parametreleri (query string) doğrulanmış — open redirect koruması
```

## 11. Frontend Güvenlik Kuralları (Mart 2026)

### 11.1 Open Redirect Koruması

Login sayfasında `?redirect=...` parametresi kullanılıyorsa:
- **Sadece göreceli path** (`/dashboard`, `/exports` vb.) kabul edilmeli
- Protocol-relative URL'ler (`//evil.com`) reddedilmeli
- Mutlak URL'ler (`https://...`) reddedilmeli

```typescript
// Doğru
const redirectTo = rawRedirect.startsWith('/') && !rawRedirect.startsWith('//') 
  ? rawRedirect 
  : '/dashboard';
```

### 11.2 Token Expire Redirect Koruması

`api-client.ts` içindeki `handle401()` fonksiyonu, 401 alındığında kullanıcı konumunu (`window.location.pathname`) `?redirect=...` parametresiyle login sayfasına taşımalıdır. Böylece kullanıcı yeniden giriş sonrası orijinal sayfasına döner.

### 11.3 CSV Formula Injection

İstemci tarafı CSV üretiminde `=`, `+`, `-`, `@`, `\t`, `\r` ile başlayan hücreler sanitize edilmelidir:
```typescript
if (/^[=+\-@\t\r]/.test(cellValue)) {
    cellValue = `'${cellValue}`;
}
```

### 11.4 NaN Guard

Backend'den gelen `balance` veya sayısal string alanlar `parseFloat()` sonrası mutlaka `isNaN` guard ile korunmalıdır. Geçersiz değerlerde `0` döndürülmelidir.
