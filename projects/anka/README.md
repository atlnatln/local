# Anka Platform - End-to-End Setup Guide

> B2B Data Utility SaaS with Deterministic Batch Processing, Pre-paid Credits, and Automated Dispute Resolution

## 📋 Project Overview

**Technology Stack:**
- **Backend:** Django 5.2 + Django REST Framework 3.16
- **Frontend:** Next.js 15.5.9 with App Router + TypeScript
- **Database:** PostgreSQL 14 (ACID transactions)
- **Cache & Queue:** Redis 7 + Celery 5.6.2
- **File Storage:** S3/MinIO (signed URLs)
- **Payment:** Stripe + Iyzico (integration-ready)
- **Container:** Docker & docker-compose

**Architecture:** Hybrid Modular Monolith (MVP-0) → Microservices (future)

---

## 🚀 Quick Start

### Prerequisites

- Docker & docker-compose (recommended)
- Python 3.11+ (for local development)
- Node.js 18+ (for local frontend development)
- PostgreSQL 14+ (if not using Docker)

### Option 1: Docker (Recommended)

```bash
# 1. Clone and setup
cd /home/akn/anka
cp .env.example .env

# 2. Build and start all services
docker-compose up -d

# 3. Run migrations
docker-compose exec backend python manage.py migrate

# 4. Create superuser
docker-compose exec backend python manage.py createsuperuser

# 5. Access services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs
- Nginx: http://localhost
```

### Option 2: Local Development

#### Backend Setup

```bash
# 1. Create virtual environment
cd services/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup PostgreSQL (Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_DB=anka \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:14-alpine

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver

# 7. Start Celery worker (separate terminal)
celery -A celery_app worker -l info

# 8. Start Celery beat (separate terminal)
celery -A celery_app beat -l info
```

#### Frontend Setup

```bash
# 1. Install dependencies
cd services/frontend
npm install

# 2. Setup environment
cp .env.example .env.local
# Edit .env.local if needed

# 3. Start development server
npm run dev

# Frontend: http://localhost:3000
```

---

## 📁 Project Structure

```
/home/akn/anka/
├── .env.example                    # Environment variables template
├── docker-compose.yml              # Docker Compose configuration
│
├── services/
│   ├── backend/                    # Django Backend (MVP-0)
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   ├── celery_app.py
│   │   ├── conftest.py
│   │   ├── project/
│   │   │   ├── urls.py
│   │   │   ├── asgi.py
│   │   │   ├── wsgi.py
│   │   │   └── settings/
│   │   │       ├── base.py         # Common settings
│   │   │       ├── dev.py          # Development
│   │   │       ├── test.py         # Testing
│   │   │       └── prod.py         # Production
│   │   └── apps/
│   │       ├── accounts/           # Users, Orgs, Membership
│   │       ├── catalog/            # City, Sector, Filters
│   │       ├── records/            # Firm records (field-level provenance)
│   │       ├── batches/            # Query batches (deterministic hash)
│   │       ├── credits/            # Credit balance (read model)
│   │       ├── ledger/             # Financial transactions (batch-level)
│   │       ├── payments/           # Stripe/Iyzico webhooks
│   │       ├── exports/            # CSV/XLSX generation + S3 signed URLs
│   │       ├── disputes/           # Auto-resolution rules + items
│   │       ├── providers/          # Data provider integrations
│   │       ├── audit/              # Audit logs + FinOps
│   │       └── common/             # Shared utilities
│   │
│   └── frontend/                   # Next.js Frontend (App Router)
│       ├── app/
│       │   ├── layout.tsx          # Root layout
│       │   ├── page.tsx            # Homepage
│       │   ├── (auth)/
│       │   │   └── login/page.tsx
│       │   └── (dashboard)/
│       │       ├── layout.tsx
│       │       ├── dashboard/page.tsx
│       │       ├── batch/new/page.tsx
│       │       ├── checkout/page.tsx
│       │       ├── exports/page.tsx
│       │       └── disputes/page.tsx
│       ├── src/
│       │   └── lib/
│       │       ├── api-client.ts   # Fetch wrapper with auth
│       │       ├── auth.ts         # Auth utilities
│       │       └── types.ts        # TypeScript types
│       ├── package.json
│       ├── next.config.ts
│       └── tsconfig.json
│
├── infra/
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   └── nginx.conf
│   ├── ci-cd/
│   │   └── github-actions/
│   │       ├── backend.yml
│   │       ├── frontend.yml
│   │       ├── contract.yml
│   │       └── e2e.yml
│   └── test-compose/
│       ├── test-stack.yml
│       ├── up.sh
│       └── down.sh
│
├── tests/
│   ├── kurallar.md                 # Test rules & fixtures
│   ├── e2e/
│   │   └── playwright/
│   │       ├── smoke.spec.ts
│   │       ├── credit-purchase.spec.ts
│   │       ├── batch-create-download.spec.ts
│   │       └── dispute-auto-refund.spec.ts
│   └── contracts/
│       └── openapi/
│           └── validate.spec.ts
│
└── docs/
    ├── ADR/                        # Architecture Decision Records
    │   ├── 0001-architecture-api-frontend-split.md
    │   ├── 0002-credit-ledger-minimal.md
    │   ├── 0003-deterministic-batch-and-query-hash.md
    │   └── 0004-automatic-dispute-rules-v1.md
    ├── API/
    │   └── openapi.yaml            # OpenAPI 3.0 schema
    ├── RUNBOOKS/
    │   ├── payments-webhook-replay.md
    │   ├── export-job-failures.md
    │   └── provider-rate-limit.md
    └── TESTING.md
```

