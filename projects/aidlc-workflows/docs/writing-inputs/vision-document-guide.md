# Vizyon Belgesi Kılavuzu

## Amaç

Bir Vizyon Belgesi, AI-DLC iş akışına girmeden önce bir proje için **iş hedeflerini**, **hedeflenen sonuçları** ve **kapsam sınırlarını** tanımlar. Yapay zeka modeline ve ekibe projenin neyi başarmayı amaçladığı ve neden önemli olduğu konusunda paylaşılan bir anlayış sağlayan birincil girdi olarak hizmet eder.

İyi yazılmış bir Vizyon Belgesi, Gereksinimler Analizi sırasında belirsizliği azaltır, Kullanıcı Hikayesi kalitesini artırır ve Yapım sırasında kapsam sızmasını önler.

## Vizyon Belgesi Ne Zaman Yazılır

- Herhangi bir yeni proje veya büyük girişime başlamadan önce
- Yeni bir ürün, özellik seti veya platform önerildiğinde
- Mevcut bir ürün yeni bir yöne döndürüldüğünde
- Birden fazla paydaşın geliştirme başlamadan önce hedefler konusunda uyumlanması gerektiğinde

## Belge Yapısı

### 1. Yönetici Özeti

Projenin özünü yakalayan kısa bir paragraf (3-5 cümle). Yalnızca bu bölümü okuyan herkes, projenin ne olduğunu, kime hizmet ettiğini ve neden var olduğunu anlamalıdır.

**Şablon:**

```markdown
## Yönetici Özeti

[Proje Adı], [hedef kullanıcıların] [temel yeteneği] yapmasını sağlayan bir [sistem/ürün türü]dir.
[Benzersizlik veya yaklaşım] ile [iş sorunu veya fırsatı] ele alır.
Beklenen sonuç [ölçülebilir iş sonucu]dur.
```

**Örnek:**

```markdown
## Yönetici Özeti

OrderFlow, orta ölçekli perakendecilerin envanteri tek bir arayüzde
takip etmelerini, müşteri siparişlerini işlemelerini ve tedarikçi ilişkilerini yönetmelerini
sağlayan web tabanlı bir sipariş yönetim platformudur. Yerine getirme gecikmelerine ve envanter
uyumsuzluklarına neden olan parçalanmış araç sorununu ele alır. Beklenen sonuç,
sipariş işleme süresinde %30 azalma ve manuel envanter mutabakatının ortadan kaldırılmasıdır.
```

---

### 2. İş Bağlamı

İş ortamını, çözülen sorunu ve bunu şimdi çözmenin neden önemli olduğunu açıklayın.

**Dahil edilecek bölümler:**

```markdown
## İş Bağlamı

### Sorun Tanımı
[Bu proje hangi spesifik iş sorununu veya ağrı noktasını ele alıyor?
Somut olun. "Verimliliği artırın" gibi belirsiz ifadelerden kaçının.]

### İş Sürücüleri
[Bu proje neden şimdi yürütülüyor? Bunu zamanında yapan hangi piyasa koşulları,
rekabetçi baskılar, düzenleyici değişiklikler veya iç ihtiyaçlar var?]

### Hedef Kullanıcılar ve Paydaşlar
[Sistemi kim kullanacak? Başarısında çıkarı olan kimler?
Her birinin kısa bir açıklamasıyla birlikte kullanıcı tiplerini listeleyin.]

| Kullanıcı Tipi | Açıklama | Birincil İhtiyaç |
|-----------|-------------|--------------|
| [Rol]    | [Kim oldukları] | [Sistemden neye ihtiyaç duyuyorlar] |

### İş Kısıtlamaları
[Bütçe limitleri, düzenleyici gereksinimler, kurumsal politikalar, zaman çizelgesi
baskıları veya diğer pazarlık edilemez sınırlar.]

### Başarı Metrikleri
[İş, bu projenin başarılı olduğunu nasıl ölçecek?
Spesifik, ölçülebilir kriterler kullanın.]

| Metrik | Mevcut Durum | Hedef Durum | Ölçüm Yöntemi |
|--------|--------------|--------------|-------------------|
| [Metrik adı] | [Temel çizgi] | [Hedef] | [Nasıl ölçülür] |
```

---

### 3. Tam Kapsam Vizyonu

Bu bölüm, ürün veya sistem için **tam uzun vadeli vizyonu** açıklar. Bilerek heveslidir ve sadece ilk olarak ne inşa edileceğini değil, projenin olabileceği her şeyi kapsar.

**Dahil edilecek bölümler:**

