# Webimar URL Yapılandırma Düzeltme Raporu
**Tarih:** 8 Aralık 2025

## 🎯 Sorun Tanımı

Next.js ana sayfasından (http://localhost:3000/) tarımsal hesaplama butonlarına basıldığında yanlış URL'lere yönlendirme yapılıyordu:
- **Yanlış:** `http://localhost:3001/hesaplama/mantar-tesisi`
- **Doğru:** `http://localhost:3001/mantar-tesisi`

React SPA tarafında routing yapısı `/hesaplama/` öneki olmadan (`/{structure-type}`) şeklindeyken, Next.js tarafında bu önek eklenerek yönlendirme yapılıyordu.

## ✅ Yapılan Düzeltmeler

### 1. Next.js Ana Sayfa URL Fonksiyonu Düzeltmesi
**Dosya:** `/webimar-nextjs/pages/index.tsx`

```typescript
// ÖNCE (Yanlış)
const getCalculationUrl = (structureType: string): string => {
  if (typeof window !== 'undefined') {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseUrl = isLocalhost ? 'http://localhost:3001' : window.location.origin;
    return `${baseUrl}/hesaplama/${structureType}`;  // ❌ Yanlış /hesaplama/ öneki
  }
  return `http://localhost:3001/hesaplama/${structureType}`;
};

