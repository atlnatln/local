# Katkı Rehberi

Bu rehber, Anka projesine nasıl katkıda bulunacağınızı anlatır.

---

## 📋 Başlamadan Önce

1. **Proje Hakkında Bilgi Edinin**
   - `README.md` — Genel bakış ve teknoloji stack'i
   - `GETTING_STARTED.md` — Lokal kurulum ve başlatma
   - `docs/ADR/` — Mimari kararlar ve justification
   - `ANAHTAR_TESLIM.md` — Şu anki durum ve doğrulama

2. **Bağımlılıkları Yükleyin**
   ```bash
   ./dev-docker.sh  # Docker ile (önerilen)
   # veya
   cd services/backend && pip install -r requirements.txt
   cd services/frontend && npm ci
   ```

3. **Testleri Çalıştırın**
   ```bash
   ./verify.sh  # Tek komutla tüm kontroller
   ```

---

## 🔄 Geliştirme İş Akışı

### 1. Branch Oluşturun
```bash
git checkout -b feature/your-feature-name
# veya
git checkout -b bugfix/issue-number
```

Branch adlandırması:
- `feature/*` — Yeni özellikler
- `bugfix/*` — Hata düzeltmeleri
- `docs/*` — Dokümentasyon
- `refactor/*` — Kod iyileştirmeleri

### 2. Değişiklikleri Yapın

#### Backend (Django)
```bash
cd services/backend
source venv/bin/activate  # veya Docker kullansanız exec yapın
# Kodunuzu yazın
pytest  # Testleri çalıştırın
```

#### Frontend (Next.js)
```bash
cd services/frontend
npm run dev  # Dev server
# Kodunuzu yazın
npm run lint && npm run type-check  # Doğrulayın
npm run build  # Production build test edin
```

### 3. Testler Yazın
- **Backend:** `services/backend/apps/<module>/tests/test_*.py`
- **Frontend:** `services/frontend/src/**/*.test.ts`
- **E2E:** `tests/e2e/playwright/`

```bash
# Backend test çalıştırma
pytest apps/module/tests/test_feature.py -v

# Frontend test çalıştırma
npm test -- test/feature.test.ts
```

### 4. Doğrulayın
```bash
# Tüm kontroller
./verify.sh

# Veya manuel:
cd services/backend && pytest
cd services/frontend && npm run lint && npm run type-check && npm run build
```

### 5. Commit ve Push
```bash
git add .
git commit -m "feat: description of your change

- Detailed explanation
- Why this change?
- Related issue #123"

git push origin feature/your-feature-name
```

Commit mesajı kuralı (Conventional Commits):
- `feat:` — Yeni özellik
- `fix:` — Hata düzeltmesi
- `docs:` — Dokümentasyon
- `test:` — Test ekleme/düzeltme
- `refactor:` — Kod iyileştirmesi
- `chore:` — Bağımlılık, yapılandırma (side effects yok)

### 6. Pull Request Açın
- `PR_TEMPLATE.md` şablonunu kullanın
- Hangi sorunu çözdüğünü açıklayın
- Test sonuçlarınızı ekleyin
- Breakage risk'i belirtin

---

## 📊 Kod Standartları

### Backend (Python)
- **Style:** PEP 8 (yapılandırma: `.editorconfig`)
- **Type Hints:** Python 3.11+ type hints kullanın
- **Tests:** 80%+ coverage beklenir
- **Migrations:** Her model değişikliğinde migration oluşturun

```python
# ✅ İyi
def create_batch(
    user: User,
    fields: list[dict[str, Any]],
    quantity: int = 100,
) -> Batch:
    """Create a new batch with the given fields and quantity."""
    logger.info(f"Creating batch for user {user.id}")
    batch = Batch.objects.create(user=user, quantity=quantity)
    return batch

# ❌ Kötü
def create_batch(user, fields, quantity=100):
    batch = Batch.objects.create(user=user, quantity=quantity)
    return batch
```

