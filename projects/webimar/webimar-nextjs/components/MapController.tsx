import { useMap } from 'react-leaflet';
import { useEffect } from 'react';

interface MapControllerProps {
  onMapReady: (map: any) => void;
}

const MapController = ({ onMapReady }: MapControllerProps) => {
  const map = useMap();
  
  useEffect(() => {
    if (map) {
      onMapReady(map);
    }
  }, [map, onMapReady]);
  
  return null;
};

export default MapController;
