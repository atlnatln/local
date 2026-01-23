import Head from 'next/head';
import Seo from '../components/Seo';
import { useState, useEffect, useRef, useCallback } from 'react';
import Layout from '../components/Layout';
import { useGA4 } from '../lib/useGA4';
import dynamic from 'next/dynamic';
import Link from 'next/link';

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

// useMap hook'u için dinamik component
const MapController = dynamic(
  () => import('../components/MapController'),
  { ssr: false }
) as any;

// API Base URL
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Türkiye ay isimleri
const MONTHS = [
  'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
];

// Mevsim preset'leri
const SEASON_PRESETS = [
  { name: '🌸 İlkbahar', startMonth: 3, startDay: 21, endMonth: 6, endDay: 20, icon: '🌸', color: '#E91E63' },
  { name: '☀️ Yaz', startMonth: 6, startDay: 21, endMonth: 9, endDay: 22, icon: '☀️', color: '#FF9800' },
  { name: '🍂 Sonbahar', startMonth: 9, startDay: 23, endMonth: 12, endDay: 20, icon: '🍂', color: '#795548' },
  { name: '❄️ Kış', startMonth: 12, startDay: 21, endMonth: 3, endDay: 20, icon: '❄️', color: '#2196F3' },
];

// Tarih formatlama helper - "15 Mayıs" formatında
const formatDate = (day: number, month: number): string => {
  return `${day} ${MONTHS[month - 1]}`;
};

// Popüler bitkiler (hızlı seçim için)
const POPULAR_PLANTS = [
  { name: 'Kestane', emoji: '🌰' },
  { name: 'Kekik', emoji: '🌿' },
  { name: 'Lavanta', emoji: '💜' },
  { name: 'Akasya', emoji: '🌸' },
  { name: 'Ihlamur', emoji: '🍃' },
  { name: 'Ayçiçeği', emoji: '🌻' },
  { name: 'Yonca', emoji: '🍀' },
  { name: 'Narenciye', emoji: '🍊' },
];

// Türkçe karakterleri normalize et (İ->I, Ş->S, Ğ->G, Ü->U, Ö->O, Ç->C)
function normalizeDistrictName(name: string): string {
  return name
    .toUpperCase()
    .replace(/İ/g, 'I')
    .replace(/Ş/g, 'S')
    .replace(/Ğ/g, 'G')
    .replace(/Ü/g, 'U')
    .replace(/Ö/g, 'O')
    .replace(/Ç/g, 'C')
    .replace(/Â/g, 'A')  // Şapkalı A (KÂHTA gibi)
    .replace(/Î/g, 'I')  // Şapkalı I
    .replace(/Û/g, 'U')  // Şapkalı U
    .replace(/\s+/g, '')  // Boşlukları kaldır
    .replace(/[()]/g, '') // Parantezleri kaldır
    .replace(/MERKEZ$/g, '') // Sondaki MERKEZ'i kaldır
    .trim();
}

// Feature'dan isim çıkar - önce ilçe (ADM2), sonra il (ADM1)
function getFeatureName(feature: any): string | null {
  const props = feature?.properties;
  if (!props) return null;
  // Öncelik sırası: İlçe TR > İlçe EN > İl TR > İl EN
  const candidates = ['ADM2_TR', 'ADM2_EN', 'ADM1_TR', 'ADM1_EN', 'Adı', 'ADI', 'name', 'Name'];
  for (const key of candidates) {
    const value = props[key];
    if (typeof value === 'string' && value.trim() && value !== 'Türkiye' && !value.startsWith('TUR')) {
      return value;
    }
  }
  for (const value of Object.values(props)) {
    if (typeof value === 'string' && value.trim() && value !== 'Türkiye' && !value.startsWith('TUR')) {
      return value as string;
    }
  }
  return null;
}

interface PlantInfo {
  plant: string;
  start: [number, number];
  end: [number, number];
  isMatch?: boolean;
}

interface DistrictInfo {
  district: string;
  province?: string;
  plants: PlantInfo[];
}

interface DiversityData {
  districts: {
    province: string;
    district: string;
    diversity: number;
    plants: string[];
  }[];
  max_diversity: number;
  min_diversity: number;
  filtered: boolean;
}

// SEO Structured Data
const structuredData = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Bitki Çiçeklenme Takvimi - Türkiye İlçe Bazlı",
  "description": "Türkiye'nin 973 ilçesinde hangi bitkilerin ne zaman çiçeklendiğini interaktif harita ile keşfedin. Arıcılık, tarım ve doğa gözlemi için ideal kaynak.",
  "url": "https://tarimimar.com.tr/ciceklenme-takvimi/",
  "applicationCategory": "Agriculture, Nature, Reference",
  "operatingSystem": "Web Browser",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "TRY"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Tarım İmar",
    "url": "https://tarimimar.com.tr"
  },
  "about": {
    "@type": "Thing",
    "name": "Bitki Çiçeklenme Takvimi",
    "description": "Türkiye genelinde bitkilerin çiçeklenme dönemlerini gösteren interaktif harita ve takvim sistemi"
  },
  "keywords": "çiçeklenme takvimi, bitki çiçeklenme, Türkiye çiçeklenme haritası, nektar kaynakları, arıcılık takvimi, bal bitkileri, polen takvimi, ilçe bazlı çiçeklenme",
  "inLanguage": "tr",
  "isAccessibleForFree": true
};