### Frontend (TypeScript)
- **Style:** ESLint + Prettier (yapılandırma: `eslint.config.mjs` flat config, `prettier.config.js`)
- **Type Safety:** `any` kullanmayın; proper types yazın
- **Components:** Functional components + hooks
- **Testing:** E2E + unit tests

```typescript
// ✅ İyi
interface BatchCreateProps {
  userId: string;
  quantity: number;
}

export function BatchForm({ userId, quantity }: BatchCreateProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    setLoading(true);
    try {
      const batch = await createBatch({ userId, quantity });
      // ...
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setLoading(false);
    }
  }

  return (/* JSX */);
}

// ❌ Kötü
export function BatchForm(props: any) {
  // ...
}
```

---

## 🧪 Test Kuralları

Detaylı test rehberi için `tests/kurallar.md`'ye bakın.

### Minimum Beklentiler
- **Backend:** Unit + integration test kombinasyonu
- **Frontend:** Component + E2E test kombinasyonu
- **API:** Contract test (OpenAPI doğrulaması)

```bash
# Backend test
pytest services/backend/apps/module/tests/ -v --cov

# Frontend test
npm test -- --coverage

# Contract test
python manage.py spectacular --validate --fail-on-warn
```

---

## 📝 Dokümentasyon

Özellikle:
1. **Docstring'ler:** Her function/class'ın docstring'i olsun
2. **Type Hints:** Return type + parameter types
3. **README Güncelleme:** Yeni özellik ise ilgili bölümü güncelleyin
4. **ADR:** Mimari karar veriyorsanız `docs/ADR/` altında dokümante edin

---

## 🚀 CI/CD Pipeline

GitHub Actions otomatik çalışır:

1. **Backend Job:** `infra/ci-cd/github-actions/backend.yml`
   - Testleri çalıştır
   - Coverage rapor oluştur
   - OpenAPI contract doğrula

2. **Frontend Job:** `infra/ci-cd/github-actions/frontend.yml`
   - ESLint lint
   - TypeScript type-check
   - Build ve artifact

3. **E2E Job:** `infra/ci-cd/github-actions/e2e.yml`
   - Playwright testleri (manuel trigger)

PR birleştirilmeden tüm joblar ✅ olmalı.

---

## 🔐 Gizli Bilgiler

- `.env` dosyasını repo'ya commit **etmeyin**
- `.env.example` var; buradan template alın
- Sensitive datalar (keys, passwords, tokens) sistematik ortam değişkenlerinden gelir
- JWT token'lar **HttpOnly cookie** ile yönetilir (bkz. `apps/accounts/cookie_auth.py`)
  - Frontend: `credentials: 'include'` ile cookie otomatik gönderilir
  - 401 alındığında `api-client.ts` sessiz token refresh yapar (mutex korumalı)
  - Refresh cookie path: `/api/auth/` (logout dahil)
  - API istemcileri (Swagger, curl): `Authorization: Bearer <token>` header kullanabilir
  - Log'larda PII maskelenir (bkz. `apps/common/pii.py`)
- Export dosyaları `GET /api/exports/{id}/download/` ile auth-gated sunulur (public URL gerektirmez)

---

## 📚 Kaynaklar

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Next.js Docs](https://nextjs.org/docs)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [Proje ADRs](docs/ADR/)

---

## 🎯 Sık Sorular

### P: Hata alıyorum `DJANGO_SETTINGS_MODULE not set`
C: Ortam değişkeni ayarlayın:
```bash
export DJANGO_SETTINGS_MODULE=project.settings.dev
# veya Docker: docker compose exec -T backend pytest
```

### P: Frontend build başarısız
C: Bağımlılıkları temizleyin:
```bash
rm -rf node_modules package-lock.json
npm ci
npm run build
```

### P: OpenAPI şeması üretiliyor mu?
C: Açıkça üretmek için:
```bash
python manage.py spectacular --file docs/API/openapi.yaml --validate --fail-on-warn
```

### P: Test coverage nasıl görüntülenecek?
C:
```bash
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

---

**Teşekkürler katkılarınız için! 🙌**
