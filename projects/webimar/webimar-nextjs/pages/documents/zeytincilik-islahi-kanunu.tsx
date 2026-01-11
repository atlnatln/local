import Head from 'next/head';
import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function ZeytincilikIslahiKanumuPage() {
  return (
    <>
      <Seo
        title="Zeytinciliğin Islahı Kanunu - 3573 Sayılı Kanun"
        description="3573 sayılı Zeytinciliğin Islahı Kanunu - Zeytinlik alanlarında yapılaşma yasakları, hayvan otlatma kısıtlamaları ve sanayi tesisi kuralları"
        canonical="https://tarimimar.com.tr/documents/zeytincilik-islahi-kanunu/"
        url="https://tarimimar.com.tr/documents/zeytincilik-islahi-kanunu/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="zeytincilik kanunu, 3573 sayılı kanun, zeytinlik yapıları, hayvan otlatma yasağı, sanayi tesisi kısıtlamaları, zeytin ağacı koruma"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>🫒 Zeytinciliğin Islahı ve Yabanilerinin Aşılattırılması Hakkında Kanun</h1>
            <p>Resmî Gazete Tarihi: 07.02.1939 | Resmî Gazete Sayısı: 4126 | 3573 Sayılı Kanun</p>
          </div>

          <div className={styles.content}>
            <section className={styles.section}>
              <h2>🚫 Hayvan Otlatma Yasağı</h2>
              
              <div className={styles.subsection}>
                <div className={styles.warning}>
                  <ul>
                    <li><strong>Zeytinliklere her çeşit hayvan sokulması yasaktır</strong></li>
                    <li>Yerleşim sahaları hariç, <strong>zeytin sahalarına en az bir kilometre yakınlıkta koyun ve keçi ağılı yapılması yasaktır</strong></li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ İstisna Durumu</h3>
                <div className={styles.info}>
                  <p>Çift sürme ve nakliyatta kullanılan hayvanlara <strong>ağızlık takılması şartıyla müsaade edilir</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🏭 Sanayi Tesisi Kısıtlamaları</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Zeytinlik sahaları içinde ve bu sahalara en az 3 kilometre mesafede</strong> zeytinyağı fabrikası hariç zeytinliklerin vegatatif ve generatif gelişmesine mani olacak kimyevi atık bırakan, toz ve duman çıkaran tesis <strong>yapılamaz ve işletilemez</strong>.</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ İzin Gereken Tesisler</h3>
                <div className={styles.info}>
                  <p>Bu alanlarda yapılacak <strong>zeytinyağı fabrikaları</strong> ile <strong>küçük ölçekli tarımsal sanayi işletmeleri</strong> yapımı ve işletilmesi <strong>Tarım ve Köyişleri Bakanlığının iznine bağlıdır</strong>.</p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🏘️ Zeytinlik Sahalarının Korunması</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Zeytincilik sahaları daraltılamaz.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🏙️ Belediye Sınırları İçi İstisnası</h3>
                <div className={styles.warning}>
                  <p>Ancak, <strong>belediye sınırları içinde</strong> bulunan zeytinlik sahalarının imar hudutları kapsamı içine alınması hâlinde:</p>
                  <ul>
                    <li>Altyapı ve sosyal tesisler dahil <strong>toplam yapılaşma, zeytinlik alanının %10'unu geçemez</strong></li>
                    <li>Bu sahalardaki zeytin ağaçlarının sökülmesi <strong>Tarım ve Köyişleri Bakanlığının fenni gerekçeye dayalı iznine tabidir</strong></li>
                    <li>Bu iznin verilmesinde, Tarım ve Köyişleri Bakanlığına bağlı araştırma enstitülerinin ve mahallinde varsa ziraat odasının uygun görüşü alınır</li>
                    <li><strong>Kesin zaruret görülmeyen zeytin ağacı kesilemez ve sökülemez</strong></li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>📅 Mevcut İmar Planları</h3>
                <div className={styles.info}>
                  <p><strong>Bu Kanunun yayımından önce zeytinlik alanlarına ilişkin kesinleşmiş imar planları geçerlidir.</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>⚖️ Ceza Hükümleri</h2>
              
              <div className={styles.subsection}>
                <h3>🌳 Zeytin Ağaçlarının Korunması</h3>
                <div className={styles.warning}>
                  <p><strong>İzinsiz kesenler veya sökenlere ağaç başına altmış Türk Lirası idarî para cezası verilir.</strong></p>
                  <p>Bu Kanun hükümlerine göre idarî para cezasına karar vermeye <strong>mahallî mülkî amir yetkilidir</strong>.</p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📚 Hukuki Dayanak</h2>
              <div className={styles.subsection}>
                <p><em>Bu kanun, 26.1.1939 tarihinde Resmî Gazete'de yayımlanmış olup, 28.2.1995 tarih ve 4086 Sayılı Kanun ile güncellenmiştir.</em></p>
              </div>
            </section>

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
