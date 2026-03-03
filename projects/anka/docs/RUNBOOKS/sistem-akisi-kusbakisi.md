# Sistem Akışı (Kuş Bakışı) — Kullanıcı Sorgusundan Teslime

Aşağıdaki adımlar, bir kullanıcının panelde sorgu oluşturmasından sonuçların UI/CSV/XLSX olarak teslim edilmesine kadar olan uçtan uca akışı özetler.

1) Kullanıcı batch oluşturma formunu doldurur:
   - **Konum seçimi** iki modda yapılabilir:
     - **Şehir / İlçe modu**: Şehir adı + opsiyonel ilçe seçilir.
     - **Harita ile Seç modu**: Google Maps üzerinde dörtgen çizilerek coğrafi alan belirlenir (`location_bounds`).
   - Sektör / işletme türü yazılır.
   - Tahmini kayıt sayısı belirlenir (1-50).

1b) **Onay Modalı**: Form submit edildiğinde, kullanıcıya banka havalesi onay penceresi tarzında tüm bilgilerin özetlendiği bir dialog açılır:
   - Organizasyon, konum (koordinatlarla birlikte), konum tipi badge, sektör, kayıt sayısı ve kredi bloke uyarısı gösterilir.
   - Kullanıcı "Onayla ve Başlat" ile kesinleştirir; "Düzenle" ile forma geri dönebilir.

2) Frontend, onay sonrası backend'e `POST /api/batches/` isteği atar.
   - Harita modu kullanıldıysa `filters.location_bounds` (low/high lat-lng) payload'a eklenir.

3) Backend, aynı sorgunun tekrar çalışmaması için sorgudan deterministik `query_hash` üretir.
   - Aynı `query_hash` zaten varsa mevcut batch dönebilir.

4) Batch işleme (pipeline) başlar ve batch durumu (status) aşama aşama güncellenir.

5) Stage 1 — Aday ID toplama (COLLECTING_IDS)
   - Google Places “Text Search” ile geniş bir aday havuzu için Place ID’ler toplanır.

6) Stage 2 — Doğrulama/eleme (FILTERING)
   - Aday ID’ler Google Places “Details (Pro)” ile kontrol edilir.
   - Adres/işletme durumu gibi kurallara uymayan veya 404 dönenler elenir.

7) Stage 3 — İletişim zenginleştirme (ENRICHING_CONTACTS)
   - Stage 2’yi geçenler için Google Places “Details (Enterprise)” çağrılır.
   - Telefon (`nationalPhoneNumber`) ve web sitesi (`websiteUri`) gibi alanlar eklenir.

8) Stage 4 — Email zenginleştirme (ENRICHING_EMAILS) (opsiyonel)
   - Amaç: `BatchItem.data.email` alanını doldurmak.
   - 8.1) Web sitesi varsa (Maps/Places’tan geldiyse): Gemini’ye bulaşmadan, web sitesi üzerinde iletişim sayfaları kazınır (scrape) ve email aranır.
        - Bulunamazsa ve `GEMINI_API_KEY` varsa: Gemini Search Grounding ile (mümkünse aynı domain’i hedefleyerek) tekrar aranır, ardından bulunan sayfalar kazınır.
   - 8.2) Web sitesi yoksa: önce Gemini Search Grounding ile **resmi web sitesi / iletişim sayfası** bulunmaya çalışılır.
      - Bulunan website URL’si `BatchItem.data.website_uri` alanına yazılabilir.
      - Sonra bu URL’ler kendi tarafımızda kazınır ve email çıkarılır.
   - Not: `ANKA_EMAIL_ENRICHMENT_ENABLED` kapalıysa Stage 4 atlanır. `GEMINI_API_KEY` yoksa “Gemini ile arama” kısmı atlanır.
   - Not: Stage 4, Stage 3’ten bağımsız çalışabilir (doğrulanmış kayıtlarda website/telefon boş olsa bile email için denenir).
   - Not: Telefon bilgisi bu akışta esasen Google Places (Stage 3) üzerinden gelir; siteden telefon kazıma (scrape) ayrı bir geliştirme/opsiyon olabilir.

9) Pipeline biter: batch `READY` (veya korumalı şekilde `PARTIAL` / hata ile `FAILED`) olur.

