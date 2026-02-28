# Runbook: Iyzico Webhook Replay

Amaç: Iyzico webhook olayı kaçırıldığında veya işleme hatası oluştuğunda güvenli tekrar işleme prosedürü.

## Kapsam ve Gerçek Akış

- Webhook endpoint: `POST /api/payments/webhooks/iyzico/`
- Handler: `services/backend/apps/payments/webhooks.py`
- Audit modeli: `apps.payments.models.PaymentWebhook`
- İşlenen event tipleri:
  - `payment.completed`
  - `payment.failed`
  - `payment.refunded`

Not: Bu projede Stripe tabanlı webhook modeli yoktur; replay yalnız Iyzico akışı içindir.

## 1) Olayı Tespit Et

```bash
cd services/backend
python manage.py shell
```

```python
from apps.payments.models import PaymentWebhook

failed = PaymentWebhook.objects.filter(processing_error__isnull=False).order_by('-received_at')[:20]
for wh in failed:
    print(wh.id, wh.event_type, wh.conversation_id, wh.processed, wh.processing_error)
```

## 2) Replay Stratejisi Seç

### Tercih edilen: Provider tarafında yeniden gönderim

- Iyzico panelinden ilgili event tekrar gönderilir.
- Böylece imza doğrulama ve gerçek payload ile aynı üretim yolu kullanılır.

### Alternatif: Manuel düzeltme (yalnız zorunlu durumda)

- `conversation_id` üzerinden `PaymentIntent` bulunur.
- Gerekli alanlar (`status`, `payment_id`) dikkatle güncellenir.
- Gerekirse `PaymentTransaction` kaydı kontrol edilir.

## 3) Replay Sonrası Doğrulama

```python
from apps.payments.models import PaymentIntent, PaymentTransaction, PaymentWebhook

cid = 'CONVERSATION_ID'

print('webhooks:')
for wh in PaymentWebhook.objects.filter(conversation_id=cid).order_by('-received_at')[:5]:
    print(wh.received_at, wh.event_type, wh.processed, wh.processing_error)

intent = PaymentIntent.objects.filter(conversation_id=cid).first()
print('intent:', intent.id if intent else None, intent.status if intent else None, intent.payment_id if intent else None)

txs = PaymentTransaction.objects.filter(iyzico_conversation_id=cid).order_by('-created_at')
print('tx_count=', txs.count())
for tx in txs[:5]:
    print(tx.id, tx.status, tx.iyzico_payment_id, tx.iyzico_transaction_id)
```

## 4) Güvenlik ve İdempotency Kontrolleri

- Aynı ödeme için mükerrer transaction oluşmamalı (`iyzico_payment_id` / `iyzico_transaction_id` tekillikleri).
- `PaymentWebhook.processing_error` temizlenmeden önce kök neden not edilmeli.
- Replay sırasında doğrudan DB manipülasyonu gerekiyorsa transaction içinde çalışılmalı.

## 5) Sık Sorunlar

1. `401 Invalid webhook signature`
   - `IYZICO_WEBHOOK_SECRET` ve Iyzico tarafı secret eşleşmiyor olabilir.

2. `Payment intent not found for conversation`
   - Webhook payload içindeki `conversationId` ile sistemdeki `PaymentIntent.conversation_id` eşleşmiyor olabilir.

3. `processed=True` ama finansal etki yok
   - `PaymentIntent`, `PaymentTransaction` ve ledger kayıtları birlikte kontrol edilmelidir.

## İlgili Kaynaklar

- `docs/RUNBOOKS/payments-webhook-management.md`
- `services/backend/apps/payments/webhooks.py`
- `services/backend/apps/payments/models.py`
- `services/backend/apps/payments/signals.py`
