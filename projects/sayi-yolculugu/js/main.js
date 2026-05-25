/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Main Entry Point
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';
import { getLevels, getLevel } from './state.js';
import { $ } from './utils.js';
import { ensureAudio } from './audio.js';
import { loadProgress } from './progress.js';
import { loadLevel } from './level-manager.js';
import { runProgram } from './execution-engine.js';
import { renderQueue } from './command-system.js';
import { showLevelSelect, hideOverlay, hideLevelSelect, showLeaderboard, hideLeaderboard } from './ui-overlays.js';
import { loadDailyChallenge } from './daily-challenge.js';
import { api } from './api-client.js';
import { loadSettings, saveSettings } from './settings.js';

/* ── Editor test level loader (BroadcastChannel + fallback) ─ */
let bc = null;
if ('BroadcastChannel' in window) {
  bc = new BroadcastChannel('sayi-yolculugu-editor');
  bc.onmessage = (ev) => {
    if (ev.data.type === 'LOAD_TEST_LEVEL') {
      dispatch({ type: 'LOAD_CUSTOM_LEVEL', payload: ev.data.puzzle });
      enterGameScreen();
      loadLevel(0);
    }
  };
}

// Fallback for browsers without BroadcastChannel
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has('editor')) {
  try {
    const testLevel = JSON.parse(localStorage.getItem('editor_test_level') || 'null');
    if (testLevel) {
      dispatch({ type: 'LOAD_CUSTOM_LEVEL', payload: testLevel });
      enterGameScreen();
      loadLevel(0);
    }
  } catch { /* ignore */ }
}

// Deep link: ?challenge=YYYY-MM-DD
const challengeDate = urlParams.get('challenge');
if (challengeDate) {
  (async () => {
    try {
      const res = await api.getDailyChallenge(challengeDate);
      if (res.puzzle) {
        dispatch({ type: 'LOAD_DAILY_LEVEL', payload: res.puzzle });
        enterGameScreen();
        loadLevel(0);
      }
    } catch (e) {
      console.error('Deep link challenge yüklenemedi:', e);
    }
  })();
}

function enterGameScreen() {
  $('splash').classList.add('hidden');
  $('game').classList.add('active');
  setTimeout(() => $('splash').style.display = 'none', 600);
}

function exitToSplash() {
  $('game').classList.remove('active');
  $('splash').style.display = '';
  $('splash').classList.remove('hidden');
}

/* ── Splash screen interactions ─────────────────────────── */
document.querySelectorAll('.age-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.age-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    dispatch({ type: 'SET_AGE_GROUP', payload: btn.dataset.age });
  });
});

$('btnStart').addEventListener('click', () => {
  ensureAudio();
  loadProgress();
  dispatch({ type: 'SET_MODE', payload: 'standard' });
  dispatch({ type: 'SET_LEVEL_IDX', payload: 0 });
  enterGameScreen();
  loadLevel();
});

$('btnDaily').addEventListener('click', async () => {
  ensureAudio();
  const puzzle = await loadDailyChallenge();
  if (puzzle) {
    enterGameScreen();
    loadLevel(0);
  } else {
    alert('Günlük challenge yüklenemedi. Lütfen tekrar dene.');
  }
});

$('btnLeaderboardSplash').addEventListener('click', async () => {
  try {
    const res = await api.getLeaderboard('all');
    showLeaderboard(res.entries || [], res.period || 'all');
  } catch (e) {
    showLeaderboard([], 'all');
  }
});

document.getElementById('btnCloseLeaderboard')?.addEventListener('click', hideLeaderboard);
document.querySelectorAll('#leaderboardOverlay .age-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const period = btn.dataset.period;
    try {
      const res = await api.getLeaderboard(period);
      showLeaderboard(res.entries || [], period);
    } catch (e) {
      showLeaderboard([], period);
    }
  });
});

$('btnHome').addEventListener('click', exitToSplash);

$('btnSound').addEventListener('click', () => {
  const soundOn = !getState().settings.soundOn;
  saveSettings({ soundOn });
  $('btnSound').textContent = soundOn ? '🔊' : '🔇';
});

