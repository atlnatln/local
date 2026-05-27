/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Execution Engine
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';
import { getLevel, CMDS } from './state.js';
import { $, sleep } from './utils.js';
import { updatePlayerPos, updateWallVisuals } from './grid-renderer.js';
import { renderQueue } from './command-system.js';
import { showWinOverlay } from './ui-overlays.js';
import { saveProgress } from './progress.js';
import { playMove, playOp, playBump, playWin, playFail, playRun, ensureAudio } from './audio.js';
import { track } from './analytics.js';

export async function runProgram() {
  const state = getState();
  if (state.running || state.queue.length === 0) return;
  ensureAudio();
  playRun();
  dispatch({ type: 'SET_RUNNING', payload: true });
  $('btnRun').disabled = true;

  const lv = getLevel();
  dispatch({ type: 'SET_PLAYER_POS', payload: { x: lv.startX, y: lv.startY } });
  dispatch({ type: 'SET_PLAYER_VAL', payload: lv.startVal });
  dispatch({ type: 'SET_CURRENT_STEP', payload: -1 });
  updatePlayerPos(false);
  const playerEl = $('player');
  playerEl.classList.remove('success');

  track('level_start', { ageGroup: state.ageGroup, levelIdx: state.levelIdx });

  await sleep(200);

  let px = lv.startX, py = lv.startY, pval = lv.startVal;
  let activeWalls = new Set();   // toggle-activated extra walls
  updateWallVisuals(activeWalls);

  for (let i = 0; i < state.queue.length; i++) {
    if (!getState().running) break;

    const cmdId = state.queue[i];
    const cmd = CMDS[cmdId];
    if (!cmd) continue;

    dispatch({ type: 'SET_CURRENT_STEP', payload: i });
    renderQueue();

    // Z operations - value only
    if (cmd.dz !== 0) {
      pval += cmd.dz;
      // Clamp value to match Python BFS limits
      const VAL_MIN = -500;
      const VAL_MAX = 5000;
      if (pval < VAL_MIN) pval = VAL_MIN;
      if (pval > VAL_MAX) pval = VAL_MAX;
      dispatch({ type: 'SET_PLAYER_VAL', payload: pval });
      playerEl.textContent = pval;
      playMove();
      await sleep(400);
      continue;
    }

    const nx = px + cmd.dx;
    const ny = py + cmd.dy;

    // Bounds check
    if (nx < 0 || nx >= lv.cols || ny < 0 || ny >= lv.rows) {
      playerEl.classList.add('bump');
      playBump();
      await sleep(200);
      playerEl.classList.remove('bump');
      await sleep(150);
      continue;
    }

    // Wall check: supports legacy [x,y], full dict, directional dict, and toggle switches
    const posKey = `${nx},${ny}`;
    const wall = lv.walls.find(w => {
      if (Array.isArray(w)) return w[0] === nx && w[1] === ny;
      return w.x === nx && w.y === ny;
    });
    if (wall && !activeWalls.has(posKey)) {
      let blocked = true;
      if (!Array.isArray(wall) && wall.type === 'directional') {
        const dirMap = { '1,0': 'E', '-1,0': 'W', '0,1': 'S', '0,-1': 'N' };
        const dir = dirMap[`${cmd.dx},${cmd.dy}`];
        if (dir && !wall.blocks.includes(dir)) {
          blocked = false;
        }
      }
      if (blocked) {
        playerEl.classList.add('bump');
        playBump();
        await sleep(200);
        playerEl.classList.remove('bump');
        await sleep(150);
        continue;
      }
    }

    // Lock check
    const lock = (lv.locks || []).find(l => l.x === nx && l.y === ny);
    if (lock && pval !== lock.requiredVal) {
      playerEl.classList.add('bump');
      playBump();
      await sleep(200);
      playerEl.classList.remove('bump');
      await sleep(150);
      continue;
    }

    // Move
    const prevPx = px;
    const prevPy = py;
    px = nx; py = ny;
    dispatch({ type: 'SET_PLAYER_POS', payload: { x: px, y: py } });

    // Operator cell
    const op = lv.ops.find(o => o.x === nx && o.y === ny);
    if (op) {
      if (op.type === '+') pval += op.val;
      else if (op.type === '-') pval -= op.val;
      else if (op.type === '×') pval *= op.val;
      else if (op.type === '/') {
        if (pval % op.val === 0) pval = Math.floor(pval / op.val);
        else {
          px = prevPx; py = prevPy;
          dispatch({ type: 'SET_PLAYER_POS', payload: { x: px, y: py } });
          playerEl.classList.add('bump');
          playBump();
          updatePlayerPos(false);
          await sleep(200);
          playerEl.classList.remove('bump');
          await sleep(150);
          continue;
        }
      }
      else if (op.type === '^') pval *= pval;
      // Clamp value to match Python BFS limits
      const VAL_MIN = -500;
      const VAL_MAX = 5000;
      if (pval < VAL_MIN) pval = VAL_MIN;
      if (pval > VAL_MAX) pval = VAL_MAX;
      dispatch({ type: 'SET_PLAYER_VAL', payload: pval });
      playOp();
    } else {
      playMove();
    }

    // Restart check
    const isRestart = (lv.restarts || []).some(r => r.x === px && r.y === py);
    if (isRestart) {
      pval = lv.startVal;
      dispatch({ type: 'SET_PLAYER_VAL', payload: pval });
      playerEl.textContent = pval;
    }

    // Teleport check
    const teleport = (lv.teleports || []).find(t => t.x === px && t.y === py);
    if (teleport) {
      px = teleport.targetX;
      py = teleport.targetY;
      dispatch({ type: 'SET_PLAYER_POS', payload: { x: px, y: py } });
      const oldTransition = playerEl.style.transition;
      playerEl.style.transition = 'none';
      updatePlayerPos(false);
      playerEl.style.transition = oldTransition;
    }

    // Toggle switch check
    const sw = (lv.toggleSwitches || []).find(s => s.x === px && s.y === py);
    if (sw) {
      (sw.toggleWalls || []).forEach(([wx, wy]) => {
        const wk = `${wx},${wy}`;
        if (activeWalls.has(wk)) activeWalls.delete(wk);
        else activeWalls.add(wk);
      });
      updateWallVisuals(activeWalls);
    }

    updatePlayerPos(true);
    await sleep(400);
  }

  dispatch({ type: 'SET_CURRENT_STEP', payload: -1 });
  renderQueue();
  await sleep(200);
  checkWin(px, py, pval);
}

