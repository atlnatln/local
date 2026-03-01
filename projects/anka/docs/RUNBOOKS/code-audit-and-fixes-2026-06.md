# Kod Denetimi ve Düzeltme Raporu — Haziran 2026

**Denetim Tarihi:** Haziran 2026  
**Kapsam:** Uçtan uca kullanıcı akışı simülasyonu (Login → Batch → Ödeme → Export → Dashboard)  
**Yöntem:** Tüm backend ve frontend kodları okunarak kullanıcı perspektifinden akış simüle edildi; tespit edilen sorunlar ciddiyetine göre sınıflandırılıp düzeltildi.

---

## Özet Tablo

| Seviye | Bulgu | Düzeltilen |
|--------|-------|-----------|
| **KRİTİK** | 4 | 4 ✅ |
| **ORTA** | 3 | 3 ✅ |
| **UX/Frontend** | 2 | 2 ✅ |

---

## KRİTİK BULGULAR

### KRİTİK-1: Ödeme Sonrası Kredi Hiç Yansımıyor ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/payments/models.py` — `PaymentIntent.mark_completed()`

**Sorun:**  
`mark_completed()` metodu `self.save()` çağrısını `update_fields` parametresi olmadan yapıyordu. Ancak kredi yansıması mantığı `payments/signals.py` içindeki `post_save` signal'ında şu guard ile korunuyor:

```python
if created or not update_fields or 'status' not in update_fields:
    return
```

`update_fields=None` olduğunda (`self.save()` parametresiz çağrıldığında) signal erken çıkış yapıyor ve **kullanıcıya ödeme sonrası kredi hiçbir zaman yansımıyordu**.

**Etki:** Kullanıcılar ödeme yapıyor ama kredi bakiyesi artmıyordu. Kritik iş akışı tamamen kırıktı.

**Düzeltme:**
```python
# Önce:
self.save()

# Sonra:
self.save(update_fields=['status', 'completed_at', 'updated_at'])
```

---

### KRİTİK-2: Webhook Refund Handler'da Yanlış Field Adı ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/payments/webhooks.py` — `_handle_payment_refunded()`

**Sorun:**  
```python
transaction_obj.payment_intent.status = 'cancelled'
```
`PaymentTransaction` modelinde `PaymentIntent`'e FK ilişkisi `related_name='transactions'` ile tanımlı ve field adı `intent`. Dolayısıyla `transaction_obj.payment_intent` çağrısı `AttributeError` fırlatıyordu.

**Etki:** Refund webhook'u her zaman 500 hatası ile başarısız oluyordu.

**Düzeltme:**
```python
transaction_obj.intent.status = 'cancelled'
```

---

### KRİTİK-3: Webhook'ta Geçersiz Status Değerleri ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/payments/webhooks.py` — `_handle_payment_refunded()`

**Sorun:**  
Handler, `PaymentTransaction.status` ve `PaymentIntent.status` değerlerini `'REFUNDED'` olarak atıyordu. Ancak her iki modelin `STATUS_CHOICES` tanımında `'REFUNDED'` geçerli bir seçenek değil:

- `PaymentTransaction.STATUS_CHOICES`: pending, authorized, success, declined, error
- `PaymentIntent.STATUS_CHOICES`: pending, completed, failed, cancelled

**Etki:** Veritabanına geçersiz status değeri yazılıyordu; `full_clean()` validasyonları atlansa bile raporlama ve filtreleme bozuluyordu.

**Düzeltme:**
```python
# Transaction için: 'REFUNDED' → 'error'
# Intent için: 'REFUNDED' → 'cancelled'
```

---

### KRİTİK-4: Webhook'ta Variable Shadow (status) ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/payments/webhooks.py`

**Sorun:**  
```python
status = data.get('status')  # webhook payload'dan gelen
```
Bu atama, `from rest_framework import status` import'unu gölgeliyordu. Dosyanın geri kalanında `status.HTTP_200_OK` gibi çağrılar beklenmedik hatalara yol açabilirdi.

**Düzeltme:** Değişken adı `iyzico_status` olarak değiştirildi.

---

## ORTA SEVİYE BULGULAR

### ORTA-1: Katalog Endpoint'lerinde Yetkilendirme Eksikliği ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/catalog/views.py`

**Sorun:**  
`CityViewSet`, `SectorViewSet` ve `FilterDefinitionViewSet` hepsi `IsAuthenticatedOrReadOnly` permission kullanıyordu. Bu, herhangi bir oturum açmış kullanıcının şehir, sektör ve filtre tanımlarını oluşturmasına, güncellemesine ve silmesine olanak tanıyordu.

**Etki:** Normal kullanıcılar katalog verilerini bozabilir veya silebilirdi.

**Düzeltme:** `_ReadOnlyOrAdmin` mixin eklendi:
- `list`, `retrieve` → `IsAuthenticatedOrReadOnly` (herkes okuyabilir)
- `create`, `update`, `partial_update`, `destroy` → `IsAdminUser` (sadece admin)

