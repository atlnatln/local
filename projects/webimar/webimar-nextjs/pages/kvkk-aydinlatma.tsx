import React from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import Footer from '../components/Footer';
import styles from '../styles/LegalPage.module.css';

const KVKKAydinlatma: React.FC = () => {
  return (
    <>
      <Head>
        <title>KVKK Aydınlatma Metni | Tarım İmar</title>
        <meta name="description" content="6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında Tarım İmar aydınlatma metni." />
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href="https://tarimimar.com.tr/kvkk-aydinlatma" />
      </Head>

      <Layout>
        <div className={styles.legalContainer}>
          <article className={styles.legalContent}>
            <h1>KVKK Aydınlatma Metni</h1>
            <p className={styles.lastUpdated}>Son Güncelleme: 29 Kasım 2025</p>

            <section className={styles.highlight}>
              <p>
                Bu aydınlatma metni, 6698 sayılı Kişisel Verilerin Korunması Kanunu'nun 10. maddesi 
                ile Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında 
                Tebliğ kapsamında hazırlanmıştır.
              </p>
            </section>

            <section>
              <h2>1. Veri Sorumlusu</h2>
              <p>
                <strong>Tarım İmar</strong> olarak, 6698 sayılı Kişisel Verilerin Korunması Kanunu 
                ("KVKK") kapsamında veri sorumlusu sıfatıyla kişisel verilerinizi aşağıda açıklanan 
                amaçlar doğrultusunda ve KVKK'da öngörülen ilkelere uygun olarak işlemekteyiz.
              </p>
            </section>

            <section>
              <h2>2. İşlenen Kişisel Veriler</h2>
              
              <h3>2.1 Kimlik Bilgileri</h3>
              <ul>
                <li>Ad, Soyad</li>
                <li>E-posta adresi</li>
              </ul>

              <h3>2.2 İletişim Bilgileri</h3>
              <ul>
                <li>E-posta adresi</li>
                <li>Telefon numarası (isteğe bağlı)</li>
              </ul>

              <h3>2.3 İşlem Güvenliği Bilgileri</h3>
              <ul>
                <li>IP adresi</li>
                <li>Oturum bilgileri</li>
                <li>Giriş/çıkış zamanları</li>
              </ul>

              <h3>2.4 Hesaplama Verileri</h3>
              <ul>
                <li>Arazi koordinatları</li>
                <li>İl/İlçe bilgileri</li>
                <li>Yapı parametreleri</li>
                <li>Hesaplama sonuçları</li>
              </ul>
            </section>

            <section>
              <h2>3. Kişisel Verilerin İşlenme Amaçları</h2>
              <p>Kişisel verileriniz aşağıdaki amaçlarla işlenmektedir:</p>
              
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Veri Kategorisi</th>
                    <th>İşlenme Amacı</th>
                    <th>Hukuki Sebep</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Kimlik Bilgileri</td>
                    <td>Üyelik işlemlerinin gerçekleştirilmesi, kimlik doğrulama</td>
                    <td>Sözleşmenin kurulması ve ifası</td>
                  </tr>
                  <tr>
                    <td>İletişim Bilgileri</td>
                    <td>İletişim süreçlerinin yürütülmesi, destek hizmetleri</td>
                    <td>Sözleşmenin kurulması ve ifası</td>
                  </tr>
                  <tr>
                    <td>İşlem Güvenliği</td>
                    <td>Bilgi güvenliği süreçlerinin yürütülmesi</td>
                    <td>Veri sorumlusunun meşru menfaati</td>
                  </tr>
                  <tr>
                    <td>Hesaplama Verileri</td>
                    <td>Tarımsal yapı hesaplama hizmetinin sunulması</td>
                    <td>Sözleşmenin kurulması ve ifası</td>
                  </tr>
                </tbody>
              </table>
            </section>

            <section>
              <h2>4. Kişisel Verilerin Aktarımı</h2>
              <p>
                Kişisel verileriniz, KVKK'nın 8. ve 9. maddelerinde belirtilen şartlara uygun olarak, 
                aşağıdaki alıcı gruplarıyla paylaşılabilir:
              </p>
              <ul>
                <li><strong>İş ortakları:</strong> Web barındırma ve teknik altyapı hizmeti sağlayıcıları</li>
                <li><strong>Yetkili kamu kurum ve kuruluşları:</strong> Yasal yükümlülükler kapsamında</li>
              </ul>
              
              <h3>Yurt Dışına Aktarım</h3>
              <p>
                Web barındırma ve analiz hizmetleri kapsamında verileriniz yeterli korumaya sahip 
                ülkelere veya yeterli korumayı taahhüt eden veri işleyenlere aktarılabilir. 
                Aktarım yapılan ülkeler AB-ABD Veri Gizliliği Çerçevesi veya Standart Sözleşme 
                Maddeleri ile korunmaktadır.
              </p>
            </section>

            <section>
              <h2>5. Kişisel Veri Toplama Yöntemi</h2>
              <p>Kişisel verileriniz aşağıdaki yöntemlerle toplanmaktadır:</p>
              <ul>
                <li>Web sitesi üzerinden üyelik formu</li>
                <li>İletişim formu</li>
                <li>Hesaplama araçları</li>
                <li>Otomatik yöntemler (çerezler, log kayıtları)</li>
              </ul>
            </section>

            <section>
              <h2>6. İlgili Kişi Hakları</h2>
              <p>KVKK'nın 11. maddesi kapsamında aşağıdaki haklara sahipsiniz:</p>
              <ul>
                <li>Kişisel verilerinizin işlenip işlenmediğini öğrenme</li>
                <li>İşlenmişse buna ilişkin bilgi talep etme</li>
                <li>İşlenme amacını ve bunların amacına uygun kullanılıp kullanılmadığını öğrenme</li>
                <li>Yurt içinde veya yurt dışında aktarıldığı üçüncü kişileri bilme</li>
                <li>Eksik veya yanlış işlenmişse düzeltilmesini isteme</li>
                <li>KVKK'nın 7. maddesinde öngörülen şartlar çerçevesinde silinmesini/yok edilmesini isteme</li>
                <li>Düzeltme, silme veya yok etme işlemlerinin aktarıldığı üçüncü kişilere bildirilmesini isteme</li>
                <li>İşlenen verilerin münhasıran otomatik sistemler aracılığıyla analiz edilmesi suretiyle aleyhine bir sonucun ortaya çıkmasına itiraz etme</li>
                <li>Kanuna aykırı işleme nedeniyle zarara uğranması halinde zararın giderilmesini talep etme</li>
              </ul>
            </section>

            <section>
              <h2>7. Başvuru Hakkı</h2>
              <p>
                Yukarıda belirtilen haklarınızı kullanmak için aşağıdaki yöntemlerle başvurabilirsiniz:
              </p>
              <ul>
                <li><strong>E-posta:</strong> info@tarimimar.com.tr</li>
              </ul>
              <p>
                Başvurunuzda kimliğinizi tespit edici bilgiler ile KVKK'nın 11. maddesi kapsamındaki 
                talebiniz yer almalıdır. Başvurularınız en geç 30 (otuz) gün içinde 
                cevaplanacaktır.
              </p>
            </section>

            <section>
              <h2>8. Veri Güvenliği</h2>
              <p>
                Kişisel verilerinizin hukuka aykırı olarak işlenmesini ve erişilmesini önlemek 
                ile muhafazasını sağlamak amacıyla uygun güvenlik düzeyini temin etmeye yönelik 
                teknik ve idari tedbirler alınmaktadır.
              </p>
            </section>

            <section className={styles.highlight}>
              <h2>Önemli Bilgi</h2>
              <p>
                Bu aydınlatma metni, KVKK'nın 10. maddesi ile Aydınlatma Yükümlülüğünün 
                Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında Tebliğ'e uygun olarak 
                hazırlanmıştır. Metin, sadece bilgilendirme amacı taşımakta olup, onay niteliği 
                taşımamaktadır.
              </p>
            </section>
          </article>
        </div>
        <Footer />
      </Layout>
    </>
  );
};

export default KVKKAydinlatma;
