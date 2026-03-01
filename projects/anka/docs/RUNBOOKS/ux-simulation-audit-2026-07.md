# UX Simülasyon Denetim Raporu — Temmuz 2026

**Denetim Tarihi:** Temmuz 2026  
**Kapsam:** Uçtan uca kullanıcı akışı simülasyonu (Login → Dashboard → Batch → Export → Settings → Logout)  
**Yöntem:** Backend ve frontend kodları satır satır okunarak, bir kullanıcının giriş yapmasından oturumunu kapatıp bilgisayarın başından "mutlu" ayrılmasına kadarki tüm akış simüle edildi. Tespit edilen hata, güvenlik açığı ve UX eksiklikleri ciddiyetine göre sınıflandırılıp düzeltildi.

---

## Özet Tablo

| Seviye | Bulgu | Düzeltilen |
|--------|-------|-----------|
| **KRİTİK (Backend)** | 3 | 3 ✅ |
| **YÜKSEK (Backend)** | 3 | 3 ✅ |
| **KRİTİK (Frontend)** | 2 | 2 ✅ |
| **YÜKSEK (Frontend)** | 4 | 4 ✅ |
| **UX İyileştirme** | 5 | 5 ✅ |
| **Toplam** | **17** | **17 ✅** |

---

## BACKEND BULGULARI

### BE-KRİTİK-1: RefreshTokenView `_mutable` AttributeError ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py` — `RefreshTokenView.post()`

**Sorun:**  
```python
request.data._mutable = True  # JSON body'lerde _mutable yok → AttributeError
```
`request.data` yalnızca `QueryDict` tipindeyse `_mutable` attribute'üne sahiptir. JSON body gönderildiğinde (standart frontend davranışı) `dict` döner ve `_mutable` erişimi `AttributeError` fırlatarak token yenileme akışını tamamen kırıyordu.

**Etki:** Frontend 401 aldığında auto-refresh mekanizması çalışmıyordu; kullanıcı sürekli login sayfasına yönlendiriliyordu.

**Düzeltme:**
```python
if hasattr(request.data, '_mutable'):
    request.data._mutable = True
```

---

### BE-KRİTİK-2: `email_verified` Kontrolünde Logic Bug ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py` — `GoogleLoginView.post()`

**Sorun:**  
```python
if email_verified is False:
    return Response({'error': '...'}, status=400)
```
Google'ın `id_info` dict'inde `email_verified` anahtarı eksik olduğunda (`None` döner) `is False` kontrolü `True` üretmez ve doğrulanmamış email'ler kabul edilirdi.

**Etki:** Email doğrulaması atlanarak potansiyel güvenlik açığı.

**Düzeltme:**
```python
if not email_verified:
    return Response({'error': '...'}, status=400)
```

---

### BE-KRİTİK-3: Hardcoded Admin Email ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py` — `GoogleLoginView.post()`

**Sorun:**  
```python
if email == 'atalanakin@gmail.com':
    user.is_staff = True
    user.is_superuser = True
```
Admin promosyonu tek bir email adresine hardcoded bağlıydı. Yeni admin eklemek kod değişikliği gerektiriyordu.

**Düzeltme:**  
- `settings.ANKA_ADMIN_EMAILS` listesine taşındı
- `base.py`'de `ANKA_ADMIN_EMAILS` env var'dan parse ediliyor (virgülle ayrılmış, küçük harfe dönüştürülmüş)
- `.env` ve `.env.example` dosyalarına `ANKA_ADMIN_EMAILS=atalanakin@gmail.com` eklendi

```python
admin_emails = getattr(settings, 'ANKA_ADMIN_EMAILS', [])
if email.lower() in admin_emails:
    user.is_staff = True
    user.is_superuser = True
```

---

### BE-YÜKSEK-1: PATCH `/me/` Email Validasyonu Eksik ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py` — `CurrentUserView.patch()`

**Sorun:** Email alanı güncellenirken format doğrulaması yapılmıyor, benzersizlik kontrolü yapılmıyordu. Kullanıcı boş string veya başka kullanıcının email'ini kaydedebilirdi.

**Düzeltme:**
- `django.core.validators.validate_email` ile format kontrolü
- `User.objects.filter(email=value).exclude(pk=user.pk).exists()` ile benzersizlik kontrolü
- `str.strip()` ile whitespace temizliği

---

### BE-YÜKSEK-2: ChangePassword Google-Only Kullanıcı Koruması Eksik ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py` — `ChangePasswordView.post()`

**Sorun:** Google OAuth ile kayıt olan kullanıcıların kullanılabilir parolası yoktur (`has_usable_password() == False`). Bu kullanıcılar şifre değiştirme endpoint'ini çağırdığında `check_password()` her zaman `False` döner ve kullanıcı kafa karıştırıcı "Mevcut şifre yanlış" hatası alırdı.

