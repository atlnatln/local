/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Hint Engine (BFS Solver)
   ═══════════════════════════════════════════════════════════ */

import { CMDS } from './state.js';

const VAL_MIN = -500;
const VAL_MAX = 5000;

export function solveLevel(level) {
  const startKey = `${level.startX},${level.startY},${level.startVal}`;
  const queue = [{ x: level.startX, y: level.startY, value: level.startVal, path: [] }];
  const visited = new Set([startKey]);

  const wallSet = new Set(level.walls.map(w => `${w[0]},${w[1]}`));
  const opMap = {};
  level.ops.forEach(o => { opMap[`${o.x},${o.y}`] = o; });
  const lockMap = {};
  (level.locks || []).forEach(l => { lockMap[`${l.x},${l.y}`] = l; });
  const teleportMap = {};
  (level.teleports || []).forEach(t => { teleportMap[`${t.x},${t.y}`] = t; });
  const restartSet = new Set((level.restarts || []).map(r => `${r.x},${r.y}`));

  function isGoal(x, y, val) {
    if (x !== level.targetX || y !== level.targetY) return false;
    if (level.targetVal != null && val !== level.targetVal) return false;
    return true;
  }

  let head = 0;
  while (head < queue.length) {
    const s = queue[head++];
    if (s.path.length >= level.maxCmds) continue;

    for (const cmdKey of level.commands) {
      const cmd = CMDS[cmdKey];
      if (!cmd) continue;

      let nx = s.x, ny = s.y, nval = s.value;

      if (cmd.dz !== 0) {
        nval = s.value + cmd.dz;
        if (nval < VAL_MIN || nval > VAL_MAX) continue;
        const key = `${s.x},${s.y},${nval}`;
        const newPath = s.path.concat(cmdKey);
        if (isGoal(s.x, s.y, nval)) return newPath;
        if (!visited.has(key)) {
          visited.add(key);
          queue.push({ x: s.x, y: s.y, value: nval, path: newPath });
        }
        continue;
      }

      nx = s.x + cmd.dx;
      ny = s.y + cmd.dy;

      if (nx < 0 || nx >= level.cols || ny < 0 || ny >= level.rows) continue;
      if (wallSet.has(`${nx},${ny}`)) continue;
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

      const key = `${nx},${ny},${nval}`;
      const newPath = s.path.concat(cmdKey);
      if (isGoal(nx, ny, nval)) return newPath;
      if (!visited.has(key)) {
        visited.add(key);
        queue.push({ x: nx, y: ny, value: nval, path: newPath });
      }
    }
  }

  return null;
}
