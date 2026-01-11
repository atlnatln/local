import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
import '../styles/globals.css';
import '../lib/sw-register';
import { createPageId, sendAnalyticsEvent } from '../lib/webimarAnalytics';

// CookieBanner'ı client-side only olarak yükle
const CookieBanner = dynamic(() => import('../components/CookieBanner'), {
  ssr: false,
});

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();

  useEffect(() => {
    // Service worker unregistration is handled in sw-register.ts
    console.log('🚀 Next.js App initialized (SW disabled for React SPA compatibility)');
  }, []);

  useEffect(() => {
    let currentPath = router.asPath;
    let currentPageId = createPageId();
    let pageStart = typeof performance !== 'undefined' ? performance.now() : Date.now();
    let leaveSent = false;

    const sendView = (path: string) => {
      currentPageId = createPageId();
      pageStart = typeof performance !== 'undefined' ? performance.now() : Date.now();
      leaveSent = false;
      sendAnalyticsEvent({
        event_type: 'page_view',
        path,
        page_id: currentPageId,
        metadata: { title: typeof document !== 'undefined' ? document.title : '' },
      });
    };

    const sendLeave = (path: string) => {
      if (leaveSent) return;
      leaveSent = true;
      const now = typeof performance !== 'undefined' ? performance.now() : Date.now();
      const duration = Math.max(0, Math.round(now - pageStart));
      sendAnalyticsEvent({
        event_type: 'page_leave',
        path,
        page_id: currentPageId,
        duration_ms: duration,
      });
    };

    // İlk yükleme
    sendView(currentPath);

    const onRouteChangeStart = () => {
      sendLeave(currentPath);
    };

    const onRouteChangeComplete = (url: string) => {
      currentPath = url;
      sendView(currentPath);
    };

    const onVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        sendLeave(currentPath);
      }
    };

    const onPageHide = () => {
      sendLeave(currentPath);
    };

    router.events.on('routeChangeStart', onRouteChangeStart);
    router.events.on('routeChangeComplete', onRouteChangeComplete);
    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('pagehide', onPageHide);

    return () => {
      router.events.off('routeChangeStart', onRouteChangeStart);
      router.events.off('routeChangeComplete', onRouteChangeComplete);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      window.removeEventListener('pagehide', onPageHide);
    };
  }, [router]);

  return (
    <>
      <Component {...pageProps} />
      <CookieBanner />
    </>
  );
}
