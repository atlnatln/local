# Teknik Ortam Belgesi Kılavuzu

## Amaç

Teknik Ortam Belgesi, bir projenin nasıl inşa edileceğini yöneten **teknik araçları, standartları, kısıtlamaları ve tercihleri** tanımlar. Vizyon Belgesi'nin teknik karşılığıdır ve AI-DLC'nin İnşa Aşaması sırasında bağlayıcı bir referans olarak hizmet eder.

Bu belge, kod üretimi, altyapı tasarımı ve NFR kararlarının kurumsal standartlar, güvenlik politikaları ve ekip yetkinlikleriyle uyumlu olmasını sağlar. Bu belge olmadan, AI-DLC aşamaları bu boşlukları doldurmak için kapsamlı açıklayıcı sorular sorar veya daha kötüsü, yeniden çalışma gerektiren varsayımlarda bulunur.

## Teknik Ortam Belgesi Ne Zaman Yazılır

- Herhangi bir yeni proje başlamadan önce (Greenfield)
- Teknik kısıtlamaların değiştiği mevcut bir projede değişiklik yapmadan önce (Brownfield)
- Kurumsal teknoloji standartları güncellendiğinde
- Bulut sağlayıcıları, framework'ler veya dağıtım modelleri arasında geçiş yapılırken

## Belge Uygulanabilirliği

Bir Teknik Ortam Belgesi iki proje bağlamından birini hedefleyebilir:

| Bağlam | Tanım | Temel Farklar |
| -------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Yeşil Sahada (Greenfield)** | Mevcut kod yok. Sıfırdan inşa ediliyor. | Tüm seçenekler açık. Belge başlangıç noktasını tanımlar. |
| **Mevcut Alanda (Brownfield)** | Mevcut kod tabanı var. Ekleme, değişiklik veya taşıma yapılıyor. | Seçenekler mevcut olanlarla kısıtlıdır. Belge neyin korunacağını, değiştirileceğini veya kaçınılacağını tanımlar. |

Belgenizi uygulanabilir bağlama göre yapılandırın. Aşağıdaki bölümler **(Greenfield)**, **(Brownfield)** veya **(Both)** olarak işaretlenmiştir.

---

## Belge Yapısı

### 1. Proje Teknik Özeti (Her İkisi — Both)

```markdown
## Proje Teknik Özeti

- **Proje Adı**: [Ad]
- **Proje Türü**: [Yeşil Sahada / Mevcut Alanda]
- **Birincil Çalışma Ortamı**: [Bulut / Yerinde / Hibrit]
- **Bulut Sağlayıcısı**: [AWS / Azure / GCP / Çoklu Bulut / Yok]
- **Hedef Dağıtım Modeli**: [Sunucusuz / Konteynerler / VM'ler / Hibrit]
- **Ekip Büyüklüğü**: [Geliştirici sayısı]
- **Ekip Deneyimi**: [Teknoloji seçimleriyle ilgili temel yetkinlikler ve deneyim seviyeleri]
```

---

### 2. Programlama Dilleri (Her İkisi — Both)

Projenin kullanması zorunlu olan, kullanabileceği ve kullanmaması gereken dilleri tanımlayın.

```markdown
## Programlama Dilleri

### Zorunlu Diller
[Belirli amaçlar için kullanılması zorunlu olan diller.]

| Dil | Sürüm | Amaç | Gerekçe |
|----------|---------|---------|-----------|
| TypeScript | 5.x | Backend servisleri, CDK altyapısı | Ekip uzmanlığı, tip güvenliği |
| Python | 3.12+ | Veri işleme, Lambda fonksiyonları | ML kütüphane ekosistemi |

### İzin Verilen Diller
[Gerekçesi varsa kullanılabilir ancak zorunlu olmayan diller.]

| Dil | Kullanım Koşulları |
|----------|-------------------|
| Go | Gecikmenin kritik olduğu yüksek işlem hacimli mikroservisler için onaylı |
| Rust | Sadece teknik lider onayıyla sistem seviyesi bileşenler için onaylı |

### Yasaklı Diller
[Kullanılmaması gereken diller ve gerekçeleri.]

| Dil | Neden |
|----------|--------|
| PHP | Ekip uzmanlığı yok, platform yönüyle uyumsuz |
| Ruby | Kurumsal standart yeni Ruby servislerini yasaklıyor |
```

