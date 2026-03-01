# Runbooks Index

Bu klasör, Anka Data için operasyonel uygulama rehberlerini içerir.

## Operasyonel Runbooklar
- [Core Structure Audit (2026-02-15)](core-structure-audit-2026-02-15.md)
- [Dev Docker Performance](dev-docker-performance.md)
- [Documentation Alignment Audit (2026-02-21)](documentation-alignment-audit-2026-02-21.md)
- [Email Enrichment (Stage 4)](email-enrichment-stage4.md)
- [Export Job Failures](export-job-failures.md)
- [Gemini Search Grounding Enrichment](gemini-search-grounding-enrichment.md)
- [Maps Query Logic Pipeline](maps-query-logic-pipeline.md)
- [Payments Webhook Management](payments-webhook-management.md)
- [Payments Webhook Replay](payments-webhook-replay.md)
- [Provider Rate Limit](provider-rate-limit.md)
- [Production Readiness ve Deploy Guardrail](production-readiness-and-deploy-guardrails.md)
- [Secure Local VPS Access](secure-local-vps-access.md)

## Denetim / Audit Raporları
- [Code Audit & Fixes (Haziran 2026)](code-audit-and-fixes-2026-06.md)
- [UX Simülasyon Denetim Raporu (Temmuz 2026)](ux-simulation-audit-2026-07.md)
- [UX Simülasyon Denetim Raporu (Mart 2026)](ux-simulation-audit-2026-03.md)

## Güvenlik Belgeleri
> Detaylı güvenlik politikaları, denetim raporları ve prosedürler `docs/SECURITY/` dizininde yer alır.

- [Güvenlik Denetim Raporu (2026-02-28)](../SECURITY/security-audit-2026-02-28.md)
- [Incident Response Playbook](../SECURITY/incident-response-playbook.md)
- [Secret Rotation Runbook](../SECURITY/secret-rotation-runbook.md)
- [API Güvenlik Politikası](../SECURITY/api-security-policy.md)
- [Hardening Checklist](../SECURITY/hardening-checklist.md)
- [KVKK/Veri Uyumluluk Rehberi](../SECURITY/kvkk-data-compliance.md)
- [Bağımlılık Güncelleme Politikası](../SECURITY/dependency-update-policy.md)

## Hızlı Seçim Rehberi
- **UX denetim raporu (BE+FE hata düzeltmeleri):** `ux-simulation-audit-2026-07.md`, `ux-simulation-audit-2026-03.md`
- **Önceki kod denetimi (ödeme/export/katalog):** `code-audit-and-fixes-2026-06.md`
- **Maps/Places sorgu akışı ve maliyet güvenlikleri:** `maps-query-logic-pipeline.md`
- **Stage 4 email kazıma/zenginleştirme:** `email-enrichment-stage4.md`
- **Website enrichment (Gemini + grounding):** `gemini-search-grounding-enrichment.md`
- **Provider kaynaklı 429/kota sorunları:** `provider-rate-limit.md`
- **Production deploy güvenlik kapıları ve smoke testleri:** `production-readiness-and-deploy-guardrails.md`
- **Ödeme webhook operasyonları:** `payments-webhook-management.md`, `payments-webhook-replay.md`

## Kaynak Önceliği (Copilot için)

Doküman-kod çelişkisinde aşağıdaki sıra uygulanır:
1. Çalışan kod ve scriptler (`services/backend/**`, `services/frontend/**`, `dev-docker.sh`, `dev-local.sh`, `verify.sh`, `deploy.sh`)
2. API sözleşmesi (`docs/API/openapi.yaml`)
3. ADR kararları (`docs/ADR/*`)
4. Runbook’lar (`docs/RUNBOOKS/*`)

## Kanonik Hızlı Gerçekler

- Docker dev portları: frontend `3100`, backend `8100`.
- Native dev portları: frontend `3000`, backend `8000`.
- Auth modeli: JWT — tarayıcı oturumları **HttpOnly cookie** ile, API istemcileri `Authorization: Bearer <token>` header ile.
- Cookie ayarları: `HttpOnly=True`, `Secure=True` (prod), `SameSite=Lax`. Refresh cookie path: `/api/auth/` (logout dahil).
- Frontend auth akışı: `credentials: 'include'` ile cookie otomatik gönderilir; localStorage'da sadece optimistik flag tutulur.
- Token auto-refresh: `api-client.ts` 401 alınca mutex ile sessiz refresh yapar, orijinal isteği tekrarlar.
- Export indirme: `GET /api/exports/{id}/download/` (auth-gated FileResponse) — public URL gerektirmez.
- Export yenileme: `POST /api/exports/{id}/regenerate/` — süresi dolmuş veya hatalı export'u yeniden kuyruğa alır.
- API dokümantasyon endpoint’i: `/api/docs`.
- Test-only login endpoint’i: `/api/auth/test-login/` (yalnız test ayarında).

## Notlar
- Mimari kararlar için `docs/ADR/` klasörünü kullanın.
- API sözleşmesi için `docs/API/openapi.yaml` esas alınır.
- Bu index, operasyonel onboarding için giriş noktasıdır.
