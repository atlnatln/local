/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Hint Engine (BFS Solver)
   ═══════════════════════════════════════════════════════════ */

const VAL_MIN = -500;
const VAL_MAX = 5000;

const _CMDS = {
  'x+': { dx: 1, dy: 0, dz: 0 },
  'x-': { dx: -1, dy: 0, dz: 0 },
  'y-': { dx: 0, dy: -1, dz: 0 },
  'y+': { dx: 0, dy: 1, dz: 0 },
  'z+': { dx: 0, dy: 0, dz: 1 },
  'z-': { dx: 0, dy: 0, dz: -1 },
};

function _makeWallKey(x, y) { return `${x},${y}`; }
function _makeActiveWallsKey(activeWalls) {
  if (!activeWalls || activeWalls.size === 0) return '';
  return Array.from(activeWalls).sort().join(';');
}

export function solveLevel(level) {
  const wallMap = new Map();
  level.walls.forEach(w => {
    if (Array.isArray(w)) {
      wallMap.set(`${w[0]},${w[1]}`, { type: 'full' });
    } else {
      wallMap.set(`${w.x},${w.y}`, w);
    }
  });
  const opMap = {};
  level.ops.forEach(o => { opMap[`${o.x},${o.y}`] = o; });
  const lockMap = {};
  (level.locks || []).forEach(l => { lockMap[`${l.x},${l.y}`] = l; });
  const teleportMap = {};
  (level.teleports || []).forEach(t => { teleportMap[`${t.x},${t.y}`] = t; });
  const restartSet = new Set((level.restarts || []).map(r => `${r.x},${r.y}`));
  const switchMap = {};
  (level.toggleSwitches || []).forEach(s => { switchMap[`${s.x},${s.y}`] = s; });

  function isBlocked(nx, ny, cmd, activeWalls) {
    const posKey = _makeWallKey(nx, ny);
    const wall = wallMap.get(posKey);
    if (!wall) return false;
    // Toggle-activated walls are OPENED (non-blocking)
    if (activeWalls && activeWalls.has(posKey)) return false;
    if (wall.type === 'directional') {
      const dirMap = { '1,0': 'E', '-1,0': 'W', '0,1': 'S', '0,-1': 'N' };
      const dir = dirMap[`${cmd.dx},${cmd.dy}`];
      return !!(dir && wall.blocks.includes(dir));
    }
    return true;
  }

  function isGoal(x, y, val) {
    if (x !== level.targetX || y !== level.targetY) return false;
    if (level.targetVal != null && val !== level.targetVal) return false;
    return true;
  }

  const startActive = new Set();
  const startKey = `${level.startX},${level.startY},${level.startVal},${_makeActiveWallsKey(startActive)}`;
  const queue = [{ x: level.startX, y: level.startY, value: level.startVal, path: [], activeWalls: startActive }];
  const visited = new Set([startKey]);

  let head = 0;
  while (head < queue.length) {
    const s = queue[head++];
    if (s.path.length >= level.maxCmds) continue;

    for (const cmdKey of level.commands) {
      const cmd = _CMDS[cmdKey];
      if (!cmd) continue;

      let nx = s.x, ny = s.y, nval = s.value;
      let nextActiveWalls = s.activeWalls;

      if (cmd.dz !== 0) {
        nval = s.value + cmd.dz;
        if (nval < VAL_MIN || nval > VAL_MAX) continue;
        const key = `${s.x},${s.y},${nval},${_makeActiveWallsKey(s.activeWalls)}`;
        const newPath = s.path.concat(cmdKey);
        if (isGoal(s.x, s.y, nval)) return newPath;
        if (!visited.has(key)) {
          visited.add(key);
          queue.push({ x: s.x, y: s.y, value: nval, path: newPath, activeWalls: s.activeWalls });
        }
        continue;
      }

      nx = s.x + cmd.dx;
      ny = s.y + cmd.dy;

      if (nx < 0 || nx >= level.cols || ny < 0 || ny >= level.rows) continue;
      if (isBlocked(nx, ny, cmd, s.activeWalls)) continue;

      const lock = lockMap[`${nx},${ny}`];
      if (lock && s.value !== lock.requiredVal) continue;

      nval = s.value;
      const op = opMap[`${nx},${ny}`];
      if (op) {
        if (op.type === '+') nval += op.val;
        else if (op.type === '-') nval -= op.val;
        else if (op.type === '×') nval *= op.val;
        else if (op.type === '/') {
          if (nval % op.val !== 0) continue;
          nval = Math.floor(nval / op.val);
        } else if (op.type === '^') nval *= nval;
      }

      if (nval < VAL_MIN || nval > VAL_MAX) continue;

      if (restartSet.has(`${nx},${ny}`)) {
        nval = level.startVal;
      }

      const teleport = teleportMap[`${nx},${ny}`];
      if (teleport) {
        nx = teleport.targetX;
        ny = teleport.targetY;
      }

      // Toggle switch: activate on step
      const sw = switchMap[`${nx},${ny}`];
      if (sw) {
        nextActiveWalls = new Set(s.activeWalls);
        (sw.toggleWalls || []).forEach(([wx, wy]) => {
          const wk = _makeWallKey(wx, wy);
          if (nextActiveWalls.has(wk)) nextActiveWalls.delete(wk);
          else nextActiveWalls.add(wk);
        });
      }

      const key = `${nx},${ny},${nval},${_makeActiveWallsKey(nextActiveWalls)}`;
      const newPath = s.path.concat(cmdKey);
      if (isGoal(nx, ny, nval)) return newPath;
      if (!visited.has(key)) {
        visited.add(key);
        queue.push({ x: nx, y: ny, value: nval, path: newPath, activeWalls: nextActiveWalls });
      }
    }
  }

  return null;
}
