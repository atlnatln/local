# Runbook: Provider API Rate Limit Problemi Tanı ve Çözüm

**Amaç:** Dış veri provider API'larından rate limit hataları alınırsa sorunü tespit edip çözmek.

---

## Ön Koşullar

- Docker stack çalışıyor: `./dev-docker.sh` ✅
- Provider credentials `.env` dosyasında (test keys)
- Monitoring logs erişimi
- Redis erişimi (rate limit cache)

---

## Adımlar

### 1. Rate Limit Error'unu Tespit Et

```bash
# Backend log'unda rate limit error
docker compose logs -f backend | grep -i "rate.limit\|429\|quota"

# Veya Django shell
docker compose exec -T backend python manage.py shell

from apps.providers.models import ProviderCall
from django.utils import timezone

# Son 1 saatteki rate limit errors
rate_limit_errors = ProviderCall.objects.filter(
    status_code__in=[429, 503],  # Too Many Requests, Service Unavailable
    created_at__gte=timezone.now() - timezone.timedelta(hours=1)
)

for call in rate_limit_errors[:10]:
    print(f"Provider: {call.provider_name}")
    print(f"Status: {call.status_code}")
    print(f"Time: {call.created_at}")
    print(f"Error: {call.response_body[:200]}\n")

print(f"Total errors in last hour: {rate_limit_errors.count()}")
```

### 2. Rate Limit Politikasını Kontrol Et

```python
# Provider API doc'unda rate limit kuralları
# Örnek: Stripe
# - 100 requests/second (burst: 200/10s)
# - Daily limit: unlimited

# Veya Redis'te tracking
from django_ratelimit.backends import cache

# Current usage for provider
from apps.providers.models import ProviderAPIClient

provider = ProviderAPIClient.get('stripe')
rate_limit_info = provider.get_rate_limit_info()
print(f"Requests used: {rate_limit_info['used']}")
print(f"Requests limit: {rate_limit_info['limit']}")
print(f"Reset at: {rate_limit_info['reset_at']}")
```

### 3. Batch İşleme Hızını Azalt

```python
# Django shell - Queue'deki pending batch'leri kontrol et
from apps.batches.models import Batch

pending = Batch.objects.filter(status='pending').count()
print(f"Pending batches: {pending}")

# Celery task'ını throttle et
from apps.batches.tasks import fetch_batch_data

# Concurrent worker sayısını azalt (normally: 4)
# docker-compose.yml'de CELERYD_CONCURRENCY=1 olarak set et

# Veya kod içinde delay ekle
import time
for batch in pending_batches:
    task = fetch_batch_data.apply_async(
        args=[batch.id],
        countdown=5  # 5 saniye bekle, sonra işle
    )
```

### 4. Exponential Backoff Konfigürasyonunu Ayarla

```python
# apps/providers/client.py
import time

class ProviderAPIClient:
    MAX_RETRIES = 5
    BASE_BACKOFF = 1  # 1 second
    
    def request_with_retry(self, method, url, **kwargs):
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.request(method, url, **kwargs)
                if response.status_code == 429:
                    raise RateLimitError(response)
                return response
            
            except RateLimitError as e:
                if attempt < self.MAX_RETRIES - 1:
                    # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                    print(f"Rate limited. Retry in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
```

### 5. Cache-Based Rate Limiter Kur

```python
# Django settings: RATELIMIT_BACKENDS
from django_ratelimit.backends import CacheBackend

# .env veya settings.py
RATELIMIT_ENABLE = True
RATELIMIT_PROVIDERS = {
    'stripe': {
        'requests_per_second': 10,  # Local limit (lower than API)
        'burst_size': 20,
    },
    'iyzico': {
        'requests_per_second': 5,
        'burst_size': 10,
    }
}
```

```python
# apps/providers/client.py - decorator kullan
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/s', method='POST')
def create_batch_from_provider(request):
    # Yalnızca 10 request/second
    pass
```

### 6. Queue Yönetimi

