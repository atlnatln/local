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
  if (window.AudioEngine) AudioEngine.play('click');
  pushHistory();
  renderQueue();
  updateGhostPreview();
  saveGameState();
}
function renderQueue() {
  const lv = getLevel();
  cmdQueue.innerHTML = '';
  state.queue.forEach(function(cmdId, i) {
    const cmd = CMDS[cmdId];
    const chip = document.createElement('span');
    chip.className = 'cmd-chip ' + cmd.css;
    if (state.hintMode) chip.classList.add('ghost');
    chip.textContent = cmd.label;
    chip.addEventListener('click', function() {
      if (state.running) return;
      if (state.hintPreview) { hideHintPreview(); return; }
      state.queue.splice(i, 1);
      state.hintMode = false;
      pushHistory();
      renderQueue();
      updateGhostPreview();
      saveGameState();
    });
    cmdQueue.appendChild(chip);
  });
  cmdCount.textContent = state.queue.length + ' / ' + lv.maxCmds;
}

function showHintPreview() {
  const lv = getLevel();
  var hintCommands = lv.hintCommands || lv.solution || [];
  if (hintCommands.length === 0) return;
  if (state.running) return;
  if (state.hintPreview) return;
  state.hintPreview = true;
  state._queueBeforeHint = state.queue.slice();
  state.queue = hintCommands.slice();
  state.hintMode = true;
  renderQueue();
}

function hideHintPreview() {
  if (!state.hintPreview) return;
  state.hintPreview = false;
  state.queue = state._queueBeforeHint || [];
  state.hintMode = false;
  delete state._queueBeforeHint;
  renderQueue();
  saveGameState();
}

function showHint() {
  const lv = getLevel();
  var hintCommands = lv.hintCommands || lv.solution || [];
  if (hintCommands.length === 0) return;
  if (state.running) return;

  state.queue = hintCommands.slice();
  state.hintMode = true;
  pushHistory();
  renderQueue();
  updateGhostPreview();
  saveGameState();
  if (window.AudioEngine) AudioEngine.play('click');
}

function pushHistory() {
  if (state.historyIdx < state.history.length - 1) {
    state.history = state.history.slice(0, state.historyIdx + 1);
  }
  state.history.push(state.queue.slice());
  state.historyIdx++;
  if (state.history.length > 50) {
    state.history.shift();
    state.historyIdx--;
  }
}

function undo() {
  if (state.historyIdx > 0) {
    state.historyIdx--;
    state.queue = state.history[state.historyIdx].slice();
    state.hintMode = false;
    renderQueue();
    updateGhostPreview();
    saveGameState();
  }
}

function redo() {
  if (state.historyIdx < state.history.length - 1) {
    state.historyIdx++;
    state.queue = state.history[state.historyIdx].slice();
    state.hintMode = false;
    renderQueue();
    updateGhostPreview();
    saveGameState();
  }
}
