# RUNBOOK: Payment Webhook Management

**Last Updated**: 2026-02-28  
**Status**: Operational

## Kapsam

Iyzico webhook’larının alınması, işlenmesi ve arıza durumunda temel müdahale adımları.

## Güncel Endpoint ve Akış

- Endpoint: `POST /api/payments/webhooks/iyzico/`
- Kod: `services/backend/apps/payments/webhooks.py`

Akış:
1. İmza doğrulama (`IYZICO_WEBHOOK_SECRET` varsa zorunlu)
2. `PaymentWebhook` kaydı oluşturma (audit)
3. Event’e göre handler çağrısı
4. Başarılıysa `processed=True`

## Desteklenen Event Tipleri

- `payment.completed`
- `payment.failed`
- `payment.refunded`

## Hızlı Teşhis (Django Shell)

```bash
cd services/backend
python manage.py shell
```

```python
from apps.payments.models import PaymentWebhook, PaymentIntent, PaymentTransaction

pending = PaymentWebhook.objects.filter(processed=False).count()
errored = PaymentWebhook.objects.filter(processing_error__isnull=False).count()
print({'pending': pending, 'errored': errored})

recent = PaymentWebhook.objects.order_by('-received_at')[:20]
for wh in recent:
    print(wh.received_at, wh.event_type, wh.conversation_id, wh.processed)
```

## Operasyon Notları

- `payment.completed` sonrası kredi yansıması webhook dosyasında değil, `payments/signals.py` içindeki `post_save(PaymentIntent)` ile yapılır.
- Aynı ödemenin tekrar işlenmesini önlemek için transaction tarafında ödeme kimlikleri (`iyzico_payment_id`, `iyzico_transaction_id`) tekillik kontrolleri vardır.

## Sık Sorunlar

1. **401 Invalid webhook signature**
   - `IYZICO_WEBHOOK_SECRET` değerini ve Iyzico tarafındaki secret eşleşmesini kontrol edin.

2. **Webhook geldi ama intent bulunamadı**
   - `conversationId` ile `PaymentIntent.conversation_id` eşleşmesini kontrol edin.

3. **Refund event sonrası durum tutarsız**
   - İlgili `PaymentTransaction` kaydında `iyzico_payment_id` var mı kontrol edin.

## İlgili Dosyalar

- `services/backend/apps/payments/models.py`
- `services/backend/apps/payments/webhooks.py`
- `services/backend/apps/payments/signals.py`
- `docs/RUNBOOKS/payments-webhook-replay.md`