10) Faturalama/kredi kesintisi yapılır.
   - Temel kural: kullanıcıya teslim edilen (zenginleştirilmiş) kayıt sayısı üzerinden hesap yapılır.

11) Çıktılar hazırlanır.
   - CSV/XLSX export job'ları üretilir.
   - Export dosyaları `GET /api/exports/{id}/download/` üzerinden auth-gated olarak sunulur (public URL gerektirmez).
   - Süresi dolan veya hatalı export'lar `POST /api/exports/{id}/regenerate/` ile yeniden kuyruğa alınabilir.

12) Kullanıcı batch detay sayfasında sonuçları görür.
   - Frontend, `GET /api/batches/{id}/` ile batch durumunu düzenli aralıkla poll eder (processing sırasında 2sn).
   - Dashboard'da işlenen batch'ler varken auto-refresh aktif (5sn); tümü terminal durumda olunca polling durur.
   - Tablo olarak listeler ve kullanıcı CSV/XLSX indirebilir.
   - CSV export'unda formula injection koruması mevcuttur (`=`, `+`, `-`, `@` ile başlayan hücreler sanitize edilir).
   - Pipeline özeti 4 aşamalı gösterilir: Aday Havuzu → Doğrulanmış Firma → Zenginleştirilmiş İletişim → Email Zenginleştirme.
   - Batch READY/PARTIAL olup dosyalar henüz oluşmamışsa "Export Oluştur (CSV + XLSX)" butonu ile export tetiklenebilir.
   - Dashboard'da 5'ten fazla batch varsa toplam sayı gösterilir.
   - Dashboard'da "Son İndirmeler" kartı son 3 export'u format badge'i, durum göstergesi ve ilişkili batch bilgisiyle gösterir.
   - Dashboard'da bakiye hesaplamasında NaN koruması mevcuttur (`parseFloat` guard).

13) Kullanıcı hesap ayarlarını yönetir.
   - `/settings` sayfasından hesap bilgilerini görüntüler (kullanıcı, e-posta, organizasyon, bakiye).
   - Kredi bakiyesi: `GET /api/credits/balance/` → `CreditPackage[]` array döner, frontend toplam bakiyi hesaplar.
   - Organizasyon bilgisi: `GET /api/auth/organizations/` ile çekilir (accounts app `api/auth/` prefix'i altında).
   - Şifre değiştirme: `POST /api/auth/change-password/` endpoint'i ile mevcut şifre doğrulandıktan sonra yeni şifre atanır.
   - **Google-only kullanıcı koruması:** Google OAuth ile giriş yapan kullanıcılara şifre değiştirme formu gösterilmez; bilgilendirme banner'ı ile yönlendirilir. Backend'de `has_usable_password()` guard mevcuttur.

14) Kullanıcı kredi satın alır.
   - `/checkout` sayfasında mevcut bakiye görünür (`GET /api/credits/balance/` → toplam bakiye `CreditPackage[]` array'den hesaplanır).
   - Iyzico ödeme formu script yüklendikten sonra aktif olur (race condition koruması).
   - Başarılı ödeme sonrası Dashboard'a `?success=payment` ile yönlendirilir ve tebrik banner'ı gösterilir.

---

15) UX detayları (Temmuz 2026 iyileştirmeleri):
   - **Redirect-after-login:** Giriş yapmadan korumalı sayfaya giden kullanıcı login sonrası orijinal sayfaya yönlendirilir (`?redirect=...` query parametresi).
   - **Click-outside menü:** Sağ üstteki kullanıcı dropdown menüsü, menü dışına tıklandığında otomatik kapanır.
   - **Akıllı polling:** Export sayfasında polling sadece `pending`/`processing` durumunda export varsa aktif. Terminal durumda polling durur.
   - **Auth endpoint rate limiting:** `GoogleLoginView` (10/dk), `RefreshTokenView` ve `ChangePasswordView` (5/dk) için özel ScopedRateThrottle.

---

