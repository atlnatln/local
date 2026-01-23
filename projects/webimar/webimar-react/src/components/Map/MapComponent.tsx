import React, { useEffect, useRef, forwardRef, useImperativeHandle, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, useMap, GeoJSON } from 'react-leaflet';
import type { Feature, FeatureCollection } from 'geojson';
import L from 'leaflet';
import styled from 'styled-components';
import 'leaflet/dist/leaflet.css';
import KMLLayerManager from './KMLLayerManager';
import TurkeyBoundaries from './TurkeyBoundaries';
import { KMLLayerConfig } from '../../utils/kmlParser';

// Leaflet default marker icons düzeltmesi
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const MapContainerStyled = styled.div`
  height: 500px;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  
  .leaflet-container {
    height: 100%;
    width: 100%;
  }
`;

// Türkiye coğrafi sınırları - haritanın aşırı uzaklaştırılmasını engellemek için
const TURKEY_BOUNDS = L.latLngBounds([
  [34.5, 25.0], // güneybatı (lat, lng)
  [43.0, 46.0]  // kuzeydoğu (lat, lng)
]);

interface Coordinate {
  lat: number;
  lng: number;
}

interface KMLLayer {
  url: string;
  name: string;
  style?: {
    color?: string;
    weight?: number;
    fillOpacity?: number;
    fillColor?: string;
  };
}

interface CustomGeoJsonLayer {
  data: FeatureCollection | Feature;
  name?: string;
  style?: {
    color?: string;
    weight?: number;
    fillOpacity?: number;
    fillColor?: string;
  };
}

interface MapComponentProps {
  center?: [number, number];
  zoom?: number;
  onMapClick?: (coordinate: Coordinate) => void;
  selectedCoordinate?: Coordinate | null;
  showMarker?: boolean; // Marker gösterilsin mi?
  kmlLayers?: KMLLayer[];
  customGeoJsonLayers?: CustomGeoJsonLayer[];
  height?: string;
}

// Map ref interface - dışarıdan erişilebilir fonksiyonlar
export interface MapRef {
  zoomToLocation: (lat: number, lng: number, zoom?: number) => void;
  getMapInstance: () => L.Map | null;
}

// KML yükleme bileşeni - gerçek KML dosyalarını yüklemek için KMLLayerManager kullanır
const KMLLoader: React.FC<{ layers: KMLLayer[] }> = ({ layers }) => {
  // KMLLayer'ı KMLLayerConfig'e dönüştür
  const layerConfigs: KMLLayerConfig[] = layers.map(layer => ({
    name: layer.name,
    url: layer.url,
    style: layer.style,
    visible: true
  }));

  return (
    <KMLLayerManager 
      layerConfigs={layerConfigs}
      onLayersLoaded={(parsedLayers) => {
        console.log('KML katmanları yüklendi:', parsedLayers.map(l => l.name));
      }}
      onError={(error) => {
        console.error('KML katman yükleme hatası:', error);
      }}
    />
  );
};

