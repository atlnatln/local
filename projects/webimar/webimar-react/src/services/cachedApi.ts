// 🚀 OPTIMIZATION: Cached API Service
import { apiCache, CACHE_KEYS, cachedApiCalls } from '../utils/apiCache';
import { getCalculationHistory } from './api';

interface CalculationHistory {
  id: number;
  user: number;
  structure_type: string;
  calculation_type: string;
  calculation_data: any;
  parameters: any;
  result: any;
  created_at: string;
  title?: string;
  description?: string;
  map_coordinates?: { lat: number; lng: number };
}

export type { CalculationHistory };

// Cached version of getCalculationHistory
export const getCachedCalculationHistory = async (): Promise<CalculationHistory[]> => {
  return cachedApiCalls.getCalculationHistory(
    () => getCalculationHistory(),
    5 * 60 * 1000 // 5 minutes cache
  );
};

// Clear specific cache entries when data changes
export const clearCalculationHistoryCache = () => {
  apiCache.remove(CACHE_KEYS.CALCULATION_HISTORY);
};

// Export cache manager for debugging
export { apiCache, CACHE_KEYS } from '../utils/apiCache';
