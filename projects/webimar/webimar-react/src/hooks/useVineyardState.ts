// Custom hooks for DikiliAlanKontrol state management
// This file implements state simplification and separation of concerns

import { useState, useEffect, useCallback } from 'react';
import { DrawnPolygon } from '../components/Map/PolygonDrawer';
import {
  AgacVerisi,
  EklenenAgac,
  getDefaultTreeData,
  HesaplamaSonucu,
  calculateVineyardResult
} from '../modules/BagEvi';
import { validateTreeInput } from '../utils/vineyardValidation';

// Types for form state
export interface VineyardFormState {
  dikiliAlan: number;
  tarlaAlani: number;
  zeytinlikAlani: number;
  secilenAgacTuru: string;
  secilenAgacTipi: 'normal' | 'bodur' | 'yaribodur';
  agacSayisi: number;
}

export interface TreeEditState {
  editingIndex: number | null;
  editingAgacSayisi: number;
}

export interface MapState {
  drawingMode: 'tarla' | 'dikili' | 'zeytinlik' | null;
  tarlaPolygon: DrawnPolygon | null;
  dikiliPolygon: DrawnPolygon | null;
  zeytinlikPolygon: DrawnPolygon | null;
  editTrigger: { timestamp: number; polygonIndex: number };
}

