/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Progress (localStorage + backend sync)
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';
import { api } from './api-client.js';
import { track } from './analytics.js';

const STORAGE_KEY = 'sy_progress';

export function loadProgress() {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    dispatch({ type: 'LOAD_PROGRESS', payload: data });
  } catch {
    dispatch({ type: 'LOAD_PROGRESS', payload: {} });
  }
}

export function saveProgress() {
  const state = getState();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress));
}

export async function savePuzzleProgress(childName, version, levelIndex, completed, stars, cmdCount) {
  // 1. Local store güncelle
  dispatch({
    type: 'SET_PUZZLE_PROGRESS',
    payload: { version: String(version), index: String(levelIndex), stars, attempts: 1 },
  });
  // 2. localStorage'a yaz
  const state = getState();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.puzzleProgress));

  // 3. Backend'e gönder (best effort)
  if (!childName) return;
  try {
    await api.saveProgress({
      child_name: childName,
      puzzle_set_version: version,
      level_index: levelIndex,
      completed,
      stars,
      cmd_count: cmdCount,
    });
    track('save_progress', { success: true, version, levelIndex, stars });
  } catch (e) {
    track('save_progress', { success: false, error: String(e) });
  }
}

export async function syncProgress(childName) {
  const state = getState();
  if (!childName) return;

  try {
    const res = await api.syncProgress({
      child_name: childName,
      progress: state.puzzleProgress,
    });
    if (res.server_progress) {
      dispatch({ type: 'LOAD_PROGRESS', payload: res.server_progress });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(res.server_progress));
    }
    track('sync_attempt', { success: true, syncedCount: res.synced || 0 });
  } catch (e) {
    track('sync_attempt', { success: false, error: String(e) });
  }
}
