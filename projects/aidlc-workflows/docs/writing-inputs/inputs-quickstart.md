# AI-DLC Hızlı Başlangıç

AI-DLC (Yapay Zeka Destekli Geliştirme Yaşam Döngüsü), bir yapay zeka asistanını yazılımı planlama, tasarlama ve inşa etme sürecinden geçiren yapılandırılmış bir iş akışıdır. Bir projeye başlamadan önce, yapay zekaya **ne inşa edileceğini** ve **hangi araçların kullanılacağını** söyleyen iki belge sağlarsınız.

---

## Sağlamanız Gerekenler

### 1. Vizyon Belgesi -- ne inşa edilecek ve neden

| Bölüm                       | Ne Yazılacak                                                              | Ne Kadar Uzun                                            |
| --------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Yönetici Özeti**         | Bir paragraf: nedir, kimin için, neden önemli                             | 3-5 cümle                                                |
| **Sorun Tanımı**           | Bu projenin çözdüğü spesifik iş sorunu                                    | 1-2 paragraf                                             |
| **Hedef Kullanıcılar**     | Kim kullanacak, her kullanıcı tipinin neye ihtiyacı var                   | Kullanıcı tipi başına bir satır içeren tablo             |
| **Başarı Metrikleri**      | Bu projenin başarılı olduğunu nasıl ölçersiniz                            | Ölçülebilir hedefler içeren tablo                        |
| **Tam Kapsam Vizyonu**     | Olgunluğa ulaştığında ürünün her şeyi olabileceği, özellik alanına göre organize edilmiş | İhtiyaç duyulan kadar özellik alanı                      |
| **MVP Kapsam -- Dahil Olan Özellikler**  | İlk sürümde dahil edilen her özellik, gerekçesiyle birlikte | Tablo. Listelenmediyse, MVP'de değildir. |
| **MVP Kapsam -- Açıkça Hariç Olan Özellikler** | Kasıtlı olarak MVP'den hariç tutulan özellikler, nedeni ve hedef aşamasıyla | Tablo. Kapsam sızmasını önler.           |
| **Riskler ve Açık Sorular**  | Ne yanlış gidebilir, ne hâlâ kararlaştırılmadı                            | Tablolar ve madde işaretli listeler                      |

**Temel ilke**: Tam vizyonu MVP'den ayırın. Tam vizyon heveslidir. MVP, değer sunan en küçük şeydir.

Tam kılavuz: [vision-document-guide.md](vision-document-guide.md)
Çalışılmış örnek: [example-vision-scientific-calculator-api.md](example-vision-scientific-calculator-api.md)

---

### 2. Teknik Ortam Belgesi -- hangi araçların kullanılacağı

| Bölüm                       | Ne Yazılacak                                                                                                                                   | Ne Kadar Uzun                                       |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **Diller**                 | Gerekli, izin verilen ve yasaklanan diller, sürümleriyle birlikte                                                                              | Kategori başına bir tablo                           |
| **Çerçeveler ve Kütüphaneler**  | Gerekli, tercih edilen ve yasaklananlar, gerekçe ve alternatiflerle birlikte                                                                   | Kategori başına bir tablo                           |
| **Bulut Servisleri**            | İzin listesi ve izin verilmeyen liste, kısıtlamalarıyla birlikte                                                                               | Liste başına bir tablo                              |
| **Mimari ve Kalıplar** | API stili, veri kalıpları, mesajlaşma, proje yapısı                                                                                          | Tablolarla kısa bölümler                            |
| **Güvenlik**                  | Kimlik doğrulama yöntemi, şifreleme, girdi doğrulama, sırlar yönetimi ve kategori başına belgelenmiş kontrollerle birlikte seçilen güvenlik uyumluluk çerçevesi | Birkaç alt bölüm                                    |
| **Test**                     | Test türleri, kapsam hedefleri, araçlar, CI/CD geçitleri                                                                                       | Tablolar                                            |
| **Örnek Kod**              | Uç noktalar, fonksiyonlar, testler ve altyapı için tipik kalıpları gösteren şablon kod                                                        | `examples/` dizininde çalışan kod dosyaları         |

