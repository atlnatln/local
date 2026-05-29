---
title: "Sayı Yolculuğu"
created: "2026-05-01"
updated: "2026-05-28"
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

1. **Standalone HTML5** — Tarayıcıda çalışan modüler web uygulaması
2. **MathLock Play entegrasyonu** — Android WebView içinde, backend bağlantılı

## Standalone HTML5 Oyunu

`projects/sayi-yolculugu/index.html` — ana oyun dosyası. **Modüler yapıya geçildi** (2026-05-25), ardından `game-` prefix'li dosya yapısına standartlaştırıldı (2026-05-27).

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | HTML5, CSS3, Vanilla JavaScript |
| Deploy | Statik dosyalar (nginx üzerinden servis edilir) |
| Yapı | Modüler (`game-` prefix'li JS + ayrı CSS) |

### Modüler Dosya Yapısı (2026-05-27)

**CSS:**
| Dosya | İçerik |
|-------|--------|
| `css/game.css` | Tüm oyun stilleri (layout, grid, renkler, responsive, overlay'ler) |

**JavaScript:**
| Dosya | İçerik |
|-------|--------|
| `js/game-main.js` | Entry point, oyun başlatma, lifecycle |
| `js/game-cmds.js` | Komut kuyruğu yönetimi |
| `js/game-command-system.js` | Blockly benzeri komut sistemi (drag & drop) |
| `js/game-execution-engine.js` | Komut çalıştırma motoru (adım adım animasyon) |
| `js/game-grid-renderer.js` | Izgara render motoru (SVG/Canvas hücre çizimi) |
| `js/game-audio.js` | Ses efektleri ve arka plan müziği (HTML5 Audio) |
| `js/game-i18n.js` | Çoklu dil desteği ve çeviri yönetimi |
| `js/game-level-manager.js` | Seviye yükleme, geçiş, kaydetme, günlük set |
| `js/game-store.js` | Yerel depolama, ayarlar, achievement'lar |
| `js/game-ui-overlays.js` | Overlay'ler (splash, pause, tutorial, game over, settings) |
| `js/game-utils.js` | Yardımcı fonksiyonlar ve genel araçlar |
| `js/state.js` | Oyun state yönetimi (global state nesnesi) |
| `js/levels-data.js` | Statik seviye tanımları (JSON formatında seviye dizisi) |
| `js/editor.js` | Seviye editörü mantığı (grid edit, test, export) |
| `js/android-bridge.js` | Android WebView ↔ JS iletişim köprüsü |

### Entry Points

| Dosya | Amaç |
|-------|------|
| `index.html` | Ana oyun (oyuncu modu) |
| `editor.html` | Tarayıcıda çalışan seviye editörü. Yeni seviyeler tasarlanıp JSON olarak dışa aktarılabilir |
| `index-web-backup.html` | Yedek/geri dönüşüm dosyası |

### Ses ve Efektler (2026-05-27)

`audio/` dizini — HTML5 Audio ile yönetilir:

| Dosya | Kullanım |
|-------|----------|
| `audio/bgm.wav` | Arka plan müziği (loop) |
| `audio/click.wav` | Buton / komut ekleme sesi |
| `audio/success.wav` | Seviye tamamlama, achievement |
| `audio/bump.wav` | Duvar çarpma, hatalı hareket |

### Dokümantasyon & Test (2026-05-27)

`docs/` ve `scripts/` dizinleri:

| Dosya | İçerik |
|-------|--------|
| `docs/game-html-test-report.md` | Oyun HTML test raporu |
| `docs/industry-gap-analysis.md` | Rakip analizi ve eksik özellikler |
| `docs/stability-report-v4.md` | v4 stabilite raporu |
| `docs/stability-test-plan.md` | Stabilite test planı |
| `docs/next-session-plan.md` | Sonraki geliştirme oturumu planı |
| `scripts/test-level-generation.py` | Seviye üretim test script'i |
| `AGENTS.md` | Proje-level agent talimatları |

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

**Kök Neden:** `procedural_levels/generator/pipeline.py` satır 175-178'de `targetVal` sadece `difficulty >= 3` ve `%60` ihtimalle atanırken, `place_ops()` her zaman çağrılıyordu. Sonuç: zorluk 2 seviyelerde (ve zorluk >=3'te %40 ihtimalle) operatörler vardı ama hedef değer yoktu.

**Düzeltme:** `pipeline.py`'de `targetVal == null` ise `ops = []`; `validate-levels.py`'de `ops` var ama `targetVal` yoksa uyarı verir; eski/cache'lenmiş seviyeler için fallback: `ops` var ama `targetVal` null ise `startVal` hedef değer olarak kabul edilir.

## Son Güncellemeler

### 2026-05-28 — Motor Senkronizasyonu ve Çeşitli Güncellemeler

- **Execution Engine:** Python BFS motoru ile JS motoru senkronize edildi. Lock persistence, switch persistence, switch timing, value boundary prune, targetVal fallback removal
- **Grid Renderer:** Izgara render motoru güncellemeleri
- **Game Store:** Yerel depolama ve state yönetimi iyileştirmeleri
- **Editör:** `editor.html` güncellemeleri
- **Yeni dosya:** `game.html` eklendi (oyun ekranı)

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

- `7c0a7249` fix(sayi-yolculugu): sync JS execution engine with Python BFS — lock persistence, switch persistence, switch timing, value boundary prune, targetVal fallback removal (2026-05-28)
- `819cf45c` feat(sayi-yolculugu): difficulty score system + session updates (2026-05-28)
- `8cc818a3` docs(wiki): ingest mathlock-play v1.0.101 release build + Google Play upload (2026-05-27)
- `2f1e4860` chore(wiki): organize wiki and fix lint warnings (2026-05-27)
- `cbed0ac0` feat(sayi-yolculugu): ses, tutorial, ipucu, path preview, undo/redo, achievements, daily set, haptic (2026-05-27)
- `acb3dd4f` refactor(sayi-yolculugu): web motoru silindi, Android motoru test alanına dönüştürüldü (2026-05-27)
- `6f2eabcc` docs(wiki): kimi-code-cli agents, skills, hooks ve plugins dokümantasyonu (2026-05-27)
- `fa05f66` feat(mathlock): v1.0.100 — ses, tutorial, ipucu, path preview, undo/redo, achievements, daily set, haptic (2026-05-27)
- `d68e371` fix(sayi-yolculugu): operators without targetVal made levels trivial to win (2026-05-25)
- `f4cba014` feat(sayi-yolculugu): modüler JS/CSS yapıya geçiş, editor.html eklendi (2026-05-25)
- `3a030f21` feat(sayi-yolculugu): `/` ve `^` operatör desteği, bölme bounce mantığı (2026-05-11)
- `e5ae1fc1` fix(mathlock-play): v1.0.78 — compile fix, test limit, Play Store upload script (2026-05-10)
