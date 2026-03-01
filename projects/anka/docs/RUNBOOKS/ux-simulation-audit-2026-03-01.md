# UX Simülasyon Denetim Raporu — 1 Mart 2026

**Denetim Tarihi:** 1 Mart 2026  
**Kapsam:** Uçtan uca kullanıcı akışı simülasyonu (Landing → Login → Dashboard → Batch Oluştur → Batch Detay → Export → Settings → Checkout → Logout)  
**Yöntem:** Backend ve frontend kodları satır satır okunarak, bir kullanıcının siteye ilk girişinden oturumunu kapatıp bilgisayarın başından "mutlu" ayrılmasına kadarki tüm akış simüle edildi.

---

## Özet Tablo

| Seviye | Bulgu | Düzeltilen |
|--------|-------|-----------|
| **KRİTİK (Backend)** | 1 | 1 ✅ |
| **KRİTİK (Frontend)** | 1 | 1 ✅ |
| **YÜKSEK (Backend)** | 1 | 1 ✅ |
| **YÜKSEK (Frontend)** | 2 | 2 ✅ |
| **Toplam** | **5** | **5 ✅** |

---

## SİMÜLASYON AKIŞI

### 1. Landing Page → Login
Kullanıcı siteyi ziyaret eder. `middleware.ts` `anka_access_token` cookie'sini kontrol eder, yoksa `/login?redirect=...` ile yönlendirir. Login sayfasında:
- Google Identity Services script'i yüklenir
- Open redirect koruması aktif (`//evil.com` reddedilir)
- `redirectRef` ile stale closure koruması aktif
- Script cleanup unmount'ta düzgün çalışıyor

**Durum: ✅ Sorunsuz**

### 2. Login → Dashboard
`GoogleLoginView` backend'de:
- Token doğrulaması ✅
- `email_verified` kontrolü (not/falsy) ✅
- `ANKA_ADMIN_EMAILS` env-based admin promosyonu ✅
- Org auto-provisioning `OrganizationMember` üzerinden ✅
- JWT HttpOnly cookie'ler set ediliyor ✅
- `ScopedRateThrottle` (10/dk) aktif ✅

Frontend `setAuthFlag()` + `redirectRef.current` → doğru sayfaya yönlendirme ✅

**Durum: ✅ Sorunsuz**

### 3. Dashboard
Paralel fetch: `/credits/balance/`, `/batches/`, `/exports/`:
- **KRİTİK BUG BULUNDU (aşağıda)**
- Processing batch varsa 5sn auto-refresh ✅
- `?success=payment` banner'ı ✅
- `router.replace()` ile URL temizleme ✅
- NaN guard on balance ✅ (mevcut)

### 4. Batch Oluşturma
- Şehir/harita modu toggle ✅
- Onay dialog (banka havalesi stili) ✅
- Org kontrolü ve validasyon ✅
- Kredi bloke (atomic deduction) ✅
- Celery task tetikleme ✅

**Durum: ✅ Sorunsuz**

### 5. Batch Detay / İşleme
- 2sn polling ile 4 aşamalı pipeline takibi ✅
- `items` serializer'da nested olarak mevcut ✅
- `Promise.allSettled` export oluşturma ✅
- CSV formula injection koruması ✅
- Website URL protocol fix (`noopener noreferrer`) ✅

**Durum: ✅ Sorunsuz**

### 6. Export / İndirme
- Auth-gated `FileResponse` via cookie ✅
- Akıllı polling (sadece pending/processing) ✅
- Initial load + polling ayrı effect'ler ✅
- Regenerate hata yönetimi ✅

**Durum: ✅ Sorunsuz**

### 7. Settings
- Google-only kullanıcı şifre koruması ✅
- **YÜKSEK BUG BULUNDU: Bakiye her zaman 0 gösteriyordu (aşağıda)**
- Org bilgisi `/auth/organizations/` ✅

### 8. Checkout
- Iyzico script yükleme + race condition koruması ✅
- **YÜKSEK BUG BULUNDU: Bakiye her zaman 0 gösteriyordu (aşağıda)**
- Onay dialog ✅
- Başarılı ödeme sonrası dashboard redirect ✅

