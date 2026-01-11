# Google Search Console Raporu - tarimimar.com.tr
**Tarih:** 4 Ocak 2026  
**Domain:** tarimimar.com.tr  
**Rapor Tarihi:** Son güncelleme 3.01.2026

---

## 📊 Özet ve Genel Durumu

Webimar projesi (tarimimar.com.tr) Google Search Console'da **ciddi sorunlar** yaşamaktadır. Önemli Web Verileri (Core Web Vitals), indeksleme ve tarama konularında iyileştirme gerektiren durum tespit edilmiştir.

---

## 🔴 ÖNEMLI WEB VERİLERİ (Core Web Vitals) - **UYARI**

### Genel Durum
- **Son Güncelleme:** 3.01.2026
- **Veri Kaynağı:** Chrome Kullanıcı Deneyimi Raporu

### MOBİL CİHAZ RAPORU (Kritik)
| Metrik | Durum | Sayı | Trend |
|--------|-------|------|-------|
| **Yetersiz URL** | ✅ İyi | 0 | Sabit |
| **İyileştirme Gerektiren** | ⚠️ **SORUN** | **50** | Sabit |
| **İyi URL** | ❌ Kötü | 0 | Sabit |

#### Tespit Edilen Sorun
**INP (Interaction to Next Paint) Sorunu: 200ms. Değerinden Uzun (Mobil)**
- **Etkilenen URL Sayısı:** 50 adet
- **İlk Tespit Tarihi:** 11.12.2025
- **Doğrulama Durumu:** Başlatılmadı
- **Önem Seviyesi:** İyileştirme Gerektiriyor

#### Etkilenen Ana Sayfalar
1. **https://tarimimar.com.tr/sigir-ahiri-kapasite-hesaplama/**
   - Etkilenen URL: 45 adet
   - INP Değeri: **203 ms** (Sınırı aşmış)

2. **https://tarimimar.com.tr/documents/tarim-arazileri-kullanimi-genelgesi**
   - Etkilenen URL: 5 adet
   - INP Değeri: **201 ms** (Sınırı aşmış)

### MASAÜSTÜ CİHAZ RAPORU (İyi)
| Metrik | Durum | Sayı |
|--------|-------|------|
| **Yetersiz URL** | ✅ | 0 |
| **İyileştirme Gerektiren** | ✅ | 0 |
| **İyi URL** | ✅ | 50 |

Masaüstü kullanıcıları için hiçbir sorun yoktur.

### INP Sorunu Detayları ve Çözüm Önerileri

**INP (Interaction to Next Paint) Nedir?**
- Kullanıcının bir sayfada etkileşim (tıklama, yazma, vb.) yaptığı andan sayfa yanıt verene kadar geçen süre
- Google'a göre ideal INP < 200ms olmalı
- Sınırı aşması, sayfanın yavaş ve cevapsız hissedilmesine neden olur

**Etkilenen Sayfa:** `/sigir-ahiri-kapasite-hesaplama/`
- **Sorun:** Bu hesaplama aracı (React SPA) büyük olasılıkla ağır JavaScript işlemleri yapıyor
- **Root Cause:** React render işlemleri, state yönetimi veya form girdileri işlenirken ana thread bloklanıyor

**Çözüm Önerileri (Öncelik Sırasıyla):**
1. **JavaScript Optimizasyonu**
   - React component'leri `useMemo` ile memoize edin
   - Ağır hesaplamalar Web Worker'a taşıyın
   - Bakın: copilot-instructions.md `- webimar-react/` sektion

2. **Code Splitting**
   - Hesaplama formlarını lazy-load edin
   - Bundle boyutunu azaltmak için tree-shaking uygulayın

3. **Event Handler Optimizasyonu**
   - `onChange` event handler'larında debounce/throttle kullanın
   - Gereksiz re-render'ları kaldırın

4. **Hızlı İyileştirme**
   - Form input validation'ını debounce edin
   - Büyük listeleri virtualize edin

5. **Server-Side Rendering Alternatifi**
   - Next.js SSR kullanarak hesaplama sonuçlarını pre-render etmeyi düşünün

---

## 📑 İNDEKSLEME SORUNLARI (Index Coverage)

### Genel Durum
- **Dizine Eklenen Sayfalar:** 201
- **Dizine Eklenmeyen Sayfalar:** 125 (**%38 ORANINDA İNDEKSLENMEDİ**)
- **Son Güncelleme:** 23.12.2025
- **Rapor Durumu:** ⚠️ Dahili sorunlar nedeniyle bu rapor güncellenemedi