**Brownfield eki:**

```markdown
### Mevcut Dil Envanteri
[Şu anda kod tabanında bulunan ve bakımı yapılması veya taşınması gereken diller.]

| Dil | Mevcut Kullanım | Yön |
|----------|--------------|-----------|
| Java 11 | Temel backend servisleri | Bakım (2. Aşama'da Java 21'e yükseltme) |
| JavaScript | Eski frontend | TypeScript'e taşıma |
```

---

### 3. Framework'ler ve Kütüphaneler (Her İkisi — Both)

```markdown
## Framework'ler ve Kütüphaneler

### Zorunlu Framework'ler
[İlgili alanlarında kullanılması zorunlu olan framework'ler.]

| Framework/Kütüphane | Sürüm | Alan | Gerekçe |
|-------------------|---------|--------|-----------|
| React | 18.x | Frontend UI | Kurumsal standart |
| Express | 4.x | API katmanı | Hafif, ekip aşinalığı |
| AWS CDK | 2.x | Altyapı Kodu olarak | AWS dağıtım hedefi |
| Jest | 29.x | Birim testi | Projeler arasında tutarlı test çalıştırıcısı |

### Tercih Edilen Kütüphaneler
[İhtiyaç duyulduğunda kullanılması gereken ancak ilgili yetkinlik zorunlu olmadığında mecburi olmayan kütüphaneler.]

| Kütüphane | Amaç | Ne Zaman Kullanılır |
|---------|---------|----------|
| Zod | Çalışma zamanı tip doğrulama | Harici veri alımı veya API girdisi durumlarında |
| Pino | Yapılandırılmış loglama | Log üreten tüm servislerde |
| Axios | HTTP istemcisi | Servislerden dışarıya HTTP çağrılarında |

### Yasaklı Kütüphaneler
[Kullanılmaması gereken kütüphaneler. Tercih edilen alternatifi de belirtin.]

| Kütüphane | Neden | Alternatif |
|---------|--------|-------------|
| Moment.js | Kullanımdan kaldırıldı, büyük paket boyutu | date-fns veya Luxon |
| Lodash (tam) | Paket boyutu | Native JS veya belirli import'lar için lodash-es |
| Request | Kullanımdan kaldırıldı | Axios veya native fetch |

### Kütüphane Onay Süreci
[Geliştirici zorunlu veya tercih edilen listelerde olmayan bir kütüphaneyi kullanmak için nasıl onay alır?]

- [Onay sürecini tanımlayın, örn. "Gerekçe, lisans kontrolü ve bakım durumu değerlendirmesiyle birlikte teknik inceleme talebini mimarlık ekibine sunun."]
```

---

### 4. Bulut Ortamı ve Servisleri (Her İkisi — Both)

