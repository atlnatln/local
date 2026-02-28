# ADR-0004: Otomatik Dispute Karar Kuralları (v1)

**Status:** Accepted  
**Date:** 2025-Q4 (2026-02 revizyonu)

## Karar

Dispute kayıtları `evidence_data` içeriğine göre otomatik değerlendirilir (`accept` / `reject`).

Kural değerlendirmesi:
- `apps/disputes/rule_engine.py::DecisionEngine`

Dispute oluşturma akışında karar verilip kayıt anında `resolved` durumuna alınır:
- `apps/disputes/views.py::DisputeViewSet.perform_create`

## Kural Seti (Güncel)

Accept örnekleri:
- `email_bounce`
- `phone_invalid`
- `firm_inactive`
- `duplicate`

Reject örnekleri:
- `no_response`
- `wrong_person`

Varsayılan:
- Eşleşmeyen veri `reject` (`DEFAULT_REJECT`)

## İade Modeli

- `accept` kararı çıkarsa dispute item sayısı kadar kredi iadesi uygulanır.
- İade, `CreditPackage` ve `LedgerEntry(transaction_type='refund', reference_type='dispute')` üzerinden atomic şekilde işlenir.

## Sonuç

- Manuel kuyruk olmadan hızlı ve tutarlı ilk karar sağlanır.
- Karar kodları (`decision_reason_code`) ile audit izi korunur.
