# Production Readiness ve Deploy Guardrail Runbook

## Amaç
Bu runbook, Anka production deploy sürecinde kritik hataları canlıya çıkmadan engelleyen zorunlu güvenlik kapılarını ve operasyon adımlarını tarif eder.

## Kapsam
- Frontend build-time API URL güvenliği
- Google OAuth endpoint erişilebilirlik kontrolü
- Health endpoint doğrulaması
- CORS ve public URL konfigürasyon kontrolü
- Batch kredi settlement ve idempotent iade güvenliği
- Export SLA watchdog (takılan export işleri)

## Zorunlu Env Değerleri
`deploy.sh` artık aşağıdaki değişkenleri zorunlu kontrol eder:
- `GOOGLE_OIDC_CLIENT_ID`
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SITE_URL`

### Ek Kurallar
- `NEXT_PUBLIC_API_URL` localhost/127.0.0.1 olamaz.
- `NEXT_PUBLIC_SITE_URL` localhost/127.0.0.1 olamaz.
- `CORS_ALLOWED_ORIGINS` içinde `https://ankadata.com.tr` yoksa uyarı verilir.

## Deploy Sırasında Otomatik Guardrail Kontrolleri

### 1) Frontend Runtime Bundle Check
Amaç: Production bundle içine `localhost:8000` fallback gömülmesini engellemek.

Uygulama:
- Container: `anka_frontend_prod`
- Yol: `/app/.next/static/chunks`
- Aranan pattern: `localhost:8000`

Başarısızlık davranışı:
- Deploy fail edilir.
- Muhtemel sebep: yanlış `NEXT_PUBLIC_API_URL` ile build.

### 2) Edge Smoke Check
Amaç: edge katmanında nginx route sağlık doğrulaması.

Uygulama:
- `nginx -t`
- Domain curl kontrolleri:
  - `https://ankadata.com.tr/`
  - `https://tarimimar.com.tr/`

### 3) Application Smoke Check
Amaç: uygulama ve auth kritik path’lerinin yayın sonrası çalıştığını doğrulamak.

Uygulama:
- `GET /api/health/` => `200`
- `OPTIONS /api/auth/google/` => `2xx`
- `POST /api/auth/google/` boş payload => `400` (beklenen doğrulama hatası)

Başarısızlık davranışı:
- Deploy fail edilir.
- Log üzerinden ilgili kontrol adıyla hızlı teşhis yapılır.

## Export SLA Watchdog

Amaç:
- `processing` durumunda takılan export işlerini otomatik tespit etmek ve sonsuza kadar beklemesini engellemek.

Uygulama:
- Periodic task: `apps.exports.tasks.monitor_stuck_exports_task`
- Çalışma periyodu: 2 dakika
- SLA eşiği: `ANKA_EXPORT_SLA_MINUTES` (default 5)

Davranış:
- Eşiği geçen `processing` export kayıtları `failed` yapılır.
- `error_message` içine SLA nedeni yazılır.
- `ExportLog` tablosuna `sla_failed` event'i eklenir.

Operasyon kontrolü:
1. Celery beat çalışıyor mu doğrula.
2. `failed` export kayıtlarında `SLA exceeded` mesajını doğrula.
3. Gerekirse export kaydını `pending`e çekip yeniden kuyrukla.

## Operasyon Akışı (Özet)
1. `./deploy.sh` çalıştır.
2. Env pre-check’lerin geçtiğini doğrula.
3. Servis health tamamlandıktan sonra frontend runtime bundle check sonucunu doğrula.
4. Edge + application smoke check sonuçlarını doğrula.
5. Başarısız kontrol varsa deploy’u başarılı kabul etme; sebebi düzeltip tekrar çalıştır.

## Olası Hata Senaryoları ve Müdahale

### Senaryo: Batch tamamlandı ama teslim adedi tahminden düşük
Politika:
- Batch oluşturulurken tahmini kredi bloke edilir.
- Pipeline sonunda gerçek teslim adedine göre settlement yapılır.
- Fazla bloke edilen kredi otomatik iade edilir.

Teknik güvenlik:
- İade ledger kaydı tekil referansla yazılır: `reference_type=dispute`, `reference_id=batch-refund:{batch_id}`
- Aynı batch için tekrar iade girişimi idempotent olarak atlanır.
- Kredi paketi güncellemesi transaction altında yapılır.

