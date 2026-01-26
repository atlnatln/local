# ADR-0003: Deterministic Batch ve Query Hash

**Status:** Accepted  
**Date:** 2025-Q4 (MVP-0 Batch Processing)  
**Context:** Aynı filtre/parametrelerle yapılan sorgular **aynı sonuç** vermeli ve tekrar hesaplanmamalı.

---

## Karar

**Query Hash = SHA256(city + sector + filters_json + sort_rule_version)**

```python
# apps/batches/models.py
class Batch(models.Model):
    organization = ForeignKey(Organization)
    query_hash = CharField(unique=True, db_index=True)  # Deterministic hash
    quantity = IntegerField()
    cost = DecimalField()
    # ... other fields
    
    @staticmethod
    def calculate_query_hash(city: str, sector: str, filters: dict, version: int = 1) -> str:
        """Deterministic SHA256 hash for query idempotency."""
        query_key = json.dumps({
            'city': city,
            'sector': sector,
            'filters': filters,
            'version': version,
        }, sort_keys=True)
        return hashlib.sha256(query_key.encode()).hexdigest()
```

---

## Mantık

### Neden Deterministic Hash?
1. **Caching:** Same hash = Same result set (reuse from previous batch)
2. **Cost Optimization:** Duplicate queries skip data provider calls
3. **Auditing:** Query parameters immutable (hash is proof)
4. **Performance:** O(1) lookup in Batch table via `query_hash` index

### Neden SHA256?
- ✅ Deterministic (same input → same output always)
- ✅ Collision-resistant (virtually impossible duplicates)
- ✅ Fast (< 1ms even for large filter JSON)
- ❌ No reversibility (can't extract original filters from hash)

---

## İmplementasyon

### Frontend'den Batch Oluşturma
```typescript
// services/frontend/app/(dashboard)/batch/new/page.tsx
async function createBatch(
  city: string,
  sector: string,
  filters: Record<string, any>,
  quantity: number,
) {
  const response = await post('/batches/', {
    city,
    sector,
    filters,
    quantity,
    // query_hash backend'de otomatik hesaplanır
  });
  return response;
}
```

### Backend'de Hash Hesaplama
```python
# apps/batches/views.py — CreateBatchViewSet.create()
class BatchCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Extract parameters
        city = validated_data.get('city')
        sector = validated_data.get('sector')
        filters = validated_data.get('filters', {})
        
        # Calculate hash
        query_hash = Batch.calculate_query_hash(city, sector, filters)
        
        # Check if batch with same hash exists
        existing_batch = Batch.objects.filter(
            query_hash=query_hash,
            organization=self.context['request'].user.organization
        ).first()
        
        if existing_batch:
            logger.info(f"Batch {existing_batch.id} already exists (same hash)")
            return existing_batch
        
        # Create new batch
        batch = Batch.objects.create(
            organization=self.context['request'].user.organization,
            query_hash=query_hash,
            **validated_data
        )
        return batch
```

---

## Sorunlar ve Çözümler

### Neden `query_hash`'ı Unique Constraint'le Yap?
- **Problem:** Concurrent requests aynı query_hash'e sahip iki batch yaratabilir
- **Çözüm:** `UNIQUE` constraint → 2. request `IntegrityError` alır
- **Pattern:** `get_or_create()` idiomatik kullanımı

### Version Numarasının Neden Olması?
- **Reason:** Provider API'lar güncellenirse filter semantiği değişebilir
- **Example:** City names, sector codes revize edildiğinde query results farklı olabilir
- **Solution:** Hash'e `version` ekle → eski cached results auto-invalidate

### Hash Collisions?
- **Risk:** SHA256 collision = 2^128 guessing (negligible)
- **Monitor:** `django-audit` ile hash collision attempts logl (hacking indicator)

---

## İlgili Dosyalar

- `apps/batches/models.py` — Batch model + hash calculation
- `apps/batches/serializers.py` — Batch creation serializer
- `apps/batches/views.py` — Batch creation with deduplication
- `tests/batches/tests/test_batch_deterministic_hash.py` — Hash collision tests

---

## Referanslar

- [Idempotency Pattern](https://stripe.com/docs/api/idempotent_requests)
- [Deterministic Caching](https://www.postgresql.org/docs/14/indexes-unique.html)
- [SHA256 Hashing](https://en.wikipedia.org/wiki/SHA-2)
