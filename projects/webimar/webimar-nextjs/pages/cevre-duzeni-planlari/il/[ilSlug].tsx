import { GetStaticProps, GetStaticPaths } from 'next';
import Seo from '../../../components/Seo';
import Layout from '../../../components/Layout';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import styles from '../../../styles/CevreDuzeniPlanlari.module.css';
import planData from '../../../data/cevre-duzeni-planlari.json';

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

// İl verisi tipi
interface IlData {
  ilAdi: string;
  ilSlug: string;
  plan: typeof planData.planlar[0];
  komsuIller: string[];
}

const PLACEHOLDER_IL_SLUG_VALUES = new Set(['[ilSlug]', '%5BilSlug%5D']);

// Slug normalize (Unicode birleşik karakterleri ve Türkçe harfleri sadeleştir)
function normalizeSlugValue(value: string): string {
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
}

// İl adından slug oluştur
function createSlug(ilAdi: string): string {
  return normalizeSlugValue(ilAdi);
}

function decodeLegacySlug(value: string): string {
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

function isPlaceholderIlSlug(value: string): boolean {
  const decodedValue = decodeLegacySlug(value);
  return (
    PLACEHOLDER_IL_SLUG_VALUES.has(value) ||
    PLACEHOLDER_IL_SLUG_VALUES.has(decodedValue) ||
    decodedValue.includes('[') ||
    decodedValue.includes(']')
  );
}

// Tüm illeri ve planlarını eşleştir
function getTumIller(): IlData[] {
  const iller: IlData[] = [];
  
  planData.planlar.forEach(plan => {
    plan.iller.forEach(il => {
      const komsuIller = plan.iller.filter(k => k !== il);
      iller.push({
        ilAdi: il,
        ilSlug: createSlug(il),
        plan: plan,
        komsuIller: komsuIller
      });
    });
  });
  
  return iller;
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

interface IlSayfasiProps {
  ilData: IlData;
}

export default function IlSayfasi({ ilData }: IlSayfasiProps) {
  const [mapLoaded, setMapLoaded] = useState(false);
  const [geoData, setGeoData] = useState<any>(null);
  
  const { ilAdi, plan, komsuIller } = ilData;
  const ortakHukumler = planData.ortakHukumler;

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setMapLoaded(true);
    }
  }, []);

  // GeoJSON verisi yükle - İl sınırlarını kullan (ana sayfa ile aynı)
  useEffect(() => {
    if (mapLoaded) {
      fetch('/turkey-provinces.geojson')
        .then(res => res.json())
        .then(data => {
          const features = data.features.map((feature: any) => {
            const geoIlAdi = feature.properties.ADM1_TR;
            const isCurrentIl = normalizeIlAdi(geoIlAdi) === normalizeIlAdi(ilAdi);
            const isKomsu = komsuIller.some(k => normalizeIlAdi(k) === normalizeIlAdi(geoIlAdi));
            
            return {
              ...feature,
              properties: {
                ...feature.properties,
                ilAdi: geoIlAdi,
                isCurrentIl,
                isKomsu
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
  }, [mapLoaded, ilAdi, komsuIller]);

  // Feature style - İl sınırları (ana sayfa ile tutarlı)
  const getFeatureStyle = (feature: any) => {
    const isCurrentIl = feature?.properties?.isCurrentIl;
    const isKomsu = feature?.properties?.isKomsu;
    
    if (isCurrentIl) {
      return {
        fillColor: '#FF6B35',
        weight: 2,
        opacity: 1,
        color: '#d4532a',
        fillOpacity: 0.6
      };
    }
    if (isKomsu) {
      return {
        fillColor: '#FFB088',
        weight: 2,
        opacity: 1,
        color: '#d4532a',
        fillOpacity: 0.4
      };
    }
    return {
      fillColor: '#e5e7eb',
      weight: 2,
      opacity: 1,
      color: '#9ca3af',
      fillOpacity: 0.3
    };
  };

  // İl merkezi koordinatları (yaklaşık)
  const ilKoordinatlari: Record<string, [number, number]> = {
    'ADIYAMAN': [37.76, 38.28], 'ŞANLIURFA': [37.16, 38.79], 'DİYARBAKIR': [37.91, 40.21],
    'AMASYA': [40.65, 35.83], 'ANTALYA': [36.88, 30.70], 'BURDUR': [37.72, 30.29],
    'ISPARTA': [37.76, 30.55], 'ARDAHAN': [41.11, 42.70], 'KARS': [40.60, 43.09],
    'IĞDIR': [39.92, 44.04], 'AĞRI': [39.72, 43.05], 'AYDIN': [37.85, 27.85],
    'MUĞLA': [37.21, 28.36], 'DENİZLİ': [37.77, 29.09], 'BALIKESİR': [39.65, 27.88],
    'ÇANAKKALE': [40.15, 26.41], 'ÇANKIRI': [40.60, 33.62], 'KASTAMONU': [41.38, 33.78],
    'SİNOP': [42.03, 35.15], 'ÇORUM': [40.55, 34.96], 'SAMSUN': [41.29, 36.33],
    'TOKAT': [40.31, 36.55], 'EDİRNE': [41.68, 26.56], 'KIRKLARELİ': [41.73, 27.22],
    'TEKİRDAĞ': [41.00, 27.52], 'ERZURUM': [39.90, 41.27], 'ERZİNCAN': [39.75, 39.49],
    'BAYBURT': [40.26, 40.23], 'İZMİR': [38.42, 27.13], 'MANİSA': [38.61, 27.43],
    'KIRŞEHİR': [39.15, 34.16], 'NEVŞEHİR': [38.62, 34.71], 'AKSARAY': [38.37, 34.03],
    'NİĞDE': [37.97, 34.69], 'KONYA': [37.87, 32.48], 'KARAMAN': [37.18, 33.23],
    'MALATYA': [38.35, 38.31], 'ELAZIĞ': [38.67, 39.22], 'TUNCELİ': [39.11, 39.55],
    'BİNGÖL': [38.88, 40.50], 'MARDİN': [37.31, 40.73], 'BATMAN': [37.89, 41.13],
    'ŞIRNAK': [37.52, 42.46], 'SİİRT': [37.93, 41.94], 'HAKKARİ': [37.58, 43.74],
    'MERSİN': [36.80, 34.64], 'ADANA': [37.00, 35.32], 'MUŞ': [38.74, 41.49],
    'BİTLİS': [38.40, 42.11], 'VAN': [38.49, 43.38], 'ORDU': [40.98, 37.88],
    'GİRESUN': [40.91, 38.39], 'GÜMÜŞHANE': [40.46, 39.48], 'TRABZON': [41.00, 39.73],
    'RİZE': [41.02, 40.52], 'ARTVİN': [41.18, 41.82], 'YOZGAT': [39.82, 34.80],
    'SİVAS': [39.75, 37.01], 'KAYSERİ': [38.73, 35.48], 'ZONGULDAK': [41.45, 31.79],
    'BARTIN': [41.63, 32.34], 'KARABÜK': [41.20, 32.63]
  };

  const merkez = ilKoordinatlari[ilAdi] || [39.0, 35.0];

  // SEO Structured Data
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebPage",
        "@id": `https://tarimimar.com.tr/cevre-duzeni-planlari/il/${ilData.ilSlug}#page`,
        "name": `${ilAdi} İli Çevre Düzeni Planı Tarımsal Hükümleri`,
        "description": `${ilAdi} ili için geçerli 1/100.000 ölçekli çevre düzeni planı tarımsal hükümleri, yapılaşma koşulları ve emsal değerleri. ${plan.baslik} kapsamındadır.`,
        "url": `https://tarimimar.com.tr/cevre-duzeni-planlari/il/${ilData.ilSlug}/`,
        "isPartOf": {
          "@type": "WebPage",
          "@id": `https://tarimimar.com.tr/cevre-duzeni-planlari/${plan.id}/`,
          "name": plan.baslik
        },
        "about": {
          "@type": "AdministrativeArea",
          "name": ilAdi,
          "addressCountry": "TR"
        },
        "datePublished": "2025-11-29",
        "dateModified": "2025-11-29",
        "inLanguage": "tr-TR"
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
            "name": ilAdi,
            "item": `https://tarimimar.com.tr/cevre-duzeni-planlari/il/${ilData.ilSlug}/`
          }
        ]
      },
      {
        "@type": "FAQPage",
        "mainEntity": [
          {
            "@type": "Question",
            "name": `${ilAdi}'da mutlak tarım arazisinde emsal ne kadar?`,
            "acceptedAnswer": {
              "@type": "Answer",
              "text": `${ilAdi} ilinde mutlak tarım arazilerinde emsal (E) ${ortakHukumler.tarimArazileriSiniflari.mutlakTarim.genelEmsal} arasındadır. Çiftçinin barınabileceği yapı emsale dahil olup inşaat alanı ${ortakHukumler.tarimArazileriSiniflari.mutlakTarim.genelBarinma}'yi geçemez.`
            }
          },
          {
            "@type": "Question",
            "name": `${ilAdi}'da marjinal tarım arazisinde yapılaşma koşulları nelerdir?`,
            "acceptedAnswer": {
              "@type": "Answer",
              "text": `${ilAdi} ilinde marjinal tarım arazilerinde emsal (E) ${ortakHukumler.tarimArazileriSiniflari.marjinalTarim.genelEmsal} arasındadır. Çiftçinin barınabileceği yapının inşaat alanı ${ortakHukumler.tarimArazileriSiniflari.marjinalTarim.genelBarinma}'yi geçemez.`
            }
          },
          {
            "@type": "Question",
            "name": `${ilAdi} hangi çevre düzeni planı kapsamında?`,
            "acceptedAnswer": {
              "@type": "Answer",
              "text": `${ilAdi} ili, ${plan.baslik} kapsamındadır. Bu planlama bölgesinde ${plan.iller.join(', ')} illeri yer almaktadır.`
            }
          }
        ]
      }
    ]
  };

  return (
    <>
      <Seo
        title={`${ilAdi} Çevre Düzeni Planı | Tarımsal Yapılaşma Koşulları | Tarım İmar`}
        description={`${ilAdi} ili için 1/100.000 ölçekli çevre düzeni planı tarımsal hükümleri. Mutlak tarım, marjinal tarım ve dikili tarım arazilerinde emsal değerleri ve yapılaşma koşulları.`}
        canonical={`https://tarimimar.com.tr/cevre-duzeni-planlari/il/${ilData.ilSlug}/`}
        url={`https://tarimimar.com.tr/cevre-duzeni-planlari/il/${ilData.ilSlug}/`}
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        jsonLd={structuredData}
        keywords={`${ilAdi}, çevre düzeni planı, tarımsal hükümler, emsal, mutlak tarım arazisi, yapılaşma koşulları, ${ilAdi} tarım`}
      />

      <Layout>
        <div className={styles.ilContainer}>
          {/* Header */}
          <div className={styles.ilHeader}>
            <Link href="/cevre-duzeni-planlari" className={styles.backButton}>
              ← Tüm Planlar
            </Link>
            
            <h1>🏛️ {ilAdi} İli Çevre Düzeni Planı</h1>
            <p className={styles.ilAciklama}>
              {ilAdi} ili için geçerli tarımsal yapılaşma hükümleri ve emsal değerleri
            </p>
          </div>

          {/* Plan Bilgisi */}
          <div className={styles.planBilgisi}>
            <div className={styles.planKartBuyuk}>
              <div className={styles.planIcon}>📋</div>
              <div className={styles.planDetay}>
                <h2>{plan.baslik}</h2>
                <p>{ilAdi} ili bu planlama bölgesi kapsamındadır.</p>
                
                {komsuIller.length > 0 && (
                  <div className={styles.komsuIller}>
                    <span>Aynı plandaki diğer iller:</span>
                    <div className={styles.komsuBadgeContainer}>
                      {komsuIller.map((il, idx) => (
                        <Link 
                          key={idx} 
                          href={`/cevre-duzeni-planlari/il/${createSlug(il)}/`}
                          className={styles.komsuBadge}
                        >
                          {il}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                <Link href={`/cevre-duzeni-planlari/${plan.id}`} className={styles.planDetayLink}>
                  📖 Tam Plan Hükümlerini Görüntüle →
                </Link>
              </div>
            </div>
          </div>

          {/* Harita */}
          <div className={styles.mapSection}>
            <h2>📍 {ilAdi} Konumu</h2>
            
            {mapLoaded && geoData ? (
              <>
                <div className={styles.mapContainer} style={{ height: '350px' }}>
                  <MapContainer
                    center={merkez}
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
                    />
                  </MapContainer>
                </div>
                
                <div className={styles.mapLegend}>
                  <div className={styles.legendItem}>
                    <div className={`${styles.legendColor} ${styles.legendOrange}`}></div>
                    <span>{ilAdi}</span>
                  </div>
                  {komsuIller.length > 0 && (
                    <div className={styles.legendItem}>
                      <div className={`${styles.legendColor} ${styles.legendLightOrange}`}></div>
                      <span>Aynı Plandaki Diğer İller</span>
                    </div>
                  )}
                  <div className={styles.legendItem}>
                    <div className={`${styles.legendColor} ${styles.legendGray}`}></div>
                    <span>Diğer İller</span>
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

          {/* Yapılaşma Koşulları */}
          <div className={styles.yapiKosullari}>
            <h2>🏗️ {ilAdi}'da Tarım Arazilerinde Yapılaşma Koşulları</h2>
            
            <div className={styles.araziGrid}>
              <div className={styles.araziKart}>
                <h3>🌾 Mutlak Tarım Arazisi</h3>
                <p>{ortakHukumler.tarimArazileriSiniflari.mutlakTarim.tanim}</p>
                <div className={styles.araziDeger}>
                  <span>Emsal: {ortakHukumler.tarimArazileriSiniflari.mutlakTarim.genelEmsal}</span>
                  <span>Barınma: {ortakHukumler.tarimArazileriSiniflari.mutlakTarim.genelBarinma}</span>
                </div>
              </div>

              <div className={styles.araziKart}>
                <h3>🌿 Özel Ürün Arazisi</h3>
                <p>{ortakHukumler.tarimArazileriSiniflari.ozelUrun.tanim}</p>
                <div className={styles.araziDeger}>
                  <span>Emsal: {ortakHukumler.tarimArazileriSiniflari.ozelUrun.genelEmsal}</span>
                  <span>Barınma: {ortakHukumler.tarimArazileriSiniflari.ozelUrun.genelBarinma}</span>
                </div>
              </div>

              <div className={styles.araziKart}>
                <h3>🌳 Dikili Tarım Arazisi</h3>
                <p>{ortakHukumler.tarimArazileriSiniflari.dikiliTarim.tanim}</p>
                <div className={styles.araziDeger}>
                  <span>Emsal: {ortakHukumler.tarimArazileriSiniflari.dikiliTarim.genelEmsal}</span>
                  <span>Barınma: {ortakHukumler.tarimArazileriSiniflari.dikiliTarim.genelBarinma}</span>
                </div>
              </div>

              <div className={styles.araziKart}>
                <h3>🏜️ Marjinal Tarım Arazisi</h3>
                <p>{ortakHukumler.tarimArazileriSiniflari.marjinalTarim.tanim}</p>
                <div className={styles.araziDeger}>
                  <span>Emsal: {ortakHukumler.tarimArazileriSiniflari.marjinalTarim.genelEmsal}</span>
                  <span>Barınma: {ortakHukumler.tarimArazileriSiniflari.marjinalTarim.genelBarinma}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Genel Kurallar */}
          <div className={styles.genelKurallar}>
            <h2>⚖️ {ilAdi}'da Geçerli Genel Kurallar</h2>
            <ul>
              {ortakHukumler.ortakKurallar.map((kural, idx) => (
                <li key={idx}>✓ {kural}</li>
              ))}
            </ul>
          </div>

          {/* CTA */}
          <div className={styles.ctaSection}>
            <h3>📖 Detaylı Plan Hükümlerini İnceleyin</h3>
            <p>
              {ilAdi} ili için geçerli tüm tarımsal hükümleri, özel durumları ve 
              istisnai kuralları görmek için bölgesel plan sayfasını ziyaret edin.
            </p>
            <Link href={`/cevre-duzeni-planlari/${plan.id}`} className={styles.ctaButton}>
              {plan.baslik} Hükümlerini Görüntüle →
            </Link>
          </div>

          {/* Alt navigasyon */}
          <div className={styles.altNav}>
            <Link href="/cevre-duzeni-planlari" className={styles.backButton}>
              ← Tüm Çevre Düzeni Planları
            </Link>
          </div>
        </div>
      </Layout>
    </>
  );
}

export const getStaticPaths: GetStaticPaths = async () => {
  const tumIller = getTumIller();
  
  const paths = tumIller.map((il) => ({
    params: { ilSlug: il.ilSlug }
  }));

  return {
    paths,
    fallback: 'blocking'
  };
};

export const getStaticProps: GetStaticProps<IlSayfasiProps> = async ({ params }: { params?: { ilSlug?: string } }) => {
  const ilSlug = params?.ilSlug as string;

  if (!ilSlug || isPlaceholderIlSlug(ilSlug)) {
    return {
      redirect: {
        destination: `/cevre-duzeni-planlari/`,
        permanent: true
      }
    };
  }

  const decodedSlug = decodeLegacySlug(ilSlug);
  const normalizedSlug = normalizeSlugValue(decodedSlug);
  const tumIller = getTumIller();
  
  const ilData = tumIller.find(il => il.ilSlug === normalizedSlug);

  if (!ilData) {
    return { notFound: true };
  }

  if (ilData.ilSlug !== ilSlug) {
    return {
      redirect: {
        destination: `/cevre-duzeni-planlari/il/${ilData.ilSlug}/`,
        permanent: true
      }
    };
  }

  return {
    props: {
      ilData
    }
  };
};
