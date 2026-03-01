# UX Simülasyon Denetim Raporu — Mart 2026

**Denetim Tarihi:** 1 Mart 2026  
**Kapsam:** Uçtan uca kullanıcı akışı simülasyonu (Landing → Login → Dashboard → Batch Oluştur → Batch Detay → Export → Settings → Checkout → Logout)  
**Yöntem:** Backend ve frontend kodları satır satır okunarak, bir kullanıcının siteye ilk girişinden oturumunu kapatıp bilgisayarın başından "mutlu" ayrılmasına kadarki tüm akış simüle edildi.

---

## Özet Tablo

| Seviye | Bulgu | Düzeltilen |
|--------|-------|-----------|
| **KRİTİK (Frontend)** | 2 | 2 ✅ |
| **YÜKSEK (Frontend)** | 3 | 3 ✅ |
| **ORTA (Frontend)** | 1 | 1 ✅ |
| **Toplam** | **6** | **6 ✅** |

---

## SİMÜLASYON AKIŞI

### 1. Landing Page → Login
Kullanıcı ana sayfayı ziyaret eder, "Başlayın" CTA'sına tıklar. `proxy.ts` cookie kontrolü yapar, cookie yoksa `/login?redirect=...` ile yönlendirir. Login sayfasında Google Identity Services yüklenir, kullanıcı Google butonu ile giriş yapar.

### 2. Login → Dashboard  
`GoogleLoginView` backend'de token doğrulaması yapar, kullanıcı oluşturulur/güncellenir, organizasyon auto-provision edilir, JWT cookie'ler set edilir. Frontend `setAuthFlag()` ile localStorage günceller ve `redirectRef.current` (varsayılan: `/dashboard`) adresine yönlendirir.

### 3. Dashboard
Paralel fetch: `/credits/balance/`, `/batches/`, `/exports/`. Kredi bakiyesi, son batch'ler, hızlı işlemler ve son indirmeler gösterilir. Processing batch varsa 5sn auto-refresh aktif.

### 4. Batch Oluşturma
Şehir/harita modu + sektör + kayıt sayısı formu. Onay dialog'u açılır. Backend'de org kontrolü, kredi bakiye kontrolü (atomic deduction), Celery task tetiklenir.

### 5. Batch Detay / İşleme
2sn polling ile 4 aşamalı pipeline takibi. Sonuç tablosu: firma, telefon, website, email, adres. CSV indirme (client-side) + Export oluşturma (server-side).

### 6. Export / İndirme
Auth-gated `FileResponse` endpoint. Süresi dolan URL'ler için regenerate. Akıllı polling.

### 7. Settings
Hesap bilgileri, bakiye, şifre değiştirme (Google-only kullanıcılar korumalı).

### 8. Checkout
3 kredi paketi, Iyzico entegrasyonu, başarılı ödeme sonrası dashboard'a yönlendirme.

### 9. Logout
Sidebar menü → Çıkış Yap → `POST /auth/logout/` → cookie/localStorage temizlik → `/login` yönlendirmesi.

---

## BULUNAN VE DÜZELTLEN HATALAR

### FE-KRİTİK-1: `handle401()` Redirect Kaybı ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/src/lib/api-client.ts` — `handle401()`

**Sorun:**  
```typescript
window.location.href = '/login';
```
Token refresh başarısız olduğunda kullanıcı `/login`'e yönlendiriliyordu ancak **mevcut sayfa yolu korunmuyordu**. Bu durumda kullanıcı oturum yeniledikten sonra her zaman dashboard'a gidiyordu — batch detay, exports, settings gibi sayfadaki konumunu kaybediyordu.

**Etki:** `ProtectedRoute` ve `proxy.ts` redirect parametresini doğru işlese de, API istekleri sırasında oluşan 401'ler bu mekanizmayı bypass ediyordu. Kullanıcı oturum süresi dolduğunda yerini kaybediyordu.

**Düzeltme:**
```typescript
const currentPath = window.location.pathname;
const redirectParam =
  currentPath && currentPath !== '/' && currentPath !== '/login'
    ? `?redirect=${encodeURIComponent(currentPath)}`
    : '';
window.location.href = `/login${redirectParam}`;
```

---

### FE-KRİTİK-2: Exports Sayfası Sonsuz Döngü ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/exports/page.tsx`

**Sorun:**  
```tsx
useEffect(() => {
    loadData()         // ← exports state'ini günceller
    const interval = setInterval(() => { ... }, 8000)
    return () => clearInterval(interval)
}, [exports])          // ← exports değişince tekrar çalışır → loadData → exports değişir → ...
```

`useEffect` dependency array'inde `exports` bulunuyordu ve effect body'si `loadData()` çağırıyordu. `loadData()` her çalıştığında `setExports()` ile state güncelleniyordu, bu da `exports` referansını değiştirip effect'i tekrar tetikliyordu. **Sonsuz API çağrısı döngüsü** oluşuyordu.

**Etki:** Exports sayfası açıldığında backend'e saniyede birçok kez istek atılıyor, UI donuyor, tarayıcı yavaşlıyordu.

**Düzeltme:** Effect ikiye bölündü:
1. İlk yükleme: `useEffect(() => { loadData() }, [])` — tek seferlik
2. Akıllı polling: `useEffect(() => { if (!hasPending) return; setInterval(...) }, [exports])` — sadece pending/processing export varsen polling başlar, tümü bitince durur

