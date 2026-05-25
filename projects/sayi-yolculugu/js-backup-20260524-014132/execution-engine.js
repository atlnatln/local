/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Execution Engine
   ═══════════════════════════════════════════════════════════ */

import { state, getLevel, CMDS } from './state.js';
import { $, sleep } from './utils.js';
import { updatePlayerPos } from './grid-renderer.js';
import { renderQueue } from './command-system.js';
import { showWinOverlay } from './ui-overlays.js';
import { saveProgress } from './progress.js';
import { playMove, playOp, playBump, playWin, playFail, playRun, ensureAudio } from './audio.js';

export async function runProgram() {
  if (state.running || state.queue.length === 0) return;
  ensureAudio();
  playRun();
  state.running = true;
  $('btnRun').disabled = true;

  const lv = getLevel();
  state.playerX = lv.startX;
  state.playerY = lv.startY;
  state.playerVal = lv.startVal;
  state.currentStep = -1;
  updatePlayerPos(false);
  const playerEl = $('player');
  playerEl.classList.remove('success');

  await sleep(200);

  let px = lv.startX, py = lv.startY, pval = lv.startVal;

  for (let i = 0; i < state.queue.length; i++) {
    if (!state.running) break;

    const cmdId = state.queue[i];
    const cmd = CMDS[cmdId];
    if (!cmd) continue;

    state.currentStep = i;
    renderQueue();

    // Z operations - value only
    if (cmd.dz !== 0) {
      pval += cmd.dz;
      state.playerVal = pval;
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

    // Wall check
    const isWall = lv.walls.some(w => w[0] === nx && w[1] === ny);
    if (isWall) {
      playerEl.classList.add('bump');
      playBump();
      await sleep(200);
      playerEl.classList.remove('bump');
      await sleep(150);
      continue;
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
    state.playerX = px;
    state.playerY = py;

    // Operator cell
    const op = lv.ops.find(o => o.x === nx && o.y === ny);
    if (op) {
      if (op.type === '+') pval += op.val;
      else if (op.type === '-') pval -= op.val;
      else if (op.type === '×') pval *= op.val;
      else if (op.type === '/') {
        if (pval % op.val === 0) pval /= op.val;
        else {
          px = prevPx; py = prevPy;
          state.playerX = px; state.playerY = py;
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
      state.playerVal = pval;
      playOp();
    } else {
      playMove();
    }

    // Restart check
    const isRestart = (lv.restarts || []).some(r => r.x === px && r.y === py);
    if (isRestart) {
      pval = lv.startVal;
      state.playerVal = pval;
      playerEl.textContent = pval;
    }

    // Teleport check
    const teleport = (lv.teleports || []).find(t => t.x === px && t.y === py);
    if (teleport) {
      px = teleport.targetX;
      py = teleport.targetY;
      state.playerX = px;
      state.playerY = py;
      const oldTransition = playerEl.style.transition;
      playerEl.style.transition = 'none';
      updatePlayerPos(false);
      playerEl.style.transition = oldTransition;
    }

    updatePlayerPos(true);
    await sleep(400);
  }

  state.currentStep = -1;
  renderQueue();
  await sleep(200);
  checkWin(px, py, pval);
}

export function checkWin(px, py, pval) {
  const lv = getLevel();
  const posOk = px === lv.targetX && py === lv.targetY;
  const valOk = lv.targetVal == null || pval === lv.targetVal;
  const playerEl = $('player');

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
      prog[state.levelIdx] = { completed: true, stars };
      state.progress[state.ageGroup] = prog;
      saveProgress();
    }
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
  }

  state.running = false;
  $('btnRun').disabled = false;
}