```bash
# Celery queue'ü kontrol et
docker compose exec -T backend python -m celery -A celery_app inspect active

# Pending task'ları göster
docker compose exec -T backend python -m celery -A celery_app inspect reserved

# Queue'i temizle (zararlı: lose jobs!)
# docker compose exec -T backend python -m celery -A celery_app purge  # DANGER
```

```python
# Django shell - queue denetimi
from celery.app.control import Inspect

celery = Inspect()
active_tasks = celery.active()
print(f"Active tasks: {len(active_tasks)}")

# Long-running tasks'ı kapat
for worker, tasks in active_tasks.items():
    for task in tasks:
        if task['name'] == 'fetch_batch_data' and task['time_start'] > 3600:
            print(f"Long-running task: {task['id']}")
```

---

## Ortak Hatalar ve Çözümler

### Hata 1: 429 Too Many Requests (Kota Aşılmış)
```
HTTP 429 - Rate Limit Exceeded
Retry-After: 60
```

**Çözüm:** Retry logic + exponential backoff
- Otomatik retry 5 saniyeden başlayarak
- Her retry'da 2x bekle
- Max 5 retry = 31 saniye total

### Hata 2: 503 Service Unavailable (Provider Down)
```
HTTP 503 - Service Temporarily Unavailable
```

**Çözüm:** Healthcheck + fallback
```python
from apps.providers.healthcheck import check_provider_health

if not check_provider_health('stripe'):
    print("Provider temporarily down, queuing for later")
    # Queue task for 30 minutes later
    fetch_batch_data.apply_async(
        args=[batch.id],
        countdown=1800
    )
```

### Hata 3: Quota Exceeded (Günlük Limit Aşılmış)
```
HTTP 400 - Daily Quota Exceeded
```

**Çözüm:** Limit tracking + alerting
```python
from apps.providers.quota import track_quota_usage

usage = track_quota_usage('stripe')
if usage > 0.9:  # 90% quota used
    send_alert("Stripe quota 90% used. Daily reset at 00:00 UTC")
    # Pause non-critical batches
```

---

## Monitoring Dashboard

### Metrikleri İzle
```python
from django.db.models import Count
from apps.providers.models import ProviderCall

# Last hour stats by provider
from django.utils import timezone

hour_ago = timezone.now() - timezone.timedelta(hours=1)
stats = ProviderCall.objects\
    .filter(created_at__gte=hour_ago)\
    .values('provider_name')\
    .annotate(
        total=Count('id'),
        errors=Count('id', filter=Q(status_code__gte=400)),
        rate_limits=Count('id', filter=Q(status_code=429))
    )

for stat in stats:
    error_rate = (stat['errors'] / stat['total']) * 100
    print(f"{stat['provider_name']}:")
    print(f"  Total: {stat['total']}")
    print(f"  Error rate: {error_rate:.1f}%")
    print(f"  Rate limits: {stat['rate_limits']}\n")
```

### Alerting Rules
```python
# Django management command: monitor_provider_health
# Cronjob: every 5 minutes

from apps.providers.models import ProviderCall
from django.utils import timezone

for provider in ['stripe', 'iyzico']:
    errors_5min = ProviderCall.objects.filter(
        provider_name=provider,
        status_code__gte=400,
        created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
    ).count()
    
    if errors_5min > 10:
        send_slack_alert(
            f"⚠️ {provider}: {errors_5min} errors in last 5 min"
        )
```

---

## Kontrol Listesi

- [ ] Rate limit error'unu buldum
- [ ] Provider'ın rate limit politikasını kontrol ettim
- [ ] Current usage'ı kontrol ettim
- [ ] Queue'deki pending task'ları kontrol ettim
- [ ] Exponential backoff retry'ı trigger ettim
- [ ] Local rate limiter kurdum (provider limit'in altında)
- [ ] Queue'yi optimize ettim (concurrency azalt)
- [ ] Monitoring dashboard'u kurdum
- [ ] Alerting rules'ları test ettim

---

## İletişim

- **Provider API logs:** `docker compose logs backend | grep provider`
- **Celery task logs:** `docker compose logs celery_worker`
- **Rate limit metrics:** Django admin > Provider Calls
- **Support:** GitHub Issues veya team Slack
