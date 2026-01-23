import React from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import styles from '../styles/LegalPage.module.css';

const CerezPolitikasi: React.FC = () => {
  return (
    <>
      <Head>
        <title>Çerez Politikası | Tarım İmar</title>
        <meta name="description" content="Tarım İmar çerez politikası. Web sitemizde kullanılan çerezler ve bunları nasıl yönetebileceğiniz hakkında bilgi." />
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href="https://tarimimar.com.tr/cerez-politikasi" />
      </Head>

      <Layout>
        <div className={styles.legalContainer}>
          <article className={styles.legalContent}>
            <h1>Çerez Politikası</h1>
            <p className={styles.lastUpdated}>Son Güncelleme: 29 Kasım 2025</p>

            <section>
              <h2>1. Çerez Nedir?</h2>
              <p>
                Çerezler (cookies), web sitelerinin tarayıcınıza yerleştirdiği küçük metin dosyalarıdır. 
                Bu dosyalar, web sitesinin sizi hatırlamasına, tercihlerinizi kaydetmesine ve size daha 
                iyi bir kullanıcı deneyimi sunmasına yardımcı olur.
              </p>
            </section>

            <section>
              <h2>2. Çerez Türleri</h2>
              
              <h3>2.1 Zorunlu Çerezler</h3>
              <p>
                Web sitesinin temel işlevlerini yerine getirmesi için gerekli olan çerezlerdir. 
                Bu çerezler olmadan site düzgün çalışmaz.
              </p>
              <table className={styles.cookieTable}>
                <thead>
                  <tr>
                    <th>Çerez Adı</th>
                    <th>Amacı</th>
                    <th>Süresi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>session_id</td>
                    <td>Oturum yönetimi</td>
                    <td>Oturum süresi</td>
                  </tr>
                  <tr>
                    <td>csrf_token</td>
                    <td>Güvenlik (CSRF koruması)</td>
                    <td>Oturum süresi</td>
                  </tr>
                  <tr>
                    <td>cookie_consent</td>
                    <td>Çerez tercihlerinizi hatırlama</td>
                    <td>1 yıl</td>
                  </tr>
                </tbody>
              </table>

              <h3>2.2 Performans Çerezleri</h3>
              <p>
                Web sitesinin nasıl kullanıldığını anlamamıza ve performansını iyileştirmemize 
                yardımcı olan çerezlerdir.
              </p>
              <table className={styles.cookieTable}>
                <thead>
                  <tr>
                    <th>Çerez Adı</th>
                    <th>Amacı</th>
                    <th>Süresi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>_ga</td>
                    <td>Google Analytics - Ziyaretçi istatistikleri</td>
                    <td>2 yıl</td>
                  </tr>
                  <tr>
                    <td>_ga_*</td>
                    <td>Google Analytics 4 - Oturum izleme</td>
                    <td>2 yıl</td>
                  </tr>
                  <tr>
                    <td>_gid</td>
                    <td>Google Analytics - Günlük ziyaretçi sayısı</td>
                    <td>24 saat</td>
                  </tr>
                </tbody>
              </table>

              <h3>2.3 İşlevsellik Çerezleri</h3>
              <p>
                Tercihlerinizi hatırlamamızı sağlayan ve kişiselleştirilmiş deneyim sunan çerezlerdir.
              </p>
              <table className={styles.cookieTable}>
                <thead>
                  <tr>
                    <th>Çerez Adı</th>
                    <th>Amacı</th>
                    <th>Süresi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>user_preferences</td>
                    <td>Kullanıcı tercihleri (tema, dil vb.)</td>
                    <td>1 yıl</td>
                  </tr>
                  <tr>
                    <td>recent_calculations</td>
                    <td>Son hesaplamaları hatırlama</td>
                    <td>30 gün</td>
                  </tr>
                </tbody>
              </table>
            </section>

            <section>
              <h2>3. Üçüncü Taraf Çerezleri</h2>
              <p>Web sitemizde aşağıdaki üçüncü taraf servislerin çerezleri kullanılmaktadır:</p>
              
              <h3>Google Analytics</h3>
              <p>
                Web sitesi trafiğini analiz etmek için Google Analytics kullanıyoruz. 
                Google Analytics, anonim istatistiksel veriler toplar ve kişisel olarak sizi tanımlayacak 
                bilgiler içermez.
              </p>
              <ul>
                <li><strong>Veri Saklama:</strong> 14 ay</li>
                <li><strong>IP Anonimleştirme:</strong> Aktif</li>
                <li>
                  <strong>Devre Dışı Bırakma:</strong>{' '}
                  <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer">
                    Google Analytics Opt-out Browser Add-on
                  </a>
                </li>
              </ul>
            </section>

            <section>
              <h2>4. Çerez Tercihlerini Yönetme</h2>
              <p>
                Çerez tercihlerinizi aşağıdaki yöntemlerle yönetebilirsiniz:
              </p>

              <h3>4.1 Çerez Banner'ı</h3>
              <p>
                Web sitemize ilk girişinizde gösterilen çerez banner'ı üzerinden tercihlerinizi belirleyebilirsiniz.
              </p>

              <h3>4.2 Tarayıcı Ayarları</h3>
              <p>Tarayıcınızın ayarlarından çerezleri kontrol edebilirsiniz:</p>
              <ul>
                <li>
                  <a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener noreferrer">
                    Google Chrome
                  </a>
                </li>
                <li>
                  <a href="https://support.mozilla.org/tr/kb/cerezleri-silme-web-sitelerinin-bilgisayariniza-yerlestirdigi-verileri-kaldirma" target="_blank" rel="noopener noreferrer">
                    Mozilla Firefox
                  </a>
                </li>
                <li>
                  <a href="https://support.apple.com/tr-tr/guide/safari/sfri11471/mac" target="_blank" rel="noopener noreferrer">
                    Safari
                  </a>
                </li>
                <li>
                  <a href="https://support.microsoft.com/tr-tr/microsoft-edge/microsoft-edge-de-%C3%A7erezleri-silme-63947406-40ac-c3b8-57b9-2a946a29ae09" target="_blank" rel="noopener noreferrer">
                    Microsoft Edge
                  </a>
                </li>
              </ul>

              <div className={styles.warning}>
                <strong>⚠️ Uyarı:</strong> Zorunlu çerezleri devre dışı bırakmanız, web sitesinin 
                düzgün çalışmasını engelleyebilir.
              </div>
            </section>

            <section>
              <h2>5. GDPR ve KVKK Uyumluluğu</h2>
              <p>
                Çerez kullanımımız, Avrupa Birliği Genel Veri Koruma Regülasyonu (GDPR) ve 
                6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) ile uyumludur.
              </p>
              <ul>
                <li>Zorunlu olmayan çerezler için önceden onay alınmaktadır</li>
                <li>Çerezler varsayılan olarak kapalıdır (opt-in yaklaşımı)</li>
                <li>Kullanıcılar tercihlerini her zaman değiştirebilir</li>
                <li>Çerez kullanımı hakkında şeffaf bilgilendirme yapılmaktadır</li>
              </ul>
            </section>

            <section>
              <h2>6. Politika Güncellemeleri</h2>
              <p>
                Bu Çerez Politikası'nı zaman zaman güncelleyebiliriz. Değişiklikler bu sayfada 
                yayınlanacak ve önemli değişiklikler için çerez banner'ı yeniden gösterilecektir.
              </p>
            </section>

            <section>
              <h2>7. İletişim</h2>
              <p>
                Çerez politikamız hakkında sorularınız için:
              </p>
              <ul>
                <li><strong>E-posta:</strong> info@tarimimar.com.tr</li>
              </ul>
            </section>
          </article>
        </div>
      </Layout>
    </>
  );
};

export default CerezPolitikasi;
