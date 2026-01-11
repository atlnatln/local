# İzmir Büyükşehir Belediyesi 5000m² Altı Uyarı Sistemi

## 📋 Proje Özeti
İzmir Büyükşehir Belediyesi plan notları (7.12.15.2) gereğince, tarımsal amaçlı yapılar için minimum 5000 m² parsel büyüklüğü kriteri bulunmaktadır. Bu kriter altındaki parsellerde kullanıcıları uyarmak için sistematik bir kontrol mekanizması geliştirilecek.

## 📑 İlgili Mevzuat
**İzmir Büyükşehir Plan Notları - Madde 7.12.15.2**
- **Mutlak Tarım Arazisi, Dikili Tarım Arazisi, Özel Ürün Arazileri**: Min 5000 m²
- **Marjinal Tarım Arazileri**: Min 5000 m²
- Belediye onayı gereksinimi

## 🎯 Hedef Hesaplama Türleri

### ✅ Uyarı Gösterilecek Hesaplamalar (5000m² altında)
- [ ] Hububat Silo
- [ ] Tarımsal Amaçlı Depo
- [ ] Lisanslı Depolar
- [ ] Yıkama Tesisi
- [ ] Kurutma Tesisi
- [ ] Meyve/Sebze Kurutma
- [ ] Zeytinyağı Fabrikası
- [ ] Soğuk Hava Deposu
- [ ] Solucan Tesisi
- [ ] Mantar Tesisi
- [ ] Arıcılık
- [ ] Süt Sığırcılığı
- [ ] Ağıl (Küçükbaş)
- [ ] Kümes (Yumurtacı)
- [ ] Kümes (Etçi)
- [ ] Kümes (Gezen)
- [ ] Kümes (Hindi)
- [ ] Kaz-Ördek
- [ ] Hara (At)
- [ ] İpek Böcekçiliği
- [ ] Evcil Hayvan
- [ ] Besi Sığırcılığı
- [ ] Su Depolama

### ❌ Uyarı Gösterilmeyecek Hesaplamalar (İstisna)
- ✅ Bağ Evi (Çiftçinin barınması - farklı kural)
- ✅ Sera (Plan notlarında ayrı düzenleme)
- ✅ Su Kuyuları (Altyapı tesisi)

## 🏗️ Teknik Implementasyon

### 1. Backend Kontrol (Gelecekte)
```python
# /calculations/utils/izmir_belediyesi_kontrol.py
def check_izmir_5000m2_rule(alan_m2, yapi_turu, lokasyon_info):
    """
    İzmir sınırlarında 5000m² altı için uyarı kontrolü
    """
    # İzmir sınırları kontrolü
    # 5000m² altı kontrolü  
    # Yapı türü istisnalar kontrolü
    # Uyarı mesajı oluşturma
    pass
```

### 2. Frontend Kontrol (Mevcut - Hızlı Çözüm)
```typescript
// /utils/izmirBelediyesiKontrol.ts
interface IzmirUyariSonuc {
  uyariGosterilsinMi: boolean;
  uyariMesaji: string;
  planNotuDetayi: string;
}

export function checkIzmirBelediyesi5000M2(
  alan_m2: number, 
  hesaplamaTuru: string,
  koordinatlar?: {lat: number, lng: number}
): IzmirUyariSonuc
```

### 3. UI Komponenti
```tsx
// /components/IzmirBelediyesiUyari.tsx
interface Props {
  alan_m2: number;
  hesaplamaTuru: string;
  koordinatlar?: Koordinat;
}

export function IzmirBelediyesiUyari({ alan_m2, hesaplamaTuru }: Props) {
  // Uyarı kartı render et
}
```

## 📍 Entegrasyon Noktaları

### React Frontend
1. **Hesaplama Formu**: Alan girişi sırasında anlık kontrol
2. **Sonuç Ekranı**: Hesaplama sonucu ile birlikte uyarı
3. **Modal Dialog**: Detaylı bilgilendirme

### Next.js
1. **Hesaplama Sayfaları**: SSR ile ön kontrol
2. **Seo Optimization**: Plan notu ile ilgili anahtar kelimeler

## ⚠️ Uyarı Mesajı Tasarımı

### Başlık
"İzmir Büyükşehir Belediyesi Plan Notu Uyarısı"

### İçerik
```markdown
🏛️ **Belediye Onayı Gerekebilir**

İzmir Büyükşehir Belediyesi plan notları (Madde 7.12.15.2) gereğince:
- Tarımsal amaçlı yapılar için minimum 5000 m² parsel büyüklüğü gerekmektedir
- Mevcut parsel: {alan_m2} m² 
- Eksik alan: {5000 - alan_m2} m²

⚠️ **Önemli**: Bu durum için mutlaka belediye İmar ve Şehircilik Müdürlüğü ile görüşmeniz önerilir.

📋 5403 sayılı Toprak Koruma Kanunu izni olsa bile, belediye plan notları gereğince ek onay gerekebilir.
```

### Aksiyon Butonları
- [📞 İzmir Belediyesi İletişim]
- [📋 Plan Notunu İncele]
- [❌ Uyarıyı Kapat]

## 📅 Implementasyon Adımları

### Faz 1: Temel Altyapı (Hafta 1)
- [ ] Utility fonksiyonu oluştur
- [ ] Uyarı komponenti tasarla
- [ ] Test senaryoları yaz

### Faz 2: Frontend Entegrasyon (Hafta 2)
- [ ] React formlarına entegre et
- [ ] Next.js sayfalarına entegre et
- [ ] UI/UX test ve optimizasyon

### Faz 3: Backend Entegrasyon (Gelecek)
- [ ] Django API endpoint'i
- [ ] Koordinat bazlı konum tespiti
- [ ] Cache mekanizması

## 🧪 Test Senaryoları

### Test Case 1: Normal Durumlar
- Alan = 3000 m², Hesaplama = "hububat-silo" → Uyarı GÖSTER
- Alan = 6000 m², Hesaplama = "hububat-silo" → Uyarı GÖSTERMEbag
- Alan = 2000 m², Hesaplama = "bag-evi" → Uyarı GÖSTERME (İstisna)

### Test Case 2: Edge Cases  
- Alan = 5000 m² (tam sınır)
- Alan = 4999 m² (1 m² altı)
- Koordinat İzmir dışı

## 📊 Ölçüm Metrikleri
- Uyarı gösterilme oranı
- Kullanıcı tıklama oranları
- Belediye iletişim sayfa ziyaretleri

## 🔄 Gelecek Geliştirmeler
1. **Otomatik Konum Tespiti**: GPS ile İzmir sınırları kontrolü
2. **Diğer Belediyeler**: Ankara, İstanbul vb. plan notları
3. **AI Destekli Analiz**: Parsel analizi ve öneriler
4. **Hukuki Danışmanlık**: Avukat bağlantısı

---
**Son Güncelleme**: 6 Eylül 2025  
**Durum**: Planlama Aşaması  
**Sorumlu**: Development Team