### Dizine Eklenen Sayfalar (201)
✅ Başarılı indeksleme sayılsa da oransal olarak yetersiz.

### Dizine Eklenmemiş Sayfalar Analizi (125 Sayfa)

| Sebep | Sayı | Kaynak | Çözüm Önerisi |
|-------|------|--------|---------------|
| **Yönlendirmeli Sayfa** | 45 | Web sitesi | 🔴 Kritik |
| **Kullanıcı Tarafından Seçilen Standart Sayfa Olmadan Kopya** | 33 | Web sitesi | 🔴 Kritik |
| **Bulunamadı (404)** | 26 | Web sitesi | 🔴 Kritik |
| **Doğru Standart Etikete Sahip Alternatif Sayfa** | 7 | Web sitesi | ⚠️ Orta |
| **Sunucu Hatası (5xx)** | 2 | Web sitesi | 🔴 Kritik |
| **Tarandı - Şu Anda Dizine Eklenmiş Değil** | 9 | Google Sistemleri | ⚠️ Orta |
| **Kopya, Google Kullanıcıdan Farklı Standart Sayfa Seçti** | 3 | Google Sistemleri | ⚠️ Orta |

#### 🔴 KRITIK SORUNLAR

##### 1. **Yönlendirmeli Sayfalar (45 adet) - %36**
**Sorun:** Sitenizde 45 sayfanın başka bir URL'ye yönlendirildiği (redirect) tespit edilmiştir. Google bu yönlendirmeli sayfaları dizine eklemez.

**Olası Nedenler:**
- Eski URL yapısından yeni URL yapısına geçiş (URL değişikliği)
- Kopyacı sayfalar veya yanlış konfigürasyon
- Sitewide HTTP→HTTPS yönlendirmesi sorunları

**Çözüm:**
```bash
# 1. Hangi sayfaların yönlendirildiğini bulun
#    Search Console'da "Yönlendirmeli Sayfa" satırına tıklayın

# 2. Eğer URL yapısı değişmişse 301 yönlendirmelerini doğru şekilde yapılandırın
#    Nginx konfigürasyonu kontrol edin:
cat docker/nginx/nginx.conf | grep -A5 "redirect\|rewrite"

# 3. Tüm HTTP → HTTPS yönlendirmelerini doğrulayın
# 4. Eski sayfaların sitemap.xml'den kaldırıldığını doğrulayın
```

**Yapılması Gerekenler:**
- [ ] Yönlendirmeli sayfaları tanımla
- [ ] Geçerli URL'ler için sitemap.xml'i güncelle
- [ ] Kırık yönlendirmeleri düzelt

##### 2. **Kopya Sayfalar (33 adet) - %26**
**Sorun:** 33 sayfanın "standart sayfa" tanımlanmadığı kopya sayfalar olduğu tespit edilmiştir.

**Olası Nedenler:**
- Parametreli URL'ler (örneğin filter veya session ID içeren)
- HTTP ve HTTPS versiyonları ikisinin de dizine eklenmesi
- www ve www olmayan versiyonların ikisinin de dizine eklenmesi
- Kopyalanan content

**Çözüm:**
```html
<!-- Her sayfada canonical tag kullanın -->
<!-- Dosya: webimar-react/public/index.html veya Next.js layout -->
<link rel="canonical" href="https://tarimimar.com.tr/page-name/" />

<!-- robots.txt'de parametreleri dışlayın -->
# Dosya: webimar-react/public/robots.txt
User-agent: *
Disallow: /*?*  # Parametreli URL'leri engelle
Allow: /*/$
```

**Django API Konfigürasyonu:**
```python
# webimar-api/settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Canonical URL'leri otomatik oluştur
CANONICAL_DOMAIN = "tarimimar.com.tr"
```

##### 3. **404 (Bulunamadı) Sayfaları (26 adet) - %21**
**Sorun:** 26 sayfaya Google erişemiyor (404 HTTP durumu alıyor).

**Olası Nedenler:**
- Dosya server'dan silinmiş ancak sitemap.xml güncellenmemiş
- Dinamik URL'ler doğru şekilde oluşturulmuyor
- API endpoint'ler down

