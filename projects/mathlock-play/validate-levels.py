#!/usr/bin/env python3
"""
Sayı Yolculuğu — levels.json doğrulama scripti.
AI'ın ürettiği seviyelerin geçerliliğini ve çözülebilirliğini kontrol eder.

Kullanım:
    python3 validate-levels.py                # levels.json doğrula
    python3 validate-levels.py --file X.json  # belirli dosya

Çıkış kodları: 0 = başarılı, 1 = hata var
"""
import json
import sys
from collections import deque
from pathlib import Path

VALID_COMMANDS = {"x+", "x-", "y+", "y-", "z+", "z-"}
VALID_OP_TYPES = {"+", "-", "×"}
VALID_AGE_GROUPS = {"5-6", "7-8", "9-10", "11-12"}
VALID_OVERALLS = {"beginner", "developing", "intermediate", "advanced"}
EXPECTED_LEVELS = 12
MAX_GRID = 64  # cols * rows limit

CMD_DELTAS = {
    "x+": (1, 0, 0), "x-": (-1, 0, 0),
    "y+": (0, 1, 0), "y-": (0, -1, 0),
    "z+": (0, 0, 1), "z-": (0, 0, -1),
}

errors = []
warnings = []


def err(msg):
    errors.append(f"  ❌ {msg}")


def warn(msg):
    warnings.append(f"  ⚠️  {msg}")


def bfs_solvable(level):
    """BFS: (x, y, val) state space. Returns (solvable, min_steps)."""
    cols, rows = level["cols"], level["rows"]
    sx, sy, sv = level["startX"], level["startY"], level["startVal"]
    tx, ty = level["targetX"], level["targetY"]
    tv = level.get("targetVal")
    commands = level["commands"]
    max_cmds = level["maxCmds"]

    wall_set = set()
    for w in level.get("walls", []):
        wall_set.add((w[0], w[1]))

    op_map = {}
    for o in level.get("ops", []):
        op_map[(o["x"], o["y"])] = o

    # BFS
    start = (sx, sy, sv)
    visited = {start}
    queue = deque([(start, 0)])  # (state, steps)

    while queue:
        (cx, cy, cv), steps = queue.popleft()
        if steps >= max_cmds:
            continue

        for cmd_id in commands:
            dx, dy, dz = CMD_DELTAS[cmd_id]

            nx, ny, nv = cx + dx, cy + dy, cv + dz

            # z commands don't move
            if dz != 0:
                nx, ny = cx, cy

            # bounds check
            if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                continue

            # wall check
            if (nx, ny) in wall_set:
                continue

            # apply operation if present
            if dz == 0 and (nx, ny) in op_map:
                op = op_map[(nx, ny)]
                if op["type"] == "+":
                    nv = cv + op["val"]
                elif op["type"] == "-":
                    nv = cv - op["val"]
                elif op["type"] == "×":
                    nv = cv * op["val"]

            state = (nx, ny, nv)
            if state in visited:
                continue

            # check win
            pos_ok = nx == tx and ny == ty
            val_ok = tv is None or nv == tv
            if pos_ok and val_ok:
                return True, steps + 1

            # limit value range to prevent infinite state space
            if nv < -100 or nv > 1000:
                continue

            visited.add(state)
            queue.append((state, steps + 1))

    return False, -1


