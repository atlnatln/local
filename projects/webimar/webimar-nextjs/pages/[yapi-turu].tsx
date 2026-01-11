import Head from 'next/head';
import Seo from '../components/Seo';
import Layout from '../components/Layout';
import Hero from '../components/LandingPage/Hero';
import Features from '../components/LandingPage/Features';
import Requirements from '../components/LandingPage/Requirements';
import Calculator from '../components/LandingPage/Calculator';
import FAQ from '../components/LandingPage/FAQ';
import RelatedPages from '../components/LandingPage/RelatedPages';
import { GetStaticProps, GetStaticPaths } from 'next';
import { YapiTuruData } from '../data/schema/yapi-turu-schema';
import { getAllYapiTuruSlugs, getYapiTuruData } from '../lib/getYapiTuruData';
import { useRouter } from 'next/router';

interface YapiTuruPageProps {
  data: YapiTuruData;
}

export default function YapiTuruPage({ data }: YapiTuruPageProps) {
  const router = useRouter();

  if (!data) {
    return (
      <Layout>
        <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <h1>Sayfa bulunamadı</h1>
          <p>Aradığınız yapı türü bulunamadı.</p>
        </div>
      </Layout>
    );
  }

  // Hesaplama sayfasına yönlendirme
  const handleCalculateClick = () => {
    router.push(data.calculator.ctaLink);
  };

  // Scroll to calculator section
  const scrollToCalculator = () => {
    const element = document.getElementById('calculator-section');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <Seo
        title={data.seo.title}
        description={data.seo.description}
        canonical={data.seo.canonical?.startsWith('http') ? data.seo.canonical : `https://tarimimar.com.tr${data.seo.canonical}`}
        url={data.seo.canonical?.startsWith('http') ? data.seo.canonical : `https://tarimimar.com.tr${data.seo.canonical}`}
        ogImage={data.seo.ogImage || 'https://tarimimar.com.tr/og-image.svg'}
        type="article"
        jsonLd={data.structuredData}
        keywords={data.seo.keywords.join(', ')}
      />

      <Layout>
        {/* Breadcrumb / Ana Sayfa Linki */}
        <div style={{ 
          padding: '1rem 2rem', 
          background: '#f8f9fa',
          borderBottom: '1px solid #e9ecef'
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <a 
              href="/"
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
              onMouseOver={(e) => e.currentTarget.style.color = '#764ba2'}
              onMouseOut={(e) => e.currentTarget.style.color = '#667eea'}
            >
              ← Ana Sayfa
            </a>
          </div>
        </div>

        {/* Hero Section */}
        <Hero
          title={data.hero.title}
          subtitle={data.hero.subtitle}
          icon={data.hero.icon}
          backgroundImage={data.hero.backgroundImage}
          ctaLink={data.calculator.ctaLink}
        />

        {/* Introduction Section */}
        <section style={{ padding: '4rem 2rem', maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem', color: '#2d3748' }}>
              {data.name} Nedir?
            </h2>
            <div 
              style={{ fontSize: '1.125rem', lineHeight: '1.8', color: '#4a5568' }}
              dangerouslySetInnerHTML={{ __html: data.introduction.whatIs }}
            />
          </div>

          {data.introduction.purpose && (
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#2d3748' }}>
                Amaç ve Kullanım
              </h3>
              <div 
                style={{ fontSize: '1.125rem', lineHeight: '1.8', color: '#4a5568' }}
                dangerouslySetInnerHTML={{ __html: data.introduction.purpose }}
              />
            </div>
          )}

          <div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#2d3748' }}>
              Kimler Yapabilir?
            </h3>
            <div 
              style={{ fontSize: '1.125rem', lineHeight: '1.8', color: '#4a5568' }}
              dangerouslySetInnerHTML={{ __html: data.introduction.whoCanBuild }}
            />
          </div>

          {/* İmar / Yapı Ruhsatı bölümü (veri varsa göster) */}
          {data.imar && (
            <div style={{ marginTop: '2rem', background: '#fff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e9ecef' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.75rem', color: '#2d3748' }}>{data.imar.title}</h3>
              <div style={{ fontSize: '1rem', lineHeight: '1.6', color: '#4a5568' }} dangerouslySetInnerHTML={{ __html: data.imar.summary }} />
              {data.imar.requirements && data.imar.requirements.length > 0 && (
                <ul style={{ marginTop: '0.75rem', color: '#4a5568' }}>
                  {data.imar.requirements.map((r, idx) => (
                    <li key={idx} style={{ marginBottom: '0.35rem' }}>{r}</li>
                  ))}
                </ul>
              )}
              {data.imar.referenceUrl && (
                <div style={{ marginTop: '0.7rem' }}>
                  <a href={data.imar.referenceUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#2266cc', fontWeight: 600 }}>Yönetmeliğin tam metni ↗</a>
                </div>
              )}
            </div>
          )}

          {/* Sera Mevzuatı Linkleri */}
          {data.slug === 'sera' && (
            <div style={{ marginTop: '3rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', justifyContent: 'center' }}>
              <a 
                href="/mevzuat/izmir-sera-yonetmeligi"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#fff',
                  color: '#2d3748',
                  padding: '1rem 1.5rem',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  border: '2px solid #e2e8f0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#48bb78';
                  e.currentTarget.style.color = '#2f855a';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.color = '#2d3748';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <span style={{ fontSize: '1.5rem' }}>📜</span>
                İzmir BŞB: Sera Yapımı Mevzuatı
              </a>

              <a 
                href="/mevzuat/kapali-ortamda-bitkisel-uretim-kayit-sistemi-yonetmeligi"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#fff',
                  color: '#2d3748',
                  padding: '1rem 1.5rem',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  border: '2px solid #e2e8f0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#667eea';
                  e.currentTarget.style.color = '#4c51bf';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.color = '#2d3748';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <span style={{ fontSize: '1.5rem' }}>🗂️</span>
                KOBÜKS Yönetmeliği (16.03.2024)
              </a>
            </div>
          )}

          {/* Arıcılık Sayfası Ek Linkler */}
          {data.slug === 'aricilik' && (
            <div style={{ marginTop: '3rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', justifyContent: 'center' }}>
              <a 
                href="/ciceklenme-takvimi"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#fff',
                  color: '#2d3748',
                  padding: '1rem 1.5rem',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  border: '2px solid #e2e8f0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#f6ad55';
                  e.currentTarget.style.color = '#c05621';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.color = '#2d3748';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <span style={{ fontSize: '1.5rem' }}>🌸</span>
                Çiçeklenme Takvimi
              </a>
              <a 
                href="/aricilik-planlama"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#fff',
                  color: '#2d3748',
                  padding: '1rem 1.5rem',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  border: '2px solid #e2e8f0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#48bb78';
                  e.currentTarget.style.color = '#2f855a';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.color = '#2d3748';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <span style={{ fontSize: '1.5rem' }}>🗺️</span>
                Konaklama Planlama
              </a>
              <a 
                href="https://www.resmigazete.gov.tr/eskiler/2024/05/20240523-1.htm"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#fff',
                  color: '#2d3748',
                  padding: '1rem 1.5rem',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  border: '2px solid #e2e8f0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#667eea';
                  e.currentTarget.style.color = '#5a67d8';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.color = '#2d3748';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <span style={{ fontSize: '1.5rem' }}>📜</span>
                Arıcılık Mevzuatı ↗
              </a>
            </div>
          )}
        </section>

        {/* Features */}
        {data.features && data.features.length > 0 && (
          <Features features={data.features} />
        )}

        {/* Requirements */}
        <Requirements
          legal={data.requirements.legal}
          technical={data.requirements.technical}
        />

        {/* Calculator CTA */}
        <div id="calculator-section">
          <Calculator
            title={data.calculator.title}
            description={data.calculator.description}
            ctaText={data.calculator.ctaText}
            ctaLink={data.calculator.ctaLink}
          />
        </div>

        {/* Harita Özellikleri Bilgilendirme */}
        <section style={{ 
          padding: '3rem 2rem', 
          background: 'linear-gradient(135deg, #f8f9fa 0%, #e9f5e9 100%)',
          borderTop: '1px solid #c3e6cb',
          borderBottom: '1px solid #c3e6cb'
        }}>
          <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            <h3 style={{ 
              fontSize: '1.5rem', 
              fontWeight: '700', 
              marginBottom: '1.5rem', 
              color: '#155724',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <span>🗺️</span>
              Hesaplama Sayfasındaki Harita Özellikleri
            </h3>
            
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '1.5rem',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              marginBottom: '1.5rem'
            }}>
              <ul style={{ 
                margin: 0, 
                padding: '0 0 0 1.25rem', 
                color: '#2d5a3d',
                fontSize: '1rem',
                lineHeight: '2'
              }}>
                <li><strong>📍 Konum Seçimi:</strong> Harita üzerinde hesaplama yapmak istediğiniz arazinin üzerine veya yakınına tıklayarak konum seçebilirsiniz.</li>
                <li><strong>🌾 Büyükova Kontrolü:</strong> Haritada işaretleyeceğiniz nokta "Büyükova Tarım Alanları" kontrolü yapar. Bu alanlarda 5403 sayılı yasa gereği tarımsal yapılaşma kısıtlamaları uygulanır.</li>
                <li><strong>💧 DSİ Kapalı Havza:</strong> İşaretlediğiniz noktanın DSİ tarafından belirlenen kapalı havza bölgelerinde olması durumunda su bağımlı tesisler (hayvancılık, yıkama tesisi vb.) için ek belgeler istenmektedir.</li>
                <li><strong>🔍 Otomatik Tespit:</strong> Seçtiğiniz konumun büyükova veya kapalı havza içinde olup olmadığı sistem tarafından otomatik olarak tespit edilir ve hesaplama sonucunda size bildirilir.</li>
              </ul>
            </div>
            
            <div style={{
              background: 'rgba(255, 193, 7, 0.15)',
              borderRadius: '8px',
              padding: '1rem 1.25rem',
              borderLeft: '4px solid #ffc107',
              color: '#856404',
              fontSize: '0.95rem',
              lineHeight: '1.6'
            }}>
              <strong>💡 İpucu:</strong> Doğru ve güvenilir hesaplama sonuçları için, arazi konumunuzu harita üzerinde mümkün olduğunca hassas bir şekilde işaretleyin. Sistem, seçilen konuma göre ilgili yasal gereksinimleri otomatik olarak değerlendirir.
            </div>
          </div>
        </section>

        {/* FAQ */}
        {data.faq && data.faq.length > 0 && (
          <FAQ faq={data.faq} />
        )}

        {/* Related Pages */}
        {data.relatedPages && data.relatedPages.length > 0 && (
          <RelatedPages pages={data.relatedPages} />
        )}

        {/* Diğer Tarımsal Yapılar */}
        <section style={{ 
          padding: '4rem 2rem', 
          background: 'white',
          borderTop: '2px solid #e9ecef'
        }}>
          <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
            <h2 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '1rem', color: '#2d3748' }}>
              🏗️ Diğer Tarımsal Yapı Hesaplamaları
            </h2>
            <p style={{ fontSize: '1.25rem', marginBottom: '2rem', color: '#4a5568' }}>
              Hayvancılık tesisleri, depolama yapıları, özel üretim tesisleri ve daha fazlası için ana sayfamızı ziyaret edin
            </p>
            <a 
              href="/"
              style={{
                display: 'inline-block',
                background: '#28a745',
                color: 'white',
                padding: '1.25rem 3rem',
                fontSize: '1.25rem',
                fontWeight: '700',
                borderRadius: '50px',
                textDecoration: 'none',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 15px rgba(40, 167, 69, 0.4)',
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-3px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Tüm Hesaplamaları Gör →
            </a>
          </div>
        </section>

        {/* Contact CTA */}
        <section style={{ 
          padding: '4rem 2rem', 
          background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
          textAlign: 'center'
        }}>
          <div style={{ maxWidth: '700px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '1rem', color: '#2d3748' }}>
              💬 Özel Danışmanlık İster misiniz?
            </h2>
            <p style={{ fontSize: '1.25rem', marginBottom: '2rem', color: '#4a5568' }}>
              Uzmanlarımızla görüşün, size özel çözümler sunalım
            </p>
            <a 
              href="/#contact-section"
              style={{
                display: 'inline-block',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '1.25rem 3rem',
                fontSize: '1.25rem',
                fontWeight: '700',
                borderRadius: '50px',
                textDecoration: 'none',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
              }}
            >
              Bize Ulaşın →
            </a>
          </div>
        </section>
      </Layout>
    </>
  );
}

export const getStaticPaths: GetStaticPaths = async () => {
  const slugs = await getAllYapiTuruSlugs();
  
  const paths = slugs.map((slug) => ({
    params: { 'yapi-turu': slug },
  }));

  return {
    paths,
    fallback: false,
  };
};

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const slug = params?.['yapi-turu'] as string;
  const data = await getYapiTuruData(slug);

  if (!data) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      data,
    },
  };
};
