function spawnParticles(x, y) {
  for (let i = 0; i < 10; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = (x + 24) + 'px';
    p.style.top = (y + 24) + 'px';
    const angle = Math.random() * Math.PI * 2;
    const dist = 30 + Math.random() * 40;
    p.style.setProperty('--tx', Math.cos(angle) * dist + 'px');
    p.style.setProperty('--ty', Math.sin(angle) * dist + 'px');
    gridEl.appendChild(p);
    setTimeout(function() { p.remove(); }, 800);
  }
}

async function runProgram() {
  if (state.running || state.queue.length === 0) return;
  state.running = true;
  state.attempts++;
  $('btnRun').disabled = true;

  try {
    const lv = getLevel();
  state.playerX = lv.startX;
  state.playerY = lv.startY;
  state.playerVal = lv.startVal;
  updatePlayerPos(false);

  var activeWalls = new Set();
  updateWallVisuals(activeWalls);

  var unlockedLocks = new Set();
  var activatedSwitches = new Set();

  const chips = cmdQueue.querySelectorAll('.cmd-chip');

  // Build opMap once for O(1) lookup throughout the execution
  const opMap = {};
  (lv.ops || []).forEach(function(o) { opMap[o.x + ',' + o.y] = o; });

  for (let i = 0; i < state.queue.length; i++) {
    const cmdId = state.queue[i];
    const cmd = CMDS[cmdId];
    chips[i].classList.add('running');

    if (cmd.dz !== 0) {
      state.playerVal += cmd.dz;
      updatePlayerPos(true);
      await sleep(300);
      chips[i].classList.remove('running');
      continue;
    }

    const nx = state.playerX + cmd.dx;
    const ny = state.playerY + cmd.dy;

    if (nx < 0 || nx >= lv.cols || ny < 0 || ny >= lv.rows) {
      chips[i].classList.remove('running');
      await sleep(200);
      continue;
    }

    const wall = (lv.walls || []).find(function(w) {
      if (Array.isArray(w)) return w[0] === nx && w[1] === ny;
      return w.x === nx && w.y === ny;
    });
    if (wall && !activeWalls.has(nx + ',' + ny)) {
      var blocked = true;
      if (!Array.isArray(wall) && wall.type === 'directional') {
        var dirMap = { '1,0': 'E', '-1,0': 'W', '0,1': 'S', '0,-1': 'N' };
        var dir = dirMap[cmd.dx + ',' + cmd.dy];
        if (dir && wall.blocks.indexOf(dir) === -1) {
          blocked = false;
        }
      }
      if (blocked) {
        chips[i].classList.remove('running');
        playerEl.classList.add('bump');
        if (window.AudioEngine) AudioEngine.play('bump');
        notifyAndroid('haptic', {type: 'light'});
        await sleep(200);
        playerEl.classList.remove('bump');
        await sleep(150);
        continue;
      }
    }

    // Lock check (persistent — once unlocked, stays unlocked)
    const lock = (lv.locks || []).find(function(l) { return l.x === nx && l.y === ny; });
    if (lock) {
      var lockKey = nx + ',' + ny;
      if (!unlockedLocks.has(lockKey)) {
        if (state.playerVal !== lock.requiredVal) {
          chips[i].classList.remove('running');
          playerEl.classList.add('bump');
          if (window.AudioEngine) AudioEngine.play('bump');
          notifyAndroid('haptic', {type: 'light'});
          await sleep(200);
          playerEl.classList.remove('bump');
          await sleep(150);
          continue;
        }
        unlockedLocks.add(lockKey);
      }
    }

    var prevX = state.playerX;
    var prevY = state.playerY;
    state.playerX = nx;
    state.playerY = ny;

    // Toggle switch check (persistent + before op, matching Python BFS order)
    const sw = (lv.toggleSwitches || []).find(function(s) { return s.x === state.playerX && s.y === state.playerY; });
    if (sw) {
      var swKey = state.playerX + ',' + state.playerY;
      if (!activatedSwitches.has(swKey)) {
        activatedSwitches.add(swKey);
        (sw.toggleWalls || []).forEach(function(tw) {
          var wk = tw[0] + ',' + tw[1];
          if (activeWalls.has(wk)) activeWalls.delete(wk);
          else activeWalls.add(wk);
        });
        updateWallVisuals(activeWalls);
      }
    }

    // Op apply — use the pre-built opMap for O(1) lookup
    const op = opMap[state.playerX + ',' + state.playerY];
    if (op) {
      if (op.type === '+') state.playerVal += op.val;
      else if (op.type === '-') state.playerVal -= op.val;
      else if (op.type === '×' || op.type === '*') state.playerVal *= op.val;
      else if (op.type === '/') {
        if (state.playerVal % op.val === 0) state.playerVal = Math.floor(state.playerVal / op.val);
        else {
          state.playerX = prevX; state.playerY = prevY;
          playerEl.classList.add('bump');
          updatePlayerPos(false);
          await sleep(200);
          playerEl.classList.remove('bump');
          await sleep(150);
          continue;
        }
      }
      else if (op.type === '^') state.playerVal *= state.playerVal;
      // Prune on boundary (matching Python BFS: state discarded)
      var VAL_MIN = -500;
      var VAL_MAX = 5000;
      if (state.playerVal < VAL_MIN || state.playerVal > VAL_MAX) {
        state.playerX = prevX;
        state.playerY = prevY;
        playerEl.classList.add('bump');
        updatePlayerPos(false);
        await sleep(200);
        playerEl.classList.remove('bump');
        await sleep(150);
        continue;
      }
    }

    // Restart check
    const isRestart = (lv.restarts || []).some(function(r) { return r.x === state.playerX && r.y === state.playerY; });
    if (isRestart) {
      state.playerVal = lv.startVal;
    }

    // Teleport check
    const teleport = (lv.teleports || []).find(function(t) { return t.x === state.playerX && t.y === state.playerY; });
    if (teleport) {
      state.playerX = teleport.targetX;
      state.playerY = teleport.targetY;
      const oldTransition = playerEl.style.transition;
      playerEl.style.transition = 'none';
      updatePlayerPos(false);
      playerEl.style.transition = oldTransition;
    }

    updatePlayerPos(true);
    await sleep(300);
    chips[i].classList.remove('running');
  }

  await sleep(200);
  checkWin();
  } catch (e) {
    console.error('[Game] runProgram error:', e);
    try {
      $('overlayTitle').textContent = t('error');
      $('overlayStars').textContent = '';
      $('overlayMsg').textContent = t('errorMsg');
      $('btnNext').style.display = 'none';
      overlay.classList.add('active');
    } catch(_) {}
  } finally {
    state.running = false;
    $('btnRun').disabled = false;
  }
}
function checkWin() {
  const lv = getLevel();
  const posOk = state.playerX === lv.targetX && state.playerY === lv.targetY;
  // Aligned with Python BFS: targetVal == null means position-only victory
  const valOk = lv.targetVal == null || state.playerVal === lv.targetVal;

  if (posOk && valOk) {
    if (window.AudioEngine) AudioEngine.playLevelComplete();
    notifyAndroid('haptic', {type: 'success'});
    const gap = 4;
    const cellSize = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--cell-size'));
    const px = 14 + lv.targetX * (cellSize + gap);
    const py = 14 + lv.targetY * (cellSize + gap);
    spawnParticles(px, py);
    const usedCmds = state.queue.length;
    let stars = 1;
    if (usedCmds <= lv.stars[0]) stars = 3;
    else if (usedCmds <= lv.stars[1]) stars = 2;

    playerEl.classList.add('success');
    const isLastLevel = state.levelIdx >= levels.length - 1;
    setTimeout(function() {
      playerEl.classList.remove('success');
      if (isLastLevel) {
        showAllComplete();
      } else {
        showWinOverlay(stars);
      }
    }, 500);

    checkAchievements(stars, usedCmds);

    const prev = state.progress[state.levelIdx];
    if (!prev || prev.stars < stars) {
      state.progress[state.levelIdx] = {
        completed: true, stars: stars,
        commandsUsed: usedCmds,
        attempts: state.attempts,
        timeSeconds: Math.round((Date.now() - state.startTime) / 1000)
      };
    }

    console.info('[Game] checkWin: levelComplete idx=' + state.levelIdx + ' id=' + (lv.id || (state.levelIdx + 1)));
    notifyAndroid('levelComplete', {
      levelId: lv.id || (state.levelIdx + 1),
      stars: stars,
      commandsUsed: usedCmds,
      attempts: state.attempts,
      timeSeconds: Math.round((Date.now() - state.startTime) / 1000)
    });
    saveGameState();
  } else {
    $('overlayTitle').textContent = t('failTitle');
    $('overlayStars').textContent = '';
    $('overlayMsg').textContent = posOk && !valOk
      ? t('failValueMsg', {playerVal: state.playerVal, targetVal: (lv.targetVal != null ? lv.targetVal : (lv.ops && lv.ops.length > 0 ? lv.startVal : null))})
      : t('failPosMsg');
    $('btnNext').style.display = 'none';
    overlay.classList.add('active');
    saveGameState();
  }

  state.hintMode = false;
  state.running = false;
  $('btnRun').disabled = false;
}

function checkAchievements(stars, usedCmds) {
  const timeSeconds = Math.round((Date.now() - state.startTime) / 1000);

  unlockAchievement('first_win');
  if (stars === 3) unlockAchievement('perfect_3');
  if (timeSeconds <= 30) unlockAchievement('speedster');
  if (state.attempts === 1) unlockAchievement('no_mistake');

  var completedCount = 0;
  for (var k in state.progress) {
    if (state.progress[k].completed) completedCount++;
  }
  if (completedCount >= 10) unlockAchievement('ten_levels');
}
