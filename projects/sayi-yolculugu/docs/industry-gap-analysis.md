# Sayı Yolculuğu — Sektör Standartları Gap Analizi

> **Tarih:** 2026-05-27  
> **Ortam:** Android WebView + Browser test skeleton  
> **Kapsam:** `index.html`, `css/game.css`, `js/game-*.js` (11 modül), `js/levels-data.js`  
> **Metodoloji:** Kod tabanı incelemesi + sektör benchmark'ı (mobil bulmaca/puzzle genre)  

---

## 1. Executive Summary

| Alan | Sektör Standardı | Mevcut Durum | Gap | Öncelik |
|------|-----------------|--------------|-----|---------|
| **Oyun Tasarımı** | Tutorial, ipucu, power-up, ses, hikaye | Temel mekanikler + procedural 10K seviye | 🔴 Yüksek | P1 |
| **UI/UX** | Drag-drop, preview, pause, settings, accessibility | Tıkla-ekle/tıkla-sil, overlay'ler var | 🟡 Orta | P2 |
| **Teknik Mimari** | TypeScript, test, lint, CI/CD, error boundary | Plain JS, modüler, Python testleri var | 🟡 Orta | P2 |
| **Mobil Platform** | PWA, haptic, wake lock, safe area, adaptive icon | WebView uyumlu, responsive, viewport meta | 🟡 Orta | P2 |
| **Monetizasyon** | Onboarding, IAP flow, ads, push, cloud save | Kredi butonu var (stub), localStorage | 🔴 Yüksek | P1 |
| **Güvenlik** | CSP, input validation, XSS koruması | innerHTML kullanımı, localStorage güveniyor | 🟢 Düşük | P3 |

**Genel Değerlendirme:** Oyunun **çekirdek mekaniği sağlam** ve **teknik altyapı stabil**. Ancak sektörde bir mobil bulmaca oyununun sahip olması beklenen **duygusal katman** (ses, animasyon, hikaye), **retention araçları** (günlük görev, achievement, sosyal) ve **monetizasyon hunisi** neredeyse tamamen eksik. Oyun "teknik olarak çalışan prototip" ile "mağazaya hazır ürün" arasındaki mesafeyi kapatmalı.

---

## 2. Oyun Tasarımı (Game Design)

### 2.1 Mevcut Durum

- **Mekanikler:** Grid hareketi, operatörler (+, −, ×, ÷, ^), duvarlar (normal, directional, toggle), kilitler, teleportlar, restart noktaları, toggle switch'ler, komut kuyruğu (programlama).
- **İçerik:** 32 statik seviye + 10.000 procedural seviye (v4). Yaş gruplarına göre (5–6, 7–8, 9–10, 11–12).
- **Zorluk sistemi:** Yıldızlar (3 / 2 / 1) — optimal hamle sayısına göre.
- **Procedural generation:** Python motor, BFS solver ile validate edilmiş, %0 unsolvable.

### 2.2 Sektör Standardı

Modern mobil bulmaca oyunları (Monument Valley, Baba Is You, Cut the Rope, Two Dots vb.) şunları sunar:

- **Guided Tutorial:** İlk 3–5 seviye sesli/yazılı rehberle öğretir. "Buraya dokun", "Şunu dene".
- **Ipucu Sistemi:** Takılan oyuncuya yarım-transparent yol çizimi veya komut önerisi.
- **Power-up / Joker:** "Bir komut sil", "Hedefi gör", "Çözümü göster" gibi tüketilebilir yetenekler.
- **Ses ve Müzik:** Arka plan müziği, komut sesleri, başarı/kutlama jingle'ları.
- **Particle Efektleri:** Hücre patlaması, yıldız toplama, duvara çarpma spark'ları.
- **Screen Shake:** Duvara çarpma veya başarı anında hafif kamera titremesi.
- **Hikaye / Tematik Bağlam:** Karakter, dünya, ilerleme hissi.
- **Achievement / Rozetler:** "İlk 10 seviye", "Hiç hata yapmadan", "Büyük sayı üret".
- **Daily Challenge:** Her gün yeni bir özel seviye.

### 2.3 Gap Analizi

