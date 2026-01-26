# Test Rehberi

Bu doküman, Anka repo’sunda testleri yerelde ve CI’da nasıl çalıştıracağınızı özetler.

## Backend (Django)

Backend testleri `pytest` + `pytest-django` ile çalışır.

### Docker ile

- Stack’i başlat: `./dev-docker.sh`
- Test çalıştır:

```bash
docker compose exec -T backend pytest
```

Tek komutla (backend + contract + frontend) doğrulama için repo root’ta:

```bash
./verify.sh
```

### Lokal (venv) ile

```bash
cd services/backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements-base.txt -r requirements.txt
pip install pytest-django pytest-cov isort

export DJANGO_SETTINGS_MODULE=project.settings.test
pytest
```

Notlar:
- Test ayarları: `project.settings.test` (SQLite `:memory:`)
- Coverage varsayılanı `pyproject.toml` içinde `apps` dizinine göre ayarlı.

## Frontend (Next.js)

```bash
cd services/frontend
npm ci
npm run lint
npm run type-check
npm run build
```

## Contract (OpenAPI)

Repo’da OpenAPI çıktısı `docs/API/openapi.yaml` olarak tutulur.

Şemayı üretip doğrulamak için:

```bash
cd services/backend
export DJANGO_SETTINGS_MODULE=project.settings.test
python manage.py spectacular --file ../../docs/API/openapi.yaml --validate --fail-on-warn
```

CI ayrıca üretilen şemanın `docs/API/openapi.yaml` ile birebir aynı olmasını bekler.

Yerelde diff kontrolü:

```bash
cd services/backend
export DJANGO_SETTINGS_MODULE=project.settings.test
mkdir -p ../../artifacts
python manage.py spectacular --file ../../artifacts/openapi.generated.yaml --validate --fail-on-warn
diff -u ../../docs/API/openapi.yaml ../../artifacts/openapi.generated.yaml
```

## E2E (Playwright)

E2E testleri `tests/e2e/playwright/` altında tutulur ve CI’da manuel (workflow_dispatch) çalışacak şekilde tanımlıdır.

Yerelde çalıştırmak için:

```bash
docker compose up -d --build
npx --yes playwright@1.41.2 install --with-deps chromium
npx --yes playwright@1.41.2 test tests/e2e/playwright
```

