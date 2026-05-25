/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Grid Renderer
   ═══════════════════════════════════════════════════════════ */

import { getState } from './store.js';
import { getLevel } from './state.js';
import { $ } from './utils.js';

export function calcCellSize(lv) {
  const max = Math.max(lv.cols, lv.rows);
  if (max <= 3) return 72;
  if (max <= 5) return 56;
  if (max <= 7) return 44;
  return 36;
}

export function buildGrid(lv) {
  const gridEl = $('grid');
  gridEl.innerHTML = '';
  const cellSize = calcCellSize(lv);
  gridEl.style.gridTemplateColumns = 'repeat(' + lv.cols + ', ' + cellSize + 'px)';

  const wallSet = new Set();
  lv.walls.forEach(w => wallSet.add(w[0] + ',' + w[1]));
  const opMap = {};
  lv.ops.forEach(o => { opMap[o.x + ',' + o.y] = o; });
  const lockMap = {};
  (lv.locks || []).forEach(l => { lockMap[l.x + ',' + l.y] = l; });
  const teleportMap = {};
  (lv.teleports || []).forEach(t => { teleportMap[t.x + ',' + t.y] = t; });
  const restartSet = new Set();
  (lv.restarts || []).forEach(r => { restartSet.add(r.x + ',' + r.y); });

  for (let r = 0; r < lv.rows; r++) {
    for (let c = 0; c < lv.cols; c++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.x = c;
      cell.dataset.y = r;
      cell.style.width = cellSize + 'px';
      cell.style.height = cellSize + 'px';

      const key = c + ',' + r;

      if (wallSet.has(key)) {
        cell.classList.add('wall');
      } else if (c === lv.targetX && r === lv.targetY) {
        cell.classList.add('target');
        if (lv.targetVal != null) {
          const tv = document.createElement('span');
          tv.className = 'target-value';
          tv.textContent = '= ' + lv.targetVal;
          cell.appendChild(tv);
        }
        cell.appendChild(document.createTextNode('🎯'));
      } else if (opMap[key]) {
        const op = opMap[key];
        if (op.type === '+') cell.classList.add('op-plus');
        else if (op.type === '-') cell.classList.add('op-minus');
        else if (op.type === '×') cell.classList.add('op-times');
        else if (op.type === '/') cell.classList.add('op-divide');
        else if (op.type === '^') cell.classList.add('op-square');
        cell.textContent = op.type + op.val;
      } else if (lockMap[key]) {
        const lock = lockMap[key];
        cell.classList.add('lock');
        cell.textContent = '🔒' + lock.requiredVal;
      } else if (teleportMap[key]) {
        cell.classList.add('teleport');
        cell.textContent = '🌀';
      } else if (restartSet.has(key)) {
        cell.classList.add('restart');
        cell.textContent = '↺';
      } else {
        cell.classList.add('empty');
      }

      gridEl.appendChild(cell);
    }
  }

  const playerEl = $('player');
  playerEl.style.width = cellSize + 'px';
  playerEl.style.height = cellSize + 'px';
  playerEl.style.transition = 'transform .35s cubic-bezier(.4,0,.2,1)';
}

export function updatePlayerPos(animate) {
  const state = getState();
  const lv = getLevel();
  const gridEl = $('grid');
  const playerEl = $('player');
  const cellSize = calcCellSize(lv);
  const gap = 4;
  const left = state.playerX * (cellSize + gap);
  const top = state.playerY * (cellSize + gap);

  playerEl.style.transform = 'translate(' + left + 'px, ' + top + 'px)';
  playerEl.textContent = state.playerVal;

  if (animate) {
    playerEl.classList.remove('bump');
    void playerEl.offsetWidth;
    playerEl.classList.add('bump');
    setTimeout(() => playerEl.classList.remove('bump'), 300);
  }
}
