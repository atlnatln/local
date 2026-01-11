import React, { createContext, useContext, useState, useEffect } from 'react';
import { StructureType } from '../types';
import { api } from '../services/api';

interface YapiTuru {
  id: number;
  ad: string;
}

interface AraziTipi {
  id: number;
  ad: string;
}

// Yapı türü kategorisi interface'i
interface StructureTypeCategory {
  name: string;
  icon: string;
  types: StructureType[];
}

// Context state interface'i
interface StructureTypesContextType {
  yapiTurleri: YapiTuru[];
  structureCategories: Record<string, StructureTypeCategory>;
  structureTypeLabels: Record<StructureType, string>;
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
  getFilteredYapiTurleri: (araziVasfi?: string) => Promise<YapiTuru[]>;
  getFilteredAraziTipleri: (yapiTuru?: string) => Promise<AraziTipi[]>;
}

// Context oluştur
const StructureTypesContext = createContext<StructureTypesContextType | undefined>(undefined);

// URL'den StructureType'a mapping (backend'deki URL pattern'ları ile uyumlu)
const createStructureTypeFromUrl = (yapiTuru: YapiTuru): StructureType => {
  // Backend constants.py'daki YAPI_TURLERI ile uyumlu URL dönüşümü
  const urlMap: Record<number, StructureType> = {
    1: 'solucan-tesisi',
    2: 'mantar-tesisi', 
    3: 'sera',
    4: 'aricilik',
    5: 'hububat-silo',
    6: 'tarimsal-depo',
    7: 'lisansli-depo',
    8: 'yikama-tesisi',
    9: 'kurutma-tesisi',
    10: 'meyve-sebze-kurutma',
    11: 'zeytinyagi-fabrikasi',
    12: 'su-depolama',
    13: 'su-kuyulari',
    14: 'bag-evi',
    15: 'su-depolama',
    16: 'soguk-hava-deposu',
    17: 'sut-sigirciligi',
    18: 'agil-kucukbas',
    19: 'kumes-yumurtaci',
    20: 'kumes-etci',
    21: 'kumes-gezen',
    22: 'kumes-hindi',
    23: 'kaz-ordek',
    24: 'hara',
    25: 'ipek-bocekciligi',
    26: 'evcil-hayvan',
    27: 'besi-sigirciligi',
    28: 'zeytinyagi-uretim-tesisi'
  };
  
  return urlMap[yapiTuru.id] || 'sera'; // fallback
};

// Kategorilere göre yapı türlerini gruplandır
const categorizeStructureTypes = (yapiTurleri: YapiTuru[]): Record<string, StructureTypeCategory> => {
  const categories: Record<string, StructureTypeCategory> = {
    special_production: {
      name: 'Özel Üretim Tesisleri',
      icon: '🌱',
      types: []
    },
    storage_processing: {
      name: 'Depolama ve İşleme Tesisleri', 
      icon: '🏪',
      types: []
    },
    livestock: {
      name: 'Hayvancılık Tesisleri',
      icon: '🐄',
      types: []
    }
  };

  yapiTurleri.forEach(yapiTuru => {
    const structureType = createStructureTypeFromUrl(yapiTuru);
    
    // Kategorilere göre ayır (ID bazlı)
    if (yapiTuru.id >= 1 && yapiTuru.id <= 4) {
      categories.special_production.types.push(structureType);
    } else if (yapiTuru.id >= 5 && yapiTuru.id <= 16) {
      categories.storage_processing.types.push(structureType);
    } else if (yapiTuru.id >= 17 && yapiTuru.id <= 27) {
      categories.livestock.types.push(structureType);
    }
  });

  return categories;
};

// Labels mapping oluştur
const createLabelsMapping = (yapiTurleri: YapiTuru[]): Record<StructureType, string> => {
  const labels: Record<string, string> = {};
  
  yapiTurleri.forEach(yapiTuru => {
    const structureType = createStructureTypeFromUrl(yapiTuru);
    labels[structureType] = yapiTuru.ad;
  });
  
  return labels as Record<StructureType, string>;
};

// Provider component
export const StructureTypesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [yapiTurleri, setYapiTurleri] = useState<YapiTuru[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/calculations/yapi-turleri/');
      if (response.data && Array.isArray(response.data.data)) {
        setYapiTurleri(response.data.data);
      } else if (Array.isArray(response.data)) {
        setYapiTurleri(response.data);
      } else {
        console.error('Beklenmeyen API yanıt formatı:', response.data);
        setYapiTurleri([]);
      }
    } catch (err) {
      console.error('❌ StructureTypesContext - API hatası:', err);
      setError(err instanceof Error ? err.message : 'Yapı türleri yüklenirken hata oluştu');
      console.error('Yapı türleri yükleme hatası:', err);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredYapiTurleri = async (araziVasfi?: string): Promise<YapiTuru[]> => {
    try {
      const response = await api.get('/calculations/yapi-turleri/', {
        params: { arazi_vasfi: araziVasfi }
      });
      return response.data.data || response.data;
    } catch (err) {
      console.error('Filtrelenen yapı türleri yükleme hatası:', err);
      throw err;
    }
  };

  const getFilteredAraziTipleri = async (yapiTuru?: string): Promise<AraziTipi[]> => {
    try {
      const response = await api.get('/calculations/arazi-tipleri/', {
        params: { yapi_turu: yapiTuru }
      });
      return response.data.data || response.data;
    } catch (err) {
      console.error('Filtrelenen arazi tipleri yükleme hatası:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const structureCategories = categorizeStructureTypes(yapiTurleri);
  const structureTypeLabels = createLabelsMapping(yapiTurleri);

  const value: StructureTypesContextType = {
    yapiTurleri,
    structureCategories,
    structureTypeLabels,
    loading,
    error,
    refreshData: fetchData,
    getFilteredYapiTurleri,
    getFilteredAraziTipleri
  };

  return (
    <StructureTypesContext.Provider value={value}>
      {children}
    </StructureTypesContext.Provider>
  );
};

// Hook to use the context
export const useStructureTypes = (): StructureTypesContextType => {
  const context = useContext(StructureTypesContext);
  if (context === undefined) {
    throw new Error('useStructureTypes must be used within a StructureTypesProvider');
  }
  return context;
};

export default StructureTypesContext;
