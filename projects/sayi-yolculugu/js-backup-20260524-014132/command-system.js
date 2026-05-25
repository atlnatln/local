/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Command System
   ═══════════════════════════════════════════════════════════ */

import { state, getLevel, CMDS, ICONS } from './state.js';
import { $ } from './utils.js';
import { playDrop, playRemove } from './audio.js';

export function buildPalette(lv) {
  const cmdPalette = $('cmdPalette');
  cmdPalette.innerHTML = '';
  lv.commands.forEach(cmdId => {
    const cmd = CMDS[cmdId];
    if (!cmd) return;
    const btn = document.createElement('button');
    btn.className = 'cmd-btn ' + cmd.css;
    btn.innerHTML = '<span>' + (ICONS[cmdId] || '') + '</span> ' + cmd.label;
    btn.addEventListener('click', () => addCommand(cmdId));
    cmdPalette.appendChild(btn);
  });
}

export function addCommand(cmdId) {
  const lv = getLevel();
  if (state.running || state.queue.length >= lv.maxCmds) return;
  state.queue.push(cmdId);
  playDrop();
  renderQueue();
}

export function renderQueue() {
  const lv = getLevel();
  const cmdQueue = $('cmdQueue');
  const cmdCount = $('cmdCount');
  cmdQueue.innerHTML = '';
  if (state.queue.length === 0) {
    cmdQueue.innerHTML = '<div class="cmd-queue-empty">Komutları buraya ekle...</div>';
  } else {
    state.queue.forEach((cmdId, i) => {
      const cmd = CMDS[cmdId];
      if (!cmd) return;
      const chip = document.createElement('button');
      chip.className = 'cmd-chip ' + cmd.css;
      if (state.running && state.currentStep === i) chip.classList.add('running');
      if (state.running && state.currentStep > i) chip.classList.add('done');
      chip.innerHTML = '<span>' + (ICONS[cmdId] || '') + '</span> ' + cmd.label;
      chip.dataset.index = i;
      if (!state.running) {
        chip.addEventListener('click', () => {
          state.queue.splice(i, 1);
          playRemove();
          renderQueue();
        });
      }
      cmdQueue.appendChild(chip);
    });
  }
  cmdCount.textContent = state.queue.length + ' / ' + lv.maxCmds;
}
