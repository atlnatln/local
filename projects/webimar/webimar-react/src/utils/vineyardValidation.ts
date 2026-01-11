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
  type BagEviValidationError as VineyardValidationError,
  type BagEviValidationResult as VineyardValidationResult,
  validateTreeInput,
  validateBagEviForm as validateVineyardData,
  checkDuplicateTreeEntries
} from '../modules/BagEvi';

// Keep AreaValidationResult import for other files
export { type AreaValidationResult } from './areaCalculation';
