---
title: "anka-readme"
created: 2026-05-01
updated: 2026-05-01
type: raw
tags: [raw]
related: []
---


# Anka Data

> **İstediğiniz şehir ve sektörde, doğrulanmış firma iletişim bilgilerini tek seferde alın.**

Anka Data, internetteki devasa veri havuzunu önce ücretsiz tarayan, ardından adayların varlığını düşük maliyetle doğrulayan ve sadece kaliteli kayıtlara iletişim bilgisi ekleyen akıllı bir B2B veri servisidir.


## 🧩 Core Mode (Non-Destructive)

Bu repo, çekirdek kullanımda Google Maps + Gemini enrichment hattına odaklanabilir; ancak MVP+ ve canlıya hazırlık için gerekli domain uygulamaları (payments, ledger, credits, disputes, exports vb.) **kod tabanından kaldırılmaz**.

Özet kural:
- Çekirdekleştirme = çalışma profilini sadeleştirme
- Çekirdekleştirme ≠ uygulama/migration silme


## 🛠 Teknoloji Yığını

*   **Backend:** Python 3.11, Django 5.2, Django REST Framework
    *   *Async Processing:* Celery & Redis.
    *   *Data:* PostgreSQL 14.
*   **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Shadcn/UI.
*   **Altyapı:** Nginx, Docker Compose.

### Frontend Altyapı Notları (Mart 2026)

*   Next.js 16 ile `middleware.ts` → `proxy.ts` olarak taşındı; fonksiyon adı `middleware` → `proxy`.
*   `next.config.ts` içinde `turbopack.root` eklendi (monorepo lockfile uyarısı kapatıldı).
*   TailwindCSS v4 geçişi tamamlandı:
    *   `app/globals.css`: `@import "tailwindcss"` + `@theme {}`
    *   `postcss.config.js`: `@tailwindcss/postcss` plugin'i
    *   `tailwind.config.ts`: deprecation notu (CSS-first config)
*   ESLint 10'a geçildi: `.eslintrc.json` yerine `eslint.config.mjs` (flat config + `FlatCompat`).
*   React 19 automatic JSX runtime nedeniyle gereksiz `import React` satırları temizlendi.

Detay ve sürüm tablosu: `ANAHTAR_TESLIM.md`


## 📚 Dokümantasyon

Mimari kararlar ve operasyonel rehberler `docs/` klasöründe yer almaktadır:
*   [ADR-0006: 3-Stage Verification Pipeline](docs/ADR/0006-three-stage-verification-pipeline.md)
*   [Runbook: Maps Sorgu Mantığı](docs/RUNBOOKS/maps-query-logic-pipeline.md)
*   [Runbook: Email Enrichment (Stage 4)](docs/RUNBOOKS/email-enrichment-stage4.md)
*   [Runbook: Gemini Search Grounding Enrichment](docs/RUNBOOKS/gemini-search-grounding-enrichment.md)
*   [Test Stratejileri](tests/kurallar.md)
*   [Veritabanı Modelleri](services/backend/apps/batches/models.py)
