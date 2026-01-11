/**
 * Bağ Evi Modülü - Ana Export Dosyası
 * 
 * Bu modül bağ evi hesaplamaları ile ilgili tüm bileşenleri,
 * utilities ve type'ları tek merkezde toplar.
 */

// Components
export { default as BagEviForm } from './components/BagEviForm';

// Main calculator (includes types, treeData, validation)
export * from './utils/calculator';

// Module info
export const MODULE_INFO = {
  name: 'BagEvi',
  version: '2.0.0',
  description: 'Bağ evi hesaplamaları modülü - refactored ve optimize edildi',
  lastUpdated: '2025-08-28'
};
