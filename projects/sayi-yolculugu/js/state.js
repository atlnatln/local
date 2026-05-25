/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — State Constants & Level Selectors
   ═══════════════════════════════════════════════════════════ */

import { LEVELS_BY_AGE } from './levels-data.js';
import { getState } from './store.js';

export const CMDS = {
  'x+': { label: 'x →', css: 'x-plus',  dx: 1,  dy: 0,  dz: 0 },
  'x-': { label: '← x', css: 'x-minus', dx: -1, dy: 0,  dz: 0 },
  'y-': { label: 'y ↑', css: 'y-minus', dx: 0,  dy: -1, dz: 0 },
  'y+': { label: '↓ y', css: 'y-plus',  dx: 0,  dy: 1,  dz: 0 },
  'z+': { label: 'z +1', css: 'z-plus',  dx: 0,  dy: 0,  dz: 1 },
  'z-': { label: 'z -1', css: 'z-minus', dx: 0,  dy: 0,  dz: -1 },
};

export const ICONS = {
  'x+': '→', 'x-': '←', 'y-': '↑', 'y+': '↓', 'z+': '+', 'z-': '-'
};

export function getLevels() {
  const state = getState();
  if (state.mode === 'editor-test' && state.customLevel) {
    return [state.customLevel];
  }
  if (state.mode === 'daily' && state.dailyLevel) {
    return [state.dailyLevel];
  }
  return LEVELS_BY_AGE[state.ageGroup] || [];
}

export function getLevel() {
  return getLevels()[getState().levelIdx];
}
