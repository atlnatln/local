type AnalyticsEventType = 'page_view' | 'page_leave' | 'calculation';

type AnalyticsPayload = {
  session_id: string;
  event_type: AnalyticsEventType;
  path: string;
  referrer?: string | null;
  page_id?: string | null;
  duration_ms?: number;
  calculation_type?: string | null;
  metadata?: Record<string, unknown> | null;
};

const SESSION_KEY = 'webimar_session_id_v1';

function randomId(length = 16): string {
  if (typeof window === 'undefined') return 'server';
  const bytes = new Uint8Array(length);
  window.crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => (b % 36).toString(36))
    .join('');
}

export function getSessionId(): string {
  if (typeof window === 'undefined') return 'server';

  const existing = window.localStorage.getItem(SESSION_KEY);
  if (existing && existing.length >= 8) return existing;

  const sid = `${Date.now().toString(36)}_${randomId(18)}`;
  window.localStorage.setItem(SESSION_KEY, sid);
  return sid;
}

export function createPageId(): string {
  return `${Date.now().toString(36)}_${randomId(12)}`;
}

const ANALYTICS_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.REACT_APP_API_BASE_URL ||
  '';

const shouldSkipAnalytics = 
  ANALYTICS_BASE.includes('localhost') || 
  ANALYTICS_BASE.includes('127.0.0.1') ||
  (typeof window !== 'undefined' && (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1'
  )) ||
  process.env.NODE_ENV === 'development';

function buildAnalyticsUrl(): string | null {
  if (!ANALYTICS_BASE || shouldSkipAnalytics) return null;
  return `${ANALYTICS_BASE.replace(/\/$/, '')}/accounts/analytics/events/`;
}

export function sendAnalyticsEvent(payload: Omit<AnalyticsPayload, 'session_id'> & { session_id?: string }): void {
  if (typeof window === 'undefined') return;

  const url = buildAnalyticsUrl();
  if (!url) return; // Dev veya base URL yok

  const body: AnalyticsPayload = {
    session_id: payload.session_id || getSessionId(),
    event_type: payload.event_type,
    path: payload.path,
    referrer: payload.referrer ?? document.referrer ?? null,
    page_id: payload.page_id ?? null,
    duration_ms: payload.duration_ms,
    calculation_type: payload.calculation_type ?? null,
    metadata: payload.metadata ?? null,
  };

  try {
    const blob = new Blob([JSON.stringify(body)], { type: 'application/json' });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, blob);
      return;
    }
  } catch {
    // fall back
  }

  // keepalive: sayfa kapanırken de gönderim şansı
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    keepalive: true,
  }).catch(() => undefined);
}
