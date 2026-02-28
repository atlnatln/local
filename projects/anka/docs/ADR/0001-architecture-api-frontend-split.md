# ADR-0001: API-Frontend Ayrımı

**Status:** Accepted  
**Date:** 2025-Q4 (2026-02 revizyonu)  

## Karar

Anka mimarisi iki bağımsız katman olarak çalışır:

- **Backend:** Django REST API (`/api/*`), OpenAPI kaynağı `docs/API/openapi.yaml`
- **Frontend:** Next.js App Router, API tüketen ayrı servis

Auth akışı **JWT Bearer** modelidir. Frontend token’ı `localStorage`/cookie’de tutar ve API çağrılarında `Authorization: Bearer ...` gönderir.

## Gerekçe

- Backend ve frontend’in bağımsız deploy edilebilmesi
- API sözleşmesinin tek kaynaktan (OpenAPI) yönetilmesi
- E2E ve contract testlerin API sınırında net çalışması

## Uygulama Notları (Güncel)

- Backend URL girişleri: `project/urls.py` (`/api/docs`, `/api/schema`, `/api/auth/*`)
- Frontend API istemcisi: `services/frontend/src/lib/api-client.ts`
- Auth yardımcıları: `services/frontend/src/lib/auth.ts`
- Test login endpoint’i: `/api/auth/test-login/` (yalnız test ayarında)

## Sonuçlar

Pozitif:
- Servis sınırları nettir, ekipler paralel ilerleyebilir.
- OpenAPI + CI kontrat kontrolü ile kırıcı değişiklikler erken yakalanır.

Dikkat noktası:
- CORS ve public URL env değerleri deploy sırasında guardrail ile doğrulanmalıdır.

## Referans

- `docs/API/openapi.yaml`
- `tests/kurallar.md`
- `docs/RUNBOOKS/production-readiness-and-deploy-guardrails.md`
