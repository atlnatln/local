# Docs Overview (Copilot Quick Start)

Bu klasör, Anka sisteminin karar kayıtlarını (ADR), API sözleşmesini ve operasyon runbook’larını içerir.

## 1) Nereden Başlamalı?

- Mimari kararlar: `docs/ADR/`
- API sözleşmesi (kanonik): `docs/API/openapi.yaml`
- Operasyonel adımlar: `docs/RUNBOOKS/`

Yeni bir Copilot/ajan için önerilen okuma sırası:
1. `docs/ADR/0001-architecture-api-frontend-split.md`
2. `docs/ADR/0006-three-stage-verification-pipeline.md`
3. `docs/ADR/0002-credit-ledger-minimal.md`
4. `docs/ADR/0004-automatic-dispute-rules-v1.md`
5. `docs/RUNBOOKS/README.md`

## 2) Kanonik Gerçekler (Hızlı)

- Docker dev: frontend `3100`, backend `8100`
- Native dev: frontend `3000`, backend `8000`
- Auth: JWT Bearer
- API docs endpoint: `/api/docs`
- Batch kritik statüler: `CREATED`, `COLLECTING_IDS`, `FILTERING`, `ENRICHING_CONTACTS`, `ENRICHING_EMAILS`, `READY`, `PARTIAL`, `FAILED`

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