| Özellik | Durum | Etki |
|---------|-------|------|
| Tutorial | ❌ Yok | İlk defa oynayan kullanıcı kaybı yüksek |
| Ipucu | ❌ Yok | Zor seviyelerde churn (çıkış) artar |
| Power-up | ❌ Yok | Monetizasyon hunisi zayıf |
| Ses/Müzik | ❌ Yok | Duygusal bağ zayıf, oyun sessiz kalır |
| Particle | ❌ Yok | Geri bildirim sadece CSS animasyonuyla sınırlı |
| Screen Shake | ❌ Yok | Fiziksel geri bildirim eksik |
| Hikaye | ❌ Yok | Retention düşük — "niye oynuyorum?" sorusu |
| Achievement | ❌ Yok | Uzun vadeli motivasyon yok |
| Daily Challenge | ❌ Yok | Günlük dönüş (DAU) için tetikleyici yok |

**Skor:** 1/9 ✅ (sadece procedural içerik var)

---

## 3. UI/UX (Kullanıcı Arayüzü & Deneyim)

### 3.1 Mevcut Durum

- **Tema:** Dark mode, Inter font, CSS custom properties.
- **Responsive:** 3 breakpoint (400px, 640px, 641px+).
- **Ekranlar:** Oyun ekranı, kazanma overlay, seviye seçim, tümü tamamlandı.
- **Kontroller:** Komut butonlarına tıkla → kuyruğa ekle. Kuyruktaki chipe tıkla → sil.

### 3.2 Sektör Standardı

- **Drag & Drop:** Komutları sıralamak için sürükle-bırak (özellikle uzun programlarda).
- **Path Preview:** Komut kuyruğuna her eklemede grid üzerinde yarım-transparent hayalet oyuncu hareketi gösterilir.
- **Pause Menüsü:** Oyunda duraklatma, ses ayarı, nasıl oynanır, ana menüye dön.
- **Settings:** Dil, ses, tema, haptic, bildirim ayarları.
- **Undo/Redo:** Sadece "son komutu sil" değil, tam undo/redo stack.
- **Step-by-Step Execution:** Komutları tek tek ilerletme (adım adım debug) modu.
- **Accessibility:** Screen reader desteği (`aria-label`, `role`), color blind modu, font size ayarı.
- **Onay Dialogları:** "Tüm komutları silmek istediğine emin misin?", "Oyundan çık?"
- **Haptic Feedback:** Butona basma, duvara çarpma, başarı (Android `VibrationEffect`).
- **Empty State:** Seviye seçimde boş durum, ilk açılışta hoş geldin.

### 3.3 Gap Analizi

| Özellik | Durum | Etki |
|---------|-------|------|
| Drag & Drop | ❌ Yok | 10+ komutlu seviyelerde kuyruk yönetimi zor |
| Path Preview | ❌ Yok | Oyuncu "çalıştır" demeden sonucu göremez |
| Pause Menü | ❌ Yok | Oyundan çıkışta durum kaybolabilir |
| Settings | ❌ Yok | Kullanıcı kontrolü sıfır |
| Undo/Redo Stack | ❌ Yok | Sadece tek undo (pop) var |
| Step-by-Step | ❌ Yok | Hata ayıklama zor, çocuklar için frustrasyon |
| Accessibility | ❌ Yok | Erişilebilirlik standartlarına uyumsuz |
| Onay Dialogları | ❌ Yok | Yanlışlıkla reset/silme riski |
| Haptic Feedback | ❌ Yok | Native his eksik |
| Empty State | ⚠️ Kısmi | `LEVELS_BY_AGE` yoksa console warn verir, UI'da göstermez |

**Skor:** 2/10 ✅ (dark tema + responsive var)

---

## 4. Teknik Mimari

### 4.1 Mevcut Durum

- **Dil:** Plain JavaScript (ES6+ `const`/`let`, `async/await` var).
- **Modülerlik:** 11 adet `game-*.js` dosyası, single responsibility.
- **State:** Global mutable state (`game-store.js`), `localStorage` persist.
- **Build:** Yok — dosyalar direkt `<script src>` ile yükleniyor.
- **Test:** Python tarafında `pytest` + BFS solver testleri mevcut. JS tarafında test yok.
- **Lint:** Yok (ESLint, Prettier yok).
- **i18n:** `game-i18n.js` — TR/EN sözlük, fallback mekanizması var.