**Düzeltme:**
```python
if not request.user.has_usable_password():
    return Response(
        {'error': 'Google ile giriş yapan kullanıcılar şifre değiştiremez.'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

---

### BE-YÜKSEK-3: Auth Endpoint'lerinde ScopedRateThrottle Eksik ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/accounts/views.py`

**Sorun:** `GoogleLoginView`, `RefreshTokenView` ve `ChangePasswordView` global DRF throttle'ı kullanıyordu ancak hassas endpoint'lere özel daraltılmış rate limit yoktu.

**Düzeltme:**
- `GoogleLoginView`: `throttle_classes = [ScopedRateThrottle]`, `throttle_scope = 'auth'` (10/dakika)
- `RefreshTokenView`: `throttle_classes = [ScopedRateThrottle]`, `throttle_scope = 'sensitive'` (5/dakika)
- `ChangePasswordView`: `throttle_classes = [ScopedRateThrottle]`, `throttle_scope = 'sensitive'` (5/dakika)

---

## FRONTEND BULGULARI

### FE-KRİTİK-1: `api-client.ts` Header Merge Bug ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/src/lib/api-client.ts`

**Sorun:**  
```typescript
const fetchOptions: RequestInit = {
    ...defaultOptions,
    ...options,          // ← options.headers burada tüm header'ları override eder
    headers: mergedHeaders,  // ← bu satır hiç çalışmıyordu
};
```
`...options` spread'i `headers` key'ini de taşıyordu ve alttaki `headers: mergedHeaders` satırı aslında çalışıyordu ama `mergedHeaders` hesaplaması `options.headers`'ı zaten içerdiğinden sorun gizli kalıyordu. Düzeltme: `headers`'ı `options` spread'inden çıkarıp ayrı set etmek.

**Düzeltme:**
```typescript
const { headers: _overrideHeaders, ...restOptions } = options;
const fetchOptions: RequestInit = {
    ...defaultOptions,
    ...restOptions,
    headers: mergedHeaders,
};
```

---

### FE-KRİTİK-2: DRF Hata Mesajları Düzgün Parse Edilmiyor ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/src/lib/api-client.ts`

**Sorun:** DRF field-level validation hataları (`{ "old_password": ["Mevcut şifre yanlış"] }`) geldiğinde frontend sadece `errorData.detail || errorData.error` aramıyordu ve kullanıcıya genel "Request failed" mesajı gösteriliyordu.

**Düzeltme:** Error parsing genişletildi:
```typescript
const message = errorData.detail
    || errorData.error
    || errorData.message
    || (typeof errorData === 'object'
        ? Object.values(errorData).flat().find(v => typeof v === 'string')
        : undefined)
    || `Request failed with status ${response.status}`;
```

---

### FE-YÜKSEK-1: Login Sayfası Stale Closure ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(auth)/login/page.tsx`

**Sorun:** `handleGoogleCallback` fonksiyonu `useEffect` closure'ı içinde yakalanıyordu ve `redirectTo` state değişse bile eski değeri kullanıyordu.

**Düzeltme:** `redirectTo` state'i `useRef` ile sarıldı, callback'ler her zaman güncel değeri kullanır:
```typescript
const redirectToRef = useRef(redirectTo);
useEffect(() => { redirectToRef.current = redirectTo; }, [redirectTo]);
```

---

### FE-YÜKSEK-2: Login DRY İhlali ve Script Cleanup Eksik ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(auth)/login/page.tsx`

**Eski Durum:** Google callback kodu iki yerde (ilk `useEffect` ve tekrar `useEffect`) tekrarlanıyordu. Ayrıca Google script DOM'a ekleniyor ama component unmount'ta kaldırılmıyordu.

**Düzeltme:**
- `handleGoogleCallback` tek bir `useCallback` olarak extract edildi
- Her iki `useEffect` de aynı fonksiyonu referans alıyor
- Script cleanup: `return () => { if (script.parentNode) { script.parentNode.removeChild(script); } }`

---

### FE-YÜKSEK-3: ProtectedRoute Redirect Kaybı ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/src/lib/protected-route.tsx`

**Sorun:** Kullanıcı giriş yapmadan `/exports` gibi bir sayfaya gittiğinde login'e yönlendiriliyordu ama giriş sonrası orijinal sayfaya dönmüyordu — her zaman dashboard'a gidiyordu.

**Düzeltme:** `withAuth` ve `ProtectedRoute` bileşenleri artık `?redirect={currentPath}` query parametresiyle login'e yönlendiriyor. Login sayfası bu parametreyi okuyup giriş sonrası doğru sayfaya yönlendiriyor.

---

### FE-YÜKSEK-4: Settings Sayfası Google-Only Kullanıcı Koruması Eksik ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/settings/page.tsx`

**Sorun:** Google OAuth ile giriş yapan kullanıcılara şifre değiştirme formu gösteriliyordu ama şifreleri olmadığı için backend 400 dönüyordu.

