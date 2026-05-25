/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Level Editor
   ═══════════════════════════════════════════════════════════ */

import { solveLevel } from './hint-engine.js';
import { deepClone } from './utils.js';

/* ── State ──────────────────────────────────────────────── */
let cols = 5;
let rows = 5;
let startVal = 1;
let targetVal = null;
let maxCmds = 10;
let selectedTool = 'start';
let grid = []; // 2D array of {type, data}
let startPos = { x: 0, y: 0 };
let targetPos = { x: 2, y: 2 };
let availableCommands = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'];

/* ── DOM refs ───────────────────────────────────────────── */
const $ = (id) => document.getElementById(id);

/* ── Init ───────────────────────────────────────────────── */
function initGrid() {
  grid = [];
  for (let y = 0; y < rows; y++) {
    const row = [];
    for (let x = 0; x < cols; x++) {
      row.push({ type: 'empty', data: null });
    }
    grid.push(row);
  }
  startPos = { x: 0, y: 0 };
  targetPos = { x: Math.min(2, cols - 1), y: Math.min(2, rows - 1) };
  grid[startPos.y][startPos.x] = { type: 'start', data: null };
  grid[targetPos.y][targetPos.x] = { type: 'target', data: null };
}

function renderGrid() {
  const el = $('editorGrid');
  el.innerHTML = '';
  const cellSize = Math.min(48, Math.max(32, Math.floor(320 / Math.max(cols, rows))));
  el.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const cell = document.createElement('div');
      cell.className = 'editor-cell';
      cell.style.width = cellSize + 'px';
      cell.style.height = cellSize + 'px';
      const g = grid[y][x];
      cell.classList.add(g.type);

      switch (g.type) {
        case 'start': cell.textContent = '🚀'; break;
        case 'target': cell.textContent = '🎯'; break;
        case 'wall': cell.textContent = ''; break;
        case 'op': cell.textContent = g.data.type + g.data.val; break;
        case 'lock': cell.textContent = '🔒' + g.data.requiredVal; break;
        case 'teleport': cell.textContent = '🌀'; break;
        case 'restart': cell.textContent = '↺'; break;
        default: cell.textContent = '';
      }

      cell.addEventListener('click', () => onCellClick(x, y));
      el.appendChild(cell);
    }
  }
}

function onCellClick(x, y) {
  const current = grid[y][x];

  // Eraser
  if (selectedTool === 'eraser') {
    if (current.type === 'start') startPos = null;
    if (current.type === 'target') targetPos = null;
    grid[y][x] = { type: 'empty', data: null };
    renderGrid();
    return;
  }

  // Start and Target are singletons
  if (selectedTool === 'start') {
    if (startPos) grid[startPos.y][startPos.x] = { type: 'empty', data: null };
    if (targetPos && targetPos.x === x && targetPos.y === y) targetPos = null;
    grid[y][x] = { type: 'start', data: null };
    startPos = { x, y };
    renderGrid();
    return;
  }

  if (selectedTool === 'target') {
    if (targetPos) grid[targetPos.y][targetPos.x] = { type: 'empty', data: null };
    if (startPos && startPos.x === x && startPos.y === y) startPos = null;
    grid[y][x] = { type: 'target', data: null };
    targetPos = { x, y };
    renderGrid();
    return;
  }

  // Don't overwrite start/target
  if (current.type === 'start' || current.type === 'target') return;

  if (selectedTool === 'wall') {
    grid[y][x] = { type: 'wall', data: null };
  } else if (selectedTool === 'op') {
    const type = $('opType').value;
    const val = parseInt($('opVal').value, 10) || 1;
    grid[y][x] = { type: 'op', data: { type, val } };
  } else if (selectedTool === 'lock') {
    const requiredVal = parseInt($('lockVal').value, 10) || 5;
    grid[y][x] = { type: 'lock', data: { requiredVal } };
  } else if (selectedTool === 'teleport') {
    const targetX = parseInt($('tpX').value, 10) || 0;
    const targetY = parseInt($('tpY').value, 10) || 0;
    grid[y][x] = { type: 'teleport', data: { targetX, targetY } };
  } else if (selectedTool === 'restart') {
    grid[y][x] = { type: 'restart', data: null };
  }

  renderGrid();
}

