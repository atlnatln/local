import Head from 'next/head';
import Seo from '../components/Seo';
import { useState, useEffect, useRef, useCallback } from 'react';
import Layout from '../components/Layout';
import { useGA4 } from '../lib/useGA4';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import DebouncedInput from '../components/DebouncedInput';

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

// Tarih formatlama helper - "15 Mayıs" formatında
const formatDate = (day: number, month: number): string => {
  return `${day} ${MONTHS[month - 1]}`;
};

// Tarih aralığı formatlama - "15 Mayıs → 30 Haziran" formatında  
const formatDateRange = (startDay: number, startMonth: number, endDay: number, endMonth: number): string => {
  return `${formatDate(startDay, startMonth)} → ${formatDate(endDay, endMonth)}`;
};

// Bal çeşitleri (bal_cesitleri.json'dan unique türler)
const HONEY_TYPES = [
  'AYÇİÇEĞİ', 'NARENCİYE', 'PAMUK', 'GEVEN', 'PÜREN', 'ÇİÇEK', 
  'SÜTLEĞEN', 'KEKİK', 'ANASON', 'ÜÇGÜL', 'YONCA', 'AKASYA',
  'KEÇİBOYNUZU', 'ÇAM', 'KESTANE', 'IHLAMUR', 'ORMAN GÜLÜ',
  'HAYIT', 'LAVANTA', 'KARAÇALI', 'KANOLA', 'MEŞE', 'SANDAL'
].sort();

// Mevsim preset'leri
const SEASON_PRESETS = [
  { name: '🌸 İlkbahar', startMonth: 3, startDay: 21, endMonth: 6, endDay: 20 },
  { name: '☀️ Yaz', startMonth: 6, startDay: 21, endMonth: 9, endDay: 22 },
  { name: '🍂 Sonbahar', startMonth: 9, startDay: 23, endMonth: 12, endDay: 20 },
  { name: '❄️ Kış', startMonth: 12, startDay: 21, endMonth: 3, endDay: 20 },
];

// Feature'dan isim çıkar
function getFeatureName(feature: any): string | null {
  const props = feature?.properties;
  if (!props) return null;
  const candidates = ['ADM2_TR', 'ADM2_EN', 'ADM1_TR', 'ADM1_EN', 'Adı', 'ADI', 'name', 'Name'];
  for (const key of candidates) {
    const value = props[key];
    if (typeof value === 'string' && value.trim() && value !== 'Türkiye' && !value.startsWith('TUR')) {
      return value;
    }
  }
  return null;
}

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

// İki ilçe ismini karşılaştır (normalize ederek)
function matchDistrictNames(name1: string, name2: string): boolean {
  const n1 = normalizeDistrictName(name1);
  const n2 = normalizeDistrictName(name2);
  // Tam eşleşme veya biri diğerinin başında/sonunda yer almalı
  // "includes" kullanmak yerine daha sıkı kontrol yapıyoruz
  return n1 === n2;
}

// İl ve ilçe birlikte eşleştirme (MERKEZ gibi aynı isimli ilçeler için)
function matchDistrictWithProvince(district1: string, province1: string, district2: string, province2: string): boolean {
  const d1 = normalizeDistrictName(district1);
  const d2 = normalizeDistrictName(district2);
  const p1 = normalizeDistrictName(province1);
  const p2 = normalizeDistrictName(province2);
  return d1 === d2 && p1 === p2;
}

interface PlantInfo {
  plant: string;
  start: [number, number];
  end: [number, number];
  overlap_type?: 'full' | 'partial' | 'minimal' | 'none';
  overlap_percentage?: number;
  warning?: string;
}

interface BeekeepingPlan {
  plan_number: number;
  province: string;
  district: string;
  target_plants: PlantInfo[];
  all_plants?: PlantInfo[];
  diversity_score: number;
  honey_power?: number;
  avg_overlap?: number;
  combined_score?: number;
  recommendation_reason: string;
}

interface DistrictSummary {
  province: string;
  district: string;
  honey_power: number;
  avg_overlap: number;
  diversity_score: number;
  combined_score: number;
  target_plant_count: number;
}

interface BeekeepingResponse {
  success: boolean;
  honey_type?: string;
  date_range?: {
    start: string;
    end: string;
  };
  total_matching_districts?: number;
  plans?: BeekeepingPlan[];
  all_districts?: DistrictSummary[];
  message?: string;
}

