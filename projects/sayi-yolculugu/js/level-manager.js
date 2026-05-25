/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Level Manager
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';
import { getLevel } from './state.js';
import { $ } from './utils.js';
import { buildGrid, updatePlayerPos } from './grid-renderer.js';
import { buildPalette, renderQueue } from './command-system.js';
import { updateStarsDisplay } from './ui-overlays.js';

export function loadLevel(idx) {
  if (idx !== undefined) dispatch({ type: 'SET_LEVEL_IDX', payload: idx });
  const lv = getLevel();
  if (!lv) return;

  dispatch({ type: 'SET_PLAYER_POS', payload: { x: lv.startX, y: lv.startY } });
  dispatch({ type: 'SET_PLAYER_VAL', payload: lv.startVal });
  dispatch({ type: 'CLEAR_QUEUE' });
  dispatch({ type: 'SET_RUNNING', payload: false });
  dispatch({ type: 'SET_CURRENT_STEP', payload: -1 });

  const state = getState();
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
