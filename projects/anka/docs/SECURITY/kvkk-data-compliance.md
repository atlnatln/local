# KVKK / GDPR Veri Uyumluluk Rehberi

**Son Güncelleme:** 28 Şubat 2026  
**Yasal Dayanak:** 6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK)  
**Kapsam:** Anka Platform'un işlediği tüm kişisel veriler

---

## 1. Veri Sınıflandırması

### 1.1 İşlenen Kişisel Veriler

| Veri Kategorisi | Veri Türü | Kaynak | Saklama Süresi | Hassasiyet |
|----------------|-----------|--------|---------------|-----------|
| **Kimlik** | Ad, Soyad | Google OIDC | Hesap aktif + 1 yıl | Orta |
| **İletişim** | Email adresi | Google OIDC | Hesap aktif + 1 yıl | Orta |
| **Profil** | Google profil resmi URL | Google OIDC | Hesap aktif | Düşük |
| **İşlem** | Batch sorgu geçmişi | Uygulama | 2 yıl | Orta |
| **Finansal** | Ödeme geçmişi (İyzico referansları) | İyzico | 10 yıl (yasal zorunluluk) | Yüksek |
| **Kredi** | Kredi bakiyesi, ledger kayıtları | Uygulama | 10 yıl (yasal zorunluluk) | Yüksek |
| **Teknik** | IP adresi, User-Agent | Nginx/Django log | 90 gün | Düşük |
| **Arama** | Sektör seçimleri, lokasyon verileri | Uygulama | Batch ile birlikte | Orta |

### 1.2 İşlenmeyen Veriler

