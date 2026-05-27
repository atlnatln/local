#!/usr/bin/env python3
"""
Procedural seviye üretim & kapsamlı validate testi.

Oyunun tüm mekaniklerini kapsar:
- Temel yapı (grid, koordinatlar, zorluk)
- BFS çözülebilirlik
- Bölme bounce, kare patlaması, clamp
- Duvarlar (directional, toggle, full)
- Lock, teleport, restart, switch
- Solution / hintCommands tutarlılığı
- Komut paleti ve star rating mantığı

Kullanım:
    # Yeni seviye üret ve test et
    cd /home/akn/local/projects/sayi-yolculugu
    PYTHONPATH=../mathlock-play python3 scripts/test-level-generation.py --count 1000

    # Mevcut JSON dosyasını test et
    PYTHONPATH=../mathlock-play python3 scripts/test-level-generation.py \
        --input ../mathlock-play/generated-levels/levels_10000_v4.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# procedural_levels mathlock-play altında
_MATHLOCK_PLAY = Path(__file__).resolve().parents[2] / "mathlock-play"
sys.path.insert(0, str(_MATHLOCK_PLAY))

from procedural_levels.core.rng import Rng
from procedural_levels.generator.pipeline import generate_level, generate_set
from procedural_levels.generator.fingerprint import compute_fingerprint, fingerprint_to_str
from procedural_levels.solver.bfs import bfs_solve, MIN_VAL, MAX_VAL
from procedural_levels.core.types import Level, Theme, Wall, WallType, Command, OpType


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS (mirror live backend logic)
# ═══════════════════════════════════════════════════════════════════════════

def _summarize_mechanics(level: dict) -> str:
    """Generate a short mechanic fingerprint for duplicate detection.
    Mirrors backend/credits/views.py::_summarize_mechanics exactly."""
    fp = level.get('fingerprint')
    if isinstance(fp, dict):
        return (
            f"grid={fp.get('grid', '?x?')}|"
            f"pathShape={fp.get('pathShape', '?')}|"
            f"branching={fp.get('branching', '?')}|"
            f"wallTopology={fp.get('wallTopology', '?')}|"
            f"valuePlanning={fp.get('valuePlanning', '?')}|"
            f"ops={fp.get('ops', '?')}"
        )
    cmds = ','.join(sorted(level.get('commands', [])))
    has_ops = 'yes' if level.get('ops') else 'no'
    has_walls = 'yes' if level.get('walls') else 'no'
    has_target_val = 'yes' if level.get('targetVal') is not None else 'no'
    grid = f"{level.get('cols', 0)}x{level.get('rows', 0)}"
    return f"cmds={cmds}|ops={has_ops}|walls={has_walls}|targetVal={has_target_val}|grid={grid}"


def build_child_stats_for_test(
    education_period: str,
    previous_sets: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Build a child_stats dict that mirrors _build_level_stats from views.py.

    previous_sets: list of LevelSet.to_dict() outputs from previous generations.
    """
    stats: Dict[str, Any] = {
        'childName': 'Test Çocuk',
        'educationPeriod': education_period,
        'questionAccuracy': 0.75,
        'currentDifficulty': 2,
    }

    if previous_sets:
        latest = previous_sets[-1]
        levels = latest.get('levels', [])
        diffs = [lv.get('difficulty', 1) for lv in levels]

        stats['lastSetEndDifficulty'] = levels[-1].get('difficulty', 1) if levels else 1
        stats['lastSetMaxDifficulty'] = max(diffs) if diffs else 1
        stats['lastSetAvgDifficulty'] = round(sum(diffs) / len(diffs), 1) if diffs else 1.0
        completed_count = int(len(levels) * 0.8)
        stats['completionRate'] = round(completed_count / len(levels), 2) if levels else 0.0
        stats['lastSetCompletionRate'] = stats['completionRate']
        stats['totalCompleted'] = completed_count
        stats['totalLevels'] = len(levels)
        stats['lastVersion'] = latest.get('version', 0)

        stats['previousSets'] = []
        for s in previous_sets[-2:]:
            pls = s.get('levels', [])
            stats['previousSets'].append({
                'version': s.get('version', 0),
                'titles': [lv.get('title', '') for lv in pls],
                'mechanics': [_summarize_mechanics(lv) for lv in pls],
            })

    return stats


