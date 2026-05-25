/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Settings
   Kullanıcı ayarları, CSS değişkenleri, localStorage persist.
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';

const STORAGE_KEY = 'sy_settings';

export function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      dispatch({ type: 'UPDATE_SETTINGS', payload: JSON.parse(raw) });
    }
  } catch {
    // ignore parse errors
  }
  applySettings();
}

export function saveSettings(partial) {
  dispatch({ type: 'UPDATE_SETTINGS', payload: partial });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(getState().settings));
  applySettings();
}

export function applySettings() {
  const s = getState().settings;
  const html = document.documentElement;

  html.classList.remove('font-small', 'font-medium', 'font-large');
  html.classList.add('font-' + s.fontSize);

  document.body.classList.toggle('high-contrast', s.highContrast);

  // Animation speed CSS variable
  document.documentElement.style.setProperty('--anim-speed', String(s.animationSpeed));

  // Reduced motion: respect OS preference if not manually overridden
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reduced = s.reducedMotion || prefersReduced;
  document.body.classList.toggle('reduced-motion', reduced);
}

// Re-apply when OS preference changes
window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', applySettings);
