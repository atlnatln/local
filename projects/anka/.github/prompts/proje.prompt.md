# Anka Platform - Proje Spesifikasyonu ve Mimarisi

> **Versiyon:** 1.0  
> **Tarih:** 10 Ocak 2026  
> **Durum:** MVP-0 (İlk Sürüm)  
> **Sahip:** Proje Ekibi

---

## 📋 İçindekiler

1. [Proje Genel Bakış](#proje-genel-bakış)
2. [Tür Analizi](#tür-analizi)
3. [Mimari Tasarım](#mimari-tasarım)
4. [Teknoloji Stack](#teknoloji-stack)
5. [Çekirdek Domain Modülleri](#çekirdek-domain-modülleri)
6. [Dış Entegrasyonlar](#dış-entegrasyonlar)
7. [Karar Ağacı & Akışlar](#karar-ağacı--akışlar)
8. [Finansal Model](#finansal-model)
9. [Ölçeklendirilme Stratejisi](#ölçeklendirilme-stratejisi)

---

## 🎯 Proje Genel Bakış

### Vizyon
Deterministik batch işleme ile ön ödemeli kredi tabanlı B2B veri hizmet platformu.

### Temel Özellikler
- **Ön ödemeli kredi sistemi** (credit_purchase → credit_spent → credit_refund)
- **Otomatik itiraz motoru** (kural bazlı karar alma)
- **Deterministik batch üretimi** (tekrar üretilebilir, sorgulanabilir)
- **Finansal denetim** (tam audit trail)

---

## 📊 Tür Analizi

### Birincil Sınıflandırma
**3. Ticaret & Pazar Yeri → Abonelik Servisleri (SaaS)**

**Temel Özellikler:**
- "Kayıt/record" satışı (pay-per-use)
- Ön ödemeli kredi modeli
- Kullanıcı yönetim paneli
- İndirilebilir çıktı (CSV/XLSX export)

### İkincil Sınıflandırma
**6. Hizmet & İşlev Odaklı → Finansal Servis Siteleri**

**Temel Özellikler:**
- Kredi bakiyesi yönetimi
- Ledger (muhasebe izi)
- İade/iade işlemleri
- Otomatik itiraz sistemi
- Webhook ve audit mechanizması

### Nihai Tanım
**B2B Data Utility SaaS (pay-per-use model)**

Bu bir "lead marketplace" değil; deterministik batch ile üretilen "record" satış platformudur.

---

## 🏗️ Mimari Tasarım

### MVP-0 Mimarisi: Hybrid (Modüler Monolith)

```
┌─────────────────────────────────────────────┐
│         Frontend (Next.js)                    │
│  ├─ Dashboard                                │
│  ├─ Checkout (Ödeme)                         │
│  └─ Exports (İndirme)                        │
└─────────────────────────────────────────────┘
           ↓ (REST API + OpenAPI)
┌─────────────────────────────────────────────┐
│     Backend (Django) - Modüler Monolith      │
│                                              │
│  ├─ Accounts & Orgs                          │
│  ├─ Catalog (Sektor/Şehir)                   │
│  ├─ Batch & Quote (Deterministik)            │
│  ├─ Credits & Ledger (Finansal)              │
│  ├─ Disputes (Otomatik Motor)                │
│  ├─ Exports (Job'lar)                        │
│  └─ Audit & Compliance                       │
│                                              │
│  + Celery (Async Tasks)                      │
│  + Redis (Cache & Queue)                     │
└─────────────────────────────────────────────┘
           ↓ (PostgreSQL)
┌─────────────────────────────────────────────┐
│           Veri Tabanı (PostgreSQL)           │
└─────────────────────────────────────────────┘
```

### Tasarım Seçiminin Gerekçesi

| Karar | Neden |
|-------|-------|
| **Django Backend** | ACID transaksiyonlar (kredi düşümü + batch kilidi) |
| **Next.js Frontend** | Server-side session + httpOnly cookie güvenliği |
| **Modüler Monolith** | Başlangıçta deployment basitliği, gelişmiş mikro-servislere çevrilebilirlik |
| **PostgreSQL** | Güçlü veri tutarlılığı, ACID garantileri |

### Yüksek Trafik Evrimi (Scaling)

Yük arttıkça **kademeli microservice ayrışımı:**

1. **Export Service** (büyük dosya üretimi, queue yoğunluğu)
2. **Provider Orchestrator** (rate limit, maliyet, cache, retry/circuit breaker)
3. **Billing/Ledger Service** (kritik modül, audit & immutability)

**Prensip:** Başlangıçta monolith, ihtiyaç doğrultusunda ayrışır. Erken mikroservisleşme yapılmaz.

---

## 🛠️ Teknoloji Stack

### Backend Stack

| Katman | Teknoloji | Amaç |
|--------|-----------|------|
| **Framework** | Django 4.2+ | Web application framework |
| **API** | Django REST Framework + drf-spectacular | REST API + OpenAPI/Swagger |
| **Database** | PostgreSQL 14+ | Relational DB (ACID) |
| **Cache/Queue** | Redis | Caching & task queue |
| **Async** | Celery | Arka plan işleri |
| **File Storage** | S3/MinIO | Document & export storage |
| **Payment** | Stripe / Iyzico | Ödeme işlemleri |
| **Email** | Postmark / Sendgrid | Transactional email |

### Frontend Stack

| Katman | Teknoloji | Amaç |
|--------|-----------|------|
| **Framework** | Next.js 14+ (App Router) | Full-stack React framework |
| **State** | React Query / SWR | Veri fetching & caching |
| **Auth** | Custom server-side sessions | Secure session management |
| **UI Components** | Shadcn/ui veya TailwindCSS | Component library |
| **Forms** | React Hook Form | Form state management |

### Önerilen Django Paketleri

```
djangorestframework                    # REST API
drf-spectacular                        # OpenAPI/Swagger
django-filter                          # Filtering
django-redis                           # Redis integration
django-ratelimit / DRF throttling      # Rate limiting
django-auditlog                        # Audit trail
django-storages                        # S3/MinIO support
celery + django-celery-results         # Async tasks
celery-beat                            # Scheduled tasks (optional)
stripe / iyzipay                       # Payment integration
django-anymail                         # Email integration
```

---

## 🏛️ Çekirdek Domain Modülleri

### 1. Accounts & Orgs
```
User
  ├─ username, email, password
  ├─ organization_id (FK)
  └─ created_at, updated_at

Organization
  ├─ name, slug
  ├─ subscription_plan (free/pro/enterprise)
  └─ created_at, updated_at

Membership
  ├─ user_id, organization_id
  ├─ role (admin/manager/viewer)
  └─ created_at, updated_at
```

### 2. Catalog
```
City
  ├─ name, code
  └─ country

Sector
  ├─ name, code
  └─ parent_id (null = root)

Filter (Seçenekler)
  ├─ name, type (range/select/multi)
  └─ available_values
```

### 3. Quote & Batch (Deterministik)
```
Batch
  ├─ id (UUIDv7)
  ├─ organization_id
  ├─ query_params (JSON) → city, sector, filters
  ├─ query_hash (SHA256) ← TEKRARLANABILIR
  ├─ sort_rule_version (sabit sıralama)
  ├─ provider_snapshot_ref (kullanılan veri sürümü)
  ├─ item_count
  ├─ created_at
  └─ status (draft/locked/exported)

BatchItem
  ├─ batch_id
  ├─ position (sıra)
  ├─ firm_id
  └─ created_at
```

### 4. Record Model (Provenance)
```
Record
  ├─ firm_id
  ├─ field_name (e.g., "email", "phone")
  ├─ value
  ├─ verified (true/false)
  ├─ source (provider A/B/C)
  ├─ confidence (0.0-1.0)
  ├─ observed_at
  └─ created_at
```

### 5. Credits & Ledger (Sade Tasarım)
```
CreditPackage
  ├─ organization_id
  ├─ balance
  ├─ created_at, updated_at

LedgerEntry
  ├─ organization_id
  ├─ transaction_type (purchase/spent/refund)
  ├─ amount
  ├─ reference (payment_id / batch_id / dispute_id)
  ├─ description
  ├─ created_at

⚠️ KRİTİK: Ledger satırı "batch başına", "record başına" değil!
  - Batch oluştu → 1 satır (credit_spent: -200)
  - Dispute kabul → 1 satır (credit_refund: +50)
```

### 6. Exports
```
Export
  ├─ batch_id
  ├─ organization_id
  ├─ format (CSV/XLSX)
  ├─ s3_key (signed URL reference)
  ├─ file_size
  ├─ created_at
  ├─ downloaded_at
  └─ status (processing/ready/expired)

ExportLog
  ├─ export_id
  ├─ event (requested/completed/downloaded)
  ├─ created_at
```

### 7. Disputes (Otomatik Karar Motoru)
```
Dispute
  ├─ id
  ├─ batch_id
  ├─ organization_id
  ├─ decision (accepted/rejected)
  ├─ decision_reason_code (e.g., "EMAIL_HARD_BOUNCE")
  ├─ evidence_payload (JSON)
  ├─ disputed_count
  ├─ accepted_count
  ├─ created_at
  └─ resolved_at

DisputeItem
  ├─ dispute_id
  ├─ firm_id
  ├─ reason
  └─ created_at
```

### 8. Audit & Compliance
```
AuditLog
  ├─ user_id (nullable)
  ├─ action (batch_created/export_downloaded/dispute_filed)
  ├─ entity_type (Batch/Export/Dispute)
  ├─ entity_id
  ├─ changes (JSON)
  ├─ ip_address
  └─ created_at

ProviderCostLog (FinOps)
  ├─ batch_id
  ├─ provider (A/B/C)
  ├─ api_calls
  ├─ estimated_cost (USD)
  ├─ created_at
```

---

## 🔗 Dış Entegrasyonlar

### Ödeme Sistemi
**Stripe veya Iyzico**
- Ön ödemeli kredi satın alma
- Webhook ile "purchase completed" doğrulama
- Secure payment flow (PCI-DSS uyumlu)

### File Storage
**S3 / MinIO**
- Batch export dosyaları
- Signed URL ile güvenli indirme
- Süre sınırlı erişim

### Async Processing
**Celery + Redis**
- Batch oluşturma (IO-heavy)
- Export file generation (CPU-heavy)
- Email gönderimi
- Dispute otomatik karar

### Email Servisi
**Postmark / Sendgrid**
- Login doğrulama
- Ödeme makbuzu
- Batch hazır bildirimi
- Dispute sonuç bildirimi

### Güvenlik & Abuse Prevention
**Opsiyonel (MVP-0 minimal)**

| Kategori | Araç | Kullanım |
|----------|------|----------|
| Rate Limiting | django-ratelimit | API endpoints |
| Brute Force | django-axes | Login attempts |
| Webhook Signature | HMAC-SHA256 | Stripe/Iyzico webhooks |
| Captcha | reCAPTCHA v3 (optional) | Sensitive forms |

---

## 🌳 Karar Ağacı & Akışlar

### 5.1 Proje Tipi / Mimari Seçimi

```
Q: Ön ödemeli kredi var mı?
   └─→ EVET → Atomic transaction gerekli

Q: İtiraz otomatik ve audit zorunlu mu?
   └─→ EVET → Tek veri tabanında transaksiyon kolaylığı

Q: Batch deterministik ve tekrar üretilebilir olmalı mı?
   └─→ EVET → Sabit sıralama kuralı + query snapshot gerekli

KARAR:
✓ Django.yaml → project_type: proj_api_frontend
✓ Backend: modüler monolith
✓ Frontend: Next.js (separate deploy)
```

### 5.2 Veri Katmanı Seçimi

```
Q: Ledger + batch + dispute için ACID gerekir mi?
   └─→ EVET

Q: Ledger satırları "record başına" mı "batch başına" mı?
   └─→ "batch başına" (ledger şişmesin)

KARAR:
✓ PostgreSQL 14+ (ACID guarantees)
✓ Read replicas + pgbouncer (yüksek trafik için)
✓ Backup & WAL archiving (DR)
```

### 5.3 API Tasarımı

```
Q: Frontend ve backend paralel geliştirilecek mi?
   └─→ EVET

Q: Provider entegrasyonları değişken mi?
   └─→ EVET

KARAR:
✓ Django.yaml → api_style: api_rest + api_rest_openapi
✓ Contract-first (OpenAPI schema as SSOT)
✓ Mock server desteği (parallel frontend development)
```

### 5.4 Authentication / Session

```
Q: B2B + finansal işlem (kredi) var mı?
   └─→ EVET

Q: Token client'ta taşımak mı vs server session?
   └─→ Server session (daha secure + audit edilebilir)

KARAR:
✓ Django.yaml → auth: auth_builtin (session-based)
✓ Next.js → custom server-side sessions (httpOnly cookie)
✓ Middleware ile auth gating (protected routes)
```

### 5.5 Ledger Tasarım Prensibi

```
AMAÇ: "Ledger şişmesin"

KURALı:
  - 1 ledger satırı = 1 batch (value)
  - NOT: "batch başına" N record ≠ N ledger satırı

ÖRNEK AKIŞLAR:

1. Batch Oluşturma:
   LedgerEntry(
     transaction_type="credit_spent",
     amount=-200,
     reference=batch_id,
     created_at=now
   )

2. Dispute Kabulu:
   LedgerEntry(
     transaction_type="credit_refund",
     amount=+50,
     reference=dispute_id,
     created_at=now
   )

3. Kredi Satın Alma:
   LedgerEntry(
     transaction_type="credit_purchase",
     amount=+500,
     reference=payment_id,
     created_at=now
   )

SONUÇ: Ledger 3 satır, Dispute için detay ayrı tablo (dispute_items).
```

### 5.6 Deterministik Batch Üretimi

```
FORMÜL:
  query_hash = SHA256(city + sector + filters_json + sort_rule_version)

KRİTİK NOKTALAR:

1. Sıralama Kuralı Sabit
   sort_rule = "google_rank DESC, infobel_score DESC"
   sort_rule_version = "v1" (değişirse batch_id değişir)

2. Input Snapshot
   batch.provider_snapshot_ref = "data_v20260110"
   (batch üretildiği sırada hangi data sürümü kullanıldığını kanıtlar)

TASARIM:

  Batch (query-centric):
    ├─ query_params: JSON
    ├─ query_hash: (deterministic)
    ├─ batch_id: UUIDv7 (time-ordered)
    ├─ sort_rule_version: "v1"
    └─ provider_snapshot_ref: "data_v*"

  BatchItem (result-centric):
    ├─ batch_id
    ├─ position: 1, 2, 3... (ordered)
    └─ firm_id (immutable)

RE-DOWNLOAD:
  - CSV yeniden üretilir (batch_items referansında değişiklik yok)
  - OR saklanan dosya sunulur (byte-for-byte identical)
```

### 5.7 Otomatik İtiraz Motoru (Rule Engine)

```
KARAR MATRİSİ (MVP-0):

┌─────────────────────────────────────────────────────────┐
│ DECISION: ACCEPT (itiraz kabul → credit refund)         │
├─────────────────────────────────────────────────────────┤
│ If ANY of:                                              │
│  • Email hard bounce (SMTP 550/5xx) → EMAIL_BOUNCE     │
│  • Phone "bu firmaya ait değil" (verified) → WRONG_ORG │
│  • Firm closed/inactive (provider data) → CLOSED_FIRM  │
│  • Duplicate (same user→same firm→previous batch)      │
│    → DUPLICATE                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ DECISION: REJECT (itiraz reddedildi)                    │
├─────────────────────────────────────────────────────────┤
│ If:                                                     │
│  • "satış sonucu" / "iletişim sonucu": ilgilenmiyor    │
│  • Cevap vermedi, spam'e düştü, yanlış kişi ama firma  │
│    doğru                                                │
│  → CONTACTED_NOT_INTERESTED                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ DEFAULT: REJECT (gri alanlar MVP-0'da otomatik reddedil)│
├─────────────────────────────────────────────────────────┤
│ Manual review: Yok (v1'de eklenebilir)                  │
└─────────────────────────────────────────────────────────┘

DISPUTE TABLO ENTRİSİ:

Dispute:
  ├─ decision: "accepted" | "rejected"
  ├─ decision_reason_code: "EMAIL_BOUNCE" | "WRONG_ORG" | ...
  ├─ evidence_payload: {
  │    "bounce_code": "550",
  │    "provider_response": {...},
  │    "duplicate_reference": batch_id_old
  │  }
  └─ accepted_count: 15 (kaç record refund aldı)

SONUÇ:
  if decision == "accepted":
    LedgerEntry(
      transaction_type="credit_refund",
      amount=+accepted_count,
      reference=dispute_id
    )
```

---

## 💳 Finansal Model

### Kredi İş Akışı

```
1. USER: Ödeme Yap
   ├─→ Stripe/Iyzico
   ├─→ $50 = 500 credit
   └─→ LedgerEntry(type=credit_purchase, amount=+500)

2. USER: Batch Oluştur
   ├─→ 200 record seç
   ├─→ Sistem: credit_spent = -200
   └─→ LedgerEntry(type=credit_spent, amount=-200)

3. USER: İtiraz Aç
   ├─→ "50 record yanlış"
   ├─→ Sistem: otomatik karar (ACCEPT)
   ├─→ Refund: +50 credit
   └─→ LedgerEntry(type=credit_refund, amount=+50)

SONUÇ:
  Ledger = [+500, -200, +50] = 3 satır (temiz!)
```

### Pricing Strategy
- **Pay-per-use:** 1 record = 1 credit
- **Volume discount:** 1000+ credits = 10% indirim (opsiyonel)
- **Dispute refund:** Otomatik (rule engine kararı)

---

## 🚀 Ölçeklendirilme Stratejisi

### MVP-0 (Monolith)
```
Single Django process + Celery workers
├─ Batch oluşturma: background task (Celery)
├─ Export: S3 signed URL
└─ Disputes: rule engine (sync)
```

### Phase-1: Export Worker Scale
```
Export Service (ayrı)
├─ Büyük dosya üretimi (>100K records)
├─ Dedicated Celery workers
├─ Separate S3 bucket
└─ Signed URL caching
```

### Phase-2: Provider Orchestration
```
Provider Service (ayrı)
├─ Rate limiting per provider
├─ Cost tracking (FinOps)
├─ Cache + retry/circuit breaker
├─ Webhook processing
└─ Separate DB (read replica)
```

### Phase-3: Billing/Ledger
```
Ledger Service (ayrı)
├─ Immutable log (event store)
├─ Audit trail (append-only)
├─ Compliance reporting
└─ Separate DB (strong consistency)
```

### Database Scaling
```
PostgreSQL:
├─ Primary (write)
├─ Read replicas (dashboard queries)
├─ pgbouncer (connection pooling)
├─ WAL archiving (disaster recovery)
└─ Backup retention (30 days)
```

### Caching Strategy
```
Redis:
├─ Session store
├─ Query cache (batch results)
├─ Rate limit counters
├─ Celery task queue
└─ TTL policies per layer
```

---

## 📝 Notlar & Kısıtlamalar

### MVP-0 Boundaries
- ✅ Otomatik itiraz (rule-based)
- ❌ Manuel review yok (v1'de)
- ✅ Deterministik batch
- ✅ Audit trail
- ✅ Ön ödemeli kredi
- ❌ Subscription plan (v1'de)

### Performance Targets
- Batch oluşturma: < 5s (< 10K records)
- Export generation: < 30s (< 100K records)
- API latency: < 200ms (p95)
- Uptime target: 99.9%

### Security Requirements
- 🔒 HTTPS only
- 🔒 CSRF protection (Django)
- 🔒 SQL injection prevention (ORM)
- 🔒 Rate limiting (per user)
- 🔒 Webhook signature verification
- 🔒 httpOnly cookies (session)
- 🔒 Audit logging (tüm finansal işlemler)

---

## 📚 Referanslar

- [Django Documentation](https://docs.djangoproject.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

## 🔨 Phase-1: API & Test Implementation (MVP-0 → MVP-1)

### Overview
MVP-0 scaffold tamamlandı. Phase-1'de **DRF API**, **Unit/Integration/Contract testleri** ve **GitHub Actions CI/CD** tamamlanacak. Sonuç: Deployment-ready API ve test coverage >80%.

**Süre:** 2-3 hafta | **Team:** 1-2 dev | **Priority:** High

---

### Phase-1 İş Paketi

#### Sprint-1: DRF Serializers & ViewSets (1 hafta)

**Hedef:** 5 ana app için RESTful endpoints oluşturmak.

**Priority Sırası:**

| # | App | Endpoints | Notes |
|---|-----|-----------|-------|
| 1 | **batches** | `GET/POST /batches/`, `GET /batches/{id}/`, `GET /batches/{id}/items/` | Deterministik hash, query_hash auto-calc |
| 2 | **ledger** | `GET /ledger/entries/`, `GET /credits/balance/` | Read-only (sistem tarafından yazılan) |
| 3 | **credits** | `GET /credits/balance/`, `POST /credits/purchase/` | Pre-paid credit flow |
| 4 | **exports** | `GET/POST /exports/`, `GET /exports/{id}/` | S3 signed URL return |
| 5 | **disputes** | `GET/POST /disputes/`, `PATCH /disputes/{id}/` | Auto-decision logic, rule engine |

**Deliverables:**

```
services/backend/apps/

├─ batches/
│  ├─ serializers.py        (BatchSerializer, BatchItemSerializer)
│  ├─ views.py              (BatchViewSet with get_queryset filters)
│  ├─ filters.py            (city, sector, status filters)
│  ├─ permissions.py        (IsOwnerOrganization)
│  └─ tests/
│     ├─ __init__.py
│     └─ test_models.py     (calculate_query_hash unit tests)

├─ ledger/
│  ├─ serializers.py        (LedgerEntrySerializer, CreditPackageSerializer)
│  ├─ views.py              (LedgerEntryViewSet (read-only), CreditBalanceView)
│  └─ tests/
│     └─ test_models.py     (balance update logic)

├─ credits/
│  ├─ serializers.py        (CreditPurchaseSerializer)
│  ├─ views.py              (CreditPurchaseView → payment webhook)
│  └─ tests/
│     └─ test_views.py      (purchase flow, balance update)

├─ exports/
│  ├─ serializers.py        (ExportSerializer, ExportCreateSerializer)
│  ├─ views.py              (ExportViewSet, signed URL generation)
│  ├─ tasks.py              (Celery: generate_export_file)
│  └─ tests/
│     └─ test_views.py      (signed URL format, permission checks)

└─ disputes/
   ├─ serializers.py        (DisputeSerializer, DisputeCreateSerializer)
   ├─ views.py              (DisputeViewSet)
   ├─ rule_engine.py        (DecisionEngine class)
   ├─ tasks.py              (Celery: auto_resolve_dispute)
   └─ tests/
      ├─ test_models.py     (dispute creation)
      ├─ test_rule_engine.py (decision logic: ACCEPT vs REJECT)
      └─ test_views.py      (dispute filing, auto-decision)
```

**Key Implementation Details:**

1. **Batch.calculate_query_hash()** - Kaydetme öncesi auto-run
2. **LedgerEntry** - ORM üzerinden immutable (update:False, delete:False)
3. **CreditPackage.balance** - Atomic update (F() expressions)
4. **Export** - Celery task (async file generation)
5. **Dispute Decision** - Rule engine (konfigüre edilebilir karar ağacı)

---

#### Sprint-2: Unit & Integration Tests (1 hafta)

**Hedef:** >80% code coverage, her app için en az 3 test tipi.

**Test Stratejisi:**

```python
tests/
├─ unit/
│  ├─ test_batch_models.py
│  │  ├─ test_batch_query_hash_deterministic()
│  │  ├─ test_batch_query_hash_different_inputs()
│  │  └─ test_batch_item_firm_id_immutable()
│  │
│  ├─ test_ledger_models.py
│  │  ├─ test_ledger_entry_balance_snapshot()
│  │  └─ test_credit_package_balance_calculation()
│  │
│  ├─ test_disputes_rule_engine.py
│  │  ├─ test_email_bounce_accept()
│  │  ├─ test_wrong_org_accept()
│  │  ├─ test_contacted_not_interested_reject()
│  │  └─ test_default_reject()
│  │
│  └─ test_exports_models.py
│     └─ test_export_s3_key_generation()
│
└─ integration/
   ├─ test_batch_workflow.py
   │  ├─ test_batch_create_decrements_credits()
   │  ├─ test_batch_list_with_filters()
   │  └─ test_batch_export_flow()
   │
   ├─ test_dispute_workflow.py
   │  ├─ test_dispute_file_triggers_auto_decision()
   │  └─ test_dispute_accept_creates_refund_ledger()
   │
   └─ test_credit_purchase_workflow.py
      ├─ test_stripe_webhook_updates_credits()
      └─ test_insufficient_credits_batch_prevent()
```

**Fixtures (conftest.py güncelle):**

```python
@pytest.fixture
def org_with_credits():
    org = Organization.objects.create(name="TestOrg")
    CreditPackage.objects.create(organization=org, balance=1000)
    return org

@pytest.fixture
def batch_with_items(org_with_credits):
    batch = Batch.objects.create(
        organization=org_with_credits,
        city="Istanbul",
        sector="IT",
        filters={"size": "large"},
    )
    for i in range(10):
        BatchItem.objects.create(batch=batch, firm_id=f"firm_{i}")
    return batch

@pytest.fixture
def api_client_authenticated(api_client, django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser", password="pass123"
    )
    api_client.force_authenticate(user=user)
    return api_client
```

**Coverage Target:**
- `apps/batches/`: >85%
- `apps/ledger/`: >80%
- `apps/disputes/`: >85%
- `apps/exports/`: >75%
- `apps/credits/`: >80%

---

#### Sprint-3: Contract & E2E Tests + CI/CD (1 hafta)

**A) Contract Testing (OpenAPI)**

```
tests/contracts/openapi/
├─ validate.spec.ts         # Playwright + OpenAPI 3.0
├─ tests/
│  ├─ batches.contract.ts   (GET /batches, POST /batches, ...)
│  ├─ ledger.contract.ts    (GET /ledger/entries, GET /credits/balance)
│  ├─ disputes.contract.ts  (POST /disputes, auto-decision verification)
│  └─ exports.contract.ts   (GET /exports, signed URL format)
│
└─ fixtures/
   └─ openapi-schema.yaml   (auto-generated: drf-spectacular)
```

**Validation Rules:**
- Request/response schema match OpenAPI spec
- Status code correct (200, 201, 400, 401, 404)
- Date formats (ISO 8601)
- UUID format validation

**B) GitHub Actions CI/CD**

```yaml
infra/ci-cd/github-actions/

├─ backend.yml
│  ├─ Lint (black, isort, flake8)
│  ├─ Type Check (mypy)
│  ├─ Unit tests (pytest)
│  ├─ Coverage report
│  └─ Security scan (bandit)
│
├─ frontend.yml
│  ├─ Lint (eslint, prettier)
│  ├─ Type check (tsc --noEmit)
│  ├─ Build (next build)
│  └─ Bundle analyze
│
├─ contract.yml
│  ├─ Start services (docker-compose)
│  ├─ OpenAPI schema validation
│  └─ Contract tests (Playwright)
│
└─ e2e.yml
   ├─ Build all services
   ├─ Run Playwright tests
   ├─ Upload artifacts
   └─ Slack notification
```

**Pipeline Specifics:**

```yaml
# backend.yml
name: Backend CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: anka_test
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r services/backend/requirements.txt
      - run: cd services/backend && black --check .
      - run: cd services/backend && isort --check-only .
      - run: cd services/backend && flake8 apps/ --max-line-length=100
      - run: cd services/backend && pytest --cov=apps --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

### Branching Strategy

```
main (production)
  ↑
release/* (staging)
  ↑
develop (integration branch)
  ↑
feature/* (feature branches)
  ├─ feature/batch-api
  ├─ feature/ledger-api
  ├─ feature/dispute-engine
  └─ feature/tests-phase1
```

**Workflow:**
1. Feature branch açınız: `git checkout -b feature/batch-api`
2. PR açınız `develop`'e
3. CI pass olduktan sonra merge
4. Release hazırlanırken: `release/v0.2.0` açınız
5. Test geçtikten sonra: `main`'e merge + tag

---

### Definition of Done (DoD)

Her feature için:
- ✅ Unit tests yazılmış (>80% coverage)
- ✅ Integration tests yazılmış
- ✅ Code review geçmiş (minimum 1 reviewer)
- ✅ Lint & format pass (black, isort, eslint)
- ✅ Type check pass (mypy, tsc)
- ✅ API docs (drf-spectacular, OpenAPI)
- ✅ README/docstring updated
- ✅ No hardcoded secrets/credentials
- ✅ CI pipeline pass (all checks)

---

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Query hash collision | Unittest for determinism + SHA256 collision theory improbable |
| Ledger race conditions | Atomic database transactions + F() expressions for balance updates |
| Export timeout (large files) | Celery with long timeout (300s) + progress tracking |
| Dispute decision false positives | Whitebox testing + decision matrix review + human QA |
| CI flakiness | Retry logic for network tests + seed database state |

---

### Success Metrics

- ✅ API endpoints: 15+ endpoints live
- ✅ Test coverage: >80% (aim for 85%)
- ✅ CI pipeline: <5 min execution time
- ✅ E2E tests: smoke + critical path (batch → export → dispute)
- ✅ Documentation: OpenAPI schema + README.md
- ✅ Zero production issues (staging deployment)

---

### Next Phase (Phase-2)

After Phase-1 complete:
- **Frontend Integration:** React components + API calls
- **Payment Integration:** Stripe/Iyzico webhooks
- **Async Tasks:** Celery workers for exports + batch processing
- **Monitoring:** Sentry + DataDog dashboards

---