**Çözüm:**
```bash
# 1. Kırık sayfaları tanımla
curl -I https://tarimimar.com.tr/example-page  # 404 döndürüyor mu?

# 2. Django views.py'de custom 404 handler ekle
# webimar-api/tarimsal_yapilar/views.py
from django.http import HttpResponseNotFound

def handle_404(request, exception=None):
    return HttpResponseNotFound({"detail": "Page not found"})

# 3. Sitemap.xml'i düzenle - ölü sayfaları kaldır
# webimar-api/generate_sitemap.py
valid_urls = [url for url in all_urls if check_page_exists(url)]

# 4. Analytics'te hangi sayfaların erişilmediğini kontrol et
```

**Yapılması Gerekenler:**
- [ ] 404 sayfaları tanımla (Search Console sitemap editor kullan)
- [ ] Ölü sayfaları sitemap.xml'den çıkar
- [ ] Kırık link'leri düzelt veya 301 yönlendirmesi yap

##### 4. **Sunucu Hataları (2 adet) - %1**
**Sorun:** 2 sayfa erişim sırasında 5xx sunucu hatası veriyor.

**Çözüm:**
```bash
# 1. Server log'larını kontrol et
docker logs webimar-api --tail 100 | grep -i "error\|500"

# 2. Veritabanı bağlantısını kontrol et
docker exec webimar-postgres-1 psql -U webimar -d webimar_db -c "SELECT 1"

# 3. Django debug mode'u kontrol et
# webimar-api/settings.py - DEBUG = False olmalı (production)
# Ancak kırık views'ları bulmak için DEBUG = True ile test et
```

#### ⚠️ ORTA ÖNCELİK SORUNLAR

##### 5. **Tarandı - Dizine Eklenmiş Değil (9 adet)**
Google tarayıcısı sayfaları bulup taradığı halde dizine eklemeyi seçmemiş (muhtemelen düşük kalite).

**Çözüm:** 
- Content kalitesini artır
- Meta description ve başlıkları iyileştir
- Internal link'leri ekle

---

## 🔍 TARAMA İSTATİSTİKLERİ (Crawl Stats)

### Genel Tarama Metrikleri
| Metrik | Değer | Trend |
|--------|-------|-------|
| **Toplam Tarama İsteği** | **1.785** | 📈 Sabit |
| **Toplam İndirme Boyutu** | 7,22 MB | 📈 Normal |
| **Ortalama Yanıt Süresi** | **629 ms** | ⚠️ Yavaş |

### ⚠️ YANIT SÜRESİ SORUNU (629ms)
**Sorun:** Google bot'un ortalama 629ms yanıt beklemesi, tarama verimini düşürüyor.
- **Ideal:** < 200ms
- **Şu anki:** 629ms (3x üstü!)

**Çözüm:**
```python
# webimar-api/settings.py
# Cache'i aktif et
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Database query'lerini optimize et
from django.db.models import Prefetch
queryset = Model.objects.prefetch_related(Prefetch('related_objects'))

# Slow query log'larını kontrol et
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        }
    }
}
```

### Ana Bilgisayar Tarama İstatistikleri

| Host | Tarama İsteği | Durum | Sorun |
|------|----------------|-------|-------|
| **tarimimar.com.tr** | 1.683 | ⚠️ Geçmişte sorun oldu | Kurtarıldı |
| **www.tarimimar.com.tr** | 102 | ⚠️ Geçmişte sorun oldu | Kurtarıldı |

**Not:** "Geçmişte sorun oldu" durumu düzeltilmiş ancak Google'a tekrar güven kazandırılmalı.

### Yanıta Göre Tarama Dökümü

| HTTP Durumu | Yüzde | Değerlendirme |
|-------------|-------|----------------|
| **200 (Tamam)** | 71% | ✅ İyi |
| **301 (Kalıcı Yönlendirme)** | 25% | ⚠️ Yüksek |
| **404 (Bulunamadı)** | 4% | 🔴 Sorun |
| **304 (Değiştirilmedi)** | <1% | ✅ İyi |
| **5xx (Sunucu Hatası)** | <1% | 🔴 Sorun |

**Analiz:**
- **301 Yönlendirmelerinin %25'i Fazla:** Her yönlendirme fazladan tarama zamanı kullanır
  - Çözüm: Doğrudan /canonical/ URL'lere yönlendir

### Tarama Amacına Göre

| Amaç | Yüzde |
|------|-------|
| **Yenile (Refresh)** | 72% |
| **Bulunma (Discovery)** | 28% |

✅ **Yenile oranı yüksek:** Google sitenizi düzenli olarak yeniledikçe kontrol ediyor (olumlu işaret)

