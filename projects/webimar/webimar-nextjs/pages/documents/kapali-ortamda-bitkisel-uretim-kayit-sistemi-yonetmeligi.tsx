import React from 'react';
import Head from 'next/head';
import Layout from '../../components/Layout';

export default function KapaliOrtamdaBitkiselUretimKayitSistemiYonetmeligi() {
  return (
    <Layout>
      <Head>
        <title>Kapalı Ortamda Bitkisel Üretim Kayıt Sistemi (KOBÜKS) Yönetmeliği | Tarım İmar</title>
        <meta
          name="description"
          content="Kapalı ortamda bitkisel üretimin kayıt altına alınmasına ilişkin KOBÜKS Yönetmeliği (16.03.2024, Resmî Gazete 32491). Kayıt eşiği, süreç ve temel kavramlar."
        />
        <link
          rel="canonical"
          href="https://tarimimar.com.tr/documents/kapali-ortamda-bitkisel-uretim-kayit-sistemi-yonetmeligi/"
        />
      </Head>

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '4rem 2rem' }}>
        <div style={{ marginBottom: '2rem' }}>
          <a
            href="/sera"
            style={{
              color: '#667eea',
              textDecoration: 'none',
              fontSize: '0.95rem',
              fontWeight: '500',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'color 0.3s ease'
            }}
          >
            ← Sera Sayfasına Dön
          </a>
        </div>

        <h1
          style={{
            fontSize: '2.5rem',
            fontWeight: '800',
            marginBottom: '1.25rem',
            color: '#2d3748',
            textAlign: 'center'
          }}
        >
          Kapalı Ortamda Bitkisel Üretim Kayıt Sistemi (KOBÜKS)
          <br />
          Yönetmeliği
        </h1>

        <p style={{ textAlign: 'center', color: '#718096', marginBottom: '2rem' }}>
          Resmî Gazete: 16 Mart 2024 • Sayı: 32491
        </p>

        <div
          style={{
            background: '#fff',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
            border: '1px solid #e2e8f0'
          }}
        >
          <div style={{ lineHeight: '1.8', color: '#2d3748' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', marginBottom: '0.75rem' }}>Bu Yönetmelik neyi düzenler?</h2>
            <p style={{ marginBottom: '1.25rem' }}>
              KOBÜKS Yönetmeliği; ortam koşulları kısmen ya da tamamen kontrol edilebilir kapalı ortamlardaki bitkisel üretimin
              kayıt altına alınması için oluşturulan sistemin (KOBÜKS) kullanım, güncelleme, izleme ve raporlama esaslarını
              düzenler.
            </p>

            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', marginBottom: '0.75rem' }}>Sera için pratik anlamı</h2>
            <div style={{ background: '#f7fafc', padding: '1.25rem', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
              <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', margin: 0 }}>
                <li style={{ marginBottom: '0.75rem' }}>
                  Yönetmelikte, sisteme kayıt başvurusu için <strong>toplam üretim yüzey alanının en az 100 m²</strong> olması
                  eşiği yer alır.
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  Bu eşik, <strong>kayıt/güncelleme</strong> ve idari süreçler açısından önemlidir; sera kurulumu ve yapılaşma
                  koşulları ise ayrıca plan hükümleri, ilgili idare uygulaması ve diğer mevzuat başlıklarıyla birlikte
                  değerlendirilir.
                </li>
                <li>
                  Küçük parsellerde (ör. 150–200 m²) sera yapılabildiği uygulamalar bulunabilir; idari/teknik birimler gibi
                  talepler için ise yerel mevzuat ve idare değerlendirmesi belirleyicidir.
                </li>
              </ul>
            </div>

            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', marginTop: '2rem', marginBottom: '0.75rem' }}>
              Temel kavramlar
            </h2>
            <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', marginBottom: '1.25rem' }}>
              <li>
                <strong>Sera / kapalı üretim ünitesi:</strong> Işık, ısı, nem, hava akışı gibi koşulların kısmen/tamamen
                denetlendiği kapalı üretim ortamları.
              </li>
              <li>
                <strong>Ek ünite:</strong> İklimlendirme, paketleme, depolama, atık depolama gibi teknik/idari birimler.
              </li>
              <li>
                <strong>İl/ilçe birimleri:</strong> Başvuru kabulü, kontrol, tespit ve raporlama süreçlerinde yetkili.
              </li>
            </ul>

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <a
                href="https://www.resmigazete.gov.tr/eskiler/2024/03/20240316-1.htm"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-block',
                  padding: '0.75rem 1.5rem',
                  background: '#e2e8f0',
                  color: '#4a5568',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  fontSize: '0.9rem'
                }}
              >
                Resmî Gazete – Tam Metin ↗
              </a>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
