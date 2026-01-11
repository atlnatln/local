import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import * as turf from '@turf/turf';
import { useMap, useMapEvents } from 'react-leaflet';
import styled from 'styled-components';
// Global CSS for polygon drawing markers and tooltips
const GlobalStyle = `
  /* Sadece mobilde harita üstü temizle butonu göster */
  .polygon-clear-mobile { display: none !important; }
  @media (max-width: 600px) {
    .polygon-clear-mobile { display: block !important; }
  }

  .polygon-tooltip {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid #3498db !important;
    border-radius: 4px !important;
    padding: 6px 8px !important;
    font-size: 11px !important;
    color: #2c3e50 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
  }
  .edit-marker {
    z-index: 1000 !important;
    pointer-events: auto !important;
    cursor: move !important;
  }
  .draggable-marker {
    z-index: 1000 !important;
    pointer-events: auto !important;
  }
  .draggable-marker .marker-handle {
    width: 20px !important;
    height: 20px !important;
    background: #e67e22 !important;
    border: 4px solid white !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6) !important;
    cursor: move !important;
    pointer-events: auto !important;
    position: absolute !important;
    top: 1px !important;
    left: 1px !important;
    z-index: 1001 !important;
    animation: pulse 2s infinite !important;
  }
  @keyframes pulse {
    0% { box-shadow: 0 4px 12px rgba(0,0,0,0.6), 0 0 0 0 rgba(230, 126, 34, 0.7); }
    70% { box-shadow: 0 4px 12px rgba(0,0,0,0.6), 0 0 0 10px rgba(230, 126, 34, 0); }
    100% { box-shadow: 0 4px 12px rgba(0,0,0,0.6), 0 0 0 0 rgba(230, 126, 34, 0); }
  }
  .draggable-marker:hover .marker-handle {
    transform: scale(1.2) !important;
    background: #d35400 !important;
  }


`;

// Inject styles once
if (typeof document !== 'undefined' && !document.getElementById('polygon-drawer-style')) {
  const style = document.createElement('style');
  style.id = 'polygon-drawer-style';
  style.textContent = GlobalStyle;
  document.head.appendChild(style);
}

// Styled components
const DrawingControls = styled.div`
  /* Sadece masaüstünde göster */
  display: none;
  @media (min-width: 601px) {
    display: block;
  }
`;

const DrawingModeContainer = styled.div`
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.98);
  border: 2px solid #34495e;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  min-width: 320px;
`;

const DrawingModeButton = styled.button<{ $active: boolean; $color: string }>`
  padding: 10px 16px;
  margin-right: 8px;
  margin-bottom: 8px;
  border: 2px solid ${props => props.$color};
  background: ${props => props.$active ? props.$color : 'white'};
  color: ${props => props.$active ? 'white' : props.$color};
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$color};
    color: white;
  }
`;

// Interfaces
interface PolygonPoint {
  lat: number;
  lng: number;
}

interface DrawnPolygon {
  points: PolygonPoint[];
  area: number;
}

interface PolygonDrawerProps {
  onPolygonComplete?: (polygon: DrawnPolygon) => void;
  onPolygonClear?: () => void;
  onDrawingStateChange?: (isDrawing: boolean) => void;
  onPolygonEdit?: (polygon: DrawnPolygon, index: number) => void;
  disabled?: boolean;
  polygonColor?: string;
  polygonName?: string;
  hideControls?: boolean;
  existingPolygons?: Array<{
    polygon: DrawnPolygon;
    color: string;
    name: string;
    id?: string;
  }>;
  drawingMode?: 'tarla' | 'dikili' | 'zeytinlik' | null;
  onDrawingModeChange?: (mode: 'tarla' | 'dikili' | 'zeytinlik' | null) => void;
  showDrawingModeControls?: boolean;
  externalEditTrigger?: { timestamp: number; polygonIndex: number };
}

