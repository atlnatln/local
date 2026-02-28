# ADR-0002: Ledger ve Kredi Modeli (Minimal + İdempotent)

**Status:** Accepted  
**Date:** 2025-Q4 (2026-02 revizyonu)

## Karar

Finansal hareketler `ledger_ledger_entry` üzerinde tutulur ve her iş olayı tekil referansla idempotent işlenir:

- `transaction_type`: `purchase | spent | refund`
- `reference_type`: `batch | payment | dispute`
- Tekillik: `ledger_unique_reference` (`reference_type`, `reference_id`)

Kullanıcı bakiyesi `CreditPackage` üzerinde tutulur; ledger kayıtları audit izi olarak korunur.

## Gerekçe

- Çift kayıt riskini DB seviyesinde engellemek
- Purchase/spent/refund akışını tek modelde izlemek
- Bakiye ve işlem geçmişini operasyonel olarak denetlenebilir tutmak

## Uygulama Notları (Güncel)

- Model: `services/backend/apps/ledger/models.py`
- Payment tamamlandığında kredi yansıması: `services/backend/apps/payments/signals.py`
- Batch settlement/refund akışı: `services/backend/apps/batches/services.py`
- Dispute kabulünde iade kaydı: `services/backend/apps/disputes/views.py`

## Sonuç

- İdempotency garantisi DB constraint + atomic güncellemelerle sağlanır.
- Aynı iş için tekrar çağrı geldiğinde ikinci ledger kaydı oluşmaz.
