# MathLock — VPS Entegrasyon Planı

## Mevcut Durum (Faz 0)

Uygulama tamamen yerel çalışır, VPS bağlantısı yoktur.  
Deploy scripti sadece APK'yı VPS'e yükler, telefon oradan indirebilir.

---

## Faz 1 — Temel Bağlantı

### VPS tarafı: `projects/mathlock/backend/`
- **Teknoloji:** FastAPI veya Django (anka/webimar ile tutarlı olması için Django önerilen)
- **Port:** 8003 (webimar: 8001, anka: 8002)
- **Docker:** `docker-compose.yml` → `mathlock_backend` servisi

### Endpoint'ler (ilk aşama)

| Endpoint | Metot | Açıklama |
|---|---|---|
| `/api/mathlock/health/` | GET | Sağlık kontrolü |
| `/api/mathlock/config/` | GET | Uygulama konfigürasyonu (mesaj, güncelleme bildirimi) |
| `/api/mathlock/stats/` | POST | Kullanım istatistikleri gönder (anonim) |
| `/api/mathlock/apk/latest/` | GET | Son APK meta verisi (versiyon, değişim notları) |

### Android tarafı değişiklik
- `PreferenceManager.kt`'ye `VPS_API_URL` tercihi ekle (varsayılan: `http://89.252.152.222/api/mathlock`)
- `AppLockService.kt`'de arka planda periyodik stats push (isteğe bağlı, sadece onay verilirse)

---

## Faz 2 — Uzaktan Konfigürasyon

VPS üzerinden uygulama ayarlarını yönet:

```
GET /api/mathlock/config/remote/
→ {
    "question_count": 5,
    "pass_score": 3,
    "locked_apps": ["com.youtube.android", ...],  // isteğe bağlı uzaktan yönetim
    "ai_difficulty_level": "easy"
}
```

Uygulamada `RemoteConfigSync` servisi bu endpoint'i periyodik çeker.

---

## Faz 3 — AI Kontrolü (ops-bot entegrasyonu)

```
VPS (ops-bot AI)
    ↓
/api/mathlock/ai/command/
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

`infrastructure/nginx/conf.d/mathlock.conf` (otomatik oluşturulur deploy ile):

```nginx
location /api/mathlock/ {
    proxy_pass http://mathlock_backend:8003;
}
location /mathlock/dist/ {
    alias /home/akn/vps/projects/mathlock/dist/;
}
```

---

## Deploy Akışı

```
Yerel makine
   │
   ├─ ./deploy.sh            → debug APK → telefona ADB + VPS dist/
   ├─ ./deploy.sh --release  → imzalı APK → Play Store veya VPS
   └─ Faz 1+: backend/deploy.sh → Docker container → VPS
```
