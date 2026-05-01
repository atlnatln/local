# MathLock Play — Host Migration Log

> **Tarih:** 29 Nisan 2026  
> **Sebep:** `kimi-cli` (AI seviye/soru üretim aracı) VPS host'ta kurulu ve login olmuş durumdaydı, ancak Docker konteyner içinden erişilemiyordu. Bu yüzden kullanıcı LevelSet v3'ü tamamladığında kredi düşüldü ama yeni set üretilemedi.  
> **Çözüm:** Django backend + Celery worker konteyner dışına çıkarıldı; sadece PostgreSQL + Redis konteynerda kaldı.

---

## Önceki Mimari (Konteyner-tabanlı)

```
Docker Compose (4 servis)
  ├─ mathlock_db      → PostgreSQL 16
  ├─ mathlock_redis   → Redis 7
  ├─ mathlock_backend → Django + gunicorn (port 8003)
  └─ mathlock_celery  → Celery worker

Nginx proxy_pass → 172.17.0.1:8003 (Docker bridge IP)
```

**Sorun:** `mathlock_celery` konteyneri içinden `kimi` komutu bulunamadı (`kimi: command not found`).  
Çünkü `kimi-cli` sadece host'ta (`/usr/local/bin/kimi`) kuruluydu, konteyner PATH'inde yoktu.

---

## Yeni Mimari (Host-based Backend)

```
Docker Compose (2 servis — sadece veritabanı)
  ├─ mathlock_db    → PostgreSQL 16 (port 5432 host'a açık)
  └─ mathlock_redis → Redis 7 (port 6379 host'a açık)

Host Systemd Servisleri
  ├─ mathlock-backend.service → gunicorn (unix socket)
  └─ mathlock-celery.service  → Celery worker

Nginx proxy_pass → unix:/var/run/mathlock/gunicorn.sock
```

**Avantaj:** `kimi-cli` host PATH'inde olduğu için Celery task'ları doğrudan çalıştırabilir.

---

## Yapılan Adımlar (Adım Adım)

### 1. Veritabanı ve Redis Portlarını Host'a Aç

`docker-compose.yml`:
```yaml
services:
  mathlock_db:
    ports:
      - "5432:5432"   # Yeni eklendi
  mathlock_redis:
    ports:
      - "6379:6379"   # Yeni eklendi
```

Sonra:
```bash
cd /home/akn/vps/projects/mathlock-play
docker-compose up -d
```

### 2. Host Üzerinde Python Virtual Environment Hazırla

```bash
cd /home/akn/vps/projects/mathlock-play/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # Django, DRF, Celery, redis, gunicorn, vb.
```

### 3. Django Migrate ve Static Files

```bash
cd /home/akn/vps/projects/mathlock-play/backend
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
```

### 4. Eksik `celery.py` Dosyasını Oluştur

Sunucuda `mathlock_backend/celery.py` yoktu (yerel repoda vardı ama deploy edilmemişti):

```python
# /home/akn/vps/projects/mathlock-play/backend/mathlock_backend/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mathlock_backend.settings")

app = Celery("mathlock_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

`__init__.py` zaten şöyleydi:
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

### 5. Systemd Servis Dosyalarını Oluştur

`/etc/systemd/system/mathlock-backend.service`:
```ini
[Unit]
Description=MathLock Play Django Backend
After=network.target

[Service]
Type=simple
User=akn
Group=akn
WorkingDirectory=/home/akn/vps/projects/mathlock-play/backend
Environment="PATH=/home/akn/vps/projects/mathlock-play/backend/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DJANGO_SECRET_KEY=..."
Environment="DJANGO_DEBUG=False"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
Environment="DB_NAME=mathlock"
Environment="DB_USER=mathlock"
Environment="DB_PASSWORD=mathlock_dev_pass"
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
Environment="CELERY_RESULT_BACKEND=redis://localhost:6379/0"
Environment="GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=/home/akn/vps/projects/mathlock-play/backend/google-service-account.json"
ExecStart=/home/akn/vps/projects/mathlock-play/backend/.venv/bin/gunicorn \
    mathlock_backend.wsgi:application \
    --bind unix:/home/akn/vps/projects/mathlock-play/backend/run/gunicorn.sock \
    --workers 2 --access-logfile - --error-logfile -
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/mathlock-celery.service`:
```ini
[Unit]
Description=MathLock Play Celery Worker
After=network.target

[Service]
Type=simple
User=akn
Group=akn
WorkingDirectory=/home/akn/vps/projects/mathlock-play/backend
Environment="PATH=..."
# (Aynı env değişkenleri)
ExecStart=/home/akn/vps/projects/mathlock-play/backend/.venv/bin/celery \
    -A mathlock_backend worker -l info -Q celery,levels,questions
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktifleştir:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mathlock-backend
sudo systemctl enable --now mathlock-celery
```

### 6. Nginx Config'i Unix Socket'e Yönlendir

`infrastructure/nginx/conf.d/mathlock-play.conf`:
```nginx
location /api/mathlock/ {
    proxy_pass http://unix:/var/run/mathlock/gunicorn.sock:/api/mathlock/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 30s;
}
```

**Socket volume mount** nginx container'a eklendi:
```yaml
volumes:
  - /home/akn/vps/projects/mathlock-play/backend/run:/var/run/mathlock:ro