/* ── Command actions ────────────────────────────────────── */
$('btnRun').addEventListener('click', runProgram);
$('btnClear').addEventListener('click', () => {
  if (!getState().running) { dispatch({ type: 'CLEAR_QUEUE' }); renderQueue(); }
});
$('btnUndo').addEventListener('click', () => {
  if (!getState().running) { dispatch({ type: 'POP_COMMAND' }); renderQueue(); }
});
$('btnReset').addEventListener('click', () => {
  if (!getState().running) loadLevel();
});

/* ── Overlay interactions ───────────────────────────────── */
$('btnRetry').addEventListener('click', () => {
  hideOverlay();
  loadLevel();
});

$('btnNext').addEventListener('click', () => {
  hideOverlay();
  const state = getState();
  if (state.levelIdx < getLevels().length - 1) {
    dispatch({ type: 'SET_LEVEL_IDX', payload: state.levelIdx + 1 });
    loadLevel();
  }
});

/* ── Level select ───────────────────────────────────────── */
$('btnLevels').addEventListener('click', () => showLevelSelect(() => loadLevel()));
$('btnCloseLevels').addEventListener('click', hideLevelSelect);
$('btnCloseLevels2').addEventListener('click', hideLevelSelect);

/* ── Hint / Show Solution ───────────────────────────────── */
$('btnHint').addEventListener('click', () => {
  if (getState().running) return;
  import('./hint-engine.js').then(({ solveLevel }) => {
    const lv = getLevel();
    const solution = solveLevel(lv);
    if (solution && solution.length > 0) {
      if (getState().queue.length < lv.maxCmds) {
        dispatch({ type: 'PUSH_COMMAND', payload: solution[0] });
        renderQueue();
      }
    } else {
      alert('Bu seviye için ipucu bulunamadı.');
    }
  });
});

$('btnShowSolution').addEventListener('click', () => {
  if (getState().running) return;
  import('./hint-engine.js').then(({ solveLevel }) => {
    const lv = getLevel();
    const solution = solveLevel(lv);
    if (solution && solution.length > 0) {
      dispatch({ type: 'CLEAR_QUEUE' });
      solution.slice(0, lv.maxCmds).forEach(cmd => {
        dispatch({ type: 'PUSH_COMMAND', payload: cmd });
      });
      renderQueue();
      import('./execution-engine.js').then(({ runProgram }) => runProgram());
    } else {
      alert('Bu seviye için çözüm bulunamadı.');
    }
  });
});

/* ── Keyboard shortcuts ─────────────────────────────────── */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if ($('overlay').classList.contains('active')) hideOverlay();
    else if ($('levelSelect').classList.contains('active')) hideLevelSelect();
  }
  if ((e.key === ' ' || e.key === 'Enter') && !$('overlay').classList.contains('active')) {
    if ($('game').classList.contains('active')) {
      e.preventDefault();
      runProgram();
    }
  }
  if (e.key === 'r' || e.key === 'R') {
    if ($('game').classList.contains('active') && !getState().running) {
      loadLevel();
    }
  }
});

/* ── Bootstrap ──────────────────────────────────────────── */
loadSettings();

// Settings panel interactions
const btnSettings = document.getElementById('btnSettings');
if (btnSettings) {
  btnSettings.addEventListener('click', () => {
    const panel = $('settingsPanel');
    panel.classList.toggle('active');
  });
}

const settSpeed = document.getElementById('settSpeed');
if (settSpeed) {
  settSpeed.addEventListener('change', (e) => {
    saveSettings({ animationSpeed: parseFloat(e.target.value) });
  });
}

const settFont = document.getElementById('settFont');
if (settFont) {
  settFont.addEventListener('change', (e) => {
    saveSettings({ fontSize: e.target.value });
  });
}

const settContrast = document.getElementById('settContrast');
if (settContrast) {
  settContrast.addEventListener('change', (e) => {
    saveSettings({ highContrast: e.target.checked });
  });
}

const settMotion = document.getElementById('settMotion');
if (settMotion) {
  settMotion.addEventListener('change', (e) => {
    saveSettings({ reducedMotion: e.target.checked });
  });
}

// Sync settings UI with store on load
(function syncSettingsUI() {
  const s = getState().settings;
  if (settSpeed) settSpeed.value = String(s.animationSpeed);
  if (settFont) settFont.value = s.fontSize;
  if (settContrast) settContrast.checked = s.highContrast;
  if (settMotion) settMotion.checked = s.reducedMotion;
})();
