/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Utilities
   ═══════════════════════════════════════════════════════════ */

export const $ = (id) => document.getElementById(id);

export function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
