// ── State ────────────────────────────────────────────────
let levels = [];
let state = {
  levelIdx: 0,
  playerX: 0, playerY: 0, playerVal: 0,
  queue: [],
  running: false,
  progress: {},
  startTime: 0,
  attempts: 0,
  hintMode: false,
  history: [],
  historyIdx: -1,
};
let currentSignature = '';

const STORAGE_KEY = 'sayiYolculuguState';

function getSetSignature(data) {
  if (data.set_id) return 'set_' + data.set_id;
  if (data.version != null) return 'set_v' + data.version;
  if (levels.length > 0) {
    const firstId = levels[0].id != null ? levels[0].id : 1;
    return 'lv_' + firstId + '_' + levels.length;
  }
  return 'unknown';
}

function saveGameState() {
  try {
    const payload = {
      signature: currentSignature,
      levelIdx: state.levelIdx,
      queue: state.queue,
      attempts: state.attempts,
      progress: state.progress,
      hintMode: state.hintMode,
      timestamp: Date.now()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch(e) {}
}

function restoreGameState(signature) {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const payload = JSON.parse(raw);
    if (payload.signature !== signature) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return payload;
  } catch(e) {
    return null;
  }
}

function clearGameState() {
  try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
}

/* ── History (Undo/Redo) ────────────────────────────────── */
function resetHistory() {
  state.history = [[]];
  state.historyIdx = 0;
}

/* ── Achievements ───────────────────────────────────────── */
function loadAchievements() {
  try {
    const raw = localStorage.getItem('sy_achievements');
    if (raw) return JSON.parse(raw);
  } catch(e) {}
  return {};
}
function saveAchievements(ach) {
  try { localStorage.setItem('sy_achievements', JSON.stringify(ach)); } catch(e) {}
}
function unlockAchievement(id) {
  var ach = loadAchievements();
  if (!ach[id]) {
    ach[id] = { unlockedAt: Date.now() };
    saveAchievements(ach);
    if (window.showAchievementToast) showAchievementToast(id);
  }
}

/* ── Settings ───────────────────────────────────────────── */
function loadSettings() {
  try {
    const raw = localStorage.getItem('sy_settings');
    if (raw) return JSON.parse(raw);
  } catch(e) {}
  return { audio: true, haptic: true };
}

function saveSettings(settings) {
  try {
    localStorage.setItem('sy_settings', JSON.stringify(settings));
  } catch(e) {}
}


