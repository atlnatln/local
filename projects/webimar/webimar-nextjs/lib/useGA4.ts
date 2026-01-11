import { useEffect } from 'react';
import { useRouter } from 'next/router';

// Google Analytics 4 Hook
export const useGA4 = () => {
  const router = useRouter();

  useEffect(() => {
    // Sayfa görüntüleme tracking
    const handleRouteChange = (url: string) => {
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('config', process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID!, {
          page_path: url,
          page_title: document.title,
          page_location: window.location.href,
        });
      }
    };

    // İlk sayfa yüklemesi için
    handleRouteChange(router.pathname);

    // Route değişikliklerini dinle
    router.events.on('routeChangeComplete', handleRouteChange);

    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router]);

  // Event tracking fonksiyonu
  const trackEvent = (
    eventName: string,
    parameters: Record<string, any> = {}
  ) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, {
        custom_map: { metric1: 'value1' },
        ...parameters,
      });
    }
  };

  // Hesaplama başlatma event'i
  const trackCalculationStart = (calculationType: string) => {
    trackEvent('calculation_start', {
      calculation_type: calculationType,
      page_location: window.location.href,
    });
  };

  // Hesaplama tamamlama event'i
  const trackCalculationComplete = (
    calculationType: string,
    success: boolean,
    duration?: number
  ) => {
    trackEvent('calculation_complete', {
      calculation_type: calculationType,
      success: success,
      duration: duration,
      page_location: window.location.href,
    });
  };

  // Hesaplama kaydetme event'i
  const trackCalculationSave = (calculationType: string) => {
    trackEvent('calculation_save', {
      calculation_type: calculationType,
      page_location: window.location.href,
    });
  };

  // Sayfa görüntüleme event'i
  const trackPageView = (pageTitle: string, pagePath: string) => {
    trackEvent('page_view', {
      page_title: pageTitle,
      page_path: pagePath,
      page_location: window.location.href,
    });
  };

  // Kullanıcı etkileşim event'i
  const trackUserInteraction = (
    action: string,
    category: string,
    label?: string,
    value?: number
  ) => {
    trackEvent('user_interaction', {
      action: action,
      category: category,
      label: label,
      value: value,
      page_location: window.location.href,
    });
  };

  // Form submission event'i
  const trackFormSubmit = (formName: string, success: boolean) => {
    trackEvent('form_submit', {
      form_name: formName,
      success: success,
      page_location: window.location.href,
    });
  };

  // Error tracking
  const trackError = (error: string, errorCategory: string = 'general') => {
    trackEvent('error_occurred', {
      error_message: error,
      error_category: errorCategory,
      page_location: window.location.href,
    });
  };

  return {
    trackEvent,
    trackCalculationStart,
    trackCalculationComplete,
    trackCalculationSave,
    trackPageView,
    trackUserInteraction,
    trackFormSubmit,
    trackError,
  };
};

// TypeScript declarations
declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'get' | 'set',
      targetId: string,
      config?: Record<string, any>
    ) => void;
  }
}

export default useGA4;
