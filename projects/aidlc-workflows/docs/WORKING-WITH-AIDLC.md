# AI-DLC ile Çalışmak

Bu kılavuz, AI-DLC (Yapay Zeka Destekli Geliştirme Yaşam Döngüsü)'nden en iyi şekilde yararlanmanıza yardımcı olur. İlk prompt'tan çalışan koda kadar her aşamada yapay zeka ile nasıl etkili etkileşim kuracağınızı kapsar.

Her bölümde temel bilgilerle başlayın. İleri düzey ipuçları, gerçek atölye deneyimlerinden çıkarılmıştır ve ekiplerin temelleri öğrendikten sonra en faydalı bulduğu kalıpları ele alır.

---

## İçindekiler

1. [Genel Kurallar](#1-genel-kurallar)
2. [Başlangıç Aşaması (Inception)](#2-başlangıç-aşaması-inception)
3. [Yapım Aşaması (Construction)](#3-yapım-aşaması-construction)
4. [Asla Doğaçlama Kod Yazma](#4-asla-doğaçlama-kod-yazma)

---

## 1. Genel Kurallar

### Dosyaları Değiştirmeden Soru Sormak

Erken dönemde edinmeniz gereken en önemli alışkanlıklardan biri: **her sorunun bir belge güncellemesini tetiklememesi gerektiğidir**.

Yapay zekaya bir şey sorduğunuzda, sorunuzu koruyucu bir ifadeyle çerçevelemezseniz, bunu bir değişiklik isteği olarak yorumlayıp hemen tasarım belgelerini güncelleyebilir. Keşif amaçlı sorularınızı, net bir "değiştirme" talimatıyla öne ekleyerek bunu önleyin.

**Temel kalıp:**

```text
Hiçbir belgeyi güncelleme. [Bu kararın] neden verildiğini anlamama yardım et.
```

```text
Hiçbir belgeyi güncelleme. [Bileşen adı] için burada [kütüphane veya teknoloji] kullanmak makul mü?
```

```text
Hiçbir şeyi değiştirme. [Önerilen değişikliğin] etkisini değerlendir.
Sonuçlarını anlamak istiyorum, karar vermeden önce.
```

Bu kalıplar, yapay zeka ile düşünce yürütmenize, seçenekleri değerlendirmenize ve kararlara bağlı kalmadan meydan okumanıza olanak tanır. Cevaptan memnun olduğunuzda, gerekiyorsa bilinçli bir güncelleme talimatıyla devam edebilirsiniz.

> **İpucu**: Her keşif amaçlı mesaja "Hiçbir belgeyi güncelleme." ile başlayın. Harekete geçmeye hazır olduğunuzda bu kısıtlamayı her zaman kaldırabilirsiniz.

---

### Soru → Belge → Onay Akışı

AIDLC, sohbet içinde açıklayıcı sorular sormaz. Soruları bir markdown dosyasına yazar ve sizin orada cevaplarınızı doldurmanızı bekler. Bu, her kararın kalıcı bir kaydını tutar ve tüm ekibin katkıda bulunmasını kolaylaştırır.

**Adım 1 — AIDLC soru dosyası oluşturur**

Yapay zeka, `aidlc-docs/inception/requirements/requirement-verification-questions.md` gibi bir dosya oluşturur ve durur. Siz cevap verene kadar ilerlemez.

**Adım 2 — Siz cevaplarınızı doldurursunuz**

Dosyayı açın ve her `[Cevap]:` etiketini doldurun. Sorular çoktan seçmeli formattadır:

```markdown
## Soru: Dağıtım modeli
Bu servis nerede dağıtılacak?

A) AWS Lambda (sunucusuz)

B) AWS ECS Fargate (konteynerleştirilmiş)

C) Mevcut şirket içi altyapı

X) Diğer (lütfen aşağıdaki [Cevap]: etiketinden sonra açıklayın)

[Cevap]: B
```

Cevap verirken işe yarayan birkaç şey:

- **Harfin yanına bir etiket ekleyin.** `C — finansal özet ve borç hizmet kapsamı`, yalnızca `C`'den daha nettir.
- **Kısa bir gerekçe ekleyin.** `A — tasarım öncelikli; kod yazmadan önce OpenAPI spesifikasyonunu oluştur` niyeti doğrular ve yapay zekaya ileriye taşıyacağı bağlamı verir.
- **İkisini de kastettiğinizde seçenekleri birleştirin.** `B ve C — hem API Gateway düzeyinde hem de uygulama düzeyinde hız sınırlama (D değil)` belirsizliği ortadan kaldırır.
- **Seçenek neredeyse doğruyken bir uyarı ekleyin.** `B — geçiş ayrı bir projedir; ancak, yeni veri yapılarına tek seferlik bir geçiş dahil edin.`
- **X'i özgürce kullanın.** Hiçbiri uygun değilse, X, zorla yanlış bir cevap vermekten daha doğru seçimdir.

**Adım 3 — Yapay zekaya cevaplarınızın hazır olduğunu söyleyin**

Sohbete dönün ve şöyle deyin: "Açıklayıcı sorularınızı cevapladık. Lütfen dosyayı yeniden okuyun ve devam edin."

İpucu: yapay zekadan dosyayı *yeniden okumasını* açıkça istemek, en son düzenlemelerinizi yansıtmayan bir bellek içi sürüme güvenmek yerine yanıtlarını diskten yüklemesini sağlar.

**Adım 4 — AIDLC doğrular ve ilerler**

Yapay zeka cevaplarınızı okur, kalan belirsizlikleri işaretler ve bir sonraki çıktıyı oluşturmaya devam eder.

> **İleri düzey ipucu**: Sorularınızı yanıtlayan bir dokümantasyonunuz varsa, bunları kendisinin çözmesini isteyebilirsiniz: "Her sorunun gerekçesini analiz et. Eğer bir soru sağlanan dokümantasyonla zaten yanıtlanmışsa, kendin yanıtla. Yalnızca hâlâ belirsizse bana sor." Bu, kontrol noktalarında gereksiz gidip gelmeleri azaltır.

**Onay geçitleri**

Her aşamanın sonunda AIDLC, iki seçenekli bir tamamlama mesajı sunar:

- **Değişiklik İste** — ilerlemeden önce değişiklik isteyin
- **Onayla ve Devam Et** — çıktıyı kabul edin ve ilerleyin

Onay vermeden önce oluşturulan çıktıyı okuyun. Gerekirse ekibinizle tartışın. Yalnızca memnun olduğunuzda onaylayın.

---

### Bağlam Yönetimi

Bağlam, yapay zekanın oturum için çalışma belleğidir. AIDLC, tutarlı aşağı akış çıktıları üretmek için yapıtlar ve talimatların tam zincirinin bağlamda olmasına bağlıdır. Bunu iyi yönetmek, geliştirebileceğiniz en yüksek kaldıraçlı alışkanlıklardan biridir.

**Temel kural: Bağlamı her doğal karar noktasında temizleyin.**

AIDLC, yapay zekanın durup size bir şey sorduğu anlar olan geçitler etrafında inşa edilmiştir: yanıtlanacak bir soru dosyası, onaylanacak bir belge, incelenecek bir plan. Bu duraklar yalnızca onay kontrol noktaları değildir. Devam etmeden önce taze bir bağlam başlatmak için doğru anlardır.

Bir geçitte bağlamı temizlemek düşük risklidir çünkü yapay zekanın mevcut çalışması zaten dosyalara kaydedilmiştir. Bir sonraki bağlam temiz başlar, ilgili yapıtları diskten yükler ve önceki adımların birikmiş gürültüsünü taşımadan ilerler.

Birden fazla geçitte bağlamın birikmesine izin verirseniz, yapay zeka önceki talimatların ve yapıtların sıkıştırılmış veya kısmen kaybolmuş bir sürümünden çalışmaya başlar. Çıktı kalitesi, ince ve teşhisi zor olan şekillerde düşer.

**Pratikte:**

- Yapay zeka size bir soru dosyasını yanıtlamanızı istediğinde — soruları yanıtlayın, sonra **taze bir bağlam başlatın** ve yapay zekaya dosyayı yeniden okumasını ve devam etmesini söyleyin
- Yapay zeka onay için bir belge sunduğunda — inceleyin, sonra değişiklik istemek veya onaylayıp ilerlemek için **taze bir bağlam başlatın**
- Aracınız iş akışının ortasında "bağlamı sıkıştır" istemi sunarsa, **her zaman reddedin** — sıkıştırma, temiz bir sıfırlama ile aynı değildir ve kurtardığından daha fazlasını kaybeder

**Bağlam sıfırlamasından sonra nasıl devam edilir:**

Seçenek 1 — Durum dosyası yöntemi (önerilen):

```text
aidlc-docs/aidlc-state.md'e git, ilk işaretlenmemiş öğeyi bul,
sonra ilgili plan dosyasına git ve o noktadan devam et.
```

Seçenek 2 — Manuel devretme:

```text
Daha önce durdurulmuş bir konuşmaya devam ediyorum. İşte bağlam:
[son çıktının veya yakın zamandaki değişikliğin özetini yapıştırın]
Lütfen [bir sonraki eylem veya X bölümü] ile devam et.
```

> **İpucu**: Bağlamı her sıfırladığınızda mevcut tüm değişiklikleri depoya işleyin ve gönderin. Saniyeler sürer ve her zaman temiz bir kurtarma noktasına sahip olmanızı sağlar.

```text
Lütfen mevcut tüm değişiklikleri depoya işleyin ve gönderin.
```

---

### Prompt'ları Toplu Gönderme

Tüm prompt'lar ayrı ayrı gönderilmemelidir. Atölye deneyiminden basit bir kural:

**İki değişiklik aynı konuya sıkıca bağlıysa, her ikisini de tek bir prompt'ta içerebilirsiniz. İki değişiklik ilişkisizse, tek tek yapın.**

Aşırı toplu gönderme (ilişkisiz değişiklikleri birleştirmek), yapay zekanın odaklanmasını kaybetmesine ve ayrıntıları kaçırmasına neden olur. Yetersiz toplu gönderme (yakından ilişkili şeyler için ayrı prompt'lar) gereksiz gidip gelmelere neden olur. Şüpheye düştüğünüzde, ayırma yönünde hata yapın.

---

### Harici Referans Dosyaları Yükleme

AIDLC'yi herhangi bir mevcut belgeye — bir şema, bir mimari diyagram, bir veri sözlüğü, bir API spesifikasyonu — yönlendirebilir ve içeriği mevcut aşamaya dahil edebilirsiniz.

**Temel kalıp:**

```text
Lütfen [dosya yolu veya açıklama] okuyun. [İstediğiniz şey] için temel olarak kullanın.
```

```text
Mevcut bir denetim tablosu yapımız var. Lütfen bunu başlangıç belgelerine ekleyin
ve bu servis için referans gösterin. İlerlediğimizde, bu servisle ilgili yeni gereksinimler ve
hikayeler bekleyin.
```

> **İleri düzey ipucu**: Belgeleri yalnızca başlangıçta değil, herhangi bir aşamada yükleyebilirsiniz. Yapım aşamasında yeni bir kısıt ortaya çıkarsa — güncellenmiş bir güvenlik politikası, revize edilmiş bir veri modeli — yükleyin ve AIDLC'nin ilerlemeden önce etkisini değerlendirmesini isteyin.
>
> **İleri düzey ipucu — Kurumsal standartlar olarak uzantılar**: Kuruluşunuzun her projeye uygulanması gereken güvenlik, uyumluluk veya API yönergeleri varsa, bunları `aidlc-rules/extensions/` altında bir markdown yönlendirme dosyası olarak ekleyin. AIDLC bunları manuel enjeksiyon gerektirmeden her aşamaya otomatik olarak yükleyecektir.

---

### Bağımsız Eleştiriler Almak

AIDLC, kendi önceki kararlarını savunacaktır. Bir yapıtın tarafsız bir değerlendirmesini istediğinizde, yapay zekanın bu kararları neden verdiğını hatırlamadığı **taze bir bağlamda** eleştiri isteyin.

```text
[Gereksinimler belgesi / bileşen tasarımı] için bir eleştiri belgesi üret.
Bunu diğer her şeyden ayrı yeni bir bağlamda yap.
```

Bu, yapıtın oluşturulduğu aynı oturumda eleştiri istemekten daha kullanışlı, nesnel geri bildirim üretir.

---

### Derinlik Seviyeleri

AIDLC, her aşamayı isteğinizin karmaşıklığına göre ne kadar derinlemesine yürüteceğini ayarlar. Bunu etkileyebilirsiniz.

```text
Bunu minimum derinlikte tut — yalnızca temel yapının belgelenmesine ihtiyacımız var.
```

```text
Bu üretim kritik bir bileşendir. Lütfen kapsamlı derinlikte çalıştır.
```

---

## 2. Başlangıç Aşaması (Inception)

Başlangıç aşaması, herhangi bir tasarım veya kod çalışması başlamadan önce sizin ve yapay zekanın *ne inşa edileceği ve neden* konusunda anlaşma sağladığı yerdir. Burada ne kadar çok bağlam getirirseniz, Yapım aşamasında o kadar az açıklayıcı soru ve o kadar az yeniden çalışma ile karşılaşırsınız.

### Başlamadan Önce Girdilerinizi Hazırlayın

AIDLC'yi başlatmadan önce yapabileceğiniz en etkili şey iki belge hazırlamaktır:

1. **Vizyon Belgesi** — ne inşa edilecek ve neden
2. **Teknik Ortam Belgesi** — hangi araçlar ve kısıtlar geçerli

Bu belgeler, AIDLC'nin soracağı açıklayıcı soruların sayısını önemli ölçüde azaltır ve yapay zekanın varsayımlar yapmak yerine ekibinizin gerçek bağlamından başlamasını sağlar.

**Nereden başlayacağınız:**

- [writing-inputs/inputs-quickstart.md](writing-inputs/inputs-quickstart.md) — hem greenfield hem de brownfield için hızlı özet
- [writing-inputs/vision-document-guide.md](writing-inputs/vision-document-guide.md) — şablonlarla tam vizyon kılavuzu
- [writing-inputs/technical-environment-guide.md](writing-inputs/technical-environment-guide.md) — şablonlarla tam teknik ortam kılavuzu

**Brownfield projeleri** (mevcut bir kod tabanına ekleme yapma) biraz farklı girdilere ihtiyaç duyar. Vizyon belgesi mevcut durum tanımı ve değişmemesi gerekenlerin açık bir listesi gerektirir. Teknik ortam belgesi mevcut yığını tanımlamalıdır, istenen bir yığın değil, ve örnek kodlar gerçek mevcut dosyalardan gelmelidir. Brownfield minimumu ve çalışılmış örnekler için [writing-inputs/inputs-quickstart.md](writing-inputs/inputs-quickstart.md)'ye bakın.

**Hızlı başlamak istiyorsanız minimum uygulanabilir girdi:**

Vizyon için: ne inşa ettiğinizi ve kimin için olduğunu anlatan bir paragraf, kapsamda olan MVP özelliklerinin bir listesi, açıkça kapsam dışı olan özelliklerin bir listesi ve açık sorular — halihazırda belirsiz olduğunu bildiğiniz şeyler. Açık sorular doğrudan Gereksinimler Analizine önceden bildirilmiş belirsizlikler olarak girer, bu nedenle tasarımın ortasında sürpriz olarak ortaya çıkmak yerine erken çözülürler.

Teknik Ortam için: dil ve sürüm, paket yöneticisi, web çerçevesi, bulut sağlayıcısı ve dağıtım modeli, test çerçevesi, yasaklı kütüphaneler tablosu (her biri için neden ve önerilen alternatif) ve bir tipik uç nokta, fonksiyon ve test için en az birer örnek.

Yasaklı kütüphaneler tablosu, düz bir listeden daha önemlidir — neden ve alternatif sütunları AI-DLC'ye bir kütüphanenin neden yasaklandığını söyler, bu da daha iyi ikame kararlarına yol açar. Örnek kod kalıpları, temel bilgilerin ötesindeki en yüksek kaldıraçlı eklentidir: kod oluşturma sırasında AI-DLC'ye kendi başına bir şey icat etmek yerine takip edeceği somut bir kalıp verir.

> **İpucu**: Önceden doldurduğunuz her boşluk, Gereksinimler Analizi sırasında bir açıklayıcı soru daha az demektir.

---

### Yeni Bir Projeye Başlarken

Girdi belgeleriniz hazır olduğunda:

```text
Yeni bir proje başlatmak istiyorum. Lütfen [vizyon belgesi yolu] ve
[teknik ortam belgesi yolu] okuyun, sonra AIDLC iş akışına başlayın.
```

AIDLC çalışma alanınızı tarayacak, greenfield veya brownfield olduğunu belirleyecek ve belgelerinizi birincil kaynak olarak kullanarak yalnızca kapsamadıklarını sorarak Gereksinimler Analizine devam edecektir.

Brownfield projesi için AIDLC önce Tersine Mühendislik çalıştırarak mevcut kod tabanınızı analiz eder ve mimari, bileşen ve API dokümantasyonu üretir. Bu yapıtları dikkatlice inceleyin — sonraki her şeyin temelini oluştururlar.

---

### Gereksinim Sorularını Yanıtlamak

Tam rehber için [Bölüm 1](#soru--belge--onay-akışı)'deki yanıtlama ipuçlarına bakın; harf kullanma, etiket ekleme, seçenekleri birleştirme ve özel yanıtlar için X kullanma konusunda rehberlik içerir. Gereksinimler Analizi'ne özgü birkaç ek nokta:

- **Tam vizyonu MVP'den açıkça ayırın.** AIDLC hangi özellikleri dahil edeceğini sorarsa, adlarını verin. Bir şey kapsam dışıysa, söyleyin — belirsiz bırakmayın.
- **Bilinçli "hayır" kararlarını açıkça belirtin.** `D — şu anda önbelleğe alma gerekli değil` niyeti bildirir. Boş bir cevap, yapay zekanın spekülatif bir seçim yapmasına davetiye çıkarır.
- **Aşamalı yaklaşımları satır içinde açıklayın.** `X — şimdilik basit rol tabanlı iş akışı; mevcut olduğunda harici iş akışı motoru ile değiştir` AIDLC'nin mevcut çözümü doğru genişleme noktalarıyla tasarlamasına olanak tanır.

> **İleri düzey ipucu — Güvenlik Uzantıları**: Gereksinimler Analizi sırasında AIDLC, güvenlik uzantı kurallarını uygulamak isteyip istemediğinizi soracaktır. Üretim kalitesinde uygulamalar için Evet'i seçin. Prototipler için Hayır yeterlidir. Bu karar kaydedilir ve Yapım aşaması boyunca uygulanır, bu nedenle bilinçli seçin.

---

### Başlangıç'a Özgü Etkileşimler

**Bir özelliği akış sırasında erteleme:**

```text
[Özellik adı] yeteneğini mevcut sürüm için biriktirme listesine alacağız.
Lütfen bunu bileşen tasarımından kaldırın ve ilgili kullanıcı hikayelerini
biriktirme listesine alınmış olarak işaretleyin.
```

Biriktirme listesine almak (silme yerine), çalışmanın gelecekteki yinelemeler için korunmasını sağlar, ancak mevcut yapıyı etkilemez.

**Mevcut bir veri yapısını kaydetme:**

```text
Mevcut bir [şema/yapı adı]mız var. Lütfen bunu başlangıç belgelerine ekleyin
ve bu servis için referans gösterin. İlerlediğimizde, bu servisle ilgili yeni gereksinimler ve
hikayeler bekleyin.
```

**Örtük veri kaynaklarını açık hale getirme:**

```text
[Servis adı] için, [yeni veri kaynağı]nın da bu özellik için bir veri kaynağı
olduğunu, [mevcut veri kaynağı]na ek olarak ekleyin. Sonra bunun yakalandığından
emin olmak için gereksinimleri ve kullanıcı hikayelerini gözden geçirin.
```

**Tasarım değişikliğinden sonra yukarı akış etkisini kontrol etme:**

Bir tasarım yapıtında anlamlı bir değişiklikten sonra, AIDLC'den önceki belgelerin hâlâ tutarlı olup olmadığını kontrol etmesini isteyin:

```text
Şimdi önceki adımları gözden geçirin — kullanıcı hikayeleri ve gereksinimler —
bu değişikliğin bu belgelerden herhangi birinin güncellenmesini gerektirip
gerektirmediğinden emin olun.
```

> **İleri düzey ipucu — Kalıcı geri yayılım kuralı**: Her değişiklikten sonra sormak yerine, bunu bir aşamanın başında kalıcı bir talimat olarak belirleyin: "Bir belgeyi her güncellediğinizde, değişikliğin gereksinimler belgesini ve kullanıcı hikayelerini etkileyip etkilemediğini kontrol edin ve etkiliyorsa bana bildirin." Bu, sizin hatırlamanızı gerektirmeden otomatik bir güvenlik ağı oluşturur.

**Bileşen tasarımının paralel ekip incelemesi:**

Ekibiniz farklı bileşenleri aynı anda incelemek için bölünürse:

```text
Düzenlemelerinizi ekibinizin kontrolündeki dosyalara sınırlayın. Herkes bitirdiğinde,
yapay zekadan tüm değişiklikleri incelemesini ve çakışma olmadığını doğrulamasını isteyeceğiz.
Sonra kullanıcı hikayeleri ve gereksinimlere etkilerini incelemesini isteyeceğiz.
```

Herkes bitirdiğinde, çakışma kontrolünü tetikleyin:

```text
[Bileşen tasarımı] dosyalarını bağımsız olarak düzenleyen [N] grup vardı. Lütfen tüm dosyaları
inceleyin ve çakışma veya tutarsızlık olup olmadığını rapor edin. Dosyaları düzenlemeyin —
incelememiz için bir rapor üretin.
```

Her çakışmayı numarasıyla açıkça çözün:

```text
[number] numaralı çakışma ([çakışma açıklaması]) için:
[kararınızı] yansıtmak üzere [hedef dosya] güncelleyin.
```

```text
[number] numaralı çakışma ([yetenek adı]):
Bu yetenek biriktirme listesine alındı. Kod oluşturmanın bunu uygulamaya çalışmaması için
dokümantasyonu açıkça biriktirme listesine alınmış olarak işaretleyin.
```

**Eski tasarım dosyalarını arşivleme:**

Tasarım sırasında üretilen ve artık gerekli olmayan dosyalar varsa:

```text
[Dosya açıklamaları] bir arşiv klasörüne taşıyın — silmeyin.
Sonra bunların kod oluşturma için gerekli olup olmadığını doğrulayın.
```

> **İleri düzey ipucu — Bileşen boyutu kısıtlamaları**: Tek bir sprintte uygulanamayacak kadar büyük bileşenleri önlemek istiyorsanız, Uygulama Tasarımı sırasında bir hikaye puanı sınırı belirleyin: "Bileşen tasarım aşamasında şu talimatı enjekte edin: tek bir bileşen [X] toplam hikaye puanından fazla olmamalıdır. Bir bileşen bu sınırı aşarsa, daha küçük alt bileşenlere bölün."
>
> **İleri düzey ipucu — Aşama ortasında bağlam sıfırlamaları**: Oturumunuz kesilirse, durumu yeniden oluşturmak için bunu kullanın:
>
> ```text
> Dur. Yeni bağlam. Az önce [yakın zamandaki çalışmanın açıklaması] tamamladık.
> Lütfen [yukarı akış yapıtlarını] yakın zamandaki değişikliğin etkisini değerlendirmek için inceleyin.
> [Değişiklik açıklamasını buraya yapıştırın.]
> ```

---

## 3. Yapım Aşaması (Construction)

Yapım aşaması, tasarımların koda dönüştüğü yerdir. Her iş birimi, bir dizi tasarım aşamasından (koşullu) geçer, ardından Kod Oluşturma (her zaman) gelir. Tüm birimler tamamlandığında, Yapı ve Test çalışmayı kapatır.

### Tasarım İnceleme Süreci

Her iş birimi için AIDLC, kod oluşturmadan önce bu tasarım aşamalarından bazılarını veya tümünü yürütebilir:

- **Fonksiyonel Tasarım** — iş mantığı, domain modelleri, veri şemaları
- **NFR Gereksinimleri** — performans, güvenlik, ölçeklenebilirlik, teknoloji yığını seçimi
- **NFR Tasarımı** — tasarıma NFR kalıplarının uygulanması
- **Altyapı Tasarımı** — tasarımın gerçek bulut servislerine eşlenmesi

Her aşama, `aidlc-docs/construction/{birim-adı}/` altında bir belge üretir. Her geçitteki göreviniz belgeyi okumak ve karar vermektir: değişiklik iste veya onayla.

**Onay vermeden önce okuyun.** Tasarım belgeleri, kod oluşturma için tek doğru kaynaktır. Burada sızan hatalar daha sonra düzeltilmesi daha zordur.

**Tasarımdan koda geçiş:**

Kod Oluşturmaya geçmeye hazır olduğunuzda, yapay zekaya ihtiyaç duyduğu yapısal bağlamı önceden verin:

```text
Bileşen tasarım incelemesini tamamladık. Kod oluşturmaya hazırız.
Lütfen aşağıdaki dizin ve kaynak kod yapısını kullanın:
[mevcut bir servise veya klasör yapısına referans verin].
API'ler için bu kalıbı kullanın. UI için [Vue.js composables/components/store]
dizin yapısını takip edin. Lütfen ilerlemeden önce sahip olduğunuz soruları sorun.
```

Oluşturma başlamadan önce soruları davet etmek, belirsizlikleri dosya oluşturmanın ortasında değil, planda çözer.

**Hedefli bir düzeltme isteme:**

Kesin olun — elemanı adlandırın, yanlış olan ve ne olması gerektiğini belirtin:

```text
[Uç nokta açıklaması], [yanlış parametre] yerine [doğru parametre] kullanmalıdır.
Lütfen [bileşen adı] buna göre güncelleyin.
```

**Yapay zekanın sunduğu seçenekler arasında seçim yapma:**

```text
Lütfen [özellik adı] için B Seçeneğini uygulayın — [seçenek açıklaması].
Tüm bileşen tasarım belgelerini buna göre güncelleyin.
```

Seçeneği hem harf hem de açıklama ile referans alın ve güncellemeyi açıkça sorunun çıktığı tek belgeyle sınırlamayın, etkilenen tüm belgelere yayın.

**Bir tasarım kalıbını geçersiz kılma:**

```text
[Standart kalıp]ndan sapmayı ve [tercih ettiğimiz yaklaşım] kullanmayı tercih ediyoruz,
[gerekçe] sağlamak için. Lütfen bileşen tasarım belgelerini buna göre güncelleyin.
```

Gerekçe önemlidir. AIDLC bunu sonraki aşamalara taşır, bu da sapmanın sessizce tersine çevrilmesini önler.

> **İleri düzey ipucu — Taahhüt etmeden önce etki değerlendirmesi**: Herhangi bir önemli tasarım değişikliği için, hareket etmeden önce değerlendirin:
>
> ```text
> Hiçbir şeyi değiştirme. [Önerilen değişikliğin] etkisini değerlendir.
> [Önerilen değişikliği ayrıntılı olarak açıkla.]
> ```
>
> **İleri düzey ipucu — Satır içi kod dokümantasyonu**: Her birime tutarlı olarak uygulanacak satır içi dokümantasyon istiyorsanız, bunu Yapım aşamasının başında kalıcı bir kural olarak eklemek, birim başına tekrarlamaktan daha iyidir: "Satır içi kod dokümantasyonunu yapım aşaması için standart bir kural olarak ekle."

---

### Kod Oluşturma Süreci

Kod Oluşturmanın iki ayrı bölümü vardır. Her ikisi de açık onayınızı gerektirir.

**Bölüm 1 — Planlama**

AIDLC, oluşturulacak veya değiştirilecek her dosya için numaralandırılmış, onay kutusuyla izlenen bir plan oluşturur. Onaylamadan önce bu planı inceleyin. Şunları kontrol edin:

- Her dosya doğru konumda (uygulama kodu çalışma alanı kökünde, asla `aidlc-docs/` içinde değil)
- Adımlar tasarım belgelerinizin belirttiği her şeyi kapsıyor
- Brownfield projeleri, yeni kopyaların yanında değil, değiştirilecek mevcut dosyaları listeliyor

> **İleri düzey ipucu — Dahili kütüphaneler**: Planı onaylamadan önce, dahili kütüphane gereksinimlerinizi Q&A dosyasına veya uygulama planına enjekte edin:
>
> ```text
> Cevaplarıma ek olarak, başlangıç projemizden / yapı taşlarımızdan aşağıdaki
> kütüphaneleri kullanmalısın: [her birini açıkça listele].
> Her birinin ne olduğunu değil, neden ve ne zaman kullanılacağını açıkla.
> ```
>
> Dahili kütüphanelerinize hazırlanmış bir markdown kılavuzu, yapay zekayı bir depoya yönlendirmekten daha iyi çalışır. Bir tane oluşturun ve kod oluşturma girdisi olarak referans verin.
>
> **İleri düzey ipucu — Figma tasarımlarından UI**: Figma tasarımınızın ekran görüntüsünü alın, bir görü kapasiteli modele (örn. ChatGPT) aktarın ve ekran görüntüsünden çerçeve kodu oluşturmasını sağlayın, sonra bu çıktıyı AIDLC'ye UI uygulama girdisi olarak sağlayın. Bu, ham tasarım aracı dışa aktarımı yerine somut, araç tarafından okunabilir bir spesifikasyon üretir.

**Bölüm 2 — Oluşturma**

AIDLC her adımı sırayla yürütür, tamamladıkça her adımı işaretler. Tüm adımlar tamamlandığında, oluşturulan dosyaların yollarıyla birlikte tamamlama mesajını sunar.

Onaylamadan önce oluşturulan kodu inceleyin. Bir şey doğru değilse:

```text
Değişiklik İste: [özellikle neyin değişmesi gerektiğini açıkla]
```

> **İleri düzey ipucu — Brownfield dosya değişiklikleri**: Mevcut kod tabanları için AIDLC dosyaları yerinde değiştirir. `ClassName_modified.java` veya `service_new.ts` gibi bir şeyi orijinalinin yanında görürseniz, hemen işaretleyin:
>
> ```text
> [ClassName_modified.java] dosyasını [ClassName.java] yanında görüyorum. Lütfen değişiklikleri
> orijinal dosyaya birleştirin ve kopyayı silin.
> ```

---

### Yapı ve Test

Tüm birimler tamamlandıktan sonra AIDLC, tüm birimler için yapı ve test talimatları oluşturur. Bilinmesi gereken birkaç kalıp:

**Doğru anda test aracını enjekte etme:**

Test çerçevesi veya test yönetim sistemi talimatlarını proje başlangıcında eklemeyin. Kod oluşturmaya gelindiğinde, bu ayrıntılar birçok ara aşama boyunca sıkıştırılmış veya kaybolmuş olabilir. Bunları tam zamanında enjekte edin:

```text
Fonksiyonel test oluşturma adımında, şu talimatı enjekte et:
[test yönetim sistemi] formatında fonksiyonel testler oluştur, bu belgede açıklanmıştır:
[ek belge]. Bu API uç noktasını kullanarak oluşturulan test vakalarını
[test yönetim sistemi] deposuna gönder: [uç nokta ayrıntıları].
```

Bu ilke, herhangi bir araç özel talimatı için geçerlidir: ihtiyaç duyulan aşamada enjekte edin, proje başlangıcında değil.

**Birim test kapsamını kapsamla:**

```text
Birim testleri oluştururken, üçüncü taraf harici bağımlılıkları kod kapsamı
hesaplamalarından hariç tut. Dahili kod yollarında minimum %80 kapsam iste.
```

---

### Kod Oluşturma Sonrası: Değişiklikleri Geri Yayma

Kod oluşturma sırasında yapılan değişiklikler — küçük tasarım kararları, kod yazılırken keşfedilen ayarlamalar — tasarım belgelerine geri akması gerekir. Bunu ad hoc olarak değil, kod parlatma tamamlandıktan sonra bilinçli bir süpürme olarak yapın:

```text
Kodu parlatmayı bitirdiğinde, her birimin son tasarım dosyalarını incele
ve değişiklikleri gereksinimlere ve kullanıcı hikayelerine geri yay.
Bunu adım adım nasıl yapacağına dair bir plan yap, sonra yürüt.
```

Yürütmeden önce plan istemek, süpürmenin seçici olmak yerine tüm birimlerde sistematik olmasını sağlar.

> **İleri düzey ipucu — Yeniden kullanılabilir spesifikasyonlar çıkarma**: Tamamlanmış bir projenin sonunda, kurduğunuz kalıpları gelecekteki projeler için yeniden kullanılabilir spesifikasyon belgelerine çıkarın:
>
> ```text
> Bu projedeki kalıpları ifade eden bir dizi yeniden kullanılabilir spesifikasyon belgesi oluştur:
> biri API tasarımı için, biri güvenlik için, biri UI spesifikasyonları için,
> biri teknoloji yığını için ve biri dizin yapısı için. Tamamlanmış birimleri kaynak olarak kullan.
> Gelecekteki projelerde kullanılmadan önce her belgeyi inceleyip onaylayacağım.
> ```

---

## 4. Asla Doğaçlama Kod Yazma

Doğaçlama kod yazma, hızlı düzeltmeler yapmak veya bir şeyler denemek için oluşturulan kod dosyalarını doğrudan düzenlemek — tasarım belgelerini tamamen atlayarak. Anlık olarak hızlı hissettirir ve kısa süre sonra sorun yaratır.

Sorun düzenlemenin kendisi değil. Tasarım belgeleri — AIDLC'nin her sonraki işlem için kullandığı tek doğru kaynak — artık kodun gerçekte ne yaptığını yansıtmıyor. Bir sonraki AIDLC çalıştırmasında, bir oturumu devam ettirdiğinizde veya bir meslektaşınız işi devraldığında, bu kopuklama kafa karışıklığı ve yeniden çalışmaya neden olur.

Bir ekip atölyeler sırasında bunu doğrudan şöyle ifade etti:

> "Kodu asla doğrudan düzeltmezsiniz. Bir sorun keşfettiyseniz, AIDLC'ye dönün ve şöyle deyin: X sorununu keşfettim. Tasarımı inceleyin ve düzeltmek için bir plan yapın. Bu tasarımı etkiliyorsa, önce güncelleyin, sonra kodu güncelleyin."

**Kural: önce tasarımı güncelle, sonra kodu oluştur.**

---

### Değişiklik Yapmanın Doğru Yolu

Bir hata fark etmiş olmanız, bir tasarım kararını değiştirmiş olmanız veya yeni gereksinimler almış olmanız fark etmeksizin, akış aynıdır:

**Adım 1 — Hiçbir şeye dokunmadan sorunu açıklayın:**

```text
Henüz hiçbir belgeyi güncelleme. [X] sorununu keşfettim.
Tasarımı incele ve bunun nerede ele alınması gerektiğini anlamama yardım et.
```

**Adım 2 — Tasarım belgesini düzeltin:**

```text
Lütfen [belirli tasarım belgesi] [düzeltmeyi] yansıtacak şekilde güncelle.
Sonra gereksinimler, kullanıcı hikayeleri gibi yukarı akış belgelerinin
de güncellenmesi gerekip gerekmediğini kontrol et.
```

**Adım 3 — Etkilenen kodu yeniden oluşturun:**

```text
[Birim adı] tasarımı güncellendi. Lütfen yalnızca etkilenen dosyalar için
kod oluşturmayı yeniden çalıştır.
```

Bu akış, doğrudan bir dosyayı düzenlemeye kıyasla birkaç dakika daha uzun sürer. Dokümantasyonunuzu senkronize tutar, denetim izinizi tamamlar ve ekibinizi gerçekte neyin inşa edildiği konusunda uyumlu tutar.

---

### "Sadece Dosyayı Düzenleyeyim" Demek İstediğinizde

**"Bu sadece tek satırlık bir düzeltme."**

Tasarımı atlayan tek satırlık düzeltmeler bile sapma yaratır. İlgili tasarım belgesinde düzeltmeyi not edin ve AIDLC'nin uygulamasına izin verin:

```text
[Birim X için functional-design.md] içinde, [yöntem veya kural] [düzeltme] olarak güncelle.
Sonra [etkilenen dosyayı] yeniden oluştur.
```

**"Sadece keşfediyoruz — henüz hiçbir şey kesin değil."**

Keşif, "Hiçbir belgeyi güncelleme"nin tam olarak ne için olduğudur. Sohbette özgürce keşfedin. Yalnızca hazır olduğunuzda taahhüt edin.

**"Şu anda ekibi açmam gerekiyor."**

Bazen hızlı hareket etmeniz gerekir. Doğrudan bir düzenleme yaparsanız, denetim izinin doğru kalması için dürüstçe kaydedin:

```text
Ekibi açmak için [dosya]ya geçici doğrudan düzenleme yaptık.
Düzeltme [açıklama]. Lütfen [tasarım belgesi] bunu yansıtacak şekilde güncelle
ve başka belgelerin tutarsız olup olmadığını doğrula.
```

---

### Sapmayı Erken Yakalayan Kalıcı Kurallar

Yapım aşamasının başında ayarlayabileceğiniz, sorunları her seferinde hatırlamanızı gerektirmeden erken yakalayan iki kalıcı talimat:

**Her güncellemede geri yayma:**

```text
Bir belgeyi her güncellediğinizde, değişikliğin gereksinimler belgesini ve
kullanıcı hikayelerini etkileyip etkilemediğini kontrol edin ve etkiliyorsa bana bildirin.
```

**Her kod kararında tasarım önceliği:**

```text
Kod oluşturma sırasında bir tasarım kararı verdiğinizde, her zaman dokümantasyonun
bu değişikliği yansıttığından emin olun, ilerlemeden önce.
```

Bunları Yapım'ın başında bir kez ayarlayın ve tüm aşama boyunca geçerlidirler.

---

### Raporları aidlc-docs Dışında Tutma

Pratik bir not: AIDLC'den insan odaklı raporlar üretmesini isterseniz — mimari diyagramlar, bileşen özetleri, paydaş sunumları — bunları `aidlc-docs/` içine kaydetmesine izin vermeyin. Bu dosyalar sonraki aşamalarda yapıtlar olarak yüklenecek, token sayısını şişirecek ve yapay zekayı yetkili tasarım girdisi konusunda kafası karışmış hale getirebilir.

Ayrı bir `reports/` klasörü kullanın ve daha temiz çıktı için raporları, özel bir rapor spesifikasyon dosyasıyla taze bir bağlamda oluşturun:

```text
Süreci durdur. Yeni bir bağlam başlat. [Rapor spesifikasyonu markdown dosyası] oku
ve AIDLC yapıtlarının mevcut durumuna dayalı olarak raporu üret.
Çıktıyı reports/ klasörüne kaydet, aidlc-docs/ değil.
```

---

*Girdi belgelerinizi hazırlama kılavuzları için [writing-inputs/inputs-quickstart.md](writing-inputs/inputs-quickstart.md)'ye bakın.*