```markdown
## Bulut Ortamı

### Bulut Sağlayıcısı
- **Birincil Sağlayıcı**: [AWS / Azure / GCP]
- **Hesap Yapısı**: [Tekil hesap / Çoklu hesap / Organizasyon]
- **Bölgeler**: [Birincil bölge(ler) ve felaket kurtarma bölge(ler)]

### Servis İzin Listesi
[Kullanımı onaylı olan servisler. Ek onay olmadan sadece bu listedeki servisler kullanılabilir.]

| Servis | Onaylı Kullanım Durumları | Kısıtlamalar |
|---------|-------------------|-------------|
| AWS Lambda | Olay güdümlü işlem, API işleyicileri | Maksimum 15 dk zaman aşımı, 10GB bellek |
| Amazon DynamoDB | Anahtar-değer ve belge depolama | Geliştirme için talep üzerine, prod için provisioned kapasite |
| Amazon S3 | Nesne depolama, statik varlıklar | Sürüm oluşturma ve şifreleme zorunlu |
| Amazon SQS | Asenkron mesaj kuyruklama | Standart kuyruklar tercih edilir; FIFO sadece sıralama gerektiğinde |
| Amazon CloudWatch | İzleme, loglama, alarmlar | Tüm servisler yapılandırılmış log üretmelidir |
| AWS Secrets Manager | Gizli bilgi depolama | Tüm kimlik bilgileri ve API anahtarları |
| Amazon API Gateway | REST ve HTTP API açığa çıkarma | Yeni servisler için HTTP API'ler REST üzerinden tercih edilir |
| Amazon ECR | Konteyner imaj kaydı | Tüm konteyner tabanlı servisler için zorunlu |
| AWS ECS Fargate | Konteyner işlem | EC2 tabanlı ECS üzerinden tercih edilir |
| Amazon RDS PostgreSQL | İlişkisel veri depolama | Değişken iş yükleri için Aurora Serverless v2 |

### Servis Yasak Listesi
[Kullanılmaması gereken servisler ve gerekçeleri ile onaylı alternatifler.]

| Servis | Neden | Alternatif |
|---------|--------|-------------|
| Amazon EC2 (doğrudan) | Yönetilen/sunucusuz işlem tercih edilir | Lambda veya ECS Fargate |
| Amazon ElastiCache | Mevcut ölçek için maliyet ve operasyonel yük | DynamoDB DAX veya uygulama düzeyinde önbellekleme |
| AWS Elastic Beanstalk | IaC iş akışına uymuyor | ECS veya Lambda ile CDK |
| Amazon Kinesis | Mevcut ihtiyaçları aşan karmaşıklık | SQS veya EventBridge |

### Servis Onay Süreci
[Geliştirici izin listesinde olmayan bir servisi kullanmak için nasıl onay alır?]

- [Süreci tanımlayın, örn. "İş gerekçesi, maliyet tahmini, güvenlik incelemesi ve operasyonel plan ile birlikte Bulut Servis Talebi sunun. Mimarlık ekibi onayı gereklidir."]
```

---

### 5. Tercih Edilen Teknolojiler ve Desenler (Her İkisi — Both)

```markdown
## Tercih Edilen Teknolojiler ve Desenler

### Mimari Desenler
| Desen | Ne Zaman Kullanılır | Ne Zaman Kullanılmaz |
|---------|-------------|-----------------|
| Önce sunucusuz (Serverless-first) | Tüm yeni servisler için varsayılan | Kalıcı bağlantı gerektiren veya >15 dk işlem yapan iş yükleri |
| Olay güdümlü (Event-driven) | Asenkron iş akışları, gevşek bağlı servisler | Aşağı akış etkisi olmayan basit CRUD |
| Mikroservisler | Bağımsız dağıtılabilir alanlar | Tek ekip sahipliği olan küçük projeler |
| Tek parça (modüler) | Tek ekip projeleri, erken aşama MVP'ler | Çok ekip veya bağımsız ölçeklenebilir alanlar |

### API Tasarım Standartları
- **Stil**: [REST / GraphQL / gRPC] - [Her birinin ne zaman kullanılacağı]
- **Sürüm Yönetimi**: [URL yolu sürümleme (v1/v2) / Header tabanlı]
- **Dokümantasyon**: [Tüm REST API'ler için OpenAPI 3.x spec zorunlu]
- **Adlandırma Kuralı**: [URL'ler için kebab-case, JSON alanları için camelCase]
- **Sayfalama**: [Cursor tabanlı tercih edilir, admin API'leri için offset tabanlı kabul edilebilir]
- **Hata Formatı**: [Standart hata yanıt yapısı]

### Veri Desenleri
- **Birincil Veri Deposu**: [Servis sahipliği verileri için DynamoDB]
- **İlişkisel Veri**: [İlişkisel sorgular gerekli olduğunda RDS PostgreSQL]
- **Önbellekleme Stratejisi**: [Önbellekleme yaklaşımını tanımlayın]
- **Veri Sahipliği**: [Her servis kendi verisine sahiptir; paylaşılan veritabanları yoktur]

### Mesajlaşma ve Olaylar
- **Senkron**: [İstek-yanıt için servisler arası HTTP/REST]
- **Asenkron**: [Görev kuyruklama için SQS, olay dağıtımı için EventBridge]
- **Olay Şeması**: [Olay şema standartlarını tanımlayın, örn. CloudEvents formatı]

### Frontend Desenleri (uygulanabilirse)
- **Bileşen Kütüphanesi**: [örn. Dahili tasarım sistemi, Material UI, Shadcn]
- **Durum Yönetimi**: [örn. Yerel için React Context, global için Zustand]
- **Yönlendirme**: [örn. React Router v6]
- **Build Aracı**: [örn. Vite]
```

