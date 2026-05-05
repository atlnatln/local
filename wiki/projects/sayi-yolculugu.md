---
title: "Sayı Yolculuğu"
created: "2026-05-01"
updated: "2026-05-03"
type: project
tags: [sayi-yolculugu, html5, javascript, android, webview, education]
related:
  - mathlock-play
  - infrastructure
sources:
  - raw/articles/sayi-yolculugu-index.html
  - projects/mathlock-play/app/src/main/java/com/akn/mathlock/SayiYolculuguActivity.kt
---

# [[Sayi-Yolculugu]]

Çocuklar için matematik eğitim oyunu. İki formatta var:

1. **Standalone HTML5** — Tarayıcıda çalışan tek dosya (`index.html`)
2. **MathLock Play entegrasyonu** — Android WebView içinde, backend bağlantılı

## Standalone HTML5 Oyunu

`projects/sayi-yolculugu/index.html` (~41 KB) — CSS, JavaScript ve oyun mantığı tek dosyada.

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | HTML5, CSS3, Vanilla JavaScript |
| Deploy | Statik dosya (nginx üzerinden servis edilir) |
| Boyut | ~41 KB tek dosya |

### Özellikler

- Yaş grubu seçimi (splash ekranı)
- Responsive tasarım (mobil uyumlu)
- Koyu tema (dark mode)
- Skor ve ilerleme takibi

### Deploy

```bash
# Nginx config'de statik dosya servisi
location /sayi-yolculugu {
    alias /home/akn/local/projects/sayi-yolculugu/;
    try_files $uri $uri/ =404;
}
```

---

## MathLock Play Entegrasyonu

`projects/mathlock-play/app/src/main/java/com/akn/mathlock/SayiYolculuguActivity.kt` (490 satır)

### Stack

| Katman | Teknoloji |
|--------|-----------|
| Android | Kotlin, WebView, JavaScript Bridge |
| Cache | `SecurePrefs` (encrypted SharedPreferences) |
| Network | `ApiClient` + `AccountManager` |
| Fallback | `assets/sayi-yolculugu/fallback-levels/{tr,en}.json` |

### Backend Endpoint'leri

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/levels/` | GET | Mevcut seviye setini döndür. `device_token`, `child_id`, `locale` query params. İlk istekte static levels'tan kişisel `LevelSet` oluşturulur. |
| `/levels/progress/` | POST | Tamamlanan seviyeleri yükle. Set bittiğinde `auto_renewal_started` ve `credits_remaining` döner. |

### Veri Akışı

```
SayiYolculuguActivity
  ├─ onCreate()
  │   ├─ fetchLevels() → GET /levels/?device_token=...&child_id=...&locale=...
  │   │   ├─ 200 OK → JSON parse → currentSetId, completed_level_ids, levels[]
  │   │   ├─ Cache'e kaydet (SecurePrefs)
  │   │   └─ Offline/Error → fallback-levels/{locale}.json
  │   └─ loadLevelsIntoGame() → webView.evaluateJavascript("initGame(...)")
  │
  ├─ JS Bridge: onGameEvent("levelComplete")
  │   ├─ completedLevelIds.add(levelId)
  │   ├─ uploadLevelProgress([levelId]) → POST /levels/progress/
  │   └─ lockedPackage varsa → levelsCompleted >= levelsToUnlock? → unlockAndFinish()
  │
  └─ JS Bridge: onGameEvent("allComplete")
      ├─ uploadLevelProgress(tüm completed)
      ├─ response.auto_renewal_started == true → pollForNewSet() (5sn aralıkla, max 120 deneme = 10 dk)
      └─ response.credits_remaining → showCreditRequired()
```

### AI Seviye Üretim Pipeline'ı

Backend'deki seviyeler bittiğinde (tüm 12 seviye tamamlandığında):

```
POST /levels/progress/ → credits_remaining > 0?
  ├─ Evet: Celery task başlatır → ai-generate-levels.sh çalıştırır
  │   ├─ kimi-cli yeni 12 seviye üretir
  │   ├─ validate-levels.py şema + matematik doğruluğu kontrol eder
  │   └─ LevelSet DB'ye kaydeder
  └─ Hayır: Aynı seviyeler tekrar eder (sonsuz döngü)
```

### Cache & Offline Davranış

| Senaryo | Davranış |
|---------|----------|
| İlk açılış + internet var | API'den çek → cache'e kaydet → oyunu başlat |
| İlk açılış + internet yok | `fallback-levels/{locale}.json` → oyunu başlat |
| Tekrar açılış + internet var | API'den çek → set değişmişse cache temizle → oyunu başlat |
| Tekrar açılış + internet yok | Cache'den yükle → oyunu başlat |
| Kullanıcı offline oynarken | Tamamlanan seviyeler `completedLevelIds`'e eklenir. Online olunca upload edilir. |

### Polling (Yeni Set Bekleme)

`allComplete` sonrası `auto_renewal_started == true` ise:
- Her 5 saniyede bir `fetchLevels()` çağrılır
- Maksimum 120 deneme (10 dk)
- Yeni set gelince `initGame()` ile WebView'e enjekte edilir
- `onDestroy()`'da `handler.removeCallbacksAndMessages(null)` ile temizlenir — memory leak önlemi

### WebView Temizliği

v1.0.67'de eklenen stabilite düzeltmesi:
```kotlin
override fun onDestroy() {
    handler.removeCallbacksAndMessages(null)  // Polling durdur
    webView.stopLoading()
    webView.loadUrl("about:blank")
    webView.clearHistory()
    webView.removeAllViews()
    webView.destroy()
    SecurePrefs.get(this, PREFS_NAME).edit()
        .remove(KEY_CACHED_LEVELS)
        .remove(KEY_COMPLETED_IDS)
        .apply()
    super.onDestroy()
}
```

## Dependencies

- [[mathlock-play]] — Android entegrasyonu burada
- [[infrastructure]] — nginx, SSL, mathlock.com.tr domain
- [[kimi-code-cli]] — AI seviye üretim aracı

## Recent Commits

- (monorepo içinde izleniyor)