### Dosya Türüne Göre Tarama

| Tür | Yüzde |
|-----|-------|
| **HTML** | 68% |
| **Diğer Dosya Türü** | 25% |
| **Görsel** | 3% |
| **Bilinmiyor (Başarısız)** | 4% |

### Googlebot Türüne Göre Tarama

| Bot | Yüzde | Durum |
|-----|-------|-------|
| **Akıllı Telefon** | 80% | ✅ Mobil-first! |
| **Diğer Aracı Türü** | 7% | İyi |
| **Görsel** | 7% | İyi |
| **Masaüstü** | 5% | ⚠️ Düşük |
| **AdsBot** | 2% | Normal |

**Analiz:** Google mobil-first indexing kullanıyor, masaüstü taraması düşük (normal).

---

## 📋 ÖNERILER - Öncelik Sırasıyla

### 🔴 KRIZZY (Hemen Yapılacak)

#### 1. **INP Performans Sorunu Çöz** (Tahmini: 3-4 gün)
```
Etkilenen: 50 mobil URL
Impact: Arama trafiğinde düşüş
Çözüm Yolu:
- React calculator component'lerini profil'le
- Web Worker'a ağır işlemleri taşı
- Bundle boyutunu ölç
- Test: lighthouse CI pipeline'ında CWV testleri ekle
```

**Lighthouse Test:**
```bash
cd webimar-react
npm run lighthouse:ci
# INP < 200ms olana kadar optimize et
```

#### 2. **45 Yönlendirmeli Sayfa Düzelt** (Tahmini: 1-2 gün)
```
Action: Search Console'da "Yönlendirmeli Sayfa" listsine bak
- Sitemap.xml'deki dead URL'leri kaldır
- Yönlendirmeleri doğrudan canonical URL'ye yap
- nginx.conf'da yönlendirmeler düzelt
```

#### 3. **26 × 404 Sayfa Düzelt** (Tahmini: 1 gün)
```
- Dead URL'leri tespit et ve 301 ile yönlendir
- Sitemap.xml'deki ölü sayfaları kaldır
- API endpoint'lerin çalıştığını doğrula
```

### 🟠 ÖNEMLİ (Bu Hafta Yapılacak)

#### 4. **33 Kopya Sayfa Canonical Tag'i Ekle** (Tahmini: 1 gün)
```html
<!-- Her sayfaya canonical tag ekle -->
<link rel="canonical" href="https://tarimimar.com.tr/dogrusal-url/" />
```

#### 5. **Veritabanı ve Cache Optimizasyonu** (Tahmini: 2-3 gün)
```
- Redis cache'i prod ortamında etkinleştir
- Django ORM query'lerini optimize et (select_related/prefetch_related)
- Database indexing'i kontrol et
Target: Yanıt süresi 629ms → 200ms'ye indirmek
```

#### 6. **Sitemap.xml Otomasyonu** (Tahmini: 1 gün)
```python
# webimar-api/tasks.py (Celery task)
@periodic_task(run_every=crontab(hour=0, minute=0))
def generate_fresh_sitemap():
    """Daily sitemap regeneration - sadece live sayfaları ekle"""
    valid_pages = Page.objects.filter(status='live', deleted=False)
    generate_sitemap_xml(valid_pages)
```

### 🟡 ORTA (Bu Ay Yapılacak)

#### 7. **2 × 5xx Sunucu Hatası Araştır** (Tahmini: 0.5 gün)
```bash
docker logs webimar-api --tail 500 | grep "500\|error"
# Kırılan API endpoint'i bul ve düzelt
```

#### 8. **Masaüstü Tarama Oranı Yüksel** (Tahmini: 1 gün)
```
- Masaüstü UX'i iyileştir
- Masaüstü sitemap.xml ekle (eğer yoksa)
- Masaüstü site hızını artır
```

#### 9. **Monitoring ve Alerting Kur** (Tahmini: 2 gün)
```bash
# Otomatik CWV monitoring
# Google Search Console API'den veri çek
# Slack'e günlük rapor gönder

# webimar-api/management/commands/check_search_console.py
python manage.py check_search_console --alert-if-issues
```

---

## 📈 İYİ Puanlar

✅ **Masaüstü Deneyimi Perfect** (50/50 URL İyi)  
✅ **İndeksleme Oranı Orta** (201 aktif sayfa)  
✅ **Mobil-First Tarama Aktif** (Google mobil versiyonu önceliklendiriyor)  
✅ **Yenileme Oranı Yüksek** (72% yenileme, site düzenli güncelleniyor)  

