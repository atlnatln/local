import Seo from '../components/Seo';
import dynamic from 'next/dynamic';
import { GetStaticProps } from 'next';
import { useMemo, useState } from 'react';
import DeferredSection from '../components/DeferredSection';
import Layout from '../components/Layout';
import MethodologySection from '../components/LandingPage/MethodologySection';
import FAQSection from '../components/LandingPage/FAQSection';
import { homepageFaqs } from '../components/LandingPage/FAQSection';
import DisclaimerSection from '../components/LandingPage/DisclaimerSection';
import { useGA4 } from '../lib/useGA4';
import styles from '../styles/HomePage.module.css';
import planData from '../data/cevre-duzeni-planlari.json';

const DeferredCalculationInsights = dynamic(() => import('../components/CalculationInsights'), {
  ssr: false,
});

const DeferredContactForm = dynamic(() => import('../components/ContactForm'), {
  ssr: false,
});

interface HomePageProps {
  yapiTurleri: unknown[];
  pageTitle: string;
  pageDescription: string;
}

type NavigationItem = {
  icon: string;
  title: string;
  description: string;
  href: string;
  trackingType?: string;
  provinceList?: string[];
};

type NavigationSection = {
  id: string;
  icon: string;
  title: string;
  description: string;
  items: NavigationItem[];
};

