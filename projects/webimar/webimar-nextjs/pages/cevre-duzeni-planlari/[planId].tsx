import { GetStaticProps, GetStaticPaths } from 'next';
import Head from 'next/head';
import Seo from '../../components/Seo';
import { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import fs from 'fs';
import path from 'path';
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

interface PlanDetayProps {
  plan: typeof planData.planlar[0];
  icerik: string;
}

const PLACEHOLDER_PLAN_ID_VALUES = new Set(['[planId]', '%5BplanId%5D']);

function decodeRouteParam(value: string): string {
  let decodedValue = value;

  for (let index = 0; index < 2; index += 1) {
    try {
      const nextValue = decodeURIComponent(decodedValue);
      if (nextValue === decodedValue) {
        break;
      }
      decodedValue = nextValue;
    } catch {
      break;
    }
  }

  return decodedValue;
}

function isPlaceholderPlanId(value: string): boolean {
  const decodedValue = decodeRouteParam(value);
  return (
    PLACEHOLDER_PLAN_ID_VALUES.has(value) ||
    PLACEHOLDER_PLAN_ID_VALUES.has(decodedValue) ||
    decodedValue.includes('[') ||
    decodedValue.includes(']')
  );
}

// İl adı normalizasyonu
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
function ilPlandaMi(geoJsonIl: string, planIller: string[]): boolean {
  const normalGeoJson = normalizeIlAdi(geoJsonIl);
  return planIller.some(il => normalizeIlAdi(il) === normalGeoJson);
}

export default function PlanDetay({ plan, icerik }: PlanDetayProps) {
  const [mapLoaded, setMapLoaded] = useState(false);
  const [geoData, setGeoData] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setMapLoaded(true);
    }
  }, []);

  // GeoJSON verisi yükle - İl sınırlarını göster (ana sayfa ile aynı)
  useEffect(() => {
    if (mapLoaded && plan) {
      fetch('/turkey-provinces.geojson')
        .then(res => res.json())
        .then(data => {
          // İlleri işle
          const features = data.features.map((feature: any) => {
            const ilAdi = feature.properties.ADM1_TR;
            const isPlanIli = ilPlandaMi(ilAdi, plan.iller);
            
            return {
              ...feature,
              properties: {
                ...feature.properties,
                ilAdi: ilAdi,
                highlighted: isPlanIli
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
  }, [mapLoaded, plan]);

  // Feature style - İl bazında renklendirme (ana sayfa ile aynı)
  const getFeatureStyle = (feature: any) => {
    const isHighlighted = feature?.properties?.highlighted;
    
    return {
      fillColor: isHighlighted ? '#FF6B35' : '#e5e7eb',
      weight: 2,
      opacity: 1,
      color: isHighlighted ? '#d4532a' : '#9ca3af',
      fillOpacity: isHighlighted ? 0.6 : 0.3
    };
  };

  // Feature events
  const onEachFeature = (feature: any, layer: any) => {
    const ilAdi = feature.properties.ilAdi;
    const isHighlighted = feature.properties.highlighted;

    layer.bindTooltip(
      `<strong>${ilAdi}</strong>${isHighlighted ? '<br><span style="color:#FF6B35">Bu plan kapsamında</span>' : ''}`,
      { permanent: false, direction: 'top' }
    );
  };

  // Plan merkezi (harita için)
  const getPlanMerkezi = (): [number, number] => {
    // Bölgelere göre yaklaşık koordinatlar
    const merkezler: Record<string, [number, number]> = {
      'adiyaman-sanliurfa-diyarbakir': [37.5, 39.5],
      'amasya': [40.6, 35.8],
      'antalya-burdur-isparta': [37.0, 31.0],
      'ardahan-kars-igdir-agri': [40.0, 43.5],
      'aydin-mugla-denizli': [37.5, 28.5],
      'balikesir-canakkale': [40.0, 27.5],
      'cankiri-kastamonu-sinop': [41.2, 33.5],
      'corum-samsun-tokat': [40.5, 36.0],
      'edirne-kirklareli-tekirdag': [41.5, 27.0],
      'erzurum-erzincan-bayburt': [40.0, 40.5],
      'izmir-manisa': [38.5, 28.0],
      'kirsehir-nevsehir-aksaray-nigde': [38.5, 34.5],
      'konya-karaman': [37.5, 33.0],
      'malatya-elazig-tunceli-bingol': [39.0, 39.0],
      'mardin-batman-sirnak-siirt-hakkari': [37.5, 42.0],
      'mersin-adana': [37.0, 35.5],
      'mus-bitlis-van': [38.5, 42.5],
      'ordu-giresun-gumushane-trabzon-rize-artvin': [40.8, 39.5],
      'yozgat-sivas-kayseri': [39.5, 36.5],
      'zonguldak-bartin-karabuk': [41.3, 32.5]
    };
    return merkezler[plan.id] || [39.0, 35.0];
  };

  if (!plan) {
    return (
      <Layout>
        <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <h1>Plan bulunamadı</h1>
          <Link href="/cevre-duzeni-planlari/">← Planlara Dön</Link>
        </div>
      </Layout>
    );
  }

  // SEO - Rich Structured Data with Breadcrumb
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Article",
        "@id": `https://tarimimar.com.tr/cevre-duzeni-planlari/${plan.id}#article`,
        "headline": plan.baslik,
        "description": `${plan.baslik} - ${plan.iller.join(', ')} illeri için 1/100.000 ölçekli çevre düzeni planı tarımsal hükümleri ve yapılaşma koşulları`,
        "datePublished": "2025-11-29",
        "dateModified": "2025-11-29",
        "author": {
          "@type": "Organization",
          "name": "Tarım İmar",
          "url": "https://tarimimar.com.tr"
        },
        "publisher": {
          "@type": "Organization",
          "name": "Tarım İmar",
          "url": "https://tarimimar.com.tr",
          "logo": {
            "@type": "ImageObject",
            "url": "https://tarimimar.com.tr/logo.png"
          }
        },
        "mainEntityOfPage": {
          "@type": "WebPage",
          "@id": `https://tarimimar.com.tr/cevre-duzeni-planlari/${plan.id}/`
        },
        "about": {
          "@type": "GovernmentService",
          "name": "Çevre Düzeni Planı",
          "description": `${plan.iller.join(', ')} illeri için tarımsal yapılaşma hükümleri`,
          "areaServed": plan.iller.map(il => ({
            "@type": "AdministrativeArea",
            "name": il,
            "addressCountry": "TR"
          }))
        },
        "keywords": `${plan.iller.join(', ')}, çevre düzeni planı, 1/100.000 ölçekli plan, tarımsal hükümler, yapılaşma koşulları, emsal, tarım arazisi`,
        "inLanguage": "tr-TR",
        "isAccessibleForFree": true
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
          },
          {
            "@type": "ListItem",
            "position": 3,
            "name": plan.baslik,
            "item": `https://tarimimar.com.tr/cevre-duzeni-planlari/${plan.id}/`
          }
        ]
      }
    ]
  };

  // İçeriği bölümlere ayır
  const bolumler = icerik.split(/\n(?=\d+\.\s)/);

  return (
    <>
      <Seo
        title={`${plan.baslik} | Tarımsal Hükümler | Tarım İmar`}
        description={`${plan.baslik} - ${plan.iller.join(', ')} illeri için 1/100.000 ölçekli çevre düzeni planı tarımsal hükümleri ve yapılaşma koşulları`}
        canonical={`https://tarimimar.com.tr/cevre-duzeni-planlari/${plan.id}/`}
        url={`https://tarimimar.com.tr/cevre-duzeni-planlari/${plan.id}/`}
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        jsonLd={structuredData}
        keywords={`${plan.iller.join(', ')}, çevre düzeni planı, tarımsal hükümler, yapılaşma`}
      />

      <Layout>
        <div className={styles.detayContainer}>
          {/* Header */}
          <div className={styles.detayHeader}>
            <Link href="/cevre-duzeni-planlari" className={styles.backButton}>
              ← Tüm Planlar
            </Link>
            <h1>📋 {plan.baslik}</h1>
            
            <div className={styles.illerBadgeContainer}>
              {plan.iller.map((il, idx) => (
                <span key={idx} className={styles.ilBadgeBuyuk}>{il}</span>
              ))}
            </div>
          </div>

          {/* Harita */}
          <div className={styles.mapSection}>
            <h2>📍 Kapsanan İller</h2>
            
            {mapLoaded && geoData ? (
              <>
                <div className={styles.mapContainer} style={{ height: '350px' }}>
                  <MapContainer
                    center={getPlanMerkezi()}
                    zoom={7}
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
                    <span>Plan Kapsamındaki İller</span>
                  </div>
                  <div className={styles.legendItem}>
                    <div className={`${styles.legendColor} ${styles.legendGray}`}></div>
                    <span>Diğer İller</span>
                  </div>
                </div>
              </>
            ) : (
              <div style={{ 
                height: '300px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                background: '#f8f9fa',
                borderRadius: '16px'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>🗺️</div>
                  <div>Harita yükleniyor...</div>
                </div>
              </div>
            )}
          </div>

          {/* İçerik - Bölümler halinde göster */}
          <div className={styles.icerikSection}>
            <h2>📝 Plan Hükümleri (Tarım ile İlgili Kısımlar)</h2>
            <div className={styles.icerikMetin}>
              {renderPlanIcerik(icerik)}
            </div>
          </div>

          {/* Alt navigasyon */}
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <Link href="/cevre-duzeni-planlari/" className={styles.backButton}>
              ← Tüm Planlara Dön
            </Link>
          </div>
        </div>
      </Layout>
    </>
  );
}

// İçeriği bölümlere ayırarak render et
function renderPlanIcerik(icerik: string) {
  // Satırları ayır
  const satirlar = icerik.split('\n');
  const bolumler: { baslik: string; seviye: number; icerik: string[] }[] = [];
  let mevcutBolum: { baslik: string; seviye: number; icerik: string[] } | null = null;

  satirlar.forEach((satir) => {
    const trimmedSatir = satir.trim();
    if (!trimmedSatir) return;
    
    // Ana başlık (ör: "4. TANIMLAR", "7. GENEL HÜKÜMLER")
    const anaBslikRegex = /^(\d+)\.\s+([A-ZÇĞİÖŞÜ\s]+)$/;
    // Alt başlık (ör: "8.7.19. Mutlak Tarım Arazileri")
    const altBaslikRegex = /^(\d+\.)+\s*(.{3,})/;
    
    const anaMatch = trimmedSatir.match(anaBslikRegex);
    const altMatch = trimmedSatir.match(altBaslikRegex);
    
    if (anaMatch) {
      // Ana başlık - yeni ana bölüm
      if (mevcutBolum) bolumler.push(mevcutBolum);
      mevcutBolum = { baslik: trimmedSatir, seviye: 1, icerik: [] };
    } else if (altMatch && trimmedSatir.length < 200) {
      // Alt başlık - kontrol et
      const numParts = altMatch[1].split('.').filter(Boolean).length;
      
      if (numParts <= 2) {
        // Orta seviye başlık (ör: "8.7.", "4.22.")
        if (mevcutBolum) bolumler.push(mevcutBolum);
        mevcutBolum = { baslik: trimmedSatir, seviye: 2, icerik: [] };
      } else if (numParts === 3) {
        // Alt seviye başlık (ör: "8.7.19.")
        if (mevcutBolum) bolumler.push(mevcutBolum);
        mevcutBolum = { baslik: trimmedSatir, seviye: 3, icerik: [] };
      } else {
        // Daha derin seviye - içerik olarak ekle
        if (mevcutBolum) {
          mevcutBolum.icerik.push(trimmedSatir);
        } else {
          mevcutBolum = { baslik: '', seviye: 0, icerik: [trimmedSatir] };
        }
      }
    } else {
      // Normal içerik satırı
      if (mevcutBolum) {
        mevcutBolum.icerik.push(trimmedSatir);
      } else {
        mevcutBolum = { baslik: '', seviye: 0, icerik: [trimmedSatir] };
      }
    }
  });

  // Son bölümü ekle
  if (mevcutBolum) bolumler.push(mevcutBolum);

  // Eğer hiç bölüm bulunamadıysa, düz metin olarak göster
  if (bolumler.length === 0) {
    return <p style={{ whiteSpace: 'pre-wrap' }}>{icerik}</p>;
  }

  return bolumler.map((bolum, index) => (
    <div key={index} className={styles.planBolum}>
      {bolum.baslik && (
        bolum.seviye === 1 ? (
          <h3 style={{ fontSize: '1.4rem', borderBottom: '3px solid #d2691e' }}>{bolum.baslik}</h3>
        ) : bolum.seviye === 2 ? (
          <h3>{bolum.baslik}</h3>
        ) : (
          <h4>{bolum.baslik}</h4>
        )
      )}
      {bolum.icerik.length > 0 && (
        <div>
          {bolum.icerik.map((paragraf, pIndex) => {
            // Numaralı alt madde kontrolü (8.7.19.1. gibi)
            const numaraliMadde = /^(\d+\.)+\s*(.+)/.test(paragraf);
            if (numaraliMadde) {
              return (
                <div key={pIndex} className={styles.planInfo}>
                  <p>{paragraf}</p>
                </div>
              );
            }
            return <p key={pIndex}>{paragraf}</p>;
          })}
        </div>
      )}
    </div>
  ));
}

export const getStaticPaths: GetStaticPaths = async () => {
  const paths = planData.planlar.map((plan) => ({
    params: { planId: plan.id }
  }));

  return {
    paths,
    fallback: false
  };
};

export const getStaticProps: GetStaticProps<PlanDetayProps> = async ({ params }) => {
  const planId = params?.planId as string;

  if (!planId || isPlaceholderPlanId(planId)) {
    return {
      redirect: {
        destination: '/cevre-duzeni-planlari/',
        permanent: true,
      },
    };
  }

  const plan = planData.planlar.find(p => p.id === planId);

  if (!plan) {
    return { notFound: true };
  }

  // txt dosyasını oku
  let icerik = '';
  try {
    // Önce data/100binlik içinden oku (Next.js projesinde)
    const dosyaYolu = path.join(process.cwd(), 'data', '100binlik', plan.dosya);
    icerik = fs.readFileSync(dosyaYolu, 'utf-8');
  } catch (error) {
    console.error('Dosya okuma hatası:', error);
    icerik = 'Plan içeriği yüklenemedi.';
  }

  return {
    props: {
      plan,
      icerik
    }
  };
};