export function checkWin(px, py, pval) {
  const lv = getLevel();
  const posOk = px === lv.targetX && py === lv.targetY;
  const valOk = lv.targetVal == null || pval === lv.targetVal;
  const playerEl = $('player');
  const state = getState();

  if (posOk && valOk) {
    const usedCmds = state.queue.length;
    let stars = 1;
    if (usedCmds <= lv.stars[0]) stars = 3;
    else if (usedCmds <= lv.stars[1]) stars = 2;

    playWin();
    playerEl.classList.add('success');
    setTimeout(() => {
      playerEl.classList.remove('success');
      showWinOverlay(stars);
    }, 600);

    const prog = state.progress[state.ageGroup] || {};
    const prev = prog[state.levelIdx];
    if (!prev || prev.stars < stars) {
      dispatch({ type: 'SAVE_LEVEL_PROGRESS', payload: { ageGroup: state.ageGroup, levelIdx: state.levelIdx, stars } });
      saveProgress();
    }

    track('level_complete', {
      ageGroup: state.ageGroup,
      levelIdx: state.levelIdx,
      stars,
      cmdCount: usedCmds,
    });
  } else {
    playFail();
    $('overlayTitle').textContent = '😢 Hedefine ulaşamadın';
    $('overlayTitle').style.color = '#e94560';
    document.getElementById('s1').textContent = '☆';
    document.getElementById('s2').textContent = '☆';
    document.getElementById('s3').textContent = '☆';
    document.getElementById('s1').className = '';
    document.getElementById('s2').className = '';
    document.getElementById('s3').className = '';
    $('overlayMsg').textContent = (posOk && !valOk)
      ? 'Sayın ' + pval + ' — ama hedef ' + lv.targetVal + ' olmalıydı.'
      : 'Doğru konuma ulaşamadın. Tekrar dene!';
    $('btnNext').style.display = 'none';
    $('overlay').classList.add('active');

    track('level_fail', {
      ageGroup: state.ageGroup,
      levelIdx: state.levelIdx,
      cmdCount: state.queue.length,
      failReason: posOk && !valOk ? 'wrong_value' : 'wrong_position',
    });
  }

  dispatch({ type: 'SET_RUNNING', payload: false });
  $('btnRun').disabled = false;
}
