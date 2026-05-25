# AI-DLC İş Akışları Değerlendirme ve Raporlama Çerçevesi - SSS

## Bu nedir?

AI-DLC iş akışları deposundaki değişiklikleri doğrulayan kapsamlı bir test ve raporlama çerçevesidir. Kod kalitesini, anlamsal doğruluğu ve performansı otomatik olarak değerlendirerek değişikliklerin sistemi olumsuz etkilemediğinden emin olur.

## Bu kim için?

- **Bakımcılar** — değişikliklerin birleştirilmeye güvenli olduğundan emin olması gerekenler
- **Katkıda Bulunanlar** — değişikliklerinin sistemi geliştirdiğini (veya zarar vermediğini) göstermek isteyenler
- **Kullanıcılar** — tutarlı, yüksek kaliteli yapay zeka destekli geliştirme iş akışlarına güvenenler

## Ana yapı taşları nelerdir?

Çerçeve altı ana yapı taşı etrafında organize edilmiştir:

**1. Altın Test Vakası**

- Tam AIDLC dokümanları ve kod çıktısı içeren hazırlanmış temel test vakaları
- Tüm değerlendirmelerin karşısında çalıştığı sürümlü referans girdiler
- Değişiklikler arasında tutarlı, tekrarlanabilir değerlendirme sağlar

**2. Yürütme Çerçevesi (Jeff)**

- Altın test vakalarını her değerlendirme boyunca çalıştıran temel orkestrasyon motoru
- Test vakası girdisinden yapılandırılmış sonuç çıktısına kadar olan ardışıl düzeni yönetir
- Tüm değerlendirme boyutları arasında koordinasyon sağlar

**3. Anlamsal Değerlendirme**

- Önemli insan inceleme noktalarında çıktıları yapay zeka ile anlamsal olarak değerlendirir
- Çıktıları doğruluk, bütünlük ve uygunluk açısından puanlar
- Yapay zeka tarafından oluşturulan içeriğin kalite standartlarını karşıladığını doğrular
- Tüm anlamsal metrikler **@k** olarak raporlanır — her değerlendirme, yapay zeka tabanlı derecelendirmedeki belirsizliği hesaba katmak için birden fazla deneme çalıştırır (aşağıdaki "@k ne anlama gelir?" bölümüne bakın)

**4. Kod Değerlendirme**

- **Linting:** Kod stili doğruluğu
- **Güvenlik:** Güvenlik açıkları için Semgrep analizi
- **Organizasyon:** Kod kopyalama tespiti, kütüphane kullanım kalıpları
- Sayısal puanlar üretir (örn. "3 yüksek şiddetli güvenlik sorunu")

**5. NFR Değerlendirme**

- İş akışı başına token tüketimi
- Yürütme süresi ölçümleri
- Çapraz model tutarlılık kontrolleri
- Kaynak kullanım metrikleri

**6. GitHub CI/CD Entegrasyonu ve Yönetimi**

- PR'lerde değerlendirmeleri tetikleyen otomatik ardışıl düzenler
- İnsan tarafından okunabilir rapor oluşturma ve ekleme
- Geçmiş karşılaştırma için sürümlü rapor arşivleme

## Nasıl çalışır?

1. **Altın test vakaları** referans girdileri tanımlar (AIDLC dokümanları + beklenen kod çıktısı)
2. **Yürütme çerçevesi** bu test vakalarını her değerlendirme boyutundan geçirir
3. **Anlamsal, kod ve NFR değerlendirmeleri** yapılandırılmış sonuçlar üretir
4. **Raporlar** tüm boyutlarda etkiyi özetleyen raporlar oluşturur
5. **GitHub CI/CD** tüm ardışıl düzeni PR'lerde otomatikleştirir ve inceleme için raporlar ekler
6. Sürümlü raporlar geçmiş karşılaştırma için arşivlenir

## Hangi ortamlar destekleniyor?