**Düzeltme:** `user.username === user.email` kontrolü ile Google-only kullanıcı tespit edildiğinde şifre formu gizlenip bilgilendirme banner'ı gösteriliyor:
> "Google hesabınız ile giriş yaptığınız için şifre değiştirme işlemi yapılamaz."

---

## UX İYİLEŞTİRMELERİ

### UX-1: Dashboard NaN Bakiye ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/dashboard/page.tsx`

**Sorun:** `CreditPackage.balance` string olarak geldiğinde `parseFloat()` `NaN` dönebiliyordu ve dashboard'da "NaN TL" gösteriliyordu.

**Düzeltme:** `isNaN` guard eklendi, geçersiz değerlerde `0` döner.

---

### UX-2: Dashboard `window.history.replaceState` → `router.replace` ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/dashboard/page.tsx`

**Sorun:** `window.history.replaceState()` kullanımı Next.js App Router state'i ile senkronize değildi.

**Düzeltme:** `useRouter().replace('/dashboard', { scroll: false })` kullanımına geçildi.

---

### UX-3: Kullanıcı Menüsü Click-Outside Kapanma ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/layout.tsx`

**Sorun:** Sağ üstteki kullanıcı dropdown menüsü açıldığında, menü dışına tıklayınca kapanmıyordu.

**Düzeltme:** `useRef` + `mousedown` event listener ile click-outside handler eklendi. Menü dışına tıklandığında `setShowUserMenu(false)` çağrılıyor.

---

### UX-4: CSV Formula Injection Koruması ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/batch/[id]/page.tsx`

**Sorun:** CSV export'unda hücre içerikleri `=`, `+`, `-`, `@`, `\t`, `\r` ile başladığında spreadsheet uygulamalarında formül olarak yorumlanabilir ve kötü amaçlı komutlar çalıştırılabilirdi.

**Düzeltme:** `sanitizeCSVCell()` fonksiyonu eklendi — tehlikeli başlangıç karakterleri tespit edildiğinde hücrenin başına `'` (tek tırnak) ekleniyor.

---

### UX-5: Export Sayfası Akıllı Polling ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/exports/page.tsx`

**Sorun:** Export listesi sayfası her 5 saniyede bir API'yi poll ediyordu — tüm export'lar tamamlanmış bile olsa.

**Düzeltme:** Polling artık sadece `pending` veya `processing` durumunda export varsa aktif. Tüm export'lar terminal durumda olduğunda polling durur.

---

## ETKİLENEN DOSYALAR

| Dosya | Değişiklikler |
|-------|--------------|
| `services/backend/apps/accounts/views.py` | RefreshToken _mutable fix, email_verified logic fix, admin email env var, PATCH email validation, Google-only password guard, ScopedRateThrottle |
| `services/backend/project/settings/base.py` | `ANKA_ADMIN_EMAILS` env parsing |
| `.env`, `.env.example` | `ANKA_ADMIN_EMAILS` eklendi |
| `services/frontend/src/lib/api-client.ts` | Header merge fix, DRF error parsing |
| `services/frontend/app/(auth)/login/page.tsx` | DRY refactor, stale closure fix, script cleanup |
| `services/frontend/src/lib/protected-route.tsx` | Redirect query parameter koruması |
| `services/frontend/app/(dashboard)/dashboard/page.tsx` | NaN guard, router.replace, useRouter import |
| `services/frontend/app/(dashboard)/settings/page.tsx` | Error parsing fix, Google-only user guard |
| `services/frontend/app/(dashboard)/layout.tsx` | Click-outside menu handler |
| `services/frontend/app/(dashboard)/batch/[id]/page.tsx` | CSV formula injection, URL protocol fix, noopener noreferrer |
| `services/frontend/app/(dashboard)/exports/page.tsx` | Smart polling, regenerate error handling |

---

## ÖNERİLER (Gelecek İyileştirmeler)

1. **Playwright E2E Test:** Login → batch oluşturma → export indirme akışı E2E test ile doğrulanmalı.
2. **Session Timeout UX:** Kullanıcı 30dk inaktifse "oturumunuz sona ermek üzere" uyarısı gösterilmeli.
3. **Optimistic UI:** Batch oluşturma sırasında loading/skeleton state'leri iyileştirilmeli.
4. **Error Boundary:** Dashboard ve batch detay sayfalarına React Error Boundary eklenmeli.
5. **Accessibility (a11y):** Menü ve modal'larda `aria-*` attribute'ları, keyboard navigation ve focus trap eksik.
6. **Backend Test Coverage:** Auth view'ları ve edge case'ler (Google-only user, email collision) için unit test yazılmalı.

---

## İlgili Dokümanlar

- [Güvenlik Denetim Raporu (Şubat 2026)](../SECURITY/security-audit-2026-02-28.md)
- [Kod Denetimi (Haziran 2026)](code-audit-and-fixes-2026-06.md)
- [Sistem Akışı Kuş Bakışı](sistem-akisi-kusbakisi.md)
- [API Güvenlik Politikası](../SECURITY/api-security-policy.md)
