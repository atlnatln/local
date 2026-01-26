# Runbook: Webhook Tekrar Oynatma (Payment Replay)

**Amaç:** Stripe/Iyzico webhooks atlanmışsa veya başarısız olduysa manuel olarak tekrar işleme sokmak.

---

## Ön Koşullar

- Docker stack çalışıyor: `./dev-docker.sh` ✅
- PostgreSQL ve Redis aktif
- Stripe/Iyzico test credentials `.env` dosyasında

---

## Adımlar

### 1. Webhook Event'ini Tespit Et

```bash
# Docker container'a bağlan
docker compose exec -T backend python manage.py shell

# Django shell'de
from apps.payments.models import WebhookEvent
from django.utils import timezone

# Son X saatte başarısız webhooks
failed_events = WebhookEvent.objects.filter(
    status='failed',
    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
).order_by('-created_at')

for event in failed_events:
    print(f"Event ID: {event.external_id}")
    print(f"Type: {event.event_type}")
    print(f"Status: {event.status}")
    print(f"Error: {event.error_message}\n")
```

### 2. Webhook Payload'unu Kontrol Et

```bash
# Stripe CLI ile gerçek webhook payload'unu al
stripe events retrieve evt_xxxxx --format json

# Veya database'den
event = WebhookEvent.objects.get(external_id='evt_xxxxx')
print(event.payload)  # JSON stored in DB
```

### 3. Webhook'u Manuel Işle

```python
# Django shell'de
from apps.payments.views import StripeWebhookView

webhook_view = StripeWebhookView()
response = webhook_view.handle_webhook_event(
    event_type='charge.succeeded',
    event_data={
        'id': 'evt_xxxxx',
        'type': 'charge.succeeded',
        'data': {...}  # payload from Step 2
    )
)

print(f"Result: {response.status_code}")
print(f"Message: {response.data}")
```

### 4. Sonucu Doğrula

```python
# Payment status'unu kontrol et
from apps.payments.models import Payment

payment = Payment.objects.get(external_id='pi_xxxxx')
print(f"Status: {payment.status}")
print(f"Amount: {payment.amount}")
print(f"Updated at: {payment.updated_at}")

# Ledger entry oluştu mu?
from apps.ledger.models import LedgerEntry

ledger = LedgerEntry.objects.filter(
    reference_type='payment',
    reference_id=str(payment.id)
).first()

if ledger:
    print(f"Ledger created: {ledger.transaction_type} {ledger.amount}")
else:
    print("WARNING: No ledger entry found!")
```

### 5. Credit Balance Güncelle (Gerekirse)

```python
# Balance yeniden hesapla
from apps.credits.models import CreditBalance

for org in Organization.objects.all():
    CreditBalance.recalculate(org.id)
    print(f"Recalculated balance for {org.name}")
```

---

## Hata Senaryoları

### Senaryo 1: Webhook Tekrarı Duplicate Ledger Atması
```python
# Sorun: 2 kez webhook işlenirse 2 ledger entry oluşur
# Çözüm: Unique constraint koyar, 2. işlem IntegrityError verir

# Çözüm: get_or_create kullan
from apps.ledger.models import LedgerEntry

ledger, created = LedgerEntry.objects.get_or_create(
    reference_type='payment',
    reference_id=payment.external_id,
    defaults={'organization': org, 'amount': payment.amount, ...}
)

if not created:
    print(f"Webhook already processed (idempotent)")
```

### Senaryo 2: Stripe API Timeout
```python
# Sorun: Stripe'dan response alınamadı
# Çözüm: Retry mekanizması

import time

max_retries = 3
for attempt in range(max_retries):
    try:
        payment = stripe.PaymentIntent.retrieve('pi_xxxxx')
        break
    except stripe.error.APIConnectionError:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Retry in {wait_time}s...")
            time.sleep(wait_time)
        else:
            print("Max retries exceeded")
            raise
```

### Senaryo 3: Iyzico Callback Alamadı
```bash
# Iyzico webhook log'unu kontrol et
docker compose logs -f backend | grep -i "iyzico"

# Iyzico test dashboard'dan webhook history
# https://sandbox-merchant.iyzipay.com/webhooks
```

---

## Monitoring ve Logging

### Log Kontrol
```bash
# Webhook-related logs
docker compose logs -f backend | grep -i webhook

# Specific event
docker compose logs -f backend | grep evt_xxxxx
```

### Metrics
```python
from django.db.models import Count

# Webhook status distribution
status_counts = WebhookEvent.objects.values('status').annotate(count=Count('id'))
for status_row in status_counts:
    print(f"{status_row['status']}: {status_row['count']}")

# Failed webhooks by type
failed_by_type = WebhookEvent.objects.filter(
    status='failed'
).values('event_type').annotate(count=Count('id'))

for row in failed_by_type:
    print(f"{row['event_type']}: {row['count']} failures")
```

---

## Kontrol Listesi

- [ ] Docker stack çalışıyor
- [ ] Failed webhook event'ini buldum
- [ ] Payload DB veya Stripe'dan aldım
- [ ] Webhook'u manuel işledim
- [ ] Payment status'unu doğruladım
- [ ] Ledger entry oluştu mu kontrol ettim
- [ ] Credit balance güncel
- [ ] Logs'da error yok

---

## İletişim

- **Backend logs:** `docker compose logs -f backend`
- **Database:** `psql anka` (Docker container'da PostgreSQL)
- **Support:** GitHub Issues veya team Slack