---

### 6. Güvenlik Gereksinimleri (Her İkisi — Both)

```markdown
## Güvenlik Gereksinimleri

### Kimlik Doğrulama ve Yetkilendirme
- **Kimlik Doğrulama Yöntemi**: [örn. Amazon Cognito, OIDC, SAML]
- **Yetkilendirme Modeli**: [örn. RBAC, ABAC, özel politika motoru]
- **Token Formatı**: [örn. RS256 imzalama ile JWT]
- **Oturum Yönetimi**: [örn. Token süre sonu, refresh token rotasyonu]

### Veri Koruma
- **Bekleyen Şifreleme**: [Tüm veri depoları için zorunlu. KMS anahtar yönetimini belirtin.]
- **Aktarımda Şifreleme**: [Tüm iletişimler için TLS 1.2+ zorunlu]
- **PII İşleme**: [PII alanlarını tanımlayın, maskeleme gereksinimleri, saklama politikaları]
- **Veri Sınıflandırması**: [Halka Açık / İç / Gizli / Kısıtlı]

### Ağ Güvenliği
- **VPC Gereksinimleri**: [VPC içinde çalışması gereken servisler]
- **Güvenlik Grupları**: [En düşük ayrıcalık kuralları, 0.0.0.0/0 giriş yok]
- **WAF**: [Tüm halka açık uç noktalar için zorunlu]
- **Özel Uç Noktalar**: [Mevcut olduğunda AWS servis erişimi için VPC uç noktalarını kullanın]

### Gizli Bilgi Yönetimi
- **Gizli Bilgi Depolama**: [AWS Secrets Manager / Parameter Store]
- **Rotasyon Politikası**: [Otomatik rotasyon her N günde bir]
- **Erişim Politikası**: [Servis başına en düşük ayrıcalık IAM politikaları]
- **Yasaklı Uygulamalar**:
  - Kaynak kodda, derleme zamanı çevre değişkenlerinde veya yapılandırma dosyalarında gizli bilgi yok
  - Servisler arasında paylaşılan kimlik bilgileri yok
  - Uzun ömürlü erişim anahtarları yok

### Uyumluluk Gereksinimleri
- **Standartlar**: [SOC 2, HIPAA, PCI-DSS, GDPR, FedRAMP, veya "Belirli bir standart yok"]
- **Denetim Loglama**: [Tüm API çağrıları loglanır, CloudTrail etkin, log saklama süresi]
- **Güvenlik Açığı Taraması**: [Konteyner imaj taraması, bağımlılık taraması araçları]

### Bağımlılık Güvenliği
- **Bağımlılık Taraması**: [Araç ve sıklık, örn. Dependabot haftalık, Snyk PR'de]
- **Lisans Politikası**: [İzin verilen lisanslar: MIT, Apache 2.0, BSD. Yasaklı: GPL, AGPL]
- **Güncelleme Politikası**: [Kritik güvenlik açıkları N gün içinde yamanır]

### Güvenlik Uyumluluk Çerçevesi

Her proje bir güvenlik riski çerçevesi benimsemeli ve projenin her risk kategorisinde bu çerçeveyi nasıl ele aldığını dokümante etmelidir. Çerçeve seçimi projenin alanına, düzenleyici ortamına ve kurumsal standartlarına bağlıdır.

**Bir veya daha fazla çerçeve seçin ve kategori başına uyumluluğu dokümante edin:**

- **Seçilen çerçeve**: [Ad ve sürüm, örn. OWASP Top 10 (2021),
  NIST 800-53, CIS Controls v8, AWS Well-Architected Security Pillar,
  SANS Top 25, veya dahili kurumsal çerçeve]
- **Gerekçe**: [Bu çerçevenin neden seçildiği. Uygulanabilirse düzenleyici
  gereksinimlere, müşteri sözleşmelerine veya kurumsal politikaya atıfta bulunun.]

**Bağlama göre yaygın çerçeveler:**

| Bağlam | Yaygın Çerçeve Seçenekleri |
|---------|------------------------|
| Web uygulamaları ve API'ler | OWASP Top 10, OWASP API Security Top 10 |
| Bulut yerel altyapı | AWS/Azure/GCP Well-Architected Security Pillar, CIS Benchmarks |
| Devlet / düzenlenmiş | NIST 800-53, FedRAMP, ISO 27001 |
| Genel yazılım | CIS Controls v8, SANS Top 25 |
| Dahili / düşük risk | Kurumsal güvenlik kontrol listesi (burada dokümante edin) |

**Seçilen çerçevedeki her risk kategorisi için şunları dokümante edin:**

1. **Proje bunu nasıl ele alıyor** - Riski azaltan spesifik kontroller, desenler ve
   araçlar
2. **Uygulanamaz gerekçeleri** - Bir kategori uygulanmıyorsa,
   nedenini açıkça belirtin. Kategorileri boş bırakmayın.
3. **Ertelenen öğeler** - Bir kontrol daha sonraki bir aşamada planlanıyorsa,
   mevcut açığı ve düzeltilmesi hedeflenen aşamayı dokümante edin

**Ayrıntılı uyumluluk matrisinin nereye konulacağı:**

Küçük çerçeveler için (10 veya daha az kategori), tam matrisi
bu belgenin bu başlığı altına ekleyin.

Büyük çerçeveler için (NIST 800-53, ISO 27001), ayrı bir dosya oluşturun
ve burada referans verin:
- `security/[çerçeve-adı]-compliance.md`

Tam çalışan bir örnek için CalcEngine örneğine bakın; burada seçilen çerçeve olarak
OWASP Top 10 (2021) kullanılmıştır.
```