export default function AricilikPlanlama() {
  const ga4 = useGA4();
  
  // Info panel state
  const [showInfoPanel, setShowInfoPanel] = useState(false);
  
  // Map state
  const [mapLoaded, setMapLoaded] = useState(false);
  const [geoData, setGeoData] = useState<any>(null);
  const mapRef = useRef<any>(null);
  const [mapInstance, setMapInstance] = useState<any>(null);
  const [hoveredDistrict, setHoveredDistrict] = useState<string | null>(null);
  const [zoomedDistrict, setZoomedDistrict] = useState<string | null>(null); // Hangi ilçeye zoom yapıldığını takip et
  
  // Form states
  const [selectedHoneyType, setSelectedHoneyType] = useState('KESTANE');
  const [startMonth, setStartMonth] = useState(6);
  const [startDay, setStartDay] = useState(1);
  const [endMonth, setEndMonth] = useState(7);
  const [endDay, setEndDay] = useState(31);
  
  // Result states
  const [plans, setPlans] = useState<BeekeepingPlan[]>([]);
  const [allDistricts, setAllDistricts] = useState<DistrictSummary[]>([]);
  const [totalMatchingDistricts, setTotalMatchingDistricts] = useState(0);
  const [selectedPlan, setSelectedPlan] = useState<BeekeepingPlan | null>(null);
  const [highlightedDistricts, setHighlightedDistricts] = useState<Set<string>>(new Set());
  const [topPlanDistricts, setTopPlanDistricts] = useState<Set<string>>(new Set()); // Top 4 plan ilçeleri (mavi renkte gösterilecek)
  
  // Modal states
  const [showAllDistrictsModal, setShowAllDistrictsModal] = useState(false);
  const [showAllPlantsModal, setShowAllPlantsModal] = useState(false);
  const [showOnlyTopPlans, setShowOnlyTopPlans] = useState(true); // Başlangıçta sadece önerilen planlar gösterilsin
  const [honeyPowerTooltip, setHoneyPowerTooltip] = useState<{show: boolean; power: number; x: number; y: number}>({show: false, power: 0, x: 0, y: 0});
  const [selectedDistrictFromModal, setSelectedDistrictFromModal] = useState<DistrictSummary | null>(null);
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultSummary, setResultSummary] = useState<string>('');

  // SEO Structured Data for Beekeeping Planning Page
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Gezginci Arıcılık Konaklama Planlama Sistemi",
    "description": "Türkiye genelinde bitkilerin çiçeklenme zamanına göre arıcılık rotası planlayın. İlçe ilçe çiçeklenme takvimi ve interaktif Türkiye çiçeklenme haritası.",
    "url": "https://tarimimar.com.tr/aricilik-planlama/",
    "applicationCategory": "Agriculture",
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
      "name": "Gezginci Arıcılık",
      "description": "Kovanların bir yerden başka bir yere taşınarak farklı bitkilerin çiçeklenme dönemlerinden faydalanma yöntemi"
    },
    "keywords": "gezginci arıcılık, çiçeklenme takvimi, bal üretim rotası, arıcılık planlama, Türkiye çiçeklenme haritası, nektar kaynakları, konaklama planlama",
    "inLanguage": "tr",
    "isAccessibleForFree": true
  };

  // Leaflet CSS _document.tsx'de global olarak yükleniyor
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setMapLoaded(true);
    }
  }, []);

  // GeoJSON yükle
  useEffect(() => {
    fetch('/turkey-districts.geojson')
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => {
        console.error('GeoJSON yüklenemedi:', err);
        setError('Harita verisi yüklenemedi.');
      });
  }, []);

  // Mevsim preset uygula
  const applySeasonPreset = (preset: typeof SEASON_PRESETS[0]) => {
    setStartMonth(preset.startMonth);
    setStartDay(preset.startDay);
    setEndMonth(preset.endMonth);
    setEndDay(preset.endDay);
  };

  // Plan temizle
  const clearPlan = () => {
    setPlans([]);
    setAllDistricts([]);
    setTotalMatchingDistricts(0);
    setSelectedPlan(null);
    setHighlightedDistricts(new Set());
    setResultSummary('');
    setError(null);
    setShowAllDistrictsModal(false);
    setShowAllPlantsModal(false);
  };

  // Plan oluştur
  const generatePlan = useCallback(async () => {
    setLoading(true);
    setError(null);
    setPlans([]);
    setAllDistricts([]);
    setTotalMatchingDistricts(0);
    setSelectedPlan(null);
    setHighlightedDistricts(new Set());
    setResultSummary('');
    
    try {
      const response = await fetch(`${API_BASE}/flowering/beekeeping-plan/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          honey_type: selectedHoneyType,
          start_month: startMonth,
          start_day: startDay,
          end_month: endMonth,
          end_day: endDay,
          include_all: true  // Tüm bölgeleri al
        })
      });
      
      const data: BeekeepingResponse = await response.json();
      
      if (data.success && data.plans && data.plans.length > 0) {
        setPlans(data.plans);
        setAllDistricts(data.all_districts || []);
        setTotalMatchingDistricts(data.total_matching_districts || 0);
        setResultSummary(
          `${data.honey_type} balı için ${data.total_matching_districts} uygun bölge bulundu. ` +
          `En iyi ${data.plans.length} plan hazırlandı.`
        );
        
        // Top 4 plan ilçeleri (kırmızı renkte gösterilecek)
        // GeoJSON'da merkez ilçeler il adıyla kayıtlı - "MERKEZ" → il adına dönüştür
        const topPlanKeys = new Set<string>(
          data.plans.map(p => {
            const districtName = p.district.toUpperCase() === 'MERKEZ' ? p.province : p.district;
            return `${normalizeDistrictName(districtName)}|${normalizeDistrictName(p.province)}`;
          })
        );
        setTopPlanDistricts(topPlanKeys);
        setShowOnlyTopPlans(true); // Başlangıçta sadece önerilen planları göster
        
        // Tüm uygun bölgeler (yeşil/sarı renkte gösterilecek)
        const allDistrictKeys = new Set<string>(
          (data.all_districts || []).map(d => {
            const districtName = d.district.toUpperCase() === 'MERKEZ' ? d.province : d.district;
            return `${normalizeDistrictName(districtName)}|${normalizeDistrictName(d.province)}`;
          })
        );
        setHighlightedDistricts(allDistrictKeys);
        setSelectedPlan(data.plans[0]);
        
        ga4.trackEvent('beekeeping_plan_generated', {
          honey_type: selectedHoneyType,
          date_range: `${startDay}/${startMonth} - ${endDay}/${endMonth}`,
          plans_count: data.plans.length
        });
      } else {
        setError(
          `${selectedHoneyType} balı için seçtiğiniz tarih aralığında (${startDay}/${startMonth} - ${endDay}/${endMonth}) uygun bölge bulunamadı. ` +
          `Farklı bir tarih aralığı veya bal çeşidi deneyebilirsiniz.`
        );
        ga4.trackEvent('beekeeping_plan_no_result', {
          honey_type: selectedHoneyType
        });
      }
    } catch (err) {
      console.error('Plan oluşturma hatası:', err);
      setError('Plan oluşturulurken hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  }, [selectedHoneyType, startMonth, startDay, endMonth, endDay, ga4]);

  // GeoJSON stil fonksiyonu
  const getStyle = useCallback((feature: any) => {
    const name = getFeatureName(feature);
    const nameNormalized = name ? normalizeDistrictName(name) : '';
    
    // GeoJSON'dan il bilgisini al
    const props = feature?.properties || {};
    const geoProvince = props.ADM1_TR || props.ADM1_EN || props.il || '';
    const geoProvinceNormalized = geoProvince ? normalizeDistrictName(geoProvince) : '';
    
    // Zoom yapılan ilçe - il+ilçe kombinasyonu ile kontrol
    // zoomedDistrict formatı: "ILCE|IL" veya sadece "ILCE"
    // GeoJSON'da merkez ilçeler il adıyla kayıtlı
    if (zoomedDistrict && name) {
      const [zoomedDistrictName, zoomedProvinceName] = zoomedDistrict.split('|');
      // "MERKEZ" → il adına dönüştür
      const effectiveZoomedDistrict = (zoomedDistrictName.toUpperCase() === 'MERKEZ' && zoomedProvinceName)
        ? zoomedProvinceName
        : zoomedDistrictName;
      const isZoomed = matchDistrictNames(effectiveZoomedDistrict, name) &&
        (!zoomedProvinceName || matchDistrictNames(zoomedProvinceName, geoProvince));
      
      if (isZoomed) {
        return {
          fillColor: 'transparent',
          fillOpacity: 0,
          color: '#FF5722',
          weight: 4,
          dashArray: '5, 10'
        };
      }
    }
    
    // Hover durumu
    if (hoveredDistrict && matchDistrictNames(hoveredDistrict, name || '')) {
      return {
        fillColor: '#FF5722',
        fillOpacity: 0.6,
        color: '#E64A19',
        weight: 3
      };
    }
    
    // Seçili plan - il+ilçe kombinasyonu ile kontrol
    // GeoJSON'da merkez ilçeler il adıyla kayıtlı
    if (selectedPlan && name) {
      const selectedDistrictName = selectedPlan.district.toUpperCase() === 'MERKEZ' 
        ? selectedPlan.province 
        : selectedPlan.district;
      const isSelected = matchDistrictNames(selectedDistrictName, name) &&
        matchDistrictNames(selectedPlan.province, geoProvince);
      
      if (isSelected) {
        return {
          fillColor: '#4CAF50',
          fillOpacity: 0.7,
          color: '#2E7D32',
          weight: 3
        };
      }
    }
    
    // Vurgulu ilçeler - il+ilçe kombinasyonu ile karşılaştır
    const featureKey = geoProvinceNormalized ? `${nameNormalized}|${geoProvinceNormalized}` : nameNormalized;
    
    // Top 4 plan ilçeleri - kırmızı renkte
    if (topPlanDistricts.has(featureKey)) {
      return {
        fillColor: '#F44336',
        fillOpacity: 0.6,
        color: '#C62828',
        weight: 2.5
      };
    }
    
    // Diğer uygun bölgeler - yeşil/sarı renkte (sadece showOnlyTopPlans false ise göster)
    if (!showOnlyTopPlans && highlightedDistricts.has(featureKey)) {
      return {
        fillColor: '#FFD700',
        fillOpacity: 0.5,
        color: '#FFA500',
        weight: 2
      };
    }
    
    // Varsayılan
    return {
      fillColor: '#3388ff',
      fillOpacity: 0.1,
      color: '#3388ff',
      weight: 1
    };
  }, [selectedPlan, highlightedDistricts, topPlanDistricts, hoveredDistrict, zoomedDistrict, showOnlyTopPlans]);

  // İlçeye tıklama
  const onDistrictClick = useCallback((feature: any) => {
    const districtName = getFeatureName(feature);
    if (!districtName) return;
    
    const plan = plans.find(
      p => matchDistrictNames(p.district, districtName)
    );
    
    if (plan) {
      setSelectedPlan(plan);
    }
  }, [plans]);

  // İlçe hover - sadece planlanan ilçelerde tooltip göster (performans için)
  const onEachFeature = useCallback((feature: any, layer: any) => {
    const name = getFeatureName(feature);
    if (name) {
      const nameNormalized = normalizeDistrictName(name);
      const isPlannedDistrict = highlightedDistricts.has(nameNormalized);
      
      layer.on({
        mouseover: () => {
          // Sadece planlanan ilçelerde hover efekti ve tooltip
          if (isPlannedDistrict) {
            setHoveredDistrict(name);
            layer.bindTooltip(name, { permanent: false, direction: 'auto' }).openTooltip();
          }
        },
        mouseout: () => {
          if (isPlannedDistrict) {
            setHoveredDistrict(null);
            layer.closeTooltip();
          }
        }
      });
    }
  }, [highlightedDistricts]);

  // Türkiye'nin tamamını göster (zoom out)
  const resetMapView = useCallback(() => {
    if (!mapInstance) return;
    // Harita hazır mı kontrol et
    try {
      // Türkiye'nin orta noktası ve varsayılan zoom
      mapInstance.setView([39, 35], 6, { animate: true, duration: 0.5 });
      setZoomedDistrict(null);
    } catch (error) {
      console.log('resetMapView: Harita henüz hazır değil', error);
      // Harita hazır değilse sadece state'i temizle
      setZoomedDistrict(null);
    }
  }, [mapInstance]);

  // Tüm highlighted bölgeleri kapsayacak şekilde zoom yap
  const fitAllHighlightedDistricts = useCallback(() => {
    if (!mapInstance || !geoData || highlightedDistricts.size === 0) {
      console.log('fitAllHighlightedDistricts: Gerekli veriler yok');
      return;
    }
    
    try {
      const L = (window as any).L;
      if (!L) return;
      
      // Tüm highlighted bölgelerin bounds'larını birleştir
      let combinedBounds: any = null;
      
      geoData.features.forEach((feature: any) => {
        const props = feature?.properties || {};
        const name = props.ADM2_TR || props.ADM2_EN || props.name || props.NAME;
        const geoProvince = props.ADM1_TR || props.ADM1_EN || props.il || '';
        
        if (!name) return;
        
        const nameNormalized = normalizeDistrictName(name);
        const geoProvinceNormalized = normalizeDistrictName(geoProvince);
        const featureKey = geoProvinceNormalized ? `${nameNormalized}|${geoProvinceNormalized}` : nameNormalized;
        
        // Bu feature highlighted districts içinde mi?
        if (highlightedDistricts.has(featureKey)) {
          const layer = L.geoJSON(feature);
          const bounds = layer.getBounds();
          
          if (!combinedBounds) {
            combinedBounds = bounds;
          } else {
            combinedBounds.extend(bounds);
          }
        }
      });
      
      if (combinedBounds) {
        console.log('fitAllHighlightedDistricts: Tüm bölgelere zoom yapılıyor');
        mapInstance.fitBounds(combinedBounds, {
          padding: [30, 30],
          maxZoom: 8,
          animate: true,
          duration: 0.5
        });
        setZoomedDistrict(null);
        setSelectedPlan(null); // Seçili planı temizle
      }
    } catch (error) {
      console.log('fitAllHighlightedDistricts: Hata', error);
      // Hata olursa en azından zoom out yap
      resetMapView();
    }
  }, [mapInstance, geoData, highlightedDistricts, resetMapView]);

  // İlçeye zoom yap (toggle: aynı ilçeye tekrar basınca zoom out yap)
  // provinceName opsiyonel - aynı isimli ilçeleri ayırt etmek için kullanılır (örn: MERKEZ)
  const zoomToDistrict = useCallback((districtName: string, provinceName?: string) => {
    if (!mapInstance || !geoData) {
      console.log('zoomToDistrict: mapInstance veya geoData yok', { mapInstance: !!mapInstance, geoData: !!geoData });
      return;
    }
    
    // GeoJSON'da merkez ilçeler il adıyla kayıtlı (örn: BOLU, ZONGULDAK)
    // API'den gelen "MERKEZ" → GeoJSON'daki il adına dönüştür
    const effectiveDistrictName = (districtName.toUpperCase() === 'MERKEZ' && provinceName) 
      ? provinceName 
      : districtName;
    
    // Zoom için benzersiz key oluştur (il varsa il+ilçe, yoksa sadece ilçe)
    const zoomKey = provinceName ? `${districtName}|${provinceName}` : districtName;
    
    // Aynı ilçeye tekrar tıklandıysa, zoom out yap
    if (zoomedDistrict && zoomedDistrict === zoomKey) {
      console.log('Aynı ilçeye tıklandı, zoom out yapılıyor');
      resetMapView();
      return;
    }
    
    console.log('zoomToDistrict çağrıldı:', districtName, provinceName ? `(${provinceName})` : '', '→ effective:', effectiveDistrictName);
    
    // GeoJSON'dan ilçeyi bul - il bilgisi varsa onu da kullan
    const districtFeature = geoData.features.find((f: any) => {
      const name = getFeatureName(f);
      if (!name) return false;
      
      // İlçe adı eşleşmeli (effectiveDistrictName kullan)
      if (!matchDistrictNames(name, effectiveDistrictName)) return false;
      
      // İl bilgisi varsa, GeoJSON'daki il bilgisini de kontrol et
      if (provinceName) {
        const props = f.properties || {};
        const geoProvince = props.ADM1_TR || props.ADM1_EN || props.il || '';
        return matchDistrictNames(geoProvince, provinceName);
      }
      
      return true;
    });
    
    if (districtFeature && districtFeature.geometry) {
      const L = (window as any).L;
      if (L) {
        try {
          const layer = L.geoJSON(districtFeature);
          const bounds = layer.getBounds();
          console.log('fitBounds çağrılıyor:', districtName, provinceName || '', bounds);
          // animate: true ve duration ekleyerek smooth zoom sağla
          mapInstance.fitBounds(bounds, { 
            padding: [50, 50], 
            maxZoom: 10,
            animate: true,
            duration: 0.5
          });
          setZoomedDistrict(zoomKey);
        } catch (error) {
          console.log('zoomToDistrict: Harita henüz hazır değil', error);
          // Harita hazır değilse sadece state'i güncelle
          setZoomedDistrict(zoomKey);
        }
      }
    } else {
      console.log('İlçe bulunamadı:', districtName, provinceName || '');
    }
  }, [mapInstance, geoData, zoomedDistrict, resetMapView]);

  return (
    <Layout>
      <Seo 
        title="Gezginci Arıcılık Konaklama Planlama - Çiçeklenme Takvimine Göre Rota Planı | Tarımİmar"
        description="Bitkilerin çiçeklenme zamanına göre gezginci arıcılık planınızı yapın. İlçe ilçe çiçeklenme takvimi, Türkiye çiçeklenme haritası ve en uygun bal üretim rotaları. Kestane, çam, kekik ve 20+ bal çeşidi için bölge önerileri."
        canonical="https://tarimimar.com.tr/aricilik-planlama/"
        url="https://tarimimar.com.tr/aricilik-planlama/"
        ogImage="https://tarimimar.com.tr/og-aricilik-planlama.svg"
        type="website"
        jsonLd={structuredData}
        keywords="gezginci arıcılık, çiçeklenme takvimi, bal üretim rotası, arıcılık planlama, Türkiye çiçeklenme haritası, nektar kaynakları, konaklama planlama, kestane balı, çam balı, kekik balı, arıcılık yönetmeliği, bal arısı, koloni, arı kovanı"
      />
      <Head>
        {/* Leaflet CSS _document.tsx'de global olarak yükleniyor */}
        {/* Ek SEO meta etiketleri */}
        <meta name="geo.placename" content="Türkiye" />
        <meta name="geo.region" content="TR" />
        <meta name="content-language" content="tr" />
        <meta name="subject" content="Gezginci Arıcılık ve Çiçeklenme Takvimi" />
        <meta name="classification" content="Tarım, Arıcılık, Hayvancılık" />
        <meta name="coverage" content="Türkiye" />
        <meta name="distribution" content="global" />
        <style>{`
          /* Mobil Uyumluluk - Tablet ve Mobil */
          @media (max-width: 1024px) {
            .aricilik-container {
              flex-direction: column !important;
            }
            .aricilik-sidebar {
              width: 100% !important;
              max-height: 45vh !important;
              padding: 16px !important;
            }
            .aricilik-map-area {
              height: 55vh !important;
              min-height: 300px !important;
            }
            .aricilik-detail-panel {
              height: auto !important;
              max-height: 35vh !important;
              padding: 16px !important;
            }
          }
          
          @media (max-width: 768px) {
            .aricilik-container {
              flex-direction: column !important;
              height: auto !important;
              min-height: 100vh !important;
            }
            .aricilik-sidebar {
              width: 100% !important;
              max-height: none !important;
              height: auto !important;
              padding: 12px !important;
              order: 1 !important;
              flex: 0 0 auto !important;
            }
            .aricilik-map-area {
              width: 100% !important;
              height: 350px !important;
              min-height: 350px !important;
              max-height: 350px !important;
              flex: 0 0 350px !important;
              order: 2 !important;
            }
            .aricilik-map-area > div:first-child {
              height: 100% !important;
              min-height: 100% !important;
            }
            .aricilik-map-area .leaflet-container {
              height: 100% !important;
              min-height: 100% !important;
            }
            .aricilik-detail-panel {
              height: auto !important;
              max-height: 40vh !important;
              padding: 12px !important;
              order: 3 !important;
            }
          }
          
          @media (max-width: 480px) {
            .aricilik-sidebar {
              padding: 10px !important;
            }
            .aricilik-sidebar h2 {
              font-size: 16px !important;
            }
            .aricilik-sidebar p {
              font-size: 11px !important;
            }
            .aricilik-sidebar select,
            .aricilik-sidebar input,
            .aricilik-sidebar button {
              font-size: 14px !important;
              padding: 10px !important;
            }
            .aricilik-map-area {
              height: 300px !important;
              min-height: 300px !important;
              max-height: 300px !important;
              flex: 0 0 300px !important;
            }
            .aricilik-map-area > div:first-child {
              height: 100% !important;
              min-height: 100% !important;
            }
            .aricilik-detail-panel {
              padding: 10px !important;
            }
            .aricilik-detail-panel h3 {
              font-size: 16px !important;
            }
            .aricilik-detail-panel > div:first-child > div:first-child > h3 {
              font-size: 16px !important;
            }
          }
          
          /* Welcome box - mobilde gizle veya küçült */
          @media (max-width: 768px) {
            .aricilik-welcome-box {
              display: none !important;
            }
          }
          
          /* Modal Mobil Uyumluluk */
          @media (max-width: 768px) {
            [style*="position: fixed"][style*="zIndex: 2000"] > div {
              width: 95% !important;
              max-width: none !important;
              max-height: 90vh !important;
              margin: 5vh auto !important;
            }
            [style*="gridTemplateColumns"] {
              grid-template-columns: 1fr !important;
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
        `}</style>
      </Head>
      
      <div className="aricilik-container" style={{ display: 'flex', height: 'calc(100vh - 60px)', flexDirection: 'row' }}>
        {/* Sol Panel - Form */}
        <div className="aricilik-sidebar" style={{
          width: '380px',
          padding: '20px',
          background: '#fff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          overflowY: 'auto',
          flexShrink: 0
        }}>
          <h2 style={{ marginTop: 0, marginBottom: '8px', fontSize: '20px', color: '#2E7D32' }}>
            🐝 Gezginci Arıcılık Konaklama Planlama
          </h2>
          
          <p style={{ fontSize: '12px', color: '#555', marginBottom: '12px', lineHeight: '1.5' }}>
            Bitkilerin çiçeklenme zamanına göre planınızı yapın. 
            İlçe ilçe çiçeklenme takvimi ile Türkiye çiçeklenme haritası.
          </p>
          
          {/* Çiçeklenme Takvimi Link Banner */}
          <Link href="/ciceklenme-takvimi" style={{ textDecoration: 'none' }}>
            <div style={{
              padding: '12px 16px',
              marginBottom: '16px',
              background: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
              borderRadius: '10px',
              border: '1px solid #81C784',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{ fontSize: '28px' }}>🌸</span>
              <div>
                <div style={{ fontWeight: 'bold', color: '#2E7D32', fontSize: '14px' }}>
                  Çiçeklenme Takvimi
                </div>
                <div style={{ fontSize: '11px', color: '#388E3C' }}>
                  İlçe bazlı bitki çiçeklenme haritası →
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
              background: showInfoPanel ? 'linear-gradient(135deg, #FF9800, #F57C00)' : 'linear-gradient(135deg, #2196F3, #1976D2)',
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
            {showInfoPanel ? '📖 Bilgi Panelini Kapat' : '📚 Arıcılık Hakkında Bilgi'}
          </button>
          
          {/* Bilgi Paneli */}
          {showInfoPanel && (
            <div style={{
              marginBottom: '20px',
              padding: '16px',
              background: 'linear-gradient(135deg, #f5f5f5, #e8e8e8)',
              borderRadius: '12px',
              border: '1px solid #ddd',
              fontSize: '12px',
              lineHeight: '1.7',
              color: '#444',
              maxHeight: '400px',
              overflowY: 'auto'
            }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#2E7D32', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🐝 Gezginci Arıcılık Nedir?
              </h3>
              <p style={{ marginBottom: '12px' }}>
                Bir koloniden daha fazla ürün alabilmek ve bitkilerde tozlaşmayı sağlamak amacıyla 
                kovanların bir yerden başka bir yere taşınmasına <strong>&quot;gezginci arıcılık&quot;</strong> denir. 
                Gezginci arıcılık sayesinde değişik zamanlarda değişik bitkilerden yararlanılarak daha fazla ürün almak mümkündür.
              </p>
              
              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#1976D2' }}>
                🇹🇷 Türkiye&apos;de Arıcılık
              </h4>
              <p style={{ marginBottom: '12px' }}>
                Türkiye <strong>4.888.961 adet koloni varlığı</strong> ile dünyada ikinci sırada yer almaktadır. 
                Dünyada arılı kovan başına ortalama bal üretimi 20 kg civarındayken, Türkiye&apos;de bu rakam 16 kg dolayındadır. 
                Avustralya&apos;da 64 kg, Kanada&apos;da 60 kg, Çin&apos;de 38 kg olduğu göz önüne alındığında, 
                <strong> gezginci arıcılık</strong> ile verimlilik artırılabilir.
              </p>
              
              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#1976D2' }}>
                🌸 Nektar Kaynakları
              </h4>
              <p style={{ marginBottom: '12px' }}>
                Yonca, korunga, fiğ, üçgül, kekik, adaçayı, geven, ballıbaba, pamuk, ayçiçeği, kestane, 
                ıhlamur, akasya, okalüptus, turunçgiller, elma ve badem arıcılık yönünden önemli bitki türlerindendir. 
                <strong> Çiçeklenme zamanı</strong>; güneş ışığı, hava sıcaklığı, nem ve toprak yapısı gibi faktörlerden etkilenmektedir.
              </p>
              
              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#1976D2' }}>
                🗺️ Gezginci Arıcılık Rotaları
              </h4>
              <p style={{ marginBottom: '12px' }}>
                Türkiye&apos;de gezginci arıcılar üretim sezonu içerisinde Ege, Akdeniz ve Karadeniz Bölgesi&apos;nden başlayarak 
                Orta ve Doğu Anadolu&apos;ya doğru hareket etmekte; bu bölgelerden de tekrar Ege Bölgesi&apos;ndeki çam balı alanlarına 
                ya da mevsimsel koşulların daha uygun olduğu bölgelere gitmektedirler. Kovanların taşınması genellikle 
                <strong> ilkbahar sonu ile yaz başlangıcında sahil ve ovalardan yüksek yaylalara</strong>; 
                yaz sonu ve sonbaharda ise çam balı üretim alanlarına olmaktadır.
              </p>
              
              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#E65100' }}>
                📋 Arıcılık Yönetmeliği (2024)
              </h4>
              <p style={{ marginBottom: '8px' }}>
                <strong>23 Mayıs 2024</strong> tarihli Resmi Gazete&apos;de yayımlanan Arıcılık Yönetmeliği, 
                arıcılık işletmelerinin kayıt altına alınması, gen kaynaklarının korunması ve 
                sürdürülebilir arıcılık için temel esasları belirlemektedir.
              </p>
              <a 
                href="https://www.resmigazete.gov.tr/eskiler/2024/05/20240523-1.htm"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 12px',
                  background: '#fff',
                  border: '1px solid #E65100',
                  borderRadius: '6px',
                  color: '#E65100',
                  textDecoration: 'none',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  marginBottom: '12px'
                }}
              >
                📄 Resmi Gazete - Arıcılık Yönetmeliği →
              </a>
              
              <div style={{
                marginTop: '12px',
                padding: '10px',
                background: '#fff',
                borderRadius: '8px',
                border: '1px solid #81c784'
              }}>
                <p style={{ margin: 0, fontSize: '11px', color: '#2E7D32' }}>
                  <strong>💡 İpucu:</strong> Arıcılar yörenin bitki örtüsünü tanımalı, çiçeklenme ve ana nektar akım döneminin 
                  başlangıcını, süresini ve nektar akım miktarını iyi bilmelidir. Bu planlama aracı ile bölgesel hareketler 
                  için en uygun rotayı belirleyebilirsiniz.
                </p>
              </div>
              
              <p style={{ margin: '12px 0 0 0', fontSize: '10px', color: '#888', fontStyle: 'italic' }}>
                Kaynak: Arıcılık Araştırma Enstitüsü / ORDU - Veysel Serkan GÜNBEY
              </p>
            </div>
          )}
          
          {/* Bal Çeşidi Seçimi */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              fontWeight: 'bold', 
              fontSize: '14px', 
              display: 'block', 
              marginBottom: '8px',
              color: '#333'
            }}>
              🍯 Bal Çeşidi
            </label>
            <select 
              value={selectedHoneyType} 
              onChange={(e) => setSelectedHoneyType(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontSize: '14px',
                cursor: 'pointer',
                background: '#fff'
              }}
            >
              {HONEY_TYPES.map(type => (
                <option key={type} value={type}>{type} BALI</option>
              ))}
            </select>
          </div>
          
          {/* Mevsim Preset'leri */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              fontWeight: 'bold', 
              fontSize: '14px', 
              display: 'block', 
              marginBottom: '8px',
              color: '#333'
            }}>
              🗓️ Hızlı Seçim (Mevsim)
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {SEASON_PRESETS.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => applySeasonPreset(preset)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '20px',
                    border: '1px solid #ddd',
                    background: '#f5f5f5',
                    fontSize: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.background = '#e0e0e0';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.background = '#f5f5f5';
                  }}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>
          
          {/* Tarih Aralığı */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              fontWeight: 'bold', 
              fontSize: '14px', 
              display: 'block', 
              marginBottom: '8px',
              color: '#333'
            }}>
              📅 Başlangıç Tarihi
            </label>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
              <DebouncedInput
                type="number"
                min="1"
                max="31"
                value={startDay}
                onChange={(val) => setStartDay(Number(val))}
                style={{ 
                  width: '70px', 
                  padding: '10px', 
                  borderRadius: '8px', 
                  border: '2px solid #ddd',
                  fontSize: '14px',
                  textAlign: 'center'
                }}
              />
              <select
                value={startMonth}
                onChange={(e) => setStartMonth(Number(e.target.value))}
                style={{ 
                  flex: 1, 
                  padding: '10px', 
                  borderRadius: '8px', 
                  border: '2px solid #ddd',
                  fontSize: '14px'
                }}
              >
                {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>
            
            <label style={{ 
              fontWeight: 'bold', 
              fontSize: '14px', 
              display: 'block', 
              marginBottom: '8px',
              color: '#333'
            }}>
              📅 Bitiş Tarihi
            </label>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
              <DebouncedInput
                type="number"
                min="1"
                max="31"
                value={endDay}
                onChange={(val) => setEndDay(Number(val))}
                style={{ 
                  width: '70px', 
                  padding: '10px', 
                  borderRadius: '8px', 
                  border: '2px solid #ddd',
                  fontSize: '14px',
                  textAlign: 'center'
                }}
              />
              <select
                value={endMonth}
                onChange={(e) => setEndMonth(Number(e.target.value))}
                style={{ 
                  flex: 1, 
                  padding: '10px', 
                  borderRadius: '8px', 
                  border: '2px solid #ddd',
                  fontSize: '14px'
                }}
              >
                {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>
          </div>
          
          {/* Butonlar */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
            <button
              onClick={generatePlan}
              disabled={loading}
              style={{
                flex: 2,
                padding: '14px',
                background: loading ? '#ccc' : 'linear-gradient(135deg, #4CAF50, #45a049)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'wait' : 'pointer',
                fontWeight: 'bold',
                fontSize: '15px',
                boxShadow: '0 3px 6px rgba(0,0,0,0.2)',
                transition: 'all 0.3s'
              }}
            >
              {loading ? '⏳ Planlar Hazırlanıyor...' : '🚀 Plan Oluştur'}
            </button>
            
            {(plans.length > 0 || error) && (
              <button
                onClick={clearPlan}
                style={{
                  flex: 1,
                  padding: '14px',
                  background: '#f5f5f5',
                  color: '#666',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
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
            )}
          </div>
          
          {/* Hata Mesajı */}
          {error && (
            <div style={{
              marginTop: '16px',
              padding: '14px',
              background: '#fff3e0',
              color: '#e65100',
              borderRadius: '8px',
              fontSize: '13px',
              border: '1px solid #ffcc80',
              lineHeight: '1.6'
            }}>
              <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>
                ⚠️ Sonuç Bulunamadı
              </div>
              {error}
            </div>
          )}
          
          {/* Özet Bilgi */}
          {resultSummary && (
            <div style={{
              marginTop: '16px',
              padding: '14px',
              background: 'linear-gradient(135deg, #e8f5e9, #c8e6c9)',
              color: '#2e7d32',
              borderRadius: '8px',
              fontSize: '13px',
              border: '1px solid #81c784',
              lineHeight: '1.5',
              fontWeight: '500'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>✅ {resultSummary}</span>
                {totalMatchingDistricts > 4 && (
                  <button
                    onClick={() => {
                      setShowOnlyTopPlans(false); // Tüm bölgeleri haritada göster
                      setShowAllDistrictsModal(true);
                    }}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#1976D2',
                      cursor: 'pointer',
                      fontSize: '12px',
                      textDecoration: 'underline',
                      fontWeight: 'bold'
                    }}
                  >
                    📍 Tüm {totalMatchingDistricts} bölgeyi gör →
                  </button>
                )}
              </div>
            </div>
          )}
          
          {/* Planlar Listesi */}
          {plans.length > 0 && (
            <div style={{ marginTop: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h3 style={{ fontSize: '16px', margin: 0, color: '#2E7D32', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  📋 Önerilen Planlar
                  <span style={{ 
                    background: '#4CAF50', 
                    color: 'white', 
                    padding: '2px 8px', 
                    borderRadius: '12px', 
                    fontSize: '12px' 
                  }}>
                    {plans.length}
                  </span>
                </h3>
                {!showOnlyTopPlans && (
                  <button
                    onClick={() => setShowOnlyTopPlans(true)}
                    style={{
                      background: 'linear-gradient(135deg, #F44336, #C62828)',
                      color: 'white',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '11px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.transform = 'scale(1.05)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.transform = 'scale(1)';
                    }}
                    title="Haritada sadece önerilen 4 planı göster"
                  >
                    🎯 Sadece Önerilenleri Göster
                  </button>
                )}
              </div>
              
              {plans.map((plan) => (
                <div
                  key={plan.plan_number}
                  style={{
                    padding: '16px',
                    marginBottom: '12px',
                    background: selectedPlan?.plan_number === plan.plan_number 
                      ? 'linear-gradient(135deg, #e8f5e9, #c8e6c9)' 
                      : '#fafafa',
                    border: selectedPlan?.plan_number === plan.plan_number
                      ? '2px solid #4CAF50'
                      : '1px solid #e0e0e0',
                    borderRadius: '10px',
                    transition: 'all 0.2s',
                    boxShadow: selectedPlan?.plan_number === plan.plan_number
                      ? '0 4px 12px rgba(76,175,80,0.3)'
                      : '0 1px 3px rgba(0,0,0,0.1)'
                  }}
                >
                  <div 
                    onClick={() => {
                      setSelectedPlan(plan);
                      // Eğer bir ilçeye zoom yapılmışsa, haritayı genel görünüme döndür
                      if (zoomedDistrict) {
                        resetMapView();
                      }
                    }}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={(e) => {
                      if (selectedPlan?.plan_number !== plan.plan_number) {
                        (e.currentTarget.parentElement as HTMLElement).style.background = '#f0f0f0';
                        (e.currentTarget.parentElement as HTMLElement).style.transform = 'translateY(-2px)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedPlan?.plan_number !== plan.plan_number) {
                        (e.currentTarget.parentElement as HTMLElement).style.background = '#fafafa';
                        (e.currentTarget.parentElement as HTMLElement).style.transform = 'translateY(0)';
                      }
                    }}
                  >
                    <div style={{ 
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start'
                    }}>
                      <div style={{ 
                        fontSize: '16px', 
                        fontWeight: 'bold', 
                        marginBottom: '6px',
                        color: selectedPlan?.plan_number === plan.plan_number ? '#2E7D32' : '#1976D2'
                      }}>
                        {plan.plan_number === 1 && '🥇'} 
                        {plan.plan_number === 2 && '🥈'} 
                        {plan.plan_number === 3 && '🥉'} 
                        {plan.plan_number === 4 && '⭐'} 
                        {' '}{plan.district}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // İlçeye zoom yap veya zoom out yap (toggle) - il bilgisini de gönder
                          zoomToDistrict(plan.district, plan.province);
                          setSelectedPlan(plan);
                        }}
                        style={{
                          padding: '4px 8px',
                          fontSize: '11px',
                          background: zoomedDistrict === `${plan.district}|${plan.province}` 
                            ? 'linear-gradient(135deg, #FF9800, #F57C00)' 
                            : 'linear-gradient(135deg, #2196F3, #1976D2)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLElement).style.transform = 'scale(1.05)';
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLElement).style.transform = 'scale(1)';
                        }}
                        title={zoomedDistrict === `${plan.district}|${plan.province}` ? "Tüm haritayı göster" : "Haritada bu ilçeye yakınlaş"}
                      >
                        {zoomedDistrict === `${plan.district}|${plan.province}` ? '🔎 Uzaklaş' : '🔍 Göster'}
                      </button>
                    </div>
                    <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>
                      📍 {plan.province}
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#2E7D32', 
                      fontWeight: 'bold',
                      display: 'flex',
                      gap: '12px',
                      flexWrap: 'wrap'
                    }}>
                      <span>🌸 {plan.target_plants.length} bitki</span>
                      <span 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedPlan(plan);
                          setShowAllPlantsModal(true);
                        }}
                        style={{ 
                          cursor: 'pointer', 
                          textDecoration: 'underline',
                          color: '#1976D2'
                        }}
                        title="Tüm bitki türlerini görmek için tıklayın"
                      >
                        🌿 {plan.diversity_score} tür
                      </span>
                      {plan.honey_power !== undefined && plan.honey_power > 0 && (
                        <span 
                          onClick={(e) => {
                            e.stopPropagation();
                            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                            setHoneyPowerTooltip({show: true, power: plan.honey_power!, x: rect.left, y: rect.bottom + 5});
                          }}
                          style={{ 
                            color: '#FF9800', 
                            cursor: 'pointer',
                            textDecoration: 'underline dotted'
                          }}
                          title={`${selectedHoneyType} Balı Toplama Oranı: %${plan.honey_power}`}
                        >
                          🍯 %{plan.honey_power}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Harita Lejantı */}
          {plans.length > 0 && (
            <div style={{ 
              marginTop: '20px', 
              padding: '14px', 
              background: '#f9f9f9', 
              borderRadius: '8px',
              border: '1px solid #e0e0e0'
            }}>
              <div style={{ fontWeight: 'bold', fontSize: '13px', marginBottom: '10px', color: '#333' }}>
                🗺️ Harita Lejantı
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '20px', height: '14px', background: '#4CAF50', borderRadius: '3px', border: '2px solid #2E7D32' }}></div>
                  <span>Seçili Plan</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '20px', height: '14px', background: '#F44336', borderRadius: '3px', border: '2px solid #C62828' }}></div>
                  <span>En İyi 4 Plan (Önerilen)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '20px', height: '14px', background: '#FFD700', borderRadius: '3px', border: '2px solid #FFA500' }}></div>
                  <span>Diğer Uygun Bölgeler</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '20px', height: '14px', background: '#FF5722', borderRadius: '3px', border: '2px solid #E64A19' }}></div>
                  <span>İmleç Üzerinde</span>
                </div>
                {zoomedDistrict && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px', paddingTop: '6px', borderTop: '1px dashed #ccc' }}>
                    <div style={{ width: '20px', height: '14px', background: 'url(https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/4/6/9)', backgroundSize: 'cover', borderRadius: '3px', border: '2px dashed #FF5722' }}></div>
                    <span>🛰️ Uydu Görüntüsü Aktif</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Sağ Panel - Harita */}
        <div className="aricilik-map-area" style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column' }}>
          {/* Harita */}
          <div style={{ flex: 1, minHeight: '300px' }}>
            {mapLoaded && (
              <MapContainer
                center={[39, 35]}
                zoom={typeof window !== 'undefined' && window.innerWidth < 768 ? 5 : 6}
                style={{ height: '100%', width: '100%' }}
              >
                <MapController onMapReady={(map: any) => {
                  if (!mapInstance) {
                    mapRef.current = map;
                    setMapInstance(map);
                  }
                }} />
                {/* Zoom yapıldığında uydu görüntüsü, yoksa normal harita */}
                {zoomedDistrict ? (
                  <TileLayer 
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution='&copy; <a href="https://www.esri.com/">Esri</a> | Uydu Görüntüsü'
                  />
                ) : (
                  <TileLayer 
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  />
                )}
                {geoData && (
                  <GeoJSON
                    key={`geo-${selectedPlan?.plan_number || 0}-${highlightedDistricts.size}-${topPlanDistricts.size}-${hoveredDistrict}-${zoomedDistrict}-${showOnlyTopPlans}`}
                    data={geoData}
                    style={getStyle}
                    onEachFeature={onEachFeature}
                    eventHandlers={{
                      click: (e: any) => onDistrictClick(e.layer.feature)
                    }}
                  />
                )}
              </MapContainer>
            )}
          </div>
          
          {/* Alt Panel - Seçili Plan Detayları */}
          {selectedPlan && (
            <div className="aricilik-detail-panel" style={{
              height: '280px',
              background: 'white',
              borderTop: '3px solid #4CAF50',
              padding: '20px',
              overflowY: 'auto',
              boxShadow: '0 -4px 12px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '20px', color: '#2E7D32', marginBottom: '4px' }}>
                    {selectedPlan.plan_number === 1 && '🥇'} 
                    {selectedPlan.plan_number === 2 && '🥈'} 
                    {selectedPlan.plan_number === 3 && '🥉'} 
                    {selectedPlan.plan_number === 4 && '⭐'} 
                    {' '}{selectedPlan.district}, {selectedPlan.province}
                  </h3>
                  <div style={{ fontSize: '13px', color: '#666' }}>
                    Plan {selectedPlan.plan_number} • {selectedPlan.diversity_score} farklı bitki türü
                  </div>
                </div>
                <button
                  onClick={() => setSelectedPlan(null)}
                  style={{
                    background: '#f5f5f5',
                    border: '1px solid #ddd',
                    borderRadius: '50%',
                    width: '32px',
                    height: '32px',
                    fontSize: '18px',
                    cursor: 'pointer',
                    color: '#666',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  ×
                </button>
              </div>
              
              <div style={{ 
                padding: '12px 16px', 
                background: 'linear-gradient(135deg, #fff8e1, #ffecb3)', 
                borderRadius: '8px', 
                marginBottom: '16px',
                fontSize: '13px',
                color: '#f57c00',
                border: '1px solid #ffe082'
              }}>
                💡 {selectedPlan.recommendation_reason}
              </div>
              
              <h4 style={{ fontSize: '15px', marginBottom: '12px', color: '#333', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🌸 Hedef Bitkiler
                <span style={{ 
                  background: '#e8f5e9', 
                  color: '#2E7D32', 
                  padding: '2px 8px', 
                  borderRadius: '12px', 
                  fontSize: '12px' 
                }}>
                  {selectedPlan.target_plants.length} adet
                </span>
              </h4>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                {selectedPlan.target_plants.map((plant, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '12px',
                      background: plant.overlap_type === 'minimal' 
                        ? 'linear-gradient(135deg, #fff3e0, #ffe0b2)'
                        : plant.overlap_type === 'partial'
                        ? 'linear-gradient(135deg, #fffde7, #fff9c4)'
                        : 'linear-gradient(135deg, #e8f5e9, #c8e6c9)',
                      border: plant.overlap_type === 'minimal'
                        ? '1px solid #ffcc80'
                        : plant.overlap_type === 'partial'
                        ? '1px solid #fff176'
                        : '1px solid #a5d6a7',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '6px', color: '#1976D2', fontSize: '14px' }}>
                      🌱 {plant.plant}
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#666',
                      background: '#fff',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      display: 'inline-block',
                      marginBottom: '8px'
                    }}>
                      📅 {formatDateRange(plant.start[1], plant.start[0], plant.end[1], plant.end[0])}
                    </div>
                    
                    {/* Örtüşme Görselleştirmesi - Sayı Doğrusu */}
                    {plant.overlap_percentage !== undefined && (
                      <div style={{ marginTop: '8px' }}>
                        <div style={{ 
                          fontSize: '10px', 
                          color: '#666', 
                          marginBottom: '4px',
                          display: 'flex',
                          justifyContent: 'space-between'
                        }}>
                          <span>Sizin tarihiniz ↔ Çiçeklenme dönemi</span>
                          <span style={{ 
                            fontWeight: 'bold',
                            color: plant.overlap_type === 'minimal' ? '#e65100' : plant.overlap_type === 'partial' ? '#f57f17' : '#2e7d32'
                          }}>
                            %{plant.overlap_percentage}
                          </span>
                        </div>
                        {/* Progress Bar Görselleştirmesi */}
                        <div style={{ 
                          width: '100%', 
                          height: '8px', 
                          background: '#e0e0e0', 
                          borderRadius: '4px',
                          overflow: 'hidden',
                          position: 'relative'
                        }}>
                          <div style={{ 
                            width: `${plant.overlap_percentage}%`, 
                            height: '100%', 
                            background: plant.overlap_type === 'minimal' 
                              ? 'linear-gradient(90deg, #ff5722, #ff9800)'
                              : plant.overlap_type === 'partial'
                              ? 'linear-gradient(90deg, #ffc107, #ffeb3b)'
                              : 'linear-gradient(90deg, #4caf50, #8bc34a)',
                            borderRadius: '4px',
                            transition: 'width 0.5s ease'
                          }}></div>
                        </div>
                        {/* Durum Mesajı */}
                        <div style={{
                          marginTop: '6px',
                          fontSize: '11px',
                          color: plant.overlap_type === 'minimal' ? '#e65100' : plant.overlap_type === 'partial' ? '#f57f17' : '#2e7d32',
                          fontWeight: 'bold'
                        }}>
                          {plant.overlap_type === 'full' && '✅ Tam uyum - Mükemmel zamanlama!'}
                          {plant.overlap_type === 'partial' && `⚠️ Kısmi örtüşme - İyi ama geliştirilebilir`}
                          {plant.overlap_type === 'minimal' && `⛔ Düşük örtüşme - Tarih aralığını kontrol edin!`}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Başlangıç durumu - plan yoksa (mobilde gizli) */}
          {!selectedPlan && plans.length === 0 && !loading && (
            <div className="aricilik-welcome-box" style={{
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
              zIndex: 10
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🐝</div>
              <h3 style={{ margin: '0 0 12px 0', color: '#2E7D32', fontSize: '20px' }}>
                Arıcılık Rotanızı Planlayın
              </h3>
              <p style={{ color: '#666', fontSize: '14px', lineHeight: '1.6', margin: 0 }}>
                Sol panelden bal çeşidini ve tarih aralığını seçip 
                <strong> &quot;Plan Oluştur&quot;</strong> butonuna tıklayın.
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
                <div style={{ fontSize: '48px', marginBottom: '16px', animation: 'pulse 1.5s infinite' }}>🍯</div>
                <div style={{ color: '#2E7D32', fontWeight: 'bold', fontSize: '16px' }}>
                  Planlar hazırlanıyor...
                </div>
                <div style={{ color: '#666', fontSize: '13px', marginTop: '8px' }}>
                  En uygun bölgeler analiz ediliyor
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Tüm Bölgeler Modal */}
      {showAllDistrictsModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000
          }}
          onClick={() => {
            setShowAllDistrictsModal(false);
            setSelectedDistrictFromModal(null);
          }}
        >
          <div 
            style={{
              background: 'white',
              borderRadius: '16px',
              maxWidth: '900px',
              width: '95%',
              maxHeight: '85vh',
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              padding: '20px 24px',
              borderBottom: '1px solid #e0e0e0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'linear-gradient(135deg, #e8f5e9, #c8e6c9)'
            }}>
              <h3 style={{ margin: 0, color: '#2E7D32', fontSize: '18px' }}>
                📍 Tüm Uygun Bölgeler ({totalMatchingDistricts} ilçe)
                {selectedDistrictFromModal && (
                  <span style={{ fontSize: '14px', fontWeight: 'normal', marginLeft: '12px' }}>
                    → {selectedDistrictFromModal.district} seçili
                  </span>
                )}
              </h3>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                {/* Tümünü Haritada Gör butonu */}
                <button
                  onClick={() => {
                    // Modal'ı kapat
                    setShowAllDistrictsModal(false);
                    setSelectedDistrictFromModal(null);
                    // Tüm bölgeleri haritada göster
                    setShowOnlyTopPlans(false);
                    // Haritayı tüm highlighted bölgeleri kapsayacak şekilde zoom yap
                    fitAllHighlightedDistricts();
                  }}
                  style={{
                    background: 'linear-gradient(135deg, #4CAF50, #388E3C)',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.transform = 'scale(1.05)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.transform = 'scale(1)';
                  }}
                >
                  🗺️ Tümünü Haritada Gör
                </button>
                {selectedDistrictFromModal && (
                  <button
                    onClick={() => setSelectedDistrictFromModal(null)}
                    style={{
                      background: '#FF9800',
                      color: 'white',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '13px'
                    }}
                  >
                    ← Tüm Bölgeleri Göster
                  </button>
                )}
                <button
                  onClick={() => {
                    setShowAllDistrictsModal(false);
                    setSelectedDistrictFromModal(null);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '24px',
                    cursor: 'pointer',
                    color: '#666'
                  }}
                >
                  ×
                </button>
              </div>
            </div>
            <div style={{ 
              padding: '16px 24px', 
              overflowY: 'auto', 
              maxHeight: 'calc(85vh - 70px)'
            }}>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', 
                gap: '12px' 
              }}>
                {allDistricts.map((d, idx) => {
                  // İlçeye ait plan bilgisini bul (bitki listesi için)
                  const relatedPlan = plans.find(p => 
                    matchDistrictNames(p.district, d.district) && 
                    matchDistrictNames(p.province, d.province)
                  );
                  
                  return (
                    <div
                      key={idx}
                      onClick={() => {
                        // Modal'ı kapat ve haritada uydu görünümüyle ilçeye zoom yap
                        setShowAllDistrictsModal(false);
                        setSelectedDistrictFromModal(null);
                        // İl bilgisini de gönder - aynı isimli ilçeleri (MERKEZ vb.) ayırt etmek için
                        zoomToDistrict(d.district, d.province);
                        // Eğer bu ilçe için plan varsa onu seç
                        if (relatedPlan) {
                          setSelectedPlan(relatedPlan);
                        }
                      }}
                      style={{
                        padding: '14px',
                        background: idx < 4 ? 'linear-gradient(135deg, #fff8e1, #ffecb3)' : '#f9f9f9',
                        border: idx < 4 ? '2px solid #FFC107' : '1px solid #e0e0e0',
                        borderRadius: '10px',
                        fontSize: '13px',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                        (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                        (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                      }}
                    >
                      <div style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'flex-start',
                        marginBottom: '6px'
                      }}>
                        <div style={{ fontWeight: 'bold', color: '#333' }}>
                          {idx < 4 && '⭐ '}{d.district}
                        </div>
                        <span style={{ 
                          fontSize: '10px', 
                          background: '#E3F2FD', 
                          padding: '2px 6px', 
                          borderRadius: '4px', 
                          color: '#1565C0' 
                        }}>
                          🛰️ Haritada Gör
                        </span>
                      </div>
                      <div style={{ color: '#666', fontSize: '11px', marginBottom: '8px' }}>
                        📍 {d.province}
                      </div>
                      
                      {/* Bal gücü ve örtüşme bilgileri */}
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', fontSize: '10px', marginBottom: '8px' }}>
                        {d.honey_power > 0 && (
                          <span 
                            style={{ background: '#FFF3E0', padding: '2px 6px', borderRadius: '4px', color: '#E65100' }}
                            title={`${selectedHoneyType} Balı Toplama Oranı`}
                          >
                            🍯 %{d.honey_power}
                          </span>
                        )}
                        <span style={{ background: '#E3F2FD', padding: '2px 6px', borderRadius: '4px', color: '#1565C0' }}>
                          ⏱️ %{d.avg_overlap} örtüşme
                        </span>
                        <span style={{ background: '#E8F5E9', padding: '2px 6px', borderRadius: '4px', color: '#2E7D32' }}>
                          🌿 {d.diversity_score} bitki
                        </span>
                      </div>
                      
                      {/* Örtüşme Progress Bar */}
                      <div style={{ 
                        width: '100%', 
                        height: '4px', 
                        background: '#e0e0e0', 
                        borderRadius: '2px',
                        overflow: 'hidden'
                      }}>
                        <div style={{ 
                          width: `${d.avg_overlap}%`, 
                          height: '100%', 
                          background: d.avg_overlap >= 70 
                            ? 'linear-gradient(90deg, #4caf50, #8bc34a)'
                            : d.avg_overlap >= 40
                            ? 'linear-gradient(90deg, #ffc107, #ffeb3b)'
                            : 'linear-gradient(90deg, #ff5722, #ff9800)',
                          borderRadius: '2px'
                        }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Tüm Bitkiler Modal */}
      {showAllPlantsModal && selectedPlan && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000
          }}
          onClick={() => setShowAllPlantsModal(false)}
        >
          <div 
            style={{
              background: 'white',
              borderRadius: '16px',
              maxWidth: '700px',
              width: '90%',
              maxHeight: '80vh',
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              padding: '20px 24px',
              borderBottom: '1px solid #e0e0e0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'linear-gradient(135deg, #e3f2fd, #bbdefb)'
            }}>
              <h3 style={{ margin: 0, color: '#1565C0', fontSize: '18px' }}>
                🌿 {selectedPlan.district}, {selectedPlan.province} - Tüm Bitkiler ({selectedPlan.all_plants?.length || selectedPlan.diversity_score} tür)
              </h3>
              <button
                onClick={() => setShowAllPlantsModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: '#666'
                }}
              >
                ×
              </button>
            </div>
            <div style={{ 
              padding: '16px 24px', 
              overflowY: 'auto', 
              maxHeight: 'calc(80vh - 70px)'
            }}>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
                gap: '10px' 
              }}>
                {(selectedPlan.all_plants || []).map((plant, idx) => {
                  const isTarget = selectedPlan.target_plants.some(tp => tp.plant === plant.plant);
                  return (
                    <div
                      key={idx}
                      style={{
                        padding: '10px',
                        background: isTarget ? 'linear-gradient(135deg, #fff8e1, #ffecb3)' : '#f9f9f9',
                        border: isTarget ? '2px solid #FFC107' : '1px solid #e0e0e0',
                        borderRadius: '8px',
                        fontSize: '12px'
                      }}
                    >
                      <div style={{ fontWeight: 'bold', color: isTarget ? '#E65100' : '#333', marginBottom: '4px' }}>
                        {isTarget && '🎯 '}{plant.plant}
                      </div>
                      <div style={{ color: '#666', fontSize: '11px' }}>
                        📅 {formatDateRange(plant.start[1], plant.start[0], plant.end[1], plant.end[0])}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Bal Toplama Oranı Tooltip */}
      {honeyPowerTooltip.show && (
        <div
          style={{
            position: 'fixed',
            left: honeyPowerTooltip.x,
            top: honeyPowerTooltip.y,
            background: 'linear-gradient(135deg, #fff8e1, #ffecb3)',
            border: '2px solid #FFC107',
            borderRadius: '12px',
            padding: '16px 20px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
            zIndex: 3000,
            maxWidth: '280px',
            animation: 'fadeIn 0.2s ease'
          }}
          onClick={() => setHoneyPowerTooltip({...honeyPowerTooltip, show: false})}
        >
          <div style={{ 
            fontSize: '16px', 
            fontWeight: 'bold', 
            color: '#E65100',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🍯 {selectedHoneyType} Balı
          </div>
          <div style={{ fontSize: '13px', color: '#666', marginBottom: '12px' }}>
            Bu ilin bal toplama kapasitesi
          </div>
          <div style={{ 
            fontSize: '28px', 
            fontWeight: 'bold', 
            color: '#FF9800',
            textAlign: 'center',
            marginBottom: '8px'
          }}>
            %{honeyPowerTooltip.power}
          </div>
          {/* Progress bar */}
          <div style={{ 
            width: '100%', 
            height: '10px', 
            background: '#e0e0e0', 
            borderRadius: '5px',
            overflow: 'hidden'
          }}>
            <div style={{ 
              width: `${honeyPowerTooltip.power}%`, 
              height: '100%', 
              background: 'linear-gradient(90deg, #FF9800, #FFC107)',
              borderRadius: '5px'
            }}></div>
          </div>
          <div style={{ 
            fontSize: '11px', 
            color: '#999', 
            marginTop: '10px',
            textAlign: 'center'
          }}>
            Kapatmak için tıklayın
          </div>
        </div>
      )}
      
      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </Layout>
  );
}
