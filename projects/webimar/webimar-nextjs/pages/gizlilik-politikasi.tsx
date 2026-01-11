import React from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import Footer from '../components/Footer';
import styles from '../styles/LegalPage.module.css';

const GizlilikPolitikasi: React.FC = () => {
  return (
    <>
      <Head>
        <title>Gizlilik Politikası | Tarım İmar</title>
        <meta name="description" content="Tarım İmar gizlilik politikası. Kişisel verilerinizin nasıl toplandığı, işlendiği ve korunduğu hakkında bilgi edinin." />
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href="https://tarimimar.com.tr/gizlilik-politikasi" />
      </Head>

      <Layout>
        <div className={styles.legalContainer}>
          <article className={styles.legalContent}>
            <h1>Gizlilik Politikası</h1>
            <p className={styles.lastUpdated}>Son Güncelleme: 29 Kasım 2025</p>

            <section>
              <h2>1. Giriş</h2>
              <p>
                Tarım İmar (<strong>tarimimar.com.tr</strong>) olarak, kullanıcılarımızın gizliliğine önem veriyoruz. 
                Bu Gizlilik Politikası, web sitemizi ziyaret ettiğinizde veya hizmetlerimizi kullandığınızda 
                kişisel verilerinizin nasıl toplandığını, işlendiğini, korunduğunu ve paylaşıldığını açıklamaktadır.
              </p>
              <p>
                Bu politika, Avrupa Birliği Genel Veri Koruma Regülasyonu (GDPR) ve 6698 sayılı Kişisel Verilerin 
                Korunması Kanunu (KVKK) kapsamında hazırlanmıştır.
              </p>
            </section>

            <section>
              <h2>2. Veri Sorumlusu</h2>
              <p>
                Kişisel verilerinizin işlenmesinden sorumlu veri sorumlusu:
              </p>
              <ul>
                <li><strong>Şirket:</strong> Tarım İmar</li>
                <li><strong>E-posta:</strong> info@tarimimar.com.tr</li>
                <li><strong>Web Sitesi:</strong> https://tarimimar.com.tr</li>
              </ul>
            </section>

            <section>
              <h2>3. Toplanan Kişisel Veriler</h2>
              <p>Web sitemizi kullanırken aşağıdaki kişisel verilerinizi toplayabiliriz:</p>
              
              <h3>3.1 Otomatik Olarak Toplanan Veriler</h3>
              <ul>
                <li>IP adresi</li>
                <li>Tarayıcı türü ve versiyonu</li>
                <li>İşletim sistemi</li>
                <li>Erişim tarihi ve saati</li>
                <li>Ziyaret edilen sayfalar</li>
                <li>Çerez verileri</li>
              </ul>

              <h3>3.2 Kullanıcı Tarafından Sağlanan Veriler</h3>
              <ul>
                <li>Ad ve soyad</li>
                <li>E-posta adresi</li>
                <li>Telefon numarası (opsiyonel)</li>
                <li>Hesaplama parametreleri (arazi bilgileri, yapı özellikleri vb.)</li>
                <li>İletişim formu aracılığıyla gönderilen mesajlar</li>
              </ul>

              <h3>3.3 Harita ve Konum Verileri</h3>
              <ul>
                <li>Tarımsal hesaplamalar için girilen arazi koordinatları</li>
                <li>İl/ilçe seçim bilgileri</li>
              </ul>
            </section>

            <section>
              <h2>4. Kişisel Verilerin İşlenme Amaçları</h2>
              <p>Kişisel verileriniz aşağıdaki amaçlarla işlenmektedir:</p>
              <ul>
                <li>Tarımsal yapılaşma hesaplamalarının gerçekleştirilmesi</li>
                <li>Kullanıcı hesabı oluşturma ve yönetimi</li>
                <li>Hesaplama geçmişinin saklanması</li>
                <li>Teknik destek ve iletişim hizmetlerinin sunulması</li>
                <li>Web sitesi performansının analizi ve iyileştirilmesi</li>
                <li>Yasal yükümlülüklerin yerine getirilmesi</li>
              </ul>
            </section>

            <section>
              <h2>5. Hukuki Dayanak</h2>
              <p>Kişisel verilerinizi aşağıdaki hukuki dayanaklara göre işliyoruz:</p>
              <ul>
                <li><strong>Sözleşmenin ifası:</strong> Hizmetlerimizi sunmak için gerekli veriler</li>
                <li><strong>Meşru menfaat:</strong> Web sitesi güvenliği ve performans analizi</li>
                <li><strong>Yasal yükümlülük:</strong> Mevzuatın gerektirdiği veri saklama</li>
                <li><strong>Açık rıza:</strong> Pazarlama iletişimi ve çerez kullanımı</li>
              </ul>
            </section>

            <section>
              <h2>6. Kişisel Verilerin Paylaşılması</h2>
              <p>Kişisel verileriniz aşağıdaki durumlarda üçüncü taraflarla paylaşılabilir:</p>
              <ul>
                <li><strong>Hizmet sağlayıcılar:</strong> Web barındırma, e-posta hizmetleri</li>
                <li><strong>Analitik araçları:</strong> Google Analytics (anonim veriler)</li>
                <li><strong>Yasal gereklilikler:</strong> Mahkeme kararı veya yasal zorunluluk halinde</li>
              </ul>
              <p>
                Kişisel verilerinizi hiçbir koşulda üçüncü taraf pazarlama şirketlerine satmıyor veya kiralamıyoruz.
              </p>
            </section>

            <section>
              <h2>7. Veri Güvenliği</h2>
              <p>Kişisel verilerinizin güvenliği için aşağıdaki önlemleri alıyoruz:</p>
              <ul>
                <li>SSL/TLS şifreleme ile veri iletimi</li>
                <li>Güvenli sunucu altyapısı</li>
                <li>Düzenli güvenlik güncellemeleri</li>
                <li>Erişim kontrolü ve yetkilendirme</li>
                <li>Veritabanı şifreleme</li>
              </ul>
            </section>

            <section>
              <h2>8. Veri Saklama Süresi</h2>
              <p>
                Kişisel verileriniz, işlenme amaçları için gerekli olan süre boyunca saklanır:
              </p>
              <ul>
                <li><strong>Kullanıcı hesap verileri:</strong> Hesap silinene kadar</li>
                <li><strong>Hesaplama geçmişi:</strong> 2 yıl</li>
                <li><strong>İletişim kayıtları:</strong> 1 yıl</li>
                <li><strong>Analitik veriler:</strong> 14 ay (Google Analytics)</li>
              </ul>
            </section>

            <section>
              <h2>9. Kullanıcı Hakları</h2>
              <p>KVKK ve GDPR kapsamında aşağıdaki haklara sahipsiniz:</p>
              <ul>
                <li>Kişisel verilerinize erişim hakkı</li>
                <li>Verilerin düzeltilmesini talep etme hakkı</li>
                <li>Verilerin silinmesini talep etme hakkı (unutulma hakkı)</li>
                <li>İşlemenin kısıtlanmasını talep etme hakkı</li>
                <li>Veri taşınabilirliği hakkı</li>
                <li>İtiraz hakkı</li>
                <li>Otomatik karar almaya tabi olmama hakkı</li>
              </ul>
              <p>
                Bu haklarınızı kullanmak için <a href="mailto:info@tarimimar.com.tr">info@tarimimar.com.tr</a> 
                adresine başvurabilirsiniz.
              </p>
            </section>

            <section>
              <h2>10. Çerezler</h2>
              <p>
                Web sitemizde çerez kullanımı hakkında detaylı bilgi için 
                <a href="/cerez-politikasi"> Çerez Politikası</a> sayfamızı ziyaret ediniz.
              </p>
            </section>

            <section>
              <h2>11. Politika Değişiklikleri</h2>
              <p>
                Bu Gizlilik Politikası'nı zaman zaman güncelleyebiliriz. Önemli değişiklikler 
                yapıldığında, web sitemizde bildirim yayınlayacağız. Politikayı düzenli olarak 
                gözden geçirmenizi öneririz.
              </p>
            </section>

            <section>
              <h2>12. İletişim</h2>
              <p>
                Gizlilik politikamız veya kişisel verilerinizin işlenmesi hakkında sorularınız için:
              </p>
              <ul>
                <li><strong>E-posta:</strong> info@tarimimar.com.tr</li>
              </ul>
            </section>
          </article>
        </div>
        <Footer />
      </Layout>
    </>
  );
};

export default GizlilikPolitikasi;
