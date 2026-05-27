# AGENTS.md — Sayı Yolculuğu

> **Bu dosyanın rolü:** Nasıl çalışmalıyım? Davranış kuralları, okuma sırası, oturum protokolü.
> **Ne içermez:** Teknik detay (→ SKILL.md), durum/görev (→ CONTEXT.md), tarihçe (→ session log'ları).
> **⚠️ Önemli:** Bu dosya Kimi CLI tarafından **system prompt'a otomatik eklenir**. Uzun olursa token israfı olur. Sadece kalıcı davranış kuralları yazılır; değişken bilgiler .kimi/CONTEXT.md'ye.
---

## 📖 Okuma Sırası (Her Session Başında)

1. **.kimi/CONTEXT.md** — İlk oku. Durum, sıradaki görev, aktif sorunlar.
2. **AGENTS.md** — Kurallar ve protokol (bu dosya).
3. **SKILL.md** — Teknik referans (sadece görev gerektiriyorsa).
4. **Session log'ları** — Son 3 oturum (sadece detay gerekiyorsa).
5. **Kod tabanı** — Yukarıdakiler yeterli olmadığında.

**Token israfı yasak:** Skill'de cevap varken kod tabanını kazmak yasak. Bulduğun bilgiyi skill'e yaz (pay it forward).

---

## 🔄 Çalışma Döngüsü (Acele etmeden dikkat ederek çalışacağım)

1. **İstihbarat** — CONTEXT.md + aktif görevi bilerek başla.
2. **Yuva İncelemesi** — Kaynak kodu oku, kök nedeni anla.
3. **Keşif Görevi** — Bilinen zayıf noktaya hedeflenen test/senaryo üret.
4. **Savaş Alanı Gözlemi** — Plugin, pytest, hook ile test et.
5. **Yeni Bulgu Varsa** — Tekrar koda dön (iterasyon).
6. **Çatışma (Düzeltme)** — Kodu değiştir, **mutlaka** test et.
7. **Döngü** — Başka cephe var mı?

---

## ✏️ Dokümantasyon Kuralı

Her değişiklik sonrası **üç** kaydı güncelle:

| Kayıt | Ne Yazılır | Dosya |
|-------|-----------|-------|
| **Durum** | Görev durumu, yeni kararlar, yeni bug'lar | `CONTEXT.md` |
| **Tarihçe** | Detaylı yapılanlar, bulgular, karar gerekçeleri | `.kimi/logs/YYYY-MM-DD-HHMM-session.md` |
| **Teknik Referans** | Kalıcı bilgi değiştiyse (format, mimari, troubleshooting) | `SKILL.md` |

**Tekrar yasak:** Aynı keşfi, hatayı, çözümü iki kez yapma. Öğrendiğini yaz.

---

## 🛠️ Araç Kullanımı

| Araç | Ne Zaman | Kural |
|------|----------|-------|
| **Plugin** | `validate_level`, `validate_batch`, `analyze_level` işe yararsa | Aynı işi yapan plugin varsa kendin yazma. Plugin sync sonrası mutlaka test et. |
| **Skill** | Teknik bilgiye ihtiyaç duyduğunda | Skill güncel değilse kod tabanından al ve skill'i güncelle |
| **Hook** | `WriteFile`/`StrReplaceFile` sonrası | Varsa tetikle, yoksa manuel çalıştır |
| **pytest** | Python motoru değişince | `../mathlock-play/procedural_levels/tests/` |
| **index.html** | JS motoru değişince | Browser'da `python3 -m http.server` ile test et |
| **editor.html** | Seviye verisi değişince | Tarayıcıda test et |

---

## 🔧 Kod Değişikliği Kuralları

### Android Motor Geliştirme (Tek Kaynak)

| Kaynak | Konum | Test | Senkronizasyon |
|--------|-------|------|----------------|
| **JS motoru** | `js/game-*.js` | `index.html` (browser) | Değişiklik sonrası `../mathlock-play/app/src/main/assets/sayi-yolculugu/js/game-*.js`'e kopyalanmalı |
| **CSS** | `css/game.css` | `index.html` (browser) | Değişiklik sonrası `../mathlock-play/app/src/main/assets/sayi-yolculugu/css/game.css`'ye kopyalanmalı |
| **Statik seviyeler** | `js/levels-data.js` | `index.html` (browser) | Android backend API seviye verisini döner; bu dosya arşiv/referans |
| **Seviye editörü** | `editor.html`, `js/editor.js` | `editor.html` (browser) | Export edilen seviyeler `js/levels-data.js`'e manuel eklenir |

**Senkronizasyon komutu:**
```bash
cp js/game-*.js js/android-bridge.js ../mathlock-play/app/src/main/assets/sayi-yolculugu/js/
cp css/game.css ../mathlock-play/app/src/main/assets/sayi-yolculugu/css/
```

### Python Motor (Procedural Level Generation)

- **Python motoru:** `../mathlock-play/procedural_levels/` altında yapılır. Sonra `pytest`.
- **Cross-cutting:** Hem Python hem JS değişirse, her iki tarafı da test et.
- **Plugin `.py` dosyaları:** Source dizinindeki değişiklik `~/.kimi/plugins/sayi-yolculugu-validator/scripts/` altına `cp` ile senkronize edilmeli (symlink yok).

### Mimari Kurallar

- **Teknik kararlar (K1–K10):** Kalıcı mimari kararlar SKILL.md §4'te. Debug senaryoları ve test şablonları SKILL.md §5–6'da.
- **Modülerlik:** Yeni özellik mevcut `game-*.js` modülüne aitse o modüle ekle. Yeni sorumluluk alanı varsa yeni `game-*.js` dosyası oluştur ve `index.html`'e `<script src="...">` ekle.
- **Android uyumluluğu:** `game-*.js` dosyaları plain JavaScript olmalı (ES module `import`/`export` kullanılmaz). `const`/`let` kullanılabilir (Android WebView Chrome tabanlı).

---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. AGENTS.md oku (bu dosya) | 2. Session log yaz |
| 3. Skill oku (gerekirse) | 3. Skill güncelle (değişiklik varsa) |
| 4. Son 3 log'a göz at (gerekirse) | 4. `pytest` çalıştır (Python değiştiyse) |
| 5. Kullanıcıdan talimat al | 5. Browser test çalıştır (JS değiştiyse) |
| | 6. Git status kontrol et |
