/**
 * React Hook for Webimar Analytics
 * useAnalytics() hook'u ile component'lerde kullanım
 */
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getAnalytics } from '../utils/analytics';

/**
 * Analytics hook - her sayfa değişiminde otomatik tracking
 */
export const usePageTracking = () => {
  const location = useLocation();
  const analytics = getAnalytics();

  useEffect(() => {
    // Sayfa değişiminde tracking
    analytics.trackPageView(location.pathname);
  }, [location.pathname, analytics]);
};

/**
 * Analytics instance'ı döndüren hook
 */
export const useAnalytics = () => {
  return getAnalytics();
};

export default useAnalytics;
