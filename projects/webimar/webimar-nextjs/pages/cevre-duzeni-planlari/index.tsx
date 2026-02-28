import Head from 'next/head';
import Seo from '../../components/Seo';
import { useState, useEffect, useMemo } from 'react';
import Layout from '../../components/Layout';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import styles from '../../styles/CevreDuzeniPlanlari.module.css';
import planData from '../../data/cevre-duzeni-planlari.json';

// Leaflet'i client-side only yükle
const MapContainer = dynamic(
  () => import('react-leaflet').then(mod => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then(mod => mod.TileLayer),
  { ssr: false }
);
const GeoJSON = dynamic(
  () => import('react-leaflet').then(mod => mod.GeoJSON),
  { ssr: false }
);

// Tüm planlardaki illeri topla
const tumIller = new Set<string>();
planData.planlar.forEach(plan => {
  plan.iller.forEach(il => tumIller.add(il));
});

// Tüm iller array olarak (arama için)
const tumIllerArray = Array.from(tumIller).sort((a, b) => a.localeCompare(b, 'tr'));

// İl adı normalizasyonu (GeoJSON'daki formatla eşleştirme için)
function normalizeIlAdi(ilAdi: string): string {
  return ilAdi
    .toUpperCase()
    .replace(/İ/g, 'I')
    .replace(/Ş/g, 'S')
    .replace(/Ğ/g, 'G')
    .replace(/Ü/g, 'U')
    .replace(/Ö/g, 'O')
    .replace(/Ç/g, 'C')
    .trim();
}

// İl eşleşmesi kontrolü
function ilEslesiyor(geoJsonIl: string, planIller: string[]): boolean {
  const normalGeoJson = normalizeIlAdi(geoJsonIl);
  return planIller.some(il => normalizeIlAdi(il) === normalGeoJson);
}

// İl'e ait plan ID'sini bul
function ildenPlanBul(ilAdi: string): string | null {
  const normalizedIl = normalizeIlAdi(ilAdi);
  for (const plan of planData.planlar) {
    if (plan.iller.some(il => normalizeIlAdi(il) === normalizedIl)) {
      return plan.id;
    }
  }
  return null;
}

// SEO Structured Data - Breadcrumb ve CollectionPage
const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "CollectionPage",
      "@id": "https://tarimimar.com.tr/cevre-duzeni-planlari/#page",
      "name": "1/100.000 Ölçekli Çevre Düzeni Planlarında Tarımsal Hükümler",
      "description": "Türkiye'nin çeşitli bölgelerindeki 1/100.000 ölçekli çevre düzeni planlarında yer alan tarımsal hükümler, yapılaşma koşulları ve emsal değerleri",
      "url": "https://tarimimar.com.tr/cevre-duzeni-planlari/",
      "publisher": {
        "@type": "Organization",
        "name": "Tarım İmar",
        "url": "https://tarimimar.com.tr"
      },
      "about": {
        "@type": "GovernmentService",
        "name": "Çevre Düzeni Planları",
        "description": "Türkiye'de tarımsal yapılaşma için geçerli 1/100.000 ölçekli çevre düzeni planları"
      },
      "numberOfItems": 20,
      "keywords": "çevre düzeni planı, 1/100000 ölçekli plan, tarımsal hükümler, yapılaşma koşulları, emsal, mutlak tarım arazisi, marjinal tarım, dikili tarım, özel ürün arazisi",
      "inLanguage": "tr-TR",
      "isAccessibleForFree": true,
      "datePublished": "2025-11-29",
      "dateModified": "2025-11-29"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Ana Sayfa",
          "item": "https://tarimimar.com.tr"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Çevre Düzeni Planları",
          "item": "https://tarimimar.com.tr/cevre-duzeni-planlari/"
        }
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Mutlak tarım arazisinde emsal ne kadardır?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Mutlak tarım arazilerinde emsal (E) genellikle 0.05 ile 0.20 arasındadır. Çiftçinin barınabileceği yapı emsale dahil olup inşaat alanı 75 m²'yi geçemez."
          }
        },
        {
          "@type": "Question",
          "name": "Marjinal tarım arazisinde yapılaşma koşulları nelerdir?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Marjinal tarım arazilerinde tarımsal amaçlı yapılar için emsal (E) 0.10 ile 0.30 arasındadır. Çiftçinin barınabileceği yapının inşaat alanı 150 m²'yi geçemez."
          }
        },
        {
          "@type": "Question",
          "name": "Seralarda emsal hesabı nasıl yapılır?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Örtü altı tarım yapılması durumunda sera yapıları emsale dahil değildir. Bu kural hem mutlak tarım arazileri hem de marjinal tarım arazileri için geçerlidir."
          }
        }
      ]
    }
  ]
};

