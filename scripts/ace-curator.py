#!/usr/bin/env python3
"""
ACE Curator — Adaptive Cross-session Experience playbook manager.

Parses, edits, and maintains hierarchical ACE lesson playbooks in wiki/ace/.
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ACE_DIR = Path("/home/akn/local/wiki/ace")
ARCHIVE_DIR = ACE_DIR / ".archive"
GENERAL_PLAYBOOK = ACE_DIR / "playbook.md"

PROJECT_MAP = {
    "ops-bot/": "ops-bot",
    "projects/webimar/": "webimar",
    "projects/mathlock-play/": "mathlock-play",
    "projects/sayi-yolculugu/": "sayi-yolculugu",
    "projects/telegram-kimi/": "telegram-kimi",
    "projects/robotopia-android/": "robotopia-android",
    "infrastructure/": "infrastructure",
}

LESSON_HEADER_RE = re.compile(r"^## Ders (\d+): (.+)$", re.MULTILINE)
CONFIDENCE_RE = re.compile(r"\*\*Confidence:\*\* ([\d.]+)")
CREATED_RE = re.compile(r"\*\*Created:\*\* (\d{4}-\d{2}-\d{2})")
UPDATED_RE = re.compile(r"\*\*Updated:\*\* (\d{4}-\d{2}-\d{2})")
VALIDATIONS_RE = re.compile(r"\*\*Validations:\*\* (\d+)")
SOURCE_RE = re.compile(r"\*\*Source:\*\* (.+)")
SCOPE_RE = re.compile(r"\*\*Scope:\*\* (.+)")
TYPE_RE = re.compile(r"\*\*Type:\*\* (.+)")

LESSON_TEMPLATE = """## Ders {id:03d}: {title}
**Confidence:** {confidence:.2f}
**Created:** {created}
**Updated:** {updated}
**Validations:** {validations}
**Source:** {source}
**Scope:** {scope}
**Type:** {type}

### Context
{context}

### Rule
{rule}

### Rationale
{rationale}

### Examples
#### ✅ Do
```{lang}
{do_example}
```

#### ❌ Don't
```{lang}
{dont_example}
```

### Related
{related}

---
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def detect_project(cwd: str = os.getcwd()) -> Optional[str]:
    """Bulunduğu dizinden proje adını tespit et."""
    for path_fragment, project_name in PROJECT_MAP.items():
        if path_fragment in cwd:
            return project_name
    return None


def playbook_path(project: Optional[str] = None) -> Path:
    if project is None or project == "genel":
        return GENERAL_PLAYBOOK
    path = ACE_DIR / f"{project}.md"
    if not path.exists():
        print(f"[WARN] Project playbook not found: {path}; falling back to general.")
        return GENERAL_PLAYBOOK
    return path


def parse_lessons(text: str) -> List[dict]:
    """Parse all ## Ders blocks from playbook markdown."""
    lessons = []
    matches = list(LESSON_HEADER_RE.finditer(text))
    for i, m in enumerate(matches):
        lesson_id = int(m.group(1))
        title = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]

        def _find(pattern: re.Pattern, default="") -> str:
            mm = pattern.search(block)
            return mm.group(1).strip() if mm else default

        lessons.append({
            "id": lesson_id,
            "title": title,
            "block": block,
            "confidence": float(_find(CONFIDENCE_RE, "0.50")),
            "created": _find(CREATED_RE, ""),
            "updated": _find(UPDATED_RE, ""),
            "validations": int(_find(VALIDATIONS_RE, "0")),
            "source": _find(SOURCE_RE, ""),
            "scope": _find(SCOPE_RE, "genel"),
            "type": _find(TYPE_RE, "pattern"),
        })
    return lessons


def next_lesson_id(text: str) -> int:
    lessons = parse_lessons(text)
    if not lessons:
        return 1
    return max(l["id"] for l in lessons) + 1


