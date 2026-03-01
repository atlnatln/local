# Changelog — Anka Platform

Tüm önemli değişiklikler bu dosyada belgelenir.
Format: [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/)

---

## [Unreleased]

### Kritik Bug Düzeltmeleri & UX İyileştirmeleri (Haziran 2026 — Kod Denetimi)

Uçtan uca kullanıcı akışı simülasyonu ile tespit edilen 4 kritik, 3 orta seviye hata ve 2 UX iyileştirmesi.

#### Düzeltilen (Kritik)
- **Ödeme sonrası kredi yansımıyordu** — `PaymentIntent.mark_completed()` `save(update_fields=...)` olmadan çağrılıyordu, `post_save` signal kredi hiç vermiyordu. `update_fields=['status', 'completed_at', 'updated_at']` eklendi.
- **Webhook refund handler crash** — `transaction_obj.payment_intent` (yanlış) → `transaction_obj.intent` (doğru FK adı). `AttributeError` düzeltildi.
- **Webhook'ta geçersiz status değerleri** — `'REFUNDED'` STATUS_CHOICES'ta yoktu → transaction: `'error'`, intent: `'cancelled'` olarak düzeltildi.
- **Webhook variable shadow** — `status = data.get('status')` DRF `status` import'unu gölgeliyordu → `iyzico_status` olarak yeniden adlandırıldı.

#### Düzeltilen (Orta)
- **Katalog write izinleri** — Tüm authenticated kullanıcılar city/sector/filter oluşturabiliyordu → `_ReadOnlyOrAdmin` mixin ile write sadece admin'e kısıtlandı.
- **SIMPLE_JWT tekrarlanan anahtar** — `JTI_CLAIM` iki kez tanımlanmıştı → duplikasyon kaldırıldı.
- **Confirm view'da payment_id kaybı** — `mark_completed()` sadece status kaydettiği için `payment_id` kayboluyordu → ayrı `save(update_fields=['payment_id', 'updated_at'])` eklendi.

#### Eklenen (UX)
- **Batch detay: Export toast bildirimi** — Export oluşturma başarı/hata durumunda toast gösterimi + "İndirilmişlere Git" yönlendirme linki.
- **Dashboard: Son İndirmeler kartı** — Son 3 export format badge, batch bilgisi, durum göstergesi ve tarih ile gösterilir. ADR-0005 gereksinimini karşılar.

#### Belgeleme
- `docs/RUNBOOKS/code-audit-and-fixes-2026-06.md` — tam denetim raporu.
- `docs/RUNBOOKS/payments-webhook-management.md` — düzeltilen hatalar bölümü eklendi.
- `docs/RUNBOOKS/sistem-akisi-kusbakisi.md` — dashboard export kartı notu eklendi.
- `docs/SECURITY/security-audit-2026-02-28.md` — katalog izin düzeltmesi ek bölümü.

---

### Frontend Bug Düzeltmeleri & Eksik Özellikler (1 Mart 2026 — 2. tur)

Kullanıcı akışı simülasyonu (login → batch → export → ayarlar → çıkış) ile tespit edilen 7 sorunun düzeltmesi.