Kiro test için birinci sınıf vatandaştır, ancak çerçeve müşterilerin bulunduğu yerde onlara ulaşmak için birden fazla yapay zeka aracı ve ortamı destekler.

## Anlamsal metrikler için @k ne anlama gelir?

Yapay zeka tabanlı değerlendirmeler belirleyici değildir — aynı girdi farklı çalıştırmalarda farklı puanlar üretebilir. Güvenilir sonuçlar elde etmek için çerçeve her anlamsal değerlendirmeyi birden fazla kez (*k* deneme) çalıştırır ve iki tamamlayıcı metrik raporlar (bkz. [Anthropic: Yapay Zeka Ajanları için Değerlendirmelerin Gizemini Çözmek](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)):

- **pass@k** — *k* denemede en az bir başarının olasılığı. Şunu yanıtlar: *"Bu iş akışı doğru bir sonuç üretebilir mi?"* Daha yüksek *k*, puanı artırır çünkü daha fazla deneme daha yüksek başarı olasılığı demektir.
- **pass^k** — *tüm k* denemenin başarılı olma olasılığı. Şunu yanıtlar: *"Bu iş akışı tutarlı olarak doğru sonuçlar üretiyor mu?"* Daha yüksek *k*, bunu başarmayı zorlaştırır çünkü her deneme geçmelidir.

*k*=1'de iki metrik özdeştir (her ikisi de deneme başına başarı oranına eşittir). *k* büyüdükçe birbirinden ayrılırlar — pass@k %100'e yaklaşırken pass^k 0'a doğru düşer. Birlikte, bir iş akışı değişikliğinin hem yetenek tavanını hem de güvenilirlik tabanını size söylerler.

Kod değerlendirme ve NFR metrikleri belirleyicidir ve @k gerektirmez.

## Raporları nasıl yorumlarım?

Raporlar şunları içerir:

- **Anlamsal puanlar @k:** pass@k (yetenek) ve pass^k (güvenilirlik) ile yapay zeka tarafından değerlendirilen derecelendirmeler
- **Kod puanları:** Linting, güvenlik, kopyalama için sayısal metrikler (belirleyici)
- **NFR metrikleri:** Token kullanımı, yürütme süresi, tutarlılık (belirleyici)
- **Trend analizi:** Önceki sürümlere karşı karşılaştırma (altın test vakalarına karşı)
- **Geçiş/başarısızlık geçitleri:** Değişikliklerin eşikleri karşılayıp karşılamadığına dair net göstergeler

## Değerlendirmem kötü çıkarsa ne olur?

Değerlendirmeler otomatik olarak birleştirmeleri engellemez — bağlam sağlarlar. Bakımcılarla birlikte şunları yapın:

- Değerlendirmenin faydalar göz önünde bulundurulduğunda kabul edilebilir olup olmadığını anlayın
- Değerlendirmeyi hafifletmenin yollarını belirleyin
- Bilinen ödünleri belgeleyin

## Bu AI-DLC iş akışları deposuyla nasıl ilişkilidir?

Bu çerçeve, [AI-DLC iş akışları](https://github.com/awslabs/aidlc-workflows)'nı kaliteyi korumaya veya geliştirmeye devam ettiğinden emin olmak için izler ve doğrular. İş akışlarının kendilerinin üzerinde bir test katmanıdır.

## PR göndermeden önce testleri yerel olarak çalıştırabilir miyim?

Evet — çerçeve CI/CD'de çalışacak şekilde tasarlanmıştır ancak erken geri bildirim almak için yerel olarak da yürütülebilir.

## Raporlar nasıl sürümlenir?

Her test çalıştırması şunları içeren numaralandırılmış/adlandırılmış bir sürüm üretir:

- Zaman damgası ve commit SHA
- Tam test sonuçları
- Temel çizgiye karşı karşılaştırma
- İnsan tarafından okunabilir özet

Raporlar geçmiş analizi ve trend takibi için saklanır.
