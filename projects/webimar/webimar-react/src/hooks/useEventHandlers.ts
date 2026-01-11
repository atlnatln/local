// Custom hook for centralized event handling
// This file implements event handler abstraction and standardization

import { useCallback } from 'react';
import { DrawnPolygon } from '../components/Map/PolygonDrawer';

// Types for event handling
export interface EventHandlerContext {
  // State update functions
  setTarlaPolygon: (polygon: DrawnPolygon | null) => void;
  setDikiliPolygon: (polygon: DrawnPolygon | null) => void;
  setZeytinlikPolygon: (polygon: DrawnPolygon | null) => void;
  setDrawingMode: (mode: 'tarla' | 'dikili' | 'zeytinlik' | null) => void;
  triggerEdit: (polygonIndex: number) => void;
  updateField: (field: string, value: any) => void;

  // Current state values
  tarlaPolygon: DrawnPolygon | null;
  dikiliPolygon: DrawnPolygon | null;
  zeytinlikPolygon: DrawnPolygon | null;
  drawingMode: 'tarla' | 'dikili' | 'zeytinlik' | null;
}

export interface StandardizedCallbacks {
  onPolygonComplete: (polygon: DrawnPolygon) => void;
  onPolygonClear: () => void;
  onPolygonEdit: (polygon: DrawnPolygon, index: number) => void;
  onDrawingModeChange: (mode: 'tarla' | 'dikili' | 'zeytinlik' | null) => void;
  onAreaDisplayEdit: (type: 'tarla' | 'dikili' | 'zeytinlik') => void;
  onTabChange: (tab: 'manuel' | 'harita') => void;
}

export interface ErrorHandler {
  handleError: (error: Error, context: string) => void;
  showUserError: (message: string) => void;
  logError: (error: any, context: string) => void;
}

