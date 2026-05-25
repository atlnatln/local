/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Store (Single Source of Truth)
   Redux-like lightweight state management.
   ═══════════════════════════════════════════════════════════ */

import { events } from './event-bus.js';
import { deepClone } from './utils.js';

const INITIAL_STATE = {
  // Navigasyon
  ageGroup: '7-8',
  levelIdx: 0,
  mode: 'standard',        // 'standard' | 'daily' | 'editor-test' | 'custom'
  customLevel: null,       // Editor'den gelen test seviyesi
  dailyLevel: null,        // Günlük challenge seviyesi

  // Oyun durumu
  playerX: 0,
  playerY: 0,
  playerVal: 0,
  queue: [],
  running: false,
  currentStep: -1,

  // İlerleme
  progress: {},            // { ageGroup: { levelIdx: {completed, stars} } }
  puzzleProgress: {},      // { version: { index: {stars, attempts} } }

  // Ayarlar
  settings: {
    animationSpeed: 1,     // 0.25 | 0.5 | 1 | 1.5 | 2
    fontSize: 'medium',    // 'small' | 'medium' | 'large'
    highContrast: false,
    reducedMotion: false,  // prefers-reduced-motion || manual
    soundOn: true,
  },

  // Analytics (geçici buffer)
  sessionEvents: [],       // [{type, timestamp, data}]
};

let _state = deepClone(INITIAL_STATE);

function reducer(state, action) {
  switch (action.type) {
    // Navigasyon
    case 'SET_AGE_GROUP':
      return { ...state, ageGroup: action.payload };
    case 'SET_LEVEL_IDX':
      return { ...state, levelIdx: action.payload };
    case 'SET_MODE':
      return { ...state, mode: action.payload };
    case 'LOAD_CUSTOM_LEVEL':
      return { ...state, customLevel: deepClone(action.payload), mode: 'editor-test' };
    case 'LOAD_DAILY_LEVEL':
      return { ...state, dailyLevel: deepClone(action.payload), mode: 'daily' };

    // Oyun
    case 'RESET_LEVEL':
      return { ...state, queue: [], running: false, currentStep: -1 };
    case 'PUSH_COMMAND':
      return { ...state, queue: [...state.queue, action.payload] };
    case 'POP_COMMAND':
      return { ...state, queue: state.queue.slice(0, -1) };
    case 'REMOVE_COMMAND_AT': {
      const idx = action.payload;
      return { ...state, queue: state.queue.filter((_, i) => i !== idx) };
    }
    case 'CLEAR_QUEUE':
      return { ...state, queue: [] };
    case 'SET_RUNNING':
      return { ...state, running: action.payload };
    case 'SET_CURRENT_STEP':
      return { ...state, currentStep: action.payload };
    case 'SET_PLAYER_POS':
      return { ...state, playerX: action.payload.x, playerY: action.payload.y };
    case 'SET_PLAYER_VAL':
      return { ...state, playerVal: action.payload };

    // İlerleme
    case 'LOAD_PROGRESS':
      return { ...state, progress: deepClone(action.payload) };
    case 'SAVE_LEVEL_PROGRESS': {
      const { ageGroup, levelIdx, stars } = action.payload;
      const group = { ...(state.progress[ageGroup] || {}), [levelIdx]: { completed: true, stars } };
      return { ...state, progress: { ...state.progress, [ageGroup]: group } };
    }
    case 'SET_PUZZLE_PROGRESS': {
      const { version, index, stars, attempts } = action.payload;
      const ver = { ...(state.puzzleProgress[version] || {}), [index]: { stars, attempts } };
      return { ...state, puzzleProgress: { ...state.puzzleProgress, [version]: ver } };
    }

    // Ayarlar
    case 'UPDATE_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } };

    // Analytics
    case 'PUSH_ANALYTICS_EVENT':
      return { ...state, sessionEvents: [...state.sessionEvents, action.payload] };
    case 'CLEAR_ANALYTICS_BUFFER':
      return { ...state, sessionEvents: [] };

    default:
      return state;
  }
}

export function dispatch(action) {
  const prev = _state;
  _state = reducer(_state, action);
  events.emit('state:changed', { state: _state, prev, action });
  events.emit(action.type, action.payload);
}

export function getState() {
  return _state;
}