Operasyon kontrolü:
1. İlgili batch için spent ledger kaydı var mı doğrula.
2. Refund ledger kaydı tekil referansla var mı doğrula.
3. `CreditPackage.balance` ve `total_refunded` alanlarını doğrula.

### Senaryo: Google login’da "Failed to fetch"
Muhtemel nedenler:
- Frontend bundle içinde localhost fallback
- OAuth preflight endpoint 502/5xx

Müdahale:
1. `deploy.sh` guardrail çıktısını incele.
2. `NEXT_PUBLIC_API_URL` değerini doğrula.
3. Backend/nginx container loglarını kontrol et.

### Senaryo: Health check başarısız
Muhtemel nedenler:
- Backend startup/migration sorunu
- Nginx upstream routing sorunu

Müdahale:
1. `docker compose ... ps`
2. `docker compose ... logs backend nginx`
3. Migrate/collectstatic adımlarını tekrar doğrula.

## Not
Bu runbook, deploy sırasında insan hatasını azaltmak için "fail-fast" yaklaşımı kullanır: kritik kontrol geçmezse deploy otomatik durdurulur.

---

## Export Task Retry Politikası (Exponential Backoff)

`generate_export_file` Celery task'ı artık geçici hatalarda otomatik retry yapar:

| Deneme | Bekleme |
|--------|---------|
| 1. (ilk) | — |
| 2. retry | 2 dakika |
| 3. retry | 4 dakika |
| 4. retry (son) | 8 dakika |

Son denemede de başarısız olursa:
- `Export.status = "failed"` olarak güncellenir
- `ExportLog(event="failed")` kaydedilir
- `emit_alarm(code="EXPORT_FAILED")` tetiklenir

**Takıp kalan export retry'ı için manuel tetikleme:**
```bash
docker exec anka_celery_worker_prod python manage.py shell -c "
from apps.exports.tasks import generate_export_file
export_id = '<UUID>'
generate_export_file.apply_async(args=[export_id])
print('Queued:', export_id)
"
```

---

## Merkezi Alarm Sistemi (`apps.common.alerts`)

Her kritik hata `apps/common/alerts.py#emit_alarm()` üzerinden yayılır.

**Çıktı formatı (Docker log driver tarafından yakalanır):**
```json
{
  "alarm": true,
  "code": "EXPORT_FAILED",
  "level": "ERROR",
  "timestamp": "2026-02-21T18:00:00+00:00",
  "message": "Export generation failed after all retries",
  "metadata": { "export_id": "...", "format": "csv" }
}
```

**Tanımlı alarm kodları:**

| Kod | Tetikleyen | Seviye |
|-----|------------|--------|
| `EXPORT_FAILED` | `generate_export_file` (max retry sonrası) | ERROR |
| `EXPORT_SLA_EXCEEDED` | `monitor_stuck_exports_task` | ERROR |
| `BATCH_PIPELINE_FAILED` | `BatchProcessor.run_pipeline()` exception | ERROR |
| `DISPUTE_RESOLUTION_FAILED` | `auto_resolve_dispute` (max retry sonrası) | ERROR |

**Email bildirimi aktifleştirmek için:**
`.env.production` içine ekle:
```env
ANKA_ALARM_EMAIL_ENABLED=True
DJANGO_ADMINS=Admin Name <admin@ankadata.com.tr>
```
Email backend olarak Postmark kullanılır (`prod.py`).

---

## Dispute Task Retry Politikası

`auto_resolve_dispute` Celery task'ı artık geçici hatalarda otomatik retry yapar:

| Deneme | Bekleme |
|--------|---------|
| 1. (ilk) | — |
| 2. retry | 1 dakika |
| 3. retry (son) | 2 dakika |

Son denemede başarısız olursa `DISPUTE_RESOLUTION_FAILED` alarımı tetiklenir.

---

## Sentry DSN Konfigürasyonu

`SENTRY_DSN` boş bırakılırsa Sentry pasiftir (hatalı DSN değeri backend'i crash etmez).

Aktif etmek için `.env.production` içine gerçek bir Sentry DSN gir:
```env
SENTRY_DSN=https://abc123@o123.ingest.sentry.io/456789
```
Değer `https://` ile başlamıyorsa `prod.py` init'i atlar.
