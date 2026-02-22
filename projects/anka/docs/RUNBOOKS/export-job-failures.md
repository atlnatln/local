# Runbook: Export İş Başarısızlıkları Tanı ve Çözüm

**Amaç:** CSV/XLSX export job'ları başarısız olduğunda tanı koyup çözmek.

---

## Ön Koşullar

- Docker stack çalışıyor: `./dev-docker.sh` ✅
- Celery worker çalışıyor: `docker compose logs -f celery_worker`
- Redis erişimi var
- S3/MinIO erişimi var

---

## Adımlar

### 1. Başarısız Job'ları Tespit Et

```bash
# Django shell
docker compose exec -T backend python manage.py shell

from apps.exports.models import ExportJob
from django.utils import timezone

# Son 24 saatteki başarısız joblar
failed_jobs = ExportJob.objects.filter(
    status='failed',
    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
).order_by('-created_at')

for job in failed_jobs:
    print(f"Job ID: {job.id}")
    print(f"Organization: {job.organization.name}")
    print(f"Format: {job.export_format}")  # csv, xlsx
    print(f"Error: {job.error_message}\n")
```

# Runbook: Export İş Başarısızlıkları Tanı ve Çözüm

Amaç: CSV/XLSX export üretiminde sorun olduğunda kök nedeni hızlı bulup güvenli şekilde düzeltmek.

## Güncel Mimari
- Model: `apps.exports.models.Export`
- Task: `apps.exports.tasks.generate_export_file`
- Tetikleme:
  - `BatchProcessor` READY olduğunda CSV ve XLSX export otomatik kuyruğa alınır.
  - `POST /api/exports/` çağrısı da export task'ını tetikler.
- Çıktı:
  - Dosya yolu: `/app/media/exports/{batch_id}/...`
  - Public URL: `https://ankadata.com.tr/media/...`
  - Batch alanları: `batch.csv_url`, `batch.xlsx_url`

## Hızlı Tanı Adımları

### 1) Başarısız export kayıtlarını bul
```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T backend \
python manage.py shell -c "
from apps.exports.models import Export
for e in Export.objects.filter(status='failed').order_by('-created_at')[:20]:
    print(e.id, e.format, e.batch_id, e.error_message)
"
```

### 2) Worker loglarında export hatasını doğrula
```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail 200 celery_worker | grep -i "export\|traceback\|error"
```

### 3) Batch URL alanları güncellenmiş mi kontrol et
```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T backend \
python manage.py shell -c "
from apps.batches.models import Batch
b = Batch.objects.get(id='BATCH_ID')
print('csv_url=', b.csv_url)
print('xlsx_url=', b.xlsx_url)
"
```

## Sık Sorunlar ve Çözümler

### Sorun: Export `failed`, `error_message` boş değil
Neden:
- Desteklenmeyen format
- Dosya sistemi izin/hacim problemi
- Veri satırı hazırlanırken beklenmeyen tip

Çözüm:
1. `error_message` değerini al.
2. `services/backend/apps/exports/tasks.py` ilgili branch'i kontrol et.
3. Düzeltme sonrası export'u `pending` yapıp yeniden kuyrukla.

### Sorun: Batch READY ama “Dosyalar hazırlanıyor...” uzun süre kalıyor
Neden:
- Celery worker çalışmıyor
- Export kaydı oluşmamış
- Export processing'te takılmış

Çözüm:
1. Worker health kontrol et.
2. `Export` kayıtlarını batch bazında filtrele.
3. Gerekirse `generate_export_file.delay(export_id)` ile manuel tetikle.

## Güvenli Retry Prosedürü
```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T backend \
python manage.py shell -c "
from apps.exports.models import Export
from apps.exports.tasks import generate_export_file

e = Export.objects.get(id='EXPORT_ID')
e.status='pending'
e.error_message=''
e.save(update_fields=['status','error_message','updated_at'])
generate_export_file.delay(str(e.id))
print('retry queued', e.id)
"
```

## Operasyonel Kontrol Listesi
- [ ] Hata veren `Export` kaydı tespit edildi
- [ ] `error_message` ve worker log'u incelendi
- [ ] Batch `csv_url/xlsx_url` alanları doğrulandı
- [ ] Retry güvenli şekilde tetiklendi
- [ ] Export `completed` + `file_size > 0` doğrulandı
- [ ] `/media/...` URL erişimi test edildi
# Stream directly to MinIO
