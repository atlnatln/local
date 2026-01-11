import { useEffect, useState } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';

interface Province {
  type: string;
  geometry: any;
  properties: {
    name: string;
    ADM1_TR: string;
    ADM1_EN?: string;
  };
}

interface District {
  type: string;
  geometry: any;
  properties: {
    name: string;
    ADM2_TR: string;
    ADM1_TR?: string;
  };
}

interface TurkeyBoundariesProps {
  onProvinceClick?: (provinceName: string, bounds: L.LatLngBounds) => void;
  onDistrictClick?: (districtName: string, bounds: L.LatLngBounds) => void;
}

const TurkeyBoundaries: React.FC<TurkeyBoundariesProps> = ({ 
  onProvinceClick,
  onDistrictClick 
}) => {
  const map = useMap();
  const [provinces, setProvinces] = useState<any>(null);
  const [districts, setDistricts] = useState<any>(null);
  const [showDistricts, setShowDistricts] = useState(false);
  const [selectedProvince, setSelectedProvince] = useState<string | null>(null);

  useEffect(() => {
    // İl sınırlarını yükle
    fetch('/turkey-provinces.geojson')
      .then(res => res.json())
      .then(data => setProvinces(data))
      .catch(err => console.error('İl sınırları yüklenemedi:', err));

    // İlçe sınırlarını yükle
    fetch('/turkey-districts.geojson')
      .then(res => res.json())
      .then(data => setDistricts(data))
      .catch(err => console.error('İlçe sınırları yüklenemedi:', err));
  }, []);

  const provinceStyle = (feature?: any) => ({
    color: '#dc2626',
    weight: 1.5,
    fillOpacity: 0,
    fillColor: 'transparent',
    opacity: 0.4
  });

  const districtStyle = (feature?: any) => ({
    color: '#dc2626',
    weight: 1.3,
    fillOpacity: 0,
    fillColor: 'transparent',
    opacity: 0.3
  });

  const getPadding = (): [number, number] => (window.innerWidth <= 600 ? [20, 20] : [40, 40]);

  const onEachProvince = (feature: Province, layer: L.Layer) => {
    // Tooltip kaldırıldı, sadece pasif görünüm
  };

  const onEachDistrict = (feature: District, layer: L.Layer) => {
    // Tooltip kaldırıldı, sadece pasif görünüm
  };

  // Zoom değiştiğinde ilçeleri gizle/göster
  useEffect(() => {
    const handleZoomEnd = () => {
      const zoom = map.getZoom();
      // Zoom 9 ve üzerinde ilçeleri göster
      setShowDistricts(zoom >= 9);
    };

    map.on('zoomend', handleZoomEnd);
    
    // İlk yükleme için zoom kontrolü
    handleZoomEnd();
    
    return () => {
      map.off('zoomend', handleZoomEnd);
    };
  }, [map]);

  return (
    <>
      {provinces && (
        <GeoJSON
          key="provinces"
          data={provinces}
          style={provinceStyle}
          onEachFeature={onEachProvince}
        />
      )}
      
      {showDistricts && districts && (
        <GeoJSON
          key="districts-all"
          data={districts}
          style={districtStyle}
          onEachFeature={onEachDistrict}
        />
      )}
    </>
  );
};

export default TurkeyBoundaries;
