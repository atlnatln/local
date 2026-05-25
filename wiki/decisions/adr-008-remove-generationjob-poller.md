---
title: "Remove GenerationJob and poll_generation_jobs after procedural migration"
created: "2026-05-25"
updated: "2026-05-25"
type: decision
tags: [decision, adr, mathlock-play, backend, technical-debt]
related:
  - mathlock-play-backend
  - mathlock-play
  - adr-007-mathlock-meb-curriculum-compliance-implantation
status: Active
---

# adr-008-remove-generationjob-poller: Remove GenerationJob and poll_generation_jobs after procedural migration

## Context

The `GenerationJob` + `poll_generation_jobs` architecture was created for AI-based (`kimi-cli`) async level/question generation, which took 5–15 minutes and required a fire-and-forget launcher + periodic poller pattern. After migrating all generators (levels, questions, puzzles) to procedural Python modules (`procedural_levels`, `procedural_questions`, `procedural-puzzles.py`), this architecture is no longer necessary. Procedural generation completes in 1–5 seconds.

Yet the codebase still creates `GenerationJob` records, launches `subprocess.Popen`, and polls every 30 seconds via the Celery beat task. This creates a conceptual mismatch: `is_ai_generated=False` but the code still uses the AI async architecture.

## Decision

Remove the `GenerationJob` model, `poll_generation_jobs` Celery beat task, and related async launcher code. Replace with direct `subprocess.run` (to keep process isolation) or inline Python function calls within the Celery task. `subprocess.run` is preferred for isolation.

## Consequences

### ✅ Pozitif

- Less complexity, fewer DB queries, no conceptual mismatch.
- Easier onboarding for new developers/agents — no need to understand the Job+Poller lifecycle.
- Procedural generation runs synchronously within the Celery task; no 30-second polling overhead.

### ⚠️ Negatif / Riskler

- If changed to direct Python calls instead of `subprocess.run`, generator code runs in the Celery worker process and could affect worker stability.
- Mitigation: keep `subprocess` but use `subprocess.run` instead of `Popen+Job+Poller`.

### 🔄 Teknik Borç

- Migration needed: Django migration to drop `GenerationJob` table, update Celery beat schedule, update tests, update wiki docs.

## Alternatives Considered

### Alternatif A: GenerationJob'ı Korumak (Status Quo)

- **Açıklama:** Mevcut `GenerationJob` + poller mimarisini koruyarak sadece `generator` alanını procedural olarak işaretlemek.
- **Neden reddedildi:** DB tablosu, poller overhead ve konseptsel uyumsuzluk gereksiz. 1–5 saniyelik işlem için 30 saniyelik polling ve Job lifecycle yönetimi aşırı.

### Alternatif B: Doğrudan Python Fonksiyon Çağrısı (subprocess.run Kullanmadan)

- **Açıklama:** Generator'ları Celery task içinden doğrudan Python fonksiyonu olarak çağırmak.
- **Neden reddedildi:** Generator kodu Celery worker process'inde çalışır; bir hata veya sonsuz döngü tüm worker'ı etkileyebilir. `subprocess.run` ile process izolasyonu korunur.

## Status

**Mevcut Durum:** `Active`

> Bu karar alındı ancak implementasyon ertelendi. Mevcut sistem stabil çalışıyor; cleanup gelecek bir "backend cleanup" session'ına bırakıldı.

> Son durum güncellemesi: 2026-05-25
