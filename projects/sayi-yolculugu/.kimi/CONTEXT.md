# Sayı Yolculuğu — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).

---

## 🎯 Durum

**3 Haftalık Pragmatik Geliştirme Planı aktif.** Hafta 2 tamamlandı.

---

## 📚 Kalıcı Dersler (Aynı Hatayı Tekrar Yapma)

- **Plugin sync:** Source'daki `.py` değişince `~/.kimi/plugins/sayi-yolculugu-validator/scripts/` altına da `cp` ile kopyala (symlink yok).
- **JS↔Python motor senkronize edildi:** Clamp (-500/5000), bölme (`Math.floor`/`//`), kare (`val * val`). Bu konularda cross-check yapılmasına gerek yok.
- **Path planning must respect commands:** `plan_solution_path` sadece oyuncunun kullanabileceği komut yönlerini kullanmalı.
- **Op processing order must match path order:** `place_ops`'ta `chosen` listesi path sırasına göre sort edilmeli.
- **Android asset sync:** Her değişiklik sonrası `cp js/game-*.js css/game.css ../mathlock-play/app/src/main/assets/sayi-yolculugu/`
- **Browser cache:** Playwright testlerinde cache bypass gerekli (`Network.clearBrowserCache` CDP). Android WebView'da da benzer: `game-execution-engine.js` değişince browser cache'den eski versiyon yüklenip "Unexpected end of input" hatası verebilir. Çözüm: `location.reload(true)` veya cache bypass header'ları.
- **Tutorial localStorage key:** `sy_tutorial_{setId}_{levelIdx}` formatında tutulur, set değişiminde tekrar gösterilir
- **Hint system:** `hintCommands` Python `to_dict()`'a eklendi. JS'te `showHint()` kredi kontrolü ve tüm kredi sistemi kodu tamamen kaldırıldı (oyun içi kredi kaldırıldı). `showHintPreview()`/`hideHintPreview()` basılı-tutma mekaniği eklendi. `hintCommands` yoksa `lv.solution`'a fallback yapılır. Android asset'ler senkronize edildi.
- **Ghost preview:** Komut kuyruğu değiştiğinde `updateGhostPreview()` otomatik çağrılır, duvar kontrolü yapar
- **IAP bridge:** `BillingHelper` `SayiYolculuguActivity`'de initialize ediliyor, `buyCredits` → `launchPurchase("kredi_1")`
- **Cross-file variable scope:** `const`/`let` ile tanımlanan değişkenler block-scoped'tur. Farklı `<script>` dosyaları arasında paylaşılan değerlar global `state` objesine veya fonksiyon parametresine alınmalı. `effectiveTargetVal` `loadLevel()`'ın local değişkeniydi, `checkWin()` göremedi → `ReferenceError` → UI dondu.
- **Duplicate op consistency:** Grid renderer (`opMap`, son yazan kazanır) ve execution engine (`Array.find()`, ilk bulan kazanır) farklı lookup kullanıyordu. Aynı mekanizma kullanılmalı.
- **Async exception safety:** `runProgram` gibi async fonksiyonlarda `try/catch/finally` zorunlu. Exception atılırsa `state.running = false` ve UI reset hiç çalışmaz, ekran donar.

---

## ✅ Tamamlananlar

**Hafta 1 (His ve Kontrol) — Tamamlandı:**
- HTML5 Audio Engine (`js/game-audio.js`) — SFX (click, bump, success) + BGM loop
- Haptic Feedback trigger'ları (`game-execution-engine.js`)
- Pause Menüsü + Settings (`#pauseOverlay`)
- CSS Particle Efektleri
- Android asset senkronizasyonu

**Hafta 2 (Öğrenme ve Yönlendirme) — Tamamlandı:**
- **Tutorial Overlay** — İlk 3 seviyeye `tutorialSteps` metadata, balon + pointer UI
  - `game-ui-overlays.js`: `showTutorial()`, `nextTutorialStep()`, `dismissTutorial()`
  - `game-level-manager.js`: `loadLevel()` sonrası otomatik başlatma (localStorage tracking)
  - `css/game.css`: `.tutorial-bubble`, `.tutorial-pointer`, `@keyframes pointerPulse`
- **Ipucu Sistemi** — Python `hintCommands` + JS ghost komutlar
  - `core/types.py`: `to_dict()`'a `hintCommands` eklendi (`solution`'dan map edilir)
  - `game-command-system.js`: `showHint()` — kredi stub (3 ücretsiz), `hintMode` ghost chip
  - `game-store.js`: `getCredits()`, `setCredits()`, `window.onPurchaseSuccess()`
  - `index.html` / `game.html`: `btnHint` butonu
