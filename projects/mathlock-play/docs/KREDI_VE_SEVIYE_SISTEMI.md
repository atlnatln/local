# Kredi ve Seviye İlerleme Sistemi — Tasarım Dokümanı

> **Amaç:** Sayı Yolculuğu ve Matematik Problemleri modüllerinde; kredi, seviye seti ve ilerleme kaydının nasıl çalışması gerektiğini tanımlar. Bu doküman hem mevcut hataların kök nedenini açıklar hem de sektör standartlarına uygun hedef mimariyi belirtir.
> 
> **Son güncelleme:** 26 Nisan 2026 — Celery + Redis, i18n, stale lock cleanup

---

## 1. Sektör Standardı (Hedef Mimari)

Freemium oyunlarda yaygın kullanılan **"Set Bazlı İlerleme + Kredi Kilidi"** modeli:

| Durum | Beklenen Davranış |
|-------|-------------------|
| **İlk açılış** | Kullanıcıya ücretsiz 12 seviyelik ilk set verilir. |
| **Set içinde ilerleme** | Tamamlanan seviyeler kalıcı olarak kaydedilir. Uygulama kapatılıp açılsa bile **kaldığı seviyeden devam eder**. |
| **Set tamamlandı, kredi var** | Otomatik (veya manuel) olarak yeni 12 seviyelik set oluşturulur. 1 kredi düşülür. |
| **Set tamamlandı, kredi yok** | Yeni set oluşturulmaz. Kullanıcıya "kredi gerekli" mesajı gösterilir. Ama mevcut setteki ilerleme korunur; kullanıcı istediği seviyeyi **tekrar oynayabilir**. |
| **Hesap kurtarma** | Email ile başka cihaza geçişte; kredi bakiyesi, çocuk profili, tamamlanan seviyeler ve aktif set **eksiksiz aktarılır**. |

### 1.1 Kritik Kural
> **Seviye ID'leri set başına izole olmalıdır.** Aynı ID (örn: "seviye 1") farklı setlerde tekrar kullanılabilir; bu nedenle ilerleme kaydı **set_id + seviye_id** çiftiyle birlikte tutulmalıdır.

---

## 2. Mevcut Sistemdeki Hatalar

### 2.1 Hata #1 — Set Değişiminde Eski İlerleme Yeni Sete Sızıyor
**Yer:** `SayiYolculuguActivity.fetchLevels()`  
**Neden:** `fetchLevels()` metodunda "local merge" mantığı, eski setin tamamlanmış seviye ID'lerini (1..12) yeni sete de uyguluyor. Her sette seviye ID'leri aynı (1..12) olduğundan, yeni set açıldığında sanki hepsi tamamlanmış gibi görünüyor.

**Sonuç:**
- Kullanıcı yeni set açtığında anında "Tüm seviyeler tamamlandı" ekranı görür.
- `showCreditRequired()` tetiklenir.
- Kullanıcı "tekrar oyna" dediğinde `game.html` içinde `isCompleted = true` olduğu için `clearGameState()` çalışır ve seviye 1'den başlar.

**Durum:** ✅ Düzeltildi. Artık `isNewSet` kontrolü ile yeni set yüklendiğinde local tamamlanmış seviyeler temizleniyor.

---

### 2.2 Hata #2 — `activeChildId` Hiç Kaydedilmiyor
**Yer:** `AccountManager.getOrRegister()`  
**Neden:** Cihaz kayıt yanıtında dönen `children[i].id` değeri `PreferenceManager.activeChildId`'ye atılmıyor.

**Sonuç:**
- Tüm API isteklerinde `child_id=0` (veya hiç) gönderiliyor.
- Backend `child_id` olmadığında `device.children.filter(is_active=True).first()` ile buluyor; şu an için tek çocuk profili olduğundan şanslı çalışıyor ama çoklu profil aktif olduğunda yanlış profilin verisine ulaşılacak.

**Durum:** ✅ Düzeltildi. `getOrRegister()` içinde `prefManager.activeChildId = c.optInt("id", 0)` eklendi.

