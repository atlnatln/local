# ADR-0002: Minimal Ledger Design (SADE Prensibi)

**Status:** Accepted  
**Date:** 2025-Q4 (MVP-0 Financial Module)  
**Context:** Batch'ler için finansal işlemleri takip etmek gerekiyor (satın alma, harcama, iade).

---

## Karar

**Ledger = 1 Row Per Batch Event (SADE: Single Atomic Database Entry)**

```python
# apps/ledger/models.py
class LedgerEntry(models.Model):
    organization = ForeignKey(Organization)
    transaction_type = CharField(
        choices=[
            ('purchase', 'Credit purchase (payment)'),
            ('spent', 'Batch retrieval (data access)'),
            ('refund', 'Dispute refund'),
        ]
    )
    amount = DecimalField()  # Positive: in, Negative: out
    reference_type = CharField(default='batch')  # 'batch', 'payment'
    reference_id = CharField()  # batch.id veya payment.id
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['reference_type', 'reference_id'],
                name='ledger_unique_reference'
            ),
        ]
```

---

## Mantık

### Neden SADE?
1. **Atomicity:** 1 batch = 1 ledger satırı → atomic transaction
2. **Auditability:** Her batch'in finansal imzası kaydedilir
3. **Query Performance:** No N+1 queries, simple aggregates
4. **Uniqueness:** Duplicate entries DB constraint tarafından bloke edilir

### Neden Satır Başına Batch Değil N Satır?
- ❌ (Yanlış) Batch'in her item'ı için ledger satırı → DB overload, complex joins
- ✅ (Doğru) Batch'in toplamı 1 satır → clean, auditable, unique

---

## İmplementasyon

### Batch Oluşturulduğunda
```python
# apps/batches/views.py — CreateBatchViewSet.create()
batch = Batch.objects.create(
    organization=org,
    query_hash=calculate_query_hash(filters),
    quantity=quantity,
    cost=calculate_batch_cost(quantity),
)

# Ledger entry (idempotent)
ledger_entry, created = LedgerEntry.objects.get_or_create(
    reference_type='batch',
    reference_id=str(batch.id),
    defaults={
        'organization': org,
        'transaction_type': 'spent',
        'amount': batch.cost,
    }
)

if created:
    logger.info(f"Ledger entry created for batch {batch.id}")
```

### Balans Projection (Read Model)
```python
# apps/credits/models.py
class CreditBalance(models.Model):
    organization = OneToOneField(Organization, primary_key=True)
    balance = DecimalField(default=0)  # Denormalized, refreshed on transaction
    
    @classmethod
    def recalculate(cls, org_id):
        """Ledger entries'den balance hesapla (eventual consistency)."""
        ledger_sum = LedgerEntry.objects\
            .filter(organization_id=org_id)\
            .aggregate(total=Sum('amount'))['total'] or 0
        
        cls.objects.update_or_create(
            organization_id=org_id,
            defaults={'balance': ledger_sum}
        )
```

---

## Sorunlar ve Çözümler

### Race Condition (Duplicate Batch Ledger Entries)
- **Problem:** İki concurrent request aynı batch için ledger yaratabilir
- **Çözüm:** DB unique constraint + `get_or_create()` (atomic at DB level)
- **Test:** `test_batch_create_duplicate_ledger_rolls_back_when_constraint_violation`

### Idempotency
- **Problem:** İstemci retrylerse duplicate entries oluşur
- **Çözüm:** `get_or_create()` semantiği (same input → same output)
- **Test:** `test_ledger_entry_creation_retries_on_integrity_error`

---

## İlgili Dosyalar

- `apps/ledger/models.py` — Model + constraints
- `apps/batches/views.py` — Ledger creation logic
- `apps/ledger/migrations/0002_ledgerentry_ledger_unique_reference.py` — DB constraint
- `tests/batches/tests/test_batch_ledger_atomic.py` — 10+ test cases

---

## Referanslar

- [Double-Entry Bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Django Transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
