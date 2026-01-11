import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { checkCoordinate, CoordinateCheckResponse } from '../services/apiService';
import { isWaterRestrictedArea, isLivestockCalculationType, getWaterRestrictionMessage } from '../utils/waterRestrictions';

interface MapCheckResult {
  province: string | null;
  district: string | null;
  insideOvaPolygons: string[];
  insideYasPolygons: string[];
  isWaterRestricted?: boolean;
}

interface LocationValidationState {
  selectedPoint: { lat: number; lng: number } | null;
  kmlCheckResult: MapCheckResult | null;
  isValidating: boolean;
  error: string | null;
  canProceedWithForm: boolean;
  suTahsisBelgesi: boolean | null;
  waterRestricted: boolean;
}

interface LocationValidationContextType {
  state: LocationValidationState;
  setSelectedPoint: (point: { lat: number; lng: number } | null) => void;
  validateLocation: (point: { lat: number; lng: number }) => Promise<void>;
  setSuTahsisBelgesi: (value: boolean) => void;
  clearValidation: () => void;
  canUserProceedWithCalculation: (calculationType?: string) => boolean;
  isWaterRestrictedForLivestock: (calculationType?: string) => boolean;
}

const LocationValidationContext = createContext<LocationValidationContextType | undefined>(undefined);

const initialState: LocationValidationState = {
  selectedPoint: null,
  kmlCheckResult: null,
  isValidating: false,
  error: null,
  canProceedWithForm: false,
  suTahsisBelgesi: null,
  waterRestricted: false
};

export const LocationValidationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<LocationValidationState>(initialState);

  const setSelectedPoint = useCallback((point: { lat: number; lng: number } | null) => {
    setState(prev => ({
      ...prev,
      selectedPoint: point,
      kmlCheckResult: null,
      error: null,
      canProceedWithForm: false,
      suTahsisBelgesi: null,
      waterRestricted: false
    }));
  }, []);

  const validateLocation = useCallback(async (point: { lat: number; lng: number }) => {
    setState(prev => ({ ...prev, isValidating: true, error: null }));

    try {
      const result: CoordinateCheckResponse = await checkCoordinate(point.lat, point.lng);

      const normalized: MapCheckResult = {
        province: result.province || null,
        district: result.district || null,
        insideOvaPolygons: result.inside_ova_polygons || result.inside_polygons || [],
        insideYasPolygons: result.inside_yas_polygons || result.inside_kapali_alan_polygons || [],
        isWaterRestricted: isWaterRestrictedArea(result.province, result.district)
      };

      setState(prev => ({
        ...prev,
        kmlCheckResult: normalized,
        isValidating: false,
        canProceedWithForm: true,
        waterRestricted: normalized.isWaterRestricted || false
      }));
    } catch (error) {
      console.error('❌ LocationValidation: KML check failed', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Konum doğrulama hatası',
        isValidating: false,
        canProceedWithForm: false
      }));
    }
  }, []);

  const setSuTahsisBelgesi = useCallback((value: boolean) => {
    setState(prev => ({ ...prev, suTahsisBelgesi: value }));
  }, []);

  const clearValidation = useCallback(() => {
    setState(initialState);
  }, []);

  const canUserProceedWithCalculation = useCallback((calculationType?: string) => {
    const { kmlCheckResult, waterRestricted } = state;

    // Konum seçilmemişse hesaplama yapılamaz.
    if (!kmlCheckResult) {
      return false;
    }

    // Su kısıtı kontrolü - büyükbaş hayvancılık için
    if (waterRestricted && isLivestockCalculationType(calculationType)) {
      return false;
    }

    // Su tahsis belgesi gibi diğer tüm kontroller backend'de uyarı olarak ele alınacaktır.
    // Bu fonksiyon sadece temel harita ve konum geçerliliği için kullanılır.
    return true;
  }, [state]);

  const isWaterRestrictedForLivestock = useCallback((calculationType?: string) => {
    return state.waterRestricted && isLivestockCalculationType(calculationType);
  }, [state]);

  // Auto validate when point changes
  useEffect(() => {
    if (state.selectedPoint && !state.kmlCheckResult && !state.isValidating) {
      validateLocation(state.selectedPoint);
    }
  }, [state.selectedPoint, state.kmlCheckResult, state.isValidating, validateLocation]);

  const contextValue: LocationValidationContextType = {
    state,
    setSelectedPoint,
    validateLocation,
    setSuTahsisBelgesi,
    clearValidation,
    canUserProceedWithCalculation,
    isWaterRestrictedForLivestock
  };

  return (
    <LocationValidationContext.Provider value={contextValue}>
      {children}
    </LocationValidationContext.Provider>
  );
};

export const useLocationValidation = () => {
  const context = useContext(LocationValidationContext);
  if (context === undefined) {
    throw new Error('useLocationValidation must be used within a LocationValidationProvider');
  }
  return context;
};