// Custom hook for tree data management
export const useTreeData = () => {
  const [agacVerileri, setAgacVerileri] = useState<AgacVerisi[]>([]);
  const [eklenenAgaclar, setEklenenAgaclar] = useState<EklenenAgac[]>([]);

  // Load tree data on mount
  useEffect(() => {
    const treeData = getDefaultTreeData();
    setAgacVerileri(treeData);
  }, []);

  // Add tree with validation
  const addTree = useCallback((
    secilenAgacTuru: string,
    secilenAgacTipi: 'normal' | 'bodur' | 'yaribodur',
    agacSayisi: number
  ) => {
    // Validation
    const validation = validateTreeInput(secilenAgacTuru, agacSayisi, agacVerileri);
    if (!validation.isValid) {
      throw new Error(validation.error);
    }

    const agacTuru = agacVerileri.find(a => a.sira.toString() === secilenAgacTuru);
    if (!agacTuru) {
      throw new Error('Ağaç türü bulunamadı');
    }

    let gerekliSayi = 0;
    switch (secilenAgacTipi) {
      case 'normal':
        gerekliSayi = agacTuru.normal || 0;
        break;
      case 'bodur':
        gerekliSayi = agacTuru.bodur || 0;
        break;
      case 'yaribodur':
        gerekliSayi = agacTuru.yariBodur || 0;
        break;
    }

    const yeniAgac: EklenenAgac = {
      turid: secilenAgacTuru,
      turAdi: agacTuru.tur,
      tipi: secilenAgacTipi,
      sayi: agacSayisi,
      gerekliAgacSayisi: gerekliSayi
    };

    setEklenenAgaclar(prev => [...prev, yeniAgac]);
    return yeniAgac;
  }, [agacVerileri]);

  // Remove tree
  const removeTree = useCallback((index: number) => {
    setEklenenAgaclar(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Update tree count
  const updateTreeCount = useCallback((index: number, newCount: number) => {
    if (newCount <= 0) {
      throw new Error('Ağaç sayısı pozitif olmalıdır');
    }

    setEklenenAgaclar(prev => {
      const newList = [...prev];
      newList[index].sayi = newCount;
      return newList;
    });
  }, []);

  // Clear all trees
  const clearAllTrees = useCallback(() => {
    setEklenenAgaclar([]);
  }, []);

  return {
    agacVerileri,
    eklenenAgaclar,
    addTree,
    removeTree,
    updateTreeCount,
    clearAllTrees
  };
};

// Custom hook for form state management
export const useVineyardForm = (initialDikiliAlan: number = 0, initialTarlaAlani: number = 0, initialZeytinlikAlani: number = 0) => {
  const [formState, setFormState] = useState<VineyardFormState>({
    dikiliAlan: initialDikiliAlan,
    tarlaAlani: initialTarlaAlani,
    zeytinlikAlani: initialZeytinlikAlani,
    secilenAgacTuru: '',
    secilenAgacTipi: 'normal',
    agacSayisi: 0
  });
  
  // Initial değerler değiştiğinde state'i güncelle
  useEffect(() => {
    setFormState(prev => ({
      ...prev,
      dikiliAlan: initialDikiliAlan,
      tarlaAlani: initialTarlaAlani,
      zeytinlikAlani: initialZeytinlikAlani
    }));
  }, [initialDikiliAlan, initialTarlaAlani, initialZeytinlikAlani]);

  // Update individual form fields
  const updateField = useCallback(<K extends keyof VineyardFormState>(
    field: K,
    value: VineyardFormState[K]
  ) => {
    setFormState(prev => ({ ...prev, [field]: value }));
  }, []);

  // Update multiple fields at once
  const updateFields = useCallback((updates: Partial<VineyardFormState>) => {
    setFormState(prev => ({ ...prev, ...updates }));
  }, []);

  // Reset form
  const resetForm = useCallback(() => {
    setFormState({
      dikiliAlan: 0,
      tarlaAlani: 0,
      zeytinlikAlani: 0,
      secilenAgacTuru: '',
      secilenAgacTipi: 'normal',
      agacSayisi: 0
    });
  }, []);

  // Reset tree selection only
  const resetTreeSelection = useCallback(() => {
    setFormState(prev => ({
      ...prev,
      secilenAgacTuru: '',
      secilenAgacTipi: 'normal',
      agacSayisi: 0
    }));
  }, []);

  return {
    formState,
    updateField,
    updateFields,
    resetForm,
    resetTreeSelection
  };
};

// Custom hook for tree editing state
export const useTreeEditing = () => {
  const [editState, setEditState] = useState<TreeEditState>({
    editingIndex: null,
    editingAgacSayisi: 0
  });

  const startEdit = useCallback((index: number, currentCount: number) => {
    setEditState({
      editingIndex: index,
      editingAgacSayisi: currentCount
    });
  }, []);

  const updateEditCount = useCallback((count: number) => {
    setEditState(prev => ({ ...prev, editingAgacSayisi: count }));
  }, []);

  const cancelEdit = useCallback(() => {
    setEditState({
      editingIndex: null,
      editingAgacSayisi: 0
    });
  }, []);

  return {
    editState,
    startEdit,
    updateEditCount,
    cancelEdit
  };
};

// Custom hook for map state management
export const useMapState = () => {
  const [mapState, setMapState] = useState<MapState>({
    drawingMode: null,
    tarlaPolygon: null,
    dikiliPolygon: null,
    zeytinlikPolygon: null,
    editTrigger: { timestamp: 0, polygonIndex: -1 }
  });

  const setDrawingMode = useCallback((mode: 'tarla' | 'dikili' | 'zeytinlik' | null) => {
    setMapState(prev => ({ ...prev, drawingMode: mode }));
  }, []);

  const setTarlaPolygon = useCallback((polygon: DrawnPolygon | null) => {
    setMapState(prev => ({ ...prev, tarlaPolygon: polygon }));
  }, []);

  const setDikiliPolygon = useCallback((polygon: DrawnPolygon | null) => {
    setMapState(prev => ({ ...prev, dikiliPolygon: polygon }));
  }, []);

  const setZeytinlikPolygon = useCallback((polygon: DrawnPolygon | null) => {
    setMapState(prev => ({ ...prev, zeytinlikPolygon: polygon }));
  }, []);

  const triggerEdit = useCallback((polygonIndex: number) => {
    setMapState(prev => ({
      ...prev,
      editTrigger: { timestamp: Date.now(), polygonIndex }
    }));
  }, []);

  const clearPolygons = useCallback(() => {
    setMapState(prev => ({
      ...prev,
      tarlaPolygon: null,
      dikiliPolygon: null,
      zeytinlikPolygon: null
    }));
  }, []);

  return {
    mapState,
    setDrawingMode,
    setTarlaPolygon,
    setDikiliPolygon,
    setZeytinlikPolygon,
    triggerEdit,
    clearPolygons
  };
};

// Custom hook for calculation logic
export const useVineyardCalculation = () => {
  const [hesaplamaSonucu, setHesaplamaSonucu] = useState<HesaplamaSonucu | null>(null);

  const calculate = useCallback((
    dikiliAlan: number,
    tarlaAlani: number,
    eklenenAgaclar: EklenenAgac[],
    araziVasfi?: string
  ) => {
    const result = calculateVineyardResult(dikiliAlan, tarlaAlani, eklenenAgaclar, araziVasfi);
    setHesaplamaSonucu(result);
    return result;
  }, []);

  const clearResult = useCallback(() => {
    setHesaplamaSonucu(null);
  }, []);

  return {
    hesaplamaSonucu,
    calculate,
    clearResult
  };
};
