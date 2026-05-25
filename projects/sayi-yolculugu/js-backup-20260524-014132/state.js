/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — State & Commands
   ═══════════════════════════════════════════════════════════ */

import { LEVELS_BY_AGE } from './levels-data.js';

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

export let customTestLevel = null;

export let state = {
  ageGroup: '7-8',
  levelIdx: 0,
  playerX: 0, playerY: 0, playerVal: 0,
  queue: [],
  running: false,
  currentStep: -1,
  progress: {},
  soundOn: true,
};

export function getLevels() {
  if (state.ageGroup === '__editor_test__' && customTestLevel) {
    return [customTestLevel];
  }
  return LEVELS_BY_AGE[state.ageGroup] || [];
}

export function getLevel() {
  return getLevels()[state.levelIdx];
}
