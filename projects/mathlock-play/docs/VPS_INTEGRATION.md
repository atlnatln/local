# MathLock Play — VPS Entegrasyon Planı

> **Son güncelleme:** 26 Nisan 2026 — Redis + Celery, i18n, deploy --backend

---

## Mevcut Durum (Aktif)

Play Store sürümü HTTPS üzerinden `mathlock.com.tr` domaini ile çalışır.

### Aktif Sistem:

```
📱 Telefon (com.akn.mathlock.play)
   ├─ Soru indirme:  GET  https://mathlock.com.tr/api/mathlock/questions/
   ├─ Seviye indirme: GET  https://mathlock.com.tr/api/mathlock/levels/
   ├─ Stats yükleme:  POST https://mathlock.com.tr/api/mathlock/stats/
   └─ Sağlık:         GET  https://mathlock.com.tr/api/mathlock/health/

🖥️ VPS (nginx — mathlock.com.tr)
   ├─ SSL: Let's Encrypt (certbot)
   ├─ Web: /var/www/mathlock/website/ (privacy, support sayfaları)
   ├─ API: /api/mathlock/ → Django backend (port 8003)
   └─ Conf: infrastructure/nginx/conf.d/mathlock-play.conf

🐳 Docker Compose (4 servis)
   ├─ mathlock_db      — PostgreSQL 16 (named volume, kalıcı)
   ├─ mathlock_backend — Django + gunicorn
   ├─ mathlock_redis   — Redis 7 (Celery broker)
   └─ mathlock_celery  — Celery worker (AI üretim task'ları)

🤖 AI Pipeline (Celery task queue)
   ├─ levels/progress/  → generate_level_set.delay()
   ├─ questions/progress/ → generate_question_set.delay()
   └─ Celery worker → kimi-cli → questions.json / levels.json → DB
```

### VPS Dizin Yapısı:

| VPS Yolu | İçerik | Kaynak |
|----------|--------|--------|
| `/var/www/mathlock/website/` | index.html, privacy.html, support.html | `website/` dizini |
| `docker-compose.yml` | 4 servis (db, backend, redis, celery) | `projects/mathlock-play/` |
| nginx conf | mathlock.com.tr HTTPS + /api/mathlock proxy | `infrastructure/nginx/conf.d/mathlock-play.conf` |

### Deploy Akışı:

```bash
# Debug APK (test)
./deploy.sh --adb

# Release AAB (Play Store)
./deploy.sh --release

# Sadece data sync
./deploy.sh --sync-data

# Backend deploy (docker-compose, migrate, compilemessages, Celery health check)
./deploy.sh --backend
```

---

## Faz 1 — Backend API (Aktif)

