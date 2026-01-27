# RUNBOOK: Payment Webhook Management

**Last Updated**: 2025-01-26  
**Status**: Operational  
**Owner**: Payments Team

## Overview

Anka processes payment notifications from **Iyzico** via webhooks. Webhook events trigger transactions, disputes, and refund processing. There is **no frontend UI** for webhook management - all operations are performed via backend API and manual database queries.

## Webhook Event Types

| Event | Handler | Action |
|-------|---------|--------|
| `payment.completed` | `_handle_payment_completed()` | Create transaction, update credits |
| `payment.failed` | `_handle_payment_failed()` | Mark failed, notify organization |
| `payment.refunded` | `_handle_payment_refunded()` | Issue refund, reverse credits |

## Webhook Flow

```
Iyzico → POST /api/webhooks/payment/
   ↓
PaymentWebhook.create(event_type, payload)
   ↓
Process event based on type
   ↓
webhook.mark_processed()
   ↓
Return 200 OK to Iyzico
```

## Webhook Storage

All webhooks are stored in `payments_payment_webhook` table for audit trail:

```sql
SELECT id, event_type, conversation_id, processed, processed_at 
FROM payments_payment_webhook
ORDER BY created_at DESC
LIMIT 100;
```

## Common Tasks

### 1. Check Webhook Status

```bash
python manage.py shell
```

```python
from apps.payments.models import PaymentWebhook, PaymentTransaction

# Get unprocessed webhooks
pending = PaymentWebhook.objects.filter(processed=False)
print(f"Pending webhooks: {pending.count()}")

# Get failed webhooks
failed = PaymentWebhook.objects.filter(processing_error__isnull=False)
for wh in failed:
    print(f"Webhook {wh.id}: {wh.processing_error}")
```

### 2. Manually Retry Webhook

**Scenario**: A webhook failed but Iyzico won't resend.

```python
# Option A: Re-fetch from Iyzico API
from apps.payments.services import IyzicoClient

client = IyzicoClient()
payment = client.retrieve_payment(conversation_id='conv_123')
# ... manually create transaction from payment details

# Option B: Manual database modification
from apps.payments.models import PaymentTransaction, PaymentIntent

# Find the intent
intent = PaymentIntent.objects.get(id='intent_uuid')

# Create transaction manually
transaction = PaymentTransaction.objects.create(
    intent=intent,
    status='completed',
    external_payment_id='iyz_payment_123',
    amount_cents=10000,
    currency='TRY'
)

# Process it like normal
from apps.credits.models import Credit
Credit.objects.create(
    organization=intent.organization,
    amount=intent.credits_to_purchase,
    source='payment',
    source_id=str(transaction.id)
)
```

### 3. Investigate Webhook Failure

```python
# Get the webhook
wh = PaymentWebhook.objects.get(id='webhook_id_uuid')

# Check payload
print(wh.payload)  # Full Iyzico event

# Check error
print(wh.processing_error)  # Error message

# Check related transaction
tx = PaymentTransaction.objects.filter(
    external_payment_id=wh.payload['data']['paymentId']
).first()

if tx:
    print(f"Transaction status: {tx.status}")
else:
    print("No transaction created - webhook failed before creation")
```

### 4. Check Organization's Payments

```python
from apps.payments.models import PaymentTransaction
from apps.accounts.models import Organization

org = Organization.objects.get(slug='example-org')

transactions = PaymentTransaction.objects.filter(
    intent__organization=org
).order_by('-created_at')

for tx in transactions:
    print(f"{tx.created_at}: {tx.amount_cents/100} {tx.currency} - {tx.status}")
```

### 5. Emergency: Disable Webhooks

If webhooks are causing cascading failures:

```python
# Set flag in Django shell
from django.conf import settings

# Option 1: Temporarily mark webhooks as "processed" to skip them
from apps.payments.models import PaymentWebhook

PaymentWebhook.objects.filter(processed=False).update(
    processed=True,
    processing_error='Disabled during incident'
)
```

Then contact Iyzico support to temporarily disable webhook delivery.

## Monitoring

### Production Alerts

Set up alerts for:
1. **Webhook processing errors**: `PaymentWebhook.processing_error` is not null
2. **Unprocessed webhooks**: `PaymentWebhook.processed = False` for >5 minutes
3. **Missing transactions**: Webhook processed but no `PaymentTransaction` created

### Dashboard Query

```sql
-- Daily webhook health
SELECT 
    DATE(created_at) as date,
    event_type,
    COUNT(*) as total,
    SUM(CASE WHEN processing_error IS NOT NULL THEN 1 ELSE 0 END) as errors,
    SUM(CASE WHEN processed=FALSE THEN 1 ELSE 0 END) as pending
FROM payments_payment_webhook
WHERE created_at > NOW() - INTERVAL 7 days
GROUP BY DATE(created_at), event_type
ORDER BY date DESC;
```

## Troubleshooting

### "Webhook processed but transaction not found"

**Cause**: Payment was successful but transaction creation failed mid-process

**Fix**:
1. Get the webhook payload: `wh = PaymentWebhook.objects.get(id='...')`
2. Extract `conversation_id` and check Iyzico API
3. Create transaction manually (see "Manually Retry Webhook" section)

### "Duplicate transaction created"

**Cause**: Webhook retried by Iyzico, handler ran twice

**Fix**: Check by `external_payment_id`:

```python
from apps.payments.models import PaymentTransaction

# Find duplicates
payments = PaymentTransaction.objects.values('external_payment_id').filter(
    external_payment_id__isnull=False
).annotate(Count('id')).filter(id__count__gt=1)

# Delete duplicates (keep the first)
for dup in payments:
    txs = PaymentTransaction.objects.filter(
        external_payment_id=dup['external_payment_id']
    ).order_by('created_at')
    for tx in txs[1:]:  # Keep first, delete rest
        # Reverse credits first
        tx.delete()
```

## Contacts

- **Iyzico Support**: support@iyzico.com
- **Payment Team Lead**: [Name]
- **On-Call**: Check Opsgenie schedule

## See Also

- Payments Architecture: `/docs/ARCHITECTURE.md`
- Iyzico Integration: `/services/backend/apps/payments/clients.py`
- Webhook Models: `/services/backend/apps/payments/models.py`