# ═══════════════════════════════════════════════════════════════════════════
#  REPORTING
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationReport:
    level_id: int
    errors: List[str]
    warnings: List[str]
    mechanics: List[str]
    difficulty: int


# ═══════════════════════════════════════════════════════════════════════════
#  JSON -> LEVEL
# ═══════════════════════════════════════════════════════════════════════════

def _json_to_theme(d: Dict[str, Any]) -> Theme:
    return Theme(
        name=d.get("name", "default"),
        bg_color=d.get("bgColor", "#0f0f1a"),
        wall_color=d.get("wallColor", "#2a2a40"),
        player_color=d.get("playerColor", "#e94560"),
        target_color=d.get("targetColor", "#00d68f"),
        op_colors=d.get("opColors", {}),
    )


def dict_to_level(d: Dict[str, Any]) -> Level:
    """Convert a JSON level dict (from to_dict) back to a Level object."""
    walls = []
    for w in d.get("walls", []):
        if isinstance(w, list):
            walls.append(Wall.from_legacy(w))
        else:
            walls.append(Wall.from_dict(w))

    theme = _json_to_theme(d.get("theme", {}))

    return Level(
        id=d["id"],
        title=d.get("title", ""),
        description=d.get("desc", ""),
        difficulty=d.get("difficulty", 1),
        rows=d.get("rows", 1),
        cols=d.get("cols", 1),
        startX=d.get("startX", 0),
        startY=d.get("startY", 0),
        startVal=d.get("startVal", 0),
        targetX=d.get("targetX", 0),
        targetY=d.get("targetY", 0),
        targetVal=d.get("targetVal"),
        maxCmds=d.get("maxCmds", 10),
        stars=d.get("stars", [1, 2]),
        commands=d.get("commands", []),
        walls=walls,
        ops=d.get("ops", []),
        locks=d.get("locks", []),
        teleports=d.get("teleports", []),
        restarts=d.get("restarts", []),
        switches=d.get("toggleSwitches", []),
        theme=theme,
        ascii_map=d.get("asciiMap", ""),
        fingerprint=d.get("fingerprint", {}),
        legendary=d.get("legendary", False),
        solution=d.get("solution"),
    )


# ═══════════════════════════════════════════════════════════════════════════
#  STEP-BY-STEP SIMULATION (cross-check with BFS logic)
# ═══════════════════════════════════════════════════════════════════════════