const MapComponent = forwardRef<MapRef, MapComponentProps>(({
  center = [38.4237, 27.1428], // İzmir koordinatları
  zoom = 10,
  onMapClick,
  selectedCoordinate,
  showMarker = true, // Default olarak marker göster
  kmlLayers = [],
  customGeoJsonLayers = [],
  height = '500px'
}, ref) => {
  const mapRef = useRef<L.Map | null>(null);
  const fitBoundsDoneRef = useRef(false); // Sadece ilk açılışta fitBounds yapılacak

  // External API için ref expose etme
  useImperativeHandle(ref, () => ({
    zoomToLocation: (lat: number, lng: number, zoom = 15) => {
      if (mapRef.current) {
        mapRef.current.setView([lat, lng], zoom, {
          animate: true,
          duration: 1.5
        });
      }
    },
    getMapInstance: () => mapRef.current
  }), []);

  const handleMapClick = useCallback((e: L.LeafletMouseEvent) => {
    const coordinate: Coordinate = {
      lat: e.latlng.lat,
      lng: e.latlng.lng
    };
    
    onMapClick?.(coordinate);
    fitBoundsDoneRef.current = true; // Kullanıcı haritayla etkileşime geçtiyse fitBounds bir daha çalışmasın
  }, [onMapClick]);

  // İzmir KML sınırlarına fit ol (sadece ilk açılışta)
  useEffect(() => {
    if (!mapRef.current || !kmlLayers.length || fitBoundsDoneRef.current) return;
    // Sadece İzmir sınırları katmanı için fitBounds uygula
    const izmirKml = kmlLayers.find(k => k.name.includes('İzmir'));
    if (!izmirKml) return;
    fetch(izmirKml.url)
      .then(res => res.text())
      .then(kmlString => {
        // KML'i GeoJSON'a çevir
        const parser = new DOMParser();
        const kmlDoc = parser.parseFromString(kmlString, 'text/xml');
        const polygons = kmlDoc.getElementsByTagName('Polygon');
        let allCoords: [number, number][] = [];
        for (let i = 0; i < polygons.length; i++) {
          const linearRing = polygons[i].getElementsByTagName('LinearRing')[0];
          if (!linearRing) continue;
          const coordinates = linearRing.getElementsByTagName('coordinates')[0];
          if (!coordinates) continue;
          const coordString = coordinates.textContent?.trim();
          if (!coordString) continue;
          const coords = coordString.split(/\s+/).map(c => {
            const [lng, lat] = c.split(',').map(Number);
            return [lat, lng] as [number, number];
          });
          allCoords = allCoords.concat(coords);
        }
        if (allCoords.length && mapRef.current) {
          const bounds = L.latLngBounds(allCoords);
          mapRef.current.fitBounds(bounds, { padding: [window.innerWidth <= 600 ? 10 : 40, window.innerWidth <= 600 ? 10 : 40] });
          setTimeout(() => {
            const currentZoom = mapRef.current!.getZoom();
            mapRef.current!.setZoom(currentZoom + 1); // 1 seviye daha yakınlaştır
          }, 400);
          fitBoundsDoneRef.current = true; // fitBounds sadece ilk açılışta çalıştı
        }
      });
  }, [kmlLayers]);

  return (
    <MapContainerStyled style={{ height }}>
      
      <MapContainer
        center={center}
        zoom={zoom}
        minZoom={5}
        maxBounds={TURKEY_BOUNDS}
        maxBoundsViscosity={1}
        style={{ height: '100%', width: '100%' }}
      >
        {/* Uydu görüntüsü - mevcut sistemle uyumlu */}
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
          maxZoom={18}
        />
        
        {/* Türkiye il ve ilçe sınırları */}
        <TurkeyBoundaries />
        
        {/* KML katmanları */}
        {kmlLayers.length > 0 && <KMLLoader layers={kmlLayers} />}

        {/* Kullanıcıdan yüklenen veya custom GeoJSON katmanları */}
        {customGeoJsonLayers.map((layer, idx) => (
          <GeoJSON
            key={layer.name || `custom-geojson-${idx}`}
            data={layer.data as any}
            style={() => ({
              color: layer.style?.color || '#f97316',
              weight: layer.style?.weight || 3,
              fillOpacity: layer.style?.fillOpacity ?? 0.1,
              fillColor: layer.style?.fillColor || '#fb923c'
            })}
          />
        ))}
        
        {/* Seçilen koordinat marker'ı - sadece showMarker true ise göster */}
        {selectedCoordinate && showMarker && (
          <Marker position={[selectedCoordinate.lat, selectedCoordinate.lng]} />
        )}
        
        {/* Harita tıklama olayı */}
        <MapEventHandler onMapClick={handleMapClick} mapRef={mapRef} />
      </MapContainer>
    </MapContainerStyled>
  );
});

// Harita olaylarını yöneten bileşen
const MapEventHandler: React.FC<{ 
  onMapClick: (e: L.LeafletMouseEvent) => void;
  mapRef: React.MutableRefObject<L.Map | null>;
}> = ({ onMapClick, mapRef }) => {
  const map = useMap();

  useEffect(() => {
    // Map instance'ı ref'e kaydet
    if (mapRef.current !== map) {
      mapRef.current = map;
    }

    map.on('click', onMapClick);
    return () => {
      map.off('click', onMapClick);
    };
  }, [map, onMapClick, mapRef]);

  return null;
};

// forwardRef için displayName ekle
MapComponent.displayName = 'MapComponent';

export default MapComponent;
export type { Coordinate, KMLLayer };