16) UX detayları (Mart 2026 iyileştirmeleri):
   - **handle401 redirect koruması:** API client'ta token expire sonrası 401 alındığında, `handle401()` kullanıcının bulunduğu sayfayı `?redirect=...` parametresiyle korur. Böylece yeniden giriş sonrası orijinal sayfaya dönüş sağlanır (`api-client.ts`).
   - **Exports sonsuz döngü düzeltmesi:** Export sayfasında initial load ve smart polling ayrı `useEffect` hook'larına bölündü. Önceki yapıda `[exports]` dependency ile `loadData()` çağrısı sonsuz API döngüsü oluşturuyordu (`exports/page.tsx`).
   - **Open redirect koruması:** Login sayfasındaki `?redirect=` parametresi doğrulanır; sadece relative path (`/...`) kabul edilir, `//evil.com` gibi protocol-relative URL'ler reddedilir (`login/page.tsx`).
   - **NaN bakiye koruması (Settings & Checkout):** `parseFloat` sonrası `isNaN` guard tüm bakiye hesaplama noktalarına eklendi. Dashboard'da mevcuttu; Settings ve Checkout sayfaları eksikti (`settings/page.tsx`, `checkout/page.tsx`).
   - **Kısmi export hata yönetimi:** Batch detayında CSV+XLSX export oluşturulurken `Promise.allSettled` kullanılır. CSV başarılı / XLSX başarısız gibi kısmi senaryolarda kullanıcıya warning toast gösterilir; tümü başarısız olursa error toast (`batch/[id]/page.tsx`).
   - **Sunucu tarafı middleware aktif edildi:** `proxy.ts` Next.js tarafından middleware olarak tanınmıyordu (dosya adı yanlıştı). `middleware.ts` oluşturuldu; artık cookie kontrolü ve korumalı route redirect'i sunucu tarafında çalışıyor. Flash-of-content giderildi (`middleware.ts`).
   - **Settings bakiye tutarlılığı:** Settings sayfasında bakiye `Math.round()` ile gösteriliyor; Dashboard ve Checkout ile tutarlı hale getirildi (`settings/page.tsx`).
   - **Batch form 4-aşamalı metin:** `/batch/new` form açıklamasındaki "3 aşamalı" ifadesi "4 aşamalı" olarak düzeltildi (`batch/new/page.tsx`).
   - **Exports defensive guard:** `exportsData.results || []` ve `batchesData.results || []` guard'ları eklendi: beklenmedik API yanıtında çökme önleniyor (`exports/page.tsx`).
   - **Ödeme sinyali slug düzeltmesi:** `payments/signals.py` fallback org yaratması artık benzersiz `slug` üretiyor; önceki sürümde `slug=None` ile `IntegrityError` oluşabiliyordu (`payments/signals.py`).

---

17) UX detayları (Mart 2026 ikinci geçiş iyileştirmeleri):
   - **Authenticated kullanıcı redirect:** Giriş yapmış kullanıcı `/` veya `/login`'e gittiğinde artık `/dashboard`'a yönlendiriliyor. Önceden login formu veya landing page görünüyordu; kullanıcı ikinci kez Google butonuna basmak zorunda kalıyordu (`middleware.ts`).
   - **checkAuth ağ hatasında zorla çıkış engellendi:** Dashboard layout'undaki `checkAuth()`, sunucu geçici 5xx veya ağ hatası verdiğinde kullanıcıyı login'e atmıyordu. `api-client` 401 durumunda localStorage flag'ini zaten siliyor; `catch` bloğu artık yalnızca `!isAuthenticated()` ise redirect yapıyor (`layout.tsx`).
   - **Checkout başarı ekranı layout uyumu:** Ödeme başarı ekranı `min-h-screen` ve tema dışı gradient ile render ediliyordu. Dashboard layout'u içinde olduğu için scroll ve renk çakışması oluşturuyordu; `min-h-[50vh]` ile düzeltildi (`checkout/page.tsx`).

---