// SONRA (Doğru)
const getCalculationUrl = (structureType: string): string => {
  if (typeof window !== 'undefined') {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseUrl = isLocalhost ? 'http://localhost:3001' : window.location.origin;
    return `${baseUrl}/${structureType}`;  // ✅ Doğru - öneksiz
  }
  return `http://localhost:3001/${structureType}`;
};
```

### 2. JSON Data Dosyaları Toplu Düzeltme
**Konum:** `/webimar-nextjs/data/yapi-turleri/*.json`

23 adet JSON dosyasındaki `ctaLink` değerleri toplu olarak düzeltildi:

```bash
sed -i 's|"/hesaplama/|"/|g' *.json
```

**Düzeltilen Dosyalar:**
- ✅ agil-kucukbas.json
- ✅ aricilik.json
- ✅ bag-evi.json
- ✅ besi-sigirciligi.json
- ✅ hara.json
- ✅ hububat-silo.json
- ✅ ipek-bocekciligi.json
- ✅ kaz-ordek.json
- ✅ kumes-etci.json
- ✅ kumes-gezen.json
- ✅ kumes-hindi.json
- ✅ kumes-yumurtaci.json
- ✅ kurutma-tesisi.json
- ✅ mantar-tesisi.json
- ✅ meyve-sebze-kurutma.json
- ✅ sera.json
- ✅ soguk-hava-deposu.json
- ✅ solucan-tesisi.json
- ✅ su-depolama.json
- ✅ sut-sigirciligi.json
- ✅ tarimsal-depo.json
- ✅ yikama-tesisi.json
- ✅ zeytinyagi-fabrikasi.json

**Örnek Değişiklik:**
```json
// Önce
"ctaLink": "/hesaplama/mantar-tesisi"

// Sonra
"ctaLink": "/mantar-tesisi"
```

## 📊 Google Search Console Analizi

### Dizine Eklenmeyen Sayfalar (27 sayfa)

#### 1. Kullanıcı Tarafından Seçilen Standart Sayfa Olmadan Kopya (21 sayfa)
**Sebep:** Duplicate content - URL varyasyonları

**Tespit Edilen Problemler:**
- ❌ `https://tarimimar.com.tr/hesaplama/kurutma-tesisi/` (trailing slash)
- ❌ `https://tarimimar.com.tr/hesaplama/sera/` (trailing slash)
- ❌ `https://tarimimar.com.tr/hesaplama/agil-kucukbas` (öneksiz)
- ❌ `https://tarimimar.com.tr/hesaplama/sera` (önekli)
- ❌ `https://www.tarimimar.com.tr/gubre-cukuru-hesaplama`
- ❌ `https://www.tarimimar.com.tr/documents/...` (www varyasyonu)
- ❌ `https://tarimimar.com.tr/yikama-tesisi` (öneksiz)
- ❌ `https://tarimimar.com.tr/bag-evi` (öneksiz)
- ❌ `https://tarimimar.com.tr/sut-sigirciligi` (öneksiz)
- ❌ `https://tarimimar.com.tr/mantar-tesisi` (öneksiz)

**Çözüm:** 
- ✅ Next.js routing düzeltmesi yapıldı (öneksiz URL'ler kullanılacak)
- ⚠️ Canonical tag'lerin kontrol edilmesi gerekiyor
- ⚠️ Sitemap.xml'in güncellenmesi gerekiyor

#### 2. Yönlendirmeli Sayfa (3 sayfa)
**Sebep:** Normal yönlendirmeler (sorun yok)
- `http://www.tarimimar.com.tr/` → `https://tarimimar.com.tr/`
- `https://www.tarimimar.com.tr/` → `https://tarimimar.com.tr/`
- `http://tarimimar.com.tr/` → `https://tarimimar.com.tr/`

#### 3. Bulunamadı 404 (1 sayfa)
**URL:** `https://tarimimar.com.tr/documents/ibb-plan-notlari`
**Sebep:** Eski URL - Yeni isim: `izmir-buyuksehir-plan-notlari`
**Çözüm:** 301 redirect eklenmeli veya sitemap'ten kaldırılmalı

#### 4. Tarandı - Şu Anda Dizine Eklenmiş Değil (2 sayfa)
**Sebep:** Google henüz indekslememişti (normal süreç)

### Dizine Eklenen Sayfalar: 50 sayfa ✅

## 🔍 React SPA Routing Yapısı

React App.tsx'te routing tanımları doğru şekilde yapılandırılmış:

```typescript
// webimar-react/src/App.tsx
<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/:structureType" element={<CalculationPage />} />
  // Öneksiz route yapısı ✅
</Routes>
```

**Desteklenen URL'ler:**
- ✅ `/mantar-tesisi`
- ✅ `/sera`
- ✅ `/bag-evi`
- ✅ `/aricilik`
- ✅ `/sut-sigirciligi`
- ve diğer 22 yapı türü...

## 🎨 SEO ve URL Tutarlılığı

### Mevcut Durum
- **Production:** nginx `/hesaplama/*` path'ini React SPA'ya yönlendiriyor
- **Development:** React doğrudan 3001 portunda çalışıyor
- **Next.js:** 3000 portunda SEO sayfaları sunuyor

### Öneriler

1. **Canonical URL Standardizasyonu**
   ```html
   <!-- Tüm sayfalarda canonical tag ekle -->
   <link rel="canonical" href="https://tarimimar.com.tr/mantar-tesisi" />
   ```

2. **Sitemap.xml Güncelleme**
   - `/hesaplama/` önekli URL'leri kaldır
   - Sadece öneksiz URL'leri ekle
   - Trailing slash tutarlılığını sağla

3. **301 Redirects (Nginx)**
   ```nginx
   # Eski URL'lerden yeni URL'lere yönlendirme
   location ~ ^/hesaplama/(.*)$ {
       return 301 /$1;
   }
   
   # 404 olan eski döküman
   location /documents/ibb-plan-notlari {
       return 301 /documents/izmir-buyuksehir-plan-notlari;
   }
   ```

4. **robots.txt Kontrolü**
   - `/hesaplama/` path'inin disallow edilmemesi
   - Sitemap URL'inin doğru olması

## 📝 Test Adımları

### Manuel Test
```bash
# 1. Next.js sayfasını aç
http://localhost:3000/

# 2. Herhangi bir hesaplama butonuna tıkla
# Örnek: Mantar Tesisi

# 3. Beklenen URL:
http://localhost:3001/mantar-tesisi

# 4. Sayfa yüklenmeli ve çalışmalı ✅
```

### Production Test
```bash
# Production'da test
https://tarimimar.com.tr/mantar-tesisi

# Kontrol edilmesi gerekenler:
# ✓ Sayfa 200 OK döndürüyor mu?
# ✓ Canonical tag doğru mu?
# ✓ Meta description var mı?
# ✓ Structured data doğru mu?
```

## 🚀 Deployment Sonrası Kontrol Listesi

- [ ] Production'a deploy et
- [ ] Tüm hesaplama linklerini manuel test et
- [ ] Google Search Console'da yeni sitemap gönder
- [ ] Canonical tag'leri kontrol et
- [ ] 404 sayfası için redirect ekle
- [ ] Nginx config'e redirect kuralları ekle
- [ ] 1-2 hafta sonra GSC'de indeksleme durumunu kontrol et

## 📈 Beklenen Sonuç

### Önce
- 27 sayfa dizine eklenemedi
- 21 sayfa duplicate content sorunu
- Tutarsız URL yapısı

### Sonra (Beklenen)
- 0-3 sayfa dizine eklenemez (sadece redirect'ler)
- Duplicate content sorunu çözülmüş olacak
- Temiz ve tutarlı URL yapısı
- Daha iyi SEO performansı

## 🔗 İlgili Dosyalar

1. `/webimar-nextjs/pages/index.tsx` ✅ Düzeltildi
2. `/webimar-nextjs/data/yapi-turleri/*.json` ✅ Düzeltildi (23 dosya)
3. `/webimar-react/src/App.tsx` ✅ Zaten doğru
4. `nginx.conf` ⚠️ Redirect kuralları eklenmeli
5. `sitemap.xml` ⚠️ Güncellenmeli

## 📸 Ekran Görüntüleri

Ekran görüntüleri şu klasörde:
- `/.playwright-mcp/google-search-console-duplicate-pages.png`
- `/.playwright-mcp/google-search-console-redirects.png`

---

**Hazırlayan:** GitHub Copilot (Claude Sonnet 4.5)  
**Tarih:** 8 Aralık 2025