#### Düzeltilen
- **Checkout & Settings balance bug'ı** — Backend `GET /api/credits/balance/` `CreditPackage[]` array dönüyor ama frontend `{ balance: number }` bekliyordu → bakiye her zaman `undefined`/`NaN` görünüyordu. Her iki sayfa da array parse edip toplam bakiye hesaplayacak şekilde düzeltildi.
- **Settings organizations endpoint yolu** — `/organizations/` (404) → `/auth/organizations/` olarak düzeltildi (`accounts` app'in URL'leri `api/auth/` prefix'i altında).
- **Landing sayfa "Nasıl Çalışır?" butonu** — `onClick` yoktu → `#nasil-calisir` anchor + `scroll-mt-8` ile smooth scroll eklendi.
- **Landing sayfa "Hesap Oluştur" metni** — Kayıt sayfası mevcut değil (Google OAuth auto-register yapıyor) → "Giriş Yap" olarak düzeltildi.

#### Eklenen
- **Batch detay: 4. pipeline aşaması (Email Zenginleştirme)** — Pipeline özeti 3 aşama gösteriyordu, Stage 4 (emails_enriched, `Mail` icon, violet tema) eklendi.
- **Batch detay: Export oluşturma butonu** — Batch READY/PARTIAL olup dosyalar henüz oluşmadığında "Export Oluştur (CSV + XLSX)" butonu ile `POST /api/exports/` tetikleyebilme.
- **Dashboard: Toplam batch sayısı** — DRF pagination `count` alanı takip ediliyor, 5+ batch varsa "Gösterilen: 5 / N" bilgi mesajı gösteriliyor.

#### Belgeleme
- `ADR-0006` frontend Stage 4 yansıması eklendi.
- `sistem-akisi-kusbakisi.md` frontend düzeltmeleri güncellendi.
- `roadmap-kalite-maliyet.md` tamamlanan maddeler işaretlendi.
- `CHANGELOG.md` ikinci tur notları eklendi.

---

### UX / Frontend İyileştirmeleri (1 Mart 2026)

#### Eklenen
- **Token Auto-Refresh** — `api-client.ts`'de 401 alındığında arka planda `tryRefreshToken()` çağrılıyor, mutex ile tekil refresh sağlanıyor. Kullanıcı 15dk sonra oturumu kaybetmiyor.
- **Login Redirect Parametresi** — Middleware `?redirect=pathname` set ediyor, login sayfası artık bu parametreyi okuyup başarılı giriş sonrası hedef sayfaya yönlendiriyor.
- **ErrorBoundary Bileşeni** — React hata sınırı; yakalanmayan hatalar beyaz ekran yerine "Bir şeyler ters gitti" + "Tekrar Dene" gösteriyor.
- **ToastProvider Bileşeni** — Global bildirim sistemi; `useToast()` hook'u ile 4 variant (default/success/error/warning), 4sn auto-dismiss.
- **Dashboard Ödeme Başarı Bannerı** — `?success=payment` query parametresi ile checkout'tan dönen kullanıcıya yeşil tebrik mesajı gösteriliyor.
- **Dashboard Auto-Refresh** — İşlenen batch'ler varken 5sn aralıkla otomatik veri yenileme, tüm batch'ler terminal durumda olunca polling durur.
- **Custom 404 Sayfası** — `not-found.tsx` ile gradient arka planlı, Dashboard ve Ana Sayfa bağlantıları olan 404 sayfası.
- **Settings / Ayarlar Sayfası** — Hesap bilgileri (kullanıcı, e-posta, organizasyon, bakiye), şifre değiştirme formu. Sidebar + kullanıcı popup menüsüne "Ayarlar" linki eklendi.
- **Export Güvenli İndirme** — `GET /api/exports/{id}/download/` endpoint'i: auth-gated `FileResponse` ile dosya stream. Public URL gerektirmez.
- **Export URL Yenileme** — `POST /api/exports/{id}/regenerate/` endpoint'i: süresi dolmuş export'ları yeniden kuyruğa alır.
- **Exports Sayfası Pending/Failed Kartları** — İşlenen export'lar mavi animasyonlu kart, başarısız olanlar kırmızı kart + "Tekrar Dene" butonu. 8sn auto-refresh polling.
- **Exports URL Yenile Butonu** — Tamamlanmış fakat süresi dolmuş dosyalar için "URL Yenile" butonu.
- **Checkout Kredi Bakiyesi** — Satın alma sayfasında mevcut kredi bakiyesi gösteriliyor (`/credits/balance/` endpoint'i).
- **Batch List Serializer** — `BatchListSerializer` ile hafif liste endpoint'i; N+1 sorgu problemi çözüldü.

#### Değiştirilen
- **Refresh Cookie Path** — `/api/auth/refresh/` → `/api/auth/` (logout endpoint'ine de refresh cookie gönderilsin).
- **Google Login Button** — Genişlik `400` → `'auto'` (mobil responsive).
- **Batch Detail Loading** — `setLoading(false)` artık her başarılı fetch'te çağrılıyor (sadece terminal durumda değil).
- **Batch New Org Uyarısı** — Organizasyonu olmayan kullanıcıya açıklama metni + Dashboard'a git butonu eklendi.
- **Iyzico Script Yükleme** — Race condition düzeltildi: `onload` callback ile `iyzicoReady` state takibi, script yüklenmeden paket seçilemez.
- **ENRICHING_EMAILS Status** — Dashboard status filtre ve metin fonksiyonuna `ENRICHING_EMAILS` durumu eklendi.
- **Exports İndirme** — Public signed URL yerine güvenli `download` action endpoint'i kullanılıyor.

#### Eklenen
- **JWT HttpOnly Cookie Authentication** — Token'lar artık `HttpOnly` + `Secure` + `SameSite=Lax` cookie'lerle yönetiliyor ([cookie_auth.py](services/backend/apps/accounts/cookie_auth.py))
  - `CookieJWTAuthentication`: Cookie'den token okur, `Authorization` header fallback destekler
  - `set_jwt_cookies()` / `clear_jwt_cookies()`: Tüm auth endpoint'lerde çağrılır
  - Refresh cookie path `/api/auth/refresh/` ile kısıtlandı
- **Next.js Standalone Output** — `output: 'standalone'` ile Docker image boyutu önemli ölçüde azaltıldı
- **REDIS_PASSWORD** placeholder `.env.production` ve `.env.example`'a eklendi
- `CHANGELOG.md` oluşturuldu

#### Değiştirilen
- `DEFAULT_AUTHENTICATION_CLASSES` → `CookieJWTAuthentication` (önceki: `JWTAuthentication`)
- Frontend `auth.ts`: localStorage token yönetimi kaldırıldı → sadece optimistik `anka_authenticated` flag
- Frontend `api-client.ts`: `Authorization` header kaldırıldı → `credentials: 'include'`
- `frontend.Dockerfile`: Standalone modeline uyarlandı; `npm install` → `npm ci --ignore-scripts`
- `create_test_user.py`: Parola stdout yerine stderr'e yazılır
- LogoutView / RefreshTokenView: Cookie'den refresh token okuma desteği eklendi

#### Düzeltilen
- `create_test_user.py` indentation hatası düzeltildi (satır 56-58)
- **GCP Google Maps API Key Rotasyonu** — Eski key (`AIzaSyAZxawz0ab...`) GCP Console'dan rotate edildi ve silindi. Yeni key tüm env dosyalarına uygulandı (`.env`, `.env.production`, `.env.local.docker`, `.env.local.native`, `.env.example`, `.env.test.example`)

#### Belgeleme
- `security-audit-2026-02-28.md` v1.2'ye güncellendi (3/3 kritik, 7/7 yüksek, 8/8 orta düzeltildi)
- `ADR-0007` üçüncü tur kararları eklendi (HttpOnly cookie, standalone output, stdout güvenliği)
- `RUNBOOKS/README.md` auth modeli notları güncellendi
- `CONTRIBUTING.md` güvenlik bölümüne cookie auth notu eklendi
- `hardening-checklist.md`'ye 4 yeni kontrol maddesi eklendi

---

### Güvenlik (İkinci Düzeltme Turu — 28 Şubat 2026)

#### Eklenen
- `apps/common/pii.py` — `mask_email()`, `mask_username()`, `hash_pii()` PII maskeleme modülü
- `deploy.sh` preflight: SECRET_KEY uzunluk/içerik, CSRF, Redis, Maps key kontrolleri
- `.gitignore`: `.env`, `.env.production`, `*.pem`, `*.key`, `*.crt` pattern'ları
- `ADR-0007` güvenlik kararları belgesi
- `docs/SECURITY/` dizini: 8 güvenlik belgesi

#### Değiştirilen
- 7 log satırında PII maskelendi (`accounts/views.py`)
- `deploy.sh`: Admin parolası default kaldırıldı → `secrets.token_urlsafe(20)`
- `webhooks.py`: Secret boşken `return True` → `return False` + warning
- `dev.py`: `ALLOWED_HOSTS = ['*']` → `['localhost', '127.0.0.1', '0.0.0.0', '[::1]']`

---

### Güvenlik (İlk Düzeltme Turu — 28 Şubat 2026)

#### Eklenen
- DRF Rate Limiting: anon 30/dk, user 120/dk, auth 10/dk, sensitive 5/dk
- `token_blacklist` INSTALLED_APPS'e eklendi
- LogoutView → `RefreshToken.blacklist()` çağrısı
- CSRF cookie güvenlik flag'leri (prod.py)
- Redis `--requirepass` (docker-compose.prod.yml)
- Tüm dev compose portları `127.0.0.1`'e bind

#### Düzeltilen
- Hardcoded Google Maps API key ve OAuth Client ID kaldırıldı
- MinIO default credentials kaldırıldı
- `ALLOWED_HOSTS = ['*']` → `[]` (base.py)
