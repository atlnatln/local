# Tarımsal Amaçlı Depo - Bağ Evi Mantığıyla Dinamik Emsal ve Minimum Arazi Sistemi Kuralları

Bu doküman, *Tarımsal Amaçlı Depo* için Bağ Evi modülüne benzer şekilde, dinamik emsal ve arazi tipine göre minimum arazi büyüklüğü sisteminin uygulanacağı yeni kuralları ve gereksinimleri açıklar.

---

## 1. Minimum Arazi Büyüklüğü Kuralları

Depo yapılabilmesi için arazi tipine göre aşağıdaki minimum büyüklüklerin sağlanması gereklidir:

| Arazi Tipi                              | Minimum Alan (m²) |
|------------------------------------------|-------------------|
| Dikili, Mutlak ve Özel Ürün Arazisi     | 5.000             |
| Marjinal Tarım Arazisi (Tarla)          | 20.000            |
| Örtüaltı/Sera                           | 3.000             |

---

## 2. Maksimum Yapı Alanı (Dinamik Emsal Sistemi)

Depo yapılabilecek *maksimum yapı alanı*, arazi tipine göre emsal oranı ile arazi büyüklüğünün çarpımı ile hesaplanır.

| Arazi Tipi                              | Emsal Oranı (%)   | Emsal Oranı (Ondalık) |
|------------------------------------------|-------------------|-----------------------|
| Dikili, Mutlak ve Özel Ürün Arazisi     | %5                | 0.05                  |
| Marjinal Tarım Arazisi (Tarla)          | %20               | 0.20                  |
                

*Formül:*  
Maksimum Yapı Alanı (m²) = Arazi Büyüklüğü (m²) × Emsal Oranı

> *Not:* Depo için sabit alanlar (Depo, İdari, Teknik) kaldırılmıştır; tümü maksimum yapı alanı içinde değerlendirilir.

---

## 3. Arazi Tipi ve Alan Kontrolleri

- Arazi tipi ve büyüklüğü, Bağ Evi modülündeki gibi frontend ve backend'de seçilir ve kontrol edilir.
- Minimum arazi büyüklüğü sağlanmadan depo yapılamaz.
- *Zeytinlik ve ağaç yoğunluğu kontrolleri* ile ilgili kurallar Bağ Evi modülündeki ile aynıdır:
  - Zeytinliklerde dekara 10 adet ve üstü ağaç varsa depo yapılamaz.

---

## 4. Birden Fazla Depo Hakkı

- *Her aileye bir depo sınırı* veya ilçede bir depo kuralı YOKTUR.
- Her arazide, gerekli alan ve emsal sağlandığı sürece depo yapılabilir.

---

## 5. Depolama Kapasitesi Hesabı

- *Depolama kapasitesi hesabı yapılmayacak.*
- Sadece yapı alanı (m²) dönecek.

---

## 6. Diğer Kurallar ve Özellikler

- Arazi ve yapı alanı kontrolleri Bağ Evi modülündeki mantıkla (konfigürasyon tabanlı) yapılır.
- Zeytinlik ve dekara yoğunluk kontrolleri, Bağ Evi kuralları ile birebir aynı şekilde uygulanır.
- Manuel veya harita ile alan kontrolü (direct transfer) desteği vardır.
- Sonuçta; izin durumu, maksimum yapılaşma alanı, varsa alan/ağaç kontrollerinin sonucu, HTML rapor döndürülür.

---

## 7. Örnek Hesaplama

- *Dikili Arazi, 10.000 m²:*  
  Maksimum depo alanı = 10.000 × 0.05 = *500 m²*

- *Tarla (Marjinal), 30.000 m²:*  
  Maksimum depo alanı = 30.000 × 0.20 = *6.000 m²*


---

## 8. Sonuç Olarak

- Depo modülü Bağ Evi modülünün minimum arazi ve zeytinlik kontrollerini aynen alacak.
- Maksimum yapı alanı, sabit değerler yerine *emsal ile dinamik olarak* hesaplanacak.
- Her aileye veya ilçeye özel bir sınır olmayacak.
- Depolama kapasitesi veya sabit depo/idari/teknik alan yok.
- Diğer tüm arazi/ağaç tiplerine ilişkin kontroller Bağ Evi kuralları ile aynıdır.
- Sonuçlar: izin durumu, maksimum yapı alanı, alan/ağaç kontrolü, HTML rapor.

---

## 9. Uygulama Gereksinimleri

- Backend fonksiyonu:  
  - Minimum arazi ve emsal oranı kuralları, Bağ Evi modülündeki gibi konfigürasyonlu yapılmalı.
  - Alan/ağaç kontrolleri için Bağ Evi modülündeki fonksiyonlar yeniden kullanılmalı veya uyarlanmalı.
  - Sonuçta: izin durumu, maksimum depo alanı, kontrollerin detayları ve HTML rapor döndürülmeli.

- Frontend:  
  - Bağ Evi formunun arazi tipi ve manuel/dinamik alan kontrolleri aynen kullanılabilir.
  - Depo modülü için sadece depo alanı (m²) ve izin durumu dönecek şekilde yapılandırılmalı.

---

*Not:* Bu dokümandaki kurallar, Bağ Evi modülünde uygulanan minimum arazi büyüklüğü ve ağaç yoğunluğu kontrollerinin aynen Tarımsal Amaçlı Depo modülüne uygulanmasını, maksimum yapı alanının ise araziye göre emsal ile dinamik olarak belirlenmesini öngörür.