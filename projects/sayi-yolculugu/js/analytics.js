/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Analytics
   Olay toplama, buffer, batch gönderim, offline backup.
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';
import { api } from './api-client.js';

const BUFFER_LIMIT = 50;
const FLUSH_INTERVAL_MS = 30000;
const STORAGE_KEY = 'sy_analytics';

let flushTimer = null;

export function track(eventType, data = {}) {
  const event = {
    type: eventType,
    timestamp: Date.now(),
    data,
  };
  dispatch({ type: 'PUSH_ANALYTICS_EVENT', payload: event });

  const len = getState().sessionEvents.length;
  if (len >= 10) {
    flush();
  } else {
    scheduleFlush();
  }
}

function scheduleFlush() {
  if (flushTimer) return;
  flushTimer = setTimeout(() => {
    flushTimer = null;
    flush();
  }, FLUSH_INTERVAL_MS);
}

export async function flush() {
  const events = getState().sessionEvents;
  if (events.length === 0) return;

  // Offline backup
  try {
    const backup = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...backup, ...events]));
  } catch {
    // ignore
  }

  try {
    await api.sendAnalytics(events);
    dispatch({ type: 'CLEAR_ANALYTICS_BUFFER' });
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    console.warn('[Analytics] flush failed, will retry', e);
  }
}
