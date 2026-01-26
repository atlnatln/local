# ADR-0004: Otomatik Uyuşmazlık Çözüm Kuralları (MVP-0)

**Status:** Accepted  
**Date:** 2025-Q4 (MVP-0 Dispute Module)  
**Context:** Müşteriler firma verilerinin yanlış/eski olduğunu şikayet edebilir. MVP-0'da manual inceleme yok; kurallar otomatik karar verir.

---

## Karar

Uyuşmazlık otomatik olarak **ACCEPT** (iade) veya **REJECT** (reddedildi) olur:

```python
# apps/disputes/models.py
class DisputeAutoResolver:
    """MVP-0: No manual review. Auto-resolve based on rules."""
    
    @staticmethod
    def resolve(dispute: Dispute) -> str:
        """Return 'accept' or 'reject'."""
        
        # RULE 1: Email hard bounce (SMTP error)
        if dispute.email_hard_bounce:
            return 'accept'  # Firma e-mailinde sorun var
        
        # RULE 2: Phone validation negative
        if dispute.phone_validation == 'wrong_firm':
            return 'accept'  # "Bu firma için değil" cevabı
        
        # RULE 3: Firm closed/inactive
        if dispute.firm_closed or dispute.firm_inactive:
            return 'accept'  # Firma kapalı
        
        # RULE 4: Duplicate batch
        if dispute.duplicate_batch:
            return 'accept'  # Zaten verilmiş
        
        # DEFAULT: Reject (insufficient evidence)
        return 'reject'
```

---

## Mantık

### Neden Otomatik Çözüm?
1. **Speed:** Manual review = delays, customer frustration
2. **Cost:** Manual review resources (MVP-0 limitation)
3. **Fairness:** Kurallar transparent, consistent
4. **Scalability:** İlerde manual review eklenebilir (v1+)

### Neden ACCEPT > REJECT?
- **ACCEPT:** Data quality issue (provider/field problem)
  - Email bounce = firma iletişim yöntemi hatalı
  - Phone validation = firma kimliği hatalı
  - Firm closed = firma artık yok
  
- **REJECT:** Veri doğru olabilir, talep exaggerated
  - "Yanlış versiyon" (old data) = user expectation ≠ data age guarantee
  - "Satış sonuç yok" (no sales) = data ≠ sales outcome guarantee

---

## İmplementasyon

### Dispute Dosyalama
```python
# apps/disputes/views.py — DisputeViewSet.create()
class DisputeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        dispute = super().create(validated_data)
        
        # Auto-resolve
        resolution = DisputeAutoResolver.resolve(dispute)
        dispute.status = resolution
        dispute.resolved_at = timezone.now()
        dispute.resolved_by = 'auto_rule'
        dispute.save()
        
        # If ACCEPT, refund credits
        if resolution == 'accept':
            refund_batch_credits(dispute.batch)
            logger.info(f"Dispute {dispute.id} accepted → refunded batch {dispute.batch.id}")
        else:
            logger.info(f"Dispute {dispute.id} rejected → user can appeal")
        
        return dispute
```

### Refund İşlemi (ACCEPT Durumu)
```python
def refund_batch_credits(batch: Batch):
    """Add refund ledger entry."""
    ledger_entry = LedgerEntry.objects.create(
        organization=batch.organization,
        transaction_type='refund',
        amount=batch.cost,  # Positive: credit back
        reference_type='batch',
        reference_id=str(batch.id),
    )
    
    # Update balance
    CreditBalance.recalculate(batch.organization.id)
```

---

## Kurallar Detayları

| Kural | Trigger | Karar | Reason |
|------|---------|--------|--------|
| Email Hard Bounce | SMTP 550/5xx return | ACCEPT (refund) | Firma iletişim yöntemi hatalı |
| Phone Validation | "Bu firma için değil" | ACCEPT (refund) | Wrong identity |
| Firm Closed | Tax authority KATICAK | ACCEPT (refund) | Firma artık yok |
| Duplicate | Same batch_id 2. dispute | ACCEPT (refund) | İçeriği tekrar mı? |
| Old Data | "Data 6 aydan eski" | REJECT | Veriler yaşa guarantee yok |
| No Sales | "Satış sonuç yok" | REJECT | Data ≠ sales conversion |
| Other | (unmapped) | REJECT | Default: user burden |

---

## MVP-0 Limitations

- ❌ No manual review queue
- ❌ No dispute appeal process
- ❌ No partial refunds (all or nothing)
- ❌ No dispute history analytics

---

## v1+ Enhancements

- ✅ Add manual review workflow (support team)
- ✅ Appeal process (user can contest REJECT)
- ✅ Partial refunds (item-level?)
- ✅ Analytics dashboard (dispute patterns, refund rates)
- ✅ Rule machine learning (historical acceptance patterns)

---

## Test Cases

```python
# tests/disputes/tests/test_auto_resolver.py
✅ test_accept_on_email_hard_bounce
✅ test_accept_on_phone_validation_negative
✅ test_accept_on_firm_closed
✅ test_accept_on_duplicate_batch
✅ test_reject_on_old_data_complaint
✅ test_reject_on_no_sales_complaint
✅ test_refund_ledger_created_on_accept
✅ test_credit_balance_updated_on_refund
```

---

## İlgili Dosyalar

- `apps/disputes/models.py` — Dispute model + auto-resolver
- `apps/disputes/views.py` — Dispute creation + resolution
- `apps/disputes/serializers.py` — Dispute request/response schemas
- `tests/disputes/tests/test_auto_resolver.py` — Auto-resolution tests

---

## Referanslar

- [Rules Engine Pattern](https://en.wikipedia.org/wiki/Business_rules_engine)
- [Event-Driven Refunds](https://stripe.com/docs/refunds)
- [Dispute Lifecycle](https://stripe.com/docs/payments/disputes)
