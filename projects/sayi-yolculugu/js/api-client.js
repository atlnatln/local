/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — API Client
   Backend iletişim, retry logic, offline-first aware.
   ═══════════════════════════════════════════════════════════ */

const API_BASE = '';
const MAX_RETRIES = 3;
const RETRY_DELAY = 800;

async function _fetch(path, options = {}, retries = MAX_RETRIES) {
  const url = API_BASE + path;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (res.status === 503 && retries > 0) {
      await new Promise(r => setTimeout(r, RETRY_DELAY));
      return _fetch(path, options, retries - 1);
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    if (retries > 0) {
      await new Promise(r => setTimeout(r, RETRY_DELAY));
      return _fetch(path, options, retries - 1);
    }
    throw err;
  }
}

export const api = {
  async register(installationId) {
    return _fetch('/api/mathlock/register/', {
      method: 'POST',
      body: JSON.stringify({ installation_id: installationId }),
    });
  },

  async getPuzzles(childName) {
    return _fetch('/api/mathlock/puzzles/', {
      method: 'POST',
      body: JSON.stringify({ child_name: childName }),
    });
  },

  async saveProgress(data) {
    return _fetch('/api/mathlock/puzzles/progress/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async syncProgress(data) {
    return _fetch('/api/mathlock/puzzles/progress/sync/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getDailyChallenge(dateStr) {
    const body = dateStr ? JSON.stringify({ date: dateStr }) : undefined;
    return _fetch('/api/mathlock/puzzles/daily/', body ? { method: 'POST', body } : { method: 'POST' });
  },

  async getLeaderboard(period = 'daily') {
    return _fetch(`/api/mathlock/puzzles/leaderboard/?period=${encodeURIComponent(period)}`);
  },

  async sendAnalytics(events) {
    return _fetch('/api/mathlock/puzzles/analytics/', {
      method: 'POST',
      body: JSON.stringify({ events }),
    });
  },
};
