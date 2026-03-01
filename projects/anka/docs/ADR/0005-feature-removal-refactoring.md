# Architecture Decision Record: Feature Removal - Refactoring Debt Cleanup

**ADR-0005**  
Date: 2025-01-26  
Status: DECIDED  
Author: Team

## Context

The Anka platform carried planned but unimplemented features that increased cognitive load and created technical debt:

1. **WebSocket Real-time Updates** - Intended for async job progress but never fully implemented
2. **Admin Webhook UI** - UI layer for webhook management (backend exists for Iyzico)
3. **Org Switch UI** - Organization selector for multi-org support
4. **Snapshot Tests** - Frontend regression testing approach
5. **Over-engineered Role-based UI Logic** - Frontend permission checking that duplicated backend validation

### Analysis

**Frontend Status**: All five features were either never implemented or already removed:
- No WebSocket implementations found in frontend source
- No webhook admin UI components in frontend
- No org switch/selector components in frontend  
- No Jest snapshot tests in project source
- No permission helper functions (canEdit, canView, etc.) in frontend

**Backend Status**:
- **Webhooks**: Fully implemented (Iyzico payment notifications in `/apps/payments/webhooks.py`)
- **Multi-org**: Fully implemented (`Organization` and `OrganizationMember` models)
- **RBAC**: Partially implemented (role-based permissions on `OrganizationMember`)

## Decision

### ✅ Frontend (No Changes Needed)

All five features were never implemented in frontend source code. No removal is required.

### 🔄 Backend - Clarification Needed

The following remain implemented and functional:

1. **Payment Webhooks** - KEEP
   - Iyzico webhook handler is actively used for payment processing
   - Should NOT be removed

2. **Multi-Organization Support** - KEEP (with notes)
   - `Organization` model exists but may not be actively used
   - `OrganizationMember` with role-based access control exists
   - Frontend currently doesn't utilize multi-org features
   - **Decision**: Keep implementation; document for future use or explicit removal in separate ADR

3. **Role-Based Access Control** - KEEP (with clarification)
   - Backend enforces permissions on `OrganizationMember` model
   - Frontend will NOT replicate these checks
   - All permission checks must happen at API boundary (403 responses)
   - **Decision**: Keep backend RBAC; document that frontend must handle 403 errors

## Implementation

### Frontend Changes
**None** - All planned removals already absent from source code.

### Backend Changes
**None** - Existing implementations are functional and necessary.

### Documentation Changes
1. **README.md**: Add section clarifying feature status
2. **RUNBOOK - Payments**: Document webhook retry procedures (manual only, no UI)
3. **Architecture Guide**: Clarify org/RBAC design and future evolution

## Rationale

1. **Avoid Premature Optimization**: Backend implementations are stable and necessary
2. **Reduce Cognitive Load**: Frontend complexity is already minimal
3. **Future-Ready**: Keep multi-org and RBAC infrastructure for planned scaling
4. **API-First Design**: Frontend respects backend authorization (403 on denial)

## Consequences

### Positive
- Reduced frontend complexity already achieved
- Backend ready for multi-org scaling without refactoring
- Clear API boundary enforcement (backend → frontend)

### Negative  
- Backend carries features not currently exposed in UI
- May seem like "over-engineering" for single-org usage

## Monitoring

- [ ] Verify webhook processing in production
- [ ] Confirm frontend handles 403 responses gracefully
- [ ] Document future multi-org enablement path

---

## Addendum (2026-01-26): MVP Frontend Minimum Ekranlar (Zorunlu)

Bu bölüm “olsa güzel olur” değildir. Ürünün para kazanması ve uçtan uca çalışması için **zorunlu minimum** ekran setidir.

### MVP Kapsam Kuralı (Non-Negotiable)

- **MVP’de kullanıcı = tek organizasyon**. Frontend, organizasyon seçimi/switching sunmaz.
- Frontend, backend’deki RBAC/multi-org varlığını **UI’da ifşa etmez**; yalnızca `403/401` durumlarını kullanıcıya anlaşılır biçimde yansıtır.
- “Teknik ayrıntılar” (provider, task id, job id, hash/retry detayları, webhook iç durumları) UI’da gösterilmez.

### 1) Giriş / Kimlik Doğrulama Ekranı

