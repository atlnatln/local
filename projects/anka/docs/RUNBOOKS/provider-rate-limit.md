# Runbook: Provider Rate Limit (Google Places)

Amaç: Google Places çağrılarında `429`/`5xx` kaynaklı yavaşlama veya başarısızlık olduğunda hızlı teşhis ve güvenli toparlama.

## Kapsam

Bu repo için ana provider akışı Google Places üzerindedir:
- İstemci: `services/backend/apps/providers/google_places.py`
- Pipeline: `services/backend/apps/batches/services.py`
- Stage’ler: `COLLECTING_IDS`, `FILTERING`, `ENRICHING_CONTACTS`

## 1) Belirtiyi Doğrula

```bash
# Docker dev örneği
docker compose logs -f backend | grep -Ei "429|rate limit|quota|google places|Server Error"
```

Özellikle şu pattern’ler önemlidir:
- `Rate limited (429). Retrying ...`
- `Server Error 5xx. Retrying ...`
- `Stage 1 API cap reached`

## 2) Sistem Davranışını Bil

`GooglePlacesClient._make_request` davranışı:
- `429`: exponential backoff + retry
- `5xx`: retry
- `404`: business miss (kayıt yok)
- `400/403`: fail-fast (konfigürasyon/izin sorunu)

Pipeline güvenlik limitleri:
- `ANKA_BATCH_MAX_RECORDS` (default `50`)
- `ANKA_STAGE1_MAX_API_CALLS` (default `20`)
- `ANKA_STAGE2_MAX_API_CALLS` (default `80`)
- `ANKA_STAGE3_MAX_API_CALLS` (default `80`)

## 3) Hızlı Müdahale

1. Aynı anda açılan batch sayısını düşür.
2. Gerekirse geçici olarak stage cap değerlerini aşağı çek.
3. Provider tarafı normale dönünce limitleri eski haline getir.

Örnek (prod env):

```env
ANKA_STAGE1_MAX_API_CALLS=10
ANKA_STAGE2_MAX_API_CALLS=40
ANKA_STAGE3_MAX_API_CALLS=40
```

## 4) Kök Neden Kontrolü

- API key doğru projeye bağlı mı?
- Places API (New) ilgili metotlar açık mı?
- Quota dolumu veya ani trafik artışı var mı?
- Aynı batch için tekrar deneme döngüsü oluşmuş mu?

## 5) Sonuç Doğrulama

Başarılı toparlamada:
- Yeni batch’ler `FAILED` yerine `READY`/`PARTIAL` ilerler.
- `429` log yoğunluğu düşer.
- Stage metrikleri (`ids_collected`, `ids_verified`, `contacts_enriched`) tekrar artar.

## Operasyonel Komutlar

```bash
# Son batch durumları
docker compose exec -T backend python manage.py shell -c "
from apps.batches.models import Batch
for b in Batch.objects.order_by('-created_at')[:20]:
    print(b.id, b.status, b.ids_collected, b.ids_verified, b.contacts_enriched)
"
```

## İlgili Kaynaklar

- `docs/RUNBOOKS/maps-query-logic-pipeline.md`
- `services/backend/apps/providers/google_places.py`
- `services/backend/apps/batches/services.py`
