import { CalculationResult } from '../types';

interface CalculationHistory {
  id: number;
  user: number;
  structure_type: string;
  calculation_type: string;
  calculation_data: any;
  parameters: any;
  result: CalculationResult;
  created_at: string;
  title?: string;
  description?: string;
  map_coordinates?: { lat: number; lng: number };
}

interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiresIn: number;
}

class ApiCacheManager {
  private cache = new Map<string, CacheItem<any>>();
  private readonly DEFAULT_CACHE_TIME = 5 * 60 * 1000; // 5 minutes

  // 🚀 OPTIMIZATION: Cache API responses with expiration
  set<T>(key: string, data: T, expiresIn: number = this.DEFAULT_CACHE_TIME): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expiresIn
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.expiresIn) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  // Clear cache manually
  clear(): void {
    this.cache.clear();
  }

  // Remove specific cache entry
  remove(key: string): void {
    this.cache.delete(key);
  }

  // Get cache info for debugging
  getInfo(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Singleton instance
export const apiCache = new ApiCacheManager();

// 🚀 Cache keys for different API endpoints
export const CACHE_KEYS = {
  CALCULATION_HISTORY: 'calculation_history',
  USER_PROFILE: 'user_profile',
  CALCULATION_RESULT: (type: string, params: string) => `calc_${type}_${params}`,
  LOCATION_DATA: (lat: number, lng: number) => `location_${lat}_${lng}`
} as const;

// 🚀 OPTIMIZATION: Cached API wrapper functions
export const cachedApiCalls = {
  // Cache calculation history
  getCalculationHistory: async (
    originalFetch: () => Promise<CalculationHistory[]>,
    cacheTime?: number
  ): Promise<CalculationHistory[]> => {
    const cached = apiCache.get<CalculationHistory[]>(CACHE_KEYS.CALCULATION_HISTORY);
    if (cached) {
      console.log('📦 Using cached calculation history');
      return cached;
    }

    const data = await originalFetch();
    apiCache.set(CACHE_KEYS.CALCULATION_HISTORY, data, cacheTime);
    console.log('🔄 Cached calculation history');
    return data;
  },

  // Cache calculation results
  getCalculationResult: async <T>(
    calculationType: string,
    params: Record<string, any>,
    originalFetch: () => Promise<T>,
    cacheTime?: number
  ): Promise<T> => {
    const paramsHash = btoa(JSON.stringify(params)).slice(0, 16); // Simple hash
    const cacheKey = CACHE_KEYS.CALCULATION_RESULT(calculationType, paramsHash);
    
    const cached = apiCache.get<T>(cacheKey);
    if (cached) {
      console.log(`📦 Using cached ${calculationType} result`);
      return cached;
    }

    const data = await originalFetch();
    apiCache.set(cacheKey, data, cacheTime || 10 * 60 * 1000); // 10 min for calc results
    console.log(`🔄 Cached ${calculationType} result`);
    return data;
  }
};

export default apiCache;
