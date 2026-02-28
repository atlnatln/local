# ADR-0003: Deterministik Batch Kimliği (`query_hash`)

**Status:** Accepted  
**Date:** 2025-Q4 (2026-02 revizyonu)

## Karar

Batch sorgu kimliği deterministik olarak hesaplanır:

`SHA256(city|sector|filters_json_sorted|sort_rule_version)`

Hash üretimi `Batch.calculate_query_hash()` içinde yapılır ve `save()` sırasında otomatik set edilir.

## Gerekçe

- Aynı sorgunun aynı kimlikle izlenmesi
- Pipeline, audit ve raporlama tarafında tekrar üretilebilirlik
- Farklı sort/filter semantiklerinin `sort_rule_version` ile ayrıştırılması

## Uygulama Notları (Güncel)

- Model: `services/backend/apps/batches/models.py`
- Determinizm için `json.dumps(..., sort_keys=True, separators=(',', ':'))` kullanılır.
- `query_hash` **unique değildir**; aynı sorgu farklı zamanlarda birden fazla batch olarak tutulabilir.

## Sonuç

- Aynı giriş parametreleri her zaman aynı hash’i üretir.
- Hash tek başına deduplikasyon garantisi değil, sorgu kimliği ve izlenebilirlik standardıdır.
