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

### 2. Celery Task Log'unu Kontrol Et

```bash
# Celery worker log'unda exception
docker compose logs -f celery_worker | grep -i "export\|error"

# Task ID'ye göre detay
docker compose exec -T backend python manage.py shell

from celery.result import AsyncResult

task = AsyncResult('task_id_xxxxx')
print(f"Status: {task.status}")
print(f"Result: {task.result}")  # Exception message
print(f"Traceback: {task.traceback}")
```

### 3. Ortak Sorunlar ve Çözümler

#### Sorun: Memory Limit (Large Batch)
```
MemoryError: export_to_xlsx ran out of memory
```

**Çözüm:** Batch chunk'lara böl
```python
# apps/exports/tasks.py
@app.task(bind=True)
def export_batch_to_file(self, export_job_id):
    export_job = ExportJob.objects.get(id=export_job_id)
    batch = export_job.batch
    
    # Chunk by 10,000 items
    chunk_size = 10_000
    items = batch.items.all()
    
    for i in range(0, items.count(), chunk_size):
        chunk = items[i:i+chunk_size]
        # Process chunk
        write_chunk_to_file(export_job, chunk)
```

#### Sorun: S3/MinIO Connection Timeout
```
TimeoutError: MinIO connection timeout
```

**Çözüm:** Retry + exponential backoff
```python
from celery import app
import time

@app.task(bind=True, autoretry_for=(TimeoutError,), retry_kwargs={'max_retries': 3})
def upload_to_s3(self, file_path):
    try:
        s3_client.upload_file(file_path, bucket, key)
    except TimeoutError as e:
        # Celery auto-retry with backoff
        raise self.retry(exc=e, countdown=2**self.request.retries)
```

#### Sorun: Database Lock (Concurrent Exports)
```
DatabaseError: could not serialize access due to concurrent update
```

**Çözüm:** Select for update (pessimistic locking)
```python
from django.db import transaction

with transaction.atomic():
    export_job = ExportJob.objects.select_for_update().get(id=job_id)
    # No concurrent modifications while locked
```

#### Sorun: File System Full
```
OSError: No space left on device
```

**Çözüm:** Stream to S3 instead of temp file
```python
import io
from minio import Minio

# Create in-memory buffer
buffer = io.BytesIO()
write_xlsx(batch.items, buffer)
buffer.seek(0)

# Stream directly to MinIO
minio_client.put_object(
    'exports',
    f'{export_job.id}.xlsx',
    buffer,
    length=buffer.getbuffer().nbytes
)
```

### 4. Job'u Retry Et

```python
# Django shell
from apps.exports.models import ExportJob
from apps.exports.tasks import export_batch_to_file

job = ExportJob.objects.get(id=job_id)
job.status = 'pending'
job.error_message = None
job.save()

# Celery task'ı yeniden kuyruğa koy
task = export_batch_to_file.delay(job.id)
print(f"Retry started: Task ID {task.id}")
```

### 5. Progress Izleme

```python
# Django shell - realtime progress
from apps.exports.models import ExportJob

job = ExportJob.objects.get(id=job_id)

while job.status not in ['completed', 'failed']:
    job.refresh_from_db()
    print(f"Status: {job.status}")
    print(f"Progress: {job.progress}%")
    print(f"Items processed: {job.items_processed}/{job.total_items}")
    
    import time
    time.sleep(5)

print(f"Final status: {job.status}")
if job.status == 'completed':
    print(f"Signed URL: {job.signed_url}")
```

---

## Debug İçin Lokal Test

```bash
# Docker container'da Celery worker'ı single-threaded mode'da çalıştır
docker compose run --rm celery_worker celery -A celery_app worker --loglevel=debug --concurrency=1

# Ayrı terminal'de Django shell'den test task'ı gönder
docker compose exec -T backend python manage.py shell

from apps.exports.models import ExportJob, Batch
from apps.exports.tasks import export_batch_to_file

# Test export
batch = Batch.objects.first()
job = ExportJob.objects.create(
    batch=batch,
    organization=batch.organization,
    export_format='xlsx',
    created_by=batch.organization.owner
)

# Synchronously çalıştır (debug)
export_batch_to_file(job.id)
```

---

## Monitoring ve Alerting

### Celery Flower Dashboard
```bash
# http://localhost:5555 (Flower)
docker-compose up -d flower

# Task history ve performance metrics
```

### Log Aggregation
```bash
# Recent errors
docker compose logs --tail 100 celery_worker | grep -i "error\|exception"

# Export-specific logs
docker compose logs --tail 50 backend | grep -i "export"
```

---

## Kontrol Listesi

- [ ] Başarısız job'u buldum
- [ ] Celery task log'unu kontrol ettim
- [ ] Hata nedeni tespit ettim (memory, timeout, lock, space vb.)
- [ ] Uygun çözümü uyguladım
- [ ] Job'u retry ettim
- [ ] Progress izledim
- [ ] Sonuç doğrulandı (signed URL, file size)
- [ ] Logs'da cleanup yapıldı (debug artifacts)

---

## İletişim

- **Celery logs:** `docker compose logs celery_worker`
- **Backend logs:** `docker compose logs backend | grep export`
- **Database:** `docker compose exec -T backend python manage.py dbshell`
- **Support:** GitHub Issues