---

### 2.3 Hata #3 — Hesap Kurtarmada `LevelSet` Kayboluyordu
**Yer:** `credits/views.py::register_email()`  
**Neden:** Email ile yeni cihaza geçişte `QuestionSet` ve `ChildProfile` taşınıyordu ama `LevelSet` taşınmıyordu. Eski `ChildProfile` silinince CASCADE ile `LevelSet`'ler de siliniyordu.

**Sonuç:** Kullanıcı email ile başka telefonda giriş yaptığında tüm seviye ilerlemesi sıfırlanıyordu.

**Durum:** ✅ Düzeltildi. `child.level_sets.update(child=existing_child)` satırı eklendi.

---

### 2.4 Hata #4 — AI Üretimi Başarısız Olunca Yeni Set Oluşturulmuyor
**Yer:** `credits/views.py::_auto_renew_levels()`  
**Neden:** `ai-generate-levels.sh` zaman aşımına uğradığında (`600sn`) veya başka bir hata verdiğinde background thread exception ile çıkıyor. Kredi iade ediliyor ama yeni set oluşturulmuyor.

**Sonuç:** Kullanıcı seti bitirdikten sonra sonsuza kadar "kredi gerekli" ekranında kalıyor; yeni set hiç gelmiyor.

**Durum:** ✅ Düzeltildi. Arka plan üretimi artık `threading.Thread` yerine **Celery task kuyruğu** üzerinden çalışıyor. `generate_level_set.delay()` ve `generate_question_set.delay()` ile Redis broker üzerinden reliable işlem yapılıyor. Task `max_retries=3`, hata durumunda kredi iade + kilit serbest bırakma `finally` bloğunda garanti altında.

---

## 3. Veri Modeli Özeti

```
Device (cihaz)
  └─ ChildProfile (çocuk)
       ├─ locale: 'tr' | 'en'                        # YENİ: UI dili
       ├─ education_period: 'sinif_2' | ...          # Eğitim dönemi
       ├─ LevelSet (12 seviyelik bulmaca seti) [v1, v2, v3...]
       │      └─ completed_level_ids: [1, 3, 7, ...]
       │
       ├─ QuestionSet (50 soruluk matematik seti) [v1, v2, v3...]
       │      └─ solved_ids: [5, 12, 33, ...]
       │
       └─ CreditBalance (cihaz başına)
              └─ balance: 0, total_purchased: 0, total_used: 0
```

---

## 4. API Akışları

### 4.1 Cihaz Kaydı (i18n Destekli)
```
POST /api/mathlock/register/
Body: {"installation_id": "...", "device_token": "...", "locale": "en"}
→ {"device_token": "...", "children": [{"id": 1, "name": "Child", "locale": "en"}]}
```
`locale` opsiyoneldir; varsayılan `'tr'`. Kayıt sonrası çocuk profili bu `locale` ile oluşturulur.

### 4.2 Seviye Seti Çekme (i18n Destekli)
```
GET /api/mathlock/levels/?device_token=<uuid>&child_id=<id>&locale=en
→ {"levels": [...], "set_id": 30, "completed_level_ids": [2, 5], ...}
```
`locale` parametresi ile `fallback-levels.{locale}.json` üzerinden varsayılan set döndürülür.

### 4.3 İlerleme Gönderme
```
POST /api/mathlock/levels/progress/
Body: {"device_token": "...", "set_id": 30, "completed_level_ids": [2, 5, 7]}
→ {"success": true, "all_completed": false}
```

### 4.4 Set Tamamlandığında (Kredili Yenileme + Celery)
```
POST /api/mathlock/levels/progress/
Body: {"device_token": "...", "set_id": 30, "completed_level_ids": [1..12]}
→ {"success": true, "all_completed": true, "auto_renewal_started": true, "job_id": "abc-123"}

# Arka planda:
# _auto_renew_levels() → generate_level_set.delay() → Celery worker → LevelSet v2 oluştur
# Durum sorgusu: GET /api/mathlock/jobs/abc-123/status/
```

