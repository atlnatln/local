import Head from 'next/head';
import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function ZeytincilikIslahiYonetmeligiPage() {
  return (
    <>
      <Seo
        title="Zeytinciliğin Islahı Yönetmeliği - Zeytinlik Yapılaşma Kısıtlamaları"
        description="Zeytinciliğin Islahı Yabanilerinin AşılatTırılmasına Dair Yönetmelik - Zeytinlik alanlarında sanayi tesisi kurulması ve yapılaşma kısıtlamaları"
        canonical="https://tarimimar.com.tr/documents/zeytincilik-islahi-yonetmeligi/"
        url="https://tarimimar.com.tr/documents/zeytincilik-islahi-yonetmeligi/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="zeytincilik yönetmeliği, zeytinlik kısıtlamaları, sanayi tesisi yasağı, zeytin ağacı koruma, tarımsal işletme izinleri"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>🫒 Zeytinciliğin Islahı Yabanilerinin Aşılattırılmasına Dair Yönetmelik</h1>
            <p>Resmî Gazete Tarihi: 03.04.1996 | Resmî Gazete Sayısı: 22600</p>
          </div>

          <div className={styles.content}>
            <section className={styles.section}>
              <h2>📋 Tanımlar</h2>
              
              <div className={styles.subsection}>
                <h3>🏭 Küçük Ölçekli Tarımsal İşletme</h3>
                <div className={styles.info}>
                  <p>Üretim faktörlerini kullanarak, bitkisel ve/veya hayvansal ürünlerin üretimi için tarımsal faaliyet yapan ve işletme içerisinde tarımsal ürünlerin üretimden sonra koruma ve/veya işlemesini yaparak mamul veya yarı mamul hale getirmeye yönelik ekonomik faaliyette bulunan <strong>elli kişiden az yıllık çalışan istihdam eden işletmeler</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🚫 Sanayi Tesisi Kurulmasının Önlenmesi</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Zeytinlik sahaları içinde ve bu sahalara en az üç kilometre mesafede</strong> zeytin ağaçlarının bitkisel gelişimini ve çoğalmalarını engelleyecek kimyevi atık, toz ve duman çıkaran tesis <strong>yapılamaz ve işletilemez</strong>.</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ İstisna Durumları</h3>
                <div className={styles.info}>
                  <p>Bu alanlarda yapılacak <strong>zeytinyağı fabrikaları</strong> ile <strong>küçük ölçekli tarımsal işletmelerin</strong> yapımı ve işletilmesi <strong>Gıda, Tarım ve Hayvancılık Bakanlığı'nın iznine bağlıdır</strong>.</p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🏘️ Zeytinlik Alanlarının Daraltılmasının Önlenmesi</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Zeytinlik sahaları daraltılamaz.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🏙️ Belediye Sınırları İçi İstisnası</h3>
                <div className={styles.warning}>
                  <p>Ancak <strong>belediye sınırları içerisinde</strong> bulunan zeytinlik sahalarının imar hudutları içerisine alınması halinde:</p>
                  <ul>
                    <li>Alt yapı ve sosyal tesisler dahil <strong>toplam yapılaşma zeytinlik sahasının %10'unu geçemez</strong></li>
                    <li>Bu sahalardaki zeytin ağaçlarının sökülmesi, <strong>Bakanlığın fenni gerekçeye dayalı iznine tabidir</strong></li>
                    <li>Bu iznin verilmesinde Bakanlığa bağlı Müdürlüklerin, Enstitülerin ve varsa Ziraat Odalarının uygun görüşü alınır</li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>📅 Mevcut İmar Planları</h3>
                <div className={styles.info}>
                  <p><strong>28.2.1995 tarih ve 4086 sayılı Kanun'un yayımından önceki zeytinlik alanlar için kesinleşmiş imar planları geçerlidir.</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📚 Hukuki Dayanak</h2>
              <div className={styles.subsection}>
                <p><em>Bu yönetmelik, 26.1.1939 tarih ve 3573 Sayılı Zeytinciliğin Islahı ve Yabanilerinin Aşılattırılması Hakkındaki Kanun'a dayanarak çıkarılmıştır.</em></p>
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
