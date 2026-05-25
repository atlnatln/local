/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Level Manager
   ═══════════════════════════════════════════════════════════ */

import { state, getLevel } from './state.js';
import { $ } from './utils.js';
import { buildGrid, updatePlayerPos } from './grid-renderer.js';
import { buildPalette, renderQueue } from './command-system.js';
import { updateStarsDisplay } from './ui-overlays.js';

export function loadLevel(idx) {
  if (idx !== undefined) state.levelIdx = idx;
  const lv = getLevel();
  if (!lv) return;

  state.playerX = lv.startX;
  state.playerY = lv.startY;
  state.playerVal = lv.startVal;
  state.queue = [];
  state.running = false;
  state.currentStep = -1;

  $('levelBadge').textContent = 'Seviye ' + (state.levelIdx + 1);
  $('levelTitle').textContent = lv.title;
  updateStarsDisplay(0);

  $('goalDesc').textContent = lv.desc;
  const valText = lv.targetVal != null ? ' = ' + lv.targetVal : '';
  $('goalDetail').textContent = lv.startVal + valText + ' → hedef';
  $('moveCounter').textContent = '0 / ' + lv.maxCmds;

  buildGrid(lv);
  updatePlayerPos(false);
  buildPalette(lv);
  renderQueue();
  $('btnRun').disabled = false;
  $('player').classList.remove('success');
}
