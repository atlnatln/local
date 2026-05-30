function updateWallVisuals(activeWalls) {
  var cells = gridEl.querySelectorAll('.cell.toggle-wall');
  cells.forEach(function(cell) {
    var key = cell.dataset.x + ',' + cell.dataset.y;
    if (activeWalls.has(key)) {
      cell.classList.remove('wall');
    } else {
      cell.classList.add('wall');
    }
  });
}
function buildGrid(lv) {
  gridEl.innerHTML = '';
  gridEl.style.gridTemplateColumns = 'repeat(' + lv.cols + ', var(--cell-size))';

  const wallMap = buildWallMap(lv);
  const opMap = {};
  (lv.ops || []).forEach(function(o) { opMap[o.x + ',' + o.y] = o; });
  const lockMap = {};
  (lv.locks || []).forEach(function(l) { lockMap[l.x + ',' + l.y] = l; });
  const teleportMap = {};
  (lv.teleports || []).forEach(function(t) { teleportMap[t.x + ',' + t.y] = t; });
  const restartSet = new Set();
  (lv.restarts || []).forEach(function(r) { restartSet.add(r.x + ',' + r.y); });
  const switchMap = {};
  (lv.toggleSwitches || []).forEach(function(s) { switchMap[s.x + ',' + s.y] = s; });
  const toggleWallSet = new Set();
  (lv.toggleSwitches || []).forEach(function(s) {
    (s.toggleWalls || []).forEach(function(tw) { toggleWallSet.add(tw[0] + ',' + tw[1]); });
  });

  for (let r = 0; r < lv.rows; r++) {
    for (let c = 0; c < lv.cols; c++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.x = c;
      cell.dataset.y = r;
      const key = c + ',' + r;

      if (wallMap[key]) {
        const w = wallMap[key];
        cell.classList.add('wall');
        if (toggleWallSet.has(key)) cell.classList.add('toggle-wall');
        if (w.type === 'directional') {
          cell.classList.add('wall-directional');
          cell.textContent = w.blocks.map(function(b) {
            return {N:'↑', S:'↓', E:'→', W:'←'}[b] || '';
          }).join('');
        }
      } else if (c === lv.targetX && r === lv.targetY) {
        cell.classList.add('target');
        // BUG FIX fallback: show effective target value when ops exist but targetVal is null
        const effectiveTargetVal = lv.targetVal != null
          ? lv.targetVal
          : (lv.ops && lv.ops.length > 0 ? lv.startVal : null);
        if (effectiveTargetVal != null) {
          const tv = document.createElement('span');
          tv.className = 'target-value';
          tv.textContent = '= ' + effectiveTargetVal;
          cell.appendChild(tv);
        }
        cell.innerHTML = '🎯' + cell.innerHTML;
      } else if (opMap[key]) {
        const op = opMap[key];
        if (op.type === '+') { cell.classList.add('op-plus'); cell.textContent = '+' + op.val; }
        else if (op.type === '-') { cell.classList.add('op-minus'); cell.textContent = '-' + op.val; }
        else if (op.type === '×' || op.type === '*') { cell.classList.add('op-times'); cell.textContent = '×' + op.val; }
        else if (op.type === '/') { cell.classList.add('op-divide'); cell.textContent = '÷' + op.val; }
        else if (op.type === '^') { cell.classList.add('op-square'); cell.textContent = '^' + op.val; }
      } else if (lockMap[key]) {
        const lock = lockMap[key];
        cell.classList.add('lock');
        cell.textContent = '🔒' + lock.requiredVal;
      } else if (teleportMap[key]) {
        cell.classList.add('teleport');
        cell.textContent = '🌀';
      } else if (restartSet.has(key)) {
        cell.classList.add('restart');
        cell.textContent = '↺';
      } else if (switchMap[key]) {
        cell.classList.add('switch');
        cell.textContent = '🔘';
      } else {
        cell.classList.add('empty');
      }
      gridEl.appendChild(cell);
    }
  }
}
function updateGhostPreview() {
  document.querySelectorAll('.cell.ghost').forEach(function(c) { c.classList.remove('ghost'); });
  const lv = getLevel();
  if (!lv) return;
  let gx = lv.startX, gy = lv.startY;
  for (var i = 0; i < state.queue.length; i++) {
    const cmdId = state.queue[i];
    const cmd = CMDS[cmdId];
    if (cmd.dz !== 0) continue;
    const nx = gx + cmd.dx, ny = gy + cmd.dy;
    if (nx < 0 || nx >= lv.cols || ny < 0 || ny >= lv.rows) break;
    var blocked = false;
    for (var j = 0; j < (lv.walls || []).length; j++) {
      var w = lv.walls[j];
      var wx = Array.isArray(w) ? w[0] : w.x;
      var wy = Array.isArray(w) ? w[1] : w.y;
      if (wx === nx && wy === ny) { blocked = true; break; }
    }
    if (blocked) break;
    gx = nx; gy = ny;
  }
  const cell = document.querySelector('.cell[data-x="' + gx + '"][data-y="' + gy + '"]');
  if (cell) cell.classList.add('ghost');
}

function updatePlayerPos(animate) {
  const gap = 4;
  const cellSize = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--cell-size'));
  const left = 14 + state.playerX * (cellSize + gap);
  const top = 14 + state.playerY * (cellSize + gap);

  playerEl.style.left = left + 'px';
  playerEl.style.top = top + 'px';
  playerEl.textContent = state.playerVal;

  if (animate) {
    playerEl.classList.remove('bump');
    void playerEl.offsetWidth;
    playerEl.classList.add('bump');
  }
}