def validate_level(lv, idx, age_group):
    """Validate a single level."""
    prefix = f"Seviye {idx + 1} (id={lv.get('id', '?')})"

    # Required fields
    required = ["id", "title", "desc", "difficulty", "cols", "rows",
                "startX", "startY", "startVal", "targetX", "targetY",
                "walls", "ops", "commands", "maxCmds", "stars"]
    for field in required:
        if field not in lv:
            err(f"{prefix}: '{field}' alanı eksik")
            return

    # ID check
    if lv["id"] != idx + 1:
        err(f"{prefix}: id={lv['id']} ama beklenen {idx + 1}")

    # Grid bounds
    cols, rows = lv["cols"], lv["rows"]
    if cols < 1 or cols > 8 or rows < 1 or rows > 8:
        err(f"{prefix}: grid boyutu geçersiz ({cols}×{rows}), max 8×8")
    if cols * rows > MAX_GRID:
        err(f"{prefix}: grid çok büyük ({cols}×{rows} = {cols * rows} > {MAX_GRID})")

    # Difficulty
    if not (1 <= lv["difficulty"] <= 5):
        err(f"{prefix}: difficulty={lv['difficulty']}, 1-5 arası olmalı")

    # Start position in bounds
    if lv["startX"] < 0 or lv["startX"] >= cols or lv["startY"] < 0 or lv["startY"] >= rows:
        err(f"{prefix}: başlangıç ({lv['startX']},{lv['startY']}) grid dışında")

    # Target position in bounds
    if lv["targetX"] < 0 or lv["targetX"] >= cols or lv["targetY"] < 0 or lv["targetY"] >= rows:
        err(f"{prefix}: hedef ({lv['targetX']},{lv['targetY']}) grid dışında")

    # startVal positive
    if lv["startVal"] <= 0:
        err(f"{prefix}: startVal={lv['startVal']}, pozitif olmalı")

    # Commands valid
    for cmd in lv["commands"]:
        if cmd not in VALID_COMMANDS:
            err(f"{prefix}: geçersiz komut '{cmd}'")

    # Walls check
    wall_set = set()
    for w in lv["walls"]:
        if not isinstance(w, list) or len(w) != 2:
            err(f"{prefix}: geçersiz duvar formatı: {w}")
            continue
        wx, wy = w[0], w[1]
        if wx < 0 or wx >= cols or wy < 0 or wy >= rows:
            err(f"{prefix}: duvar ({wx},{wy}) grid dışında")
        wall_set.add((wx, wy))

    # Wall on start/target
    if (lv["startX"], lv["startY"]) in wall_set:
        err(f"{prefix}: başlangıç noktasında duvar var!")
    if (lv["targetX"], lv["targetY"]) in wall_set:
        err(f"{prefix}: hedef noktasında duvar var!")

    # Ops check
    for o in lv["ops"]:
        if not all(k in o for k in ["x", "y", "type", "val"]):
            err(f"{prefix}: operasyon eksik alan: {o}")
            continue
        if o["type"] not in VALID_OP_TYPES:
            err(f"{prefix}: geçersiz operasyon tipi '{o['type']}'")
        if o["val"] <= 0:
            err(f"{prefix}: operasyon değeri pozitif olmalı: {o}")
        if o["x"] < 0 or o["x"] >= cols or o["y"] < 0 or o["y"] >= rows:
            err(f"{prefix}: operasyon ({o['x']},{o['y']}) grid dışında")
        if o["x"] == lv["startX"] and o["y"] == lv["startY"]:
            warn(f"{prefix}: operasyon başlangıç noktasında (beklenmedik)")

    # Stars check
    stars = lv["stars"]
    if not isinstance(stars, list) or len(stars) != 2:
        err(f"{prefix}: stars formatı [3yıldız, 2yıldız] olmalı")
    else:
        if stars[0] >= stars[1]:
            err(f"{prefix}: stars[0]={stars[0]} >= stars[1]={stars[1]} (3-yıldız < 2-yıldız olmalı)")
        if stars[1] > lv["maxCmds"]:
            err(f"{prefix}: stars[1]={stars[1]} > maxCmds={lv['maxCmds']}")

    # maxCmds reasonable
    if lv["maxCmds"] < 1 or lv["maxCmds"] > 30:
        err(f"{prefix}: maxCmds={lv['maxCmds']}, 1-30 arası olmalı")

    # Title/desc checks
    if len(lv["title"]) < 2 or len(lv["title"]) > 30:
        warn(f"{prefix}: title uzunluğu {len(lv['title'])} (2-30 arası ideal)")
    if len(lv["desc"]) < 5 or len(lv["desc"]) > 60:
        warn(f"{prefix}: desc uzunluğu {len(lv['desc'])} (5-60 arası ideal)")

    # Solvability (BFS)
    solvable, min_steps = bfs_solvable(lv)
    if not solvable:
        err(f"{prefix}: ÇÖZÜLEMİYOR! BFS ile başlangıçtan hedefe ulaşılamadı.")
    else:
        if min_steps > lv["maxCmds"]:
            err(f"{prefix}: optimum çözüm ({min_steps} adım) > maxCmds ({lv['maxCmds']})")
        if min_steps > lv["stars"][0]:
            warn(f"{prefix}: optimum çözüm ({min_steps}) > 3-yıldız eşiği ({lv['stars'][0]}), 3 yıldız alınamaz")
        # Log solution info
        print(f"  ✅ {prefix}: çözülebilir (optimum={min_steps}, 3⭐≤{stars[0]}, 2⭐≤{stars[1]}, max={lv['maxCmds']})")