- **Route**: `/login`
- **Kullanıcı neden buraya gelir?** Sistemi kullanmak için token almak ve organizasyon bağlamına girmek.
- **Backend’te kullandığı yetenekler**: JWT auth; `POST /auth/google`; `GET /me` (user resolve).
- **Frontend sorumluluğu (mutlaka)**:
   - “Google ile devam et”
   - Hata mesajı (401/403)
   - Başarılı girişte tek org varsayımı ile yönlendirme
- **Göstermemesi gerekenler**:
   - Organization listesi
   - Rol bilgisi / yetki matrisi

### 2) Dashboard / Genel Durum Ekranı

- **Route**: `/dashboard`
- **Kullanıcı neden buraya gelir?** Sistem çalışıyor mu, kredim var mı, son işlemlerim neler.
- **Backend’te kullandığı yetenekler**: Ledger/credit balance; recent batches; recent exports; dispute summary.
- **Mutlaka göstermesi gerekenler**:
   - Mevcut kredi bakiyesi
   - Son 3 batch
   - Son 3 export
   - “Yeni Batch” butonu
- **Göstermemesi gerekenler**:
   - Ham ledger satırları
   - Provider bazlı maliyetler
   - Teknik durumlar (job id, task id)

### 3) Batch Oluşturma + İzleme Ekranı

- **Route**: `/batch/new`
- **Kullanıcı neden buraya gelir?** Kriterlere göre veri istemek, kaç kayıt/kredi gideceğini görmek, aynı batch’i tekrar indirebilmek.
- **Backend’te kullandığı yetenekler**: deterministic batch hashing; batch + batch items; credit pre-check; idempotent create.
- **Mutlaka içermesi gerekenler**:
   - Arama formu (il, sektör, kategori vb.)
   - **Konum seçim modu toggle**: "Şehir / İlçe" ↔ "Harita ile Seç"
   - Harita modu: Google Maps üzerinde dörtgen çizerek coğrafi alan belirleme (`MapAreaSelector` bileşeni)
   - Şehir modu: şehir + opsiyonel ilçe alanları
   - Tahmini kayıt sayısı
   - Tahmini kredi maliyeti
   - **Onay Modalı (Dialog)**: Submit öncesi banka havalesi tarzı özet penceresi — organizasyon, konum (koordinatlarla), konum tipi badge, sektör, kayıt sayısı, kredi bloke uyarısı
   - "Onayla ve Başlat" / "Düzenle" butonları
   - Batch durumu (created / processing / ready)
- **Göstermemesi gerekenler**:
   - Provider isimleri (Infobel, Outscraper vb.)
   - "Ham veri" vs "doğrulanmış veri" gibi teknik ayrımlar
   - Retry / hash detayları
- **Mobil uyumluluk**: Form alanları tek kolon, harita tam genişlik, onay modalı bottom-sheet benzeri

### 4) Export / İndirme Ekranı

- **Route**: `/exports`
- **Kullanıcı neden buraya gelir?** CSV/XLSX indirmek, daha önce aldığı veriyi tekrar indirmek.
- **Backend’te kullandığı yetenekler**: export job; Celery task; S3 signed URL; status polling.
- **Mutlaka içermesi gerekenler**:
   - Export listesi
   - Format seçimi (CSV / XLSX)
   - Durum (hazırlanıyor / hazır)
   - “İndir” butonu
- **Göstermemesi gerekenler**:
   - Signed URL
   - Dosya path’i
   - Expiration timestamp (detaylı)

### 5) Ödeme & Kredi Satın Alma Ekranı

- **Route**: `/checkout` (veya `/credits`)
- **Kullanıcı neden buraya gelir?** Kredi bitmiştir; daha fazla veri almak ister.
- **Backend’te kullandığı yetenekler**: payment intent; Stripe/Iyzico; webhook → ledger credit.
- **Mutlaka içermesi gerekenler**:
   - Mevcut kredi
   - Paket seçenekleri (net, sade)
   - Ödeme başlat
   - Başarılı / başarısız mesajı
- **Göstermemesi gerekenler**:
   - Webhook durumu
   - Provider farkları
   - Fatura altyapısı (MVP dışı)

## References

- Previous: `ADR-0001` (Architecture: API/Frontend Split)
- Previous: `ADR-0004` (Automatic Dispute Rules)
- Related: Backend RBAC model in `/apps/accounts/models.py`
- Related: Webhook handler in `/apps/payments/webhooks.py`