```markdown
## Tam Kapsam Vizyonu

### Ürün Vizyonu Bildirimi
[Ürünün tam olarak gerçekleştiğindeki uzun vadeli hevesli durumunu yakalayan tek bir cümle
veya kısa paragraf. Bu ürün tamamen gerçekleştiğinde dünya nasıl görünür?]

### Özellik Alanları
[Tam özellik setini mantıksal gruplara düzenleyin. Her alan için, sistem tam olgunluğunda
ne yapacağını açıklayın.]

#### Özellik Alanı 1: [Ad]
- **Açıklama**: [Bu alanın kapsadığı şey]
- **Temel Yetenekler**:
  - [Yetenek 1]
  - [Yetenek 2]
  - [Yetenek 3]
- **Kullanıcı Değeri**: [Kullanıcılar için neden önemli]

#### Özellik Alanı 2: [Ad]
[Aynı yapı]

### Entegrasyon Noktaları
[Tam olgunluğunda sistem hangi harici sistemler, API'ler veya veri kaynaklarıyla
entegre olacak?]

- [Sistem/Servis] - [Entegrasyonun amacı]

### Kullanıcı Yolculukları (Tam Vizyon)
[Tam ürün deneyimini temsil eden 2-3 uçtan uca kullanıcı yolculuğu açıklayın.
Bunlar tam kapsamı yansıtmalıdır, MVP'yi değil.]

#### Yolculuk 1: [Ad]
1. [Adım]
2. [Adım]
3. [Adım]
**Sonuç**: [Kullanıcının başardığı şey]

### Ölçeklenebilirlik ve Büyüme
[Ürünün nasıl büyümesi bekleniyor? Yeni pazarlar, kullanıcı tipleri, coğrafyalar,
veri hacimleri veya özellik kategorileri?]

### Uzun Vadeli Yol Haritası (İsteğe Bağlı)
[Biliniyorsa, MVP ötesindeki üst düzey aşamaları veya kilometre taşlarını özetleyin.
Bu yönlendiricidir, taahhütlü değil.]

| Aşama | Odak | Zaman Çerçevesi (biliniyorsa) |
|-------|-------|---------------------|
| MVP | [Temel kapsam] | [Hedef] |
| Aşama 2 | [Genişleme alanı] | [Hedef] |
| Aşama 3 | [Daha fazla genişleme] | [Hedef] |
```

---

### 4. MVP Kapsamı

Bu bölüm, **minimum uygulanabilir ürünü** tanımlar: ölçülebilir değer sunan ve temel iş hipotezini doğrulayan en küçük işlevsellik seti. Burada listelenen her şey, ürün başlatılabilir veya değerlendirilebilir olmadan önce inşa edilmelidir.

**Dahil edilecek bölümler:**

```markdown
## MVP Kapsamı

### MVP Hedefi
[MVP'nin kanıtlaması veya sunması gereken en önemli tek şey nedir?
Bunu 1-2 cümleyle tutun.]

### MVP Başarı Kriterleri
[MVP'nin başarılı olduğunu nasıl bileceksiniz? Bunlar test edilebilir ve spesifik olmalıdır.]

- [ ] [Kriter 1]
- [ ] [Kriter 2]
- [ ] [Kriter 3]

### Kapsamda Olan Özellikler (MVP)
[MVP'ye dahil edilen her özelliği listeleyin. Açık olun. Burada listelenmemişse,
MVP'de değildir.]

| Özellik | Açıklama | Öncelik | Dahil Edilme Gerekçesi |
|---------|-------------|----------|------------------------|
| [Özellik adı] | [Kısa açıklama] | Zorunlu | [Neden ertelenemez] |

### Açıkça Kapsam Dışı Olan Özellikler (MVP)
[Tam Kapsam Vizyonundan kasıtlı olarak MVP'den hariç tutulan özellikleri listeleyin.
Her birinin neden ertelendiğini belirtin. Bu, kapsam sızmasını önler.]

| Özellik | Erteleme Nedeni | Hedef Aşama |
|---------|-------------------|--------------|
| [Özellik adı] | [Neden bekleyebilir] | [Aşama 2/3/Belirlenmedi] |

### MVP Kullanıcı Yolculukları
[MVP'nin desteklemesi gereken kullanıcı yolculuklarını açıklayın. Bunlar,
Tam Vizyon yolculuklarının alt kümeleri veya basitleştirilmiş versiyonlarıdır.]

#### Yolculuk 1: [Ad]
1. [Adım]
2. [Adım]
3. [Adım]
**Sonuç**: [Kullanıcının başardığı şey]
**Tam Vizyona Göre Sınırlama**: [Tam kapsama kıyasla ne basitleştirilmiş veya eksik]

### MVP Kısıtlamaları ve Varsayımlar
[MVP hangi varsayımlar üzerine inşa edilmiştir? Hangi bilinen sınırlamalar kabul edilmiştir?]

- **Varsayım**: [İfade] - **Yanlışsa risk**: [Sonuç]
- **Kabul Edilen Sınırlama**: [Kasıtlı olarak sınırlı olan ve neden]

### MVP Tamamlanma Tanımı
[MVP'nin tam ve değerlendirme veya lansman için hazır olarak kabul edilebilmesi için
ne doğru olmalıdır?]

- [ ] Tüm "Zorunlu" özellikler uygulandı ve test edildi
- [ ] [Bu projeye özgü ek kriterler]
- [ ] [Dağıtım veya erişilebilirlik gereksinimi]
- [ ] [Paydaş onay gereksinimi]
```

