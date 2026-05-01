# MathLock Play — VPS Entegrasyon Planı

> **Son güncelleme:** 26 Nisan 2026 — Redis + Celery, i18n, deploy --backend

---

## Mevcut Durum (Aktif)

> **29 Nisan 2026:** Backend (Django + Celery) konteyner dışına çıkarıldı.
> `kimi-cli` host'ta kurulu ve login olduğu için, AI seviye üretimi konteyner içinde çalışmıyordu.
> Artık sadece PostgreSQL ve Redis konteynerda; Django ve Celery host üzerinde systemd servisi olarak çalışıyor.

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
   ├─ API: /api/mathlock/ → Django backend (unix socket)
   └─ Conf: infrastructure/nginx/conf.d/mathlock-play.conf

🐳 Docker Compose (2 servis — sadece altyapı)
   ├─ mathlock_db    — PostgreSQL 16 (named volume, kalıcı, port 5432)
   └─ mathlock_redis — Redis 7 (Celery broker, port 6379)

⚙️ Host Systemd Servisleri (konteyner dışı)
   ├─ mathlock-backend.service — Django + gunicorn (unix socket)
   └─ mathlock-celery.service  — Celery worker (queues: celery,levels,questions)

🤖 AI Pipeline (Celery task queue)
   ├─ levels/progress/  → generate_level_set.delay()
   ├─ questions/progress/ → generate_question_set.delay()
   └─ Celery worker → kimi-cli (host PATH) → questions.json / levels.json → DB
```

### VPS Dizin Yapısı:

| VPS Yolu | İçerik | Kaynak |
|----------|--------|--------|
| `/var/www/mathlock/website/` | index.html, privacy.html, support.html | `website/` dizini |
| `docker-compose.yml` | 2 servis (db, redis) | `projects/mathlock-play/` |
| systemd servisleri | backend + celery | `/etc/systemd/system/mathlock-*.service` |
| nginx conf | mathlock.com.tr HTTPS + /api/mathlock proxy | `infrastructure/nginx/conf.d/mathlock-play.conf` |
| backend socket | gunicorn unix socket | `/home/akn/vps/projects/mathlock-play/backend/run/gunicorn.sock` |

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

## Faz 1 — Backend API (Aktif — Host-based)

> **29 Nisan 2026:** Backend konteyner dışına çıkarıldı. Detay: `docs/HOST_MIGRATION.md`

### VPS tarafı: `projects/mathlock-play/backend/`
- **Teknoloji:** Django REST Framework (anka/webimar ile tutarlı)
- **Socket:** `/home/akn/vps/projects/mathlock-play/backend/run/gunicorn.sock` (unix domain socket)
- **Systemd:** `mathlock-backend.service` (host üzerinde `.venv`)
- **Veritabanı:** PostgreSQL (Docker, named volume `mathlock_pgdata` — deploy'da silinmez, `localhost:5432`)
- **Cache/Queue:** Redis 7 (Docker, `redis://localhost:6379/0`)
- **Celery Worker:** `mathlock-celery.service` (host üzerinde, queues: `celery`, `levels`, `questions`)
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

`infrastructure/nginx/conf.d/mathlock-play.conf` (VPS üzerinde doğrudan düzenlenir):

```nginx
# Statik veriler
location /mathlock/data/ {
    alias /var/www/mathlock/data/;
}
location /mathlock/health {
    return 200 "mathlock ok\n";
}

# Backend API (unix socket üzerinden)
location /api/mathlock/ {
    proxy_pass http://unix:/var/run/mathlock/gunicorn.sock:/api/mathlock/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 30s;
}
```

> **Not:** Backend konteyner dışında olduğu için nginx container'a socket dizini volume olarak mount edilir:
> `- /home/akn/vps/projects/mathlock-play/backend/run:/var/run/mathlock:ro`

---

## VPS SSH Erişimi ve Debug

Sunucuya bağlanmak için:

```bash
ssh akn@89.252.152.222
```

### Servis Durumunu Kontrol Et

```bash
# Tüm mathlock servisleri
systemctl status mathlock-backend --no-pager
systemctl status mathlock-celery --no-pager
docker ps | grep mathlock

# Backend logları
sudo journalctl -u mathlock-backend -f --no-pager

# Celery worker logları
sudo journalctl -u mathlock-celery -f --no-pager

# Redis kontrol
docker exec mathlock_redis redis-cli ping

# Celery health check (host üzerinden)
cd /home/akn/vps/projects/mathlock-play/backend
.venv/bin/celery -A mathlock_backend inspect ping

# DB sorgusu (Django shell — host üzerinden)
cd /home/akn/vps/projects/mathlock-play/backend
.venv/bin/python manage.py shell

# PostgreSQL doğrudan erişim
docker exec -it mathlock_db psql -U mathlock -d mathlock
# veya host üzerinden:
psql -h localhost -U mathlock -d mathlock
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
   └─ ./deploy.sh --backend   → rsync backend + AI pipeline dosyaları, migrate, systemd restart, health check
```

### Backend deploy detayı (`--backend`):
1. `git pull` (yerelden VPS'ye kod sync)
2. `sudo systemctl restart mathlock-backend`
3. `sudo systemctl restart mathlock-celery`
4. `cd backend && .venv/bin/python manage.py migrate --noinput`
5. `cd backend && .venv/bin/python manage.py compilemessages --ignore=.venv`
6. `.venv/bin/celery -A mathlock_backend inspect ping` (health check)
7. HTTP health check `curl -f https://mathlock.com.tr/api/mathlock/health/`

### İlk Kurulum (Host-based)

```bash
# 1. Veritabanı ve Redis konteynerlarını başlat
cd /home/akn/vps/projects/mathlock-play
docker-compose up -d

# 2. Python venv oluştur
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Django migrate + static
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 4. Systemd servislerini kopyala ve başlat
sudo cp docs/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mathlock-backend
sudo systemctl enable --now mathlock-celery
```