### 9. Logout
- **YÜKSEK BUG BULUNDU: Token expired ise logout 401 dönüyordu (aşağıda)**
- Cookie/localStorage temizliği ✅
- `/login` yönlendirmesi ✅

---

## BULUNAN VE DÜZELTİLEN HATALAR

### BE-KRİTİK-1: CreditBalanceView Tamamen Bozuk ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/credits/views.py` — `CreditBalanceView.get()`

**Sorun (3 ayrı hata aynı view'da):**

1. `user.organizations.first()` — `Organization` modelinde `users` M2M ilişkisi **yok**. İlişki `OrganizationMember` FK üzerinden. Bu satır `AttributeError` fırlatıyordu.

2. Fallback kodu `Organization.objects.create(name=..., owner=user)` — `Organization` modelinde `owner` field'ı **yok**. Bu satır `TypeError` fırlatıyordu.

3. Response tek dict dönüyordu (`{organization_id, balance, ...}`) ama frontend ve dokümanlar `CreditPackage[]` array bekliyordu.

**Etki:** `GET /api/credits/balance/` her zaman **500 Internal Server Error** dönüyordu. Dashboard, Settings ve Checkout hiçbir zaman gerçek bakiye gösteremiyordu.

**Düzeltme:**
```python
# ESKİ (Bozuk):
organization = user.organizations.first()  # ← AttributeError
if not organization:
    organization = Organization.objects.create(
        name=f"{user.username}'s Organization",
        owner=user,  # ← owner field yok
    )
    organization.users.add(user)  # ← users M2M yok

return Response({...})  # ← tek object

# YENİ (Düzeltilmiş):
from apps.accounts.models import OrganizationMember

org_ids = (
    OrganizationMember.objects
    .filter(user=user, is_active=True)
    .values_list('organization_id', flat=True)
)

results = []
for org in Organization.objects.filter(id__in=org_ids):
    credit_package, _ = CreditPackage.objects.get_or_create(
        organization=org, defaults={'balance': 0}
    )
    results.append({
        'id': str(credit_package.id),
        'organization': str(org.id),
        'balance': str(credit_package.balance),
        ...
    })

return Response(results)  # ← array
```

---

### FE-KRİTİK-1: Dashboard `credits.reduce()` Çökme ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/dashboard/page.tsx`

**Sorun:**
```typescript
const creditsData = await fetchAPI<CreditPackage[]>('/credits/balance/')
setCredits(creditsData || [])
// ...
const totalBalance = credits.reduce(...)  // ← credits tek object ise TypeError!
```

Backend tek dict döndüğünde `creditsData` bir plain object oluyordu. `creditsData || []` truthy olduğu için object kalıyordu. Sonraki render'da `credits.reduce()` → **TypeError: credits.reduce is not a function**. React ErrorBoundary hata sayfası gösteriyordu.

**Düzeltme:**
```typescript
const creditsRaw = await fetchAPI<CreditPackage[] | CreditPackage>('/credits/balance/')
const creditsData = Array.isArray(creditsRaw) ? creditsRaw : (creditsRaw ? [creditsRaw] : [])
setCredits(creditsData)
```

---

### FE-YÜKSEK-1: Settings Sayfası Bakiye Her Zaman 0 ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/settings/page.tsx`

**Sorun:**
```typescript
const total = Array.isArray(creditData)
  ? creditData.reduce(...)
  : 0  // ← Backend tek object dönünce buraya düşüyor → bakiye 0
```

`Array.isArray()` guard backend'in tek dict response'u için `false` döndürüyordu. Kullanıcı bakiyesi ne olursa olsun "0" gösteriliyordu.

**Düzeltme:** Response'u array'e normalize eden guard eklendi:
```typescript
const creditArr = Array.isArray(creditRaw) ? creditRaw : (creditRaw ? [creditRaw] : [])
const total = creditArr.reduce(...)
```

---

### FE-YÜKSEK-2: Checkout Sayfası Bakiye Her Zaman 0 ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/checkout/page.tsx`

**Sorun:** Settings ile aynı `Array.isArray()` guard sorunu.

**Düzeltme:** Aynı normalizasyon pattern'ı uygulandı.

---

### BE-YÜKSEK-1: LogoutView Token Expired İken Çıkış Yapılamıyor ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py` — `LogoutView`

**Sorun:**
```python
permission_classes = (IsAuthenticated,)
```

Access token süresi dolmuş bir kullanıcı "Çıkış Yap" butonuna tıkladığında:
1. Frontend `POST /api/auth/logout/` gönderir
2. `IsAuthenticated` guard 401 döner
3. `api-client.ts` `tryRefreshToken()` çalıştırır
4. Refresh da expired ise → `handle401()` → `/login` redirect
5. **Refresh token asla blacklist edilmez** (7 gün boyunca yeniden kullanılabilir)
6. Kullanıcı uygulama arayüzünde "Çıkış Yap"a bastığı halde arka planda çıkış yapılmamış

**Ek sorun:** Refresh token body'de gelmediğinde 400 dönüyordu; cookie-tabanlı flow'da refresh cookie her zaman gelmez.

**Düzeltme:**
```python
# AllowAny: Expired token ile de çıkış yapılabilsin
permission_classes = (AllowAny,)

# Refresh token yoksa da başarılı dön (cookie temizliği yeterli)
if refresh_token:
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        pass

# Her durumda cookie'leri temizle (hata durumunda bile)
clear_jwt_cookies(response)
```

---

## ETKİLENEN DOSYALAR

| Dosya | Değişiklikler |
|-------|--------------|
| `services/backend/apps/credits/views.py` | CreditBalanceView: OrganizationMember kullanımı, array response |
| `services/backend/apps/accounts/views.py` | LogoutView: AllowAny, graceful token handling, cookie cleanup on error |
| `services/backend/apps/accounts/tests/test_auth.py` | test_logout_without_refresh_token: artık 200 bekliyor |
| `services/frontend/app/(dashboard)/dashboard/page.tsx` | Defensive array guard for credits response |
| `services/frontend/app/(dashboard)/settings/page.tsx` | Array normalization for balance calculation |
| `services/frontend/app/(dashboard)/checkout/page.tsx` | Array normalization for balance calculation |

---

## BACKEND NOTU — Önceki Audit'lerden Devam Eden Düzeltmeler Hâlâ Yerinde

- `RefreshTokenView._mutable` guard ✅
- `email_verified` logic (`not email_verified`) ✅
- `ANKA_ADMIN_EMAILS` env var ✅
- `PATCH /me/` email validation ✅
- `ChangePasswordView` Google-only guard ✅
- `ScopedRateThrottle` auth endpoint'leri ✅
- `api-client.ts` header merge fix ✅
- `handle401()` redirect koruması ✅
- Exports sonsuz döngü fix ✅
- Open redirect koruması ✅
- NaN bakiye koruması (Dashboard/Settings/Checkout) ✅
- CSV formula injection koruması ✅

---

## TEST SONUÇLARI

```
21 passed, 0 failed (apps/accounts + apps/credits)
```

---

## ÖNERİLER (Gelecek)

1. **CreditBalanceView test coverage:** Yeni array response formatı için unit test yazılmalı (org üyeliği olan, olmayan, çoklu org).
2. **Session Timeout UX:** 30dk inaktivitede "oturumunuz sona ermek üzere" uyarısı.
3. **Playwright E2E:** Login → dashboard → batch → export → download → logout otomatik test.
4. **Error Boundary test:** Dashboard credits endpoint 500 dönerse ErrorBoundary'nin doğru çalıştığı test edilmeli.
5. **Accessibility (a11y):** Modal/menü'lerde `aria-*`, keyboard navigation, focus trap.

---

## İlgili Dokümanlar

- [Önceki UX Denetim Raporu (Mart 2026 — Önceki)](ux-simulation-audit-2026-03.md)
- [Önceki UX Denetim Raporu (Temmuz 2026)](ux-simulation-audit-2026-07.md)
- [Sistem Akışı Kuş Bakışı](sistem-akisi-kusbakisi.md)
- [API Güvenlik Politikası](../SECURITY/api-security-policy.md)
