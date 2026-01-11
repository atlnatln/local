import { useState, useEffect } from 'react';

/**
 * Medya sorguları için hook
 * @param query - CSS medya sorgusu stringu
 * @returns boolean - Sorgu eşleşip eşleşmediği
 */
export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState<boolean>(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    // İlk değeri set et
    setMatches(mediaQuery.matches);
    
    // Değişiklikleri dinle
    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };
    
    mediaQuery.addEventListener('change', handler);
    
    return () => {
      mediaQuery.removeEventListener('change', handler);
    };
  }, [query]);

  return matches;
};

/**
 * Mobil cihaz algılama hook'u
 */
export const useIsMobile = (): boolean => {
  return useMediaQuery('(max-width: 768px)');
};