export default function CiceklenmeTakvimi() {
  const ga4 = useGA4();
  
  // Info panel state
  const [showInfoPanel, setShowInfoPanel] = useState(false);
  
  // Map state
  const [mapLoaded, setMapLoaded] = useState(false);
  const [geoData, setGeoData] = useState<any>(null);
  const mapRef = useRef<any>(null);
  const [mapInstance, setMapInstance] = useState<any>(null);
  
  // Filter states
  const [filterMode, setFilterMode] = useState<'date' | 'plant' | 'diversity'>('diversity');
  const [startMonth, setStartMonth] = useState(5);
  const [startDay, setStartDay] = useState(1);
  const [endMonth, setEndMonth] = useState(5);
  const [endDay, setEndDay] = useState(31);
  const [plantSearch, setPlantSearch] = useState('');
  
  // Data states
  const [allPlants, setAllPlants] = useState<string[]>([]);
  const [filteredPlants, setFilteredPlants] = useState<string[]>([]);
  const [showPlantSuggestions, setShowPlantSuggestions] = useState(false);
  const [diversityData, setDiversityData] = useState<DiversityData | null>(null);
  const [highlightedDistricts, setHighlightedDistricts] = useState<Set<string>>(new Set());
  const [selectedDistrictInfo, setSelectedDistrictInfo] = useState<DistrictInfo | null>(null);
  
  // Statistics
  const [stats, setStats] = useState<{totalPlants: number; totalDistricts: number; avgDiversity: number} | null>(null);
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultSummary, setResultSummary] = useState<string>('');

  // Leaflet CSS _document.tsx'de global olarak yükleniyor
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setMapLoaded(true);
    }
  }, []);

  // İlk yüklemede tüm bitki listesini ve istatistikleri çek
  useEffect(() => {
    fetch(`${API_BASE}/flowering/plants/`)
      .then(res => res.json())
      .then(data => {
        setAllPlants(data);
        setStats(prev => ({ ...prev, totalPlants: data.length, totalDistricts: prev?.totalDistricts || 973, avgDiversity: prev?.avgDiversity || 0 }));
      })
      .catch(err => console.error('Bitki listesi yüklenemedi:', err));
  }, []);

  // Mevsim preset uygula
  const applySeasonPreset = (preset: typeof SEASON_PRESETS[0]) => {
    setStartMonth(preset.startMonth);
    setStartDay(preset.startDay);
    setEndMonth(preset.endMonth);
    setEndDay(preset.endDay);
    setFilterMode('date');
  };

  // Bitki arama önerileri
  useEffect(() => {
    if (!plantSearch.trim()) {
      setFilteredPlants([]);
      return;
    }
    const lower = plantSearch.toLocaleLowerCase('tr');
    const filtered = allPlants
      .filter(p => p.toLocaleLowerCase('tr').includes(lower))
      .slice(0, 15);
    setFilteredPlants(filtered);
  }, [plantSearch, allPlants]);

  // GeoJSON yükle (Türkiye ilçe sınırları)
  useEffect(() => {
    // Statik GeoJSON dosyası yükle
    fetch('/turkey-districts.geojson')
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => {
        console.error('GeoJSON yüklenemedi:', err);
        setError('Harita verisi yüklenemedi. Lütfen turkey-districts.geojson dosyasını public klasörüne ekleyin.');
      });
  }, []);

  // Tarih filtresi
  const onDateFilter = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResultSummary('');
    try {
      const url = `${API_BASE}/flowering/flowering-districts/?start_month=${startMonth}&start_day=${startDay}&end_month=${endMonth}&end_day=${endDay}`;
      const res = await fetch(url);
      const data = await res.json();
      
      const districtNames = new Set<string>(data.districts.map((d: any) => normalizeDistrictName(d.district)));
      setHighlightedDistricts(districtNames);
      setDiversityData(null);
      setResultSummary(`${formatDate(startDay, startMonth)} - ${formatDate(endDay, endMonth)} arasında ${data.count} ilçede çiçeklenme var.`);
      
      ga4.trackEvent('flowering_date_filter', {
        start_date: `${startMonth}/${startDay}`,
        end_date: `${endMonth}/${endDay}`,
        result_count: data.count
      });
    } catch (err) {
      setError('Veriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  }, [startMonth, startDay, endMonth, endDay, ga4]);

  // Bitki filtresi
  const onPlantFilter = useCallback(async () => {
    if (!plantSearch.trim()) {
      setError('Bitki adı girin');
      return;
    }
    setLoading(true);
    setError(null);
    setResultSummary('');
    try {
      const url = `${API_BASE}/flowering/plant-districts/?plant=${encodeURIComponent(plantSearch)}`;
      const res = await fetch(url);
      const data = await res.json();
      
      const districtNames = new Set<string>(data.districts.map((d: any) => normalizeDistrictName(d.district)));
      setHighlightedDistricts(districtNames);
      setDiversityData(null);
      setResultSummary(`"${plantSearch}" bitkisi ${data.count} ilçede yetişiyor.`);
      
      ga4.trackEvent('flowering_plant_filter', {
        plant: plantSearch,
        result_count: data.count
      });
    } catch (err) {
      setError('Veriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  }, [plantSearch, ga4]);

  // Çeşitlilik haritası
  const onDiversityFilter = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResultSummary('');
    try {
      const url = `${API_BASE}/flowering/district-diversity/`;
      const res = await fetch(url);
      const data = await res.json();
      
      setDiversityData(data);
      setHighlightedDistricts(new Set());
      
      // İstatistik hesapla
      const totalDiversity = data.districts.reduce((acc: number, d: any) => acc + d.diversity, 0);
      const avgDiv = Math.round(totalDiversity / data.districts.length);
      setStats(prev => ({ ...prev, totalPlants: prev?.totalPlants || 0, totalDistricts: data.districts.length, avgDiversity: avgDiv }));
      setResultSummary(`${data.districts.length} ilçe analiz edildi. En zengin ilçe: ${data.max_diversity} bitki türü.`);
      
      ga4.trackEvent('flowering_diversity_map', {
        max_diversity: data.max_diversity,
        min_diversity: data.min_diversity
      });
    } catch (err) {
      setError('Veriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  }, [ga4]);

  // İlçeye tıklama
  const onDistrictClick = useCallback(async (feature: any) => {
    const districtName = getFeatureName(feature);
    if (!districtName) return;
    
    try {
      // Tarih filtresi modundaysak, tarih parametrelerini de gönder
      let url = `${API_BASE}/flowering/district-plants/?district=${encodeURIComponent(districtName)}`;
      
      if (filterMode === 'date') {
        url += `&start_month=${startMonth}&start_day=${startDay}&end_month=${endMonth}&end_day=${endDay}`;
      }
      
      const res = await fetch(url);
      const data = await res.json();
      
      if (data && data.plants) {
        let plantsToShow = data.plants;
        
        // Bitki arama modundaysak, aranan bitkiyi vurgula
        if (filterMode === 'plant' && plantSearch.trim()) {
          const lowerSearch = plantSearch.toLocaleLowerCase('tr');
          plantsToShow = plantsToShow.map((p: PlantInfo) => ({
            ...p,
            isMatch: p.plant.toLocaleLowerCase('tr').includes(lowerSearch)
          }));
          // Eşleşenleri başa al
          plantsToShow.sort((a: PlantInfo, b: PlantInfo) => {
            if (a.isMatch && !b.isMatch) return -1;
            if (!a.isMatch && b.isMatch) return 1;
            return 0;
          });
        }
        
        setSelectedDistrictInfo({
          district: data.district || districtName,
          province: data.province,
          plants: plantsToShow
        });
      } else {
        setSelectedDistrictInfo({
          district: districtName,
          plants: []
        });
      }
    } catch (err) {
      console.error('İlçe bilgisi alınamadı:', err);
      setSelectedDistrictInfo({
        district: districtName,
        plants: []
      });
    }
  }, [filterMode, plantSearch, startMonth, startDay, endMonth, endDay]);

  // GeoJSON stil fonksiyonu
  const getStyle = useCallback((feature: any) => {
    const name = getFeatureName(feature);
    const nameNormalized = name ? normalizeDistrictName(name) : '';
    
    // Çeşitlilik haritası modu
    if (diversityData) {
      const districtData = diversityData.districts.find(
        d => normalizeDistrictName(d.district) === nameNormalized
      );
      
      if (!districtData || districtData.diversity === 0) {
        return {
          fillColor: '#cccccc',
          fillOpacity: 0.3,
          color: '#999',
          weight: 1,
          dashArray: '3, 3'
        };
      }
      
      const { max_diversity, min_diversity } = diversityData;
      const range = max_diversity - min_diversity;
      const normalizedValue = range > 0 ? (districtData.diversity - min_diversity) / range : 0;
      const ratio = Math.sqrt(normalizedValue);
      
      let r, g, b;
      if (ratio < 0.5) {
        r = Math.floor(50 + ratio * 2 * 205);
        g = Math.floor(50 + ratio * 2 * 205);
        b = Math.floor(255 - ratio * 2 * 255);
      } else {
        r = 255;
        g = Math.floor((1 - (ratio - 0.5) * 2) * 255);
        b = 0;
      }
      
      return {
        fillColor: `rgb(${r},${g},${b})`,
        fillOpacity: 0.8,
        color: '#555',
        weight: 1
      };
    }
    
    // Vurgulu ilçeler
    if (highlightedDistricts.has(nameNormalized)) {
      return {
        fillColor: '#ffeb3b',
        fillOpacity: 0.6,
        color: '#ffcc00',
        weight: 3
      };
    }
    
    // Varsayılan stil
    return {
      fillColor: '#3388ff',
      fillOpacity: 0.12,
      color: '#3388ff',
      weight: 1
    };
  }, [diversityData, highlightedDistricts]);

  return (
    <Layout>
      <Seo 
        title="Bitki Çiçeklenme Takvimi - Türkiye İlçe Bazlı Harita | Tarımİmar"
        description="Türkiye'nin 973 ilçesinde hangi bitkilerin ne zaman çiçeklendiğini interaktif harita ile keşfedin. Arıcılık, tarım ve doğa gözlemi için ideal kaynak. Kestane, kekik, lavanta ve 500+ bitki türü."
        canonical="https://tarimimar.com.tr/ciceklenme-takvimi/"
        url="https://tarimimar.com.tr/ciceklenme-takvimi/"
        ogImage="https://tarimimar.com.tr/og-ciceklenme-takvimi.svg"
        type="website"
        jsonLd={structuredData}
        keywords="çiçeklenme takvimi, bitki çiçeklenme, Türkiye çiçeklenme haritası, nektar kaynakları, arıcılık takvimi, bal bitkileri, polen takvimi, ilçe bazlı çiçeklenme, kestane çiçeklenme, kekik çiçeklenme, lavanta çiçeklenme"
      />
      <Head>
        {/* Leaflet CSS _document.tsx'de global olarak yükleniyor */}
        <meta name="geo.placename" content="Türkiye" />
        <meta name="geo.region" content="TR" />
        <meta name="content-language" content="tr" />
        <meta name="subject" content="Bitki Çiçeklenme Takvimi ve Haritası" />
        <meta name="classification" content="Tarım, Arıcılık, Botanik" />
        <style>{`
          /* Mobil Uyumluluk - Tablet ve Mobil */
          @media (max-width: 1024px) {
            .ciceklenme-container {
              flex-direction: column !important;
            }
            .ciceklenme-sidebar {
              width: 100% !important;
              max-height: 50vh !important;
              padding: 16px !important;
            }
            .ciceklenme-map-area {
              height: 50vh !important;
              min-height: 350px !important;
            }
          }
          
          @media (max-width: 768px) {
            .ciceklenme-container {
              flex-direction: column !important;
              height: auto !important;
              min-height: 100vh !important;
            }
            .ciceklenme-sidebar {
              width: 100% !important;
              max-height: none !important;
              height: auto !important;
              padding: 12px !important;
              order: 1 !important;
            }
            .ciceklenme-sidebar h2 {
              font-size: 18px !important;
            }
            .ciceklenme-sidebar p {
              font-size: 12px !important;
            }
            .ciceklenme-map-area {
              width: 100% !important;
              height: 350px !important;
              min-height: 350px !important;
              max-height: 350px !important;
              flex: 0 0 350px !important;
              order: 2 !important;
            }
          }
          
          @media (max-width: 480px) {
            .ciceklenme-sidebar {
              padding: 10px !important;
            }
            .ciceklenme-sidebar h2 {
              font-size: 16px !important;
            }
            .ciceklenme-sidebar select,
            .ciceklenme-sidebar input,
            .ciceklenme-sidebar button {
              font-size: 14px !important;
              padding: 10px !important;
            }
            .ciceklenme-map-area {
              height: 300px !important;
              min-height: 300px !important;
              max-height: 300px !important;
              flex: 0 0 300px !important;
            }
          }
          
          /* İlçe Bilgi Popup Mobil */
          @media (max-width: 768px) {
            [style*="position: absolute"][style*="top: '20px'"][style*="right: '20px'"] {
              top: 10px !important;
              right: 10px !important;
              left: 10px !important;
              max-width: none !important;
              width: auto !important;
            }
          }
          
          /* İstatistik kartları mobil */
          @media (max-width: 480px) {
            [style*="grid-template-columns: repeat(3, 1fr)"] {
              grid-template-columns: repeat(3, 1fr) !important;
              gap: 6px !important;
            }
            [style*="grid-template-columns: repeat(3, 1fr)"] > div {
              padding: 8px 4px !important;
            }
            [style*="grid-template-columns: repeat(3, 1fr)"] > div > div:first-child {
              font-size: 14px !important;
            }
            [style*="grid-template-columns: repeat(3, 1fr)"] > div > div:last-child {
              font-size: 9px !important;
            }
          }
          
          /* Touch-friendly butonlar */
          @media (max-width: 768px) {
            button {
              min-height: 44px !important;
              touch-action: manipulation;
            }
            select, input {
              min-height: 44px !important;
            }
          }
          
          /* Popüler bitkiler scroll */
          @media (max-width: 480px) {
            [style*="flexWrap: 'wrap'"] {
              flex-wrap: nowrap !important;
              overflow-x: auto !important;
              padding-bottom: 8px !important;
              -webkit-overflow-scrolling: touch;
            }
          }
        `}</style>
      </Head>
      
      <div className="ciceklenme-container" style={{ display: 'flex', height: 'calc(100vh - 60px)', flexDirection: 'row' }}>
        {/* Sol Panel */}
        <div className="ciceklenme-sidebar" style={{
          width: '360px',
          padding: '20px',
          background: 'linear-gradient(180deg, #fff 0%, #f8faf8 100%)',
          boxShadow: '2px 0 12px rgba(0,0,0,0.08)',
          overflowY: 'auto',
          flexShrink: 0
        }}>
          <h2 style={{ marginTop: 0, marginBottom: '8px', fontSize: '22px', color: '#2E7D32', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🌸 Çiçeklenme Takvimi
          </h2>
          
          <p style={{ fontSize: '13px', color: '#555', marginBottom: '16px', lineHeight: '1.5' }}>
            Türkiye&apos;nin tüm ilçelerinde bitki çiçeklenme dönemlerini interaktif harita ile keşfedin.
          </p>
          
          {/* Arıcılık Planlama Link Banner */}
          <Link href="/aricilik-planlama" style={{ textDecoration: 'none' }}>
            <div style={{
              padding: '12px 16px',
              marginBottom: '16px',
              background: 'linear-gradient(135deg, #FFF8E1, #FFECB3)',
              borderRadius: '10px',
              border: '1px solid #FFD54F',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{ fontSize: '28px' }}>🐝</span>
              <div>
                <div style={{ fontWeight: 'bold', color: '#E65100', fontSize: '14px' }}>
                  Arıcılık Rota Planlama
                </div>
                <div style={{ fontSize: '11px', color: '#795548' }}>
                  Bal çeşidine göre en iyi bölgeleri keşfedin →
                </div>
              </div>
            </div>
          </Link>
          
          {/* Bilgi Butonu */}
          <button
            onClick={() => setShowInfoPanel(!showInfoPanel)}
            style={{
              width: '100%',
              padding: '10px 14px',
              marginBottom: '16px',
              background: showInfoPanel ? 'linear-gradient(135deg, #FF9800, #F57C00)' : 'linear-gradient(135deg, #4CAF50, #388E3C)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
              transition: 'all 0.3s'
            }}
          >
            {showInfoPanel ? '📖 Bilgi Panelini Kapat' : '📚 Çiçeklenme Hakkında Bilgi'}
          </button>
          
          {/* Bilgi Paneli */}
          {showInfoPanel && (
            <div style={{
              marginBottom: '20px',
              padding: '16px',
              background: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
              borderRadius: '12px',
              border: '1px solid #A5D6A7',
              fontSize: '12px',
              lineHeight: '1.7',
              color: '#2E7D32',
              maxHeight: '350px',
              overflowY: 'auto'
            }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1B5E20', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🌿 Çiçeklenme Takvimi Nedir?
              </h3>
              <p style={{ marginBottom: '12px' }}>
                Çiçeklenme takvimi, bitkilerin <strong>nektar ve polen ürettiği dönemleri</strong> gösteren bir rehberdir. 
                Arıcılar, çiftçiler ve doğa gözlemcileri için vazgeçilmez bir kaynaktır.
              </p>
              
              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#2E7D32' }}>
                🌡️ Çiçeklenmeyi Etkileyen Faktörler
              </h4>
              <ul style={{ margin: '0 0 12px 0', paddingLeft: '20px' }}>
                <li>Hava sıcaklığı ve güneş ışığı</li>
                <li>Yağış miktarı ve toprak nemi</li>
                <li>Rakım ve coğrafi konum</li>
                <li>Bitki türü ve çeşidi</li>
              </ul>
              
              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#2E7D32' }}>
                🍯 Arıcılık İçin Önemi
              </h4>
              <p style={{ marginBottom: '12px' }}>
                Gezginci arıcılar, çiçeklenme takvimini kullanarak <strong>kovanlarını en verimli bölgelere</strong> taşır. 
                Doğru zamanda doğru yerde olmak, bal verimini %40&apos;a kadar artırabilir.
              </p>
              
              <div style={{
                marginTop: '12px',
                padding: '10px',
                background: '#fff',
                borderRadius: '8px',
                border: '1px solid #81c784'
              }}>
                <p style={{ margin: 0, fontSize: '11px', color: '#2E7D32' }}>
                  <strong>💡 İpucu:</strong> Haritada bir ilçeye tıklayarak o bölgedeki tüm bitkileri ve çiçeklenme dönemlerini görebilirsiniz.
                </p>
              </div>
            </div>
          )}
          
          {/* İstatistik Kartları */}
          {stats && (
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(3, 1fr)', 
              gap: '8px', 
              marginBottom: '16px' 
            }}>
              <div style={{
                padding: '10px 8px',
                background: 'linear-gradient(135deg, #E3F2FD, #BBDEFB)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1565C0' }}>
                  {stats.totalPlants || '500+'}
                </div>
                <div style={{ fontSize: '10px', color: '#1976D2' }}>Bitki Türü</div>
              </div>
              <div style={{
                padding: '10px 8px',
                background: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2E7D32' }}>
                  {stats.totalDistricts || 973}
                </div>
                <div style={{ fontSize: '10px', color: '#388E3C' }}>İlçe</div>
              </div>
              <div style={{
                padding: '10px 8px',
                background: 'linear-gradient(135deg, #FFF3E0, #FFE0B2)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#E65100' }}>
                  {stats.avgDiversity || '~15'}
                </div>
                <div style={{ fontSize: '10px', color: '#F57C00' }}>Ort. Çeşitlilik</div>
              </div>
            </div>
          )}
          
          {/* Filtreleme Modu */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontWeight: 'bold', fontSize: '14px', display: 'block', marginBottom: '8px', color: '#333' }}>
              🔍 Filtreleme Modu
            </label>
            <select 
              value={filterMode} 
              onChange={(e) => setFilterMode(e.target.value as any)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontSize: '14px',
                cursor: 'pointer',
                background: '#fff'
              }}
            >
              <option value="diversity">🗺️ Çeşitlilik Haritası</option>
              <option value="date">📅 Tarih Aralığı</option>
              <option value="plant">🌿 Bitki Ara</option>
            </select>
          </div>
          
          {/* Tarih Filtresi */}
          {filterMode === 'date' && (
            <div style={{ marginBottom: '16px' }}>
              {/* Mevsim Hızlı Seçim */}
              <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '8px', color: '#333' }}>
                🗓️ Hızlı Seçim (Mevsim)
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                {SEASON_PRESETS.map((preset) => (
                  <button
                    key={preset.name}
                    onClick={() => applySeasonPreset(preset)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '16px',
                      border: `1px solid ${preset.color}`,
                      background: '#fff',
                      fontSize: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      color: preset.color
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = preset.color;
                      (e.currentTarget as HTMLElement).style.color = 'white';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = '#fff';
                      (e.currentTarget as HTMLElement).style.color = preset.color;
                    }}
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
              
              <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '8px' }}>
                📅 Başlangıç Tarihi
              </label>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                <input
                  type="number"
                  min="1"
                  max="31"
                  value={startDay}
                  onChange={(e) => setStartDay(Number(e.target.value))}
                  style={{ width: '65px', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', textAlign: 'center' }}
                />
                <select
                  value={startMonth}
                  onChange={(e) => setStartMonth(Number(e.target.value))}
                  style={{ flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid #ddd' }}
                >
                  {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
                </select>
              </div>
              
              <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '8px' }}>
                📅 Bitiş Tarihi
              </label>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <input
                  type="number"
                  min="1"
                  max="31"
                  value={endDay}
                  onChange={(e) => setEndDay(Number(e.target.value))}
                  style={{ width: '65px', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', textAlign: 'center' }}
                />
                <select
                  value={endMonth}
                  onChange={(e) => setEndMonth(Number(e.target.value))}
                  style={{ flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid #ddd' }}
                >
                  {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
                </select>
              </div>
              
              <button
                onClick={onDateFilter}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: loading ? '#ccc' : 'linear-gradient(135deg, #4CAF50, #388E3C)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: loading ? 'wait' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                {loading ? '⏳ Yükleniyor...' : '🔍 Filtrele'}
              </button>
            </div>
          )}
          
          {/* Bitki Filtresi */}
          {filterMode === 'plant' && (
            <div style={{ marginBottom: '16px', position: 'relative' }}>
              {/* Popüler Bitkiler */}
              <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '8px', color: '#333' }}>
                ⭐ Popüler Bitkiler
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                {POPULAR_PLANTS.map((plant) => (
                  <button
                    key={plant.name}
                    onClick={() => {
                      setPlantSearch(plant.name);
                    }}
                    style={{
                      padding: '5px 10px',
                      borderRadius: '16px',
                      border: plantSearch.toLowerCase() === plant.name.toLowerCase() 
                        ? '2px solid #4CAF50' 
                        : '1px solid #ddd',
                      background: plantSearch.toLowerCase() === plant.name.toLowerCase() 
                        ? '#E8F5E9' 
                        : '#fff',
                      fontSize: '11px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <span>{plant.emoji}</span>
                    <span>{plant.name}</span>
                  </button>
                ))}
              </div>
              
              <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '8px' }}>
                🌿 Bitki Adı
              </label>
              <input
                type="text"
                value={plantSearch}
                onChange={(e) => {
                  setPlantSearch(e.target.value);
                  setShowPlantSuggestions(true);
                }}
                onFocus={() => setShowPlantSuggestions(true)}
                onBlur={() => setTimeout(() => setShowPlantSuggestions(false), 200)}
                placeholder="Örn: kekik, lavanta, kestane..."
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '2px solid #ddd',
                  marginBottom: '8px',
                  boxSizing: 'border-box',
                  fontSize: '14px'
                }}
              />
              
              {/* Öneri Listesi */}
              {showPlantSuggestions && filteredPlants.length > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '165px',
                  left: 0,
                  right: 0,
                  background: 'white',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                  zIndex: 1000,
                  maxHeight: '200px',
                  overflowY: 'auto',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                }}>
                  {filteredPlants.map(p => (
                    <div
                      key={p}
                      onClick={() => {
                        setPlantSearch(p);
                        setShowPlantSuggestions(false);
                      }}
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        borderBottom: '1px solid #f0f0f0',
                        fontSize: '13px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                      onMouseEnter={(e) => (e.currentTarget as HTMLElement).style.background = '#f5f5f5'}
                      onMouseLeave={(e) => (e.currentTarget as HTMLElement).style.background = 'white'}
                    >
                      <span>🌱</span> {p}
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={onPlantFilter}
                disabled={loading || !plantSearch.trim()}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: loading || !plantSearch.trim() ? '#ccc' : 'linear-gradient(135deg, #2196F3, #1976D2)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: loading || !plantSearch.trim() ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                {loading ? '⏳ Yükleniyor...' : '🔍 Ara'}
              </button>
            </div>
          )}
          
          {/* Çeşitlilik Haritası */}
          {filterMode === 'diversity' && (
            <div style={{ marginBottom: '16px' }}>
              <p style={{ fontSize: '12px', color: '#666', marginBottom: '12px', lineHeight: '1.6' }}>
                İlçelerdeki <strong>bitki çeşitliliğini</strong> renkli harita olarak gösterir. 
                Sıcak renkler (kırmızı) yüksek çeşitliliği, soğuk renkler (mavi) düşük çeşitliliği temsil eder.
              </p>
              
              <button
                onClick={onDiversityFilter}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: loading ? '#ccc' : 'linear-gradient(135deg, #4CAF50, #388E3C)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: loading ? 'wait' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                {loading ? '⏳ Yükleniyor...' : '🗺️ Haritayı Göster'}
              </button>
              
              {diversityData && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{
                    fontSize: '12px',
                    padding: '12px',
                    background: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    border: '1px solid #A5D6A7'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span>En zengin ilçe:</span>
                      <strong style={{ color: '#2E7D32' }}>{diversityData.max_diversity} bitki</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>En az çeşitlilik:</span>
                      <strong style={{ color: '#1565C0' }}>{diversityData.min_diversity} bitki</strong>
                    </div>
                  </div>
                  
                  {/* Renk Lejantı */}
                  <div style={{
                    padding: '12px',
                    background: '#fff',
                    border: '1px solid #ddd',
                    borderRadius: '8px'
                  }}>
                    <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '10px', color: '#333' }}>
                      🎨 Renk Lejantı
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '30px', height: '16px', background: '#cccccc', border: '1px dashed #999', borderRadius: '3px' }}></div>
                        <span style={{ fontSize: '11px' }}>Veri yok</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '30px', height: '16px', background: 'rgb(50,50,255)', borderRadius: '3px' }}></div>
                        <span style={{ fontSize: '11px' }}>Az çeşitlilik (1-10)</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '30px', height: '16px', background: 'rgb(255,255,0)', borderRadius: '3px' }}></div>
                        <span style={{ fontSize: '11px' }}>Orta çeşitlilik (10-25)</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '30px', height: '16px', background: 'rgb(255,0,0)', borderRadius: '3px' }}></div>
                        <span style={{ fontSize: '11px' }}>Yüksek çeşitlilik (25+)</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Sonuç Özeti */}
          {resultSummary && (
            <div style={{
              padding: '12px',
              background: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
              color: '#2E7D32',
              borderRadius: '8px',
              fontSize: '13px',
              marginBottom: '16px',
              border: '1px solid #81C784',
              fontWeight: '500'
            }}>
              ✅ {resultSummary}
            </div>
          )}
          
          {/* Hata Mesajı */}
          {error && (
            <div style={{
              padding: '12px',
              background: '#ffebee',
              color: '#c62828',
              borderRadius: '8px',
              fontSize: '13px',
              marginBottom: '16px',
              border: '1px solid #ef9a9a'
            }}>
              ⚠️ {error}
            </div>
          )}
          
          {/* Temizle Butonu */}
          <button
            onClick={() => {
              setHighlightedDistricts(new Set());
              setDiversityData(null);
              setSelectedDistrictInfo(null);
              setError(null);
              setResultSummary('');
              setPlantSearch('');
            }}
            style={{
              width: '100%',
              padding: '10px',
              background: '#f5f5f5',
              color: '#666',
              border: '1px solid #ddd',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '13px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#e0e0e0';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#f5f5f5';
            }}
          >
            🗑️ Temizle
          </button>
          
          {/* Alt Bilgi - İlgili Sayfalar */}
          <div style={{
            marginTop: '20px',
            padding: '14px',
            background: '#f9f9f9',
            borderRadius: '8px',
            border: '1px solid #e0e0e0'
          }}>
            <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: '10px', color: '#333' }}>
              📎 İlgili Sayfalar
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Link href="/aricilik-planlama" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 10px',
                background: '#fff',
                borderRadius: '6px',
                textDecoration: 'none',
                color: '#1976D2',
                fontSize: '12px',
                border: '1px solid #e0e0e0',
                transition: 'all 0.2s'
              }}>
                <span>🐝</span>
                <span>Arıcılık Konaklama Planlama</span>
              </Link>
              <Link href="/aricilik" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 10px',
                background: '#fff',
                borderRadius: '6px',
                textDecoration: 'none',
                color: '#1976D2',
                fontSize: '12px',
                border: '1px solid #e0e0e0',
                transition: 'all 0.2s'
              }}>
                <span>🏠</span>
                <span>Arıcılık Tesisi Hesaplama</span>
              </Link>
            </div>
          </div>
        </div>
        
        {/* Harita */}
        <div className="ciceklenme-map-area" style={{ flex: 1, position: 'relative', minHeight: '400px' }}>
          {mapLoaded && (
            <MapContainer
              center={[39, 35]}
              zoom={typeof window !== 'undefined' && window.innerWidth < 768 ? 5 : 6}
              style={{ height: '100%', width: '100%' }}
              ref={mapRef}
            >
              <MapController onMapReady={(map: any) => {
                if (!mapInstance) {
                  mapRef.current = map;
                  setMapInstance(map);
                }
              }} />
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {geoData && (
                <GeoJSON
                  key={`geo-${highlightedDistricts.size}-${diversityData?.max_diversity || 0}`}
                  data={geoData}
                  style={getStyle}
                  eventHandlers={{
                    click: (e: any) => onDistrictClick(e.layer.feature)
                  }}
                />
              )}
            </MapContainer>
          )}
          
          {/* İlçe Bilgi Popup */}
          {selectedDistrictInfo && (
            <div style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              background: 'white',
              padding: '20px',
              borderRadius: '12px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
              maxWidth: '320px',
              maxHeight: '80vh',
              overflow: 'auto',
              zIndex: 1000
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '16px'
              }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '18px', color: '#2E7D32' }}>
                    📍 {selectedDistrictInfo.district}
                  </h3>
                  {selectedDistrictInfo.province && (
                    <span style={{ fontSize: '13px', color: '#666' }}>
                      {selectedDistrictInfo.province}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setSelectedDistrictInfo(null)}
                  style={{
                    background: '#f5f5f5',
                    border: 'none',
                    fontSize: '18px',
                    cursor: 'pointer',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    lineHeight: 1
                  }}
                >
                  ×
                </button>
              </div>
              
              {selectedDistrictInfo.plants.length > 0 ? (
                <div>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '12px',
                    padding: '8px 12px',
                    background: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
                    borderRadius: '6px'
                  }}>
                    <span style={{ fontSize: '12px', color: '#2E7D32' }}>
                      🌿 Toplam bitki türü:
                    </span>
                    <strong style={{ color: '#1B5E20', fontSize: '14px' }}>
                      {selectedDistrictInfo.plants.length}
                    </strong>
                  </div>
                  <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                    {selectedDistrictInfo.plants.map((p, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: '10px 12px',
                          marginBottom: '8px',
                          background: p.isMatch 
                            ? 'linear-gradient(135deg, #FFF9C4, #FFF59D)' 
                            : '#f9f9f9',
                          border: p.isMatch ? '2px solid #FBC02D' : '1px solid #e0e0e0',
                          borderRadius: '8px',
                          fontSize: '12px'
                        }}
                      >
                        <div style={{ 
                          fontWeight: 'bold', 
                          marginBottom: '6px', 
                          color: p.isMatch ? '#F57F17' : '#333',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}>
                          {p.isMatch && <span>⭐</span>}
                          🌱 {p.plant}
                        </div>
                        <div style={{ 
                          fontSize: '11px', 
                          color: '#666',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          background: '#fff',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          width: 'fit-content'
                        }}>
                          📅 {formatDate(p.start[1], p.start[0])} → {formatDate(p.end[1], p.end[0])}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div style={{
                  padding: '20px',
                  textAlign: 'center',
                  color: '#999'
                }}>
                  <div style={{ fontSize: '32px', marginBottom: '8px' }}>🌿</div>
                  <p style={{ fontSize: '13px', margin: 0 }}>
                    Bu ilçe için bitki verisi bulunamadı.
                  </p>
                </div>
              )}
            </div>
          )}
          
          {/* Başlangıç durumu - harita boşken */}
          {!geoData && !loading && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              background: 'rgba(255,255,255,0.95)',
              padding: '30px 40px',
              borderRadius: '16px',
              textAlign: 'center',
              boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
              maxWidth: '400px',
              zIndex: 1000
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
              <h3 style={{ margin: '0 0 12px 0', color: '#2E7D32', fontSize: '20px' }}>
                Harita Yükleniyor...
              </h3>
              <p style={{ color: '#666', fontSize: '14px', lineHeight: '1.6', margin: 0 }}>
                Türkiye ilçe haritası hazırlanıyor. Lütfen bekleyin.
              </p>
            </div>
          )}
          
          {/* Loading overlay */}
          {loading && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(255,255,255,0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}>
              <div style={{
                background: 'white',
                padding: '30px 50px',
                borderRadius: '16px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px', animation: 'pulse 1.5s infinite' }}>🌸</div>
                <div style={{ color: '#2E7D32', fontWeight: 'bold', fontSize: '16px' }}>
                  Veriler yükleniyor...
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
      `}</style>
    </Layout>
  );
}
