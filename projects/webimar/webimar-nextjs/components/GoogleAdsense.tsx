import Script from 'next/script';
import { useEffect, useMemo, useState } from 'react';

export default function GoogleAdsense() {
  const [shouldLoad, setShouldLoad] = useState(false);
  const clientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID || 'ca-pub-XXXXXXXXXXXXXXXX';
  const hasValidClientId = useMemo(() => {
    return (
      clientId.startsWith('ca-pub-') &&
      !clientId.includes('XXXXXXXXXXXXXXXX')
    );
  }, [clientId]);

  useEffect(() => {
    if (!hasValidClientId) {
      return;
    }

    let fallbackTimer: ReturnType<typeof setTimeout> | undefined;
    let idleTimer: ReturnType<typeof setTimeout> | undefined;

    const scheduleLoad = () => {
      if ('requestIdleCallback' in window) {
        (window as any).requestIdleCallback(
          () => setShouldLoad(true),
          { timeout: 4000 }
        );
        return;
      }

      idleTimer = setTimeout(() => setShouldLoad(true), 1500);
    };

    const triggerLoad = () => {
      cleanupListeners();
      scheduleLoad();
    };

    const cleanupListeners = () => {
      window.removeEventListener('scroll', triggerLoad);
      window.removeEventListener('touchstart', triggerLoad);
      window.removeEventListener('mousedown', triggerLoad);
      window.removeEventListener('keydown', triggerLoad);
    };

    window.addEventListener('scroll', triggerLoad, { passive: true, once: true });
    window.addEventListener('touchstart', triggerLoad, { passive: true, once: true });
    window.addEventListener('mousedown', triggerLoad, { passive: true, once: true });
    window.addEventListener('keydown', triggerLoad, { once: true });

    fallbackTimer = setTimeout(triggerLoad, 15000);

    return () => {
      cleanupListeners();
      if (fallbackTimer) {
        clearTimeout(fallbackTimer);
      }
      if (idleTimer) {
        clearTimeout(idleTimer);
      }
    };
  }, [hasValidClientId]);

  if (!hasValidClientId || !shouldLoad) {
    return null;
  }

  return (
    <Script
      strategy="afterInteractive"
      src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${clientId}`}
      crossOrigin="anonymous"
    />
  );
}
