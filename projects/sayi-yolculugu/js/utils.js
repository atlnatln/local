/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Utilities
   ═══════════════════════════════════════════════════════════ */

export const $ = (id) => document.getElementById(id);

export function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export function deepClone(obj) {
  if (typeof structuredClone === 'function') {
    return structuredClone(obj);
  }
  return JSON.parse(JSON.stringify(obj));
}

export function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}