function updateConfigPanels() {
  $('opConfig').classList.toggle('active', selectedTool === 'op');
  $('lockConfig').classList.toggle('active', selectedTool === 'lock');
  $('teleportConfig').classList.toggle('active', selectedTool === 'teleport');
}

function buildPuzzleFromEditorState() {
  const walls = [];
  const ops = [];
  const locks = [];
  const teleports = [];
  const restarts = [];

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const c = grid[y][x];
      if (c.type === 'wall') walls.push([x, y]);
      else if (c.type === 'op') ops.push({ x, y, type: c.data.type, val: c.data.val });
      else if (c.type === 'lock') locks.push({ x, y, requiredVal: c.data.requiredVal });
      else if (c.type === 'teleport') teleports.push({ x, y, targetX: c.data.targetX, targetY: c.data.targetY });
      else if (c.type === 'restart') restarts.push({ x, y });
    }
  }

  const tvInput = $('targetValInput').value;
  const tv = tvInput === '' ? null : parseInt(tvInput, 10);

  return {
    title: 'Özel Seviye',
    desc: 'Editörden oluşturuldu',
    cols,
    rows,
    startX: startPos ? startPos.x : 0,
    startY: startPos ? startPos.y : 0,
    startVal: parseInt($('startVal').value, 10) || 1,
    targetX: targetPos ? targetPos.x : 0,
    targetY: targetPos ? targetPos.y : 0,
    targetVal: tv,
    walls,
    ops,
    locks,
    teleports,
    restarts,
    commands: availableCommands,
    maxCmds: parseInt($('maxCmds').value, 10) || 10,
    stars: [3, 5],
  };
}

/* ── Tool selection ─────────────────────────────────────── */
document.querySelectorAll('.tool-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedTool = btn.dataset.tool;
    updateConfigPanels();
  });
});

/* ── Grid size inputs ───────────────────────────────────── */
function resizeGrid() {
  const newCols = Math.max(1, Math.min(10, parseInt($('gridCols').value, 10) || 5));
  const newRows = Math.max(1, Math.min(10, parseInt($('gridRows').value, 10) || 5));

  const newGrid = [];
  for (let y = 0; y < newRows; y++) {
    const row = [];
    for (let x = 0; x < newCols; x++) {
      if (y < rows && x < cols) {
        row.push(grid[y][x]);
      } else {
        row.push({ type: 'empty', data: null });
      }
    }
    newGrid.push(row);
  }

  // Ensure start/target still exist
  let hasStart = false, hasTarget = false;
  for (let y = 0; y < newRows; y++) {
    for (let x = 0; x < newCols; x++) {
      if (newGrid[y][x].type === 'start') { hasStart = true; startPos = { x, y }; }
      if (newGrid[y][x].type === 'target') { hasTarget = true; targetPos = { x, y }; }
    }
  }
  if (!hasStart) {
    newGrid[0][0] = { type: 'start', data: null };
    startPos = { x: 0, y: 0 };
  }
  if (!hasTarget) {
    const tx = Math.min(2, newCols - 1);
    const ty = Math.min(2, newRows - 1);
    if (newGrid[ty][tx].type !== 'start') {
      newGrid[ty][tx] = { type: 'target', data: null };
      targetPos = { x: tx, y: ty };
    } else {
      const alt = newCols > 1 ? 1 : 0;
      newGrid[0][alt] = { type: 'target', data: null };
      targetPos = { x: alt, y: 0 };
    }
  }

  cols = newCols;
  rows = newRows;
  grid = newGrid;
  renderGrid();
}

$('gridCols').addEventListener('change', resizeGrid);
$('gridRows').addEventListener('change', resizeGrid);

