---
title: "MEB 2024 Müfredatı ile Teknik Sistem Uyum Analizi ve Çözüm Çerçevesi"
created: "2026-05-08"
updated: "2026-05-08"
type: concept
tags: [mathlock-play, meb, curriculum, concept]
related:
  - mathlock-play
  - mathlock-play-ai
  - mathlock-play-android
  - mathlock-play-backend
  - adr-007-mathlock-meb-curriculum-compliance-implantation
---

# MEB 2024 Müfredatı ile Teknik Sistem Uyum Analizi ve Çözüm Çerçevesi

> Eğitim teknolojilerinde müfredat uyumunun analitik yaklaşımla değerlendirilmesi ve sistematik iyileştirme önerileri

| Kritik Uyumsuzluk | Çözüm Önerisi |
|---|---|
| 1. sınıf müfredatında çarpma işlemi örtük olarak yasaklanmışken, `generate_age_questions.py` %20 olasılıkla çarpma sorusu üretmektedir. | Yaş-işlem eşleştirme tablosu ve dinamik zorluk algoritması ile müfredatla tam uyum sağlanabilir. |

**Özet Değerlendirme:** MEB 2024 matematik öğretim programı ile mevcut teknik sistem arasında beş temel uyumsuzluk alanı tespit edilmiştir: müfredat kazanımları ile zorluk skalası çelişkileri, matematiksel temsil çeşitliliği ile Android render kapasitesi arasındaki farklar, veri modeli ontolojisindeki standartizasyon eksiklikleri, pedagojik farklılaştırma prensipleri ile statik zorluk algoritmalarının uyumsuzluğu, ve beceri temelli değerlendirme yaklaşımı ile raporlama yapısının tutarsızlığı.

---

## 1. Müfredat Kazanım Haritası ↔ Zorluk Skalası Çelişkisi

### 1.1 1. Sınıf "Çarpma YASAK" Kuralının Analizi

#### 1.1.1 Örtük Kapsam Dışı Bırakma Mekanizması

MEB 2024 matematik öğretim programında çarpma işlemi açık bir "yasaklama" ifadesiyle değil, öğrenme çıktılarının kapsam dışında tutulması yoluyla örtük bir dışlama mekanizmasıyla engellenmektedir. Bu durum, "somuttan soyuta geçiş" ve "basitten karmaşığa doğru ilerleme" prensiplerinin doğal bir sonucudur.

1. sınıf programı "Sayılar ve İşlemler", "Geometri", "Ölçme" ve "Veri İşleme" olmak üzere dört ana öğrenme alanından oluşmakta olup, bu alanların hiçbirinde çarpma işlemine yer verilmemektedir. "Sayılar ve İşlemler" alanındaki üç alt öğrenme alanı — "Doğal Sayılar", "Doğal Sayılarla Toplama İşlemi" ve "Doğal Sayılarla Çıkarma İşlemi" — tamamen toplama ve çıkarma odaklı yapılandırılmıştır.