**Temel ilke**: Neye izin verildiğini ve neye izin verilmediğini açıkça belirtin. İzin listeleri ve izin verilmeyen listeler, yapay zekanın varsayımlar yapmasını engeller.

Tam kılavuz: [technical-environment-guide.md](technical-environment-guide.md)
Çalışılmış örnek: [example-tech-env-scientific-calculator-api.md](example-tech-env-scientific-calculator-api.md)

---

## Minimum Uygulanabilir Girdi

Hızlı başlamak ve ayrıntıları sonra doldurmak istiyorsanız, en az bunu sağlayın:

### Vizyon (minimum)

```text
1. Ne inşa ettiğinizi ve kimin için olduğunu söyleyen bir paragraf
2. MVP özelliklerinin bir listesi (kapsamda olanlar)
3. MVP'de olmayanların bir listesi
4. Açık sorular -- halihazırda belirsiz veya çözülmemiş olduğunu bildiğiniz şeyler
```

Açık sorular isteğe bağlıdır ama değerlidir. Bunlar doğrudan Gereksinimler Analizine önceden bildirilmiş belirsizlikler olarak girer, bu nedenle tasarımın ortasında sürpriz olarak ortaya çıkmak yerine erken çözülürler.

Çalışılmış örnek için [example-minimal-vision-scientific-calculator-api.md](example-minimal-vision-scientific-calculator-api.md)'ye bakın.

### Teknik Ortam (minimum)

```text
1. Dil ve sürüm
2. Paket yöneticisi
3. Web çerçevesi (uygulanabilirse)
4. Bulut sağlayıcısı ve dağıtım modeli (veya "yalnızca yerel")
5. Test çerçevesi
6. Yasaklı kütüphaneler ve servisler -- tablo kullan: yasaklı | neden | bunun yerine kullan
7. Güvenlik temelleri (kimlik doğrulama yöntemi, girdi doğrulama yaklaşımı, sırlar yönetimi)
8. Örnek kod kalıpları -- tipik bir uç nokta, fonksiyon ve test için birer kısa örnek
```

**Madde 6 hakkında**: nedeni ve önerilen alternatifi içermek önemlidir. Bunlar olmadan, AI-DLC yasağa saygı gösterebilir ama iyi ikame kararları vermek için niyeti yeterince anlamayabilir.

**Madde 8 hakkında**: bir veya iki kısa örnek bile, AI-DLC'ye kod oluşturma sırasında kendi başına bir şey icat etmek yerine takip edeceği somut bir kalıp verir. Bu, temel bilgilerin ötesindeki en yüksek kaldıraçlı eklentidir.

Çalışılmış örnek için [example-minimal-tech-env-scientific-calculator-api.md](example-minimal-tech-env-scientific-calculator-api.md)'ye bakın.

Gerisi, Başlangıç aşaması boyunca AI-DLC'nin açıklayıcı sorularıyla yanıtlanabilir. Önceden ne kadar çok sağlarsanız, yapay zekanın sorması gereken soru o kadar az olur.

---

## Brownfield Projeleri

Mevcut bir kod tabanına ekleme yapıyor veya değişiklik yapıyorsanız, girdileriniz farklı bir soru setini yanıtlaması gerekir. Tam kılavuzlar brownfield'i ayrıntılı olarak ele alır, ancak minimum şunlardır:

### Vizyon (brownfield minimum)

```text
1. Mevcut durum -- sistemin bugün ne yaptığını anlatan bir paragraf
2. Ne ekliyor veya değiştiriyoruz -- değişikliğin net bir açıklaması
3. Bu yineleme için kapsamda olan özellikler
4. Bu yineleme için kapsam dışı olan özellikler
5. Değişmemesi gerekenler -- yeni çalışmanın dokunmaması gereken mevcut bileşenler, API'ler veya veriler
6. Açık sorular
```

