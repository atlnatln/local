# game.html Test Raporu — 2026-05-27

> **Ortam:** Android WebView (`game.html`)
> **Motor:** Inline JS, global state, `initGame(levelsJson)` Android bridge

---

## ✅ Yapılan Değişiklikler (Kullanıcı Tarafından)

| # | Değişiklik | Dosya | Satır |
|---|-----------|-------|-------|
| 1 | `updateWallVisuals(activeWalls)` eklendi | `game.html` | 708 |
| 2 | `buildGrid()`'e switchMap, toggleWallSet eklendi | `game.html` | 733–737 |
| 3 | `.toggle-wall` class'ı wall hücrelerine eklendi | `game.html` | 751 |
| 4 | `runProgram()`'a `activeWalls` Set'i eklendi | `game.html` | 874–875 |
| 5 | Inline wall check + `activeWalls` kontrolü | `game.html` | 905–915 |
| 6 | Toggle switch activation (teleport sonrası) | `game.html` | 984–991 |
| 7 | Value clamping (`VAL_MIN=-500`, `VAL_MAX=5000`) | `game.html` | 960–963 |
| 8 | Bölme `Math.floor()` ile güncellendi | `game.html` | 947 |
| 9 | CSS: `.switch`, `.toggle-wall`, `.toggle-wall.wall` | `game.html` | `<style>` |

---

## 🧪 Test Sonuçları

### Test 1: Switch Mekaniği — Baştan Sona Akış

**Seviye:** 3×3 grid, wall (1,0), switch (0,1) → wall'ı açar
**Beklenen:** Switch basılmadan wall'dan geçilemez, basıldıktan sonra geçilir.

| Adım | Komut | Sonuç | Durum |
|------|-------|-------|-------|
| Render | — | (1,0): `wall toggle-wall`, (0,1): `switch 🔘` | ✅ |
| Switch bas | `y+` → `y-` → `x+` → `x+` | (2,0) hedef, "🎉 Tebrikler!" | ✅ |

**Sonuç: ✅ PASSED**

---

### Test 2: Kapalı Wall'dan Bounce + Görsel Değişim

**Seviye:** 3×3 grid, wall (1,0) kapalı, switch (0,1)

| Adım | Komut | Beklenen | Sonuç | Durum |
|------|-------|----------|-------|-------|
| Bounce test | `x+` | Oyuncu (0,0)'da kalmalı | `playerX=0, playerY=0` | ✅ |
| Switch sonrası | `y+` → `y-` → `x+` | Oyuncu (1,0)'a geçmeli | `playerX=1, playerY=0` | ✅ |
| Görsel | — | `.wall` class'ı kalkmalı | `wallClasses="cell toggle-wall"` | ✅ |

**Sonuç: ✅ PASSED**

---

### Test 3: Value Clamping

**Seviye:** 2×1 grid, op `×10000`, startVal=1, targetVal=5000

| Metric | Değer | Durum |
|--------|-------|-------|
| Op sonrası değer | 10000 | — |
| Clamp sonrası değer | 5000 | ✅ |
| `clampedTo5000` | `true` | ✅ |
| Win overlay | Aktif | ✅ |

**Sonuç: ✅ PASSED** (Python BFS ile aynı limit: -500 / 5000)

---

### Test 4: Bölme Bounce (Tam Bölünmezse Geri Git)

**Seviye:** 2×1 grid, op `/3`, startVal=5

| Metric | Değer | Durum |
|--------|-------|-------|
| 5 % 3 | 2 (tam bölünmez) | — |
| Oyuncu pozisyonu | (0, 0) (başlangıç) | ✅ |
| `bouncedToStart` | `true` | ✅ |
| Oyuncu değeri | 5 (korundu) | ✅ |

**Sonuç: ✅ PASSED**

---

### Test 5: Directional Wall + Switch Kombinasyonu

**Seviye:** 3×2 grid, directional wall (1,0) blocks=['E'], switch (0,1)

| Adım | Komut | Beklenen | Sonuç | Durum |
|------|-------|----------|-------|-------|
| E yönünden bounce | `x+` | Oyuncu (0,0)'da kalmalı | `playerX=0, playerY=0` | ✅ |
| Switch sonrası geçiş | `y+` → `y-` → `x+` → `x+` | Hedef (2,0) | `playerX=2, playerY=0` | ✅ |

**Sonuç: ✅ PASSED**

---

### Test 6: maxCmds Kontrolü

**Seviye:** Tüm test seviyelerinde

| Metric | Beklenen | Sonuç | Durum |
|--------|----------|-------|-------|
| `addCommand()` limit | `state.queue.length >= lv.maxCmds` → reject | Tüm testlerde çalıştı | ✅ |

**Sonuç: ✅ PASSED** (Zaten vardı, regression yok)

---

### Test 7: effectiveTargetVal Fallback

**Seviye:** Op var ama `targetVal=null`

| Metric | Beklenen | Sonuç | Durum |
|--------|----------|-------|-------|
| `checkWin()` | `effectiveTargetVal = startVal` (ops varsa) | Doğru çalıştı | ✅ |

**Sonuç: ✅ PASSED** (Zaten vardı, regression yok)

---

## ⚠️ Notlar

### 1. `isBlockedByWall()` — Dead Code
`game.html` satır 696'da `isBlockedByWall(wallMap, nx, ny, dx, dy)` tanımlı ama **hiç çağrılmıyor**. `runProgram()`'da (satır 905+) wall kontrolü inline yapılıyor. Zararsız, ama temizlenebilir.

### 2. `buildWallMap()` vs `runProgram()` wall formatı
- `buildGrid()`'de `buildWallMap()` + `normalizeWall()` kullanılıyor (her format → `{x, y, type, blocks}`)
- `runProgram()`'da `lv.walls.find()` inline kullanılıyor (hem `[x,y]` hem `{x,y,type}` destekler)
- İkisi tutarlı, sorun yok.

### 3. Console Hataları
Test süresince sadece `favicon.ico` 404 hatası görüldü. Oyun motoru hatası **0**.

---

## 📊 Özet

| Test Kategorisi | Test Sayısı | Durum |
|-----------------|-------------|-------|
| Switch render + toggle wall açılma | 2 | ✅ 2/2 |
| Kapalı wall bounce + görsel değişim | 2 | ✅ 2/2 |
| Value clamping (-500 / 5000) | 1 | ✅ 1/1 |
| Bölme bounce (tam bölünmezse geri) | 1 | ✅ 1/1 |
| Directional wall + switch kombinasyonu | 2 | ✅ 2/2 |
| maxCmds limit | 1 | ✅ 1/1 |
| effectiveTargetVal fallback | 1 | ✅ 1/1 |
| **Toplam** | **10** | **✅ 10/10** |

---

**Sonuç: game.html motoru stabil çalışıyor. Tüm yeni özellikler (switch, clamping, bölme bounce) doğru implemente edilmiş.**