```

### 7. SSL Sertifika Yollarını Düzelt

Nginx config'te `/etc/letsencrypt/live/mathlock.com.tr/` yolları konteyner içinde yoktu.  
Host'ta `/home/akn/vps/infrastructure/ssl/mathlock.com.tr/` altında zaten kopyalar vardı.  
Yollar `/etc/nginx/ssl/mathlock.com.tr/` olarak değiştirildi (bu dizin zaten container'a mount ediliyordu).

### 8. UFW ve Docker Etkileşim Sorunu

`ufw` aktifken (`default deny incoming`) Docker container'ları host'a erişemiyordu.  
Bu yüzden backend'i **TCP port** yerine **Unix socket** üzerinden dinlemeye aldık.  
Unix socket, nginx container'a volume mount edildiği için UFW'yi bypass etmiyor (kernel-level IPC).

---

## Karşılaşılan Sorunlar ve Çözümleri

| # | Sorun | Neden | Çözüm |
|---|-------|-------|-------|
| 1 | `ModuleNotFoundError: mathlock_backend.celery` | Sunucuda `celery.py` dosyası yoktu | Dosyayı oluşturduk |
| 2 | `Worker failed to boot` gunicorn | `__init__.py` `from .celery import app` yapıyordu ama `celery.py` yoktu | Dosya oluşturuldu, `__pycache__` temizlendi |
| 3 | `nginx -t` SSL hatası | `/etc/letsencrypt/live/...` container içinde yok | `/etc/nginx/ssl/...` olarak değiştirildi |
| 4 | 504 Gateway Time-out | `proxy_pass 127.0.0.1:8003` → nginx container loopback'e gidiyordu | `172.21.0.1` (Docker gateway) kullanıldı |
| 5 | 504 devam etti | gunicorn `127.0.0.1`e bind edilmiş, Docker bridge'den gelen istekleri reddediyordu | `0.0.0.0` yapıldı |
| 6 | 504 devam etti (UFW) | `ufw` Docker container'ların host'a TCP erişimini engelliyordu | **Unix socket** kullanıldı, UFW sorunu çözüldü |
| 7 | 502 Bad Gateway (socket) | `proxy_pass http://unix:/path/uri` syntax'ı yanlıştı | `http://unix:/path:/uri` olarak düzeltildi |
| 8 | Django SQLite kullanıyordu | `DATABASE_URL` env'i tanımlı değildi, `settings.py` SQLite fallback yapıyordu | `DATABASE_URL=postgres://...` eklendi |
| 9 | DB bağlantı hatası | `DB_HOST=localhost` → `::1` (IPv6) çözülüyordu, auth hatası | `DB_HOST=127.0.0.1` yapıldı |
| 10 | `kimi: command not found` | `kimi-cli` `uv tool` ile kuruluydu, PATH'te yoktu | `PATH=/home/akn/.local/share/uv/tools/kimi-cli/bin:...` eklendi |
| 11 | `tasks.py` eksik | Yerelde vardı ama sunucuya deploy edilmemişti | `tasks.py` kopyalandı |
| 12 | Celery task `PENDING` kalıyor | `settings.py`'de `CELERY_BROKER_URL` tanımlı değildi; task broker'a (Redis) gitmiyordu | `settings.py`'ye `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_TASK_SERIALIZER` eklendi |
| 13 | `credits_childprofile.locale does not exist` | `tasks.py` ve migration dosyaları sunucuya deploy edilmemişti | `rsync` ile tüm `backend/` sync edildi, `migrate --noinput` çalıştırıldı |
| 14 | `DuplicateNodenameWarning` | Eski Celery worker instance'ları Redis'te kayıtlı kalmış | `-n mathlock-celery@%h` ile worker node name unique yapılabilir (opsiyonel) |

---

## Anlık Komut Referansı (Context Kaybolduğunda)

```bash
# Durum kontrol
sudo systemctl status mathlock-backend --no-pager
sudo systemctl status mathlock-celery --no-pager
docker ps | grep mathlock

# Loglar
sudo journalctl -u mathlock-backend -f --no-pager
sudo journalctl -u mathlock-celery -f --no-pager

# Restart
sudo systemctl restart mathlock-backend
sudo systemctl restart mathlock-celery

# Django shell (host üzerinden)
cd /home/akn/vps/projects/mathlock-play/backend
.venv/bin/python manage.py shell

# Celery ping
cd /home/akn/vps/projects/mathlock-play/backend
.venv/bin/celery -A mathlock_backend inspect ping

# Health check
curl -s https://mathlock.com.tr/api/mathlock/health/

# DB
psql -h localhost -U mathlock -d mathlock
```

---

## Kimi-cli Durumu

