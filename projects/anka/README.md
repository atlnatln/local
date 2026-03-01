# Anka Data

> **İstediğiniz şehir ve sektörde, doğrulanmış firma iletişim bilgilerini tek seferde alın.**

Anka Data, internetteki devasa veri havuzunu önce ücretsiz tarayan, ardından adayların varlığını düşük maliyetle doğrulayan ve sadece kaliteli kayıtlara iletişim bilgisi ekleyen akıllı bir B2B veri servisidir.

---

## 🏗 Mimari: 3 Aşamalı Doğrulama Hattı (Pipeline)

Maliyetleri optimize etmek ve veri kalitesini maksimize etmek için backend tarafında "Waterfall" (Şelale) modeli uygulanmıştır:

1.  **Aşama 1: Aday Havuzu (Tarama)**
    *   **Amaç:** Geniş kapsamlı arama ile potansiyel firma ID'lerini toplamak.
    *   **Yöntem:** Google Places Text Search (Sadece ID & İsim).
    *   **Maliyet:** Ücretsiz / Çok Düşük.

2.  **Aşama 2: Doğrulama (Filtreleme)**
    *   **Amaç:** Firmanın hala faal olduğunu ve adresinin doğruluğunu teyit etmek.
    *   **Yöntem:** Place Details Pro (Adres & Display Name).
    *   **Güvenlik:** Kapanmış, taşınmış veya hatalı kayıtlar bu aşamada elenir. Enterprise maliyeti oluşmaz.

3.  **Aşama 3: Zenginleştirme (Teslim)**
    *   **Amaç:** Sadece doğrulanmış firmalara telefon ve web sitesi eklemek.
    *   **Yöntem:** Place Details Enterprise (Website & Phone).
    *   **Sonuç:** Kullanıcı sadece bu aşamayı geçen "temiz" veri için ödeme yapar.

---

## 🧩 Core Mode (Non-Destructive)

Bu repo, çekirdek kullanımda Google Maps + Gemini enrichment hattına odaklanabilir; ancak MVP+ ve canlıya hazırlık için gerekli domain uygulamaları (payments, ledger, credits, disputes, exports vb.) **kod tabanından kaldırılmaz**.

Özet kural:
- Çekirdekleştirme = çalışma profilini sadeleştirme
- Çekirdekleştirme ≠ uygulama/migration silme

---

## 🚀 Kurulum (Quick Start)

Bu proje Docker üzerinde çalışacak şekilde tasarlanmıştır.

### Gereksinimler
*   Docker & Docker Compose
*   Google Maps API Key (Places API New aktif)

### Çalıştırma

1.  **Repoyu klonlayın ve yapılandırın:**
    ```bash
    cp .env.example .env
    # .env dosyasında GOOGLE_MAPS_API_KEY alanını doldurun.
    ```

2.  **Servisleri başlatın:**
    ```bash
    docker-compose up -d --build
    ```

3.  **Veritabanı kurulumu:**
    ```bash
    docker-compose exec backend python manage.py migrate
    docker-compose exec backend python manage.py createsuperuser
    ```

4.  **Erişim:**
    *   **Frontend (Panel):** [http://localhost:3000](http://localhost:3000)
    *   **Backend API:** [http://localhost:8000/api](http://localhost:8000/api)
    *   **API Dokümantasyonu:** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)

---

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

---

## 📊 Güvenlik ve Limitler

*   **Rate Limiting:** Google API çağrılarında `Exponential Backoff` stratejisi uygulanır (429 hatalarına karşı).
*   **Hard Limits:** Varsayılan koruma limitleri env ile yönetilir (`ANKA_BATCH_MAX_RECORDS=50`, stage API call cap'leri aktif).
*   **Circuit Breaker:** Doğrulama aşamasında %50'den fazla hata alınırsa işlem otomatik durdurulur (`PARTIAL` status).

---

## 📚 Dokümantasyon

Mimari kararlar ve operasyonel rehberler `docs/` klasöründe yer almaktadır:
*   [ADR-0006: 3-Stage Verification Pipeline](docs/ADR/0006-three-stage-verification-pipeline.md)
*   [Runbook: Maps Sorgu Mantığı](docs/RUNBOOKS/maps-query-logic-pipeline.md)
*   [Runbook: Email Enrichment (Stage 4)](docs/RUNBOOKS/email-enrichment-stage4.md)
*   [Runbook: Gemini Search Grounding Enrichment](docs/RUNBOOKS/gemini-search-grounding-enrichment.md)
*   [Test Stratejileri](tests/kurallar.md)
*   [Veritabanı Modelleri](services/backend/apps/batches/models.py)

---

## 🧪 Testler

```bash
# Backend Testleri
docker-compose exec backend pytest

# E2E Testleri (Playwright)
cd tests/e2e
npx playwright test
```
