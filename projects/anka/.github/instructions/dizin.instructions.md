---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generatrepo-root/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── .env.example
├── .env.test.example
├── docker-compose.yml
│
├── docs/
│   ├── ADR/
│   │   ├── 0001-architecture-api-frontend-split.md
│   │   ├── 0002-credit-ledger-minimal.md
│   │   ├── 0003-deterministic-batch-and-query-hash.md
│   │   └── 0004-automatic-dispute-rules-v1.md
│   ├── API/
│   │   └── openapi.yaml
│   ├── RUNBOOKS/
│   │   ���── payments-webhook-replay.md
│   │   ├── export-job-failures.md
│   │   └── provider-rate-limit.md
│   └── TESTING.md
│
├── infra/
│   ├── ci-cd/
│   │   └── github-actions/
│   │       ├── backend.yml
│   │       ├── frontend.yml
│   │       ├── contract.yml
│   │       └── e2e.yml
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   └── nginx.conf
│   └── test-compose/
│       ├── test-stack.yml                 # tests/kurallar.md: TEST_COMPOSE_FILE
│       ├── up.sh
│       └── down.sh
│
├── services/
│   ├── backend/
│   │   ├── manage.py
│   │   ├── pyproject.toml
│   │   ├── project/
│   │   │   ├── settings/
│   │   │   │   ├── base.py
│   │   │   │   ├── dev.py
│   │   │   │   ├── test.py
│   │   │   │   └── prod.py
│   │   │   ├── urls.py
│   │   │   ├── asgi.py
│   │   │   └── wsgi.py
│   │   ├── apps/
│   │   │   ├── accounts/                  # user/org/roles
│   │   │   ├── catalog/                   # şehir/sektör
│   │   │   ├── records/                   # firm+fields provenance schema
│   │   │   ├── batches/                   # query_hash, batch_id, batch_items
│   │   │   ├── credits/                   # balance projections (read model)
│   │   │   ├── ledger/                    # purchase/spent/refund
│   │   │   ├── payments/                  # Stripe/Iyzico + webhooks
│   │   │   ├── exports/                   # csv/xlsx jobs + signed urls
│   │   │   ├── disputes/                  # auto rules + dispute items
│   │   │   ├── providers/                 # API clients + adapters
│   │   │   ├── audit/                     # audit events
│   │   │   └── common/
│   │   ├── celery_app.py
│   │   ├── conftest.py                    # shared fixtures (tests_kurallar)
│   │   └── tests/
│   │       ├── unit/
│   │       ├── integration/
│   │       └── contract/
│   │
│   └── frontend/
│       ├── package.json
│       ├── next.config.ts
│       ├── tsconfig.json
│       ├── app/
│       │   ├── page.tsx                   # landing
│       │   ├── (auth)/
│       │   │   └── login/page.tsx
│       │   ├── (dashboard)/
│       │   │   ├── dashboard/page.tsx
│       │   │   ├── batch/new/page.tsx     # filtre+adet+opsiyon
│       │   │   ├── checkout/page.tsx
│       │   │   ├── exports/page.tsx
│       │   │   └── disputes/page.tsx
│       │   └── api/                       # (opsiyonel) BFF/proxy routes
│       └── src/
│           ├── components/
│           ├── lib/
│           │   ├── api-client.ts
│           │   ├── auth.ts
│           │   └── validation.ts
│           └── tests/
│
├── tests/
│   ├── kurallar.md                         # tests_kurallar_Version1.md’nin repo kopyası
│   ├── e2e/
│   │   └── playwright/
│   │       ├── smoke.spec.ts
│   │       ├── credit-purchase.spec.ts
│   │       ├── batch-create-download.spec.ts
│   │       └── dispute-auto-refund.spec.ts
│   ├── contracts/
│   │   └── openapi/
│   │       └── validate.spec.ts
│   └── fixtures/
│       ├── e2e_seed.dump
│       └── sample_provider_payloads.json
│
└── artifacts/                              # CI çıktıları (gitignored)
    ├── playwright/
    ├── test-logs/
    └── coverage/ing code, answering questions, or reviewing changes.