---

## 5. Yenileme Kilidi (RenewalLock) — Güvenlik ve Temizlik

```python
_RENEWAL_LOCK_TTL = 20 * 60  # 20 dakika (saniye)
```

| Özellik | Açıklama |
|---------|----------|
| **Atomic işlem** | `transaction.atomic()` içinde kilit alınır + kredi düşülür |
| **Stale lock cleanup** | 2×TTL (40 dk) eski kilitler otomatik silinir (`created_at__lt=very_old`) |
| **Sunucu çökme dayanıklılığı** | Kilit 20 dk sonra `expires_at` ile geçersiz sayılır; sonraki istek yeni üretim başlatır |
| **Celery entegrasyonu** | Task `finally` bloğunda `_release_renewal_lock()` çağrılır |

---

## 6. Android Tarafı — Önemli Kurallar

| Kural | Açıklama |
|-------|----------|
| **Set izolasyonu** | Her `set_id` değişiminde `SharedPreferences` içindeki `completed_level_ids` temizlenmelidir. `initGame` payload'unda `forceClear: true` gönderilir. |
| **Local + Server merge** | Sadece **aynı set** için yapılmalı; farklı setlerde merge yapılmamalı. |
| **Child ID** | `AccountManager.getOrRegister()` sonrası `activeChildId` mutlaka kaydedilmeli. |
| **WebView localStorage** | `game.html` içindeki `signature` (`set_id` bazlı) sayesinde kaldığı yerden devam eder. Eğer `completedIds` içinde kaldığı seviye varsa, `clearGameState()` çalışmamalı. |
| **Locale** | `initGame` payload'unda `locale` (tr/en) gönderilir; `game.html` `I18N` sözlüğüne göre UI render eder. |
| **Polling** | Yeni set üretimi için 10 dakika boyunca 5 saniyede bir sorgu (`120 × 5s = 10 dk`). `pollForNewSet(attempt >= 120)` ise hata gösterilir. |
| **onDestroy cleanup** | `SayiYolculuguActivity.onDestroy()` içinde WebView `localStorage` + `SharedPreferences` temizlenir. |

---

## 7. Arka Plan Üretim Mimarisi (Celery + Redis)

```
Android → POST /levels/progress/ (tüm seviyeler bitti)
   ↓
Backend → _deduct_credit_and_lock() → RenewalLock + kredi düş
   ↓
Backend → generate_level_set.delay(child_pk, cb_pk, ...)
   ↓
Redis Broker → Celery Worker (mathlock_celery container)
   ↓
_kimi-cli_ → AI üretim → LevelSet kaydet → Kilit serbest bırak
```

**Servisler:**
- `mathlock_redis`: Redis 7 broker + result backend
- `mathlock_celery`: `celery -A mathlock_backend worker -l info`

**Task özellikleri:**
- `max_retries=3`, hata durumunda 60 saniye sonra retry
- `finally` bloğunda kilit serbest bırakma garanti altında
- Hata durumunda ücretli set için kredi otomatik iade

---

## 8. Özet

Kullanıcının istediği mantık (**kredi varsa yeni set, yoksa mevcut sette kaldığı yerden devam**) sektörde standart bir Freemium modelidir. Mevcut sistemdeki temel problem, **set değişimlerinde ilerlemenin izole edilmemesidir**. Yapılan düzeltmelerle:

1. Yeni set açıldığında eski tamamlanmış seviyeler temizleniyor (`forceClear`).
2. `activeChildId` doğru kaydediliyor.
3. Hesap kurtarmada `LevelSet` de taşınıyor.
4. AI üretimi Celery + Redis ile reliable hale getirildi; thread crash sorunu ortadan kalktı.
5. 20 dk TTL + stale lock cleanup ile sunucu çökme dayanıklılığı sağlandı.
6. i18n (tr/en) desteği eklendi; tüm kullanıcı yüzeyi dilde tutarlı.
