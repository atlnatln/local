# MathLock Play — VPS Entegrasyon Planı

## Mevcut Durum (Aktif)

Play Store sürümü HTTPS üzerinden `mathlock.com.tr` domaini ile çalışır.

### Aktif Sistem:

```
📱 Telefon (com.akn.mathlock.play)
   ├─ Soru indirme:  GET  https://mathlock.com.tr/mathlock/data/questions.json
   ├─ Konu indirme:  GET  https://mathlock.com.tr/mathlock/data/topics.json
   ├─ Stats yükleme: PUT  https://mathlock.com.tr/mathlock/data/stats.json
   └─ Sağlık:        GET  https://mathlock.com.tr/mathlock/health

🖥️ VPS (nginx — mathlock.com.tr)
   ├─ SSL: Let's Encrypt (certbot)
   ├─ Web: /var/www/mathlock/website/ (privacy, support sayfaları)
   ├─ Data: /var/www/mathlock/data/ (questions.json, topics.json, stats.json)
   └─ Conf: infrastructure/nginx/conf.d/mathlock-play.conf

🤖 AI Pipeline (otomatik)
   ├─ VPS cron: */5 * * * * mathlock-trigger.sh
   │   └─ stats.json varsa → ai-generate.sh --vps-mode
   ├─ Local monitor: mathlock-monitor.sh (systemd user service)
   │   └─ VPS'teki stats izler → ai-generate.sh yerel
   └─ Copilot CLI: AGENTS.md kurallarıyla 50 soru üretir
```

### VPS Dizin Yapısı:

| VPS Yolu | İçerik | Kaynak |
|----------|--------|--------|
| `/var/www/mathlock/website/` | index.html, privacy.html, support.html | `website/` dizini |
| `/var/www/mathlock/data/` | questions.json, topics.json, stats.json | AI pipeline |
| nginx conf | mathlock.com.tr HTTPS config | `website/nginx-mathlock.conf` |

### Deploy Akışı:

```bash
# Debug APK (test)
./deploy.sh --adb

# Release AAB (Play Store)
./deploy.sh --release

# Sadece data sync
./deploy.sh --sync-data
```

---

## Faz 1 — Backend API (Gelecek)

### VPS tarafı: `projects/mathlock-play/backend/`
- **Teknoloji:** Django (anka/webimar ile tutarlı)
- **Port:** 8003 (webimar: 8001, anka: 8002)
- **Docker:** `docker-compose.yml` → `mathlock_play_backend` servisi

### Endpoint'ler (ilk aşama)

| Endpoint | Metot | Açıklama |
|---|---|---|
| `/api/mathlock/health/` | GET | Sağlık kontrolü |
| `/api/mathlock/config/` | GET | Uygulama konfigürasyonu |
| `/api/mathlock/stats/` | POST | Kullanım istatistikleri gönder (anonim) |

### Android tarafı değişiklik
- `PreferenceManager.kt`'ye `VPS_API_URL` tercihi ekle (varsayılan: `https://mathlock.com.tr/api/mathlock`)
- `AppLockService.kt`'de arka planda periyodik stats push (isteğe bağlı, sadece onay verilirse)

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

# Faz 1+ (backend eklenince)
location /api/mathlock/ {
    proxy_pass http://mathlock_play_backend:8003;
}
```

---

## Deploy Akışı

```
Yerel makine
   │
   ├─ ./deploy.sh --adb       → debug APK → telefona ADB
   ├─ ./deploy.sh --release   → AAB → Play Store'a yükle
   ├─ ./deploy.sh --sync-data → VPS ile soru verisi sync
   └─ Faz 1+: backend/deploy.sh → Docker container → VPS
```
