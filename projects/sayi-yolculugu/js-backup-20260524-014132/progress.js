/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Progress (localStorage)
   ═══════════════════════════════════════════════════════════ */

import { state } from './state.js';

const STORAGE_KEY = 'sy_progress';

export function loadProgress() {
  try {
    state.progress = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    state.progress = {};
  }
}

export function saveProgress() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress));
}
