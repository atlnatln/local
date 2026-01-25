import React from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import Seo from '../components/Seo';
import ContactForm from '../components/ContactForm';
import styles from '../styles/LegalPage.module.css';

export default function ContactPage() {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'ContactPage',
    name: 'İletişim - Tarım İmar',
    description: 'Tarım İmar ile iletişime geçin. E-posta ve iletişim formu üzerinden bize ulaşabilirsiniz.',
    mainEntity: {
      '@type': 'Organization',
      name: 'Tarım İmar',
      url: 'https://tarimimar.com.tr',
      email: 'info@tarimimar.com.tr',
      contactPoint: {
        '@type': 'ContactPoint',
        contactType: 'customer support',
        email: 'info@tarimimar.com.tr',
        availableLanguage: ['Turkish']
      }
    }
  };

  return (
    <Layout>
      <Seo
        title="İletişim - Tarım İmar"
        description="Sorularınız, önerileriniz ve destek için bizimle iletişime geçin. info@tarimimar.com.tr adresine e-posta gönderebilir veya iletişim formunu kullanabilirsiniz."
        keywords="iletişim, e-posta, destek, tarım imar, tarımsal yapı hesaplama iletişim, tarım imar e-posta"
        canonical="https://tarimimar.com.tr/iletisim"
        structuredData={structuredData}
      />
      
      {/* İletişim Bilgileri Bölümü */}
      <div className={styles.legalContainer} style={{ paddingBottom: '0' }}>
        <div className={styles.legalContent} style={{ textAlign: 'center' }}>
          <h1>İletişim</h1>
          <p style={{ fontSize: '1.2rem', color: '#4b5563', margin: '20px auto', maxWidth: '700px' }}>
            Projeleriniz, hesaplamalarınız veya platformumuzla ilgili her türlü sorunuz için bize ulaşabilirsiniz.
          </p>
          
          <div style={{ 
            display: 'inline-flex',
            flexDirection: 'column',
            alignItems: 'center',
            background: '#eff6ff', 
            border: '1px solid #bfdbfe',
            borderRadius: '12px',
            padding: '30px',
            marginTop: '20px',
            marginBottom: '10px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>📧</div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1e40af', margin: '0 0 10px 0' }}>E-Posta</h2>
            <p style={{ margin: '0 0 15px 0', color: '#64748b' }}>
              Bize doğrudan e-posta gönderebilirsiniz:
            </p>
            <a 
              href="mailto:info@tarimimar.com.tr" 
              style={{ 
                fontSize: '1.25rem', 
                fontWeight: '700', 
                color: '#2563eb', 
                textDecoration: 'none',
                padding: '10px 20px',
                background: 'white',
                borderRadius: '8px',
                border: '1px solid #dbeafe',
                transition: 'all 0.2s'
              }}
            >
              info@tarimimar.com.tr
            </a>
          </div>
        </div>
      </div>

      {/* İletişim Formu */}
      <div style={{ marginTop: '-40px' }}>
        <ContactForm />
      </div>

    </Layout>
  );
}