```bash
# Host'ta mevcut mu?
which kimi          # /usr/local/bin/kimi
kimi --version      # v1.39.0

# Login durumu
ls ~/.kimi/         # config, auth dosyaları

# Celery task içinden çalışıyor mu?
# (ai-generate-levels.sh içinde `kimi` komutu çağrılıyor)
```

---

## Önemli Dosya Yolları

| Dosya/Dizin | Açıklama |
|-------------|----------|
| `/home/akn/vps/projects/mathlock-play/backend/` | Django projesi kökü |
| `/home/akn/vps/projects/mathlock-play/backend/.venv/` | Python virtual env |
| `/home/akn/vps/projects/mathlock-play/backend/run/gunicorn.sock` | Gunicorn unix socket |
| `/home/akn/vps/projects/mathlock-play/backend/mathlock_backend/celery.py` | Celery app tanımı |
| `/etc/systemd/system/mathlock-backend.service` | Backend systemd servisi |
| `/etc/systemd/system/mathlock-celery.service` | Celery systemd servisi |
| `/home/akn/vps/infrastructure/nginx/conf.d/mathlock-play.conf` | Nginx vhost config |
| `/home/akn/vps/infrastructure/ssl/mathlock.com.tr/` | SSL sertifikaları |
| `/home/akn/vps/projects/mathlock-play/docker-compose.yml` | Sadece DB + Redis |

---

## Context Kaybolduğunda Hızlı Başlangıç

> Eğer bu migration'ın detayları context compaction sonrası kaybolduysa, aşağıdaki adımlar yeterlidir.

### 1. Sistem Durumu (30 saniyelik kontrol)

```bash
ssh akn@89.252.152.222
sudo systemctl status mathlock-backend mathlock-celery --no-pager
curl -s https://mathlock.com.tr/api/mathlock/health/
docker ps | grep mathlock
```

### 2. Yerel Repo → Sunucu Sync

```bash
cd projects/mathlock-play
./deploy.sh --backend   # rsync + migrate + systemd restart
```

**Sync edilenler:** `backend/`, `ai-generate*.sh`, `validate-*.py`, `agents/`, `AGENTS.md`, `docs/systemd/*.service`

**Sync EDİLMEYENLER:** `backend/.venv/`, `backend/db.sqlite3`, `backend/google-service-account.json`

### 3. Sorun Giderme

| Belirti | Muhtemel Neden | Çözüm |
|---------|---------------|-------|
| 502/504 | gunicorn çalışmıyor | `sudo systemctl restart mathlock-backend` |
| AI üretilmiyor | `kimi` PATH'te yok | `which kimi` → `/home/akn/.local/share/uv/tools/kimi-cli/bin/kimi` |
| `ModuleNotFoundError` | `tasks.py` veya `celery.py` eksik | `rsync` ile `backend/` sync et |
| `column ... does not exist` | Migration uygulanmamış | `.venv/bin/python manage.py migrate --noinput` |
| `PENDING` task | `CELERY_BROKER_URL` tanımlı değil | `settings.py`'de `CELERY_BROKER_URL` kontrol et |

---

## Yerel Repo ↔ Sunucu Dosya Haritası

| Yerel Yol | Sunucu Yolu | Sync? | Not |
|-----------|-------------|-------|-----|
| `backend/` | `/home/akn/vps/projects/mathlock-play/backend/` | ✅ rsync | `.venv` hariç |
| `ai-generate.sh` | `.../mathlock-play/ai-generate.sh` | ✅ scp | |
| `ai-generate-levels.sh` | `.../mathlock-play/ai-generate-levels.sh` | ✅ scp | |
| `validate-questions.py` | `.../mathlock-play/validate-questions.py` | ✅ scp | |
| `validate-levels.py` | `.../mathlock-play/validate-levels.py` | ✅ scp | |
| `agents/` | `.../mathlock-play/agents/` | ✅ rsync | |
| `AGENTS.md` | `.../mathlock-play/AGENTS.md` | ✅ scp | |
| `docs/systemd/*.service` | `/etc/systemd/system/` | ✅ scp | |
| `website/` | `/var/www/mathlock/website/` | ❌ | `deploy.sh` data sync ile ayrı |
| `docker-compose.yml` | `.../mathlock-play/docker-compose.yml` | ❌ | Elle sync, dikkatli |
| `infrastructure/nginx/...` | VPS üzerinde doğrudan | ❌ | Elle düzenlenir |

---

## Başarı Kriterleri (Migration Sonrası)

- [x] `curl https://mathlock.com.tr/api/mathlock/health/` → `{"status":"ok"}`
- [x] `systemctl status mathlock-backend` → `active (running)`
- [x] `systemctl status mathlock-celery` → `active (running)`
- [x] Celery worker 3 queue'yu dinliyor: `celery`, `levels`, `questions`
- [x] `kimi-cli` host PATH'inde erişilebilir
- [x] `ufw` aktif ve güvenlik sağlanıyor
- [x] SSL sertifikaları geçerli
- [x] **AI pipeline end-to-end:** `levels.json` üretildi (`/tmp/mathlock-levels-gen-*/levels.json`)
