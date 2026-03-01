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

---

İlgili dokümanlar:
- `docs/RUNBOOKS/maps-query-logic-pipeline.md`
- `docs/RUNBOOKS/email-enrichment-stage4.md`
- `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`
- `docs/RUNBOOKS/code-audit-and-fixes-2026-06.md`
- `docs/RUNBOOKS/ux-simulation-audit-2026-07.md`
- `docs/RUNBOOKS/ux-simulation-audit-2026-03.md`
