/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — State Constants & Level Selectors
   ═══════════════════════════════════════════════════════════ */

import { LEVELS_BY_AGE } from './levels-data.js';
import { getState } from './store.js';
import { solveLevel } from './hint-engine.js';

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

let _cachedStaticValid = {};
let _preloadedGenerated = null;
let _cachedAgeGroup = null;
let _loadingPromise = null;

/* ─── async pre-load (call once per age-group change) ─── */
export async function preloadLevels(ageGroup) {
  const maxDiff = {
    '5-6': 2,
    '7-8': 3,
    '9-10': 4,
    '11-12': 5,
  }[ageGroup] || 5;

  if (_cachedAgeGroup === ageGroup && _preloadedGenerated !== null) {
    return;                 // already loaded for this age group
  }

  _cachedAgeGroup = ageGroup;
  _preloadedGenerated = null;

  const modules = [];
  const keys   = [];
  if (maxDiff >= 1) { modules.push(import('./levels-diff1.js')); keys.push('LEVELS_DIFF1'); }
  if (maxDiff >= 2) { modules.push(import('./levels-diff2.js')); keys.push('LEVELS_DIFF2'); }
  if (maxDiff >= 3) { modules.push(import('./levels-diff3.js')); keys.push('LEVELS_DIFF3'); }
  if (maxDiff >= 4) { modules.push(import('./levels-diff4.js')); keys.push('LEVELS_DIFF4'); }
  if (maxDiff >= 5) { modules.push(import('./levels-diff5.js')); keys.push('LEVELS_DIFF5'); }

  _loadingPromise = Promise.all(modules).then(loaded => {
    const all = [];
    for (let i = 0; i < loaded.length; i++) {
      const arr = loaded[i][keys[i]];
      if (Array.isArray(arr)) all.push(...arr);
    }
    _preloadedGenerated = all;
    _loadingPromise = null;
  });

  return _loadingPromise;
}

export function areLevelsLoaded() {
  return _preloadedGenerated !== null;
}

/* ─── sync getters (require preloadLevels() to have resolved) ─── */
export function getLevels() {
  const state = getState();
  if (state.mode === 'editor-test' && state.customLevel) {
    return [state.customLevel];
  }
  if (state.mode === 'daily' && state.dailyLevel) {
    return [state.dailyLevel];
  }

  const rawStatic = LEVELS_BY_AGE[state.ageGroup] || [];

  // Validate static levels once per age group at runtime
  if (!_cachedStaticValid[state.ageGroup]) {
    const valid = [];
    for (const lv of rawStatic) {
      if (solveLevel(lv)) {
        valid.push(lv);
      } else {
        console.warn(`[getLevels] Static level "${lv.title}" is unsolvable — filtered out.`);
      }
    }
    _cachedStaticValid[state.ageGroup] = valid;
  }
  const staticLevels = _cachedStaticValid[state.ageGroup];

  const generated = _preloadedGenerated || [];
  return [...staticLevels, ...generated];
}

export function getGeneratedLevels() {
  return _preloadedGenerated || [];
}

export function getGeneratedLevelsV2() {
  return [];
}

export function getLevel() {
  return getLevels()[getState().levelIdx];
}