def read_playbook(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_playbook(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_stats(args) -> int:
    files = sorted(ACE_DIR.glob("*.md"))
    total_lessons = 0
    per_project = {}
    confidences = []

    for f in files:
        if f.name.startswith("_"):
            continue
        if f.name == "playbook.md":
            pname = "genel"
        else:
            pname = f.stem
        text = read_playbook(f)
        lessons = parse_lessons(text)
        total_lessons += len(lessons)
        per_project[pname] = len(lessons)
        confidences.extend([l["confidence"] for l in lessons])

    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    print("=" * 50)
    print("ACE Playbook İstatistikleri")
    print("=" * 50)
    print(f"Toplam ders: {total_lessons}")
    print(f"Ortalama confidence: {avg_conf:.2f}")
    print("\nProje başına dağılım:")
    for pname, count in sorted(per_project.items()):
        print(f"  {pname:20s} : {count:3d} ders")
    print("=" * 50)
    return 0


def cmd_list(args) -> int:
    path = playbook_path(args.project)
    text = read_playbook(path)
    lessons = parse_lessons(text)
    if not lessons:
        print(f"Playbook'ta ders yok: {path}")
        return 0
    print(f"{'ID':>5} {'Conf':>6} {'Type':>12} {'Title'}")
    print("-" * 60)
    for l in lessons:
        print(f"{l['id']:05d} {l['confidence']:6.2f} {l['type']:>12} {l['title']}")
    return 0


def cmd_get(args) -> int:
    path = playbook_path(args.project)
    text = read_playbook(path)
    lessons = parse_lessons(text)
    for l in lessons:
        if l["id"] == args.id:
            print(l["block"])
            return 0
    print(f"[ERROR] Ders bulunamadı: {args.id:03d} in {path}")
    return 1


def cmd_learn(args) -> int:
    path = playbook_path(args.project)
    text = read_playbook(path)
    lid = next_lesson_id(text)
    today = datetime.now().strftime("%Y-%m-%d")

    if args.title:
        title = args.title
        context = args.context or ""
        rule = args.rule or ""
        rationale = args.rationale or ""
        source = args.source or ""
        scope = args.scope or (args.project if args.project else "genel")
        ltype = args.type or "pattern"
        lang = args.lang or "python"
        do_ex = args.do_example or ""
        dont_ex = args.dont_example or ""
        related = args.related or ""
    else:
        print("Interaktif mod henüz desteklenmiyor. Lütfen argümanları kullanın:")
        print("  --title, --context, --rule, --rationale, --source, --scope, --type")
        return 1

    new_lesson = LESSON_TEMPLATE.format(
        id=lid,
        title=title,
        confidence=0.80,
        created=today,
        updated=today,
        validations=0,
        source=source,
        scope=scope,
        type=ltype,
        context=context,
        rule=rule,
        rationale=rationale,
        lang=lang,
        do_example=do_ex,
        dont_example=dont_ex,
        related=related,
    )

    # Append after the last lesson, or at end of file
    if text.strip():
        # Ensure separator before appending
        text = text.rstrip() + "\n\n" + new_lesson
    else:
        text = new_lesson

    write_playbook(path, text)
    print(f"[OK] Ders eklendi: {path} — Ders {lid:03d}: {title}")
    return 0


def _update_confidence(path: Path, lesson_id: int, delta: float) -> int:
    text = read_playbook(path)
    lessons = parse_lessons(text)
    found = False
    new_text = text
    for l in lessons:
        if l["id"] == lesson_id:
            found = True
            old_conf = l["confidence"]
            new_conf = max(0.0, min(1.0, old_conf + delta))
            # Replace confidence in block
            old_block = l["block"]
            new_block = CONFIDENCE_RE.sub(
                f"**Confidence:** {new_conf:.2f}", old_block, count=1
            )
            # Update updated date
            new_block = UPDATED_RE.sub(
                f"**Updated:** {datetime.now().strftime('%Y-%m-%d')}", new_block, count=1
            )
            if delta > 0:
                new_val = l["validations"] + 1
                new_block = VALIDATIONS_RE.sub(
                    f"**Validations:** {new_val}", new_block, count=1
                )
            new_text = new_text.replace(old_block, new_block, 1)
            print(f"[OK] Ders {lesson_id:03d}: confidence {old_conf:.2f} -> {new_conf:.2f}")
            break
    if not found:
        print(f"[ERROR] Ders bulunamadı: {lesson_id:03d} in {path}")
        return 1
    write_playbook(path, new_text)
    return 0


def cmd_validate(args) -> int:
    path = playbook_path(args.project)
    return _update_confidence(path, args.id, +0.05)


def cmd_invalidate(args) -> int:
    path = playbook_path(args.project)
    return _update_confidence(path, args.id, -0.15)


def cmd_prune(args) -> int:
    files = sorted(ACE_DIR.glob("*.md"))
    today = datetime.now().strftime("%Y-%m-%d")
    archived_any = False

    for f in files:
        if f.name.startswith("_"):
            continue
        text = read_playbook(f)
        lessons = parse_lessons(text)
        to_archive = [l for l in lessons if l["confidence"] < 0.30]
        if not to_archive:
            continue

        archive_file = ARCHIVE_DIR / f"{today}.md"
        archive_header = f"# Arşiv — {today}\n\nKaynak: `{f.name}`\n\n"
        archive_body = "\n\n".join(l["block"] for l in to_archive)

        if args.dry_run:
            print(f"[DRY-RUN] {f.name}: {len(to_archive)} ders arşivlenecek")
            for l in to_archive:
                print(f"  - Ders {l['id']:03d}: {l['title']} (conf={l['confidence']:.2f})")
            continue

        # Write to archive
        if archive_file.exists():
            existing = archive_file.read_text(encoding="utf-8")
            archive_file.write_text(existing + "\n\n" + archive_header + archive_body, encoding="utf-8")
        else:
            archive_file.write_text(archive_header + archive_body, encoding="utf-8")

        # Remove from source
        new_text = text
        for l in to_archive:
            new_text = new_text.replace(l["block"], "", 1)
        write_playbook(f, new_text)
        archived_any = True
        print(f"[OK] {f.name}: {len(to_archive)} ders arşivlendi -> {archive_file}")

    if not archived_any and not args.dry_run:
        print("Arşivlenecek ders yok (confidence < 0.30).")
    return 0


def cmd_conflicts(args) -> int:
    files = sorted(ACE_DIR.glob("*.md"))
    all_rules = []
    for f in files:
        if f.name.startswith("_"):
            continue
        text = read_playbook(f)
        lessons = parse_lessons(text)
        for l in lessons:
            # Extract rule text (simple heuristic: first line after ### Rule)
            rule_match = re.search(r"### Rule\n(.+?)(?:\n###|\Z)", l["block"], re.DOTALL)
            rule_text = rule_match.group(1).strip() if rule_match else ""
            all_rules.append((f.name, l["id"], l["title"], rule_text, l["confidence"]))

    # Very simple conflict detection: look for negations
    conflicts = []
    for i, (f1, id1, t1, r1, c1) in enumerate(all_rules):
        for j, (f2, id2, t2, r2, c2) in enumerate(all_rules):
            if i >= j:
                continue
            # Heuristic: one says "X" the other says "X yapma / don't X"
            r1_lower = r1.lower()
            r2_lower = r2.lower()
            if ("yapma" in r1_lower or "don't" in r1_lower or "kullanma" in r1_lower) and \
               ("yap" in r2_lower or "do" in r2_lower or "kullan" in r2_lower):
                if len(set(r1_lower.split()) & set(r2_lower.split())) >= 3:
                    conflicts.append(((f1, id1, t1, c1), (f2, id2, t2, c2)))

    if not conflicts:
        print("Çakışan ders bulunamadı.")
        return 0

    print(f"{len(conflicts)} olası çakışma bulundu:")
    for (f1, id1, t1, c1), (f2, id2, t2, c2) in conflicts:
        print(f"  - Ders {id1:03d} ({f1}, conf={c1:.2f}): {t1}")
        print(f"    Ders {id2:03d} ({f2}, conf={c2:.2f}): {t2}")
    return 0


def cmd_topla(args) -> int:
    print("=" * 50)
    print("ACE TOPLA — Oturum Sonu Özeti")
    print("=" * 50)
    print("\n[1/4] Stats:")
    cmd_stats(args)
    print("\n[2/4] Prune dry-run:")
    args.dry_run = True
    cmd_prune(args)
    args.dry_run = False
    print("\n[3/4] Çakışma kontrolü:")
    cmd_conflicts(args)
    print("\n[4/4] Wiki Ingest:")
    import subprocess
    result = subprocess.run(
        ["python3", "/home/akn/local/scripts/wiki-assistant.py", "--prepare", "--project", "ace"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("[OK] Wiki asistanı çalıştırıldı.")
        print(result.stdout[:500] if result.stdout else "  (değişiklik yok veya başarılı)")
    else:
        print("[WARN] Wiki asistanı çalıştırılamadı, fallback aktif:")
        print(result.stderr[:300] if result.stderr else "  (bilinmeyen hata)")
        print("  Manuel: cd /home/akn/local && python3 scripts/wiki-assistant.py --prepare")
    print("\n" + "=" * 50)
    print("ACE topla tamamlandı.")
    print("Ders eklemek için: ace-curator.py --learn --title '...' --rule '...'")
    print("=" * 50)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="ACE Curator — Playbook manager")
    sub = parser.add_subparsers(dest="command")

    p_stats = sub.add_parser("stats", help="Playbook istatistikleri")
    p_stats.add_argument("--project", help="Proje adı (varsayılan: genel)")

    p_list = sub.add_parser("list", help="Tüm dersleri listele")
    p_list.add_argument("--project", help="Proje adı")

    p_get = sub.add_parser("get", help="Belirli dersi göster")
    p_get.add_argument("id", type=int, help="Ders ID")
    p_get.add_argument("--project", help="Proje adı")

    p_learn = sub.add_parser("learn", help="Yeni ders ekle")
    p_learn.add_argument("--project", help="Proje adı")
    p_learn.add_argument("--title", required=True, help="Ders başlığı")
    p_learn.add_argument("--context", default="", help="Context açıklaması")
    p_learn.add_argument("--rule", default="", help="Kural")
    p_learn.add_argument("--rationale", default="", help="Gerekçe")
    p_learn.add_argument("--source", default="", help="Kaynak dosya/komut")
    p_learn.add_argument("--scope", default="", help="Kapsam (genel veya proje)")
    p_learn.add_argument("--type", default="pattern", help="pattern | anti-pattern | workflow | pitfall")
    p_learn.add_argument("--lang", default="python", help="Örnek kod dili")
    p_learn.add_argument("--do-example", default="", help="Doğru örnek")
    p_learn.add_argument("--dont-example", default="", help="Yanlış örnek")
    p_learn.add_argument("--related", default="", help="Çapraz referanslar")

    p_validate = sub.add_parser("validate", help="Ders confidence'ını artır (+0.05)")
    p_validate.add_argument("id", type=int, help="Ders ID")
    p_validate.add_argument("--project", help="Proje adı")

    p_invalidate = sub.add_parser("invalidate", help="Ders confidence'ını düşür (-0.15)")
    p_invalidate.add_argument("id", type=int, help="Ders ID")
    p_invalidate.add_argument("--project", help="Proje adı")

    p_prune = sub.add_parser("prune", help="Düşük confidence dersleri arşivle")
    p_prune.add_argument("--dry-run", action="store_true", help="Sadece göster, arşivleme")
    p_prune.add_argument("--project", help="Proje adı (varsayılan: hepsi)")

    p_conflicts = sub.add_parser("conflicts", help="Çakışan dersleri listele")

    p_topla = sub.add_parser("topla", help="Oturum sonu toplu işlem (stats + prune dry-run + conflicts)")
    p_topla.add_argument("--project", help="Proje adı")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Auto-detect project if not given (except for global ops)
    if hasattr(args, "project") and args.project is None and args.command not in ("stats", "prune", "conflicts", "topla"):
        args.project = detect_project()

    commands = {
        "stats": cmd_stats,
        "list": cmd_list,
        "get": cmd_get,
        "learn": cmd_learn,
        "validate": cmd_validate,
        "invalidate": cmd_invalidate,
        "prune": cmd_prune,
        "conflicts": cmd_conflicts,
        "topla": cmd_topla,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