export default function HomePage({ pageTitle, pageDescription }: Omit<HomePageProps, 'yapiTurleri'>) {
  const ga4 = useGA4();
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [expandedProvinceGroups, setExpandedProvinceGroups] = useState<Record<string, boolean>>({});

  const normalizeSlugValue = (value: string): string => {
    return value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/ı/g, 'i')
      .replace(/İ/g, 'i')
      .replace(/I/g, 'i')
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  };

  const getStructureUrl = (urlSlug: string) => {
    return `/${urlSlug}`;
  };

  // GA4: Hesaplama sayfasına yönlendirme tracking
  const handleCalculationClick = (calculationType: string) => {
    ga4.trackEvent('calculation_navigation', {
      calculation_type: calculationType,
      source_page: 'homepage',
      page_location: window.location.href,
    });
  };

  const coveredProvinceNames = useMemo(
    () => Array.from(new Set(planData.planlar.flatMap((plan) => plan.iller)))
      .sort((firstProvince, secondProvince) => firstProvince.localeCompare(secondProvince, 'tr-TR')),
    []
  );

  const navigationSections: NavigationSection[] = [
    {
      id: 'tarimsal-yapi-hesaplama',
      icon: '🏗️',
      title: 'Tarımsal Yapı Hesaplama',
      description: 'Yapı türlerine göre alan, kapasite ve mevzuat uygunluğu hesaplamaları',
      items: [
        { icon: '🏡', title: 'Bağ evi', description: 'Bağ evi yapı alanı ve koşulları hesaplaması', href: getStructureUrl('bag-evi'), trackingType: 'bag-evi' },
        { icon: '🪱', title: 'Solucan ve solucan gübresi', description: 'Solucan üretimi ve kompost gübre tesisi hesaplaması', href: getStructureUrl('solucan-tesisi') },
        { icon: '🍄', title: 'Mantar üretim', description: 'Mantar üretim alanı ve tesisi hesaplaması', href: getStructureUrl('mantar-tesisi') },
        { icon: '🌱', title: 'Sera', description: 'Sera tesisi kurulum alanı ve kapasite hesaplaması', href: getStructureUrl('sera') },
        { icon: '🐝', title: 'Arıcılık', description: 'Arı kovanı ve bal üretim tesisi hesaplaması', href: getStructureUrl('aricilik'), trackingType: 'aricilik' },
        { icon: '🌾', title: 'Hububat ve yem depolama silosu', description: 'Hububat depolama silosu alan ve kapasite hesaplaması', href: getStructureUrl('hububat-silo') },
        { icon: '🏪', title: 'Tarımsal amaçlı depo', description: 'Genel tarımsal ürün depolama tesisi hesaplaması', href: getStructureUrl('tarimsal-depo') },
        { icon: '📦', title: 'Lisanslı depolar', description: 'Lisanslı depolama tesisi alan hesaplaması', href: getStructureUrl('lisansli-depo') },
        { icon: '🚿', title: 'Tarımsal ürün yıkama', description: 'Ürün yıkama ve temizleme tesisi hesaplaması', href: getStructureUrl('yikama-tesisi') },
        { icon: '🌞', title: 'Hububat, çeltik, ayçiçeği kurutma', description: 'Tahıl kurutma tesisi alan hesaplaması', href: getStructureUrl('kurutma-tesisi') },
        { icon: '🍑', title: 'Açıkta meyve/sebze kurutma', description: 'Meyve ve sebze kurutma alanı hesaplaması', href: getStructureUrl('meyve-sebze-kurutma') },
        { icon: '🫒', title: 'Zeytinyağı fabrikası', description: 'Zeytinyağı üretim tesisi alan hesaplaması', href: getStructureUrl('zeytinyagi-fabrikasi') },
        { icon: '❄️', title: 'Soğuk hava deposu', description: 'Tarımsal ürün soğuk depolama tesisi hesaplaması', href: getStructureUrl('soguk-hava-deposu') },
        { icon: '💧', title: 'Su depolama ve pompaj sistemi', description: 'Tarımsal sulama su depolama hesaplaması', href: getStructureUrl('su-depolama') },
        { icon: '⛲', title: 'Su kuyuları', description: 'Tarımsal sulama kuyusu tesisi hesaplaması', href: getStructureUrl('su-kuyulari') },
        { icon: '🐄', title: 'Süt Sığırcılığı', description: 'Süt sığırı ahırı alan ve kapasite hesaplaması', href: getStructureUrl('sut-sigirciligi') },
        { icon: '🐑', title: 'Ağıl (küçükbaş)', description: 'Koyun-keçi ağılı alan ve kapasite hesaplaması', href: getStructureUrl('agil-kucukbas') },
        { icon: '🥚', title: 'Kümes (yumurtacı tavuk)', description: 'Yumurta tavuğu tesisi alan ve kapasite hesaplaması', href: getStructureUrl('kumes-yumurtaci') },
        { icon: '🍗', title: 'Kümes (etçi tavuk)', description: 'Etlik piliç tesisi alan ve kapasite hesaplaması', href: getStructureUrl('kumes-etci') },
        { icon: '🐔', title: 'Kümes (gezen tavuk)', description: 'Organik tavuk tesisi alan hesaplaması', href: getStructureUrl('kumes-gezen') },
        { icon: '🦃', title: 'Kümes (hindi)', description: 'Hindi üretim tesisi alan hesaplaması', href: getStructureUrl('kumes-hindi') },
        { icon: '🦆', title: 'Kaz Ördek çiftliği', description: 'Su kuşları üretim tesisi hesaplaması', href: getStructureUrl('kaz-ordek') },
        { icon: '🐎', title: 'Hara (at üretimi)', description: 'At yetiştiriciliği tesisi alan hesaplaması', href: getStructureUrl('hara') },
        { icon: '🦋', title: 'İpek böcekçiliği', description: 'İpek böceği üretim tesisi hesaplaması', href: getStructureUrl('ipek-bocekciligi') },
        { icon: '🐕', title: 'Evcil hayvan ve bilimsel araştırma hayvanı üretim', description: 'Pet ve laboratuvar hayvanı üretim tesisi', href: getStructureUrl('evcil-hayvan') },
        { icon: '🐃', title: 'Besi Sığırcılığı', description: 'Besi sığırı tesisi alan ve kapasite hesaplaması', href: getStructureUrl('besi-sigirciligi') },
      ],
    },
    {
      id: 'ciftlik-hayvanciligi',
      icon: '🐄',
      title: 'Çiftlik Hayvancılığı',
      description: 'Hayvancılık işletmeleri için gelişmiş kapasite, planlama ve 3D analiz araçları',
      items: [
        { icon: '🐄', title: 'Gübre Çukuru Kapasite Hesaplama', description: 'Hayvan türüne göre gübre deposu hacim hesaplaması - 3D görselleştirme ile profesyonel analiz', href: '/gubre-cukuru-hesaplama', trackingType: 'gubre_cukuru' },
        { icon: '🐮', title: 'Buzağı Destekleme Hesaplaması', description: '2026 buzağı desteklerini temel tutar ve ilave katsayılara göre detaylı hesaplayın', href: '/buzagi-destegi-hesaplama', trackingType: 'buzagi_destegi_hesaplama' },
        { icon: '🏗️', title: 'Hayvancılık İşletmeleri Kapasite Hesaplama', description: 'Besi ve süt sığırı ahırları için istenilen kapasite raporunu yaş gruplarına göre alan gereksinimleri ile hesaplayın.', href: '/sigir-ahiri-kapasite-hesaplama', trackingType: 'sigir_ahiri_kapasite' },
        { icon: '🗺️', title: 'Gezginci Arıcılık Konaklama Planlama', description: 'Bitkilerin çiçeklenme zamanına göre gezginci arıcılık rotanızı planlayın.', href: '/aricilik-planlama', trackingType: 'aricilik_planlama' },
        { icon: '🌸', title: 'Çiçeklenme Takvimi', description: 'İlçe bazlı çiçeklenme takvimi ve Türkiye haritası ile verimli bölgeleri keşfedin.', href: '/ciceklenme-takvimi', trackingType: 'ciceklenme_takvimi' },
      ],
    },
    {
      id: 'bitkisel-uretim',
      icon: '🌾',
      title: 'Bitkisel Üretim',
      description: 'Bitkisel üretim destek modelleri ve ürün bazlı teşvik hesaplamaları',
      items: [
        { icon: '💰', title: 'Havza Bazlı Destekleme Modeli', description: '2026 yılı bitkisel üretim desteklerini ürün, il/ilçe ve destek türüne göre hesaplayın', href: '/havza-bazli-destekleme-modeli', trackingType: 'havza_bazli_destekleme_modeli' },
      ],
    },
    {
      id: 'mevzuat',
      icon: '📚',
      title: 'Mevzuat',
      description: 'Tarımsal yapılaşma için temel kanunlar, genelgeler ve plan notları',
      items: [
        { icon: '🌱', title: 'Toprak Koruma ve Arazi Kullanımı Kanunu', description: '5403 Sayılı Kanun - Tarım arazilerinin korunması ve sınıflandırılması', href: '/documents/toprak-koruma-kanunu' },
        { icon: '📋', title: 'Tarım Arazileri Kullanımı Genelgesi', description: 'İmar ve yapılaşma düzenlemeleri - Bağ evi, sera, hayvancılık tesisleri', href: '/documents/tarim-arazileri-kullanimi-genelgesi' },
        { icon: '🫒', title: 'Zeytinciliğin Islahı Kanunu', description: '3573 Sayılı Kanun (1939) - Zeytinlik alanlarda yapılaşma yasak ve kısıtlamaları', href: '/documents/zeytincilik-islahi-kanunu' },
        { icon: '🫒', title: 'Zeytinciliğin Islahı Yönetmeliği', description: '1996 Yönetmeliği - Zeytincilik alanlarında yapılaşma kısıtlamaları', href: '/documents/zeytincilik-islahi-yonetmeligi' },
        { icon: '🗺️', title: 'İzmir Büyükşehir Plan Notları', description: 'Tarım alanları ve yapılaşma koşulları', href: '/documents/izmir-buyuksehir-plan-notlari' },
        {
          icon: '🗺️',
          title: '1/100.000 Ölçekli Çevre Düzeni Planlarında Tarımsal Hükümler',
          description: '20 bölge, 55+ il için tarımsal yapılaşma koşulları ve emsal değerleri - İnteraktif harita',
          href: '/cevre-duzeni-planlari',
          provinceList: coveredProvinceNames,
        },
      ],
    },
  ];

  const toggleSection = (sectionId: string) => {
    setActiveSection((current) => (current === sectionId ? null : sectionId));
  };

  const toggleProvinceGroup = (itemKey: string) => {
    setExpandedProvinceGroups((current) => ({
      ...current,
      [itemKey]: !current[itemKey],
    }));
  };

  // Structured Data for the homepage
  const webPageStructuredData = {
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

  const faqStructuredData = {
    "@type": "FAQPage",
    "mainEntity": homepageFaqs.map((faq) => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer,
      },
    })),
  };

  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [webPageStructuredData, faqStructuredData],
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
            <h1>Tarım ve İmar Mevzuatında Güvenilir Dijital Çözüm Ortağınız</h1>
            <p>
              Tarımsal arazilerde yapılaşma süreçlerinde <strong>5403 Sayılı Kanun</strong> ve güncel yönetmeliklere tam uyumlu, 
              mühendislik esaslı ve şeffaf hesaplama araçları. Yatırımlarınızı mevzuat güvencesiyle planlayın.
            </p>
            <button 
              className={styles.contactButton}
              onClick={() => {
                document.getElementById('contact-section')?.scrollIntoView({ 
                  behavior: 'smooth' 
                });
              }}
            >
              Uzman Desteği Alın
            </button>
          </div>

          <div className={styles.content}>
            <section className={styles.section} aria-label="Hızlı Erişim Menüsü">
              <div className={styles.accordionContainer}>
                {navigationSections.map((section) => {
                  const panelId = `${section.id}-panel`;
                  const isOpen = activeSection === section.id;

                  return (
                    <div key={section.id} className={styles.accordionItem}>
                      <button
                        type="button"
                        className={styles.accordionButton}
                        aria-expanded={isOpen}
                        aria-controls={panelId}
                        onClick={() => toggleSection(section.id)}
                      >
                        <span className={styles.accordionButtonMain}>
                          <span className={styles.accordionIcon}>{section.icon}</span>
                          <span>
                            <span className={styles.accordionTitle}>{section.title}</span>
                            <span className={styles.accordionDescription}>{section.description}</span>
                          </span>
                        </span>
                        <span className={styles.accordionChevron} aria-hidden="true">{isOpen ? '−' : '+'}</span>
                      </button>

                      <div
                        id={panelId}
                        className={`${styles.accordionPanel} ${isOpen ? styles.accordionPanelOpen : styles.accordionPanelClosed}`}
                      >
                          <div className={styles.calculationGrid}>
                            {section.items.map((item) => {
                              const itemKey = `${section.id}-${item.href}`;

                              if (!item.provinceList || item.provinceList.length === 0) {
                                return (
                                  <a
                                    key={itemKey}
                                    href={item.href}
                                    className={styles.calculationCard}
                                    onClick={item.trackingType ? () => handleCalculationClick(item.trackingType!) : undefined}
                                  >
                                    <div className={styles.calculationIcon}>{item.icon}</div>
                                    <h3>{item.title}</h3>
                                    <p>{item.description}</p>
                                  </a>
                                );
                              }

                              return (
                                <div key={itemKey} className={`${styles.calculationCard} ${styles.calculationCardWithChildren}`}>
                                  {(() => {
                                    const isProvinceGroupOpen = Boolean(expandedProvinceGroups[itemKey]);

                                    return (
                                      <>
                                  <a
                                    href={item.href}
                                    className={styles.calculationCardMainLink}
                                    onClick={item.trackingType ? () => handleCalculationClick(item.trackingType!) : undefined}
                                  >
                                    <div className={styles.calculationIcon}>{item.icon}</div>
                                    <h3>{item.title}</h3>
                                    <p>{item.description}</p>
                                  </a>

                                  <div className={styles.nestedDetails}>
                                    <button
                                      type="button"
                                      className={styles.nestedSummaryButton}
                                      onClick={() => toggleProvinceGroup(itemKey)}
                                      aria-expanded={isProvinceGroupOpen}
                                      aria-controls={`${itemKey}-province-list`}
                                    >
                                      <span className={styles.nestedSummaryLabel}>
                                        🏛️ Kapsamdaki Tüm İller ({item.provinceList.length})
                                      </span>
                                      <span className={styles.nestedSummaryChevron} aria-hidden="true">
                                        {isProvinceGroupOpen ? '−' : '+'}
                                      </span>
                                    </button>

                                    {isProvinceGroupOpen && (
                                      <div id={`${itemKey}-province-list`} className={styles.provinceLinks}>
                                        {item.provinceList.map((province) => {
                                          const href = `/cevre-duzeni-planlari/il/${normalizeSlugValue(province)}`;

                                          return (
                                            <a
                                              key={href}
                                              href={href}
                                              className={styles.provinceLink}
                                            >
                                              {province}
                                            </a>
                                          );
                                        })}
                                      </div>
                                    )}
                                  </div>
                                      </>
                                    );
                                  })()}
                                </div>
                              );
                            })}
                          </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <nav className={styles.botSitemap} aria-label="Ana sayfa kapsamındaki tüm alt bağlantılar">
                {navigationSections.flatMap((section) =>
                  section.items.map((item) => (
                    <a key={`bot-${section.id}-${item.href}`} href={item.href}>{item.title}</a>
                  ))
                )}
              </nav>
            </section>

            <DeferredSection
              minHeight={240}
              placeholder={<div className={styles.lazySectionPlaceholder} aria-hidden="true" />}
            >
              <DeferredCalculationInsights />
            </DeferredSection>

            <DisclaimerSection />
          </div>

          <MethodologySection />

          <FAQSection />

          <DeferredSection
            minHeight={520}
            placeholder={<div className={`${styles.lazySectionPlaceholder} ${styles.lazySectionPlaceholderLarge}`} aria-hidden="true" />}
          >
            <DeferredContactForm />
          </DeferredSection>
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