export default function CevreDuzeniPlanlari() {
  const [mapLoaded, setMapLoaded] = useState(false);
  const [geoData, setGeoData] = useState<any>(null);
  const [hoveredIl, setHoveredIl] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedKategori, setSelectedKategori] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');

  // Arama sonuçları
  const filteredIller = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const query = searchQuery.toLowerCase();
    return tumIllerArray.filter(il => 
      il.toLowerCase().includes(query)
    ).slice(0, 8);
  }, [searchQuery]);

  // Filtrelenmiş planlar
  const filteredPlanlar = useMemo(() => {
    if (!searchQuery.trim()) return planData.planlar;
    const query = searchQuery.toLowerCase();
    return planData.planlar.filter(plan => 
      plan.baslik.toLowerCase().includes(query) ||
      plan.iller.some(il => il.toLowerCase().includes(query))
    );
  }, [searchQuery]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setMapLoaded(true);
    }
  }, []);

  // GeoJSON verisi yükle - İl sınırlarını göster
  useEffect(() => {
    if (mapLoaded) {
      fetch('/turkey-provinces.geojson')
        .then(res => res.json())
        .then(data => {
          // İlleri işle
          const features = data.features.map((feature: any) => {
            const ilAdi = feature.properties.ADM1_TR;
            const isHighlighted = tumIller.has(ilAdi) || Array.from(tumIller).some(il => normalizeIlAdi(il) === normalizeIlAdi(ilAdi));
            
            return {
              ...feature,
              properties: {
                ...feature.properties,
                ilAdi: ilAdi,
                planId: ildenPlanBul(ilAdi),
                highlighted: isHighlighted
              }
            };
          });

          setGeoData({
            type: 'FeatureCollection',
            features: features
          });
        })
        .catch(err => console.error('GeoJSON yüklenemedi:', err));
    }
  }, [mapLoaded]);

  // Feature style - İl bazında renklendirme
  const getFeatureStyle = (feature: any) => {
    const isHighlighted = feature?.properties?.highlighted;
    const isHovered = feature?.properties?.ilAdi === hoveredIl;
    
    return {
      fillColor: isHighlighted ? '#FF6B35' : '#e5e7eb',
      weight: isHovered ? 3 : 2,
      opacity: 1,
      color: isHighlighted ? '#d4532a' : '#9ca3af',
      fillOpacity: isHighlighted ? (isHovered ? 0.8 : 0.6) : 0.3
    };
  };

  // Feature events
  const onEachFeature = (feature: any, layer: any) => {
    const ilAdi = feature.properties.ilAdi;
    const planId = feature.properties.planId;
    const isHighlighted = feature.properties.highlighted;

    layer.bindTooltip(
      `<strong>${ilAdi}</strong>${isHighlighted ? '<br><span style="color:#FF6B35">📋 Plan mevcut - Tıklayın</span>' : ''}`,
      { permanent: false, direction: 'top' }
    );

    layer.on({
      mouseover: () => setHoveredIl(ilAdi),
      mouseout: () => setHoveredIl(null),
      click: () => {
        if (planId) {
          window.location.href = `/cevre-duzeni-planlari/${planId}/`;
        }
      }
    });
  };

  return (
    <>
      <Seo
        title="1/100.000 Ölçekli Çevre Düzeni Planları | Tarımsal Hükümler | Tarım İmar"
        description="Türkiye'nin çeşitli bölgelerindeki 1/100.000 ölçekli çevre düzeni planlarında yer alan tarımsal hükümler, yapılaşma koşulları ve emsal değerleri"
        canonical="https://tarimimar.com.tr/cevre-duzeni-planlari/"
        url="https://tarimimar.com.tr/cevre-duzeni-planlari/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        jsonLd={structuredData}
        keywords="çevre düzeni planı, 1/100000 ölçekli plan, tarımsal hükümler, yapılaşma koşulları"
      />

      <Layout>
        <div className={styles.container}>
          {/* Hero Header */}
          <div className={styles.heroHeader}>
            <Link href="/" className={styles.backButton}>
              ← Ana Sayfa
            </Link>
            <div className={styles.heroContent}>
              <h1>🗺️ {planData.title}</h1>
              <p className={styles.heroDescription}>{planData.description}</p>
              
              {/* Hızlı Arama */}
              <div className={styles.searchBox}>
                <span className={styles.searchIcon}>🔍</span>
                <input
                  type="text"
                  placeholder="İl veya bölge adı ara... (örn: Antalya, Konya)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={styles.searchInput}
                />
                {searchQuery && (
                  <button 
                    className={styles.clearSearch}
                    onClick={() => setSearchQuery('')}
                  >
                    ✕
                  </button>
                )}
              </div>
              
              {/* Arama Sonuçları */}
              {filteredIller.length > 0 && searchQuery && (
                <div className={styles.searchResults}>
                  <span className={styles.searchResultsTitle}>İller:</span>
                  {filteredIller.map(il => {
                    const planId = ildenPlanBul(il);
                    return planId ? (
                      <Link 
                        key={il} 
                        href={`/cevre-duzeni-planlari/${planId}/`}
                        className={styles.searchResultItem}
                      >
                        📍 {il}
                      </Link>
                    ) : null;
                  })}
                </div>
              )}
            </div>
            
            {/* Dashboard İstatistikleri */}
            <div className={styles.dashboardStats}>
              <div className={styles.dashboardCard}>
                <div className={styles.dashboardIcon}>📊</div>
                <div className={styles.dashboardValue}>{planData.planlar.length}</div>
                <div className={styles.dashboardLabel}>Plan Bölgesi</div>
              </div>
              <div className={styles.dashboardCard}>
                <div className={styles.dashboardIcon}>🏛️</div>
                <div className={styles.dashboardValue}>{tumIller.size}</div>
                <div className={styles.dashboardLabel}>İl Kapsamında</div>
              </div>
              <div className={styles.dashboardCard}>
                <div className={styles.dashboardIcon}>🌾</div>
                <div className={styles.dashboardValue}>4</div>
                <div className={styles.dashboardLabel}>Arazi Sınıfı</div>
              </div>
              <div className={styles.dashboardCard}>
                <div className={styles.dashboardIcon}>📐</div>
                <div className={styles.dashboardValue}>0.05-0.30</div>
                <div className={styles.dashboardLabel}>Emsal Aralığı</div>
              </div>
            </div>
          </div>

          {/* Hızlı Navigasyon */}
          <div className={styles.quickNav}>
            <button 
              className={`${styles.quickNavBtn} ${activeSection === 'overview' ? styles.active : ''}`}
              onClick={() => setActiveSection('overview')}
            >
              📋 Genel Bakış
            </button>
            <button 
              className={`${styles.quickNavBtn} ${activeSection === 'map' ? styles.active : ''}`}
              onClick={() => setActiveSection('map')}
            >
              🗺️ Harita
            </button>
            <button 
              className={`${styles.quickNavBtn} ${activeSection === 'compare' ? styles.active : ''}`}
              onClick={() => setActiveSection('compare')}
            >
              ⚖️ Karşılaştırma
            </button>
            <button 
              className={`${styles.quickNavBtn} ${activeSection === 'regions' ? styles.active : ''}`}
              onClick={() => setActiveSection('regions')}
            >
              📑 Bölgeler
            </button>
          </div>

          {/* BÖLÜM 1: Genel Bakış - Tarım Kategorileri */}
          {(activeSection === 'overview' || activeSection === 'all') && (
            <div className={styles.overviewSection}>
              <h2>🌱 Tarım Arazileri Sınıflandırması</h2>
              <p className={styles.sectionDesc}>
                Türkiye'deki tarım arazileri, verimlilik ve kullanım özelliklerine göre 4 ana kategoride değerlendirilir. 
                Her kategori için farklı yapılaşma koşulları geçerlidir.
              </p>
              
              <div className={styles.categoryShowcase}>
                {/* Mutlak Tarım */}
                <div 
                  className={`${styles.categoryCard} ${selectedKategori === 'mutlak' ? styles.selected : ''}`}
                  onClick={() => setSelectedKategori(selectedKategori === 'mutlak' ? null : 'mutlak')}
                >
                  <div className={styles.categoryHeader}>
                    <span className={styles.categoryEmoji}>🌾</span>
                    <h3>Mutlak Tarım Arazisi</h3>
                  </div>
                  <div className={styles.categoryBadges}>
                    <span className={styles.emsalTag}>E: 0.05-0.20</span>
                    <span className={styles.yapiTag}>75 m²</span>
                  </div>
                  <p>{planData.ortakHukumler.tarimArazileriSiniflari.mutlakTarim.tanim}</p>
                  <div className={styles.categoryMeter}>
                    <div className={styles.meterFill} style={{width: '25%'}}></div>
                    <span>En düşük emsal</span>
                  </div>
                </div>

                {/* Özel Ürün */}
                <div 
                  className={`${styles.categoryCard} ${selectedKategori === 'ozel' ? styles.selected : ''}`}
                  onClick={() => setSelectedKategori(selectedKategori === 'ozel' ? null : 'ozel')}
                >
                  <div className={styles.categoryHeader}>
                    <span className={styles.categoryEmoji}>🍇</span>
                    <h3>Özel Ürün Arazisi</h3>
                  </div>
                  <div className={styles.categoryBadges}>
                    <span className={styles.emsalTag}>E: 0.05-0.20</span>
                    <span className={styles.yapiTag}>75-100 m²</span>
                  </div>
                  <p>{planData.ortakHukumler.tarimArazileriSiniflari.ozelUrun.tanim}</p>
                  <div className={styles.categoryMeter}>
                    <div className={styles.meterFill} style={{width: '25%'}}></div>
                    <span>Düşük emsal</span>
                  </div>
                </div>

                {/* Dikili Tarım */}
                <div 
                  className={`${styles.categoryCard} ${selectedKategori === 'dikili' ? styles.selected : ''}`}
                  onClick={() => setSelectedKategori(selectedKategori === 'dikili' ? null : 'dikili')}
                >
                  <div className={styles.categoryHeader}>
                    <span className={styles.categoryEmoji}>🌳</span>
                    <h3>Dikili Tarım Arazisi</h3>
                  </div>
                  <div className={styles.categoryBadges}>
                    <span className={styles.emsalTag}>E: 0.05-0.10</span>
                    <span className={styles.yapiTag}>75-100 m²</span>
                  </div>
                  <p>{planData.ortakHukumler.tarimArazileriSiniflari.dikiliTarim.tanim}</p>
                  <div className={styles.categoryMeter}>
                    <div className={styles.meterFill} style={{width: '15%'}}></div>
                    <span>En kısıtlı emsal</span>
                  </div>
                </div>

                {/* Marjinal Tarım */}
                <div 
                  className={`${styles.categoryCard} ${selectedKategori === 'marjinal' ? styles.selected : ''}`}
                  onClick={() => setSelectedKategori(selectedKategori === 'marjinal' ? null : 'marjinal')}
                >
                  <div className={styles.categoryHeader}>
                    <span className={styles.categoryEmoji}>🏜️</span>
                    <h3>Marjinal Tarım Arazisi</h3>
                  </div>
                  <div className={styles.categoryBadges}>
                    <span className={styles.emsalTag}>E: 0.10-0.30</span>
                    <span className={styles.yapiTag}>150 m²</span>
                  </div>
                  <p>{planData.ortakHukumler.tarimArazileriSiniflari.marjinalTarim.tanim}</p>
                  <div className={styles.categoryMeter}>
                    <div className={styles.meterFill} style={{width: '50%'}}></div>
                    <span>En yüksek emsal</span>
                  </div>
                </div>
              </div>

              {/* Önemli Kurallar - Kompakt Grid */}
              <div className={styles.rulesGrid}>
                <h3>⚖️ Tüm Planlarda Geçerli Ortak Kurallar</h3>
                <div className={styles.rulesCards}>
                  <div className={styles.ruleCard}>
                    <span className={styles.ruleIcon}>🚫</span>
                    <p>Tarımsal yapılar başka amaçla kullanılamaz</p>
                  </div>
                  <div className={styles.ruleCard}>
                    <span className={styles.ruleIcon}>🌿</span>
                    <p>Seralar emsale dahil değildir</p>
                  </div>
                  <div className={styles.ruleCard}>
                    <span className={styles.ruleIcon}>📏</span>
                    <p>Silo/samanlık yüksekliği ihtiyaca göre</p>
                  </div>
                  <div className={styles.ruleCard}>
                    <span className={styles.ruleIcon}>📜</span>
                    <p>5403 sayılı Kanun hükümleri geçerli</p>
                  </div>
                  <div className={styles.ruleCard}>
                    <span className={styles.ruleIcon}>🐄</span>
                    <p>Mera alanlarında özel hükümler</p>
                  </div>
                  <div className={styles.ruleCard}>
                    <span className={styles.ruleIcon}>🏭</span>
                    <p>Organize tarım için min. 20 ha</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* BÖLÜM 2: Harita */}
          {(activeSection === 'map' || activeSection === 'all') && (
            <div className={styles.mapSection}>
              <h2>📍 Türkiye Haritası - Plan Kapsamındaki İller</h2>
              <p className={styles.sectionDesc}>
                Turuncu renkli iller plan kapsamındadır. Bir ile tıklayarak detaylı bilgilere ulaşabilirsiniz.
              </p>
              
              {mapLoaded && geoData ? (
                <>
                  <div className={styles.mapContainer}>
                    <MapContainer
                      center={[39.0, 35.0]}
                      zoom={6}
                      minZoom={5}
                      maxZoom={10}
                      style={{ height: '100%', width: '100%' }}
                      scrollWheelZoom={true}
                      boxZoom={false}
                      doubleClickZoom={true}
                    >
                      <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                      />
                      <GeoJSON
                        data={geoData}
                        style={getFeatureStyle}
                        onEachFeature={onEachFeature}
                      />
                    </MapContainer>
                  </div>
                  
                  <div className={styles.mapLegend}>
                    <div className={styles.legendItem}>
                      <div className={`${styles.legendColor} ${styles.legendOrange}`}></div>
                      <span>Plan Mevcut (Tıklanabilir)</span>
                    </div>
                    <div className={styles.legendItem}>
                      <div className={`${styles.legendColor} ${styles.legendGray}`}></div>
                      <span>Plan Henüz Eklenmedi</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className={styles.mapPlaceholder}>
                  <div>🗺️</div>
                  <div>Harita yükleniyor...</div>
                </div>
              )}
            </div>
          )}

          {/* BÖLÜM 3: Karşılaştırma Tablosu */}
          {(activeSection === 'compare' || activeSection === 'all') && (
            <div className={styles.compareSection}>
              <h2>⚖️ Arazi Sınıfları Karşılaştırma Tablosu</h2>
              <p className={styles.sectionDesc}>
                Tüm arazi sınıflarının yapılaşma koşullarını tek bakışta karşılaştırın.
              </p>
              
              <div className={styles.comparisonTable}>
                <table>
                  <thead>
                    <tr>
                      <th>Arazi Sınıfı</th>
                      <th>Emsal (E)</th>
                      <th>Barınma Yapısı</th>
                      <th>Koruma Düzeyi</th>
                      <th>Özellikler</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className={styles.rowMutlak}>
                      <td>
                        <span className={styles.tableEmoji}>🌾</span>
                        <strong>Mutlak Tarım</strong>
                      </td>
                      <td><span className={styles.emsalValue}>0.05-0.20</span></td>
                      <td><span className={styles.alanValue}>75 m²</span></td>
                      <td>
                        <div className={styles.protectionBar}>
                          <div className={styles.protectionFill} style={{width: '95%'}}></div>
                        </div>
                        <span>Çok Yüksek</span>
                      </td>
                      <td>En verimli tarım arazileri</td>
                    </tr>
                    <tr className={styles.rowOzel}>
                      <td>
                        <span className={styles.tableEmoji}>🍇</span>
                        <strong>Özel Ürün</strong>
                      </td>
                      <td><span className={styles.emsalValue}>0.05-0.20</span></td>
                      <td><span className={styles.alanValue}>75-100 m²</span></td>
                      <td>
                        <div className={styles.protectionBar}>
                          <div className={styles.protectionFill} style={{width: '85%'}}></div>
                        </div>
                        <span>Yüksek</span>
                      </td>
                      <td>Özel bitkiler, su ürünleri</td>
                    </tr>
                    <tr className={styles.rowDikili}>
                      <td>
                        <span className={styles.tableEmoji}>🌳</span>
                        <strong>Dikili Tarım</strong>
                      </td>
                      <td><span className={styles.emsalValue}>0.05-0.10</span></td>
                      <td><span className={styles.alanValue}>75-100 m²</span></td>
                      <td>
                        <div className={styles.protectionBar}>
                          <div className={styles.protectionFill} style={{width: '90%'}}></div>
                        </div>
                        <span>Yüksek</span>
                      </td>
                      <td>Çok yıllık bitkiler</td>
                    </tr>
                    <tr className={styles.rowMarjinal}>
                      <td>
                        <span className={styles.tableEmoji}>🏜️</span>
                        <strong>Marjinal Tarım</strong>
                      </td>
                      <td><span className={styles.emsalValue}>0.10-0.30</span></td>
                      <td><span className={styles.alanValue}>150 m²</span></td>
                      <td>
                        <div className={styles.protectionBar}>
                          <div className={styles.protectionFill} style={{width: '60%'}}></div>
                        </div>
                        <span>Orta</span>
                      </td>
                      <td>Geleneksel toprak işlemeli</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Emsal Açıklama */}
              <div className={styles.emsalExplainer}>
                <h4>📐 Emsal (E) Nedir?</h4>
                <p>
                  Emsal, yapı inşaat alanının parsel alanına oranıdır. Örneğin; 10.000 m² 
                  büyüklüğündeki bir parselde E=0.05 emsali için maksimum <strong>500 m²</strong>, 
                  E=0.20 emsali için maksimum <strong>2.000 m²</strong> inşaat yapılabilir.
                </p>
                <div className={styles.emsalExample}>
                  <div className={styles.exampleItem}>
                    <span>10.000 m² parsel</span>
                    <span>×</span>
                    <span>E: 0.05</span>
                    <span>=</span>
                    <span className={styles.result}>500 m² yapı</span>
                  </div>
                  <div className={styles.exampleItem}>
                    <span>10.000 m² parsel</span>
                    <span>×</span>
                    <span>E: 0.20</span>
                    <span>=</span>
                    <span className={styles.result}>2.000 m² yapı</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* BÖLÜM 4: Bölgesel Planlar */}
          {(activeSection === 'regions' || activeSection === 'all') && (
            <div className={styles.planListSection}>
              <h2>📑 Bölgesel Çevre Düzeni Planları</h2>
              <p className={styles.sectionDesc}>
                {searchQuery 
                  ? `"${searchQuery}" araması için ${filteredPlanlar.length} sonuç bulundu.`
                  : `Türkiye genelinde ${planData.planlar.length} farklı çevre düzeni planı mevcuttur.`
                }
              </p>
              
              <div className={styles.planGrid}>
                {filteredPlanlar.map((plan: any) => (
                  <Link 
                    key={plan.id} 
                    href={`/cevre-duzeni-planlari/${plan.id}/`}
                    className={styles.planKart}
                  >
                    <div className={styles.planKartHeader}>
                      <span className={styles.planIcon}>📋</span>
                      <h3>{plan.baslik}</h3>
                    </div>
                    
                    {/* Emsal Özet Bilgisi */}
                    {plan.hukumler && (
                      <div className={styles.emsalOzet}>
                        <div className={styles.emsalMini}>
                          <span className={styles.emsalLabel}>🌾 Mutlak:</span>
                          <span className={styles.emsalDeger}>{plan.hukumler.mutlakTarim?.emsal || '-'}</span>
                        </div>
                        <div className={styles.emsalMini}>
                          <span className={styles.emsalLabel}>🏜️ Marjinal:</span>
                          <span className={styles.emsalDeger}>{plan.hukumler.marjinalTarim?.emsal || '-'}</span>
                        </div>
                      </div>
                    )}
                    
                    {/* Özel Notlar Varsa Göster */}
                    {plan.ozelNotlar && plan.ozelNotlar.length > 0 && (
                      <div className={styles.ozelNotBadge}>
                        <span>⚠️ Özel hükümler mevcut</span>
                      </div>
                    )}
                    
                    <div className={styles.illerListesi}>
                      {plan.iller.map((il: string, idx: number) => (
                        <span key={idx} className={styles.ilBadge}>{il}</span>
                      ))}
                    </div>
                    <div className={styles.planKartFooter}>
                      <span className={styles.ilCount}>{plan.iller.length} il</span>
                      <span className={styles.viewDetails}>Detayları Gör →</span>
                    </div>
                  </Link>
                ))}
              </div>
              
              {filteredPlanlar.length === 0 && (
                <div className={styles.noResults}>
                  <span>🔍</span>
                  <p>"{searchQuery}" için sonuç bulunamadı.</p>
                  <button onClick={() => setSearchQuery('')}>Aramayı Temizle</button>
                </div>
              )}
            </div>
          )}

          {/* İller Listesi (Hızlı Erişim) */}
          <div className={styles.illerQuickAccess}>
            <h3>🏛️ Kapsamdaki Tüm İller ({tumIller.size})</h3>
            <div className={styles.illerGrid}>
              {tumIllerArray.map(il => {
                const planId = ildenPlanBul(il);
                return planId ? (
                  <Link 
                    key={il}
                    href={`/cevre-duzeni-planlari/${planId}/`}
                    className={styles.ilQuickLink}
                  >
                    {il}
                  </Link>
                ) : (
                  <span key={il} className={styles.ilNoLink}>{il}</span>
                );
              })}
            </div>
          </div>

        </div>
      </Layout>
    </>
  );
}
