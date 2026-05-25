/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Main Entry Point
   ═══════════════════════════════════════════════════════════ */

import { state, getLevels, getLevel } from './state.js';
import { $ } from './utils.js';
import { ensureAudio } from './audio.js';
import { loadProgress } from './progress.js';
import { loadLevel } from './level-manager.js';
import { runProgram } from './execution-engine.js';
import { renderQueue } from './command-system.js';
import { showLevelSelect, hideOverlay, hideLevelSelect, updateStarsDisplay } from './ui-overlays.js';

/* ── Editor test level loader ───────────────────────────── */
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has('editor')) {
  try {
    const testLevel = JSON.parse(localStorage.getItem('editor_test_level') || 'null');
    if (testLevel) {
      import('./state.js').then(({ state, customTestLevel }) => {
        state.ageGroup = '__editor_test__';
        state.levelIdx = 0;
        // customTestLevel is a module-level let; we need to reassign it in the module
        // Since we can't mutate another module's let from here directly via import binding,
        // set it via a helper or just mutate state and handle in getLevels.
      });
      // Use direct assignment by importing the binding reference
    }
  } catch { /* ignore */ }
}

/* ── Splash screen interactions ─────────────────────────── */
document.querySelectorAll('.age-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.age-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.ageGroup = btn.dataset.age;
  });
});

$('btnStart').addEventListener('click', () => {
  ensureAudio();
  loadProgress();
  state.levelIdx = 0;
  $('splash').classList.add('hidden');
  $('game').classList.add('active');
  setTimeout(() => $('splash').style.display = 'none', 600);
  loadLevel();
});

$('btnHome').addEventListener('click', () => {
  $('game').classList.remove('active');
  $('splash').style.display = '';
  $('splash').classList.remove('hidden');
});

$('btnSound').addEventListener('click', () => {
  state.soundOn = !state.soundOn;
  $('btnSound').textContent = state.soundOn ? '🔊' : '🔇';
});

/* ── Command actions ────────────────────────────────────── */
$('btnRun').addEventListener('click', runProgram);
$('btnClear').addEventListener('click', () => { if (!state.running) { state.queue = []; renderQueue(); } });
$('btnUndo').addEventListener('click', () => { if (!state.running) { state.queue.pop(); renderQueue(); } });
$('btnReset').addEventListener('click', () => { if (!state.running) loadLevel(); });

/* ── Overlay interactions ───────────────────────────────── */
$('btnRetry').addEventListener('click', () => {
  hideOverlay();
  loadLevel();
});

$('btnNext').addEventListener('click', () => {
  hideOverlay();
  if (state.levelIdx < getLevels().length - 1) {
    state.levelIdx++;
    loadLevel();
  }
});

/* ── Level select ───────────────────────────────────────── */
$('btnLevels').addEventListener('click', () => showLevelSelect(loadLevel));
$('btnCloseLevels').addEventListener('click', hideLevelSelect);
$('btnCloseLevels2').addEventListener('click', hideLevelSelect);

/* ── Hint / Show Solution ───────────────────────────────── */
$('btnHint').addEventListener('click', () => {
  if (state.running) return;
  import('./hint-engine.js').then(({ solveLevel }) => {
    const lv = getLevel();
    const solution = solveLevel(lv);
    if (solution && solution.length > 0) {
      if (state.queue.length < lv.maxCmds) {
        state.queue.push(solution[0]);
        renderQueue();
      }
    } else {
      alert('Bu seviye için ipucu bulunamadı.');
    }
  });
});

$('btnShowSolution').addEventListener('click', () => {
  if (state.running) return;
  import('./hint-engine.js').then(({ solveLevel }) => {
    const lv = getLevel();
    const solution = solveLevel(lv);
    if (solution && solution.length > 0) {
      state.queue = solution.slice(0, lv.maxCmds);
      renderQueue();
      import('./execution-engine.js').then(({ runProgram }) => runProgram());
    } else {
      alert('Bu seviye için çözüm bulunamadı.');
    }
  });
});