---

### FE-YÜKSEK-1: Settings Sayfası NaN Bakiye ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/settings/page.tsx`

**Sorun:**  
```typescript
creditData.reduce((sum, pkg) => sum + parseFloat(pkg.balance || '0'), 0)
```
`parseFloat('abc')` → `NaN`, `sum + NaN` → `NaN`. Dashboard sayfasında `isNaN` guard mevcuttu ama settings sayfasında eksikti.

**Etki:** Backend'den beklenmeyen format gelmesi durumunda "NaN" görüntüleniyordu.

**Düzeltme:**
```typescript
creditData.reduce((sum, pkg) => {
    const val = parseFloat(pkg.balance || '0')
    return sum + (isNaN(val) ? 0 : val)
}, 0)
```

---

### FE-YÜKSEK-2: Checkout Sayfası NaN Bakiye ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/checkout/page.tsx`

**Sorun:** Settings sayfasıyla aynı `parseFloat` NaN sorunu.

**Düzeltme:** Aynı `isNaN` guard pattern'ı uygulandı.

---

### FE-YÜKSEK-3: Login Sayfası Open Redirect Zafiyeti ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(auth)/login/page.tsx`

**Sorun:**  
```typescript
const redirectTo = searchParams.get('redirect') || '/dashboard'
```
`redirect` query parametresi doğrulanmadan kullanılıyordu. Kötü niyetli bir link: `/login?redirect=//evil.com` → Next.js `router.push('//evil.com')` durumunda protocol-relative URL olarak yorumlanabilir.

**Etki:** Phishing saldırılarında kullanılabilecek open redirect.

**Düzeltme:**
```typescript
const rawRedirect = searchParams.get('redirect') || '/dashboard'
const redirectTo = rawRedirect.startsWith('/') && !rawRedirect.startsWith('//') ? rawRedirect : '/dashboard'
```

---

### FE-ORTA-1: Batch Export Kısmi Hata Yönetimi ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/batch/[id]/page.tsx`

**Sorun:**  
```typescript
await fetchAPI('/exports/', { method: 'POST', body: JSON.stringify({ batch: batch.id, format: 'csv' }) })
await fetchAPI('/exports/', { method: 'POST', body: JSON.stringify({ batch: batch.id, format: 'xlsx' }) })
setExportCreated(true)
addToast('Export oluşturuldu!', 'success')
```
İki sıralı istek yapılıyordu. CSV başarıyla oluşturulursa ama XLSX hata alırsa, catch bloğuna düşüyor ve kullanıcıya sadece hata gösteriliyordu — CSV'nin başarılı olduğu bildirilmiyordu.

**Etki:** Kısmi başarı durumunda kullanıcı sadece hata mesajı görüyor, başarılı oluşturulan export'ı fark etmiyordu.

**Düzeltme:** `Promise.allSettled()` kullanımına geçildi:
- Tümü başarılı → success toast
- Kısmi başarı → warning toast ("Bazı formatlar oluşturuldu ancak bir kısmı hata aldı")
- Tümü başarısız → error toast

---

## ETKİLENEN DOSYALAR

| Dosya | Değişiklikler |
|-------|--------------|
| `services/frontend/src/lib/api-client.ts` | handle401 redirect path koruması |
| `services/frontend/app/(dashboard)/exports/page.tsx` | Sonsuz döngü fix, initial load + smart polling ayrımı |
| `services/frontend/app/(dashboard)/settings/page.tsx` | NaN guard on balance calculation |
| `services/frontend/app/(dashboard)/checkout/page.tsx` | NaN guard on balance calculation |
| `services/frontend/app/(auth)/login/page.tsx` | Open redirect validation |
| `services/frontend/app/(dashboard)/batch/[id]/page.tsx` | Promise.allSettled for partial export failure handling |

---

## BACKEND NOTU

Önceki denetimlerden (Temmuz 2026) düzeltilen backend bulguları hâlâ yerinde:
- `RefreshTokenView._mutable` guard ✅
- `email_verified` logic ✅  
- `ANKA_ADMIN_EMAILS` env var ✅
- `PATCH /me/` email validation ✅
- `ChangePasswordView` Google-only guard ✅
- `ScopedRateThrottle` auth endpoint'leri ✅

Bu denetimde yeni backend hatası **tespit edilmedi**.

---

## ÖNERİLER (Gelecek)

1. **Session Timeout UX:** 30dk inaktivitede "oturumunuz sona ermek üzere" uyarısı.
2. **Logout token blacklist edge case:** Refresh token expired ise `LogoutView` 401 dönüyor; backend `AllowAny` + cookie-based blacklist daha güvenli olabilir.
3. **Playwright E2E:** Login → batch → export → download akışı otomatik test.
4. **Accessibility (a11y):** Modal/menü'lerde `aria-*`, keyboard navigation, focus trap.
5. **Loading skeleton:** Dashboard ve batch detail sayfalarında skeleton UI.

---

## İlgili Dokümanlar

- [Önceki UX Denetim Raporu (Temmuz 2026)](ux-simulation-audit-2026-07.md)
- [Sistem Akışı Kuş Bakışı](sistem-akisi-kusbakisi.md)
- [API Güvenlik Politikası](../SECURITY/api-security-policy.md)
