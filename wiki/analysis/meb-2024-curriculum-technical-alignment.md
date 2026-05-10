---
title: "MEB 2024 Müfredatı ile Teknik Sistem Uyum Analizi ve Çözüm Çerçevesi"
created: "2026-05-08"
updated: "2026-05-10"
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

> Bu bölüm ayrı sayfaya çıkarılmıştır: [[meb-2024-curriculum-render|Matematiksel Temsil ve Android Render Uyumu →]]

## 3. Veri Modeli Ontolojisi: Tip Standardizasyonu ve ID Çakışması

> Bu bölüm ayrı sayfaya çıkarılmıştır: [[meb-2024-curriculum-ontoloji|Veri Modeli Ontolojisi ve ID Standardizasyonu →]]

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

