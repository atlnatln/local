export type AnalyticsEventType = 'page_view' | 'page_leave' | 'calculation';

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
  const bytes = new Uint8Array(length);
  window.crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => (b % 36).toString(36))
    .join('');
}

export function getSessionId(): string {
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
  process.env.REACT_APP_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';

// Dev ortamında (localhost) analytics isteğini atlama
const shouldSkipAnalytics = 
  ANALYTICS_BASE.includes('localhost') || 
  ANALYTICS_BASE.includes('127.0.0.1') ||
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  process.env.NODE_ENV === 'development';

function buildAnalyticsUrl(): string | null {
  if (!ANALYTICS_BASE || shouldSkipAnalytics) return null;
  return `${ANALYTICS_BASE.replace(/\/$/, '')}/accounts/analytics/events/`;
}

export function sendAnalyticsEvent(payload: Omit<AnalyticsPayload, 'session_id'> & { session_id?: string }): void {
  const url = buildAnalyticsUrl();
  if (!url) return; // Development veya base URL yoksa gönderme

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

  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    keepalive: true,
  }).catch(() => undefined);
}