const PolygonDrawer: React.FC<PolygonDrawerProps> = ({
  onPolygonComplete,
  onPolygonClear,
  onDrawingStateChange,
  onPolygonEdit,
  disabled = false,
  polygonColor = '#e74c3c',
  polygonName = 'Polygon',
  hideControls = false,
  existingPolygons = [],
  drawingMode = null,
  onDrawingModeChange,
  showDrawingModeControls = false,
  externalEditTrigger = { timestamp: 0, polygonIndex: -1 }
}) => {
  const map = useMap();

  // Core state
  const [isDrawing, setIsDrawing] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number>(-1);
  const [currentPoints, setCurrentPoints] = useState<PolygonPoint[]>([]);

  // Layer references
  const drawingLayerRef = useRef<L.LayerGroup | null>(null);
  const polygonsLayerRef = useRef<L.LayerGroup | null>(null);
  const editLayerRef = useRef<L.LayerGroup | null>(null);

  // Edit state refs
  const editingPointsRef = useRef<PolygonPoint[]>([]);
  const editMarkersRef = useRef<L.Marker[]>([]);
  const dragThrottleRef = useRef<{ [key: number]: NodeJS.Timeout }>({});
  const startEditModeRef = useRef<((index: number) => void) | null>(null);

  // Leaflet Control: Tamamla ve Temizle butonları
  const leafletCompleteControl = useRef<L.Control | null>(null);
  const leafletClearControl = useRef<L.Control | null>(null);

  // Initialize layers
  useEffect(() => {
    if (!drawingLayerRef.current) {
      drawingLayerRef.current = L.layerGroup().addTo(map);
    }
    if (!polygonsLayerRef.current) {
      polygonsLayerRef.current = L.layerGroup().addTo(map);
    }
    if (!editLayerRef.current) {
      if (!map.getPane('editPane')) {
        const editPane = map.createPane('editPane');
        editPane.style.zIndex = '999';
      }
      editLayerRef.current = L.layerGroup().addTo(map);
    }

    return () => {
      // Copy ref to a variable to avoid React warning about ref changing
      // eslint-disable-next-line react-hooks/exhaustive-deps
      const dragThrottle = dragThrottleRef.current;
      [drawingLayerRef, polygonsLayerRef, editLayerRef].forEach(ref => {
        if (ref.current) {
          map.removeLayer(ref.current);
          ref.current = null;
        }
      });
      // eslint-disable-next-line react-hooks/exhaustive-deps
      Object.values(dragThrottle).forEach(clearTimeout);
    };
  }, [map]);

  // Leaflet Control for "Tamamla" (like ZoomControl) ve "Temizle"
  useEffect(() => {
    // --- TAMAMLA BUTONU ---
    if (!(isDrawing || editingIndex >= 0)) {
      if (leafletCompleteControl.current) {
        leafletCompleteControl.current.remove();
        leafletCompleteControl.current = null;
      }
    } else {
      if (leafletCompleteControl.current) {
        leafletCompleteControl.current.remove();
        leafletCompleteControl.current = null;
      }
      const CompleteControl = L.Control.extend({
        onAdd: function (map: L.Map) {
          const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
          const button = L.DomUtil.create('a', '', container);
          button.innerHTML = '✅';
          button.title = isDrawing
            ? 'Poligonu tamamla'
            : 'Düzenlemeyi bitir';
          button.href = '#';
          if (isDrawing && currentPoints.length < 3) {
            button.className = 'leaflet-disabled';
          }
          L.DomEvent.on(button, 'click', function (e) {
            L.DomEvent.stopPropagation(e);
            L.DomEvent.preventDefault(e);
            if (isDrawing) {
              if (currentPoints.length >= 3) completePolygon();
            } else if (editingIndex >= 0) {
              stopEditMode();
            }
          });
          return container;
        },
        onRemove: function () {}
      });
      leafletCompleteControl.current = new CompleteControl({ position: 'topleft' });
      leafletCompleteControl.current.addTo(map);
    }

    // --- TEMİZLE BUTONU ---
    // Sadece poligon çizimi tamamlandıysa göster
    const hasCompletedPolygons = existingPolygons.length > 0 && !isDrawing && editingIndex < 0;
    if (leafletClearControl.current) {
      leafletClearControl.current.remove();
      leafletClearControl.current = null;
    }
    if (hasCompletedPolygons) {
      const ClearControl = L.Control.extend({
        onAdd: function (map: L.Map) {
          const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom polygon-clear-mobile');
          const button = L.DomUtil.create('a', '', container);
          button.innerHTML = '🗑️';
          button.title = 'Tüm poligonları temizle';
          button.href = '#';
          L.DomEvent.on(button, 'click', function (e) {
            L.DomEvent.stopPropagation(e);
            L.DomEvent.preventDefault(e);
            polygonsLayerRef.current?.clearLayers();
            onPolygonClear?.();
          });
          return container;
        },
        onRemove: function () {}
      });
      leafletClearControl.current = new ClearControl({ position: 'topright' });
      leafletClearControl.current.addTo(map);
    }

    // Cleanup
    return () => {
      if (leafletCompleteControl.current) {
        leafletCompleteControl.current.remove();
        leafletCompleteControl.current = null;
      }
      if (leafletClearControl.current) {
        leafletClearControl.current.remove();
        leafletClearControl.current = null;
      }
    };
    // currentPoints.length intentionally not in dependencies for performance
    // eslint-disable-next-line
  }, [isDrawing, editingIndex, map, currentPoints.length, onPolygonClear]);

  // Update drawing visual
  const updateDrawingVisual = useCallback((points: PolygonPoint[]) => {
    if (!drawingLayerRef.current) return;

    drawingLayerRef.current.clearLayers();

    if (points.length === 0) return;

    points.forEach((point, index) => {
      const circle = L.circleMarker([point.lat, point.lng], {
        color: polygonColor,
        fillColor: polygonColor,
        fillOpacity: 0.8,
        radius: 5,
        weight: 2
      });

      circle.bindTooltip(`Nokta ${index + 1}`, {
        permanent: false,
        direction: 'top',
        offset: [0, -10],
        className: 'polygon-tooltip'
      });

      circle.addTo(drawingLayerRef.current!);
    });

    if (points.length > 1) {
      const polyline = L.polyline(points.map(p => [p.lat, p.lng]), {
        color: polygonColor,
        weight: 2,
        dashArray: '5, 5'
      });
      polyline.addTo(drawingLayerRef.current!);
    }

    if (points.length >= 3) {
      const polygon = L.polygon(points.map(p => [p.lat, p.lng]), {
        color: polygonColor,
        weight: 2,
        fillColor: polygonColor,
        fillOpacity: 0.2
      });
      polygon.addTo(drawingLayerRef.current!);
    }
  }, [polygonColor]);

  // Update edit visual
  const updateEditVisual = useCallback((points: PolygonPoint[]) => {
    if (!editLayerRef.current || points.length < 3) return;

    editLayerRef.current.eachLayer((layer: any) => {
      if (layer instanceof L.Polygon) {
        editLayerRef.current!.removeLayer(layer);
      }
    });

    const polygon = L.polygon(points.map(p => [p.lat, p.lng]), {
      color: '#e67e22',
      weight: 2,
      fillColor: '#e67e22',
      fillOpacity: 0.3,
      dashArray: '5, 5'
    });

    polygon.addTo(editLayerRef.current);
  }, []);

  // Start drawing
  const startDrawing = useCallback(() => {
    if (disabled) return;

    setIsDrawing(true);
    setCurrentPoints([]);
    setEditingIndex(-1);
    onDrawingStateChange?.(true);

    editLayerRef.current?.clearLayers();
    editMarkersRef.current = [];

    map.doubleClickZoom.disable();
  }, [disabled, onDrawingStateChange, map]);

  // Stop drawing
  const stopDrawing = useCallback(() => {
    setIsDrawing(false);
    onDrawingStateChange?.(false);
    drawingLayerRef.current?.clearLayers();
    setCurrentPoints([]);
    map.doubleClickZoom.enable();
  }, [onDrawingStateChange, map]);

  // Complete polygon
  const completePolygon = useCallback(() => {
    if (currentPoints.length < 3) return;

    try {
      const coordinates = [...currentPoints.map(p => [p.lng, p.lat]), [currentPoints[0].lng, currentPoints[0].lat]];
      const turfPolygon = turf.polygon([coordinates]);
      const area = turf.area(turfPolygon);

      const completedPolygon: DrawnPolygon = {
        points: currentPoints,
        area: Math.round(area)
      };

      onPolygonComplete?.(completedPolygon);
      stopDrawing();
      onDrawingModeChange?.(null);
    } catch (error) {
      console.error('Polygon tamamlama hatası:', error);
    }
  }, [currentPoints, onPolygonComplete, stopDrawing, onDrawingModeChange]);

  // Add permanent polygon to map
  const addPermanentPolygon = useCallback((
    polygonData: DrawnPolygon,
    color: string,
    name: string,
    uniqueId?: string
  ) => {
    if (!polygonsLayerRef.current || polygonData.points.length < 3) return;

    const polygon = L.polygon(polygonData.points.map(p => [p.lat, p.lng]), {
      color: color,
      weight: 2,
      fillColor: color,
      fillOpacity: 0.3
    });

    (polygon as any).options.polygonId = uniqueId || `${name}-${Date.now()}`;

    const areaText = polygonData.area >= 10000
      ? `${(polygonData.area / 10000).toFixed(2)} hektar`
      : `${polygonData.area} m²`;

    polygon.bindTooltip(`${name}: ${areaText}`, {
      permanent: false,
      direction: 'top',
      offset: [0, -10],
      className: 'polygon-tooltip'
    });

    polygon.on('click', () => {
      if (isDrawing) return;
      const polygonsArray = existingPolygons;
      const index = polygonsArray.findIndex(item => {
        if (item.id === uniqueId) return true;
        return item.polygon.points.length === polygonData.points.length &&
               Math.abs(item.polygon.area - polygonData.area) < 100 &&
               item.polygon.points.every((point, i) =>
                 Math.abs(point.lat - polygonData.points[i].lat) < 0.000001 &&
                 Math.abs(point.lng - polygonData.points[i].lng) < 0.000001
               );
      });
      if (index >= 0) {
        startEditModeRef.current?.(index);
      }
    });

    polygon.addTo(polygonsLayerRef.current);
  }, [existingPolygons, isDrawing]);

  // Start new edit helper function
  const startNewEdit = useCallback((polygonIndex: number) => {
    polygonsLayerRef.current?.eachLayer((layer: any) => {
      layer.setStyle({ opacity: 0.8, fillOpacity: 0.3 });
    });
    setEditingIndex(polygonIndex);
    setIsDrawing(false);
    const points = existingPolygons[polygonIndex].polygon.points;
    editingPointsRef.current = [...points];
    setCurrentPoints([...points]);

    editLayerRef.current?.clearLayers();
    editMarkersRef.current = [];

    points.forEach((point, index) => {
      const marker = L.marker([point.lat, point.lng], {
        draggable: true,
        interactive: true,
        bubblingMouseEvents: false,
        zIndexOffset: 1000,
        pane: 'editPane',
        icon: L.divIcon({
          html: '<div class="marker-handle"></div>',
          className: 'edit-marker draggable-marker',
          iconSize: [22, 22],
          iconAnchor: [11, 11]
        })
      });

      marker.on('dragstart', () => {
        map.dragging.disable();
        map.touchZoom.disable();
        map.doubleClickZoom.disable();
        map.scrollWheelZoom.disable();
        map.boxZoom.disable();
        map.keyboard.disable();
      });

      marker.on('drag', (e: any) => {
        const newLatLng = e.target.getLatLng();
        const updatedPoints = [...editingPointsRef.current];
        updatedPoints[index] = { lat: newLatLng.lat, lng: newLatLng.lng };
        editingPointsRef.current = updatedPoints;
        setCurrentPoints([...updatedPoints]);
        updateEditVisual(updatedPoints);

        if (onPolygonEdit && updatedPoints.length >= 3) {
          try {
            const coordinates = [...updatedPoints.map(p => [p.lng, p.lat]), [updatedPoints[0].lng, updatedPoints[0].lat]];
            const turfPolygon = turf.polygon([coordinates]);
            const area = turf.area(turfPolygon);

            const editedPolygon: DrawnPolygon = {
              points: updatedPoints,
              area: Math.round(area)
            };

            onPolygonEdit(editedPolygon, polygonIndex);
          } catch (error) {
            console.error('Drag sırasında alan hesaplama hatası:', error);
          }
        }
      });

      marker.on('dragend', () => {
        map.dragging.enable();
        map.touchZoom.enable();
        map.doubleClickZoom.enable();
        map.scrollWheelZoom.enable();
        map.boxZoom.enable();
        map.keyboard.enable();
      });

      marker.addTo(editLayerRef.current!);
      editMarkersRef.current.push(marker);
    });

    polygonsLayerRef.current?.eachLayer((layer: any) => {
      const targetId = existingPolygons[polygonIndex].id;
      if (layer.options?.polygonId === targetId) {
        layer.setStyle({ opacity: 0, fillOpacity: 0 });
      }
    });

    setTimeout(() => {
      updateEditVisual(points);
    }, 50);
  }, [existingPolygons, onPolygonEdit, updateEditVisual, map]);

  // Start edit mode
  const startEditMode = useCallback((polygonIndex: number) => {
    if (isDrawing || !existingPolygons[polygonIndex]) return;
    if (editingIndex === polygonIndex) return;
    if (editingIndex >= 0) {
      editLayerRef.current?.clearLayers();
      editMarkersRef.current = [];
      editingPointsRef.current = [];
      setEditingIndex(-1);
      setTimeout(() => {
        startNewEdit(polygonIndex);
      }, 100);
      return;
    }
    startNewEdit(polygonIndex);
  }, [isDrawing, existingPolygons, editingIndex, startNewEdit]);

  useEffect(() => {
    startEditModeRef.current = startEditMode;
  }, [startEditMode]);

  // Stop edit mode
  const stopEditMode = useCallback(() => {
    if (editingIndex < 0) return;
    editLayerRef.current?.clearLayers();
    editMarkersRef.current = [];
    editingPointsRef.current = [];
    setEditingIndex(-1);
    setIsDrawing(false);
  }, [editingIndex]);

  // Load existing polygons
  useEffect(() => {
    if (editingIndex >= 0) return;
    polygonsLayerRef.current?.clearLayers();
    existingPolygons.forEach((item, index) => {
      addPermanentPolygon(item.polygon, item.color, item.name, item.id);
    });
  }, [existingPolygons, editingIndex, addPermanentPolygon]);

  // Global clear function
  useEffect(() => {
    const handleClearRequest = () => {
      polygonsLayerRef.current?.clearLayers();
      drawingLayerRef.current?.clearLayers();
      editLayerRef.current?.clearLayers();
      setCurrentPoints([]);
      setEditingIndex(-1);
      editMarkersRef.current = [];
      editingPointsRef.current = [];
    };
    if (typeof window !== 'undefined') {
      (window as any).__polygonDrawerClear = handleClearRequest;
    }
    return () => {
      if (typeof window !== 'undefined') {
        delete (window as any).__polygonDrawerClear;
      }
    };
  }, []);

  // Drawing mode change handler
  const handleModeChange = useCallback((mode: 'tarla' | 'dikili' | 'zeytinlik') => {
    if (drawingMode === mode && isDrawing) return;
    onDrawingModeChange?.(mode);
    setTimeout(() => startDrawing(), 50);
  }, [drawingMode, isDrawing, onDrawingModeChange, startDrawing]);

  // Auto-start/stop drawing when mode changes (but not during edit)
  useEffect(() => {
    if (editingIndex >= 0) return;
    if (drawingMode && !isDrawing) {
      startDrawing();
    } else if (!drawingMode && isDrawing) {
      stopDrawing();
    }
  }, [drawingMode, isDrawing, editingIndex, startDrawing, stopDrawing]);

  // Listen for external edit triggers (with throttling)
  const lastEditTriggerRef = useRef<number>(0);
  useEffect(() => {
    if (externalEditTrigger &&
        externalEditTrigger.timestamp > 0 &&
        externalEditTrigger.timestamp > lastEditTriggerRef.current &&
        externalEditTrigger.polygonIndex >= 0) {
      lastEditTriggerRef.current = externalEditTrigger.timestamp;
      const { polygonIndex } = externalEditTrigger;
      if (polygonIndex < existingPolygons.length) {
        startEditMode(polygonIndex);
      }
    }
  }, [externalEditTrigger, startEditMode, existingPolygons]);

  // Enhanced map click handler with double-click detection
  const lastClickTimeRef = useRef<number>(0);
  const handleMapClickWithDoubleClick = useCallback((e: L.LeafletMouseEvent) => {
    const currentTime = Date.now();
    const timeDiff = currentTime - lastClickTimeRef.current;
    // Çift tıklama aralığını 300ms'ye düşür (eski: 500ms)
    if (timeDiff < 300 && isDrawing && currentPoints.length >= 3) {
      completePolygon();
      lastClickTimeRef.current = 0;
      return;
    }
    lastClickTimeRef.current = currentTime;
    if (!isDrawing || editingIndex >= 0) return;
    const newPoint: PolygonPoint = {
      lat: e.latlng.lat,
      lng: e.latlng.lng
    };
    setCurrentPoints(prev => {
      const newPoints = [...prev, newPoint];
      updateDrawingVisual(newPoints);
      return newPoints;
    });
  }, [isDrawing, editingIndex, currentPoints.length, completePolygon, updateDrawingVisual]);

  // Map events
  useMapEvents({
    click: handleMapClickWithDoubleClick,
    dblclick: (e) => {
      e.originalEvent?.preventDefault();
      if (isDrawing && currentPoints.length >= 3) {
        completePolygon();
      }
    }
  });

  // ESC key handler to stop drawing
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isDrawing) {
          stopDrawing();
        } else if (editingIndex >= 0) {
          stopEditMode();
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isDrawing, editingIndex, stopDrawing, stopEditMode]);

  // Drawing mode controls and legacy controls
  return (
    <>
      {showDrawingModeControls && (
        <DrawingModeContainer>
          <div style={{ marginBottom: '8px', fontWeight: '600' }}>Çizim Modu:</div>
          <DrawingModeButton
            $active={drawingMode === 'tarla'}
            $color="#8B4513"
            onClick={() => handleModeChange('tarla')}
          >
            🟤 Tarla Alanı Çiz
          </DrawingModeButton>
          <DrawingModeButton
            $active={drawingMode === 'dikili'}
            $color="#27ae60"
            onClick={() => handleModeChange('dikili')}
          >
            🟢 Dikili Alan Çiz
          </DrawingModeButton>
          <DrawingModeButton
            $active={drawingMode === 'zeytinlik'}
            $color="#9c8836"
            onClick={() => handleModeChange('zeytinlik')}
          >
            🫒 Zeytinlik Alanı Çiz
          </DrawingModeButton>
          {isDrawing && (
            <DrawButton onClick={stopDrawing}>
              ⏹️ Çizimi Durdur
            </DrawButton>
          )}
        </DrawingModeContainer>
      )}

      {/* Regular Controls */}
      {/* Çiz, Durdur, Tamamla, Düzenlemeyi Bitir butonları floating panelde kalabilir, Temizle harita üstünde! */}
      {!hideControls && (
        <DrawingControls>
          {editingIndex >= 0 ? (
            <DrawButton onClick={stopEditMode}>
              ✅ Düzenlemeyi Bitir
            </DrawButton>
          ) : !isDrawing ? (
            <DrawButton onClick={startDrawing} disabled={disabled}>
              🎨 Polygon Çiz
            </DrawButton>
          ) : (
            <>
              <DrawButton $active onClick={stopDrawing}>
                ⏹️ Çizimi Durdur
              </DrawButton>
              <DrawButton
                onClick={completePolygon}
                disabled={currentPoints.length < 3}
              >
                ✅ Tamamla ({currentPoints.length})
              </DrawButton>
            </>
          )}
          {/* Temizle butonu artık harita üstünde, burada yok */}
        </DrawingControls>
      )}
    </>
  );
};

const DrawButton = styled.button<{ $active?: boolean }>`
  background: ${props => props.$active ? '#e74c3c' : '#3498db'};
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  &:hover {
    background: ${props => props.$active ? '#c0392b' : '#2980b9'};
    transform: translateY(-1px);
  }
  &:disabled {
    background: #95a5a6;
    cursor: not-allowed;
  }
`;

export default PolygonDrawer;
export type { DrawnPolygon, PolygonPoint };