Özellikle dikkat çekici olan, "İşlemlerden Cebirsel Düşünmeye" temasının adında "işlemler" geçmesine rağmen yalnızca toplama ve çıkarma işlemleriyle sınırlı kalmasıdır. Ayrıca, sayı aralıklarının bilinçli sınırlandırılması (20'ye kadar) çarpma işleminin doğası gereği daha büyük sayılar üretme potansiyelini kontrol altında tutmaktadır.

| Kazanım Kodu | Kazanım Açıklaması | İşlem Türü | Çarpma İçerir mi? |
|---|---|---|---|
| MAT.1.2.1 | Toplama işleminin anlamını kavrar (20'ye kadar) | Toplama | Hayır |
| MAT.1.2.2 | Çıkarma işleminin anlamını kavrar (20'ye kadar) | Çıkarma | Hayır |
| MAT.1.2.3 | Toplama-çıkarma ilişkisini kurar | Toplama, Çıkarma | Hayır |
| MAT.1.2.4 | Toplama-çıkarma problemlerini çözer | Toplama, Çıkarma | Hayır |

**Tablo 1:** 1. Sınıf "İşlemlerden Cebirsel Düşünmeye" Teması Öğrenme Çıktıları

MAT.1.2.1 kazanımı, öğrencinin toplama işlemini "bir araya getirme" ve "artırma" eylemleri olarak anlamlandırmasını hedeflemektedir. Kazanımın açıklayıcı notlarında, toplama işleminin somut nesnelerle modellenmesi, bir araya getirme yoluyla toplama ve büyük sayıdan başlama stratejisi gibi alt kavramlar vurgulanmaktadır. Bu kazanımın dilsel yapısı açıkça "toplama" ile sınırlıdır ve çarpma işlemine en ufak bir atıf bile bulunmamaktadır.

MAT.1.2.4 kazanımı, öğrencinin toplama ve çıkarma işlemlerini gerektiren problemleri çözebilmesini hedeflemektedir. Kazanımın örnek problem senaryoları — "8 bilyem vardı, 4 tane de kardeşim verdi, kaç bilyem oldu?" (toplama) veya "12 bilyem vardı, 5 tanesini kaybettim, kaç bilyem kaldı?" (çıkarma) — tamamen bu iki işlemle sınırlıdır. "3 kutu var, her kutuda 4 elma, toplam kaç elma?" gibi çarpma gerektiren bir senaryo, bu kazanımın kapsamı dışında kalmaktadır.

#### 1.1.2 2. Sınıfa Ötelenen Çarpma Girişi

MEB müfredatında çarpma işleminin 2. sınıftan itibaren başlatılacağına dair açık bir planlama söz konusudur. 2014 tarihli MEB matematik dersi öğretim programında "Çarpma ve bölme işlemleri, 2. sınıftan itibaren başlamaktadır" ifadesi, bu yapısal ayrımın bilinçli bir tercih olduğunu doğrulamaktadır. Bu kademelendirme, "spiral müfredat" yaklaşımının bir yansımasıdır.

2. sınıf "Doğal Sayılarla Çarpma İşlemi" alt öğrenme alanı kapsamında üç kazanımla yapılandırılmıştır: çarpma işleminin tekrarlı toplama anlamını açıklama (M.2.1.4.1), doğal sayılarla çarpma işlemi yapma (M.2.1.4.2) ve çarpma işlemi gerektiren problemleri çözme (M.2.1.4.3). Bu kazanımlar, 1. sınıfta edinilen toplama becerileri üzerine inşa edilmektedir.

### 1.2 `generate_age_questions.py` Çarpma Üretimi ile Çatışma

#### 1.2.1 Çatışan Kazanım: MAT.1.2.1 (Toplama Anlamı)

Betiğin %20 olasılıkla çarpma sorusu üretmesi, MAT.1.2.1 kazanımıyla doğrudan ve ciddi bir çatışma oluşturmaktadır. Çatışmanın temel dinamiği, sembolik temsil düzeyindeki kargaşadır.

1. sınıf öğrencisi, henüz "+" işaretinin anlamını tam olarak içselleştirmemişken, "×" işaretiyle karşılaştığında bu iki sembol arasında ayrım yapmakta zorlanabilir. Özellikle "2+3=5" ve "2×3=6" gibi benzer sayılarda semboller karıştırılabilir.

Çatışmanın bir diğer boyutu, öğretmen-öğrenci-veli arasındaki tutarlılığın bozulmasıdır. Öğretmen sınıf içinde toplama konusunu işlerken, öğrenci dijital ortamda çarpma işlemiyle karşılaşması, öğretim programının bütünlüğüne ilişkin şüpheler yaratmaktadır.

#### 1.2.2 Çatışan Kazanım: MAT.1.2.4 (Problem Çözme)

Çarpma üretimi, MAT.1.2.4 kazanımıyla da çok yönlü bir çatışma içindedir. Çarpma gerektiren bir problem, bu kazanımın kapsamı dışında kalmaktadır.

Bu durumun üç olumsuz sonucu vardır: (1) öğrenci problemi çözemeyerek başarısızlık deneyimi yaşar, (2) öğrenci "3+4=7" gibi yanlış bir toplama yaparak kavramsal karışıklık yaşar, (3) değerlendirmede öğrencinin gerçek performansı yanlış yorumlanır.

Bu çatışma, değerlendirme geçerliliği açısından ciddi bir tehdit oluşturur. Bir öğrencinin çarpma sorusunu yanıtlayamaması, MAT.1.2.4 kazanımına ulaşamadığı şeklinde yanlış bir negatif olarak kaydedilebilir.

#### 1.2.3 Teknik Çözüm: Yaş-İşlem Eşleştirme Tablosu

Çatışmanın çözümü için, yaş ve sınıf düzeyine göre işlem türlerini filtreleyen bir yapılandırma mekanizması uygulanmalıdır. Bu mekanizma, müfredat kazanımlarıyla tam uyumlu bir "yaş-işlem matrisi" üzerinden çalışmalıdır.

| Sınıf Düzeyi | Yaş Aralığı | İzin Verilen İşlemler | Yasak İşlemler | Müfredat Kaynağı |
|---|---|---|---|---|
| Okul Öncesi | 5–6 | Sayma, nesne eşleme, basit örüntü | Tüm aritmetik işlemler | MEB Okul Öncesi Programı |
| 1. Sınıf | 6–7 | Toplama (20'ye kadar), Çıkarma (20'ye kadar) | Çarpma, Bölme, Kesir | MAT.1.2.1–MAT.1.2.4 |
| 2. Sınıf | 7–8 | Toplama (100'e kadar), Çıkarma (100'e kadar), Çarpma (giriş) | Bölme (ileri düzey), Kesir işlemleri | M.2.1.4.1–M.2.1.4.3 |
| 3. Sınıf | 8–9 | Çarpma, Bölme (giriş), Üniter kesirler | Non-üniter kesirler, Ondalık sayılar | MEB 2024 3. Sınıf Kazanımları |
| 4. Sınıf | 9–10 | Tüm temel işlemler, Kesirler, Ondalık kesirler | İleri cebir | MEB 2024 4. Sınıf Kazanımları |

**Tablo 2:** Yaş-İşlem Eşleştirme Tablosu ve Müfredat Uyumu

### 1.3 2. Sınıf Zorluk 5 Toplama (25–90) ile "100'e Kadar Eldeli Toplama" Boşluğu

| Parametre | agents.md Zorluk 5 | MEB Müfredat Kazanımı | Fark |
|---|---|---|---|
| Alt Limit | 25 | 10 (eldesiz) / 20 (eldeli) | Uyumlu veya kısmen uyumlu |
| Üst Limit | 90 | 100 | 10 birim boşluk |
| İşlem Türü | Toplama | Eldeli/Eldesiz Toplama | Uyumlu |
| Sayı Aralığı | 25–90 | 0–100 | Müfredat daha geniş |

**Tablo 3:** Zorluk 5 ile Müfredat Kazanımı Karşılaştırması

Bu boşluğun varlığı, teknik sistemin müfredat hedeflerinin %90'ını karşıladığı, ancak tam uyum için son %10'luk dilimin kapatılması gerektiği anlamına gelmektedir. 90–100 aralığındaki toplama işlemleri — örneğin 85+15=100, 78+22=100, 95+8=103 gibi işlemler — öğrencinin onluk-birlik geçişini tam olarak kavradığını gösteren kritik beceri göstergeleridir.

#### 1.3.1 Boşluk Kapatma Stratejileri

| Strateji | Açıklama | Avantajlar | Dezavantajlar | Karmaşıklık |
|---|---|---|---|---|
| A: Doğrudan Genişletme | Zorluk 5 aralığını 25–100 yapma | Tam müfredat uyumu, basit implementasyon | Zorluk heterojenliği artar | Düşük |
| B: Ara Seviye Ekleme | Zorluk 5 (25–75) + Zorluk 5+ (75–100) | Hassas kademelendirme | Skala karmaşıklığı artar | Orta |
| C: Dinamik Aralık | Performansa göre otomatik genişleme | En kişiselleştirilmiş | Karmaşık algoritma | Yüksek |

**Tablo 4:** Boşluk Kapatma Stratejileri Karşılaştırması

Önerilen çözüm: Strateji A ve C'nin birleşimi — zorluk 5 aralığı 25–100 olarak güncellenmeli, aynı zamanda dinamik zorluk ayarı mekanizması devreye alınmalıdır. Bu mekanizmanın implementasyonu, öğrencinin geçmiş performans verilerini analiz eden bir "akıllı aralık üretici" modülü gerektirmektedir.


## 2. Matematiksel Temsil Becerisi ↔ Android Render Uyumu

### 2.1 MEB Alan Becerileri ve Temsil Çeşitliliği

**MAB3: Matematiksel Temsil**

Öğrencinin matematiksel düşünceleri çeşitli temsil biçimleriyle ifade etme ve bu temsiller arasında geçiş yapma becerisi. 1. sınıf ve okul öncesi düzeyinde somut nesneler, resimler, semboller ve sözel ifadeler arasında geçişin temelini oluşturur.

- Somut → Resimsel → Sembolik (CPA yaklaşımı)

**MAB5: Matematiksel Araç ve Teknoloji ile Çalışma**

Dijital araçları matematiksel keşif ve problem çözme süreçlerinde etkin olarak kullanma becerisi. Android bağlamında dokunmatik ekran etkileşimleri, sesli geri bildirimler ve görsel animasyonlar aracılığıyla temsillerin zenginleştirilmesini gerektirir.

- Dokunmatik etkileşimler, sesli geri bildirimler

**Temsil Gereksinimleri:**

- Emoji tabanlı sayma (🍎🍎🍎)
- Örüntü tamamlama (1, 2, 1, 2, ?)
- Sıralama görselleri
- Etkileşimli elemanlar
- Sürükle-bırak etkileşimi

| Temsil Düzeyi | Somut Nesne | Resim/Emoji | Sembol | Yaş Uygunluğu |
|---|---|---|---|---|
| Somut | Fiziksel elma, blok | — | — | Okul Öncesi (5–6) |
| Yarı-Somut | — | 🍎🍎🍎 emoji | — | Okul Öncesi–1. Sınıf (5–7) |
| Resimsel | — | Çizim, fotoğraf | — | 1. Sınıf (6–7) |
| Sembolik | — | — | 3, +, −, = | 1. Sınıf–2. Sınıf (6–8) |

**Tablo 5:** Temsil Düzeyleri ve Yaş Uygunluğu

### 2.2 Mevcut Android Parse Mantığı Sorunları

#### 2.2.1 "= ?" Format Bağımlılığı

MathChallengeActivity'nin mevcut parse mantığı, matematiksel soruları işlemek için tek bir formata bağımlıdır: `= ?` yapısı. Bu format, metin tabanlı, sembolik temsillere özgüdür.

Tek tip cevap input yapısı (sayısal klavye) sorunu derinleştirir. "Kaç tane elma var: 🍎🍎🍎" sorusu için öğrenci elmaları dokunarak sayabilmeli; "1, 2, 1, 2, ?" örüntü sorusu için seçenekler arasından seçim yapmalıdır.

Bu durum, MAB5 becerisinin "teknolojiyi matematiksel araç olarak kullanma" hedefinin gerçekleşmesini engellemektedir. Öğrenci, teknolojiyi pasif bir içerik tüketici olarak kullanmakta, aktif bir keşif aracı olarak deneyimleyememektedir.

#### 2.2.2 agents.md Formatlarının Render Engeli

"Kaç tane elma var: 🍎🍎🍎" — Mevcut `= ?` parse mantığı, emoji karakterlerini işlemek için tasarlanmamıştır. Emoji'lerin Unicode olarak algılanması metin düzeninde bozulmalara yol açabilmekte; boyutlandırma ve hizalama için özel işlemler gerekmektedir.

"1, 2, 1, 2, ?" — Sayı dizisinin yapısal özelliği (tekrarlayan 1-2 örüntüsü) kritik öneme sahiptir. Mevcut parse mantığı bu yapısal bilgiyi ayıklayamamakta, soruyu basit bir metin dizisi olarak işlemektedir.

Bu iki formatın render engeli, pedagojik bir fırsatın kaçırılmasıdır. Sayma ve örüntü becerileri, okul öncesi ve 1. sınıf düzeyinde matematiksel gelişimin temel yapı taşlarıdır.

### 2.3 Kapsamlı Refactoring Planı

#### 2.3.1 Soru Tipi Sınıflandırma Sistemi

MEB müfredatının temsil çeşitliliğini desteklemek için, polimorfik bir mimari tasarlanmalıdır. Temel bir `MathQuestion` soyut sınıfından türeyen özel soru tipleri, kendi render mantığını, etkileşim modunu ve cevap doğrulama mekanizmasını kendisi tanımlamalıdır.

| Soru Tipi | Temsil Modu | Etkileşim Tipi | Örnek | Hedef Yaş |
|---|---|---|---|---|
| TextQuestion | Sembolik metin | Sayısal klavye | "5 + 3 = ?" | 7+ |
| VisualCountQuestion | Emoji/görsel nesne | Dokunmatik sayma/seçim | "🍎🍎🍎 kaç tane?" | 5–7 |
| PatternQuestion | Yapısal dizi | Seçenek seçimi/sürükle-bırak | "1, 2, 1, 2, ?" | 6–8 |
| SortingQuestion | Sıralanabilir nesneler | Sürükle-bırak sıralama | "Küçükten büyüğe sıralayın" | 6–9 |
| MeasurementQuestion | Cetvel, terazi simülasyonu | Sürükle-bırak ölçme | "Kaç cm?" | 7–9 |

**Tablo 6:** Soru Tipi Sınıflandırma Sistemi

#### 2.3.2 Render Katmanı Mimarisi

**EmojiSpannableBuilder**

Unicode emoji karakterlerinin metin içinde düzgün görüntülenmesini, cihaz ekranına göre ölçeklendirmeyi ve tutarlı boşluklar eklemeyi sağlar. EmojiCompat kütüphanesi entegrasyonu ve TouchDelegate ile dokunmatik etkileşim alanları genişletilir.

**PatternView**

Sayı dizisini yatay olarak sıralanmış görsel öğeler olarak render eder. Eksik öğenin yerini boş kutu veya soru işareti ile belirtir. Renk kodlaması (1=mavi, 2=yeşil) ile tekrarlayan yapı görselleştirilir.

**DraggableItemView**

ItemTouchHelper ile entegre sürükle-bırak etkileşimini yönetir. Sürükleme sırasında öğe yarı saydam hale gelir, hedef pozisyon vurgulanır. Doğru sıralamada görsel geri bildirim verilir.

#### 2.3.3 Cevap Input Dönüşüm Mekanizmaları

| Input Bileşeni | Kullanım Alanı | Etkileşim Modu | Özel Özellikler |
|---|---|---|---|
| NumericKeypad | TextQuestion | Sayısal tuş takımı | Büyük tuşlar, sesli geri bildirim, hata önleme |
| PatternContinuationInput | PatternQuestion | Seçenek düğmeleri | 2-4 seçenek, animasyonlu yerleştirme, anında doğrulama |
| DragDropAnswer | SortingQuestion, VisualCountQuestion | Sürükle-bırak | Dokunmatik hassasiyet, hedef vurgulama, düzeltme imkanı |
| VoiceInput | Okul öncesi tüm soru tipleri | Sesli cevap | SpeechRecognizer API, çocuk sesi optimizasyonu, güven eşiği |

**Tablo 7:** Çok Modlu Cevap Input Sistemi

#### 2.3.4 Parse Mantığı Genişletimi

Mevcut regex tabanlı parse mantığının genişletilmesi, hem yeni soru formatlarını destekleyecek hem de mevcut `= ?` formatını koruyacak şekilde tasarlanmalıdır. Çok aşamalı bir parse pipeline'ı:

1. **Format Tespiti:** Emoji içeren → VisualCountQuestion, virgüllü sayı dizisi → PatternQuestion, `=` işareti → TextQuestion
2. **İçerik Ayrıştırma:** Format tipine göre ilgili parser: emoji sayısı/türü, örüntü dizisi/eksik eleman, operandlar/operatör
3. **JSON Serileştirme:** Standart JSON formatına dönüştürme; tüm soru tipleri için ortak yapı + özel alanlar

Geriye uyumluluk: Mevcut `= ?` formatlı sorular otomatik olarak TextQuestion tipine dönüştürülmeli, veritabanı kayıtları için migration script çalıştırılmalıdır. Çift sistem döneminde her iki format da paralel çalışabilmelidir.


## 3. Veri Modeli Ontolojisi: Tip Standardizasyonu ve ID Çakışması

### 3.1 Tip İsimlendirme Çatışması Analizi

| Bileşen | İsimlendirme Konvansiyonu | Örnek: Çarpma | Örnek: Bölme |
|---|---|---|---|
| Backend (Django Model) | CharField/choices, Türkçe karakterli | çarpma | bölme |
| generate_age_questions.py | Python değişkeni, Türkçe karakterli | çarpma | bölme |
| agents.md | Markdown dokümantasyon, Türkçe karaktersiz | carpma | bolme |

**Tablo 8:** Tip İsimlendirme Çatışması Matrisi

#### 3.1.1 Çatışma Noktaları ve Risk Analizi

Çatışmanın en kritik noktası, Backend-Agents eşleşmemesidir. Backend modelinde `Question.type` alanı CharField/choices olarak tanımlanmış ve Türkçe karakterli değerler (`çarpma`, `bölme`) içermektedir. Ancak agents.md, Türkçe karaktersiz versiyonlarını (`carpma`, `bolme`) kullanmaktadır.

**Senaryo 1:** agents.md otomatik işlenirse, çıkarılan tip değerleri backend'e kaydedilemez veya yanlış eşleşmelere yol açar.

**Senaryo 2:** Geliştiriciler agents.md'yi referans alarak kod yazdıklarında, Türkçe karaktersiz isimlendirmeyi kullanma eğilimi gösterir; bu da backend ile tutarsızlık yaratır.

**Pipeline Geçişlerinde Veri Kirliliği Riski**

`generate_age_questions.py`'nin ürettiği sorular, backend'e kaydedilirken tip dönüşümü gerekebilir. Eğer bu dönüşüm tutarlı yapılmazsa, aynı işlem türü farklı kayıtlarda farklı isimlerle yer alabilir.

Bu durum, istatistiksel analizleri, raporlamayı ve filtrelemeyi güçleştirmektedir. Görünüşte küçük bir teknik ayrıntı, sistematik veri kirliliği riski taşımaktadır.

### 3.2 MEB Müfredat Hiyerarşisine Uygun Ontoloji Tasarımı

#### 3.2.1 MAT Kodlama Sistemi Referansı

MEB 2024 müfredatı, kazanımları `MAT.{Sınıf}.{Tema}.{Kazanım}` formatında kodlamaktadır. Bu kodlama sistemi, içerik çerçevesinin yapısal bütünlüğünü yansıtmakta ve her kazanımın benzersiz tanımlanmasını sağlamaktadır.

Bu kodlama sisteminin teknik ontolojiye uyarlanması, müfredatla doğrudan eşleşen bir URI şeması oluşturulmasını mümkün kılmaktadır. Böyle bir şema, tip isimlendirme çatışmasını kökten çözmekte, aynı zamanda müfredatın pedagogik yapısını teknik sisteme taşımaktadır.

#### 3.2.2 URI Şema Önerisi: MAT.{Sınıf}.{Tema}.{Kazanım}.{İşlem}

| URI Örneği | Açıklama | Karşılık Gelen Tip Değeri |
|---|---|---|
| MAT.1.2.1.toplama | 1. sınıf, İşlemler teması, 1. kazanım, toplama | toplama |
| MAT.1.2.2.cikarma | 1. sınıf, İşlemler teması, 2. kazanım, çıkarma | cikarma |
| MAT.2.1.2.carpma | 2. sınıf, Sayılar teması, 2. kazanım, çarpma | carpma |
| MAT.2.1.3.bolme | 2. sınıf, Sayılar teması, 3. kazanım, bölme | bolme |
| MAT.3.2.1.kesir_uniter | 3. sınıf, Kesirler teması, 1. kazanım, üniter kesir | kesir_uniter |

**Tablo 9:** URI Şema Örnekleri ve Tip Eşleştirmesi

#### 3.2.3 Tekilleştirme ve Eşleştirme Katmanı

**Canonical Type Registry**

Tüm tip değerlerinin tek yetkili kaynağı. URI formatındaki tip tanımlarını içerir; sistemdeki tüm bileşenler bu tanımlara başvurur. Veritabanında konfigürasyon tablosu veya kodda enum/sabitler sınıfı olarak implement edilir.

**Legacy Mapping Table**

Mevcut isimlendirme konvansiyonlarının (Türkçe karakterli, karaktersiz, kısaltmalar) URI formatındaki canonical değerlere dönüştürülmesini sağlar. Sistem geçişi ve harici entegrasyonda kritik rol oynar.

**Validation Middleware**

Veri akışının her aşamasında tip değerlerinin canonical forma uygunluğunu kontrol eder. Geçersiz veya tanımlanmamış tip değerlerinin sisteme nüfuz etmesini engeller, hataları erken tespit ederek veri kirliliğini önler.

| Legacy Değer | Kaynak Bileşen | Canonical URI |
|---|---|---|
| çarpma | Backend, generate_age_questions.py | MAT.2.1.2.carpma |
| carpma | agents.md | MAT.2.1.2.carpma |
| carp | Eski kod, kısaltma | MAT.2.1.2.carpma |
| multiplication | İngilizce dokümantasyon | MAT.2.1.2.carpma |

**Tablo 10:** Legacy Mapping Table Örneği

### 3.3 `question_id` Çakışma Riski ve Çözümü

| ID Uzayı | Aralık | Kaynak | Kullanım Amacı |
|---|---|---|---|
| Batch 0 (Legacy) | 1000+ | Manuel oluşturulmuş sorular | Kalıtım içerik, referans sorular |
| Batch 1+ (AI Pipeline) | 1–50 | Yapay zeka ile üretilmiş sorular | Dinamik içerik üretimi, kişiselleştirme |

**Tablo 11:** Mevcut ID Uzayları ve Özellikleri

#### 3.3.1 Çakışma Riski Analizi

ID aralıklarının birbirine yakın veya örtüşebilir olması temel sorundur. Batch 0'ın 1000+ offset'i kısa vadede çakışmayı önlemekle birlikte, uzun vadede skalama sorunları yaratmaktadır.

"Soru #1005'te zorlandı" ifadesi, bu sorunun Batch 0'ın 1005 numaralı sorusu mu yoksa gelecekteki bir batch'in sorusu mu olduğunu belirsiz kılmaktadır. Bu belirsizlik, hata ayıklamayı, istatistiksel analizi ve öğrenci takibini güçleştirmektedir.

#### 3.3.2 MEB "Okul Temelli Planlama" Modelinden Esinlenme

MEB 2024 programındaki "Okul Temelli Planlama" yaklaşımı, dönemsel içerik çerçevesi modeli üzerinden yapılandırılmaktadır: zamana bağlı versiyonlama, hiyerarşik yapı (yıl → dönem → hafta → konu), ve izlenebilirlik.

Bu özellikler, soru ID'lerinin de benzer bir yapıda organize edilmesi gerektiğini düşündürmektedir.

#### 3.3.3 Kalıcı Çözüm: Yapılandırılmış ID Formatı

Format: `{Yıl}G{Sınıf}-B{Batch}-{SıraNo}`

| ID Örneği | Yapısal Analiz |
|---|---|
| 2024G1-B0-1001 | 2024 eğitim yılı, 1. sınıf, Batch 0 (legacy), sıra 1001 |
| 2024G2-B1-0042 | 2024 eğitim yılı, 2. sınıf, Batch 1 (AI), sıra 42 |
| 2025G3-B2-0150 | 2025 eğitim yılı, 3. sınıf, Batch 2 (AI), sıra 150 |

**Tablo 12:** Yapılandırılmış ID Format Örnekleri

Bu formatın temel avantajları:

- **Benzersizlik:** Yıl, sınıf, batch ve sıra numarası kombinasyonuyla her ID benzersizdir
- **İzlenebilirlik:** ID'den sorunun hangi yıl, sınıf ve kaynak için üretildiği anlaşılır
- **Sıralanabilirlik:** Kronolojik ve hiyerarşik sıralama doğal olarak desteklenir
- **Genişletilebilirlik:** Yeni batch'ler ve sınıf düzeyleri mevcut yapıya zarar vermeden eklenebilir

#### 3.3.4 Geçiş ve Uyumluluk Stratejisi

**Çift ID Dönemi**

Yeni sistem devreye alınırken eski ID'ler geçici olarak korunur. Her kayıtta hem eski hem yeni ID yer alır. Süre: 3-6 ay.

**Migration Script**

Mevcut veritabanı kayıtlarının yeni formata otomatik dönüştürülmesi. Eski ID'den yeni ID üretimi, ilişkisel verilerin güncellenmesi ve dönüşüm raporu.

**API Versiyonlama**

Mobil uygulama ve diğer istemciler yeni ID formatını destekleyecek şekilde güncellenir. API'nin belirli versiyonunda her iki format da kabul edilir.


## 4. Pedagojik Farklılaştırma ↔ Adaptif Zorluk Algoritması

### 4.1 MEB Farklılaştırma Çerçevesi

#### 4.1.1 Zenginleştirme Boyutu

"Farklılaştırma" başlığı altındaki "Zenginleştirme" boyutu, üst düzey öğrenciler için müfredatın ötesine geçen, daha derin ve karmaşık problem senaryoları sunmayı hedeflemektedir.

Teknik karşılığı: Öğrencinin mevcut kazanım seviyesinin üst bandında zorluk sunulması. 2. sınıf çarpma kazanımını (M.2.1.4) başarıyla tamamlayan bir öğrenci için, çarpım tablosunun ötesine geçen çok adımlı problemler sunulabilir.

#### 4.1.2 Destekleme Boyutu

"Destekleme" boyutu, temel düzeydeki öğrenciler için müfredatın basitleştirilmesini, ek somut materyal sunulmasını ve adım adım kılavuzluk yapılmasını öngörmektedir.

Teknik karşılığı: Öğrencinin mevcut kazanım seviyesinin alt bandında zorluk sunulması ve ek ipuçları sağlanması. Eldeli toplamada zorlanan bir öğrenci için, önce eldesiz toplama ile güven tazelenmesi, ardından onluk bozma gerektiren basit işlemlerle yavaş yavaş zorluk artırılması sağlanabilir.

#### 4.1.3 Hazır Bulunuşluk ve Ön Değerlendirme

MEB programı, "bireyin hazır bulunuşluk düzeyi" ve "ön değerlendirme süreci" ilkelerini merkeze almaktadır. Hazır bulunuşluk düzeyi, öğrencinin belirli bir konuyu öğrenmeye ne kadar hazır olduğunu ifade eder.

Teknik karşılığı: Öğrencinin ilk oturumunda veya yeni bir konuya geçişinde kısa bir tanı testi. Örneğin, 2. sınıf çarpma konusuna başlamadan önce, öğrencinin 1. sınıf toplama becerileri hızlıca değerlendirilerek başlangıç zorluk seviyesi belirlenir.

### 4.2 Mevcut Zorluk 5 Tanımlarının Statik Yapısı

| Sınıf | Zorluk 5 Tanımı | Statik Parametre | Pedagojik Sorun |
|---|---|---|---|
| 2. Sınıf | Çarpma | 8×9=72 | Tüm öğrencilere aynı; bazıları 2×3'te zorlanır, bazıları 9×9'u bekler |
| 3. Sınıf | Kesir | 3/5'i bulma | Non-üniter kesir, müfredat dışı olabilir; öğrenci 1/2'de takılıyor olabilir |
| 4. Sınıf | Bölme | 2400÷48 | İki basamaklı bölen; bazı öğrenciler 100÷5'te zorlanır |

**Tablo 13:** Statik Zorluk 5 Tanımları ve Pedagojik Sorunları

Bu statik yapının temel sorunu, "ortalama öğrenci" varsayımına dayanmasıdır. Gerçekte, aynı sınıftaki öğrenciler arasında önemli bireysel farklılıklar bulunmaktadır. Bir öğrenci çarpma tablosunu tamamen ezberlemişken, diğeri henüz 2×3'ü anlamlandırmaya çalışıyor olabilir. İkisine de 8×9=72 sorusu sunmak, birini sıkarak zenginleştirme fırsatını kaçırırken, diğerini zorlayarak öğrenme motivasyonunu zedelemektedir.

### 4.3 Sınıf Düzeyi Kazanım Analizi

#### 4.3.1 3. Sınıf Kesir Kazanımları

MEB 2024 müfredatının 3. sınıf kesir kazanımları, üniter kesirlerle (1/2, 1/4, 1/3 vb.) sınırlıdır. Bu kazanımlar, öğrencinin "bütün ve parça" ilişkisini anlamasını, üniter kesirleri modellerle göstermesini ve kesirleri sayı doğrusunda yerleştirmesini hedeflemektedir.

Non-üniter kesirler (3/5, 4/7 gibi), 3. sınıf müfredatının kapsamı dışında kalmaktadır. Üniter kesirlerde (1/5) bütün beş eşit parçaya bölünmekte ve bir parça alınmaktadır; non-üniter kesirlerde (3/5) ise birden fazla parçanın birleştirilmesi gerekmekte, bu da ek bir bilişsel adım içermektedir.

agents.md'deki "3/5'i bulma" zorluk tanımı, müfredatla doğrudan çatışmaktadır.

#### 4.3.2 4. Sınıf Bölme Kazanımları

4. sınıf müfredatında, iki basamaklı bölenle bölme işlemi yer almaktadır. Bu kazanım, öğrencinin 720÷24 gibi işlemleri yapabilmesini hedeflemektedir.

agents.md'deki "2400÷48" zorluk tanımı, bu kazanımla genel olarak uyumlu görünmekle birlikte, bireysel farklılıklar göz ardı edilmektedir. Bazı öğrenciler 720÷24 işlemini rahatlıkla yaparken, diğerleri 100÷5 işleminde zorlanabilmektedir.

Statik bir zorluk tanımı, bu farklılıkları dikkate alamamakta ve MEB farklılaştırma çerçevesinin temel ilkeleriyle doğrudan çatışmaktadır.

### 4.4 Dinamik Zorluk Algoritması Tasarımı

#### 4.4.1 Öğrenci Profili Tabanlı Zorluk Ayarı

Dinamik zorluk algoritmasının temeli, öğrenci profili oluşturulmasıdır. Bu profil, öğrencinin ön değerlendirme sonuçlarına, geçmiş performans verilerine ve öğrenme davranışlarına dayanmaktadır. Her kazanım için öğrencinin mevcut seviyesi (başlangıç, gelişim, ustalık) belirlenir.

**Başlangıç Seviyesi:** Alt banda yakın zorluk, ek ipuçları ve destek modu. Öğrenci güvenini tazeler, temel kavramları sağlamlaştırır.

**Gelişim Seviyesi:** Orta banda odaklanma, gradüel zorluk artışı. Kazanım hedeflerine uygun standart zorlukta ilerleme.

**Ustalık Seviyesi:** Üst banda yakın zorluk, zenginleştirme içerikleri. Müfredat ötesi problem senaryoları.

#### 4.4.2 Kazanım-Hazır Bulunuşluk Eşleştirmesi

| Kazanım | Min Zorluk | Max Zorluk | Başlangıç | Gelişim | Ustalık |
|---|---|---|---|---|---|
| MAT.2.1.4 (Çarpma) | 2×2=4 | 9×9=81 | 2×3, 3×2 | 5×6, 7×4 | 8×9, 9×7 |
| MAT.3.2.1 (Üniter Kesir) | 1/2 | 1/10 | 1/2, 1/4 | 1/3, 1/5 | 1/7, 1/9 |
| MAT.4.1.2 (Bölme) | 10÷2=5 | 720÷24=30 | 24÷6, 35÷5 | 144÷12, 360÷15 | 720÷24, 840÷28 |

**Tablo 14:** Kazanım Bazlı Dinamik Zorluk Bandı

#### 4.4.3 Farklılaştırma Entegrasyonu

Dinamik zorluk algoritması, MEB farklılaştırma çerçevesinin üç modunu desteklemelidir. Mod geçişleri, öğrencinin performansına göre otomatik olarak gerçekleşir. Yüksek doğruluk ve hız → zenginleştirme moduna geçiş; düşük doğruluk ve uzun yanıt süresi → destekleme moduna geçiş. Bu adaptasyon, öğrencinin her zaman "öğrenme bölgesi"nde (Vygotsky'nin yakın gelişim alanı) kalmasını sağlar.

**Zenginleştirme Modu:** Kazanım bandının üst %20'lik diliminden sorular, çok adımlı ve açık uçlu problemler. Öğrenci potansiyelini tam olarak gerçekleştirir.

**Standart Mod:** Kazanım bandının orta %50'lik diliminden sorular. Çoğu öğrenci için varsayılan mod; kazanım hedeflerine uygun zorluk.

**Destekleme Modu:** Kazanım bandının alt %30'luk diliminden sorular, adım adım çözüm kılavuzları. Öğrenci güvenini tazeler, temel kavramları sağlamlaştırır.


## 5. Beceri Temelli Değerlendirme ↔ `report.json` / `stats.json` Yapısı

### 5.1 MEB Öğrenme Kanıtları ve Değerlendirme Yaklaşımı

#### 5.1.1 Beceri Temelli Değerlendirme

MEB 2024 programının "Öğrenme Kanıtları" bölümü, geleneksel notlandırma anlayışından farklı olarak beceri temelli, süreç odaklı bir değerlendirme yaklaşımı öngörmektedir. Öğrencinin sadece doğru yanıt verip vermediği değil, aynı zamanda nasıl düşündüğü, hangi stratejileri kullandığı ve gelişim gösterip göstermediği değerlendirilir.

Teknik sistemdeki karşılığı, raporların sadece doğru/yanlış istatistikleri içermemesi, aynı zamanda süreç verilerini de yansıtmasıdır. Örneğin: "15 doğru, 5 yanlış" yerine "elde kullanımında gelişim gösteriyor, ancak onluk bozmada hâlâ destek gerekiyor".

#### 5.1.2 Dereceli Puanlama Anahtarları

MEB programı, çoklu düzey başarı tanımları içeren dereceli puanlama anahtarlarını öngörmektedir: "başlangıç", "gelişim", "hedef" ve "üst düzey".

#### 5.1.3 Performans Görevleri, Gözlem Formu ve Portfolyo

MEB programı, çoklu kaynaklı değerlendirme yaklaşımı benimsemektedir: performans görevleri (projeler, sunumlar), gözlem formları (öğretmenin sınıf içi gözlemleri) ve ürün dosyası/portfolyo (öğrencinin çalışmalarının koleksiyonu).

Teknik sistemde bu yaklaşım, her oturumun mini-portfolyo kaydı şeklinde implement edilebilir. Öğrencinin çözdüğü sorular, kullandığı stratejiler, harcadığı süre ve aldığı geri bildirimler, zaman içindeki gelişimini gösteren bir portfolyo oluşturur.

### 5.2 Mevcut Rapor Yapısı Sorunları

#### 5.2.1 Kopyala-Yapıştır Şablon Sorunu

Mevcut `report.json` şablonlarının en temel sorunu, tüm yaş gruplarında aynı metinlerin kullanılmasıdır. En çarpıcı örnek: "Bölme işlemlerinde zorlanıyor" ifadesinin okul öncesi raporlarında yer almasıdır.

Okul öncesi müfredatında bölme işlemi bulunmamaktadır; bu nedenle bu ifade tamamen anlamsızdır ve raporun güvenilirliğini zedelemektedir.

Şablonlar "matematik zorlukları" gibi genel kategoriler içermekte, ancak bu kategorilerin yaş grubuna göre somut içeriği tanımlanmamaktadır. Sonuç olarak, 5 yaşında bir çocuğun raporunda "bölme işlemleri" gibi kavramlar yer almakta, bu da velinin ve öğretmenin raporu ciddiye almasını engellemektedir.

#### 5.2.2 `stats.json` `totalShown` Uyumsuzluğu

`stats.json`'daki `totalShown` değerleri, tasarım gereği yaş grubuna göre değişiklik göstermektedir: okul öncesi 30, 1. sınıf 40, diğerleri 50. Ancak Android tarafında bu değer sabit 50 olarak kodlanmış olma riski bulunmaktadır.

**Senaryo 1:** Okul öncesi için 50 soru gösterilmesi — 5-6 yaş çocuğunun dikkat süresi 15-20 dakika ile sınırlıdır. 50 soru, yorulmaya ve olumsuz öğrenme deneyimine neden olur.

**Senaryo 2:** 1. sınıf için 50 soru gösterilmesi — Optimal soru sayısı 40 olarak tasarlanmışken, son 10 soruda performans düşüklüğü yaşanır; bu durum değerlendirme geçerliliğini tehdit eder.

### 5.3 Yaş Grubuna Özgü Rapor Senaryoları

#### 5.3.1 Okul Öncesi (5–6 yaş)

**Odağı:** Sayma ve nesne eşleme odaklı gözlem. Bu yaş grubunda matematiksel gelişim, somut nesnelerle etkileşim ve temel sayma becerileri üzerinden değerlendirilir.

> "Ayşe, 1-10 arası sayıları doğru sıralayabilmekte ve bu sayılarla nesne eşleştirme yapabilmektedir. 10'dan sonraki sayılarda bazen atlamalar yaşamakta, bu nedenle ritmik sayma etkinlikleriyle desteklenmesi önerilmektedir. Örüntü tanıma becerisi gelişmekte olup, basit ABAB örüntülerini devam ettirebilmektedir."

#### 5.3.2 1. Sınıf (6–7 yaş)

**Odağı:** 20'ye kadar toplama-çıkarma becerisi, onluk-birlik ayrımı ve yer değeri anlayışı, problem çözme stratejileri.

> "Mehmet, toplamları 20'ye kadar olan eldesiz toplama işlemlerini güvenle yapabilmektedir. Eldeli toplamada onluk bozma adımında bazen destek gerekmekte, bu nedenle onluk-birlik materyalleriyle pekiştirme önerilmektedir. Çıkarma işleminin toplamanın tersi olduğu ilişkisini fark etmekte, basit problem senaryolarını çözebilmektedir."

#### 5.3.3 2. Sınıf (7–8 yaş)

**Odağı:** 100'e kadar eldeli toplama, çarpma girişi ve çarpım tablosu bilgisi, kesir kavramına ilk adım.

> "Zeynep, 100'e kadar eldeli toplama işlemlerini başarıyla tamamlamaktadır. Çarpma işleminin tekrarlı toplama anlamını kavramış olup, 5'e kadar çarpım tablosunu ezberlemeye başlamıştır. Bütün-yarım ilişkisini modellerle gösterebilmekte, kesir kavramının temellerini atmaktadır."

#### 5.3.4 3. Sınıf (8–9 yaş)

**Odağı:** Çarpma-bölme ilişkisi, üniter kesirlerle işlemler, çok basamaklı sayılarla işlemler.

> "Ali, çarpma ve bölme işlemlerinin birbirinin tersi olduğu ilişkisini kavramıştır. Üniter kesirleri (1/2, 1/4, 1/3) modellerle gösterebilmekte ve bu kesirleri büyüklük olarak karşılaştırabilmektedir. Çok basamaklı sayılarla toplama-çıkarma işlemlerini güvenle yapabilmekte, çarpma işleminde zihinden stratejiler kullanmaktadır."

#### 5.3.5 4. Sınıf (9–10 yaş)

**Odağı:** İki basamaklı bölenle bölme, ondalık kesir girişi, alan-çevre hesaplamaları.

> "Elif, iki basamaklı bölenle bölme işlemini (720÷24 gibi) adım adım uygulayabilmektedir. Ondalık kesirleri tanımakta, ondalık gösterimi kesir ve yüzde ile ilişkilendirebilmektedir. Dikdörtgenin alan ve çevre hesaplamalarını yapabilmekte, bu kavramları günlük hayat problemlerinde uygulayabilmektedir."

### 5.4 Adaptif `totalShown` Mekanizması

#### 5.4.1 Yaş Grubu Bazlı Dinamik Soru Sayısı

| Yaş Grubu | Optimal Soru Sayısı | Maksimum Süre | Gerekçe |
|---|---|---|---|
| Okul Öncesi (5–6) | 20–30 | 15–20 dk | Dikkat süresi kısa; somut etkinlikler arası geçiş gerekir |
| 1. Sınıf (6–7) | 30–40 | 20–25 dk | Okuma-yazma becerisi gelişiyor; sembolik işlemler yorucu olabilir |
| 2. Sınıf (7–8) | 35–45 | 25–30 dk | İşlem çeşitliliği artıyor; eldeli işlemler dikkat gerektirir |
| 3. Sınıf (8–9) | 40–50 | 30–35 dk | Daha uzun süreli odaklanma mümkün; çok adımlı problemler |
| 4. Sınıf (9–10) | 40–50 | 35–40 dk | Soyut düşünme gelişiyor; daha karmaşık problemler çözülebilir |

**Tablo 15:** Yaş Grubu Bazlı Dinamik Soru Sayısı

#### 5.4.2 Performans Bazlı Ayarlama

**Yüksek Doğruluk (%85+):** Soru sayısı artırılır (yaş grubunun maksimumuna kadar). Öğrenci zorlanmadan daha fazla pratik yapar. Yorulma noktası izlenir; doğruluk düşmeye başladığında soru sayısı azaltılır.

**Düşük Doğruluk (%60 altı):** Soru sayısı azaltılır (yaş grubunun minimumuna kadar) ve destek modu aktifleştirilir. Kısa, başarı odaklı oturumlar öğrencinin motivasyonunu korur ve öğrenme kaygısını önler.

#### 5.4.3 MEB Portfolyo Yaklaşımıyla Entegrasyon

Adaptif `totalShown` mekanizması, MEB'in portfolyo yaklaşımıyla entegre edilebilir. Her oturum, öğrencinin mini-portfolyosuna bir kayıt olarak eklenir — süre, soru sayısı, doğruluk oranı, kullanılan stratejiler ve alınan geri bildirimler.

Zaman içindeki bu kayıtlar, uzun dönemli gelişim izleme için kullanılır. Örneğin: öğrencinin 1. sınıfın başında 30 soruluk oturumlarda %60 doğrulukla başladığı, yıl sonunda 40 soruluk oturumlarda %85 doğruluğa ulaştığı görülebilir.

Bu gelişim eğrisi, veli paylaşım raporlarında ve öğretmen değerlendirmelerinde somut bir kanıt olarak sunulabilir. Rapor dili, MEB müfredatının kazanım ifadelerine sadık kalır, teknik jargon içermez.