def validate(data):
    """Validate the entire levels.json."""

    # Top-level structure
    if "version" not in data:
        err("'version' alanı eksik")
    elif not isinstance(data["version"], int) or data["version"] < 1:
        err(f"version={data['version']}, pozitif int olmalı")

    if "ageGroup" not in data:
        err("'ageGroup' alanı eksik")
    elif data["ageGroup"] not in VALID_AGE_GROUPS:
        err(f"ageGroup='{data['ageGroup']}', geçerli: {VALID_AGE_GROUPS}")

    if "difficultyProfile" not in data:
        err("'difficultyProfile' alanı eksik")
    else:
        dp = data["difficultyProfile"]
        if dp.get("overall") not in VALID_OVERALLS:
            err(f"difficultyProfile.overall='{dp.get('overall')}', geçerli: {VALID_OVERALLS}")

    if "levels" not in data:
        err("'levels' dizisi eksik")
        return

    levels = data["levels"]
    if len(levels) != EXPECTED_LEVELS:
        err(f"{len(levels)} seviye var, {EXPECTED_LEVELS} bekleniyor")

    # Validate each level
    age_group = data.get("ageGroup", "7-8")
    titles = set()
    for i, lv in enumerate(levels):
        validate_level(lv, i, age_group)
        t = lv.get("title", "")
        if t in titles:
            err(f"Seviye {i + 1}: title tekrarı: '{t}'")
        titles.add(t)

    # Difficulty progression check
    diffs = [lv.get("difficulty", 0) for lv in levels]
    if len(diffs) >= 2:
        if diffs[0] > 2:
            warn(f"İlk seviye zorluk={diffs[0]}, başlangıç için çok zor")
        if diffs[-1] >= max(diffs):
            warn("Son seviye en zor — psikolojik olarak kolay bitirmek daha iyi")


def main():
    file_path = Path("data/levels.json")

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--file" and i + 1 < len(sys.argv) - 1:
            file_path = Path(sys.argv[i + 2])

    print(f"\n{'='*60}")
    print(f"  Sayı Yolculuğu — Seviye Doğrulama")
    print(f"  Dosya: {file_path}")
    print(f"{'='*60}\n")

    if not file_path.exists():
        print(f"❌ Dosya bulunamadı: {file_path}")
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        sys.exit(1)

    validate(data)

    print(f"\n{'─'*60}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} uyarı:")
        for w in warnings:
            print(w)

    if errors:
        print(f"\n❌ {len(errors)} HATA:")
        for e in errors:
            print(e)
        print(f"\n{'='*60}")
        print(f"  SONUÇ: BAŞARISIZ ({len(errors)} hata, {len(warnings)} uyarı)")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print(f"\n{'='*60}")
        print(f"  SONUÇ: BAŞARILI ✅ ({len(warnings)} uyarı)")
        print(f"{'='*60}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
