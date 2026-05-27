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
};
let currentSignature = '';

const STORAGE_KEY = 'sayiYolculuguState';

function getSetSignature(data) {
  if (data.set_id) return 'set_' + data.set_id;
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
