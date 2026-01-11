import React, { useEffect, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { KMLLoader, KMLLayerConfig, ParsedKMLLayer } from '../../utils/kmlParser';

interface KMLLayerManagerProps {
  layerConfigs: KMLLayerConfig[];
  onLayersLoaded?: (layers: ParsedKMLLayer[]) => void;
  onError?: (error: Error) => void;
  isDrawingMode?: boolean; // Çizim modu flag'i
}

const KMLLayerManager: React.FC<KMLLayerManagerProps> = ({
  layerConfigs,
  onLayersLoaded,
  onError,
  isDrawingMode = false
}) => {
  const map = useMap();
  const [loadedLayers, setLoadedLayers] = useState<L.GeoJSON[]>([]);

  useEffect(() => {
    const loadLayers = async () => {
      try {
        // Remove existing layers
        loadedLayers.forEach(layer => {
          if (map.hasLayer(layer)) {
            map.removeLayer(layer);
          }
        });

        if (layerConfigs.length === 0) {
          setLoadedLayers([]);
          return;
        }

        // Load new layers
        const parsedLayers = await KMLLoader.loadKMLLayers(layerConfigs);
        const leafletLayers: L.GeoJSON[] = [];

        parsedLayers.forEach((parsedLayer, index) => {
          if (parsedLayer.geoJson.features.length > 0) {
            const layer = L.geoJSON(parsedLayer.geoJson, {
              style: () => ({
                color: parsedLayer.style.color || '#3388ff',
                weight: parsedLayer.style.weight || 3,
                opacity: parsedLayer.style.opacity || 1,
                fillColor: 'transparent',
                fillOpacity: 0
              }),
              onEachFeature: (feature, layer) => {
                // Popup'ları tamamen devre dışı bırak - kullanıcı deneyimini bozmamak için
                // İzmir sınırları için popup gösterilmesin
              }
            });

            // Add layer to map if visible
            if (layerConfigs[index].visible !== false) {
              layer.addTo(map);
            }

            leafletLayers.push(layer);
          }
        });

        setLoadedLayers(leafletLayers);
        if (onLayersLoaded) {
          onLayersLoaded(parsedLayers);
        }
        
      } catch (error) {
        console.error('Error loading KML layers:', error);
        if (onError) {
          onError(error as Error);
        }
      }
    };

    loadLayers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(layerConfigs), map, isDrawingMode]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      loadedLayers.forEach(layer => {
        if (map.hasLayer(layer)) {
          map.removeLayer(layer);
        }
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
};

export default KMLLayerManager;