---

## 🔑 Critical Features

### 1. Deterministic Batch Processing
```python
# query_hash = SHA256(city + sector + filters_json + sort_rule_version)
# Same query = Same result set (guaranteed)
batch.calculate_query_hash()
```

### 2. Ledger Design (SADE - One Row Per Batch)
```python
# KRİTİK: 1 ledger row = 1 batch event (NOT N rows for N records)
# Types: purchase, spent, refund
LedgerEntry(
    organization=org,
    transaction_type='spent',  # Batch data retrieval
    amount=batch.cost,         # Pre-calculated cost
    reference_id=batch.id,
)
```

### 3. Automated Dispute Resolution
```python
# ACCEPT if ANY:
# - Email hard bounce (SMTP 550/5xx)
# - Phone validation: "bu firmaya ait değil"
# - Firm closed/inactive
# - Duplicate

# REJECT if:
# - Sales result: no response, wrong person

# DEFAULT: REJECT (MVP-0, no manual review)
```

### 4. Server-Side Session Authentication
```python
# NOT JWT (incompatible with httpOnly cookies)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # JS cannot access
SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## 🛠️ Development Workflow

### Creating Models

```bash
# 1. Define model in apps/[app]/models.py
# 2. Create migration
python manage.py makemigrations [app]

# 3. Review migration
cat apps/[app]/migrations/0001_initial.py

# 4. Apply migration
python manage.py migrate

# 5. Register in admin (optional)
# apps/[app]/admin.py
admin.site.register(MyModel)
```

### Creating API Endpoints

```bash
# 1. Create serializer (apps/[app]/serializers.py)
from rest_framework import serializers

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

# 2. Create ViewSet (apps/[app]/views.py)
from rest_framework import viewsets

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

# 3. Register router (project/urls.py)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'mymodel', MyModelViewSet)
urlpatterns += router.urls
```

### Running Tests

```bash
# Unit tests
pytest apps/[app]/tests/unit/

# Integration tests
pytest apps/[app]/tests/integration/

# With coverage
pytest --cov=apps/[app]

# E2E tests (Playwright)
npx playwright test tests/e2e/

# Contract tests (OpenAPI validation)
pytest tests/contracts/
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login/` - Server-side session login
- `POST /api/auth/logout/` - Clear session
- `GET /api/auth/me/` - Current user profile
- `POST /api/auth/change-password/` - Change password

### Batches
- `GET /api/batches/` - List batches
- `POST /api/batches/` - Create batch (deterministic hash auto-calculated)
- `GET /api/batches/{id}/` - Batch details
- `GET /api/batches/{id}/export/` - Trigger export job
- `GET /api/batches/{id}/items/` - Batch items

### Credits
- `GET /api/credits/balance/` - Organization credit balance
- `POST /api/credits/purchase/` - Purchase credits (payment)

### Exports
- `GET /api/exports/` - List exports
- `GET /api/exports/{id}/` - Export details (with signed URL)
- `POST /api/exports/` - Create export job

### Disputes
- `GET /api/disputes/` - List disputes
- `POST /api/disputes/` - File dispute
- `GET /api/disputes/{id}/` - Dispute details
- `PATCH /api/disputes/{id}/` - Update dispute

### OpenAPI Documentation
- `GET /api/docs/` - Swagger UI (drf-spectacular)
- `GET /api/redoc/` - ReDoc
- `GET /api/schema/` - OpenAPI JSON schema

---

## 🔐 Environment Variables

Create `.env` from `.env.example`:

```bash
# Django
DJANGO_SETTINGS_MODULE=project.settings.dev
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=anka
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0

# Payments
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
IYZICO_API_KEY=...

# Storage
USE_S3=False
AWS_S3_ENDPOINT_URL=http://minio:9000

# Email
POSTMARK_SERVER_TOKEN=...

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## 🐛 Troubleshooting

### Database Migration Issues
```bash
# Show migration history
python manage.py showmigrations

# Rollback migration
python manage.py migrate [app] [migration_number]

# Force migration
python manage.py migrate [app] --fake-initial
```

### Celery Connection Issues
```bash
# Check Redis connection
redis-cli ping

# Check Celery worker status
celery -A celery_app inspect active

# Purge queue
celery -A celery_app purge
```

### Docker Issues
```bash
# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart [service]

# Rebuild image
docker-compose build --no-cache [service]

# Clean up
docker-compose down -v  # Remove volumes too
```

---

## 📝 Next Steps

1. **Run migrations:** `python manage.py migrate`
2. **Create superuser:** `python manage.py createsuperuser`
3. **Explore API:** http://localhost:8000/api/docs
4. **Test endpoints:** Use Postman or curl
5. **Build UI:** Create React components in frontend/
6. **Implement business logic:** Fill in Celery tasks
7. **Add tests:** Write pytest cases for models/views
8. **Setup CI/CD:** Configure GitHub Actions workflows

---

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

## 📄 License

Proprietary - Anka Platform

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
