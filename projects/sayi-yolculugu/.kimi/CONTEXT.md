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
- **Browser cache:** Playwright testlerinde cache bypass gerekli (`Network.clearBrowserCache` CDP)
- **Tutorial localStorage key:** `sy_tutorial_{setId}_{levelIdx}` formatında tutulur, set değişiminde tekrar gösterilir
- **Hint system:** `hintCommands` Python `to_dict()`'a eklendi. JS'te `showHint()` kredi kontrolü ve tüm kredi sistemi kodu tamamen kaldırıldı (oyun içi kredi kaldırıldı). `showHintPreview()`/`hideHintPreview()` basılı-tutma mekaniği eklendi. `hintCommands` yoksa `lv.solution`'a fallback yapılır. Android asset'ler senkronize edildi.
- **Ghost preview:** Komut kuyruğu değiştiğinde `updateGhostPreview()` otomatik çağrılır, duvar kontrolü yapar
- **IAP bridge:** `BillingHelper` `SayiYolculuguActivity`'de initialize ediliyor, `buyCredits` → `launchPurchase("kredi_1")`

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

## ⏭️ Sonraki Adımlar (3 Haftalık Plan)

**Hafta 3: "İnce Ayar" — Tamamlandı:**
- ~~Undo/Redo Stack~~ ✅
- ~~Basit Yerel Achievements~~ ✅
- ~~Bugünün Seti~~ ✅

**Yeni: Zorluk Dengesi Düzeltme (Tam Yeniden Tasarım) — Tamamlandı:**
- `procedural_levels/generator/difficulty_score.py` — Gerçek zorluk skoru hesaplama (BFS metrik tabanlı)
- `ScoreConfig.for_target_score()` — Hedef skora göre parametre seçimi
- `pipeline.py` — `generate_level()` hedef skor-tabanlı, `generate_set()` set profili + monoton sıralama
- 1000 seviyelik batch: %100 temiz, 0 overlap, 0 band violation
- 52 pytest passed (42 eski + 10 yeni)
- Plugin `analyze_level.py` + `validate_level.py` güncellendi

---

## 🐛 Aktif Sorun

| ID | Sorun | Konum | Öncelik |
|----|-------|-------|---------|
| S2 | `browser_evaluate` MCP tool'u büyük işlemlerde timeout veriyor | Playwright MCP | Orta |
| S3 | Browser cache: Playwright testlerinde JS değişiklikleri cache'den yükleniyor | Playwright/CDP | Düşük (test-only) |

---

## 🔮 Bir Sonraki Oturum İçin Hazırlık

**Durum:** Hafta 3 tamamlandı. 3 haftalık pragmatik geliştirme planı tamamlandı.

**Hafta 3 (İnce Ayar) — Tamamlandı:**
- **Undo/Redo Stack** — Komut kuyruğu history (max 50 adım)
  - `game-store.js`: `history`, `historyIdx`, `resetHistory()`, `pushHistory()`
  - `game-command-system.js`: `undo()`, `redo()`, her `addCommand()`/remove/clear/showHint sonrası snapshot
  - `index.html` / `game.html`: `btnRedo` butonu
  - `game-main.js`: Event handler'lar, `btnClear`'a `pushHistory()`
  - `game-level-manager.js`: `loadLevel()` sonunda `resetHistory()`
- **Basit Yerel Achievements** — 5 rozet, localStorage flag'leri + toast
  - `game-store.js`: `loadAchievements()`, `saveAchievements()`, `unlockAchievement()`
  - `game-execution-engine.js`: `checkAchievements()` — `first_win`, `perfect_3`, `speedster`, `no_mistake`, `ten_levels`
  - `game-ui-overlays.js`: `showAchievementToast()` + `ACHIEVEMENT_DEFS`
  - `css/game.css`: `.achievement-toast`, `@keyframes toastIn/toastOut`
- **Bugünün Seti** — Deterministik daily, `LEVELS_BY_AGE`'den 10 seviye
  - `game-main.js`: `getDailySetIndex()`, `getAllLevelsFlat()`, `playDailySet()`
  - `index.html` / `game.html`: `btnDaily` butonu
- **Android asset senkronizasyonu** — `js/game-*.js`, `css/game.css`, `game.html` kopyalandı
- **pytest** — 42 passed, 0 failure

---

## 📝 Oturum Sonu Checklist

- [x] Bu dosyayı güncelle (görev durumu, yeni kararlar, yeni bug'lar)
- [x] Session log yaz: `.kimi/logs/YYYY-MM-DD-HHMM-session.md`
- [ ] Plugin `.py` dosyalarını `~/.kimi/plugins/.../scripts/` altına senkronize et
- [x] `pytest` çalıştır (`../mathlock-play/procedural_levels/tests/`) — 42 passed
- [x] Git status kontrol et
