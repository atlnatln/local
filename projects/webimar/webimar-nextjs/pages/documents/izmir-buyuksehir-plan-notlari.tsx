import Head from 'next/head';
import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function IzmirBuyuksehirPlanNotlariPage() {
  return (
    <>
      <Seo
        title="İzmir Büyükşehir Plan Notları - Tarım Alanları Yapılaşma Koşulları"
        description="İzmir Büyükşehir Belediyesi plan notlarında tarım alanları yapılaşma koşulları, ifraz kuralları ve tarımsal amaçlı yapılar hakkında detaylı bilgi"
        canonical="https://tarimimar.com.tr/documents/izmir-buyuksehir-plan-notlari/"
        url="https://tarimimar.com.tr/documents/izmir-buyuksehir-plan-notlari/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="İzmir plan notları, İzmir Büyükşehir, tarım alanları, yapılaşma koşulları, ifraz kuralları, tarımsal amaçlı yapılar, İzmir imar, toprak koruma"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>🗺️ İzmir Büyükşehir Plan Notları</h1>
            <p>Tarım Alanları ve Yapılaşma Koşulları</p>
          </div>

          <div className={styles.content}>
            <section className={styles.section}>
              <h2>🌾 Tarım Alanları Genel Koşulları</h2>
              <div className={styles.subsection}>
                <p>İzmir Büyükşehir Belediyesi plan notları tarım alanları için özel düzenlemeler içermektedir.</p>
              </div>
            </section>

            {/* --- Yeni Eklenen Kapsamlı Plan Notları --- */}
            <section className={styles.section}>
              <h2>📑 7.12. Tarım Alanları</h2>

              <div className={styles.subsection}>
                <h3>7.12.1. Koruma ve Sürdürülebilirlik</h3>
                <p>Bu alanlarda tarım alanlarının korunması ve sürdürülebilirliğin sağlanması esastır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.2. Sınıflama</h3>
                <p>Bu planda yer alan tarım alanları tek gösterim altında toplanmış olup, 5403 sayılı kanun ve ilgili yönetmeliğinde tanımlanan tarım arazileri sınıflarına ayrılmamıştır. Tarım alanlarında yer alan taşınmazların sınıflaması, 5403 Sayılı “Toprak Koruma ve Arazi Kullanımı Kanunu” ve ilgili yönetmelik hükümleri uyarınca ilgili kurum ve kuruluşlarca yapılır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.3. İfraz Kuralları</h3>
                <p>Tarım alanlarında yapılacak ifrazlarda 5403 Sayılı Toprak Koruma ve Arazi Kullanımı Kanunu ve ilgili yönetmelik hükümleri uyarınca, 3083 sayılı Sulama Alanlarında Arazi Düzenlemesine Dair Tarım Reformu Kanununa tabi arazilerde yapılacak ifrazlarda 3083 sayılı Sulama Alanlarında Arazi Düzenlemesine Dair Tarım Reformu Kanununa ve ilgili yönetmelik hükümleri uyarınca işlem yapılacaktır. Ancak yapılacak ifrazlarda hiçbir şekilde 25 metreden dar parsel cephesi oluşturulamaz.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.4. Yapılaşma Koşulları</h3>
                <p>5403 sayılı Toprak Koruma ve Arazi Kullanım Kanunu ve ilgili yönetmelikleri uyarınca tarım arazi sınıfı belirlenen parsellerde; yapılaşma, bu planda belirlenen koşullara uygun olarak gerçekleştirilecektir.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.5. Yol ve Geçiş Yasağı</h3>
                <p>Parseden terk suretiyle yol oluşturulamaz, geçiş yolu izin belgesi ile inşaat izni verilemez.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.6. Uygulama Esasları</h3>
                <p>Bu alanlarda yapılacak uygulamalar, bu plan ile verilmiş olan yapılaşma koşullarını aşmamak ve tarımsal amaçlı yapılar için maksimum bina yüksekliği projeyi onaylayan idaresince ihtiyaç doğrultusunda belirlenmek kaydıyla, Plansız Alanlar İmar Yönetmeliği’nin 6. bölümünde belirtilen esaslara göre yapılır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.7. Zeytinlik Alanları</h3>
                <p>Zeytinlik alanları ve yakın çevresinde, “Zeytinciliğin Islahı ve Yabanilerin Aşılattırılması Hakkında Kanun” hükümlerine uyulacaktır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.8. Ekolojik (Organik) Tarım</h3>
                <p>Ekolojik (Organik) Tarım faaliyetleri 5262 sayılı “Organik Tarım Kanunu” ile “Organik Tarımın Esasları ve Uygulanmasına Dair Yönetmelik” koşullarına uygun olarak gerçekleştirilecektir.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.9. Örtü Altı Tarım (Seralar)</h3>
                <p>Bu alanlarda örtü altı tarım yapılması halinde, seralar İl Tarım ve Orman Müdürlüğü’nce onaylı projelere uygun olmak kaydıyla inşaat emsali’ne dahil değildir.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.10. Taşkın Alanlar ve Dere Yatakları</h3>
                <p>Taşkın alanları içerisinde bulunan ve/veya dere yataklarına cepheli taşınmazlarda yapılacak her türlü uygulama öncesinde D.S.İ. Bölge Müdürlüğü ve İZSU Genel Müdürlüğü görüşü alınacaktır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.11. Tarımsal Amaçlı Yapılar</h3>
                <p>Tarımsal Amaçlı Yapılar için İl Tarım ve Orman Müdürlüğü’nün uygun görüşünün alınması ve başka bir amaçla kullanılamayacağı konusunda mülk sahiplerince ilgili idareye noterlikçe onaylı taahhütte bulunulması gerekmektedir.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.12. Mevcut Haklar</h3>
                <p>Bu planın onayından önce yürürlükteki mevzuat uyarınca yapı ruhsatı veya yapı kullanma izni verilmiş olan tarımsal amaçlı yapılara ilişkin haklar saklıdır. Bu yapılarda, mevcut bina kitlesi içinde kalmak, brüt inşaat alanını arttırmamak ve yapının kullanım amacını değiştirmemek kaydıyla tadilat ve tamirat işlemleri yapılabilir.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.13. Marjinal Tarım Arazileri</h3>
                <p>5403 sayılı Toprak Koruma ve Arazi Kullanımı Kanunu’nun geçici 1. maddesi ve geçici 4. maddesi kapsamında tarım dışı amaçla kullanıma açılmış alanlarda ve Tarım ve Orman Bakanlığı veya İl Tarım ve Orman Müdürlüğü'nün söz konusu kanun kapsamında görüş veremediği alanlarda, marjinal tarım arazilerine ilişkin koşullar uygulanır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.14. İzmir Merkez Kent İmar Koşulları</h3>
                <p>5216 sayılı yasa öncesi Büyükşehir Belediyesi sınırları içerisindeki İzmir Merkez Kentte onaylı imar planındaki yapılaşma koşulları geçerlidir.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.15. Çiftçinin Barınması ve Tarımsal Yapılar</h3>
                <div className={styles.highlight}>
                  <h4>7.12.15.1. Çiftçinin Barınması Amaçlı Yapı</h4>
                  <p>Bu alanlarda parsel cephesi ve büyüklüğüne bakılmaksızın yollara 10 metre’den, komşu parsel sınırlarına 5 metre’den fazla yaklaşmamak koşuluyla, inşaat emsali:0,05’i, yüksekliği 2 katı, maksimum yapı inşaat alanı (brüt inşaat alanı) 3083 sayılı Sulama Alanlarında Arazi Düzenlenmesine Dair Tarım Reformu Kanununa tabi araziler, mutlak tarım arazileri ve özel ürün arazilerinde 75 m2'yi, dikili tarım arazilerinde 100 m2’yi, marjinal tarım arazilerinde 150 m2’yi aşmayan çiftçinin barınması amaçlı tek yapı ve müştemilatları yapılabilir. Müştemilat binaları belirlenmiş olan inşaat alanına dahildir.</p>
                  <h4>7.12.15.2. Tarımsal Amaçlı Yapılar</h4>
                  <ul>
                    <li>
                      <strong>Mutlak Tarım Arazisi, Dikili Tarım Arazisi ve Özel Ürün Arazilerinde:</strong> Minimum parsel cephesi 10 metre ve minimum parsel büyüklüğü 5000 m2 ölçülerini sağlamak koşuluyla 4.11.5 maddesinde tanımlanan tarımsal amaçlı yapılar, yollara 10 metre’den, komşu parsel sınırlarına 5 metre’den fazla yaklaşmamak, inşaat emsali 0.05’i, yüksekliği 2 katı aşmamak şartı ile yapılabilir. Bu yapılar için maksimum yapı inşaat alanı (brüt inşaat alanı) 2000 m2’den fazla olamaz.
                    </li>
                    <li>
                      <strong>Marjinal Tarım Arazileri:</strong> Minimum parsel cephesi 10 metre ve minimum parsel büyüklüğü 5000 m2 ölçülerini sağlamak koşuluyla 4.11.5 maddesinde tanımlanan tarımsal amaçlı yapılar, yollara 10 metre‘den, komşu parsel sınırlarına 5 metre‘den fazla yaklaşmamak, parsellerin 5000 m2.lik kısmı için inşaat emsali 0,20'yi, geri kalan parsel alanı için inşaat emsali 0.10’u, yüksekliği 2 katı aşmamak şartı ile yapılabilir. Bu yapılar için maksimum yapı inşaat alanı (brüt inşaat alanı) 10000 m2’den fazla olamaz.
                    </li>
                  </ul>
                  <h4>7.12.15.3. Örtü Altı Tarım (Seralar)</h4>
                  <p>Her tür tarım alanında, örtü altı tarım yapılmak istenmesi durumunda, seralar yukarıda belirtilen yapılaşma emsallerine dahil değildir. Parselde yapılmak istenecek diğer yapılarda ise ilgisine göre yukarıda sayılan koşullar geçerlidir. Seralar karayolundan en az 25 metre, diğer yollardan en az 10 metre, komşu parsellerden ise en az 5 metre çekerek yapılabilir. Örtü altı tarım yapılan parsellerde, sera zemininde ve çevresinde betonlama yapılamaz.</p>
                  <h5>7.12.15.3.1. Teknolojik Seralar</h5>
                  <p>Zeminde betonlama yapılarak kurulacak teknolojik seralarda tarımsal amaçlı tesisler için geçerli yapılaşma koşullarına uyulacaktır.</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.16. Tabii Zemin Kotlandırma</h3>
                <p>Bu alanlarda yapılacak yapı ve tesislerin tabii zeminden kotlandırılması esastır.</p>
              </div>

              <div className={styles.subsection}>
                <h3>7.12.17. Hafriyat Yasağı</h3>
                <p>Bu alanlarda hiçbir suretle arazinin doğal yapısını bozacak şekilde hafriyat yapılamaz.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📑 7.13. Bölgesel Tarım/Hayvancılık İhtisas Alanları</h2>
              <div className={styles.subsection}>
                <p>Bu alanlarda, parsel ölçeğinde uygulama yapılamaz. Maksimum inşaat emsali 0.40 olmak üzere, diğer yapılaşma koşulları ilgili idaresince alan bütününe ilişkin yapılacak olan 1/5000 ölçekli nazım ve 1/1000 ölçekli uygulama imar planlarında belirlenecektir. İmar planları onanmadan uygulamaya geçilemez. Onaylanan planlar sayısal ortamda veri tabanına işlenmek üzere İl Özel İdaresine ve Çevre Ve Şehircilik Bakanlığı'na gönderilir. Bu alanların Tarıma Dayalı İhtisas OSB Uygulama Yönetmeliği çerçevesinde yer seçimine konu yapılması halinde, bu planda değişiklik yapılmasına gerek olmaksızın, alt ölçekli planları yapılmak suretiyle Tarıma Dayalı İhtisas OSB olarak kullanılabilir.</p>
                <p>Alan bütününde alt ölçekli İmar Planları yapılıncaya kadar, alan bütünlüğünü bozmayacak konumda yer seçmesi kaydıyla, yenilenebilir enerji kaynaklarına (güneş, biyogaz) dayalı enerji üretim tesis alanlarına ilişkin, ilgili kurum ve kuruluş görüşleri doğrultusunda, bu planda değişiklik yapılmasına gerek olmaksızın, alt ölçekli İmar Planları yapılabilir.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📑 7.14. Organize Çiçekçilik Bölgesi</h2>
              <div className={styles.subsection}>
                <p>Bölgedeki seracılık, çiçek ve fidan yetiştiriciliği alanlarındaki gelişme potansiyellerinin değerlendirilmesi amacı ile Bayındır ilçesi ve Canlı Yerleşimi arasında kalan karayolunun kuzeyindeki alandır. Belirlenen alanda ürün değerlendirme tesisleri başlığı altında soğuk hava depoları, paketleme ve ambalaj tesisleri, yönetim merkezi, borsa gibi işlevler öngörülmüştür. Bu işlevlerin yerleşeceği alanlar ve yapılanma koşulları alt ölçekli planlarda tanımlanacak olup büyüklüğü toplam bölge alanının %20 sini geçemez. Seralar için sınır yoktur.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📑 7.15. Mera Alanları</h2>
              <div className={styles.subsection}>
                <p>Bu planda Mera olarak tanımlanan alanların, doğal karakteri korunacak alanlar olarak bütünlüklü korunması esastır. Alanların kullanımında “Mera Kanunu” ve “Mera Yönetmeliği”ne göre uygulama yapılacaktır. 7.15.1 maddesinde tanımlanan bölümler dışında, planda mera olarak tanımlanmış, devletin hüküm ve tasarrufu altında bulunan alanlar ifraz edilemez, bu alanlarda yapı yapılamaz.</p>
              </div>
              <div className={styles.subsection}>
                <h3>7.15.1. Özel Mülkiyet Arazileri</h3>
                <p>Planda “Mera Alanı” olarak gösterilmiş olan bölgelerde yer alan, üzerinde mera nitelikli bitki örtüsü bulunmayan ve tarımsal amaçlarla kullanılmakta olan özel mülkiyetteki arazilerde, 7.12 maddesindeki hükümler geçerlidir. Parselden terk sureti ile yol oluşturulamaz. Geçiş yolu izin belgesi ile inşaat izni verilemez.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📑 7.16. Makilik ve Fundalık Alanlar</h2>
              <div className={styles.subsection}>
                <p>Bu alanlar sahip oldukları flora ve fauna özellikleri ile topografik özellikleri nedeniyle bütüncül olarak doğal karakterinin korunması öngörülen alanlardır. Doğal karakterini yansıtan arazi kullanımının (makilik, fundalık, çalılık) sürdürülmesi hedeflenen bu alanlarda, alan içinde bozulmaya neden olacak müdahalelerde bulunulamaz, yapı yapılamaz. Ağaçlandırma amaçlı kiraya verilemez.</p>
              </div>
              <div className={styles.subsection}>
                <h3>7.16.1. Özel Mülkiyet Arazileri</h3>
                <p>Planda “makilik ve fundalık alan” olarak gösterilmiş olan bölgelerde yer alan, üzerinde maki bitki örtüsü bulunmayan ve tarımsal amaçlarla kullanılmakta olan özel mülkiyetteki arazilerde, 7.12 maddesindeki hükümler geçerlidir. Parselden terk sureti ile yol oluşturulamaz. Geçiş yolu izin belgesi ile inşaat izni verilemez.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📑 7.17. Sazlık ve Bataklık Alanlar</h2>
              <div className={styles.subsection}>
                <p>Sulak alan niteliğinde olan bu alanların doğal karakterlerinin korunması esastır. Bu alanlarda kirlenme ve bozulmaya yol açacak müdahalelerde bulunulamaz. Özel mülkiyete konu olan kısımlarında hiçbir tesise izin verilmez, balıkçılığı destekleyici faaliyetler dışında mevcut doğal yapı korunacaktır.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📑 7.18. Doğal ve Ağaçlık Karakteri Korunacak Alanlar</h2>
              <div className={styles.subsection}>
                <p>Bu alanlar, orman sayılan yerler dışında kalan, ağaçlık dokuya sahip olan alanlar ile doğal yapısı, bitki örtüsü vb. özellikleri ile korunması gereken diğer alanlardır. Mevcut ağaç dokusunun korunması koşuluyla bu alanlarda ağaçlandırma yapılabilir. Bu alanlarda 7.12 maddesi hükümleri geçerlidir.</p>
              </div>
            </section>
            {/* --- Yeni Eklenen Plan Notları Sonu --- */}

          {/* Ana sayfaya dönüş butonu */}
          <div style={{ textAlign: 'center', marginTop: 48 }}>
            <a href="/" style={{
              display: 'inline-block',
              background: 'linear-gradient(90deg, #d2691e, #8b4513)',
              color: '#fff',
              padding: '0.75rem 2.5rem',
              borderRadius: 8,
              fontWeight: 700,
              fontSize: '1.1rem',
              textDecoration: 'none',
              boxShadow: '0 2px 8px rgba(139,69,19,0.08)',
              transition: 'background 0.2s',
            }}
              onMouseOver={e => (e.currentTarget.style.background = 'linear-gradient(90deg, #8b4513, #d2691e)')}
              onMouseOut={e => (e.currentTarget.style.background = 'linear-gradient(90deg, #d2691e, #8b4513)')}
            >
              Ana Sayfaya Dön
            </a>
          </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
