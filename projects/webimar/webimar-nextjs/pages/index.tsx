import Head from 'next/head';
import Seo from '../components/Seo';
import { GetStaticProps } from 'next';
import { Suspense, lazy } from 'react';
import Layout from '../components/Layout';
import { useGA4 } from '../lib/useGA4';
import styles from '../styles/HomePage.module.css';

// Lazy load ContactForm for better performance
const ContactForm = lazy(() => import('../components/ContactForm'));

// Environment-based URL helper function
const getCalculationUrl = (structureType: string): string => {
  // Use environment variable for React SPA URL
  const reactSpaUrl = process.env.NEXT_PUBLIC_REACT_SPA_URL;
  
  // If REACT_SPA_URL starts with http, it's a full URL (dev-local.sh mode)
  // Otherwise, it's a path (docker mode with nginx)
  if (reactSpaUrl && reactSpaUrl.startsWith('http')) {
    // Full URL mode: http://localhost:3001/mantar-tesisi
    return `${reactSpaUrl}/${structureType}`;
  } else {
    // Path mode: /hesaplama/mantar-tesisi
    return `/hesaplama/${structureType}`;
  }
};

// Yapı türü ikonları eşlemesi
const structureTypeIcons: Record<string, string> = {
  'hububat-silo': '🌾',
  'tarimsal-depo': '🏪',
  'lisansli-depo': '📦',
  'yikama-tesisi': '🚿',
  'kurutma-tesisi': '🌞',
  'meyve-sebze-kurutma': '🍑',
  'zeytinyagi-fabrikasi': '🫒',
  'su-depolama': '💧',
  'su-kuyulari': '⛲',
  'bag-evi': '🏡',
  'soguk-hava-deposu': '❄️',
  'solucan-tesisi': '🪱',
  'mantar-tesisi': '🍄',
  'sera': '🌱',
  'aricilik': '🐝',
  'sut-sigirciligi': '🐄',
  'agil-kucukbas': '🐑',
  'kumes-yumurtaci': '🥚',
  'kumes-etci': '🍗',
  'kumes-gezen': '🐔',
  'kumes-hindi': '🦃',
  'kaz-ordek': '🦆',
  'hara': '🐎',
  'ipek-bocekciligi': '🦋',
  'evcil-hayvan': '🐕',
  'besi-sigirciligi': '🐃',
};

interface HomePageProps {
  yapiTurleri: any[];
  pageTitle: string;
  pageDescription: string;
}

