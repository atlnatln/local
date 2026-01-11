/**
 * Next.js Hook for Webimar Analytics
 * useAnalytics() hook'u ile component'lerde kullanım
 * App Router uyumlu
 */
'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { getAnalytics } from '../utils/analytics';

/**
 * Analytics hook - her sayfa değişiminde otomatik tracking
 */
export const usePageTracking = () => {
  const pathname = usePathname();
  const analytics = getAnalytics();

  useEffect(() => {
    if (pathname) {
      // Sayfa değişiminde tracking
      analytics.trackPageView(pathname);
    }
  }, [pathname, analytics]);
};

/**
 * Analytics instance'ı döndüren hook
 */
export const useAnalytics = () => {
  return getAnalytics();
};

export default useAnalytics;