---

### ORTA-2: SIMPLE_JWT Ayarlarında Tekrarlanan Anahtar ✅ DÜZELTİLDİ

**Dosya:** `services/backend/project/settings/base.py`

**Sorun:**  
`SIMPLE_JWT` sözlüğünde `'JTI_CLAIM': 'jti'` iki kez tanımlanmıştı. Python'da dict'te tekrarlanan anahtar sessizce son değeri alır — bu durumda işlevsel hata yok ancak bakım sırasında kafa karıştırıcı.

**Düzeltme:** Tekrarlanan satır kaldırıldı.

---

### ORTA-3: Confirm View'da payment_id Kaybı ✅ DÜZELTİLDİ

**Dosya:** `services/backend/apps/payments/views.py` — `confirm` action

**Sorun:**  
```python
payment_intent.payment_id = iyzico_response['paymentId']
payment_intent.mark_completed()  # sadece status, completed_at, updated_at kaydeder
```
`mark_completed()` düzeltildikten sonra `save(update_fields=['status', 'completed_at', 'updated_at'])` çağrıyor — bu da `payment_id` alanını kaydetmiyordu.

**Düzeltme:** `payment_id` ayrı bir `save(update_fields=['payment_id', 'updated_at'])` çağrısıyla önce kaydedilir, ardından `mark_completed()` çağrılır:
```python
payment_intent.payment_id = iyzico_response.get('paymentId', '')
payment_intent.save(update_fields=['payment_id', 'updated_at'])
payment_intent.mark_completed()  # signal kredi yansıtır
```

---

## UX / FRONTEND İYİLEŞTİRMELERİ

### UX-1: Batch Detay — Export Geri Bildirimi ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/batch/[id]/page.tsx`

**Eski Durum:**  
"Export Oluştur" butonuna tıklandığında başarı/hata durumunda kullanıcıya hiçbir görsel geri bildirim verilmiyordu (sadece `console.error`).

**Yeni Durum:**
- Başarılı export oluşturmada **toast bildirim** gösterilir ("Export başarıyla oluşturuldu")
- Hata durumunda **hata toast'ı** gösterilir
- Export oluşturulduktan sonra buton "İndirilmişlere Git" linkine dönüşerek `/exports` sayfasına yönlendirir
- `ExternalLink` ikonu ile görsel ipucu sağlanır

---

### UX-2: Dashboard — Son İndirmeler Kartı ✅ DÜZELTİLDİ

**Dosya:** `services/frontend/app/(dashboard)/dashboard/page.tsx`

**Eski Durum:**  
Dashboard'da sadece kredi bakiyesi ve son batch'ler gösteriliyordu. Export bilgisi yoktu.

**Yeni Durum:**
- Dashboard yüklenirken `/exports/` endpoint'i de paralel olarak çekilir
- "Son İndirmeler" kartı eklendi (son 3 export gösterilir):
  - Format badge'i (XLSX: yeşil, CSV: mavi)
  - İlişkili batch'in şehir-sektör bilgisi
  - Durum göstergesi (Hazır / İşleniyor / Hata) animasyonlu badge ile
  - Oluşturulma tarihi
  - "Tümünü Gör" linki → `/exports` sayfasına  

**ADR Uyumu:** Bu değişiklik ADR-0005'te belirtilen "dashboard'da son 3 batch ve son 3 export gösterilmeli" gereksinimini karşılar.

---

## İlgili Dosyalar

| Dosya | Değişiklik |
|-------|-----------|
| `services/backend/apps/payments/models.py` | `mark_completed()` — `update_fields` eklendi |
| `services/backend/apps/payments/webhooks.py` | Field adı, status değerleri, variable shadow düzeltmeleri |
| `services/backend/apps/payments/views.py` | `confirm` — payment_id ayrı save, gereksiz satır kaldırıldı |
| `services/backend/apps/catalog/views.py` | `_ReadOnlyOrAdmin` mixin eklendi |
| `services/backend/project/settings/base.py` | Tekrarlanan `JTI_CLAIM` kaldırıldı |
| `services/frontend/app/(dashboard)/batch/[id]/page.tsx` | Toast + export sonrası yönlendirme |
| `services/frontend/app/(dashboard)/dashboard/page.tsx` | Son İndirmeler kartı + export fetch |

---

## Öneriler (Gelecek İyileştirmeler)

1. **Backend Testleri:** `payments/signals.py` için signal-based credit granting'i doğrulayan integration test yazılmalı.
2. **Webhook Replay:** `payments-webhook-replay.md` runbook'unda anlatılan replay mekanizması refund senaryosunu da test etmeli.
3. **Frontend E2E:** Ödeme → kredi yansıması → batch oluşturma → export indirme akışı Playwright ile test edilmeli.
4. **Rate Limit Monitoring:** Catalog endpoint'lerine eklenen admin kısıtlamasının beklenmedik 403 hatalarına yol açmadığı doğrulanmalı.