export default function HomePage({ yapiTurleri, pageTitle, pageDescription }: HomePageProps) {
  const ga4 = useGA4();

  const getStructureUrl = (urlSlug: string) => {
    return `/${urlSlug}`;
  };

  // GA4: Hesaplama sayfasına yönlendirme tracking
  const handleCalculationClick = (calculationType: string, event: React.MouseEvent) => {
    ga4.trackEvent('calculation_navigation', {
      calculation_type: calculationType,
      source_page: 'homepage',
      page_location: window.location.href,
    });
  };

  // Kategorilere grupla - yapiTurleri'nin array olduğundan emin ol
  const validYapiTurleri = Array.isArray(yapiTurleri) ? yapiTurleri : [];
  const categories = validYapiTurleri.reduce((acc: any, item: any) => {
    const category = item.kategori || 'Diğer';
    if (!acc[category]) {
      acc[category] = {
        name: category,
        icon: getCategoryIcon(category),
        types: []
      };
    }
    acc[category].types.push(item);
    return acc;
  }, {});

  const categoriesArray = Object.values(categories);

  function getCategoryIcon(category: string): string {
    const iconMap: Record<string, string> = {
      'Hububat Depolama': '🌾',
      'Tarımsal Depolama': '🏪',
      'Tarımsal Tesisler': '🏗️',
      'Su Yapıları': '💧',
      'Sera ve Bahçe': '🌱',
      'Hayvancılık': '🐄',
      'Diğer': '🔧'
    };
    return iconMap[category] || '🏗️';
  }

  // Structured Data for the homepage
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": pageTitle,
    "description": pageDescription,
    "url": "https://tarimimar.com.tr",
    "mainEntity": {
      "@type": "ItemList",
      "name": "Tarımsal Yapı Türleri",
      "description": "Mevzuata uygun tarımsal yapılaşma hesaplama türleri",
      "itemListElement": [
        {
          "@type": "SiteNavigationElement",
          "position": 1,
          "name": "Bağ Evi",
          "description": "Bağ evi yapı alanı ve koşulları hesaplaması",
          "url": "https://tarimimar.com.tr/hesaplama/bag-evi"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 2,
          "name": "Sera",
          "description": "Sera tesisi kurulum alanı ve kapasite hesaplaması",
          "url": "https://tarimimar.com.tr/hesaplama/sera"
        },
        {
          "@type": "SiteNavigationElement",
          "position": 3,
          "name": "Gübre Çukuru",
          "description": "Hayvan türüne göre gübre deposu hacim hesaplaması",
          "url": "https://tarimimar.com.tr/gubre-cukuru-hesaplama"
        }
      ]
    },
    "publisher": {
      "@type": "Organization",
      "name": "Tarım İmar",
      "url": "https://tarimimar.com.tr",
      "logo": {
        "@type": "ImageObject",
        "url": "https://tarimimar.com.tr/og-image.svg"
      }
    },
    "breadcrumb": {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Ana Sayfa",
          "item": "https://tarimimar.com.tr"
        }
      ]
    }
  };

  return (
    <>
      <Seo
        title={pageTitle}
        description={pageDescription}
        canonical="https://tarimimar.com.tr"
        url="https://tarimimar.com.tr"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        jsonLd={structuredData}
        keywords="tarım yapılaşma, tarımsal hesaplama, bağ evi, sera, hayvan barınağı, depo, lisanslı depo, soğuk hava deposu, gübre çukuru, toprak koruma kanunu, arazi kullanımı, tarım mevzuatı"
      />

      <Layout>
        <div className={styles.mainContainer}>
          {/* Hero Section */}
          <div className={styles.hero}>
            <h1>Arazilerde Yapılaşma Mevzuatı ve Hesaplama Sistemi</h1>
            <p>
              Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri. Yasal sınırlar, teknik gereklilikler ve modern teknolojinin birleştiği noktada, doğru ve şeffaf analiz ile karar desteği sunuyoruz.
            </p>
            <button 
              className={styles.contactButton}
              onClick={() => {
                document.getElementById('contact-section')?.scrollIntoView({ 
                  behavior: 'smooth' 
                });
              }}
            >
              Bize Ulaşın
            </button>
          </div>
          
          <div className={styles.content}>
            {/* Barınma */}
            <div className={styles.section}>
              <h2>🏡 Barınma</h2>
              <div className={styles.calculationGrid}>
                                <a href={getStructureUrl('bag-evi')} className={styles.calculationCard} onClick={(e) => handleCalculationClick('bag-evi', e)}>
                  <div className={styles.calculationIcon}>{structureTypeIcons['bag-evi']}</div>
                  <h3>Bağ evi</h3>
                  <p>Bağ evi yapı alanı ve koşulları hesaplaması</p>
                </a>
              </div>
            </div>

            {/* Özel Üretim Tesisleri */}
            <div className={styles.section}>
              <h2>🌱 Özel Üretim Tesisleri</h2>
              <div className={styles.calculationGrid}>
                <a href={getStructureUrl('solucan-tesisi')} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🪱</div>
                  <h3>Solucan ve solucan gübresi</h3>
                  <p>Solucan üretimi ve kompost gübre tesisi hesaplaması</p>
                </a>
                
                <a href={getStructureUrl('mantar-tesisi')} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🍄</div>
                  <h3>Mantar üretim</h3>
                  <p>Mantar üretim alanı ve tesisi hesaplaması</p>
                </a>
                
                <a href={getStructureUrl('sera')} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🌱</div>
                  <h3>Sera</h3>
                  <p>Sera tesisi kurulum alanı ve kapasite hesaplaması</p>
                </a>
                
                <a href={getStructureUrl('aricilik')} className={styles.calculationCard} onClick={(e) => handleCalculationClick('aricilik', e)}>
                  <div className={styles.calculationIcon}>🐝</div>
                  <h3>Arıcılık</h3>
                  <p>Arı kovanı ve bal üretim tesisi hesaplaması</p>
                </a>
              </div>
            </div>

            {/* Depolama ve İşleme */}
            <div className={styles.section}>
              <h2>📦 Depolama ve İşleme</h2>
              <div className={styles.calculationGrid}>
                <a href={getStructureUrl("hububat-silo")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🌾</div>
                  <h3>Hububat ve yem depolama silosu</h3>
                  <p>Hububat depolama silosu alan ve kapasite hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("tarimsal-depo")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🏪</div>
                  <h3>Tarımsal amaçlı depo</h3>
                  <p>Genel tarımsal ürün depolama tesisi hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("lisansli-depo")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>📦</div>
                  <h3>Lisanslı depolar</h3>
                  <p>Lisanslı depolama tesisi alan hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("yikama-tesisi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🚿</div>
                  <h3>Tarımsal ürün yıkama</h3>
                  <p>Ürün yıkama ve temizleme tesisi hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("kurutma-tesisi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🌞</div>
                  <h3>Hububat, çeltik, ayçiçeği kurutma</h3>
                  <p>Tahıl kurutma tesisi alan hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("meyve-sebze-kurutma")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🍑</div>
                  <h3>Açıkta meyve/sebze kurutma</h3>
                  <p>Meyve ve sebze kurutma alanı hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("zeytinyagi-fabrikasi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🫒</div>
                  <h3>Zeytinyağı fabrikası</h3>
                  <p>Zeytinyağı üretim tesisi alan hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("soguk-hava-deposu")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>❄️</div>
                  <h3>Soğuk hava deposu</h3>
                  <p>Tarımsal ürün soğuk depolama tesisi hesaplaması</p>
                </a>
              </div>
            </div>

            {/* Su Yapıları */}
            <div className={styles.section}>
              <h2>💧 Su Yapıları</h2>
              <div className={styles.calculationGrid}>
                <a href={getStructureUrl("su-depolama")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>💧</div>
                  <h3>Su depolama ve pompaj sistemi</h3>
                  <p>Tarımsal sulama su depolama hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("su-kuyulari")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>⛲</div>
                  <h3>Su kuyuları</h3>
                  <p>Tarımsal sulama kuyusu tesisi hesaplaması</p>
                </a>
              </div>
            </div>

            {/* Hayvancılık Tesisleri */}
            <div className={styles.section}>
              <h2>🐄 Hayvancılık Tesisleri</h2>
              <div className={styles.calculationGrid}>
                <a href={getStructureUrl("sut-sigirciligi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🐄</div>
                  <h3>Süt Sığırcılığı</h3>
                  <p>Süt sığırı ahırı alan ve kapasite hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("agil-kucukbas")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🐑</div>
                  <h3>Ağıl (küçükbaş)</h3>
                  <p>Koyun-keçi ağılı alan ve kapasite hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("kumes-yumurtaci")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🥚</div>
                  <h3>Kümes (yumurtacı tavuk)</h3>
                  <p>Yumurta tavuğu tesisi alan ve kapasite hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("kumes-etci")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🍗</div>
                  <h3>Kümes (etçi tavuk)</h3>
                  <p>Etlik piliç tesisi alan ve kapasite hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("kumes-gezen")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🐔</div>
                  <h3>Kümes (gezen tavuk)</h3>
                  <p>Organik tavuk tesisi alan hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("kumes-hindi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🦃</div>
                  <h3>Kümes (hindi)</h3>
                  <p>Hindi üretim tesisi alan hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("kaz-ordek")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🦆</div>
                  <h3>Kaz Ördek çiftliği</h3>
                  <p>Su kuşları üretim tesisi hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("hara")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🐎</div>
                  <h3>Hara (at üretimi)</h3>
                  <p>At yetiştiriciliği tesisi alan hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("ipek-bocekciligi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🦋</div>
                  <h3>İpek böcekçiliği</h3>
                  <p>İpek böceği üretim tesisi hesaplaması</p>
                </a>
                
                <a href={getStructureUrl("evcil-hayvan")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🐕</div>
                  <h3>Evcil hayvan ve bilimsel araştırma hayvanı üretim</h3>
                  <p>Pet ve laboratuvar hayvanı üretim tesisi</p>
                </a>
                
                <a href={getStructureUrl("besi-sigirciligi")} className={styles.calculationCard}>
                  <div className={styles.calculationIcon}>🐃</div>
                  <h3>Besi Sığırcılığı</h3>
                  <p>Besi sığırı tesisi alan ve kapasite hesaplaması</p>
                </a>
              </div>

              {/* Öne Çıkan Hesaplama - Havza Bazlı Destekleme Modeli */}
              <div className={styles.featuredSection} style={{ marginTop: '3rem' }}>
                <h2>🌾 Havza Bazlı Destekleme Modeli</h2>
                <p>2026 yılı bitkisel üretim desteklerini ürün, il/ilçe ve destek türüne göre hesaplayın</p>
                <a
                  href="/havza-bazli-destekleme-modeli"
                  className={styles.featuredButton}
                  onClick={(e) => handleCalculationClick('havza_bazli_destekleme_modeli', e)}
                >
                  💰 Destek Hesapla
                </a>
              </div>

              {/* Öne Çıkan Hesaplama - Gübre Çukuru */}
              <div className={styles.featuredSection} style={{ marginTop: '2rem' }}>
                <h2>🐄 Gübre Çukuru Kapasite Hesaplama</h2>
                <p>Hayvan türüne göre gübre deposu hacim hesaplaması - 3D görselleştirme ile profesyonel analiz</p>
                <a href="/gubre-cukuru-hesaplama" className={styles.featuredButton} onClick={(e) => handleCalculationClick('gubre_cukuru', e)}>
                  3D Hesaplamaya Başla
                </a>
              </div>

              {/* Hayvancılık İşletmeleri Kapasite Hesaplama */}
              <div className={styles.featuredSection} style={{ marginTop: '2rem' }}>
                <h2>🏗️ Hayvancılık İşletmeleri Kapasite Hesaplama</h2>
                <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                  <p>
                    Besi ve süt sığırı ahırları için istenilen kapasite raporunu yaş gruplarına göre alan gereksinimleri, durak boyutları ve teknik kriterleri ile hesaplayın.
                  </p>
                  <a href="/sigir-ahiri-kapasite-hesaplama" className={styles.featuredButton} onClick={(e) => handleCalculationClick('sigir_ahiri_kapasite', e)}>
                    🐄 Sığır Ahırı Hesapla
                  </a>
                </div>
              </div>

              {/* Gezginci Arıcılık Konaklama Planlama */}
              <div className={styles.featuredSection} style={{ marginTop: '2rem' }}>
                <h2>🐝 Gezginci Arıcılık Konaklama Planlama</h2>
                <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                  <p>
                    Bitkilerin çiçeklenme zamanına göre gezginci arıcılık rotanızı planlayın. İlçe bazlı çiçeklenme takvimi ve Türkiye haritası ile en verimli bal üretim bölgelerini keşfedin.
                  </p>
                  <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    <a href="/aricilik-planlama" className={styles.featuredButton} onClick={(e) => handleCalculationClick('aricilik_planlama', e)}>
                      🗺️ Rota Planla
                    </a>
                    <a href="/ciceklenme-takvimi" className={styles.featuredButton} style={{ background: 'linear-gradient(135deg, #4CAF50, #388E3C)' }} onClick={(e) => handleCalculationClick('ciceklenme_takvimi', e)}>
                      🌸 Çiçeklenme Takvimi
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Yapı Türleri */}
            {categoriesArray.length > 0 && (
              <div className={styles.section}>
                <h2>Desteklenen Yapı Türleri</h2>
                <div className={styles.calculationGrid}>
                  {categoriesArray.map((category: any, index) => (
                    <div key={index} className={styles.calculationCard}>
                      <div className={styles.calculationIcon}>{category.icon}</div>
                      <h3>{category.name}</h3>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                        {category.types.slice(0, 3).map((type: any, idx: number) => (
                          <a
                            key={type.id + '-' + idx}
                            href={getStructureUrl(type.url)}
                            style={{ 
                              padding: '4px 8px', 
                              background: '#f8f9fa', 
                              borderRadius: '4px', 
                              fontSize: '0.8rem',
                              textDecoration: 'none',
                              color: '#6c757d'
                            }}
                          >
                            {structureTypeIcons[type.url] || category.icon} {type.name}
                          </a>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Mevzuat ve Belgeler */}
            <div className={styles.section}>
              <h2>Mevzuat ve Belgeler</h2>
              <div className={styles.legislationGrid}>
                <a href="/documents/toprak-koruma-kanunu" className={styles.legislationButton}>
                  <div className={styles.legislationIcon}>🌱</div>
                  <div className={styles.legislationInfo}>
                    <h3>Toprak Koruma ve Arazi Kullanımı Kanunu</h3>
                    <p>5403 Sayılı Kanun - Tarım arazilerinin korunması ve sınıflandırılması</p>
                  </div>
                </a>
                
                <a href="/documents/tarim-arazileri-kullanimi-genelgesi" className={styles.legislationButton}>
                  <div className={styles.legislationIcon}>📋</div>
                  <div className={styles.legislationInfo}>
                    <h3>Tarım Arazileri Kullanımı Genelgesi</h3>
                    <p>İmar ve yapılaşma düzenlemeleri - Bağ evi, sera, hayvancılık tesisleri</p>
                  </div>
                </a>
                
                <a href="/documents/zeytincilik-islahi-kanunu" className={styles.legislationButton}>
                  <div className={styles.legislationIcon}>🫒</div>
                  <div className={styles.legislationInfo}>
                    <h3>Zeytinciliğin Islahı Kanunu</h3>
                    <p>3573 Sayılı Kanun (1939) - Zeytinlik alanlarda yapılaşma yasak ve kısıtlamaları</p>
                  </div>
                </a>
                
                <a href="/documents/zeytincilik-islahi-yonetmeligi" className={styles.legislationButton}>
                  <div className={styles.legislationIcon}>🫒</div>
                  <div className={styles.legislationInfo}>
                    <h3>Zeytinciliğin Islahı Yönetmeliği</h3>
                    <p>1996 Yönetmeliği - Zeytincilik alanlarında yapılaşma kısıtlamaları</p>
                  </div>
                </a>
                
                <a href="/documents/izmir-buyuksehir-plan-notlari" className={styles.legislationButton}>
                  <div className={styles.legislationIcon}>🗺️</div>
                  <div className={styles.legislationInfo}>
                    <h3>İzmir Büyükşehir Plan Notları</h3>
                    <p>Tarım alanları ve yapılaşma koşulları</p>
                  </div>
                </a>
                
                <a href="/cevre-duzeni-planlari" className={styles.legislationButton}>
                  <div className={styles.legislationIcon}>🗺️</div>
                  <div className={styles.legislationInfo}>
                    <h3>1/100.000 Ölçekli Çevre Düzeni Planlarında Tarımsal Hükümler</h3>
                    <p>20 bölge, 55+ il için tarımsal yapılaşma koşulları ve emsal değerleri - İnteraktif harita</p>
                  </div>
                </a>
              </div>
            </div>
          </div>
          
          {/* Contact Form */}
          <Suspense fallback={<div>Yükleniyor...</div>}>
            <ContactForm />
          </Suspense>
        </div>
      </Layout>
    </>
  );
}

export const getStaticProps: GetStaticProps = async () => {
  try {
    // Development/Production uyumlu API fetch
    let yapiTurleri = [];
    
    try {
      // Production'da API URL'i environment variable'dan gelecek
      const apiUrl = process.env.API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/calculations/yapi-turleri/`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        yapiTurleri = await response.json();
        console.log('API data fetched successfully, count:', yapiTurleri.length);
      } else {
        console.log('API request failed with status:', response.status);
        yapiTurleri = [];
      }
    } catch (apiError) {
      console.log('API fetch failed:', apiError);
      // Build sırasında API erişilemiyorsa boş array kullan
      yapiTurleri = [];
    }

    return {
      props: {
        yapiTurleri,
        pageTitle: 'Tarım İmar - Tarımsal Arazilerde Yapılaşma Hesaplama Sistemi',
        pageDescription: 'Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri.'
      },
    };
  } catch (error) {
    console.error('getStaticProps error:', error);
    return {
      props: {
        yapiTurleri: [],
        pageTitle: 'Tarım İmar - Tarımsal Arazilerde Yapılaşma Hesaplama Sistemi',
        pageDescription: 'Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri.'
      },
    };
  }
};
