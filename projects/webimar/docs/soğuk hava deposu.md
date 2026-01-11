# Soğuk Hava Deposu Hesaplama Sistemi - Yeni Sistem Kuralları

Bu dosya, soğuk hava deposu için *yeni hesaplama sisteminin* kullanıcı akışını ve teknik kurallarını tanımlar.  
Kullanıcı, hesaplama yapmadan önce mutlaka bir emsal türü seçmek zorundadır.  

---

## 1. Kullanıcı Akışı

### 1.1. Emsal Tipi Seçimi Zorunluluğu

- *Kullanıcı, hesapla butonuna basmadan önce aşağıdaki emsal türlerinden birini seçmek zorundadır:*
  - *Marjinal (%20 emsal)*
  - *Mutlak/Dikili/Özel (%5 emsal)*

- Emsal türü seçilmeden hesaplama yapılamaz.

---

## 2. Hesaplama Mantığı

### 2.1. Marjinal (%20) Emsal Seçildiğinde

- *Kullanıcıya sadece arazi büyüklüğü inputu* gösterilir.
- Arazi büyüklüğü girildikten sonra:
  - Başka hiçbir ek kontrol (dikili alan, tarla, zeytinlik, ağaç yoğunluğu vs.) uygulanmaz.
  - Hesaplama formülü:  
    Maksimum yapı alanı = Arazi büyüklüğü × 0.20
  - Sonuç: "Bu araziye en fazla *X m²* soğuk hava deposu yapılabilir."  
  - Alan dağılımı (depo/idari/teknik) opsiyoneldir, istenirse gösterilir.

### 2.2. Mutlak/Dikili/Özel (%5) Emsal Seçildiğinde

- *Kullanıcıdan arazi tipi seçmesi istenir.*
- Seçilen arazi tipine göre bağ evi ve tarımsal amaçlı depo sistemindeki gibi kontroller açılır:
  - Minimum alan kontrolleri (ör: dikili için ≥5000 m², tarla için ≥20.000 m², örtüaltı için ≥3.000 m²)
  - Zeytinlik/ağaç yoğunluğu kontrolleri (dekara 10 ağaç üstü ise izin verilmez)
  - Alan tiplerine göre (dikili, tarla, zeytinlik vs.) inputlar açılır.
- Kurallar tam olarak bağ evi ve tarımsal depo modülü mantığıyla aynıdır.
- Sonuç:  
  - Tüm kontroller sağlanırsa izin verilir ve maksimum yapı alanı gösterilir (sabit veya context’e göre).
  - Kontroller sağlanmazsa izin verilmez ve sebebi açıklanır.

---

## 3. Alan Dağılımı ve Kısıtlar

- Marjinalde hiçbir ek kural veya kısıtlama yoktur.
- Mutlak/dikili/özelde minimum arazi büyüklüğü ve zeytinlik/ağaç kontrolleri aynen uygulanır.
- Depo/idari/teknik alan dağılımı isteğe bağlıdır, zorunlu değildir.
- Her aileye bir depo sınırı veya ek kapasite hesabı yoktur.

---

## 4. Sonuç ve Raporlama

- Sonuçta kullanıcıya:
  - Seçilen emsal türüne göre izin durumu ve maksimum yapı alanı (m²)
  - Marjinal ise: "Bu araziye en fazla *X m²* soğuk hava deposu yapılabilir."
  - Mutlak/dikili/özel ise: Arazi tipine ve kontrollerin sonucuna göre izin durumu ve maksimum yapı alanı.
  - Alan dağılımı (depo/idari/teknik) opsiyonel olarak gösterilebilir.
  - Ek kontroller sonucu açıklama (minimum alan, zeytinlik/ağaç yoğunluğu gibi) eklenir.

---

## 5. Teknik Gereksinimler

- *Frontend:*
  - Emsal türü seçimi componenti zorunlu olmalı.
  - Emsal türüne göre dinamik olarak form alanları açılmalı/kapanmalı.
  - Marjinalde sade form, mutlak/dikili/özelde detaylı alan ve ağaç kontrolleri aktif olmalı.

- *Backend:*
  - Marjinalde: Arazi büyüklüğü × 0.20 ile maksimum yapı alanı döner.
  - Mutlak/dikili/özelde: Bağ evi/tarımsal depo sistemindeki alan ve ağaç kontrolleriyle izin durumu ve alan döner.
  - Sonuçta izin durumu ve maksimum yapı alanı (m²) ile detaylı rapor döner.

---

## 6. Örnekler

- *Marjinal (%20):*
  - Arazi: 12.000 m² → Maksimum yapı alanı: 12.000 × 0.20 = *2.400 m²*

- *Dikili (%5):*
  - Dikili alan: 10.000 m² → Minimum 5.000 m² yeterli → Maksimum yapı alanı: 10.000 × 0.05 = *500 m²*

- *Tarla + Zeytinlik (%5):*
  - Tarla: 21.000 m², Zeytinlik: 2.000 m², Toplam: 23.000 m² → Tüm kontroller sağlanırsa izin verilir ve maksimum alan gösterilir.

---

## 7. Özet Akış

1. Kullanıcı emsal türünü seçer.
2. Marjinal seçerse sadece arazi büyüklüğü girer → hesaplama yapılır → sonuç gösterilir.
3. Mutlak/dikili/özel seçerse arazi tipi seçer → ek inputlar açılır → kontroller sonrası sonuç gösterilir.

---

*Not:*  
Bu sistemde soğuk hava deposu için hesaplama akışı, marjinalde sade ve serbest, mutlak/dikili/özelde ise bağ evi/tarımsal depo sistemine tam uyumlu şekilde alan ve ağaç kontrolleri ile ilerler