def simulate_solution(level: Level, solution: List[str]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Simulate the given command sequence step-by-step.
    Returns (ok, error_msg, final_state).
    Mirrors the JS execution engine + Python BFS semantics.
    """
    cols, rows = level.cols, level.rows
    x, y = level.startX, level.startY
    val = level.startVal

    # Lookup structures
    wall_map = {(w.x, w.y): w for w in level.walls}
    op_map = {(o["x"], o["y"]): o for o in level.ops}
    lock_map = {(lk["x"], lk["y"]): lk for lk in level.locks}
    restart_set = {(r["x"], r["y"]) for r in level.restarts}
    teleport_map = {(t["x"], t["y"]): (t.get("targetX", 0), t.get("targetY", 0)) for t in level.teleports}
    switch_map = {}
    switch_targets = {}
    for sw in level.switches:
        sp = (sw["x"], sw["y"])
        switch_map[sp] = sw
        switch_targets[sp] = {(tw[0], tw[1]) for tw in sw.get("toggleWalls", [])}

    # Command name -> Command enum
    _LEGACY = {"x+": Command.XP, "x-": Command.XM, "y+": Command.YP, "y-": Command.YM, "z+": Command.ZP, "z-": Command.ZM}
    cmd_lookup = {c.name: c for c in Command}
    cmd_objs = []
    for c in solution:
        cmd = cmd_lookup.get(c) or _LEGACY.get(c, Command.XP)
        cmd_objs.append(cmd)

    active_walls = set()
    unlocked = set()
    activated_switches = set()

    for step_idx, cmd in enumerate(cmd_objs):
        # Z-command: only value change
        if cmd.dz != 0:
            val += cmd.dz
            if val < MIN_VAL or val > MAX_VAL:
                return False, f"step {step_idx}: value clamp exceeded ({val})", {}
            continue

        nx, ny = x + cmd.dx, y + cmd.dy

        # Bounds
        if not (0 <= nx < cols and 0 <= ny < rows):
            return False, f"step {step_idx}: out of bounds ({nx},{ny})", {}

        # Wall check (with toggle switch state)
        pos = (nx, ny)
        opened = set()
        for sw_pos in activated_switches:
            opened.update(switch_targets.get(sw_pos, set()))

        if pos in wall_map and pos not in opened:
            w = wall_map[pos]
            if w.blocks_movement(cmd.dx, cmd.dy):
                return False, f"step {step_idx}: blocked by wall at {pos}", {}

        # Lock check
        if pos in lock_map and pos not in unlocked:
            lk = lock_map[pos]
            req = lk.get("requiredVal", lk.get("required_val", 0))
            if val != req:
                return False, f"step {step_idx}: lock at {pos} requires {req}, have {val}", {}
            unlocked.add(pos)

        # Switch activation
        if pos in switch_map and pos not in activated_switches:
            activated_switches.add(pos)

        # Move
        x, y = nx, ny

        # Operator apply
        if pos in op_map:
            o = op_map[pos]
            ot = OpType(o["type"])
            ov = o["val"]
            if ot == OpType.PLUS:
                val += ov
            elif ot == OpType.MINUS:
                val -= ov
            elif ot == OpType.MULTIPLY:
                val *= ov
            elif ot == OpType.DIVIDE:
                if ov == 0:
                    return False, f"step {step_idx}: divide by zero", {}
                if val % ov != 0:
                    return False, f"step {step_idx}: division bounce ({val}/{ov})", {}
                val = val // ov
            elif ot == OpType.SQUARE:
                val = val * val

            if val < MIN_VAL or val > MAX_VAL:
                return False, f"step {step_idx}: value clamp after op ({val})", {}

        # Restart
        if pos in restart_set:
            val = level.startVal

        # Teleport
        if pos in teleport_map:
            x, y = teleport_map[pos]

    # Final win check
    pos_ok = x == level.targetX and y == level.targetY
    val_ok = level.targetVal is None or val == level.targetVal
    if not pos_ok:
        return False, f"final position mismatch: ({x},{y}) vs target ({level.targetX},{level.targetY})", {}
    if not val_ok:
        return False, f"final value mismatch: {val} vs target {level.targetVal}", {}

    return True, "", {"final_x": x, "final_y": y, "final_val": val}


# ═══════════════════════════════════════════════════════════════════════════
#  COMPREHENSIVE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_level_comprehensive(level: Level, lv_dict: Dict[str, Any]) -> ValidationReport:
    """Run all validation rules on a single level."""
    errors: List[str] = []
    warnings: List[str] = []
    mechanics: List[str] = []
    rows, cols = level.rows, level.cols

    # ── 1. Required fields ──────────────────────────────────────────
    required = ["id", "title", "rows", "cols", "startX", "startY", "startVal",
                "targetX", "targetY", "maxCmds", "stars", "commands"]
    for f in required:
        if f not in lv_dict:
            errors.append(f"missing required field: {f}")

    # ── 2. Grid bounds for all entities ─────────────────────────────
    def _in_bounds(px, py, name):
        if not (0 <= px < cols and 0 <= py < rows):
            errors.append(f"{name} out of bounds: ({px},{py}) vs {cols}x{rows}")

    _in_bounds(level.startX, level.startY, "start")
    _in_bounds(level.targetX, level.targetY, "target")

    for w in level.walls:
        _in_bounds(w.x, w.y, f"wall@{w.x},{w.y}")
        if w.type == WallType.DIRECTIONAL and w.blocks:
            invalid = set(d.name for d in w.blocks) - {"N", "S", "E", "W"}
            if invalid:
                errors.append(f"directional wall invalid blocks: {invalid}")

    for o in level.ops:
        _in_bounds(o["x"], o["y"], f"op@{o['x']},{o['y']}")
        if o.get("type") not in {"+", "-", "*", "×", "/", "^"}:
            errors.append(f"invalid op type: {o.get('type')}")

    for lk in level.locks:
        _in_bounds(lk["x"], lk["y"], f"lock@{lk['x']},{lk['y']}")
        if lk.get("requiredVal") is None:
            errors.append("lock missing requiredVal")

    for tp in level.teleports:
        _in_bounds(tp["x"], tp["y"], f"teleport_src")
        tx, ty = tp.get("targetX", 0), tp.get("targetY", 0)
        _in_bounds(tx, ty, f"teleport_target")
        if (tp["x"], tp["y"]) == (tx, ty):
            warnings.append("teleport src == target (pointless)")

    for sw in level.switches:
        _in_bounds(sw["x"], sw["y"], f"switch")
        for tw in sw.get("toggleWalls", []):
            _in_bounds(tw[0], tw[1], f"toggleWall")

    for r in level.restarts:
        _in_bounds(r["x"], r["y"], f"restart")

    # ── 3. Solution & solvability ───────────────────────────────────
    sol = lv_dict.get("solution")
    hint = lv_dict.get("hintCommands")

    if sol:
        if hint and sol != hint:
            warnings.append("hintCommands != solution (may be intentional)")

        # maxCmds check
        if len(sol) > level.maxCmds:
            errors.append(f"solution len({len(sol)}) > maxCmds({level.maxCmds})")

        # Commands palette contains all solution commands
        palette = set(lv_dict.get("commands", []))
        for cmd in sol:
            if cmd not in palette:
                errors.append(f"solution uses cmd '{cmd}' not in palette {palette}")
                break

        # Star sanity
        stars = level.stars
        if len(stars) != 2:
            errors.append(f"stars must have 2 elements, got {len(stars)}")
        else:
            if not (stars[0] <= stars[1] <= level.maxCmds):
                errors.append(f"stars order invalid: {stars} vs maxCmds={level.maxCmds}")
            if len(sol) > stars[1]:
                warnings.append(f"solution len({len(sol)}) > 2-star threshold({stars[1]})")
            if len(sol) > stars[0]:
                warnings.append(f"solution len({len(sol)}) > 3-star threshold({stars[0]})")

        # Step-by-step simulation
        sim_ok, sim_err, _ = simulate_solution(level, sol)
        if not sim_ok:
            errors.append(f"simulation failed: {sim_err}")
    else:
        errors.append("no solution in level dict")

    # ── 4. BFS cross-check ──────────────────────────────────────────
    bfs_solvable, bfs_steps, bfs_sol, _ = bfs_solve(level)
    if not bfs_solvable:
        errors.append("BFS reports unsolvable")
    else:
        if sol and len(sol) != bfs_steps:
            warnings.append(f"dict solution len({len(sol)}) != BFS optimal({bfs_steps})")
        # Verify BFS solution by simulation too
        sim_ok2, sim_err2, _ = simulate_solution(level, bfs_sol)
        if not sim_ok2:
            errors.append(f"BFS solution simulation failed: {sim_err2}")

    # ── 5. Mechanics detection ──────────────────────────────────────
    if level.ops:
        mechanics.append("ops")
    if level.locks:
        mechanics.append("lock")
    if level.teleports:
        mechanics.append("teleport")
    if level.restarts:
        mechanics.append("restart")
    if level.switches:
        mechanics.append("switch")
    if level.walls:
        mechanics.append("wall")
    if any(w.type == WallType.DIRECTIONAL for w in level.walls):
        mechanics.append("directional_wall")
    if level.targetVal is not None:
        mechanics.append("targetVal")

    return ValidationReport(
        level_id=level.id,
        errors=errors,
        warnings=warnings,
        mechanics=mechanics,
        difficulty=level.difficulty,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_and_validate(
    count: int,
    seed: Optional[int] = None,
    use_set_mode: bool = True,
    education_period: str = "sinif_2",
) -> Tuple[List[Dict], List[ValidationReport], Dict[str, Any]]:
    """Generate *count* levels and validate each one comprehensively.

    If ``use_set_mode`` is True, uses ``generate_set`` (mirrors live Android
    backend behaviour) instead of raw ``generate_level``.

    The ``seed`` defaults to a random value (0-999999) just like the live
    backend: ``random.randint(0, 999999)``.
    """
    if seed is None:
        seed = random.randint(0, 999_999)
    rng = Rng(seed=seed)
    level_dicts: List[Dict] = []
    reports: List[ValidationReport] = []
    previous_sets: List[Dict] = []

    # Position-diversity tracking
    positions = {
        "starts": [],
        "targets": [],
        "start_target_pairs": [],
        "grids": [],
    }

    print(f"Generating {count} levels (mode={'generate_set' if use_set_mode else 'generate_level'}, period={education_period}, seed={seed})...")

    if use_set_mode:
        set_version = 1
        while len(level_dicts) < count:
            child_stats = build_child_stats_for_test(education_period, previous_sets or None)
            level_set = generate_set(version=set_version, rng=rng, child_stats=child_stats)

            # Store full set dict so next iteration can build proper child_stats
            set_dict = level_set.to_dict()
            previous_sets.append(set_dict)

            for level in level_set.levels:
                if len(level_dicts) >= count:
                    break
                lv_dict = level.to_dict()
                report = validate_level_comprehensive(level, lv_dict)
                level_dicts.append(lv_dict)
                reports.append(report)

                positions["starts"].append((level.startX, level.startY, level.cols, level.rows))
                positions["targets"].append((level.targetX, level.targetY, level.cols, level.rows))
                positions["start_target_pairs"].append(
                    (level.startX, level.startY, level.targetX, level.targetY, level.cols, level.rows)
                )
                positions["grids"].append((level.cols, level.rows))

            if len(level_dicts) % 100 == 0 or len(level_dicts) >= count:
                err_count = sum(1 for r in reports if r.errors)
                print(f"  {len(level_dicts)}/{count} done (errors so far: {err_count})")
            set_version += 1
    else:
        level_id = 1
        while len(level_dicts) < count:
            diff = rng.randint(1, 5)
            level = None
            for attempt in range(50):
                level = generate_level(level_id=level_id, difficulty=diff, rng=rng)
                if level is None:
                    continue
                solvable, _, _, _ = bfs_solve(level)
                if not solvable:
                    continue
                break
            else:
                print(f"  WARN: level {level_id} (diff={diff}) failed after 50 attempts")
                continue

            lv_dict = level.to_dict()
            report = validate_level_comprehensive(level, lv_dict)
            level_dicts.append(lv_dict)
            reports.append(report)
            level_id += 1

            positions["starts"].append((level.startX, level.startY, level.cols, level.rows))
            positions["targets"].append((level.targetX, level.targetY, level.cols, level.rows))
            positions["start_target_pairs"].append(
                (level.startX, level.startY, level.targetX, level.targetY, level.cols, level.rows)
            )
            positions["grids"].append((level.cols, level.rows))

            if len(level_dicts) % 100 == 0:
                err_count = sum(1 for r in reports if r.errors)
                print(f"  {len(level_dicts)}/{count} done (errors so far: {err_count})")

    return level_dicts, reports, positions


# ═══════════════════════════════════════════════════════════════════════════
#  VALIDATE EXISTING FILE
# ═══════════════════════════════════════════════════════════════════════════

def validate_file(path: Path) -> List[ValidationReport]:
    """Load a JSON file of levels and validate each one."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        levels = raw.get("levels", [])
    else:
        levels = raw

    print(f"Loaded {len(levels)} levels from {path}")
    reports: List[ValidationReport] = []
    for i, lv_dict in enumerate(levels):
        level = dict_to_level(lv_dict)
        report = validate_level_comprehensive(level, lv_dict)
        reports.append(report)
        if (i + 1) % 500 == 0:
            err_count = sum(1 for r in reports if r.errors)
            print(f"  Validated {i+1}/{len(levels)} (errors: {err_count})")
    return reports


# ═══════════════════════════════════════════════════════════════════════════
#  REPORTING
# ═══════════════════════════════════════════════════════════════════════════

def _print_position_diversity(positions: Dict[str, Any]) -> None:
    """Analyze start/target position diversity."""
    print("\n--- Position Diversity ---")
    grids = positions.get("grids", [])
    grid_sizes = {}
    for g in grids:
        grid_sizes[g] = grid_sizes.get(g, 0) + 1
    print("Grid size distribution:")
    for g, c in sorted(grid_sizes.items(), key=lambda x: -x[1]):
        print(f"  {g[0]}x{g[1]}: {c}")

    starts = positions.get("starts", [])
    targets = positions.get("targets", [])
    pairs = positions.get("start_target_pairs", [])

    unique_starts = set((s[0], s[1]) for s in starts)
    unique_targets = set((t[0], t[1]) for t in targets)
    unique_pairs = set((p[0], p[1], p[2], p[3]) for p in pairs)

    print(f"\nUnique start positions:     {len(unique_starts)}")
    print(f"Unique target positions:    {len(unique_targets)}")
    print(f"Unique start→target pairs:  {len(unique_pairs)}")
    print(f"Total levels:               {len(pairs)}")

    # Corner analysis
    def _is_corner(x, y, cols, rows):
        return (x == 0 or x == cols - 1) and (y == 0 or y == rows - 1)

    target_corners = sum(1 for t in targets if _is_corner(t[0], t[1], t[2], t[3]))
    print(f"Targets in corners:         {target_corners} ({target_corners/len(targets)*100:.1f}%)")

    # Center analysis (middle 2x2)
    def _is_center(x, y, cols, rows):
        return cols // 2 - 1 <= x <= cols // 2 and rows // 2 - 1 <= y <= rows // 2

    target_centers = sum(1 for t in targets if _is_center(t[0], t[1], t[2], t[3]))
    print(f"Targets in center 2x2:      {target_centers} ({target_centers/len(targets)*100:.1f}%)")


def print_report(
    reports: List[ValidationReport],
    title: str = "Report",
    positions: Optional[Dict[str, Any]] = None,
) -> int:
    total = len(reports)
    failed = [r for r in reports if r.errors]
    warned = [r for r in reports if r.warnings and not r.errors]

    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Total levels:   {total}")
    print(f"Failed:         {len(failed)} ({len(failed)/total*100:.1f}%)")
    print(f"Warnings only:  {len(warned)} ({len(warned)/total*100:.1f}%)")
    print(f"Clean:          {total - len(failed) - len(warned)}")

    # Difficulty distribution
    by_diff: Dict[int, int] = {}
    for r in reports:
        by_diff[r.difficulty] = by_diff.get(r.difficulty, 0) + 1
    print("\nDifficulty distribution:")
    for d in sorted(by_diff):
        print(f"  diff {d}: {by_diff[d]}")

    # Mechanics
    mech_counts: Dict[str, int] = {}
    for r in reports:
        for m in r.mechanics:
            mech_counts[m] = mech_counts.get(m, 0) + 1
    print("\nMechanic usage:")
    for m, c in sorted(mech_counts.items(), key=lambda x: -x[1]):
        print(f"  {m}: {c}")

    # Position diversity
    if positions:
        _print_position_diversity(positions)

    # First few failures
    if failed:
        print(f"\n--- First 10 failures ---")
        for r in failed[:10]:
            print(f"Level {r.level_id} (diff={r.difficulty}):")
            for e in r.errors:
                print(f"  ERROR: {e}")
            for w in r.warnings:
                print(f"  WARN:  {w}")

    if warned:
        print(f"\n--- First 5 warnings ---")
        for r in warned[:5]:
            print(f"Level {r.level_id} (diff={r.difficulty}):")
            for w in r.warnings:
                print(f"  WARN: {w}")

    return len(failed)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="Comprehensive level generation validator")
    parser.add_argument("--count", type=int, default=1000, help="Number of levels to generate")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed (default: random, mirrors live backend)")
    parser.add_argument("--input", type=Path, help="Validate existing JSON file instead of generating")
    parser.add_argument("--output", type=Path, help="Write generated levels to JSON file")
    args = parser.parse_args()

    if args.input:
        reports = validate_file(args.input)
        failed = print_report(reports, f"Validate: {args.input.name}")
        return 1 if failed else 0

    # Generate mode
    level_dicts, reports, positions = generate_and_validate(
        args.count,
        seed=args.seed,
        use_set_mode=True,
        education_period="sinif_2",
    )
    failed = print_report(reports, f"Generate {args.count} levels (generate_set mode)", positions)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(level_dicts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nSaved to: {args.output}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