- **Path Preview (Ghost Player)** — Komut kuyruğunun son konumunu grid'de gösterir
  - `game-grid-renderer.js`: `updateGhostPreview()` — duvar/bounds kontrolü
  - `css/game.css`: `.cell.ghost` + `@keyframes ghostPulse`
  - `game-command-system.js`: `addCommand()`, chip remove sonrası otomatik güncelleme
- **IAP Bridge Tamamlama** — `BillingHelper` entegrasyonu
  - `SayiYolculuguActivity.kt`: `initBilling()`, `BillingListener` implementasyonu
  - `buyCredits` event'i artık `billingHelper.launchPurchase("kredi_1")` çağırıyor
  - `onDestroy()`'da `billingHelper.disconnect()`
  - Satın alma başarılı olunca JS'ye `onPurchaseSuccess(credits)` gönderilir
- **Android asset senkronizasyonu** — `js/game-*.js`, `css/game.css`, `game.html` kopyalandı
- **pytest** — 42 passed, 0 failure
- **10k validate** — `scripts/test-level-generation.py` ile 10.000 seviye %100 temiz (0 failed, 0 warning)

**Tamamlanan backlog:**
- ~~Tutorial Overlay~~ ✅
- ~~Ipucu Sistemi~~ ✅
- ~~Path Preview~~ ✅
- ~~IAP Bridge~~ ✅
- ~~Hafta 1 tüm maddeler~~ ✅

---

## ⏭️ Sonraki Adımlar

**1000 Seviye Sonrası İyileştirme Planı — Tamamlandı:**
- `build_difficulty_plan()` — `base = round(last_avg * 0.75)` + plan yapısı düzeltmesi (base değeri daha iyi temsil ediliyor)
- `difficulty_score` field'i — `Level.to_dict()`'ye `"difficultyScore"` eklendi
- Veriye dayalı kalibrasyon — `scripts/calibrate_difficulty_bands.py` + P20/P40/P60/P80/P95 percentilleri
- `score_to_difficulty` bantları — D4/D5 sınırı 55'e yükseltildi (generator varyansını tolere eder)
- Grid filtreleme — D1'de 1×N / N×1 grid'ler kaldırıldı
- 1000 batch üretim + validasyon — 996 seviye, %100 temiz, D5 oranı %9.1
- 54 pytest passed, 0 failure
- Plugin `analyze_level.py` güncellendi (yeni bantlar + `stored_difficulty_score`)

---

## 🐛 Aktif Sorun

| ID | Sorun | Konum | Öncelik |
|----|-------|-------|---------|
| S2 | `browser_evaluate` MCP tool'u büyük işlemlerde timeout veriyor | Playwright MCP | Orta |
| S3 | Browser cache: Playwright testlerinde JS değişiklikleri cache'den yükleniyor | Playwright/CDP | Düşük (test-only) |

**Çözülmüş Sorunlar (2026-05-29):**
- ~~janset 3.set 9.seviye: duplicate op (×2 + +1 aynı konumda)~~ ✅ — VPS DB düzeltildi, generator dedup koruma eklendi, plugin `check_duplicate_ops` eklendi
- ~~czerdali/kerem: Yanlış yapınca donma + uyarı vermeme~~ ✅ — `effectiveTargetVal` `loadLevel()` local `const`'ı `checkWin()`'da `ReferenceError` atıyordu. `checkWin()` içinde local hesaplamaya çevrildi + `runProgram`'a `try/catch/finally` eklendi

---

## 🔮 Bir Sonraki Oturum İçin Hazırlık

**Durum:** Zorluk dengeleme iyileştirmesi tamamlandı. D5 oranı %73.5'ten %9.1'e düştü.

**Olası devam görevleri:**
- Yeni 1000 batch'i Android asset'ine dahil etme
- `levels-data.js`'e yeni batch'i ekleme (arşiv/referans)
- Daha fazla batch üretimi (10.000 seviye)

---

## 📝 Oturum Sonu Checklist

- [x] Bu dosyayı güncelle (görev durumu, yeni kararlar, yeni bug'lar)
- [x] Session log yaz: `.kimi/logs/YYYY-MM-DD-HHMM-session.md`
- [x] Plugin `.py` dosyalarını `~/.kimi/plugins/.../scripts/` altına senkronize et
- [x] `pytest` çalıştır (`../mathlock-play/procedural_levels/tests/`) — 54 passed
- [x] 1000 batch validasyon — %100 temiz, D5 %9.1
- [x] Git status kontrol et