---

### 7. Test Gereksinimleri (Her İkisi — Both)

```markdown
## Test Gereksinimleri

### Test Stratejisi Genel Bakış
| Test Türü | Zorunlu | Kapsama Hedefi | Araçlar |
|-----------|----------|----------------|---------|
| Birim Testleri | Evet | Minimum %80 satır kapsaması | Jest / pytest |
| Entegrasyon Testleri | Evet | Tüm servis-servis etkileşimleri | Jest + Testcontainers / pytest |
| Uçtan Uca Testler | Koşullu | Kritik kullanıcı yolculukları | Playwright / Cypress |
| Kontrat Testleri | Koşullu | Tüm servisler arası API'ler | Pact |
| Performans Testleri | Koşullu | SLA hedefleri tanımlandığında | k6 / Artillery |
| Güvenlik Testleri | Evet | Tüm halka açık uç noktalar | OWASP ZAP / Snyk |

### Birim Test Standartları
- **Minimum Kapsama**: [%80 satır kapsaması, %70 dal kapsaması]
- **Mocklama Politikası**: [Harici bağımlılıkları mocklayın, dahili iş mantığını mocklamayın]
- **Adlandırma Kuralı**: [describe/it deseni, örn. "describe('OrderService') > it('should calculate total with tax')"]
- **Test Konumu**: [Kaynakla birlikte (örn. `__tests__/`) veya ayrı ağaç (örn. `tests/unit/`)]

### Entegrasyon Test Standartları
- **Kapsam**: [Gerçek servis etkileşimlerini, veritabanı sorgularını ve API kontratlarını test edin]
- **Ortam**: [Docker Compose / Testcontainers ile yerel konteynerler]
- **Veri Yönetimi**: [Test sabitleri, veritabanı tohumlaması ve temizlik yaklaşımı]

### Uçtan Uca Test Standartları
- **Kapsam**: [Sadece kritik kullanıcı yolculukları, kapsamlı UI testi değil]
- **Ortam**: [Dağıtılmış staging ortamı]
- **data-testid Gereksinimleri**: [Tüm etkileşimli öğelerde kararlı data-testid özellikleri zorunludur]

### Performans Test Standartları
- **Temel Gereksinimler**: [SLA hedeflerini tanımlayın: yanıt süresi, iş hacmi, hata oranı]
- **Test Senaryoları**: [Yük testi, stres testi, uzun süreli test]
- **Araçlar**: [k6 / Artillery / JMeter]

### CI/CD Test Kapıları
[Hat boyundaki her aşamada hangi testlerin geçmesi gerektiğini tanımlayın.]

| Hat Aşaması | Zorunlu Testler | Başarısızlık Eylemi |
|---------------|---------------|----------------|
| Pre-commit | Lintleme, tip kontrolü | Commit'i engelle |
| Pull Request | Birim testleri, entegrasyon testleri | Merge'i engelle |
| Pre-deploy (staging) | E2E testleri, kontrat testleri | Dağıtımı engelle |
| Post-deploy (production) | Duman testleri, sağlık kontrolleri | Otomatik geri alma |
```

