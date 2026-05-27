---
title: "Sayı Yolculuğu"
created: "2026-05-01"
updated: "2026-05-25"
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

`projects/sayi-yolculugu/index.html` — ana oyun dosyası. **Modüler yapıya geçildi** (2026-05-25): CSS ve JS ayrı dosyalara bölündü.

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | HTML5, CSS3, Vanilla JavaScript |
| Deploy | Statik dosyalar (nginx üzerinden servis edilir) |
| Yapı | Modüler (CSS + JS ayrılmış) |

### Modüler Dosya Yapısı (2026-05-25)

**CSS:**
| Dosya | İçerik |
|-------|--------|
| `css/base.css` | Temel stiller, layout, renkler |
| `css/components.css` | Bileşen stilleri (grid, hücreler, butonlar) |
| `css/responsive.css` | Mobil/tablet breakpoint'leri |

**JavaScript:**
| Dosya | İçerik |
|-------|--------|
| `js/main.js` | Entry point, oyun başlatma |
| `js/state.js` | Oyun state yönetimi |
| `js/grid-renderer.js` | Izgara render motoru |
| `js/execution-engine.js` | Komut çalıştırma motoru |
| `js/command-system.js` | Blockly benzeri komut sistemi |
| `js/event-bus.js` | Modüller arası iletişim |
| `js/level-manager.js` | Seviye yükleme, geçiş, kaydetme |
| `js/levels-data.js` | Statik seviye tanımları |
| `js/audio.js` | Ses efektleri ve müzik |
| `js/hint-engine.js` | İpucu sistemi |
| `js/progress.js` | İlerleme takibi |
| `js/settings.js` | Kullanıcı ayarları |
| `js/store.js` | Yerel depolama |
| `js/ui-overlays.js` | Overlay'ler (splash, pause, game over) |
| `js/utils.js` | Yardımcı fonksiyonlar |
| `js/analytics.js` | Olay takibi |
| `js/daily-challenge.js` | Günlük meydan okuma |
| `js/api-client.js` | Backend API iletişimi (MathLock entegrasyonu) |

### Level Editor (2026-05-25)

`editor.html` — tarayıcıda çalışan seviye editörü. Yeni seviyeler tasarlanıp JSON olarak dışa aktarılabilir.

| Özellik | Açıklama |
|---------|----------|
| Grid boyutu ayarı | Satır/sütun sayısı |
| Hücre tipleri | Sayı, operatör (+, −, ×, /, ^), duvar, başlangıç, bitiş |
| Test çalıştırma | Editörde seviyeyi oyna |
| JSON export | `levels-data.js` formatında çıktı |

### Özellikler

- Yaş grubu seçimi (splash ekranı) + splash features etiketleri
- Responsive tasarım (mobil uyumlu)
- Koyu tema (dark mode) + `theme-color` meta tag
- Mobil optimizasyon: `maximum-scale=1.0`, `user-scalable=no`, touch highlight kaldırma, `overscroll-behavior: none`
- Goal bar (seviye hedef göstergesi)
- Skor ve ilerleme takibi
- **Yeni operatörler (2026-05-11):** `/` (bölme) ve `^` (kare alma) hücreleri. Bölme hücresine girmeden önce sayının tam bölünüp bölünmediği kontrol edilir; bölünmüyorsa duvar çarpması gibi bounce davranışı gösterilir. Kare alma tek seferlik uygulanır.

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

## Bilinen Bug'lar ve Düzeltmeler

### 2026-05-25 — Ops var ama targetVal yok seviye geçiş bug'ı

**Semptom:** Oyuncu `+2` gibi bir operatör hücresinden geçip sayısını 3 yapıp hedefe ulaştığında seviye geçiliyordu. Hedef değer (`targetVal`) tanımlı değilse oyun sadece konum kontrolü yapıyordu.

**Kök Neden:** `procedural_levels/generator/pipeline.py` satır 175-178'de `targetVal` sadece `difficulty >= 3` ve `%60` ihtimalle atanırken, `place_ops()` her zaman çağrılıyordu. Sonuç: zorluk 2 seviyelerde (ve zorluk >=3'te %40 ihtimalle) operatörler vardı ama hedef değer yoktu. Oyuncu operatörden geçip sayısını değiştirse bile kazanıyordu.

**Düzeltme:**
- `pipeline.py`: `targetVal == null` ise `ops = []` — operatörler sadece hedef değer varsa yerleştirilir.
- `validate-levels.py`: `ops` var ama `targetVal` yoksa uyarı verir.
- `game.html` + `experimental-web`: Eski/cache'lenmiş seviyeler için fallback — `ops` var ama `targetVal` null ise `startVal` hedef değer olarak kabul edilir.
- `SayiYolculuguGameEngineTest`: Regression testleri eklendi.

## Son Güncellemeler

### 2026-05-27 — v1.0.100 Özellikleri (MVP Polish)

- **Ses sistemi:** HTML5 Audio ile arka plan müziği (`bgm.wav`), SFX (başarı, hata, buton, duvar çarpma)
- **Tutorial overlay:** İlk 3 seviyede interaktif rehber balonları (`tutorialSteps` metadata)
- **Ipucu sistemi:** Python generator `hintCommands` output'u, kuyruğa ghost chip ekleme
- **Path preview:** Komut kuyruğuna her eklemede hayalet oyuncu pozisyonu (`updateGhostPreview`)
- **Undo/Redo stack:** Komut kuyruğu history (`history[]` / `historyIdx`), max 50 adım
- **Achievement rozetleri:** `first_win`, `perfect_3`, `speedster`, `no_mistake`, `ten_levels`
- **Günlük seviye seti (Daily):** Tarihe göre deterministik 10 seviye seçimi (`getDailySetIndex`)
- **Haptic feedback:** Android bridge üzerinden `Vibrator` ile titreşim (`notifyAndroid('haptic')`)
- **Pause menüsü:** Ses, haptic toggle, nasıl oynanır
- **IAP Bridge:** Google Play Billing entegrasyonu (`BillingHelper.kt` ↔ JS `onPurchaseSuccess`)

## Recent Commits

- `fa05f66` feat(mathlock): v1.0.100 — ses, tutorial, ipucu, path preview, undo/redo, achievements, daily set, haptic (2026-05-27)
- `d68e371` fix(sayi-yolculugu): operators without targetVal made levels trivial to win (2026-05-25)
- `f4cba014` feat(sayi-yolculugu): modüler JS/CSS yapıya geçiş, editor.html eklendi (2026-05-25)
- `3a030f21` feat(sayi-yolculugu): `/` ve `^` operatör desteği, bölme bounce mantığı (2026-05-11)
- `e5ae1fc1` fix(mathlock-play): v1.0.78 — compile fix, test limit, Play Store upload script (2026-05-10)
- `681346a3` fix(mathlock-play): 7 critical bug fixes, UI/UX improvements, new tests, v1.0.77 (2026-05-09)
