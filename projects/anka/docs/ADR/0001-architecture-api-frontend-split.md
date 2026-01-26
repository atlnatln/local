# ADR-0001: Backend API ve Frontend Mimarisinin Ayrılması

**Status:** Accepted  
**Date:** 2025-Q4 (MVP-0 Finalization)  
**Context:** B2B Data Utility SaaS'in skalabilir ve bakımlanabilir mimarisine ihtiyacı var.

---

## Karar

Backend (Django REST) ve Frontend (Next.js App Router) mimari olarak ayrılmıştır:

- **Backend (Django 5.2 + DRF 3.16)**: `/api` altında tüm endpoints
  - RESTful API (OpenAPI 3.0 spec via drf-spectacular 0.29)
  - Server-side session authentication (httpOnly cookies)
  - PostgreSQL 14 + Redis 7 (cache/queue)
  
- **Frontend (Next.js 15.5.9 + React 18.3.1)**: Standalone SPA
  - App Router (route groups: `(auth)`, `(dashboard)`)
  - Page routes: `/login`, `/register`, `/dashboard` vb.
  - Client-side state management

---

## Mantık

1. **İndependent Deployment:** Backend ve frontend bağımsız deploy edilebilir
2. **API Contract:** OpenAPI schema (`docs/API/openapi.yaml`) canonical referans
3. **CORS:** Frontend cross-origin requests yapabilir (backend'den `CORS_ALLOWED_ORIGINS` ile izin)
4. **Type Safety:** Frontend TypeScript, backend type hints + drf-spectacular
5. **Testability:** Backend unit/integration tests (pytest), Frontend E2E tests (Playwright)

---

## Sonuçlar

### Pozitif
- ✅ Takımlar bağımsız çalışabilir (frontend dev ≠ backend dev)
- ✅ API dökümantasyonu otomatik (drf-spectacular)
- ✅ Microservices geçişi kolay (ileride)
- ✅ Frontend stateless (horizontal scaling kolay)

### Sorunlar
- ⚠️ API versioning dikkat gerektirir
- ⚠️ CORS ve auth flow'u koordine edilmeli
- ⚠️ Deployment sırası önemli (breaking changes)

---

## İmplementasyon Detayları

### Backend Tarafı
```python
# project/urls.py
from rest_framework.routers import DefaultRouter
from apps.accounts.views import LoginViewSet, LogoutViewSet

router = DefaultRouter()
router.register(r'auth', LoginViewSet, basename='auth')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view()),
    path('api/docs/', SpectacularSwaggerUIView.as_view()),
]
```

### Frontend Tarafı
```typescript
// src/lib/api-client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function post<T>(endpoint: string, data: any): Promise<T> {
  const response = await fetch(`${API_URL}/api${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // httpOnly cookies
    body: JSON.stringify(data),
  });
  return response.json();
}
```

---

## İlgili Dosyalar

- `docs/TESTING.md` — Integration test stratejisi
- `infra/ci-cd/github-actions/` — Ayrı backend + frontend CI jobs
- `docker-compose.yml` — Bağımsız servisler

---

## Referanslar

- [REST API Design](https://restfulapi.net/)
- [OpenAPI 3.0 Spec](https://swagger.io/specification/)
- [Next.js API Client Patterns](https://nextjs.org/docs/app/building-your-application/data-fetching)