// Custom hook for centralized event handling
export const useEventHandlers = (context: EventHandlerContext): {
  callbacks: StandardizedCallbacks;
  errorHandler: ErrorHandler;
} => {

  // Centralized error handling
  const handleError = useCallback((error: Error, context: string) => {
    console.error(`❌ [${context}] Error:`, error);

    // Log to error tracking service in production
    if (process.env.NODE_ENV === 'production') {
      // Here you would integrate with error tracking service
      // e.g., Sentry, LogRocket, etc.
    }
  }, []);

  const showUserError = useCallback((message: string) => {
    // Standardized user error display
    alert(message); // In production, use a better notification system
  }, []);

  const logError = useCallback((error: any, context: string) => {
    console.error(`⚠️ [${context}] Warning:`, error);
  }, []);

  // Polygon completion handler
  const onPolygonComplete = useCallback((polygon: DrawnPolygon) => {
    try {
      console.log('✅ handlePolygonComplete çağrıldı:', {
        drawingMode: context.drawingMode,
        area: polygon.area
      });

      if (context.drawingMode === 'tarla') {
        console.log('🟤 Tarla polygon set ediliyor:', polygon);
        context.setTarlaPolygon(polygon);
        context.updateField('tarlaAlani', Math.round(polygon.area));
      } else if (context.drawingMode === 'dikili') {
        console.log('🟢 Dikili polygon set ediliyor:', polygon);
        context.setDikiliPolygon(polygon);
        context.updateField('dikiliAlan', Math.round(polygon.area));
      } else if (context.drawingMode === 'zeytinlik') {
        console.log('🫒 Zeytinlik polygon set ediliyor:', polygon);
        context.setZeytinlikPolygon(polygon);
        context.updateField('zeytinlikAlani', Math.round(polygon.area));
      } else {
        logError('Invalid drawing mode', 'onPolygonComplete');
      }
    } catch (error) {
      handleError(error as Error, 'onPolygonComplete');
      showUserError('Polygon kaydetme sırasında hata oluştu.');
    }
  }, [context, handleError, showUserError, logError]);

  // Polygon clear handler - çizim sırasında mode korunmalı
  const onPolygonClear = useCallback(() => {
    try {
      console.log('🧹 onPolygonClear çağrıldı, mevcut state:', {
        drawingMode: context.drawingMode,
        tarlaPolygon: !!context.tarlaPolygon,
        dikiliPolygon: !!context.dikiliPolygon,
        zeytinlikPolygon: !!context.zeytinlikPolygon
      });

      // Eğer aktif çizim modu varsa, sadece o mode'un önceki polygon'unu temizle
      // (yeni çizim başladığında eski polygon'u kaldır, ama mode'u koru)
      if (context.drawingMode === 'tarla') {
        context.setTarlaPolygon(null);
        context.updateField('tarlaAlani', 0);
        console.log('🧹 Tarla polygon state\'i temizlendi (mode korundu)');
        // Drawing mode'u koruyoruz - setDrawingMode çağrılmıyor
      } else if (context.drawingMode === 'dikili') {
        context.setDikiliPolygon(null);
        context.updateField('dikiliAlan', 0);
        console.log('🧹 Dikili polygon state\'i temizlendi (mode korundu)');
        // Drawing mode'u koruyoruz - setDrawingMode çağrılmıyor
      } else if (context.drawingMode === 'zeytinlik') {
        context.setZeytinlikPolygon(null);
        context.updateField('zeytinlikAlani', 0);
        console.log('🧹 Zeytinlik polygon state\'i temizlendi (mode korundu)');
        // Drawing mode'u koruyoruz - setDrawingMode çağrılmıyor
      } else {
        // Drawing mode null ise (tamamen temizle komutu), hepsini temizle
        context.setTarlaPolygon(null);
        context.setDikiliPolygon(null);
        context.setZeytinlikPolygon(null);
        context.updateField('tarlaAlani', 0);
        context.updateField('dikiliAlan', 0);
        context.updateField('zeytinlikAlani', 0);
        context.setDrawingMode(null);
        console.log('🧹 Tüm polygon state\'leri tamamen temizlendi');
      }
    } catch (error) {
      handleError(error as Error, 'onPolygonClear');
      showUserError('Polygon temizleme sırasında hata oluştu.');
    }
  }, [context, handleError, showUserError]);

  // Polygon edit handler (DÜZELTİLMİŞ HALİ)
  const onPolygonEdit = useCallback((polygon: DrawnPolygon, index: number) => {
    try {
      console.log('✏️ Polygon düzenlendi:', { polygon, index });

      // Poligonların sırası: Tarla (varsa 0), Dikili (varsa sonra), Zeytinlik (varsa sonra)
      let tarlaIndex = -1;
      let dikiliIndex = -1;
      let zeytinlikIndex = -1;
      let idx = 0;
      if (context.tarlaPolygon) { tarlaIndex = idx++; }
      if (context.dikiliPolygon) { dikiliIndex = idx++; }
      if (context.zeytinlikPolygon) { zeytinlikIndex = idx++; }

      if (index === tarlaIndex) {
        context.setTarlaPolygon(polygon);
        context.updateField('tarlaAlani', Math.round(polygon.area));
      } else if (index === dikiliIndex) {
        context.setDikiliPolygon(polygon);
        context.updateField('dikiliAlan', Math.round(polygon.area));
      } else if (index === zeytinlikIndex) {
        context.setZeytinlikPolygon(polygon);
        context.updateField('zeytinlikAlani', Math.round(polygon.area));
      } else {
        logError(`Invalid polygon edit configuration: index=${index}`, 'onPolygonEdit');
      }
    } catch (error) {
      handleError(error as Error, 'onPolygonEdit');
      showUserError('Polygon düzenleme sırasında hata oluştu.');
    }
  }, [context, handleError, showUserError, logError]);

  // Drawing mode change handler
  const onDrawingModeChange = useCallback((mode: 'tarla' | 'dikili' | 'zeytinlik' | null) => {
    try {
      console.log('🎯 DikiliAlanKontrol handleDrawingModeChange çağrıldı:', mode);
      context.setDrawingMode(mode);
    } catch (error) {
      handleError(error as Error, 'onDrawingModeChange');
      showUserError('Çizim modu değiştirme sırasında hata oluştu.');
    }
  }, [context, handleError, showUserError]);

  // Area display edit handler (for edit buttons on area display)
  const onAreaDisplayEdit = useCallback((type: 'tarla' | 'dikili' | 'zeytinlik') => {
    try {
      if (type === 'tarla') {
        console.log('🎯 Tarla edit butonu tıklandı!');
        context.triggerEdit(0);
      } else if (type === 'dikili') {
        console.log('🎯 Dikili edit butonu tıklandı!');
        const dikiliIndex = context.tarlaPolygon ? 1 : 0;
        context.triggerEdit(dikiliIndex);
      } else if (type === 'zeytinlik') {
        console.log('🎯 Zeytinlik edit butonu tıklandı!');
        let zeytinlikIndex = 0;
        if (context.tarlaPolygon) zeytinlikIndex++;
        if (context.dikiliPolygon) zeytinlikIndex++;
        context.triggerEdit(zeytinlikIndex);
      }
    } catch (error) {
      handleError(error as Error, 'onAreaDisplayEdit');
      showUserError('Alan düzenleme modunu başlatma sırasında hata oluştu.');
    }
  }, [context, handleError, showUserError]);

  // Tab change handler
  const onTabChange = useCallback((tab: 'manuel' | 'harita') => {
    try {
      // Haritadan manuel'e geçişte alan bilgilerini koru
      if (tab === 'manuel') {
        // Haritadan alınan alan bilgileri zaten state'te mevcut
      }
      // Actual tab change logic would be handled by parent component
    } catch (error) {
      handleError(error as Error, 'onTabChange');
      showUserError('Sekme değiştirme sırasında hata oluştu.');
    }
  }, [handleError, showUserError]);

  // Return standardized callbacks and error handler
  return {
    callbacks: {
      onPolygonComplete,
      onPolygonClear,
      onPolygonEdit,
      onDrawingModeChange,
      onAreaDisplayEdit,
      onTabChange
    },
    errorHandler: {
      handleError,
      showUserError,
      logError
    }
  };
};

// Additional utility functions for event handling standardization

export const createEventLogger = (componentName: string) => ({
  logEvent: (eventName: string, data?: any) => {
    console.log(`📝 [${componentName}] ${eventName}:`, data);
  },
  logError: (eventName: string, error: any) => {
    console.error(`❌ [${componentName}] ${eventName} Error:`, error);
  },
  logWarning: (eventName: string, message: string) => {
    console.warn(`⚠️ [${componentName}] ${eventName} Warning:`, message);
  }
});

// Validation utilities for event parameters
export const validatePolygonData = (polygon: DrawnPolygon): boolean => {
  try {
    return !!(
      polygon &&
      polygon.points &&
      Array.isArray(polygon.points) &&
      polygon.points.length >= 3 &&
      typeof polygon.area === 'number' &&
      polygon.area > 0
    );
  } catch {
    return false;
  }
};

export const validateDrawingMode = (mode: any): mode is 'tarla' | 'dikili' | null => {
  return mode === null || mode === 'tarla' || mode === 'dikili';
};