- ❌ Kredi kartı numarası (İyzico tarafında saklanır, Anka'da **asla** tutulmaz)
- ❌ TC Kimlik No
- ❌ Biyometrik veri
- ❌ Sağlık verisi
- ❌ Ceza mahkumiyeti verisi

## 2. Veri İşleme Temelleri

### 2.1 Hukuki Dayanak (KVKK Md. 5)

| Veri | İşleme Amacı | Hukuki Dayanak |
|------|-------------|----------------|
| Email, Ad/Soyad | Hesap oluşturma ve yönetim | **Sözleşmenin ifası** |
| Batch sorguları | Hizmet sunumu | **Sözleşmenin ifası** |
| Ödeme bilgileri | Faturalandırma | **Yasal yükümlülük** |
| IP adresi, log | Güvenlik ve hata tespiti | **Meşru menfaat** |
| Email (pazarlama) | Ürün güncellemeleri | **Açık rıza** (opt-in) |

### 2.2 Veri Minimizasyonu İlkesi

- Sadece hizmet sunumu için **zorunlu** olan veriler toplanır
- Google OIDC'den sadece `email`, `name`, `picture` scope'ları istenir
- Batch sonuçlarında toplanan işyeri verileri **kamuya açık** kaynaklardan elde edilir

## 3. Teknik Koruma Önlemleri

### 3.1 Aktif Korumalar

| Önlem | Durum | Detay |
|-------|-------|-------|
| İletim şifreleme (TLS 1.2/1.3) | ✅ | HTTPS zorunlu, HSTS aktif |
| Parola hash'leme | ✅ | Django PBKDF2 (iteration: 720000) |
| JWT token şifreleme | ✅ | HS256 |
| Session güvenliği | ✅ | Secure, HttpOnly, SameSite cookie |
| Veritabanı erişim kontrolü | ✅ | Docker internal network, parola korumalı |
| Log'da PII maskeleme | ⚠️ | Kısmen — email maskeleme eklenmeli |
| Yedek şifreleme | ⚠️ | TODO — AES-256 ile backup şifreleme |

### 3.2 Sentry / Error Tracking

```python
sentry_sdk.init(
    send_default_pii=False,  # ✅ PII gönderme devre dışı
)
```

Sentry'ye kullanıcı IP, cookie, request body **gönderilmez**.

## 4. Veri Saklama ve Silme Politikası

### 4.1 Saklama Süreleri

| Veri | Saklama Süresi | Silme Yöntemi |
|------|---------------|---------------|
| Kullanıcı hesap bilgileri | Hesap aktif + 1 yıl | Hard delete + audit log |
| Batch/sorgu geçmişi | 2 yıl | Soft delete → 6 ay sonra hard delete |
| Ödeme kayıtları | 10 yıl | Yasal süre sonrası hard delete |
| Nginx access log'ları | 90 gün | Log rotation ile otomatik |
| Django uygulama log'ları | 90 gün | Docker log rotation |
| Redis cache | TTL-based | Otomatik expire |

### 4.2 Hesap Silme Prosedürü

Kullanıcı hesap silme talebinde bulunduğunda:

```
1. [ ] Kullanıcı kimliğini doğrula
2. [ ] Aktif batch/ödeme işlemi var mı kontrol et
3. [ ] Kullanıcı verilerini dışa aktar (data portability)
4. [ ] İlişkili verileri anonimleştir veya sil:
   - Profil bilgileri → Hard delete
   - Batch geçmişi → user_id NULL yapılır (anonimleştirme)
   - Ödeme kayıtları → 10 yıl saklama (yasal zorunluluk)
   - Session/token → Blacklist + sil
5. [ ] Redis cache temizle
6. [ ] Silme işlemini audit log'a kaydet
7. [ ] Kullanıcıya silme onayı gönder
8. [ ] 30 gün beklet (geri alınabilirlik)
9. [ ] 30 gün sonra kalıcı silme
```

### 4.3 Veri Silme Script Örneği

```python
from django.contrib.auth.models import User
from apps.batches.models import Batch
from apps.ledger.models import LedgerEntry

def anonymize_user(user_id: int):
    """KVKK uyumlu kullanıcı anonimleştirme"""
    user = User.objects.get(id=user_id)
    
    # Batch'leri anonimleştir
    Batch.objects.filter(user=user).update(user=None)
    LedgerEntry.objects.filter(user=user).update(user=None)
    
    # Profili sil
    if hasattr(user, 'profile'):
        user.profile.delete()
    
    # Kullanıcıyı anonimleştir
    user.email = f"deleted_{user.id}@anonymized.local"
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.set_unusable_password()
    user.save()
    
    return True
```

## 5. Veri İhlali Bildirim Prosedürü

KVKK Md. 12/5 uyarınca, kişisel veri ihlali durumunda:

### 5.1 İç Bildirim (İlk 24 saat)

```
1. [ ] İhlali tespit et ve doğrula
2. [ ] İhlal kapsamını belirle (etkilenen kişi sayısı, veri türleri)
3. [ ] Olay müdahale planını aktive et (incident-response-playbook.md)
4. [ ] Yönetimi bilgilendir
```

### 5.2 KVKK Kurulu Bildirimi (72 saat içinde)

```
1. [ ] KVK Kurulu'na yazılı bildirim hazırla:
   - İhlalin ne zaman gerçekleştiği
   - Etkilenen kişisel veri kategorileri
   - Etkilenen kişi sayısı (veya tahmini)
   - İhlalden kaynaklanabilecek olumsuz etkiler
   - Alınan/alınacak önlemler
2. [ ] VERBİS üzerinden / yazılı olarak bildirim gönder
```

### 5.3 İlgili Kişilere Bildirim

```
1. [ ] Etkilenen kullanıcılara email ile bildirim
2. [ ] Bildirimin içeriği:
   - İhlalin açıklaması
   - Etkilenen veriler
   - Alınan önlemler
   - Kullanıcının alabileceği önlemler
   - İletişim bilgileri
```

## 6. Üçüncü Taraf Veri İşleyenler

| Üçüncü Taraf | İşlenen Veri | Amaç | Lokasyon |
|--------------|-------------|------|----------|
| Google (OIDC) | Email, ad | Kimlik doğrulama | AB/ABD |
| Google Places API | Konum sorguları | İşyeri verisi toplama | AB/ABD |
| İyzico | Ödeme referansları | Ödeme işleme | Türkiye ✅ |
| Sentry (opsiyonel) | Hata detayları (PII yok) | Error tracking | AB |
| Postmark | Email adresleri | Transactional email | AB/ABD |

### 6.1 Veri Aktarımı Güvenceleri

- Google, İyzico: KVKK Md. 9 kapsamında yeterli koruma (SCCs / BCRs)
- Sentry: `send_default_pii = False` — PII aktarılmıyor
- Tüm aktarımlar TLS üzerinden şifreli

## 7. Veri Sahiplerinin Hakları (KVKK Md. 11)

| Hak | Uygulama Yöntemi |
|-----|-----------------|
| Bilgi alma | Kullanıcı profil sayfasında veri özeti |
| Düzeltme isteme | Profil düzenleme, destek talebi |
| Silme isteme | Hesap silme flowu (Bölüm 4.2) |
| Veri taşınabilirliği | JSON/CSV export özelliği |
| İtiraz etme | Destek kanalı üzerinden |
| Otomatik karar karşıtlığı | Batch sonuçları tamamen deterministik (AI karar yok) |

## 8. Periyodik Kontroller

| Kontrol | Sıklık | Sorumlu |
|---------|--------|---------|
| Veri envanteri güncelleme | 6 ayda bir | Proje yöneticisi |
| Saklama süresi aşımı kontrol | Aylık | Backend dev |
| Log retention politikası | 3 ayda bir | DevOps |
| Üçüncü taraf sözleşme review | Yıllık | Proje yöneticisi |
| KVKK uyumluluk denetimi | Yıllık | Dış danışman |
| Bu belgenin gözden geçirilmesi | 6 ayda bir | Tüm ekip |
