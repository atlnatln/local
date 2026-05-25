/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Audio Engine
   ═══════════════════════════════════════════════════════════ */

import { state } from './state.js';

const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

export function ensureAudio() {
  if (!audioCtx) audioCtx = new AudioCtx();
  if (audioCtx.state === 'suspended') audioCtx.resume();
}

function playTone(freq, duration, type = 'sine', vol = 0.15) {
  if (!state.soundOn || !audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
  gain.gain.setValueAtTime(vol, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.start();
  osc.stop(audioCtx.currentTime + duration);
}

export function playMove()    { playTone(440,  0.12, 'sine',   0.1); }
export function playOp()      { playTone(660,  0.2,  'triangle', 0.12); }
export function playBump()    { playTone(180,  0.25, 'sawtooth', 0.08); }
export function playWin()     { playTone(523, 0.15); setTimeout(()=>playTone(659,0.15),150); setTimeout(()=>playTone(784,0.3),300); }
export function playFail()    { playTone(330, 0.3, 'sawtooth', 0.08); setTimeout(()=>playTone(280,0.4),200); }
export function playDrop()    { playTone(600, 0.08, 'sine', 0.08); }
export function playRemove()  { playTone(400, 0.08, 'sine', 0.08); }
export function playRun()     { playTone(500, 0.1); setTimeout(()=>playTone(700,0.1),100); }
