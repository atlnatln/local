# Bir Sonraki Oturum Planı — Oyun Motoru Geliştirme

> **Oturum başlangıcında okunacak ilk dosya.** CONTEXT.md → bu plan → SKILL.md (gerekirse).

---

## 🎯 Oturum Amacı
Oyun motorunu optimize etmek ve stabiliteyi kapsamlı şekilde doğrulamak.

> **Durum: ✅ TÜM GÖREVLER TAMAMLANDI**

---

## 📋 Görev Listesi (Öncelik Sırasına Göre)

### G1: 13MB Dosya Optimizasyonu (P1 — Zorluk Chunking)
**Problem:** `js/generated-levels-10000-v4.js` (13MB) tek dosya. Tarayıcı `import()` ile main thread'de parse ediyor → ilk yüklemede UI donuyor.

**Hedef:** Tek seferde max ~3MB parse edilecek şekilde böl.

**Yaklaşım:**
1. Python script yaz: `levels_10000_v4.json`'ı zorluk seviyesine göre 5 ayrı JS module'ye böl
   - `js/levels-diff1.js` (~2.5MB)
   - `js/levels-diff2.js` (~2.5MB)
   - `js/levels-diff3.js` (~2.5MB)
   - `js/levels-diff4.js` (~2.5MB)
   - `js/levels-diff5.js` (~3MB)
2. `js/state.js`'de dinamik import:
   ```js
   async function loadLevelsByDifficulty(maxDiff) {
     const modules = await Promise.all([
       import('./levels-diff1.js'),
       import('./levels-diff2.js'),
       // ... maxDiff'e kadar
     ]);
     return modules.flatMap(m => m.default || m.LEVELS);
   }
   ```
3. `getLevels()` fonksiyonunu async yap ve loading state ekle
4. IndexedDB cache ile sonraki ziyaretlerde diskten oku

**Başarı kriteri:**
- Lighthouse Performance score ilk yüklemede > 70
- Yaş grubu değiştirildiğinde < 500ms loading
- `generated-levels-10000-v4.js` silinebilir (ya da yedek olarak kalabilir)

---

### G2: Batch Stabilite Testi (Switch Dahil)
**Problem:** 10.000 seviye üretildi ama browser'da batch validate edilmedi.

**Hedef:** 500 rastgele seviyeyi browser BFS solver ile çapraz doğrula.

**Yaklaşım:**
1. Node.js script yaz (Playwright MCP yerine daha hızlı):
   ```bash
   node js/batch-validate.js levels_10000_v4.json --sample 500
   ```
2. Veya Python ile `validate-levels.py`'yi genişlet:
   ```bash
   python3 validate-levels.py --batch generated-levels/levels_10000_v4.json --sample 500
   ```
3. Switch içeren seviyeleri ayrıca validate et
4. Rapor: solvable %, avg solution length, mechanic distribution

**Başarı kriteri:**
- 500/500 seviye çözülebilir
- Switch içeren seviyelerde 0 çözülemez
- Rapor `docs/stability-report-v4.md`'ye yazılır

---

### G3: L6 "Labirent" Statik Seviye Fix
**Problem:** `js/levels-data.js`'deki L6 seviyesi çözülemez (runtime filter tarafından gizleniyor).

**Hedef:** Ya düzelt, ya da kalıcı olarak kaldır.

**Yaklaşım:**
1. `js/levels-data.js`'deki L6 wall konumlarını kontrol et
2. `solveLevel()` ile test et
3. Eğer düzeltilemezse: seviyeyi kaldır veya yeni bir seviye ile değiştir

**Başarı kriteri:**
- 7-8 yaş grubunda tüm statik seviyeler çözülebilir
- Runtime filter 0 seviye gizlemeli

---

### G4: Loading / UX Polish
**Problem:** 13MB parse sırasında kullanıcı boş ekran görüyor.

**Hedef:** Loading indicator ekle.

**Yaklaşım:**
1. `index.html`'de loading spinner div ekle (CSS animation)
2. `state.js`'de `getLevels()` async olduğunda spinner göster/gizle
3. Ses dosyalarını lazy preload et (oyun ekranına geçince)

**Başarı kriteri:**
- Kullanıcı "yükleniyor" görmeli, boş ekran olmamalı
- Ses ilk komut çalıştırıldığında hazır olmalı

---

## 🗂️ Dosya Değişiklik Beklentisi

| Dosya | Değişiklik | Görev |
|-------|-----------|-------|
| `js/state.js` | Major refactor | G1, G4 |
| `js/levels-diff*.js` | Yeni dosyalar (5 adet) | G1 |
| `index.html` | Loading spinner ekle | G4 |
| `css/components.css` | Loading animasyonu | G4 |
| `js/levels-data.js` | L6 fix veya kaldır | G3 |
| `validate-levels.py` | Batch mode ekle | G2 |
| `docs/stability-report-v4.md` | Yeni rapor | G2 |

---

## ⚠️ Bilinen Riskler

1. **Dynamic import browser desteği:** `import()` ES2015+, eski tarayıcılarda polyfill gerekir. Ama hedef kitle modern tarayıcı (5-12 yaş oyunu).
2. **IndexedDB async complexity:** `getLevels()` sync → async değişimi tüm çağrı noktalarını etkiler. Özellikle `command-system.js` ve `ui-overlays.js`'de `getLevel()` çağrıları var.
3. **Cache invalidation:** v4 → v5 geçişinde IndexedDB cache temizlenmeli.

---

## 🔗 Bağlantılar
- Durum: `CONTEXT.md`
- Kurallar: `AGENTS.md`
- Teknik referans: `SKILL.md`
- Tarihçe: `.kimi/logs/2026-05-27-*.md`
