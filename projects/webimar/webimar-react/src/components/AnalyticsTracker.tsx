import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { createPageId, sendAnalyticsEvent } from '../utils/webimarAnalytics';

export default function AnalyticsTracker() {
  const location = useLocation();
  const currentPathRef = useRef<string>(typeof window !== 'undefined' ? window.location.pathname + window.location.search : '');
  const currentPageIdRef = useRef<string>(createPageId());
  const pageStartRef = useRef<number>(typeof performance !== 'undefined' ? performance.now() : Date.now());
  const leaveSentRef = useRef<boolean>(false);

  const sendView = (path: string) => {
    currentPageIdRef.current = createPageId();
    pageStartRef.current = typeof performance !== 'undefined' ? performance.now() : Date.now();
    leaveSentRef.current = false;

    sendAnalyticsEvent({
      event_type: 'page_view',
      path,
      page_id: currentPageIdRef.current,
      metadata: { title: document.title },
    });
  };

  const sendLeave = (path: string) => {
    if (leaveSentRef.current) return;
    leaveSentRef.current = true;
    const now = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const duration = Math.max(0, Math.round(now - pageStartRef.current));

    sendAnalyticsEvent({
      event_type: 'page_leave',
      path,
      page_id: currentPageIdRef.current,
      duration_ms: duration,
    });
  };

  // İlk mount
  useEffect(() => {
    const initialPath = window.location.pathname + window.location.search;
    currentPathRef.current = initialPath;
    sendView(initialPath);

    const onVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        sendLeave(currentPathRef.current);
      }
    };

    const onPageHide = () => {
      sendLeave(currentPathRef.current);
    };

    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('pagehide', onPageHide);

    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange);
      window.removeEventListener('pagehide', onPageHide);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Route değişimi
  useEffect(() => {
    const newPath = window.location.pathname + window.location.search;

    if (newPath !== currentPathRef.current) {
      sendLeave(currentPathRef.current);
      currentPathRef.current = newPath;
      sendView(newPath);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname, location.search]);

  return null;
}