---

### 5. Riskler ve Bağımlılıklar

```markdown
## Riskler ve Bağımlılıklar

### Temel Riskler
| Risk | Olasılık | Etki | Azaltma |
|------|-----------|--------|------------|
| [Risk açıklaması] | Yüksek/Orta/Düşük | Yüksek/Orta/Düşük | [Azaltma stratejisi] |

### Harici Bağımlılıklar
[Ekip tarafından kontrol edilemeyen, projeye bağlı olan her şeyi listeleyin.]

- [Bağımlılık] - [Sahibi] - [Durumu]

### Açık Sorular
[Geliştirme öncesinde veya sırasında yanıtlanması gereken çözülmemiş soruları listeleyin.
Bunlar doğrudan Gereksinimler Analizi açıklayıcı sorularına girer.]

- [ ] [Soru]
- [ ] [Soru]
```

---

## Yazım Yönergeleri

### Yapılması Gerekenler

- Spesifik ve ölçülebilir olun. "Sipariş işleme süresini %30 azaltın", "işleri hızlandırın"dan daha iyidir.
- Tam vizyonu MVP'den açıkça ayırın. Bunları karıştırmak kapsam sızmasına neden olur.
- "Kapsam dışı" listeleri ekleyin. "Kapsamda" listeleri kadar değerlidirler.
- Ekibi için yazın, yöneticiler için değil. Pazarlama dilinden kaçının.
- Varsayımları açıkça belirtin ki meydan okunabilsinler.
- Gerçekten test edilebilir başarı kriterleri ekleyin.

### Yapılmaması Gerekenler

- Belirsiz dil kullanmayın: "dünya standartlarında", "kesintisiz", "sezgisel", "sınıfının en iyisi."
- Teknolojileri veya uygulama ayrıntılarını listeleyin. Bu, Teknik Ortam Belgesine aittir.
- MVP bölümünü atlamayın. Her proje tanımlanmış bir başlangıç sınırına ihtiyaç duyar.
- Özellikleri ve kullanıcı yolculuklarını birleştirmeyin. Özellikler sistem ne yapar; yolculuklar kullanıcılar bunu nasıl deneyimler.
- Okuyucuların iş bağlamını bildiğini varsaymayın. Açık olsa bile Sorun Tanımı yazın.

---

## Bu Belge AI-DLC'ye Nasıl Beslenir

| Vizyon Belgesi Bölümü  | AI-DLC Aşaması                     | Nasıl Kullanılır                                     |
| ------------------------ | -------------------------------- | -------------------------------------------------- |
| Yönetici Özeti        | Çalışma Alanı Algılama              | Proje sınıflandırması için başlangıç bağlamı         |
| İş Bağlamı         | Gereksinimler Analizi            | Açıklayıcı soruları ve gereksinim derinliğini yönlendirir |
| Tam Kapsam Vizyonu        | Kullanıcı Hikayeleri, Uygulama Tasarımı | Persona oluşturma, bileşen tanımlamaya bilgi verir |
| MVP Kapsamı                | İş Akışı Planlama                | Hangi aşamaların yürütüleceğini, kapsam sınırlarını belirler  |
| Kapsamda Olan/Hariç Olan Özellikler | Kod Oluşturma                  | Bu yinelemede neyin inşa edileceğini tanımlar          |
| Riskler ve Bağımlılıklar   | Tüm aşamalar                       | Risk değerlendirmesine ve hata yönetimine bilgi verir         |
| Açık Sorular           | Gereksinimler Analizi            | Soru dosyalarında açıklayıcı sorular haline gelir  |
