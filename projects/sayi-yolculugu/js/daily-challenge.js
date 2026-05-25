/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Daily Challenge
   Seed tabanlı günlük seviye, countdown, API çağrısı.
   ═══════════════════════════════════════════════════════════ */

import { dispatch } from './store.js';
import { api } from './api-client.js';

export async function loadDailyChallenge(dateStr) {
  try {
    const res = await api.getDailyChallenge(dateStr);
    if (res.puzzle) {
      dispatch({ type: 'LOAD_DAILY_LEVEL', payload: res.puzzle });
      return res.puzzle;
    }
    return null;
  } catch (e) {
    console.error('Daily challenge yüklenemedi:', e);
    return null;
  }
}

export function getNextChallengeCountdown() {
  const now = new Date();
  const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  const diff = tomorrow - now;
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}
