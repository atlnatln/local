# Docs Overview (Copilot Quick Start)

Bu klasör, Anka sisteminin karar kayıtlarını (ADR), API sözleşmesini ve operasyon runbook’larını içerir.

## 1) Nereden Başlamalı?

- Mimari kararlar: `docs/ADR/`
- API sözleşmesi (kanonik): `docs/API/openapi.yaml`
- Operasyonel adımlar: `docs/RUNBOOKS/`
- **Güvenlik politikaları ve denetimler: `docs/SECURITY/`**

Yeni bir Copilot/ajan için önerilen okuma sırası:
1. `docs/ADR/0001-architecture-api-frontend-split.md`
2. `docs/ADR/0006-three-stage-verification-pipeline.md`
3. `docs/ADR/0002-credit-ledger-minimal.md`
4. `docs/ADR/0004-automatic-dispute-rules-v1.md`
5. `docs/RUNBOOKS/README.md`
6. `docs/SECURITY/README.md`

## 2) Kanonik Gerçekler (Hızlı)

- Docker dev: frontend `3100`, backend `8100`
- Native dev: frontend `3000`, backend `8000`
- Auth: JWT Bearer
- API docs endpoint: `/api/docs`
- Batch kritik statüler: `CREATED`, `COLLECTING_IDS`, `FILTERING`, `ENRICHING_CONTACTS`, `ENRICHING_EMAILS`, `READY`, `PARTIAL`, `FAILED`

### Frontend Önemli Özellikler (Güncel — Mart 2026)

- **Konum seçimi iki modlu**: "Şehir / İlçe" klasik modu veya "Harita ile Seç" (Google Maps üzerinde dörtgen çizme) modu.
- **Onay Modalı**: Batch oluşturma formu submit edildiğinde, kullanıcıya banka havalesi onayı tarzında tüm bilgilerin özetlendiği bir `Dialog` açılır; "Onayla ve Başlat" ile işlem kesinleşir.
- **Mobil Uyumluluk**: Dashboard layout, hamburger menü ile mobilde sidebar açılıp kapanır. Google login butonu dahil tüm bileşenler responsive.
- **Token Auto-Refresh**: 401 alındığında arka planda sessiz token yenileme; kullanıcı oturum kaybetmez.
- **ErrorBoundary**: Yakalanmayan React hataları beyaz ekran yerine kullanıcı dostu hata sayfası gösterir.
- **Toast Bildirimleri**: `useToast()` hook'u ile global bildirim sistemi (success/error/warning/default).
- **Dashboard Auto-Refresh**: İşlenen batch'ler varken 5 sn polling; tümü terminal durumda olunca durur.
- **Ayarlar Sayfası**: Hesap bilgileri görüntüleme + Google-only kullanıcılarda şifre formu gizlenir (`/settings`).
- **Export Güvenli İndirme**: Auth-gated `FileResponse` endpoint'i (`/api/exports/{id}/download/`). Süresi dolan URL'ler için "Yenile" butonu.
- **Checkout Bakiye Göstergesi**: Kredi satın alma sayfasında mevcut bakiye görünür.
- **Custom 404 Sayfası**: Gradient arka plan, Dashboard / Ana Sayfa bağlantıları.
- **CSV Formula Injection Koruması**: İstemci tarafı CSV export'unda `=`, `+`, `-`, `@` ile başlayan hücreler sanitize edilir.
- **Redirect-after-login**: Oturum süresi dolduğunda kullanıcı giriş sonrası istenen sayfaya geri döner. Token expire kaynaklı 401'lerde de `handle401()` redirect path'i korur.
- **Click-outside Menü Kapanma**: Kullanıcı menüsü dışına tıklanınca otomatik kapanır.
- **Akıllı Polling**: Export sayfasında sadece pending/processing export varken poll yapılır; tümü bitince durur. Initial load ve polling ayrı effect'lerde sonsuz döngü korumalıdır.
- **Open Redirect Koruması**: Login sayfasındaki `?redirect=...` parametresi sadece göreli path (`/` ile başlayan, `//` ile başlamayan) kabul eder; harici URL'ler dashboard'a yönlendirilir.
- **NaN Bakiye Koruması**: Dashboard, Settings ve Checkout sayfalarında `parseFloat` sonucu `isNaN` guard ile korunur; geçersiz değerlerde `0` gösterilir.
- **Kısmi Export Hata Yönetimi**: Batch detayında CSV + XLSX export oluşturulurken `Promise.allSettled` kullanılır; kısmi başarıda kullanıcı uyarı toast'u alır.
- **Gelecek Mobil App Uyumu**: Tüm iş mantığı backend API üzerinden; frontend, API-first prensibiyle çalışır. İleride React Native / Flutter ile aynı API kullanılabilir.

## 3) Çelişki Çözüm Kuralı

Doküman ile kod çelişirse öncelik sırası:
1. Çalışan kod ve scriptler
2. `docs/API/openapi.yaml`
3. ADR
4. Runbook

## 4) Güncelleme İlkesi

- Operasyonel değişiklikte ilgili runbook aynı PR’da güncellenir.
- Endpoint/şema değişikliğinde `docs/API/openapi.yaml` güncellenir.
- Karar değişikliği varsa yeni ADR eklenir veya mevcut ADR revizyon notu alır.

## 5) Mobil Uygulama Yol Haritası

- Tüm veri ve iş mantığı backend REST API'de yaşar (`/api/` namespace).
- Frontend sadece sunum katmanıdır; state yönetimi sunucu-önceliklidir (server-first).
- Gelecekte React Native veya Flutter ile mobil app yapılacaksa:
  - Aynı JWT auth akışı (`POST /api/auth/google/`) kullanılır.
  - Batch CRUD, export, checkout, ledger endpoint'leri değişmez.
  - Google Maps SDK (mobil) ile `location_bounds` aynı formatta gönderilebilir.
  - Push notification için backend'e FCM token endpoint'i eklenebilir.