### 4.2 Sektör Standardı

- **TypeScript:** Tip güvenliği, IntelliSense, refactoring kolaylığı.
- **Module Bundler:** Vite, Webpack veya Rollup — tree shaking, minification, code splitting.
- **Unit Test:** Jest / Vitest — her modül için izole test.
- **E2E Test:** Playwright / Cypress — kullanıcı senaryoları.
- **Lint & Format:** ESLint + Prettier + Husky pre-commit hook.
- **CI/CD:** GitHub Actions — test, build, deploy otomasyonu.
- **Error Boundary:** `window.onerror`, `try/catch` wrapper, kullanıcıya anlamlı hata mesajı.
- **Analytics:** Google Analytics, Firebase, Mixpanel — event tracking.
- **Service Worker:** Offline oynama, asset cache, PWA.

### 4.3 Gap Analizi

| Özellik | Durum | Etki |
|---------|-------|------|
| TypeScript | ❌ Yok | Büyük refactor riskli, yeni geliştirici onboarding zor |
| Bundler | ❌ Yok | 13MB level dosyaları ana thread'de parse ediliyor |
| JS Unit Test | ❌ Yok | Regresyon riski yüksek |
| E2E Test | ❌ Yok | Manuel test yükü ağır |
| Lint/Format | ❌ Yok | Kod tutarsızlığı, style çatışması |
| CI/CD | ❌ Yok | Deploy riskli, manuel adımlar |
| Error Boundary | ⚠️ Kısmi | `try/catch` `initGame`'de var ama genel wrapper yok |
| Analytics | ⚠️ Kısmi | Sadece Android bridge event'leri (native tarafa), web analytics yok |
| Service Worker | ❌ Yok | Offline oynama yok, PWA değil |

**Skor:** 3/9 ✅ (modülerlik + i18n var)

---

## 5. Mobil Platform Standartları

### 5.1 Mevcut Durum

- **Viewport:** `width=device-width, initial-scale=1.0, user-scalable=no`.
- **Touch:** `-webkit-tap-highlight-color: transparent`, `-webkit-user-select: none`.
- **Responsive:** CSS breakpoint'ler, `dvh` birimi.
- **Android Bridge:** `Android.onGameEvent()` ile native iletişim.

### 5.2 Sektör Standardı

- **PWA Manifest:** `manifest.json`, install prompt, standalone mode.
- **Splash Screen:** Açılışta marka logosu, yükleme göstergesi.
- **Adaptive Icon:** Farklı cihazlara uyumlu uygulama ikonu.
- **iOS Safe Area:** `env(safe-area-inset-*)` — notch/dynamic island desteği.
- **Status Bar:** `theme-color` meta + native status bar renk kontrolü.
- **Fullscreen:** `requestFullscreen()` veya display mode.
- **Wake Lock:** Oyun sırasında ekran kararmasın (`navigator.wakeLock`).
- **Vibration API:** HTML5 `navigator.vibrate()` — buton, çarpma, başarı.
- **Font Preload:** Google Fonts `display=swap` veya self-hosted.

### 5.3 Gap Analizi

| Özellik | Durum | Etki |
|---------|-------|------|
| PWA Manifest | ❌ Yok | Browser'da "Ana Ekrana Ekle" yok |
| Splash Screen | ❌ Yok | İlk açılışta beyaz/boş ekran |
| Adaptive Icon | ❌ Yok | Icon standart değil |
| iOS Safe Area | ❌ Yok | Notch/arkasına UI girebilir |
| Status Bar | ⚠️ Kısmi | Sadece `theme-color` meta var |
| Fullscreen | ❌ Yok | Browser chrome görünür |
| Wake Lock | ❌ Yok | Ekran kararabilir |
| Vibration API | ❌ Yok | Haptic eksik (bridge dışında) |
| Font Preload | ⚠️ Kısmi | Google Fonts `display=swap` var ama offline çalışmaz |

**Skor:** 2/9 ✅ (viewport + touch var)

---

## 6. Monetizasyon & Retention

### 6.1 Mevcut Durum

