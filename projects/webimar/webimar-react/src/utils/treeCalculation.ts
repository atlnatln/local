/**
 * DEPRECATED: Bu dosya konsolide edilmiştir!
 * 
 * Yeni bağ evi hesaplamaları için lütfen bagEviCalculator.ts dosyasını kullanın.
 * Bu dosya geriye uyumluluk için korunmaktadır.
 * 
 * @deprecated Lütfen bagEviCalculator.ts kullanın
 */

// Re-export from the new consolidated calculator for backward compatibility
export {
  type AgacVerisi,
  type EklenenAgac,
  type AgacDetay,
  type YeterlilikSonucu,
  type HesaplamaSonucu,
  getDefaultTreeData,
  getAvailableTreeTypes,
  calculateTreeCoverage,
  validateVineyardEligibility,
  calculateVineyardResult,
  formatAreaDisplay
} from '../modules/BagEvi';
