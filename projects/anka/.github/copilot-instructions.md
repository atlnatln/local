# Anka Data — Copilot Instructions

## Big picture (read this first)
- Monorepo with two main services: `services/backend` (Django REST) and `services/frontend` (Next.js App Router).
- API boundary is `/api/*`; canonical schema lives in `docs/API/openapi.yaml` and runtime docs are at `/api/docs/`.
- Core product flow is a 3-stage batch pipeline in backend: collect IDs → verify (Pro) → enrich contacts (Enterprise). See `apps/batches/services.py` and ADR `docs/ADR/0006-three-stage-verification-pipeline.md`.
- Financial model is ledger-based and batch-centric: one ledger row per business event (purchase/spent/refund), not per record. See `apps/ledger/models.py` (`ledger_unique_reference`).
- Disputes are auto-rule driven in MVP mode (`apps/disputes/*`) and may trigger refunds tied to ledger/credits.

## Service boundaries & integrations
- Backend app domains are explicit under `services/backend/apps/` (`batches`, `providers`, `ledger`, `credits`, `payments`, `exports`, `disputes`, etc.). Keep changes within app boundaries.
- External integrations:
  - Google Places via `apps/providers/google_places.py` (batch pipeline dependency).
  - Iyzico payment intents + webhook endpoints under `apps/payments/`.
  - Redis/Celery for async jobs (`celery_app.py`, `apps/*/tasks.py`).

## Auth and API calling conventions
- Current implementation uses JWT Bearer tokens (SimpleJWT), not only session cookies.
- Frontend stores tokens in localStorage/cookies via `services/frontend/src/lib/auth.ts` and sends `Authorization: Bearer` in `src/lib/api-client.ts`.
- E2E auth bootstraps with test endpoint `/api/auth/test-login/` (enabled in `project/settings/test.py` via `ANKA_ALLOW_TEST_LOGIN=True`).

## Developer workflows (prefer these)
- Docker dev stack: `./dev-docker.sh` (use `--build` for forced rebuild). Typical ports: frontend `3100`, backend `8100`.
- Native local dev: `./dev-local.sh`. Typical ports: frontend `3000`, backend `8000`.
- Full verification gate: `./verify.sh` (runs backend pytest, OpenAPI generation+diff, frontend lint/type-check/build).
- Contract check pattern used by CI/local gate:
  - generate schema with `python manage.py spectacular --validate --fail-on-warn`
  - compare generated output to `docs/API/openapi.yaml`.

## Project-specific coding patterns
- Deterministic batch identity is computed from `city|sector|filters|sort_rule_version` (`Batch.calculate_query_hash()` / `save()` in `apps/batches/models.py`). Preserve determinism (`json.dumps(..., sort_keys=True)`).
- Batch lifecycle statuses are domain-significant (`CREATED`, `COLLECTING_IDS`, `FILTERING`, `ENRICHING_CONTACTS`, `READY`, `PARTIAL`, `FAILED`); do not invent parallel status names.
- Keep ledger operations idempotent via unique reference constraints and atomic DB operations.
- For long-running/IO-heavy work, prefer Celery tasks (e.g., `process_batch_task`) over synchronous request handlers.
- “Core mode” is non-destructive: simplify runtime profile without deleting domain apps/migrations (see README + runbook audit).

## Practical guardrails for AI edits
- Prioritize files that already implement the flow you’re changing (example: batch changes should touch `apps/batches/*` before introducing new modules).
- Keep OpenAPI and behavior aligned: if an endpoint contract changes, update schema expectations and related tests.
- When docs and code disagree, prefer current executable scripts/settings as source of truth (`dev-docker.sh`, `dev-local.sh`, `verify.sh`, `project/settings/*`).