/* ── Actions ────────────────────────────────────────────── */
$('btnTest').addEventListener('click', () => {
  const puzzle = buildPuzzleFromEditorState();
  const sol = solveLevel(puzzle);
  if (!sol) {
    alert('⚠️ Bu seviye çözülemez! Lütfen duvarları ve hedefi kontrol et.');
    return;
  }

  if ('BroadcastChannel' in window) {
    const bc = new BroadcastChannel('sayi-yolculugu-editor');
    bc.postMessage({ type: 'LOAD_TEST_LEVEL', puzzle });
    window.open('index.html', '_blank');
  } else {
    // Fallback for browsers without BroadcastChannel
    localStorage.setItem('editor_test_level', JSON.stringify(puzzle));
    window.open('index.html?editor=1', '_blank');
  }
});

$('btnExport').addEventListener('click', () => {
  const puzzle = buildPuzzleFromEditorState();
  $('jsonOutput').value = JSON.stringify(puzzle, null, 2);
});

$('btnImport').addEventListener('click', () => {
  try {
    const puzzle = JSON.parse($('jsonOutput').value);
    if (!puzzle.cols || !puzzle.rows) throw new Error('Geçersiz puzzle');

    cols = Math.max(1, Math.min(10, puzzle.cols));
    rows = Math.max(1, Math.min(10, puzzle.rows));
    $('gridCols').value = cols;
    $('gridRows').value = rows;
    startVal = puzzle.startVal ?? 1;
    $('startVal').value = startVal;
    targetVal = puzzle.targetVal ?? null;
    $('targetValInput').value = targetVal !== null ? targetVal : '';
    maxCmds = puzzle.maxCmds || 10;
    $('maxCmds').value = maxCmds;
    availableCommands = puzzle.commands || ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'];

    initGrid();
    startPos = null;
    targetPos = null;

    // Apply walls
    (puzzle.walls || []).forEach(([x, y]) => {
      if (x < cols && y < rows) grid[y][x] = { type: 'wall', data: null };
    });
    // Apply ops
    (puzzle.ops || []).forEach(o => {
      if (o.x < cols && o.y < rows) grid[o.y][o.x] = { type: 'op', data: { type: o.type, val: o.val } };
    });
    // Apply locks
    (puzzle.locks || []).forEach(l => {
      if (l.x < cols && l.y < rows) grid[l.y][l.x] = { type: 'lock', data: { requiredVal: l.requiredVal } };
    });
    // Apply teleports
    (puzzle.teleports || []).forEach(t => {
      if (t.x < cols && t.y < rows) grid[t.y][t.x] = { type: 'teleport', data: { targetX: t.targetX, targetY: t.targetY } };
    });
    // Apply restarts
    (puzzle.restarts || []).forEach(r => {
      if (r.x < cols && r.y < rows) grid[r.y][r.x] = { type: 'restart', data: null };
    });

    // Apply start/target
    if (puzzle.startX < cols && puzzle.startY < rows) {
      grid[puzzle.startY][puzzle.startX] = { type: 'start', data: null };
      startPos = { x: puzzle.startX, y: puzzle.startY };
    }
    if (puzzle.targetX < cols && puzzle.targetY < rows) {
      grid[puzzle.targetY][puzzle.targetX] = { type: 'target', data: null };
      targetPos = { x: puzzle.targetX, y: puzzle.targetY };
    }

    if (!startPos) {
      grid[0][0] = { type: 'start', data: null };
      startPos = { x: 0, y: 0 };
    }
    if (!targetPos) {
      const tx = Math.min(2, cols - 1);
      const ty = Math.min(2, rows - 1);
      if (!(tx === startPos.x && ty === startPos.y)) {
        grid[ty][tx] = { type: 'target', data: null };
        targetPos = { x: tx, y: ty };
      } else {
        const alt = cols > 1 ? 1 : 0;
        grid[0][alt] = { type: 'target', data: null };
        targetPos = { x: alt, y: 0 };
      }
    }

    renderGrid();
    alert('✅ Puzzle başarıyla yüklendi!');
  } catch (e) {
    alert('❌ JSON parse hatası: ' + e.message);
  }
});

/* ── Bootstrap ──────────────────────────────────────────── */
initGrid();
renderGrid();
updateConfigPanels();
