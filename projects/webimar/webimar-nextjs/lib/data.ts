// Belediye logoları kaldırıldı

// Yapı türü kategorileri
export const structureCategories = {
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

// URL'den StructureType'a mapping
export const urlStructureTypeMap: Record<number, string> = {
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

// Kategorilere göre yapı türlerini gruplandır
export const categorizeStructureTypes = (yapiTurleri: any[]) => {
  const categories = {
    special_production: {
      name: 'Özel Üretim Tesisleri',
      icon: '🌱',
      types: [] as any[]
    },
    storage_processing: {
      name: 'Depolama ve İşleme Tesisleri', 
      icon: '🏪',
      types: [] as any[]
    },
    livestock: {
      name: 'Hayvancılık Tesisleri',
      icon: '🐄',
      types: [] as any[]
    }
  };

  yapiTurleri.forEach((yapiTuru: any) => {
    const structureType = urlStructureTypeMap[yapiTuru.id] || 'sera';
    
    // Kategorilere göre ayır (ID bazlı)
    if (yapiTuru.id >= 1 && yapiTuru.id <= 4) {
      categories.special_production.types.push({
        id: yapiTuru.id,
        name: yapiTuru.ad,
        url: structureType
      });
    } else if ((yapiTuru.id >= 5 && yapiTuru.id <= 16) || yapiTuru.id === 28) {
      categories.storage_processing.types.push({
        id: yapiTuru.id,
        name: yapiTuru.ad,
        url: structureType
      });
    } else if (yapiTuru.id >= 17 && yapiTuru.id <= 27) {
      categories.livestock.types.push({
        id: yapiTuru.id,
        name: yapiTuru.ad,
        url: structureType
      });
    }
  });

  return categories;
};