- **Kredi Sistemi:** `btnBuyCredits` var ama stub — tıklandığında `notifyAndroid('buyCredits', {})` gönderir.
- **State:** `localStorage` persist, `signature` ile set değişiminde temizleme.
- **Progress:** Seviye bazlı tamamlama, yıldız, deneme sayısı, süre.

### 6.2 Sektör Standardı

- **Onboarding Funnel:** İlk 24 saat içinde 3–5 seviye tamamlatma, izin isteme (bildirim), hesap oluşturma.
- **IAP Flow:** Google Play Billing entegrasyonu, ürün kataloğu, satın alma onayı, consumable/non-consumable yönetimi.
- **Rewarded Ads:** "İpucu izle", "Ekstra deneme izle" karşılığında reklam.
- **Push Notification:** "Yeni seviyeler hazır", "Günlük görevini tamamla", "3 gündür görmedik".
- **Cloud Save:** Firebase / Play Games — cihaz değiştirmede progress korunur.
- **Session Management:** Oyundan çıkıldığında exact state restore (hangi seviye, kuyruktaki komutlar).
- **Season Pass / Battle Pass:** Zaman sınırlı içerik, ödül zinciri.
- **Leaderboard:** Arkadaşlar/global sıralama.

### 6.3 Gap Analizi

| Özellik | Durum | Etki |
|---------|-------|------|
| Onboarding Funnel | ❌ Yok | İlk gün retention (D1) düşük |
| IAP Flow | ❌ Yok | Para kazanma imkanı yok |
| Rewarded Ads | ❌ Yok | Non-payer monetizasyon yok |
| Push Notification | ❌ Yok | Re-engagement yok |
| Cloud Save | ❌ Yok | Cihaz değişiminde kayıp |
| Session Mgmt | ⚠️ Kısmi | Kuyruk ve progress restore var ama pause/resume yok |
| Season Pass | ❌ Yok | Uzun vadeli monetizasyon yok |
| Leaderboard | ❌ Yok | Sosyal rekabet yok |

**Skor:** 1/8 ✅ (sadece local progress var)

---

## 7. Güvenlik

### 7.1 Mevcut Durum

- `innerHTML` kullanımı var (`game-grid-renderer.js:62`, `game-level-manager.js:54`).
- `localStorage`'a güveniyor — client-side manipülasyona açık.
- Level data'da input validation yok (Android'den gelen JSON trust ediliyor).
- CSP (Content Security Policy) header yok.

### 7.2 Sektör Standardı

- CSP header ile inline script/ eval kısıtlaması.
- Input sanitization — level data parse'ı şema doğrulaması ile.
- Signed state — sunucu tarafında doğrulanmış progress (eğer leaderboard varsa).
- `textContent` tercihi `innerHTML` yerine.

### 7.3 Gap Analizi

| Özellik | Durum | Etki |
|---------|-------|------|
| CSP | ❌ Yok | XSS riski (düşük ama var) |
| Input Validation | ❌ Yok | Bozuk level JSON = crash |
| Signed State | ❌ Yok | Hile (cheat) kolay |
| innerHTML → textContent | ⚠️ Kısmi | Bazı yerlerde `innerHTML` kullanılıyor |

**Skor:** 1/4 ✅ (XSS riski düşük çünkü kullanıcı inputu yok)

---

## 8. Güçlü Yönler (Neler İyi?)

Bu rapor sadece eksikleri değil, **güçlü yönleri** de not etmeli:

1. **Çekirdek Mekanik Sağlam:** Komut kuyruğu + grid + operatörler = benzersiz, eğitici, bağımlılık yapıcı.
2. **Procedural Generation Mükemmel:** 10.000 seviye, %0 unsolvable, BFS doğrulamalı, yaş gruplarına göre.
3. **Modüler Kod:** 11 dosya, single responsibility, okunabilir.
4. **Cross-Platform Sync:** JS ↔ Python motor clamp, bölme, kare konularında tutarlı.
5. **i18n Hazır:** TR/EN sözlük, kolayca genişletilebilir.
6. **Android Bridge:** Native entegrasyon temiz, event-based.
7. **Dark Theme Modern:** Inter font, glassmorphism, gradient'ler, hoş görünüm.
8. **State Persist:** localStorage + signature + restore mantığı doğru.