### VPS tarafı: `projects/mathlock-play/backend/`
- **Teknoloji:** Django REST Framework (anka/webimar ile tutarlı)
- **Port:** 8003
- **Docker:** `docker-compose.yml` → `mathlock_backend` + `mathlock_redis` + `mathlock_celery`
- **Veritabanı:** PostgreSQL (named volume `mathlock_pgdata` — deploy'da silinmez)
- **Cache/Queue:** Redis 7 (`redis://mathlock_redis:6379/0`)
- **i18n:** `gettext_lazy` semantic keys + `.po/.mo` dosyaları; `compilemessages` deploy'da otomatik

### Aktif Endpoint'ler

| Endpoint | Metot | Açıklama |
|---|---|---|
| `/api/mathlock/health/` | GET | Sağlık kontrolü |
| `/api/mathlock/register/` | POST | Cihaz kaydı (UUID → device_token). `locale` parametresi kabul eder. |
| `/api/mathlock/purchase/verify/` | POST | Google Play satın alma doğrulama |
| `/api/mathlock/credits/` | GET | Kredi bakiyesi sorgulama |
| `/api/mathlock/credits/use/` | POST | 1 kredi düş → AI 50 soru üret (Celery task) |
| `/api/mathlock/questions/` | GET | Ücretsiz + AI soruları listele (child-specific, `?locale=` destekli) |
| `/api/mathlock/questions/progress/` | POST | Çözülen soruları raporla, tümü bittiyse auto-renew |
| `/api/mathlock/levels/` | GET | Bulmaca seviye setini döndür (child-specific, `?locale=` destekli) |
| `/api/mathlock/levels/progress/` | POST | Tamamlanan seviyeleri raporla, tümü bittiyse auto-renew |
| `/api/mathlock/jobs/<job_id>/status/` | GET | Celery job durum sorgusu (PENDING / SUCCESS / FAILURE) |
| `/api/mathlock/stats/` | POST | Performans istatistiklerini kaydet |
| `/api/mathlock/children/` | GET/POST | Çocuk profili listele / oluştur |
| `/api/mathlock/children/detail/` | PUT/DELETE | Profil güncelle / sil |
| `/api/mathlock/children/report/` | GET | Performans raporu |
| `/api/mathlock/packages/` | GET | Satın alma paketleri |
| `/api/mathlock/auth/register-email/` | POST | Email ile hesap bağlama |

### Android tarafı entegrasyon (Tamamlanan)
- `MathLockApi.kt` → Tüm API çağrıları (`registerDevice`, `useCredit`, `uploadStats`, vb.)
- `CreditApiClient.kt` → Kredi kullanma istemcisi
- `BillingManager.kt` + `BillingHelper.kt` → Google Play Billing entegrasyonu
- `QuestionManager.kt` → API'den soru çekme + rotasyon + progress upload
- `SayiYolculuguActivity` → `/levels/` ve `/levels/progress/` entegrasyonu
- `BaseActivity` → Tüm Activity'ler `AppCompatActivity` yerine `BaseActivity` extend ediyor (locale wrapping)
- `LocaleHelper.kt` + `PreferenceManager.appLocale` → Android tarafı i18n

---

## Faz 2 — Uzaktan Konfigürasyon

VPS üzerinden uygulama ayarlarını yönet:

```
GET https://mathlock.com.tr/api/mathlock/config/remote/
→ {
    "question_count": 5,
    "pass_score": 3,
    "locked_apps": ["com.youtube.android", ...],
    "ai_difficulty_level": "easy"
}
```

Uygulamada `RemoteConfigSync` servisi bu endpoint'i periyodik çeker.

---

## Faz 3 — AI Kontrolü (ops-bot entegrasyonu)

```
VPS (ops-bot AI)
    ↓
https://mathlock.com.tr/api/mathlock/ai/command/
    ↓  (WebSocket veya polling)
Android AppLockService
```

### AI yapabilecekleri

- Günün saatine göre otomatik zorluk ayarı ("okul saatleri")
- Kullanım istatistiklerine göre kilitlenecek uygulama önermesi
- "Bu hafta YouTube'u 3 saatten fazla kullandın, ek soru eklensin mi?" gibi akıllı kararlar
- ops-bot'un `agent.py` → `routing.py` zinciri üzerinden MathLock'a komut gönderme

### Güvenlik
- Tüm komutlar JWT token ile doğrulanır
- Telefon → VPS: HTTPS zorunlu (production)
- AI komutları whitelist tabanlı (sadece önceden tanımlı eylemler)

---

## Nginx Yönlendirme

`website/nginx-mathlock.conf` (deploy.sh ile VPS'e kopyalanır):

```nginx
# Mevcut (aktif)
location /mathlock/data/ {
    alias /var/www/mathlock/data/;
}
location /mathlock/health {
    return 200 "mathlock ok\n";
}

# Faz 1+ (backend aktif)
location /api/mathlock/ {
    proxy_pass http://mathlock_play_backend:8003;
}
```

---

## VPS SSH Erişimi ve Debug

Sunucuya bağlanmak için:

```bash
ssh akn@89.252.152.222
```

### Container Durumunu Kontrol Et

```bash
# Tüm mathlock servisleri
docker ps | grep mathlock

# Backend logları
docker logs -f --tail 100 mathlock_backend

# Celery worker logları
docker logs -f --tail 100 mathlock_celery

# Redis kontrol
docker exec mathlock_redis redis-cli ping

# Celery health check
docker exec mathlock_celery celery -A mathlock_backend inspect ping

# DB sorgusu (Django shell)
docker exec -it mathlock_backend python manage.py shell

# PostgreSQL doğrudan erişim
docker exec -it mathlock_db psql -U mathlock -d mathlock
```

### Örnek: Kullanıcı Hesabını Kontrol Et

```python
# Django shell içinde
from credits.models import Device, CreditBalance, ChildProfile, LevelSet, QuestionSet

d = Device.objects.get(email='kullanici@email.com')
cb = CreditBalance.objects.get(device=d)
print(f"Kredi: {cb.balance}, Ücretsiz kullanıldı: {cb.free_set_used}")

for child in d.children.all():
    ls = LevelSet.objects.filter(child=child).order_by('-version').first()
    qs = QuestionSet.objects.filter(child=child).order_by('-version').first()
    print(f"Çocuk: {child.name}, Locale: {child.locale}")
    if ls:
        print(f"  Seviyeler: v{ls.version}, {len(ls.completed_level_ids)}/{len(ls.levels_json)} tamamlandı")
    if qs:
        print(f"  Sorular: v{qs.version}, {len(qs.solved_ids or [])}/{len(qs.questions_json or [])} çözüldü")
```

---

## Deploy Akışı

```
Yerel makine
   │
   ├─ ./deploy.sh --adb       → debug APK → telefona ADB
   ├─ ./deploy.sh --release   → AAB → Play Store'a yükle
   ├─ ./deploy.sh --sync-data → VPS ile soru verisi sync
   └─ ./deploy.sh --backend   → docker-compose down/up --build, migrate, compilemessages, Celery ping
```

### Backend deploy detayı (`--backend`):
1. `docker-compose down`
2. `docker-compose up -d --build`
3. `docker exec mathlock_backend python manage.py migrate --noinput`
4. `docker exec mathlock_backend python manage.py compilemessages --ignore=.venv`
5. `docker exec mathlock_celery celery -A mathlock_backend inspect ping` (health check)
6. HTTP health check `curl -f https://mathlock.com.tr/api/mathlock/health/`