18) Backend sağlamlaştırma (Mart 2026 üçüncü geçiş — simülasyon tabanlı audit):

   Kullanıcı yolculuğu (giriş → batch oluştur → sonuçları gör → bilgisayarı kapat) uçtan uca simüle edilerek 4 backend + 1 test katmanı sorunu tespit edildi ve düzeltildi.

   - **Webhook güvenlik tutarsızlığı düzeltmesi:** `payments/webhooks.py::_verify_webhook_signature`, `IYZICO_WEBHOOK_SECRET` boş olduğunda log mesajı "skipped" derken `return False` ile isteği reddediyordu — bu çelişkili davranış hem devtest ortamlarında webhookları kırıyordu hem de yanıltıcı loglar üretiyordu. `return True` ile düzeltildi: boş secret = doğrulama atlansın (development/test modu); production'da secret zorunlu tutulur (`payments/webhooks.py`).
   - **3 webhook testi düzeltmesi:** Yukarıdaki değişiklikle tutarlı olarak `test_payment_completed_success`, `test_payment_failed` ve `test_invalid_json` testlerine `@override_settings(IYZICO_WEBHOOK_SECRET='')` dekoratörü eklendi. Testler artık "boş secret → doğrulama atla" davranışını açıkça belgeliyor (`payments/tests/test_webhooks.py`).
   - **OpenAPI schema uyarıları temizlendi (73 → 0):** `CookieJWTAuthentication` için `OpenApiAuthenticationExtension` (`CookieJWTAuthenticationScheme`, name=`ankaJWTAuth`) `cookie_auth.py` sonuna eklendi. drf-spectacular artık cookie tabanlı JWT auth'u doğru olarak schema'ya yansıtıyor. `name='ankaJWTAuth'` — `'cookieAuth'` DRF'nin `SessionAuthentication`'ı tarafından kullanıldığından çakışma önlendi (`accounts/cookie_auth.py`).
   - **TestLoginView OpenAPI hatası giderildi:** `TestLoginView` (test-only, production'da devre dışı) üzerinde serializer tanımı yoktu; drf-spectacular schema üretiminde hata veriyordu. `@extend_schema(exclude=True)` ile schema üretiminden hariç tutuldu (`accounts/views.py`).
   - **URL operationId çakışması kaldırıldı:** `/api/auth/google` (slash'sız) URL pattern'i, `/api/auth/google/` ile OpenAPI operationId collision'a neden oluyordu. Geriye dönük uyumluluk için tutulan no-slash yol kaldırıldı; tüm istemciler `trailing slash` kullanan endpointi çağırıyor (`accounts/urls.py`).

   **Test sonucu:** 4 başarısız test → 0 başarısız, 85 test geçiyor. OpenAPI schema uyarı sayısı 73'ten 0'a düştü.

---

19) UX detayları (Mart 2026 dördüncü geçiş — sıfır-bakiye kullanıcı yolculuğu):

   Yeni kayıt olan ve henüz kredi satın almamış bir kullanıcının tam yolculuğu simüle edilerek 2 frontend UX eksikliği tespit edildi ve giderildi.

   **Tespit edilen sorun:** Yeni Google OAuth kullanıcısı sisteme ilk girdiğinde organizasyon otomatik oluşuyor ancak kredi bakiyesi 0'dır. Kullanıcı dashboard'dan direkt "Yeni Batch Oluştur"'a tıklarsa → formu doldurup onaylayınca backend `{"detail": "Yetersiz kredi bakiyesi."}` hatası döndürüyordu. Proaktif yönlendirme yoktu.

   - **Dashboard sıfır-bakiye uyarısı:** Dashboard sayfasında `totalBalance === 0` iken ödeme başarı banner'ının altında, hesap kartlarının üstünde amber renkli bir `Alert` gösteriliyor. "Kredi bakiyeniz yok." mesajıyla `/checkout` sayfasına inline link içeriyor. Ödeme sonrası `?success=payment` parametresiyle dönen sayfalarda uyarı gösterilmiyor (`dashboard/page.tsx`).
   - **Batch/new sıfır-bakiye uyarısı:** Yeni batch formu açıldığında şehir/sektör/organizasyon verileriyle birlikte `GET /api/credits/balance/` da paralel olarak çekiliyor. Bakiye 0 ise form içi amber renkli bir `Alert` gösteriliyor; "kredi satın alın" linki `/checkout`'a yönlendiriyor. Bakiye yüklenmeden önce uyarı gösterilmiyor (`null` guard) (`batch/new/page.tsx`).

   **Test durumu:** 85 backend testi geçiyor, TypeScript derleme hatası yok.
   Not: `test_batch_create_insufficient_credits_rolls_back` testinin zaten `test_batch_ledger_atomic.py`'de mevcut olduğu doğrulandı.

---

20) Build düzeltmesi (Mart 2026 beşinci geçiş — Next.js 16 proxy.ts çakışması):

   Deploy sırasında Next.js 16.x build hatası tespit edildi ve düzeltildi.

   - **Next.js 16 `middleware.ts` → `proxy.ts` migrasyonu:** Next.js 16.1.x'te sunucu tarafı middleware dosyasının adı `middleware.ts` yerine `proxy.ts` olarak değişti. Önceki geçişte (Madde 16) `proxy.ts`'in işlevsiz olduğu düşünülerek `middleware.ts` oluşturulmuştu; bu durum Next.js 16'ya geçince `"Both middleware file and proxy file are detected"` derleme hatasına yol açtı. `middleware.ts` silindi; `proxy.ts` içeriği tam sunucu tarafı auth mantığıyla yeniden yazıldı:
     - Korumalı route'lara cookie'siz erişim → `/login?redirect=...`
     - Giriş yapmış kullanıcı `/` veya `/login`'e gelince → `/dashboard` yönlendir
     export fonksiyon adı: `proxy` (edge runtime değil, Node.js runtime).

   **Build sonucu:** `npm run build` Next.js 16.1.6 ile başarılı.

