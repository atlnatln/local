function buildPalette(lv) {
  cmdPalette.innerHTML = '';
  (lv.commands || []).forEach(function(cmdId) {
    const cmd = CMDS[cmdId];
    if (!cmd) return;
    const btn = document.createElement('button');
    btn.className = 'cmd-btn ' + cmd.css;
    btn.textContent = cmd.label;
    btn.addEventListener('click', function() { addCommand(cmdId); });
    cmdPalette.appendChild(btn);
  });
}
function addCommand(cmdId) {
  const lv = getLevel();
  if (state.running || state.queue.length >= lv.maxCmds) return;
  state.queue.push(cmdId);
  renderQueue();
  saveGameState();
}
function renderQueue() {
  const lv = getLevel();
  cmdQueue.innerHTML = '';
  state.queue.forEach(function(cmdId, i) {
    const cmd = CMDS[cmdId];
    const chip = document.createElement('span');
    chip.className = 'cmd-chip ' + cmd.css;
    chip.textContent = cmd.label;
    chip.addEventListener('click', function() {
      if (state.running) return;
      state.queue.splice(i, 1);
      renderQueue();
    });
    cmdQueue.appendChild(chip);
  });
  cmdCount.textContent = state.queue.length + ' / ' + lv.maxCmds;
}
