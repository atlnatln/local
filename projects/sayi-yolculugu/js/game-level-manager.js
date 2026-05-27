function getLevel() { return levels[state.levelIdx]; }
function loadLevel() {
  const lv = getLevel();
  if (!lv) {
    showAllComplete();
    return;
  }

  state.playerX = lv.startX;
  state.playerY = lv.startY;
  state.playerVal = lv.startVal;
  state.running = false;
  state.hintMode = false;
  state.startTime = Date.now();
  resetHistory();
  // state.queue ve state.attempts'ı KORUYORUZ (initGame'den restore edilmiş olabilir)

  if (window.currentSetId) {
    $('setBadge').textContent = 'Set ' + window.currentSetId;
    $('setBadge').style.display = '';
  } else {
    $('setBadge').style.display = 'none';
  }
  $('levelBadge').textContent = t('levelBadge', {n: state.levelIdx + 1});
  $('levelTitle').textContent = lv.title || '';
  updateStarsDisplay();

  $('goalDesc').textContent = lv.desc || t('targetDesc');
  // BUG FIX fallback: show effective target value when ops exist but targetVal is null
  const effectiveTargetVal = lv.targetVal != null
    ? lv.targetVal
    : (lv.ops && lv.ops.length > 0 ? lv.startVal : null);
  const valText = effectiveTargetVal != null ? ' = ' + effectiveTargetVal : '';
  $('goalDetail').textContent = lv.startVal + valText + ' → 🎯';
  $('moveCounter').textContent = t('cmdCount', {current: 0, max: lv.maxCmds});

  buildGrid(lv);
  updatePlayerPos(false);
  buildPalette(lv);
  renderQueue();
  updateGhostPreview();
  $('btnRun').disabled = false;

  if (lv.tutorialSteps && lv.tutorialSteps.length > 0 && !isTutorialShown(state.levelIdx)) {
    markTutorialShown(state.levelIdx);
    showTutorial(lv.tutorialSteps);
  }
}
function showLevelSelect() {
  var grid = $('levelGrid');
  grid.innerHTML = '';
  levels.forEach(function(lv, i) {
    var cell = document.createElement('div');
    cell.className = 'level-cell';

    var unlocked = i === 0 || (state.progress[i - 1] && state.progress[i - 1].completed);
    if (!unlocked) cell.classList.add('locked');
    if (state.progress[i] && state.progress[i].completed) cell.classList.add('completed');
    if (i === state.levelIdx) cell.classList.add('current');

    cell.innerHTML = '<span>' + (i + 1) + '</span>';
    if (state.progress[i]) {
      cell.innerHTML += '<span class="lc-stars">' + '⭐'.repeat(state.progress[i].stars) + '☆'.repeat(3 - state.progress[i].stars) + '</span>';
    }

    if (unlocked) {
      cell.addEventListener('click', function() {
        state.levelIdx = i;
        levelSelect.classList.remove('active');
        loadLevel();
      });
    }
    grid.appendChild(cell);
  });
  levelSelect.classList.add('active');
}