---

### 8. Örnek ve Şablon Kod Rehberi (Her İkisi — Both)

Bu bölüm, AI-DLC ve geliştirme ekibine proje konvansiyonlarını oluşturan örnek veya şablon kodu nasıl sağlayacağını, kullanacağını ve bakımını yapacağını anlatır.

````markdown
## Örnek ve Şablon Kod Rehberi

### Örnek Kodun Amacı
Örnek kod, proje için **kanonik desenleri** belirler. AI-DLC kod ürettiğinde,
yeni desenler icat etmek yerine bu desenleri takip etmelidir.
Geliştiriciler kod yazarken tutarlılık için bu örneklere başvurur.

### Örnek Kodun Ne Zaman Sağlanacağı
Aşağıdakilerden herhangi biri için örnek veya şablon kod sağlayın:

- **Proje yapısı kurulumu** - Dizin düzeni, dosya adlandırma, modül organizasyonu
- **API uç noktası deseni** - Standart bir uç noktanın yoldan yanıta nasıl yapılandırıldığı
- **Veritabanı erişim deseni** - Sorguların, işlemlerin ve bağlantıların nasıl yönetildiği
- **Hata işleme deseni** - Standart hata türleri, hata yanıt formatı, loglama
- **Kimlik doğrulama/yetkilendirme entegrasyonu** - Auth'nin uç noktalara nasıl uygulandığı
- **Test deseni** - Standart bir birim testinin ve entegrasyon testinin nasıl yapılandırıldığı
- **Loglama deseni** - Yapılandırılmış log formatı, her seviyede ne loglanacak
- **Yapılandırma deseni** - Ortama özgü yapılandırmanın nasıl yüklendiği
- **Altyapı Kodu olarak deseni** - Standart bir CDK construct veya Terraform modülünün nasıl göründüğü

### Örnek Kodun Nasıl Yapılandırılacağı