"Değişmemesi gerekenler" bölümü kritiktir. AIDLC mevcut kod tabanınızı analiz etmek için bir Tersine Mühendislik aşaması çalıştıracaktır, ancak sınırları açıkça belirtmek, sistemin çalışan kısımlarını dengesizleştirecek değişiklikler önermesini engeller.

Çalışılmış örnek için [example-minimal-vision-brownfield.md](example-minimal-vision-brownfield.md)'ye bakın.

### Teknik Ortam (brownfield minimum)

```text
1. Mevcut yığın -- dil, çerçeve, veritabanı, altyapı -- sürümleriyle birlikte
2. Ne eklenecek (yeni servisler, tablolar, bileşenler)
3. Değişmeden kalması gerekenler -- dokunulmaması gereken servisler, şemalar, sözleşmeler, yapılandırmalar
4. Yasaklı kalıplar -- mevcut kod tabanıyla çatışan kütüphaneler veya yaklaşımlar
5. Güvenlik temelleri -- mevcut sistemde kimlik doğrulama ve sırlar nasıl çalışıyor
6. Mevcut kod tabanından örnek kod kalıpları
```

Örnek kod kalıpları brownfield için özellikle önemlidir. AI-DLC, mevcut kod tabanına aitmiş gibi görünen kod oluşturmalıdır, eskilerinin yanında yeni kurallar tanıtan kod değil. Örneklerinizi gerçek mevcut dosyalardan çekin.

Çalışılmış örnek için [example-minimal-tech-env-brownfield.md](example-minimal-tech-env-brownfield.md)'ye bakın.

---

## Belgeleri Sağladıktan Sonra Ne Olur

AI-DLC iki ana aşamadan geçer:

**Başlangıç** -- anla ve planla

1. Çalışma alanınızı algılar (yeni proje veya mevcut kod)
2. Gereksinimleri analiz eder (bir şey belirsizse açıklayıcı sorular sorar)
3. Kullanıcı hikayeleri oluşturur (proje bunu gerektiriyorsa)
4. Bir yürütme planı oluşturur (hangi aşamaların çalıştırılacağı, hangilerinin atlanacağı)
5. Bileşenleri ve iş birimlerini tasarlar (karmaşıklık bunu gerektiriyorsa)

**Yapım** -- tasarla ve inşa et (iş birimi başına)

1. Fonksiyonel tasarım (iş mantığı, domain modelleri)
2. NFR gereksinimleri ve tasarımı (performans, güvenlik, ölçeklenebilirlik)
3. Altyapı tasarımı (gerçek bulut servislerine eşleme)
4. Kod oluşturma (kodu, testleri ve dağıtım yapıtlarını yazar)
5. Yapı ve test (derleme talimatları, test yürütme, doğrulama)

Her aşama, ilerlemeden önce onayınızı gerektirir. Herhangi bir geçitte değişiklik isteyebilir, atlanan aşamalar ekleyebilir veya yönlendirebilirsiniz.

---

## Dosya Genel Bakışı

```text
docs/writing-inputs/
  inputs-quickstart.md                               <-- Buradasınız
  vision-document-guide.md                           <-- Vizyon belgesi nasıl yazılır
  technical-environment-guide.md                     <-- Teknik ortam belgesi nasıl yazılır

  -- Greenfield örnekleri (sıfırdan yeni proje) --
  example-vision-scientific-calculator-api.md        <-- Tam örnek: CalcEngine vizyonu
  example-tech-env-scientific-calculator-api.md      <-- Tam örnek: CalcEngine teknik ortam
  example-minimal-vision-scientific-calculator-api.md<-- Minimum örnek: CalcEngine vizyonu
  example-minimal-tech-env-scientific-calculator-api.md<-- Minimum örnek: CalcEngine teknik ortam

  -- Brownfield örnekleri (mevcut sisteme ekleme) --
  example-minimal-vision-brownfield.md               <-- Minimum örnek: mevcut platforma iade modülü
  example-minimal-tech-env-brownfield.md             <-- Minimum örnek: mevcut platforma iade modülü
```
