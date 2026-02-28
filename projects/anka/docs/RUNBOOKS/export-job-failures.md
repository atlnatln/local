# Runbook: Export Job Failures

Amaç: CSV/XLSX export üretiminde hata oluştuğunda teşhis, retry ve doğrulama adımlarını standartlaştırmak.

## Kapsam

- Model: `apps.exports.models.Export`
- Task: `apps.exports.tasks.generate_export_file`
- Watchdog: `apps.exports.tasks.monitor_stuck_exports_task`
- API: `POST /api/exports/` ve `GET /api/exports/`

## 1) Hata Kayıtlarını Bul

```bash
docker compose exec -T backend python manage.py shell -c "
from apps.exports.models import Export
for e in Export.objects.filter(status='failed').order_by('-created_at')[:20]:
    print(e.id, e.format, e.batch_id, e.error_message)
"
```

## 2) Worker Loglarını Kontrol Et

```bash
docker compose logs --tail 200 celery_worker | grep -Ei "export|traceback|error|retry"
```

## 3) Batch URL Alanlarını Doğrula

```bash
docker compose exec -T backend python manage.py shell -c "
from apps.batches.models import Batch
b = Batch.objects.get(id='BATCH_ID')
print('csv_url=', b.csv_url)
print('xlsx_url=', b.xlsx_url)
"
```

## 4) Güvenli Retry Prosedürü

```bash
docker compose exec -T backend python manage.py shell -c "
from apps.exports.models import Export
from apps.exports.tasks import generate_export_file

e = Export.objects.get(id='EXPORT_ID')
e.status = 'pending'
e.error_message = ''
e.save(update_fields=['status','error_message','updated_at'])
generate_export_file.delay(str(e.id))
print('retry queued', e.id)
"
```

## 5) Sistem Davranışı (Bilmen Gerekenler)

- Task otomatik retry yapar: `2m -> 4m -> 8m`.
- Son denemede de başarısız olursa export `failed` olur ve alarm üretilir (`EXPORT_FAILED`).
- `monitor_stuck_exports_task`, `processing` durumunda SLA’yı aşan kayıtları `failed` yapar (`EXPORT_SLA_EXCEEDED`).
- Başarıda:
  - `Export.signed_url` üretilir
  - `Batch.csv_url` veya `Batch.xlsx_url` güncellenir

## 6) Sık Nedenler

1. Desteklenmeyen format veya bozuk satır verisi
2. Dosya yazma yolu/izin problemi (`MEDIA_ROOT`)
3. Worker kesintisi (task `processing`de kalır)
4. Büyük veri hacminde geçici I/O yavaşlığı

## Operasyonel Kontrol Listesi

- [ ] `failed` export kaydı tespit edildi
- [ ] `error_message` ve worker logu incelendi
- [ ] Retry güvenli şekilde kuyruğa alındı
- [ ] Son durumda export `completed` ve `file_size > 0`
- [ ] `batch.csv_url/xlsx_url` alanı güncellendi

## İlgili Kaynaklar

- `services/backend/apps/exports/tasks.py`
- `services/backend/apps/exports/models.py`
- `services/backend/apps/exports/views.py`
- `docs/RUNBOOKS/production-readiness-and-deploy-guardrails.md`