---

## 9. Öncelikli Eylem Planı

### Phase 1: MVP Polish (2–3 hafta) — P1

| # | Görev | Dosyalar | Etki |
|---|-------|----------|------|
| 1 | **Tutorial sistemi** — ilk 3 seviyede overlay rehber | `game-ui-overlays.js`, `game-main.js` | Kullanıcı kaybını azaltır |
| 2 | **Ses entegrasyonu** — arka plan müziği + SFX | Yeni: `game-audio.js` | Duygusal bağ kurar |
| 3 | **Particle efektleri** — başarı, çarpma, yıldız | `css/game.css`, `game-execution-engine.js` | Geri bildirim zenginler |
| 4 | **Ipucu sistemi** — BFS çözümünün ilk 3 adımını göster | `game-execution-engine.js`, `game-ui-overlays.js` | Churn azalır |
| 5 | **IAP stub'ını gerçekleştir** — Android bridge'den Play Billing'e yönlendir | `game-ui-overlays.js`, `android-bridge.js` | Monetizasyon açılır |

### Phase 2: UX & Platform (2–3 hafta) — P2

| # | Görev | Dosyalar | Etki |
|---|-------|----------|------|
| 6 | **Pause + Settings menüsü** — ses, dil, haptic, nasıl oynanır | `index.html`, `game-ui-overlays.js` | Kullanıcı kontrolü |
| 7 | **Path preview** — kuyruğa komut eklerken hayalet oyuncu | `game-grid-renderer.js`, `game-command-system.js` | Planlama kolaylaşır |
| 8 | **Drag & drop** — komut kuyruğunda sıralama | `game-command-system.js` | Uzun programlar yönetilebilir |
| 9 | **Step-by-step modu** — tek komut ileri/geri | `game-execution-engine.js` | Öğrenme ve debug |
| 10 | **PWA + Service Worker** — offline, install | `index.html`, Yeni: `sw.js`, `manifest.json` | Erişilebilirlik |
| 11 | **Haptic feedback** — `navigator.vibrate()` + Android bridge | `game-execution-engine.js`, `android-bridge.js` | Native his |
| 12 | **Vibration / Wake Lock** — oyun sırasında ekran açık | `game-main.js` | UX |

### Phase 3: Retention & Scale (1–2 ay) — P3

| # | Görev | Dosyalar | Etki |
|---|-------|----------|------|
| 13 | **Achievement sistemi** — rozetler, milestones | Yeni: `game-achievements.js` | Uzun vadeli motivasyon |
| 14 | **Daily Challenge** — günün seviyesi | Yeni: `game-daily.js` + backend | DAU artar |
| 15 | **Leaderboard** — Play Games / Firebase | `android-bridge.js` + backend | Sosyal rekabet |
| 16 | **Cloud Save** — Firebase / Play Games | `game-store.js` | Cihaz bağımsızlık |
| 17 | **TypeScript migration** — `game-*.js` → `.ts` | Tüm `js/` | Teknik borç azalır |
| 18 | **Jest/Vitest testleri** — JS motor testleri | Yeni: `tests/` | Regresyon güvenliği |

---

## 10. Sonuç

**Sayı Yolculuğu, "çekirdek oyun döngüsü" açısından sektör standartlarının üzerinde** — procedural generation, BFS doğrulama, cross-platform sync, modüler mimari gibi konularda profesyonel bir seviyede.

**Ancak "ürünleştirme" açısından sektörden önemli ölçüde geride** — ses, haptic, tutorial, monetizasyon, retention, PWA gibi bir mobil oyunun mağazada başarılı olması için gerekli katmanlar eksik.

**Öneri:** Phase 1'i (MVP Polish) önceliklendir. Çekirdek mekanik zaten sağlam; üzerine duygusal katman (ses, particle, tutorial) ve temel monetizasyon (IAP flow) eklenince oyun "mağazaya hazır" seviyesine çıkar.

---

> **Rapor Hazırlayan:** Kimi Code CLI  
> **Sonraki Adım:** Kullanıcı Phase 1'den bir görev seçer veya raporun bir bölümünü detaylandırır.