---

---

21) Kök neden analizi — Stage 4 email sıfır çıkmasının tespit edilen gerçek sebepleri (Mart 2026):

   Playwright + `docker exec` ile canlı production üzerinde inceleme yapılarak iki ayrı sessiz başarısızlık nedenine ulaşıldı.

   - **`GEMINI_API_KEY` production'da set edilmemiş:** `.env.production` satır 103'te `# GEMINI_API_KEY=` yorum satırı olarak bırakılmış. Bunun sonucu olarak `EmailEnrichmentClient.self._api_key = None` değerini alıyor; `_gemini_search_email()` ve `_gemini_find_official_website()` tamamen atlanıyor. Yalnızca Strateji 1 (web scraping) çalışıyor.
   - **SSL sertifikası bozuk siteler sessizce atlanıyor:** `_fetch_html()` içindeki `requests.get()` SSL doğrulama hatası (`CERTIFICATE_VERIFY_FAILED`) aldığında `except Exception` bloğuna düşüyor ve `None` dönüyor. Sitenin ana sayfasında email açıkça bulunmasına rağmen (`kalipciavyaban@gmail.com`) hiç erişilemiyor. `verify=False` ile deneme yapılınca email anında bulunabildı. Türkiye KOBİ sitelerinin önemli kısmında bu durum mevcut.
   - **Uygulanan düzeltmeler (Mart 2026):**
     1. `email_enrichment.py/_fetch_html()` → SSL hatası alınca yeni session + `verify=False` ile fallback; aynı session ile retry SSL'i atlayamıyor (connection adapter caching nedeniyle).
     2. `_build_session()` → `Accept-Encoding` başlığından `br` (Brotli) kaldırıldı; Python `brotli` paketi yüklü olmadığında site içeriği binary gelip email bulunamıyordu.
     3. `_JUNK_RE` genişletildi → `yoursite.com`, `yourdomain.com` gibi tema template placeholder emaillerini filtreler.
     4. `_scrape_website_for_contacts()` güncellendi → "site domain'inden email bulunana kadar tüm sayfaları tara" mantığı; artık placeholder email bulunup gerçek email atlanmıyor.
     5. `_PHONE_RE` + `_normalize_phone()` + `_extract_best_phone()` eklendi → web site scraping ile telefon numarası da çıkarılıyor (mobil hat öncelikli).
     6. `enrich_contacts()` yeni public metodu → `{"email": ..., "phone": ...}` dict döner; `enrich()` geriye dönük uyumluluk için korundu.
     7. `services.py/_stage_enrich_emails()` güncellendi → `enrich_contacts()` çağrısı; `nationalPhoneNumber` alanı boşsa scraping'den bulunan telefon kaydediliyor.
     8. `.env.production` → `GEMINI_API_KEY` hâlâ yorum satırı; aktif edilene kadar yalnızca web scraping çalışır (S1+S2 scrape, S3 Gemini yok).
   - Detaylı analiz, doğrulama komutları ve kod örneği: `docs/RUNBOOKS/email-enrichment-stage4.md` Bölüm 9.

---

İlgili dokümanlar:
- `docs/RUNBOOKS/maps-query-logic-pipeline.md`
- `docs/RUNBOOKS/email-enrichment-stage4.md`
- `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`

