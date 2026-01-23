import React from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import styles from '../styles/LegalPage.module.css';

const KullanimKosullari: React.FC = () => {
  return (
    <>
      <Head>
        <title>Kullanım Koşulları | Tarım İmar</title>
        <meta name="description" content="Tarım İmar web sitesi kullanım koşulları ve şartları." />
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href="https://tarimimar.com.tr/kullanim-kosullari" />
      </Head>

      <Layout>
        <div className={styles.legalContainer}>
          <article className={styles.legalContent}>
            <h1>Kullanım Koşulları</h1>
            <p className={styles.lastUpdated}>Son Güncelleme: 29 Kasım 2025</p>

            <section>
              <h2>1. Genel Koşullar</h2>
              <p>
                Tarım İmar (<strong>tarimimar.com.tr</strong>) web sitesini ("Site") kullanarak, 
                bu kullanım koşullarını kabul etmiş sayılırsınız. Bu koşulları kabul etmiyorsanız, 
                lütfen siteyi kullanmayınız.
              </p>
            </section>

            <section>
              <h2>2. Hizmet Tanımı</h2>
              <p>
                Tarım İmar, tarımsal arazilerde yapılaşma süreçlerinde kullanılmak üzere 
                mevzuata uygun hesaplama araçları sunan bir web platformudur. Hizmetlerimiz şunları içerir:
              </p>
              <ul>
                <li>Tarımsal yapı alan hesaplamaları (bağ evi, sera, ahır vb.)</li>
                <li>Mevzuat bilgilendirmesi</li>
                <li>Harita tabanlı arazi analizi</li>
                <li>Hesaplama geçmişi kaydetme (üye kullanıcılar için)</li>
              </ul>
            </section>

            <section>
              <h2>3. Kullanıcı Yükümlülükleri</h2>
              <p>Site kullanıcıları olarak aşağıdaki kurallara uymayı kabul edersiniz:</p>
              <ul>
                <li>Gerçek ve doğru bilgiler sağlamak</li>
                <li>Hesap bilgilerinizi güvenli tutmak</li>
                <li>Siteyi yasalara aykırı amaçlarla kullanmamak</li>
                <li>Sitenin güvenliğini tehlikeye atacak eylemlerden kaçınmak</li>
                <li>Diğer kullanıcıların haklarına saygı göstermek</li>
              </ul>
            </section>

            <section>
              <h2>4. Hesaplama Sonuçları ve Sorumluluk Reddi</h2>
              <div className={styles.warning}>
                <strong>⚠️ Önemli Uyarı:</strong>
                <p>
                  Site üzerinden sunulan hesaplama sonuçları, yalnızca bilgilendirme amaçlıdır ve 
                  yasal geçerliliğe sahip resmi bir belge niteliği taşımaz.
                </p>
              </div>
              <ul>
                <li>
                  Hesaplama sonuçları, güncel mevzuata dayanmakla birlikte, resmi kurumların 
                  değerlendirmesinin yerini tutmaz.
                </li>
                <li>
                  Yapılaşma izinleri için yetkili kurumlardan (İl Tarım ve Orman Müdürlükleri, 
                  Belediyeler vb.) resmi başvuru yapılması gerekmektedir.
                </li>
                <li>
                  Hesaplama hatalarından, mevzuat değişikliklerinden veya veri güncellemelerinden 
                  kaynaklanan zararlardan Tarım İmar sorumlu tutulamaz.
                </li>
                <li>
                  Kullanıcılar, hesaplama sonuçlarını profesyonel danışmanlık yerine kullanmamalıdır.
                </li>
              </ul>
            </section>

            <section>
              <h2>5. Fikri Mülkiyet Hakları</h2>
              <p>
                Site üzerindeki tüm içerikler (metin, görsel, grafik, yazılım, logo vb.) 
                Tarım İmar'a veya lisans verenlere aittir ve 5846 sayılı Fikir ve Sanat 
                Eserleri Kanunu kapsamında korunmaktadır.
              </p>
              <ul>
                <li>İçeriklerin izinsiz kopyalanması, çoğaltılması veya dağıtılması yasaktır.</li>
                <li>Kişisel ve ticari olmayan amaçlarla alıntı yapılabilir.</li>
                <li>Hesaplama sonuçlarını kişisel kullanım için kaydedebilirsiniz.</li>
              </ul>
            </section>

            <section>
              <h2>6. Üyelik</h2>
              <h3>6.1 Hesap Oluşturma</h3>
              <p>
                Üye olmak için geçerli bir e-posta adresi ve güvenli bir şifre oluşturmanız gerekmektedir.
              </p>
              
              <h3>6.2 Hesap Güvenliği</h3>
              <p>
                Hesap bilgilerinizin güvenliğinden siz sorumlusunuz. Yetkisiz erişim fark ettiğinizde 
                derhal bize bildirmelisiniz.
              </p>
              
              <h3>6.3 Hesap Kapatma</h3>
              <p>
                Hesabınızı istediğiniz zaman kapatabilirsiniz. Hesabınızı kapatmanız durumunda 
                verileriniz gizlilik politikamızda belirtilen sürelerde saklanır ve sonra silinir.
              </p>
            </section>

            <section>
              <h2>7. Hizmet Değişiklikleri</h2>
              <p>
                Tarım İmar, herhangi bir zamanda ve önceden bildirimde bulunmaksızın:
              </p>
              <ul>
                <li>Hizmetlerini değiştirme, askıya alma veya sonlandırma hakkını saklı tutar.</li>
                <li>Yeni özellikler ekleyebilir veya mevcut özellikleri kaldırabilir.</li>
                <li>Ücretli hizmetler sunabilir.</li>
              </ul>
            </section>

            <section>
              <h2>8. Garanti Reddi</h2>
              <p>
                Site ve hizmetler "olduğu gibi" ve "mevcut olduğu şekilde" sunulmaktadır. 
                Tarım İmar, açık veya zımni hiçbir garanti vermez.
              </p>
              <ul>
                <li>Sitenin kesintisiz veya hatasız çalışacağını garanti etmiyoruz.</li>
                <li>Hesaplama sonuçlarının doğruluğunu garanti etmiyoruz.</li>
                <li>Güvenlik ihlallerinden korunacağınızı garanti etmiyoruz.</li>
              </ul>
            </section>

            <section>
              <h2>9. Sorumluluk Sınırlandırması</h2>
              <p>
                Tarım İmar, site kullanımından kaynaklanan doğrudan, dolaylı, arızi, özel veya 
                sonuç olarak ortaya çıkan zararlardan sorumlu tutulamaz. Bu sınırlama şunları kapsar:
              </p>
              <ul>
                <li>Veri kaybı</li>
                <li>Kar kaybı</li>
                <li>İş kesintisi</li>
                <li>Hatalı hesaplama sonuçlarından kaynaklanan zararlar</li>
              </ul>
            </section>

            <section>
              <h2>10. Bağlantılar</h2>
              <p>
                Site, üçüncü taraf web sitelerine bağlantılar içerebilir. Bu sitelerin içeriği, 
                gizlilik politikaları veya uygulamalarından Tarım İmar sorumlu değildir.
              </p>
            </section>

            <section>
              <h2>11. Koşul Değişiklikleri</h2>
              <p>
                Bu kullanım koşullarını istediğimiz zaman değiştirebiliriz. Önemli değişiklikler 
                sitede duyurulacaktır. Değişikliklerden sonra siteyi kullanmaya devam etmeniz, 
                yeni koşulları kabul ettiğiniz anlamına gelir.
              </p>
            </section>

            <section>
              <h2>12. Uygulanacak Hukuk ve Yetki</h2>
              <p>
                Bu kullanım koşulları Türkiye Cumhuriyeti kanunlarına tabidir. 
                Uyuşmazlıklarda Türkiye Cumhuriyeti mahkemeleri yetkilidir.
              </p>
            </section>

            <section>
              <h2>13. İletişim</h2>
              <p>
                Bu kullanım koşulları hakkında sorularınız için:
              </p>
              <ul>
                <li><strong>E-posta:</strong> info@tarimimar.com.tr</li>
                <li><strong>Web sitesi:</strong> https://tarimimar.com.tr</li>
              </ul>
            </section>
          </article>
        </div>
      </Layout>
    </>
  );
};

export default KullanimKosullari;