---

## 🔗 Kaynaklar ve Actionable Links

### Google Search Console
- [Core Web Vitals Raporu](https://search.google.com/search-console/core-web-vitals?resource_id=sc-domain%3Atarimimar.com.tr)
- [Index Coverage Raporu](https://search.google.com/search-console/index?resource_id=sc-domain%3Atarimimar.com.tr)
- [Crawl Stats](https://search.google.com/search-console/settings/crawl-stats?resource_id=sc-domain%3Atarimimar.com.tr)

### Google Kaynakları
- [INP Optimizasyonu](https://web.dev/inp/)
- [Core Web Vitals Guide](https://web.dev/vitals/)
- [Canonical URL'ler](https://developers.google.com/search/docs/beginner/simple-html-version)

### Webimar Kaynakları
- [copilot-instructions.md](./.github/copilot-instructions.md) - Proje mimarisi
- [React Performance](.github/copilot-instructions.md#🎨-frontend-conventions)
- [Django API Patterns](.github/copilot-instructions.md#🎯-django-api-patterns)

---

## 🛠️ Teknik İmplementasyon Talimatları

### React Calculator INP Optimizasyonu Adımları

**Dosya:** [webimar-react/src/components/CalculationForm.tsx](webimar-react/src/components/CalculationForm.tsx)

```typescript
// BEFORE (Yavaş)
const [inputs, setInputs] = useState({});
const handleChange = (e) => {
  setInputs({...inputs, [e.target.name]: e.target.value});
  // Immediate recalculation = blocking main thread
  const result = expensiveCalculation(inputs);
}

// AFTER (Hızlı - Web Worker kullan)
const [inputs, setInputs] = useState({});
const calculationWorkerRef = useRef(new Worker(...));

const handleChange = useCallback((e) => {
  const newInputs = {...inputs, [e.target.name]: e.target.value};
  setInputs(newInputs);
  // Ağır işlemi thread pool'a taşı
  calculationWorkerRef.current.postMessage(newInputs);
}, [inputs]);

const handleWorkerMessage = useCallback((e) => {
  setResult(e.data);
}, []);
```

### Django Query Optimizasyonu

**Dosya:** [webimar-api/tarimsal_yapilar/views.py](webimar-api/tarimsal_yapilar/views.py)

```python
# BEFORE (Yavaş - N+1 queries)
def get_calculation(request):
    calcs = Calculation.objects.all()
    for calc in calcs:
        land_types = calc.land_type.all()  # Database sorgusu her loop'ta!

# AFTER (Hızlı - Prefetch)
def get_calculation(request):
    calcs = Calculation.objects.prefetch_related('land_type').all()
    # Tek query ile tüm related verileri al
```

---

## 📊 Metrik Takip Tablosu

| Metrik | Şimdi | Target | Açıklama |
|--------|-------|--------|----------|
| INP (Mobil) | 203ms | <200ms | ❌ Kritik |
| Dizine Eklenmemiş (%) | 38% | <5% | ❌ Kritik |
| Yanıt Süresi | 629ms | <200ms | ❌ Kritik |
| İndekslenen Sayfalar | 201 | 300+ | ⚠️ Orta |
| Masaüstü CWV | 100% ✅ | 100% | ✅ İyi |
| 5xx Hatalar | 2 | 0 | ❌ Kritik |
| 404'ler | 26 | 0 | ❌ Kritik |

---

## 📝 Takip Listesi

- [ ] **Week 1:** INP optimizasyonunu başlat (React profiling)
- [ ] **Week 1:** 45 yönlendirmeli sayfayı analiz et
- [ ] **Week 1:** 26 × 404 URL'i düzelt
- [ ] **Week 2:** Canonical tag'leri ekle (33 sayfaya)
- [ ] **Week 2:** Redis cache'i production'a deploy et
- [ ] **Week 2:** Veritabanı indeksini optimize et
- [ ] **Week 3:** Lighthouse CI pipeline'ı setup et
- [ ] **Week 3:** Search Console API monitoring'ini kur
- [ ] **Week 4:** Sitemap otomasyonunu implemente et
- [ ] **Ongoing:** Weekly Search Console raporlarını kontrol et

---

**Rapor Hazırlanma Tarihi:** 4 Ocak 2026 (Playwright MCP ile)  
**Sorumlu:** Copilot Assistant  
**Sonraki Kontrol:** 11 Ocak 2026