#### Konum
Örnek kodu AI-DLC ve geliştiricilerin referans alabileceği özel bir dizinde saklayın:

```
project-root/
  examples/                        # Veya "templates/" tercih edilirse
    api-endpoint/
      handler.ts                   # Örnek API işleyici
      handler.test.ts              # İlgili test
      README.md                    # Deseni ve ne zaman kullanılacağını açıklar
    database-access/
      repository.ts                # Örnek repository deseni
      repository.test.ts
      README.md
    infrastructure/
      standard-lambda-stack.ts     # Örnek CDK stack
      README.md
```

#### Her Örneğin Yapısı
Her örnek şunları içermelidir:

1. **Çalışan kod** - Sözde kod değil. Derlenip/çalıştırılabilmelidir.
2. **İlgili test** - Deseni nasıl test edeceğini gösterir.
3. **README.md** - Şunları açıklar:
   - Bu hangi deseni gösteriyor
   - Ne zaman kullanılır
   - Ne zaman KULLANILMAZ
   - Ne özelleştirilecek, ne olduğu gibi kalacak
   - Bu Teknik Ortam Belgesi'nden ilgili standartlara referanslar

#### Örnek README Şablonu

```
# [Desen Adı] Örneği

## Ne Gösteriyor
[Deseni açıklayan bir paragraf.]

## Ne Zaman Kullanılır
- [Koşul 1]
- [Koşul 2]

## Ne Zaman Kullanılmaz
- [Koşul 1 - alternatif referansıyla birlikte]

## Dosya Envanteri
| Dosya            | Amaç                |
| --------------- | ---------------------- |
| handler.ts      | Örnek uygulama |
| handler.test.ts | Test deseni           |

## Özelleştirme Rehberi
| Öğe                  | Özelleştirilebilir mi?  | Notlar                            |
| ------------------------ | ----------- | -------------------------------- |
| Hata işleme yapısı | Hayır          | Proje standardını takip etmelidir     |
| İş mantığı           | Evet         | Gerçek alan mantığıyla değiştirin |
| Yol yolu               | Evet         | API adlandırma kurallarını takip edin    |
| Loglama çağrıları            | Hayır          | Yapılandırılmış log formatını koruyun   |

## İlgili Standartlar
- [API Tasarım Standartları bölümüne bağlantı]
- [Hata İşleme desenine bağlantı]
```

### AI-DLC Örnek Kodu Nasıl Kullanır

Kod Üretimi sırasında AI-DLC şunları yapmalıdır:

1. **Önce örnekleri okuyun** - Herhangi bir kod üretmeden önce, ilgili örnekleri
   examples/ dizininden okuyun
2. **Belirlenmiş desenleri takip edin** - Örneklerde gösterilen yapı, adlandırma, hata işleme
   ve test desenleriyle eşleşin
3. **Alternatifler icat etmeyin** - Bir desen için örnek varsa, onu kullanın.
   Örnek açıkça uygulanmıyorsa farklı bir yaklaşım oluşturmayın.
4. **Planlarda örneklere referans verin** - Kod Üretim Planları her adımda hangi
   örneklerin uygulandığına referans vermelidir

### Örnek Kodun Bakımı

- **Standartlar değiştiğinde örnekleri güncelleyin** - Örnekler bu
  Teknik Ortam Belgesi ile güncel kalmalıdır
- **Örnekleri onboarding sırasında inceleyin** - Yeni ekip üyeleri kod katkıda bulunmadan önce
  tüm örnekleri okumalıdır
- **Örnekleri proje ile sürümleyin** - Örnekler aynı depoda yaşar ve
  üretim koduyla aynı inceleme sürecinden geçer
- **Kullanımdan kaldırılan örnekleri işaretleyin** - Bir desen yerini alırsa, dizini
  "deprecated-" önekiyle yeniden adlandırın ve yerine bir not ekleyin
````

---

### 9. Mevcut Alana Özgü Bölümler (Brownfield)

