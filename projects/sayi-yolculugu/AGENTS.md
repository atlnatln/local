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

## 🔄 Çalışma Döngüsü (Yuva Keşfi ↔ Savaş Alanı) (Acele etmeden dikkat ederek çalışacağım)

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
| **editor.html** | JS motoru değişince | Tarayıcıda test et |

---

## 🔧 Kod Değişikliği Kuralları

- **Python motoru:** `../mathlock-play/procedural_levels/` altında yapılır. Sonra `pytest`.
- **JS motoru:** `js/` altında yapılır. Sonra `editor.html`'de test et.
- **Cross-cutting:** Hem Python hem JS değişirse, her iki tarafı da test et.
- **Plugin `.py` dosyaları:** Source dizinindeki değişiklik `~/.kimi/plugins/sayi-yolculugu-validator/scripts/` altına `cp` ile senkronize edilmeli (symlink yok).
- **Dosya optimizasyonu:** Mevcut dosyayı büyüklük olarak optimize etmen gerekiyorsa modüler hale getir, oyun motoru için yeni bir dosyaya ihtiyaç olursa/gerekiyorsa yarat
- **Teknik kararlar (K1–K10):** Kalıcı mimari kararlar SKILL.md §4'te. Debug senaryoları ve test şablonları SKILL.md §5–6'da.
---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. AGENTS.md oku (bu dosya) | 2. Session log yaz |
| 3. Skill oku (gerekirse) | 3. Skill güncelle (değişiklik varsa) |
| 4. Son 3 log'a göz at (gerekirse) | 4. `pytest` çalıştır |
| 5. Kullanıcıdan talimat al | 5. Git status kontrol et |
