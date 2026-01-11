import { useState, useCallback } from 'react';
import { Coordinate } from '../components/Map/MapComponent';
import { checkCoordinate, CoordinateCheckResponse } from '../services/apiService';

interface CoordinateValidationResult {
  province: string | null;
  district: string | null;
  inClosedArea: boolean;
  inBigPlain: boolean;
  plainNames: string[];
  closedAreaNames: string[];
  loading: boolean;
  error?: string;
  apiResponse?: CoordinateCheckResponse;
}

export const useCoordinateValidation = () => {
  const [validationResult, setValidationResult] = useState<CoordinateValidationResult>({
    province: null,
    district: null,
    inClosedArea: false,
    inBigPlain: false,
    plainNames: [],
    closedAreaNames: [],
    loading: false
  });

  const validateCoordinate = useCallback(async (coordinate: Coordinate) => {
    setValidationResult(prev => ({ ...prev, loading: true, error: undefined }));

    try {
      const data = await checkCoordinate(coordinate.lat, coordinate.lng);
      
      setValidationResult({
        province: data.province || null,
        district: data.district || null,
        inClosedArea: (data.inside_yas_polygons?.length || 0) > 0,
        inBigPlain: (data.inside_ova_polygons?.length || 0) > 0,
        plainNames: data.inside_ova_polygons || [],
        closedAreaNames: data.inside_yas_polygons || [],
        loading: false,
        apiResponse: data
      });

    } catch (error) {
      console.error('Koordinat doğrulama hatası:', error);
      setValidationResult(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Bilinmeyen hata'
      }));
    }
  }, []);

  return {
    validationResult,
    validateCoordinate
  };
};

export const useMapState = () => {
  const [selectedCoordinate, setSelectedCoordinate] = useState<Coordinate | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>([39.0, 35.0]);
  const [mapZoom, setMapZoom] = useState(6);

  const updateMapView = useCallback((center: [number, number], zoom?: number) => {
    setMapCenter(center);
    if (zoom !== undefined) {
      setMapZoom(zoom);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedCoordinate(null);
  }, []);

  return {
    selectedCoordinate,
    setSelectedCoordinate,
    mapCenter,
    mapZoom,
    updateMapView,
    clearSelection
  };
};