Bu bölümleri sadece mevcut alan (brownfield) projeleri için ekleyin.

```markdown
## Mevcut Alanda: Mevcut Teknik Envanter

### Mevcut Durum Değerlendirmesi
[Mevcut teknik durumun özeti için Tersine Mühendislik ürünlerine referans verin veya
mevcut teknik durumun özetini sağlayın.]

- **Mevcut Diller**: [Sürümlerle birlikte liste]
- **Mevcut Framework'ler**: [Sürümlerle birlikte liste]
- **Mevcut Altyapı**: [Bulut servisleri, dağıtım modeli]
- **Mevcut Test Kapsaması**: [Yüzde veya nitel değerlendirme]
- **Bilinen Teknik Borç**: [Temel öğeler]

### Taşıma ve Modernizasyon Kuralları

#### Ne Korunacak
[Değişmeden kalması gereken teknolojiler ve desenler.]

| Teknoloji | Korunma Nedeni |
|-----------|---------------|
| [Tek] | [Gerekçe] |

#### Ne Taşınacak
[Değiştirilecek teknolojiler, hedef ve zaman çizelgesi.]

| Mevcut | Hedef | Öncelik | Yaklaşım |
|---------|--------|----------|----------|
| JavaScript | TypeScript | Yüksek | Artımlı dosya-dosya taşıma |
| REST API v1 | REST API v2 | Orta | Yeni uç noktalar v2 kullanır, mevcut olanlar 2. Aşama'da taşınır |

#### Ne Kaldırılacak
[Elimine edilmesi gereken teknolojiler, desenler veya bağımlılıklar.]

| Öğe | Neden | Kaldırma Zaman Çizelgesi |
|------|--------|-----------------|
| [Kullanımdan kaldırılan kütüphane] | [Güvenlik/bakım endişesi] | [Ne zaman] |

### Birlikte Yaşama Kuralları
[Eski ve yeni desenler birlikte var olmalıysa kuralları tanımlayın.]

- **Taşıma sırasında API sürüm yönetimi**: [v1 ve v2'nin nasıl birlikte var olacağı]
- **Veritabanı şema taşıması**: [Mevcut verinin yanında şema değişikliklerinin nasıl yönetileceği]
- **Özellik bayrakları**: [Geçiş sırasında yeni işlevselliğin nasıl kısıtlanacağı]
- **Bağımlılık çatışmaları**: [Çatışan kütüphane sürümlerinin nasıl yönetileceği]
```

---

## Bu Belge AI-DLC'ye Nasıl Beslenir

| Teknik Ortam Bölümü | AI-DLC Aşaması | Nasıl Kullanılır |
| ----------------------------------- | -------------------------------------- | -------------------------------------------------- |
| Proje Teknik Özeti | Çalışma Alanı Algılama | Proje sınıflandırması için bağlam |
| Programlama Dilleri | Kod Üretimi | Dil seçimi ve sürüm kısıtlamaları |
| Framework'ler ve Kütüphaneler | Kod Üretimi, NFR Tasarımı | Bağımlılık seçimi ve yasaklı kütüphane kontrolleri |
| Bulut Servisleri İzin/Yasak Listeleri | Altyapı Tasarımı | Servis seçimi sınırları |
| Tercih Edilen Desenler | Uygulama Tasarımı, İşlevsel Tasarım | Mimari ve tasarım deseni kararları |
| Güvenlik Gereksinimleri | NFR Gereksinimleri, NFR Tasarımı | Güvenlik deseni seçimi ve uyumluluk kontrolleri |
| Test Gereksinimleri | Kod Üretimi, Derleme ve Test | Test stratejisi, araçlar ve kapsama hedefleri |
| Örnek Kod | Kod Üretimi | Kod üretimi sırasında desen referansı |
| Mevcut Alan Envanteri | Tersine Mühendislik, İş Akışı Planlama | Taşıma kararları ve birlikte yaşama kuralları |
