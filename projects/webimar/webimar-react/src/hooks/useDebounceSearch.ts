import { useMemo } from 'react';
import { useDebounce } from 'use-debounce';

interface CalculationHistory {
  id: number;
  calculation_type: string;
  created_at: string;
  parameters: any;
  result: any;
}

// 🚀 OPTIMIZATION: Debounced search hook for better performance
export const useDebounceSearch = <T>(
  items: T[], 
  searchTerm: string,
  searchFunction: (items: T[], term: string) => T[],
  delay: number = 300
) => {
  const [debouncedSearchTerm] = useDebounce(searchTerm, delay);
  
  const filteredItems = useMemo(() => {
    if (!debouncedSearchTerm.trim()) return items;
    return searchFunction(items, debouncedSearchTerm);
  }, [items, debouncedSearchTerm, searchFunction]);

  return {
    filteredItems,
    isSearching: searchTerm !== debouncedSearchTerm,
    debouncedSearchTerm
  };
};

// 🚀 Specialized search functions for different data types
export const searchFunctions = {
  // Search calculation history by multiple fields
  calculationHistory: (items: CalculationHistory[], term: string): CalculationHistory[] => {
    const searchTerm = term.toLowerCase();
    return items.filter(item => 
      item.calculation_type.toLowerCase().includes(searchTerm) ||
      item.created_at.toLowerCase().includes(searchTerm) ||
      JSON.stringify(item.parameters).toLowerCase().includes(searchTerm) ||
      (item.result && JSON.stringify(item.result).toLowerCase().includes(searchTerm))
    );
  },

  // Generic string search for simple arrays  
  stringArray: (items: string[], term: string): string[] => {
    const searchTerm = term.toLowerCase();
    return items.filter(item => item.toLowerCase().includes(searchTerm));
  },

  // Search objects by specific fields
  objectByFields: <T extends Record<string, any>>(fields: (keyof T)[]) => 
    (items: T[], term: string): T[] => {
      const searchTerm = term.toLowerCase();
      return items.filter(item =>
        fields.some(field => 
          String(item[field]).toLowerCase().includes(searchTerm)
        )
      );
    }
};

// 🚀 OPTIMIZATION: Advanced search with fuzzy matching (optional enhancement)
export const useFuzzySearch = <T>(
  items: T[],
  searchTerm: string,
  searchFunction: (items: T[], term: string) => T[],
  options: {
    delay?: number;
    minSearchLength?: number;
    maxResults?: number;
  } = {}
) => {
  const { delay = 300, minSearchLength = 2, maxResults = 50 } = options;
  const [debouncedSearchTerm] = useDebounce(searchTerm, delay);
  
  const filteredItems = useMemo(() => {
    if (debouncedSearchTerm.length < minSearchLength) return items;
    
    const results = searchFunction(items, debouncedSearchTerm);
    return maxResults ? results.slice(0, maxResults) : results;
  }, [items, debouncedSearchTerm, searchFunction, minSearchLength, maxResults]);

  return {
    filteredItems,
    isSearching: searchTerm !== debouncedSearchTerm,
    debouncedSearchTerm,
    hasResults: filteredItems.length > 0,
    isMinSearchLength: searchTerm.length >= minSearchLength
  };
};
