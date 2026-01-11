import L from 'leaflet';

// KML dosyalarından yüklenen poligon verilerini saklama
interface KMLPolygon {
  name: string;
  coordinates: L.LatLng[][];
  properties?: any;
}

interface KMLData {
  buyukOvalar: KMLPolygon[];
  kapaliSuHavzasi: KMLPolygon[];
  izmirSiniri: KMLPolygon[];
}

let kmlData: KMLData = {
  buyukOvalar: [],
  kapaliSuHavzasi: [],
  izmirSiniri: []
};

// KML dosyasını parse etme fonksiyonu
const parseKMLFile = async (filePath: string): Promise<KMLPolygon[]> => {
  try {
    const response = await fetch(filePath);
    const kmlText = await response.text();
    const parser = new DOMParser();
    const kmlDoc = parser.parseFromString(kmlText, 'text/xml');
    
    const polygons: KMLPolygon[] = [];
    const placemarks = kmlDoc.getElementsByTagName('Placemark');
    
    Array.from(placemarks).forEach(placemark => {
      const name = placemark.getElementsByTagName('name')[0]?.textContent || 'Unknown';
      const coordinates = placemark.getElementsByTagName('coordinates')[0]?.textContent;
      
      if (coordinates) {
        const coordPairs = coordinates.trim().split(/\s+/);
        const latLngs: L.LatLng[] = [];
        
        coordPairs.forEach(coord => {
          const [lng, lat] = coord.split(',').map(Number);
          if (!isNaN(lat) && !isNaN(lng)) {
            latLngs.push(L.latLng(lat, lng));
          }
        });
        
        if (latLngs.length > 0) {
          polygons.push({
            name,
            coordinates: [latLngs]
          });
        }
      }
    });
    
    return polygons;
  } catch (error) {
    console.error(`KML dosyası yüklenirken hata: ${filePath}`, error);
    return [];
  }
};

// KML verilerini yükleme fonksiyonu
export const loadKMLData = async (): Promise<void> => {
  try {
    console.log('🗺️ KML verileri yükleniyor...');
    
    const [buyukOvalar, kapaliSuHavzasi, izmirSiniri] = await Promise.all([
      parseKMLFile('/Büyük Ovalar İzmir.kml'),
      parseKMLFile('/izmir_kapali_alan.kml'),
      parseKMLFile('/izmir.kml')
    ]);
    
    kmlData = {
      buyukOvalar,
      kapaliSuHavzasi,
      izmirSiniri
    };
    
    console.log('✅ KML verileri başarıyla yüklendi:', {
      buyukOvalar: buyukOvalar.length,
      kapaliSuHavzasi: kapaliSuHavzasi.length,
      izmirSiniri: izmirSiniri.length
    });
    
    // Debug: İlk polygon adlarını göster
    console.log('🔍 Yüklenen poligonlar:', {
      buyukOvalar: buyukOvalar.map(p => p.name),
      kapaliSuHavzasi: kapaliSuHavzasi.map(p => p.name),
      izmirSiniri: izmirSiniri.map(p => p.name)
    });
  } catch (error) {
    console.error('❌ KML verileri yüklenirken hata:', error);
  }
};

// Bir noktanın poligon içinde olup olmadığını kontrol etme
const isPointInPolygon = (point: L.LatLng, polygon: L.LatLng[]): boolean => {
  let inside = false;
  const x = point.lat;
  const y = point.lng;
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].lat;
    const yi = polygon[i].lng;
    const xj = polygon[j].lat;
    const yj = polygon[j].lng;
    
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  
  return inside;
};

// Ana kontrol fonksiyonu
export interface KMLCheckResult {
  izmirinIcinde: boolean;
  buyukOvaIcinde: boolean;
  kapaliSuHavzasiIcinde: boolean;
  detaylar: {
    buyukOvaAdi?: string;
    kapaliSuHavzaAdi?: string;
    izmirBolgeAdi?: string;
  };
}

// LocationCheckResult backward compatibility
export type LocationCheckResult = KMLCheckResult;

export const checkKMLLocation = async (point: { lat: number; lng: number }): Promise<KMLCheckResult> => {
  // KML verileri yüklenmemişse yükle
  if (!isKMLDataLoaded()) {
    await loadKMLData();
  }
  
  return checkLocationInKML(point.lat, point.lng);
};

export const checkLocationInKML = (lat: number, lng: number): KMLCheckResult => {
  const point = L.latLng(lat, lng);
  
  const result: KMLCheckResult = {
    izmirinIcinde: false,
    buyukOvaIcinde: false,
    kapaliSuHavzasiIcinde: false,
    detaylar: {}
  };
  
  console.log('🔍 KML kontrol başlıyor:', { lat, lng, kmlDataLoaded: isKMLDataLoaded() });
  console.log('📊 Mevcut KML verileri:', {
    izmirSiniri: kmlData.izmirSiniri.length,
    buyukOvalar: kmlData.buyukOvalar.length,
    kapaliSuHavzasi: kmlData.kapaliSuHavzasi.length
  });
  
  // İzmir sınırları kontrolü
  for (const polygon of kmlData.izmirSiniri) {
    for (const coords of polygon.coordinates) {
      if (isPointInPolygon(point, coords)) {
        result.izmirinIcinde = true;
        result.detaylar.izmirBolgeAdi = polygon.name;
        break;
      }
    }
    if (result.izmirinIcinde) break;
  }
  
  // Sadece İzmir içindeyse diğer kontrolleri yap
  if (result.izmirinIcinde) {
    // Büyük ova kontrolü
    for (const polygon of kmlData.buyukOvalar) {
      for (const coords of polygon.coordinates) {
        if (isPointInPolygon(point, coords)) {
          result.buyukOvaIcinde = true;
          result.detaylar.buyukOvaAdi = polygon.name;
          break;
        }
      }
      if (result.buyukOvaIcinde) break;
    }
    
    // Kapalı su havzası kontrolü
    for (const polygon of kmlData.kapaliSuHavzasi) {
      for (const coords of polygon.coordinates) {
        if (isPointInPolygon(point, coords)) {
          result.kapaliSuHavzasiIcinde = true;
          result.detaylar.kapaliSuHavzaAdi = polygon.name;
          break;
        }
      }
      if (result.kapaliSuHavzasiIcinde) break;
    }
  }
  
  console.log('✅ KML kontrol sonucu:', result);
  
  return result;
};

// KML verilerinin yüklenip yüklenmediğini kontrol etme
export const isKMLDataLoaded = (): boolean => {
  return kmlData.izmirSiniri.length > 0;
};
