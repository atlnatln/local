#!/usr/bin/env python3
"""
wiki_lint.py — Deterministic health checker for a local markdown wiki.

Usage:
    python3 wiki_lint.py /home/akn/local/wiki

Performs 10 checks and reports findings in plain text to stdout,
plus appends a structured summary to wiki/log.md.

Exit codes:
    0 — all checks passed
    1 — at least one FAIL
    2 — only WARN (no FAIL)
"""

import sys
import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = {"title", "created", "updated", "type", "tags", "related"}
VALID_TYPES = {"concept", "project", "decision", "index", "log"}
STALE_DAYS = 90
MAX_LINES = 200
LOG_MAX_ENTRIES = 500

WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')
FRONTMATTER_RE = re.compile(r'\A---\s*\n(.*?)\n---\s*\n', re.DOTALL)
TAG_TAXONOMY_RE = re.compile(r'##\s*Tag\s*Taxonomy\b', re.IGNORECASE)
LOG_ENTRY_RE = re.compile(r'^##\s*\[')

EXCLUDED_FILES = {"index.md", "log.md"}
EXCLUDED_DIRS = {"_archive", "raw"}


# ---------------------------------------------------------------------------
# Frontmatter parser (manual — no external YAML library)
# ---------------------------------------------------------------------------
def parse_frontmatter(text: str) -> Tuple[Optional[Dict], str]:
    """Extract YAML frontmatter between --- fences and parse basic key: value pairs.

    Supports:
      - scalar strings (unquoted, single-quoted, double-quoted)
      - inline lists:  tags: [item1, item2]
      - block lists:   tags:\n  - item1\n  - item2
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text

    raw = match.group(1)
    body = text[match.end():]
    data: Dict[str, any] = {}

    # Remove comments
    lines = []
    for line in raw.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        lines.append(line)

    # Join and process
    content = "\n".join(lines)

    # Parse block-style lists first
    key = None
    current_list = []
    in_list = False

    parsed_keys = set()

    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            if in_list and key is not None:
                data[key] = current_list
                current_list = []
                in_list = False
                key = None
            continue

        # Block list item
        list_match = re.match(r'^(\s*)-\s+(.*)', stripped)
        if list_match:
            indent = len(list_match.group(1))
            value = list_match.group(2).strip()
            if indent >= 2 and in_list and key is not None:
                current_list.append(value)
            elif not in_list:
                # Orphan list item — attach to last key if possible
                if key is not None:
                    current_list.append(value)
                    in_list = True
            continue

        # Key: value line
        kv_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)', stripped)
        if kv_match:
            # Flush previous list
            if in_list and key is not None:
                data[key] = current_list
                current_list = []
                in_list = False

            key = kv_match.group(1)
            value = kv_match.group(2).strip()
            parsed_keys.add(key)

            if not value:
                # Could be a block list starting next line
                current_list = []
                in_list = True
                continue

            # Inline list [a, b, c]
            if value.startswith("[") and value.endswith("]"):
                items = []
                inner = value[1:-1]
                for item in inner.split(","):
                    item = item.strip().strip('"').strip("'")
                    if item:
                        items.append(item)
                data[key] = items
                in_list = False
                continue

            # Scalar
            val = value.strip('"').strip("'")

            # Boolean
            if val.lower() == "true":
                data[key] = True
            elif val.lower() == "false":
                data[key] = False
            else:
                data[key] = val
            in_list = False
            continue

    # Flush final list
    if in_list and key is not None and key not in data:
        data[key] = current_list

    return data, body


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------
def is_excluded(path: Path, wiki_root: Path) -> bool:
    """Check if a path should be excluded from wiki page checks."""
    rel = path.relative_to(wiki_root)
    # Check excluded filenames
    if path.name in EXCLUDED_FILES:
        return True
    # Check excluded directories
    for part in rel.parts:
        if part in EXCLUDED_DIRS:
            return True
    return False


def find_md_files(wiki_root: Path) -> List[Path]:
    """Find all .md files under wiki_root."""
    md_files = []
    for path in wiki_root.rglob("*.md"):
        md_files.append(path)
    return sorted(md_files)


def get_wiki_pages(wiki_root: Path) -> List[Path]:
    """Get all wiki pages (excluding SCHEMA.md, log.md, _archive/*)."""
    return [p for p in find_md_files(wiki_root) if not is_excluded(p, wiki_root)]


# ---------------------------------------------------------------------------
# Wikilink helpers
# ---------------------------------------------------------------------------
def extract_wikilinks(text: str) -> List[Tuple[str, int]]:
    """Extract all [[...]] wikilinks with 0-based line numbers."""
    results = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in WIKILINK_RE.finditer(line):
            link_text = match.group(1).strip()
            # Handle [[Page Title|display text]]
            if "|" in link_text:
                link_text = link_text.split("|", 1)[0].strip()
            results.append((link_text, lineno))
    return results


def wikilink_to_filename(link_text: str) -> str:
    """Convert a wikilink target to a probable filename."""
    # [[Page Title]] → Page Title.md or page-title.md
    # Try multiple forms
    candidates = [
        link_text + ".md",
        link_text.replace(" ", "-") + ".md",
        link_text.replace(" ", "_") + ".md",
        link_text.replace("-", " ") + ".md",
    ]
    return candidates


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

class CheckResult:
    """Result of a single check."""
    def __init__(self, name: str):
        self.name = name
        self.status = "PASS"   # PASS / WARN / FAIL
        self.details: List[str] = []
        self.count = 0

    def add(self, msg: str):
        self.details.append(msg)


def check_orphan_pages(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 1: Find pages with zero inbound wikilinks."""
    result = CheckResult("Orphan Pages")

    # Build title → page map and filename → page map
    title_to_page: Dict[str, Path] = {}
    filename_to_page: Dict[str, Path] = {}
    for page in pages:
        filename_to_page[page.name.lower()] = page
        fm = all_frontmatters.get(page, {})
        title = fm.get("title", "")
        if title:
            title_to_page[title.lower()] = page

    # Collect all inbound links
    inbound_counts: Dict[Path, int] = {page: 0 for page in pages}

    for page in pages:
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, IOError) as e:
            result.add(f"WARN: Could not read {page}: {e}")
            continue
        links = extract_wikilinks(text)
        for link_text, _ in links:
            link_lower = link_text.lower()
            # Try title match
            found = False
            for t, p in title_to_page.items():
                if t == link_lower:
                    inbound_counts[p] = inbound_counts.get(p, 0) + 1
                    found = True
                    break
            if not found:
                # Try filename match
                for fn, p in filename_to_page.items():
                    base = fn[:-3] if fn.endswith(".md") else fn
                    if base == link_lower or base == link_lower.replace(" ", "-").replace("_", "-"):
                        inbound_counts[p] = inbound_counts.get(p, 0) + 1
                        found = True
                        break

    orphans = [page for page in pages if inbound_counts.get(page, 0) == 0]

    if orphans:
        result.status = "WARN"
        result.count = len(orphans)
        for page in orphans:
            rel = page.relative_to(wiki_root)
            result.add(f"  [[{rel.stem}]] (no inbound links)")
    else:
        result.count = 0

    return result


def check_broken_wikilinks(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 2: Find [[...]] references that don't resolve to any page."""
    result = CheckResult("Broken Wikilinks")

    # Build set of valid targets (titles and filenames)
    valid_targets: Set[str] = set()
    for page in pages:
        valid_targets.add(page.name.lower())
        valid_targets.add(page.stem.lower())
        valid_targets.add(page.stem.lower().replace("-", " "))
        valid_targets.add(page.stem.lower().replace("_", " "))
        fm = all_frontmatters.get(page, {})
        title = fm.get("title", "")
        if title:
            valid_targets.add(title.lower())

    broken = []
    for page in pages:
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, IOError) as e:
            result.add(f"WARN: Could not read {page}: {e}")
            continue
        links = extract_wikilinks(text)
        for link_text, lineno in links:
            link_lower = link_text.lower()
            # Check all valid targets
            found = False
            for target in valid_targets:
                if target == link_lower:
                    found = True
                    break
                # Also check without .md
                if target.endswith(".md") and target[:-3] == link_lower:
                    found = True
                    break
                # Check hyphen/space variants
                normalized = target.replace("-", " ").replace("_", " ")
                if normalized == link_lower.replace("-", " ").replace("_", " "):
                    found = True
                    break
            if not found:
                rel = page.relative_to(wiki_root)
                broken.append(f"  {rel}:{lineno} — [[{link_text}]]")

    if broken:
        result.status = "WARN"
        result.count = len(broken)
        for b in broken:
            result.add(b)
    else:
        result.count = 0

    return result


def check_index_completeness(wiki_root: Path, pages: List[Path]) -> CheckResult:
    """Check 3: Ensure every page is linked from index.md, and archived pages are in ## Archived Pages."""
    result = CheckResult("Index Completeness")

    index_path = wiki_root / "index.md"
    if not index_path.exists():
        result.status = "FAIL"
        result.add("  index.md not found")
        return result

    try:
        index_text = index_path.read_text(encoding="utf-8")
    except (OSError, IOError) as e:
        result.status = "FAIL"
        result.add(f"  Could not read index.md: {e}")
        return result

    # Split index into active section and archived section
    active_lines = []
    archived_lines = []
    in_archived = False
    for line in index_text.splitlines():
        if re.match(r'^##\s*Archived\s*Pages\s*$', line, re.IGNORECASE):
            in_archived = True
            continue
        if in_archived and re.match(r'^##\s', line):
            in_archived = False
        if in_archived:
            archived_lines.append(line)
        else:
            active_lines.append(line)

    active_text = "\n".join(active_lines)
    archived_text = "\n".join(archived_lines)

    active_wikilinks = [t.lower() for t, _ in extract_wikilinks(active_text)]
    archived_wikilinks = [t.lower() for t, _ in extract_wikilinks(archived_text)]

    # Find archived pages
    archived_pages = []
    for path in wiki_root.rglob("*.md"):
        rel = path.relative_to(wiki_root)
        for part in rel.parts:
            if part == "_archive":
                archived_pages.append(path)
                break
    archived_pages.sort()

    missing_active = []
    missing_archived = []
    mixed_archived = []

    # Check active pages are in active section
    for page in pages:
        if page.name in EXCLUDED_FILES:
            continue
        stem = page.stem
        found = False
        for link in active_wikilinks:
            if link == stem.lower():
                found = True
                break
            if link == stem.lower().replace("-", " ").replace("_", " "):
                found = True
                break
            if link == stem.lower().replace(" ", "-"):
                found = True
                break
        if not found:
            missing_active.append(page.relative_to(wiki_root))

    # Check archived pages are in archived section
    for page in archived_pages:
        stem = page.stem
        found = False
        for link in archived_wikilinks:
            if link == stem.lower():
                found = True
                break
            if link == stem.lower().replace("-", " ").replace("_", " "):
                found = True
                break
            if link == stem.lower().replace(" ", "-"):
                found = True
                break
        if not found:
            missing_archived.append(page.relative_to(wiki_root))

        # Ensure archived page is not mixed into active section
        found_active = False
        for link in active_wikilinks:
            if link == stem.lower():
                found_active = True
                break
            if link == stem.lower().replace("-", " ").replace("_", " "):
                found_active = True
                break
            if link == stem.lower().replace(" ", "-"):
                found_active = True
                break
        if found_active:
            mixed_archived.append(page.relative_to(wiki_root))

    issues = []
    if missing_active:
        for m in missing_active:
            issues.append(f"  [[{m.stem}]] (missing from active section)")
    if missing_archived:
        for m in missing_archived:
            issues.append(f"  [[{m.stem}]] (missing from ## Archived Pages)")
    if mixed_archived:
        for m in mixed_archived:
            issues.append(f"  [[{m.stem}]] (archived page in active section)")

    if issues:
        result.status = "WARN"
        result.count = len(issues)
        for issue in issues:
            result.add(issue)
    else:
        result.count = 0

    return result


def check_frontmatter(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 4: Validate YAML frontmatter fields."""
    result = CheckResult("Frontmatter Validation")

    errors = []
    for page in pages:
        fm = all_frontmatters.get(page)
        rel = page.relative_to(wiki_root)

        if fm is None:
            errors.append(f"  {rel} — no frontmatter found")
            continue

        missing = REQUIRED_FIELDS - set(fm.keys())
        if missing:
            errors.append(f"  {rel} — missing fields: {sorted(missing)}")

        # Validate type
        page_type = fm.get("type", "")
        if page_type and page_type not in VALID_TYPES:
            errors.append(f"  {rel} — invalid type: '{page_type}' (expected one of: {', '.join(sorted(VALID_TYPES))})")

        # Validate tags is a list
        tags = fm.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append(f"  {rel} — 'tags' should be a list, got {type(tags).__name__}")

        # Validate related is a list
        related = fm.get("related")
        if related is not None and not isinstance(related, list):
            errors.append(f"  {rel} — 'related' should be a list, got {type(related).__name__}")

    if errors:
        result.status = "FAIL"
        result.count = len(errors)
        for e in errors:
            result.add(e)
    else:
        result.count = 0

    return result


def check_stale_content(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 5: Flag pages where 'updated' is >90 days older than source file mtime."""
    result = CheckResult("Stale Content")

    stale = []
    for page in pages:
        fm = all_frontmatters.get(page, {})
        updated_str = fm.get("updated", "")
        sources = fm.get("sources", [])

        if not updated_str or not sources:
            continue

        if isinstance(sources, str):
            sources = [sources]

        # Parse updated date
        updated_date = None
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M"):
            try:
                updated_date = datetime.datetime.strptime(updated_str, fmt)
                break
            except ValueError:
                continue

        if updated_date is None:
            continue

        # Find most recent source modification time
        max_mtime = None
        for src in sources:
            src_path = wiki_root / src if not os.path.isabs(src) else Path(src)
            if not src_path.exists():
                continue
            try:
                mtime = datetime.datetime.fromtimestamp(src_path.stat().st_mtime)
                if max_mtime is None or mtime > max_mtime:
                    max_mtime = mtime
            except (OSError, IOError):
                continue

        if max_mtime is None:
            continue

        delta = max_mtime - updated_date
        if delta.days > STALE_DAYS:
            rel = page.relative_to(wiki_root)
            stale.append(f"  {rel} — updated {updated_str}, source modified {max_mtime.strftime('%Y-%m-%d')} ({delta.days} days stale)")

    if stale:
        result.status = "WARN"
        result.count = len(stale)
        for s in stale:
            result.add(s)
    else:
        result.count = 0

    return result


def check_contradictions(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 6: Find pages with contested: true."""
    result = CheckResult("Contradictions")

    contested = []
    for page in pages:
        fm = all_frontmatters.get(page, {})
        if fm.get("contested") is True:
            rel = page.relative_to(wiki_root)
            contested.append(f"  [[{rel.stem}]] — requires human review")

    if contested:
        result.status = "WARN"
        result.count = len(contested)
        for c in contested:
            result.add(c)
    else:
        result.count = 0

    return result


def check_page_size(wiki_root: Path, pages: List[Path]) -> CheckResult:
    """Check 7: Flag pages longer than MAX_LINES."""
    result = CheckResult("Page Size")

    oversized = []
    for page in pages:
        try:
            with open(page, "r", encoding="utf-8") as f:
                lines = f.readlines()
            count = len(lines)
            if count > MAX_LINES:
                rel = page.relative_to(wiki_root)
                oversized.append(f"  {rel} — {count} lines")
        except (OSError, IOError) as e:
            result.add(f"WARN: Could not read {page}: {e}")

    if oversized:
        result.status = "WARN"
        result.count = len(oversized)
        for o in oversized:
            result.add(o)
    else:
        result.count = 0

    return result


def check_tag_audit(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 8: Compare tags against approved taxonomy in SCHEMA.md."""
    result = CheckResult("Tag Audit")

    # Load approved tags from SCHEMA.md
    approved_tags: Set[str] = set()
    schema_path = wiki_root / "SCHEMA.md"
    taxonomy_found = False

    if schema_path.exists():
        try:
            schema_text = schema_path.read_text(encoding="utf-8")
            # Find Tag Taxonomy section
            lines = schema_text.splitlines()
            in_taxonomy = False
            for line in lines:
                if TAG_TAXONOMY_RE.search(line):
                    in_taxonomy = True
                    taxonomy_found = True
                    continue
                if in_taxonomy:
                    # Stop at next h2
                    if re.match(r'^##\s', line) and not TAG_TAXONOMY_RE.search(line):
                        break
                    # Extract tags from list items or inline backticks
                    for match in re.finditer(r'`([^`]+)`', line):
                        approved_tags.add(match.group(1).lower().strip())
                    for match in re.finditer(r'^\s*[-*]\s+(\S+)', line):
                        approved_tags.add(match.group(1).lower().strip())
        except (OSError, IOError):
            result.add("WARN: Could not read SCHEMA.md")

    if not taxonomy_found:
        result.add("WARN: No ## Tag Taxonomy section found in SCHEMA.md")

    # Collect all tags from pages
    all_tags: Dict[str, int] = {}
    for page in pages:
        fm = all_frontmatters.get(page, {})
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list):
            continue
        for tag in tags:
            tag_lower = tag.lower().strip()
            all_tags[tag_lower] = all_tags.get(tag_lower, 0) + 1

    unknown = []
    for tag in sorted(all_tags.keys()):
        if tag not in approved_tags:
            unknown.append(f"  '{tag}' (used {all_tags[tag]} time{'s' if all_tags[tag] > 1 else ''})")

    if unknown:
        result.status = "WARN"
        result.count = len(unknown)
        for u in unknown:
            result.add(u)
    else:
        result.count = 0

    return result


def check_raw_existence(wiki_root: Path, pages: List[Path], all_frontmatters: Dict[Path, Dict]) -> CheckResult:
    """Check 9: Verify every source file listed in frontmatter exists in wiki/raw/."""
    result = CheckResult("Raw Existence Check")

    missing = []

    for page in pages:
        fm = all_frontmatters.get(page, {})
        sources = fm.get("sources", [])
        if not sources:
            continue
        if isinstance(sources, str):
            sources = [sources]

        for src in sources:
            if os.path.isabs(src):
                src_path = Path(src)
            else:
                # Normalize to wiki/raw/ prefix
                if src.startswith("raw/") or src.startswith("raw\\"):
                    src_path = wiki_root / src
                else:
                    src_path = wiki_root / "raw" / src
            if not src_path.exists():
                page_rel = page.relative_to(wiki_root)
                missing.append(f"  {src_path.relative_to(wiki_root)} — not found (page: [[{page_rel.stem}]])")

    if missing:
        result.status = "WARN"
        result.count = len(missing)
        for m in missing:
            result.add(m)
    else:
        result.count = 0

    return result


def check_log_rotation(wiki_root: Path) -> CheckResult:
    """Check 10: Count entries in log.md and warn if >500."""
    result = CheckResult("Log Rotation")

    log_path = wiki_root / "log.md"
    if not log_path.exists():
        result.count = 0
        return result

    try:
        log_text = log_path.read_text(encoding="utf-8")
    except (OSError, IOError) as e:
        result.add(f"WARN: Could not read log.md: {e}")
        result.count = 0
        return result

    count = 0
    for line in log_text.splitlines():
        if LOG_ENTRY_RE.match(line):
            count += 1

    result.count = count
    if count > LOG_MAX_ENTRIES:
        result.status = "WARN"
        result.add(f"  log.md has {count} entries (> {LOG_MAX_ENTRIES}), rotation needed")

    return result


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------
def format_report(results: List[CheckResult]) -> str:
    """Format results as human-readable plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("WIKI LINT REPORT")
    lines.append("=" * 60)
    lines.append("")

    for result in results:
        status_icon = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(result.status, "[?]")
        lines.append(f"{status_icon} {result.name}")
        if result.details:
            for detail in result.details:
                lines.append(f"  {detail}")
        elif result.status == "PASS":
            lines.append("  OK")
        lines.append("")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    warned = sum(1 for r in results if r.status == "WARN")
    failed = sum(1 for r in results if r.status == "FAIL")

    lines.append("-" * 60)
    lines.append(f"SUMMARY: {passed}/{total} passed, {warned} warning(s), {failed} failure(s)")
    lines.append("-" * 60)

    return "\n".join(lines)


def append_log(wiki_root: Path, results: List[CheckResult]) -> None:
    """Append structured markdown summary to wiki/log.md."""
    log_path = wiki_root / "log.md"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")

    # Extract counts/details from each check
    rmap = {r.name: r for r in results}

    def get_count(name: str) -> int:
        return rmap.get(name, CheckResult(name)).count

    def format_list(name: str) -> str:
        r = rmap.get(name, CheckResult(name))
        if not r.details:
            return "0"
        # Extract bracketed names from details
        items = []
        for d in r.details:
            m = re.search(r'\[\[([^\]]+)\]\]', d)
            if m:
                items.append(f"[[{m.group(1)}]]")
        if items:
            return f"{r.count} ({', '.join(items[:5])}{'...' if r.count > 5 else ''})"
        return str(r.count)

    def format_tags(name: str) -> str:
        r = rmap.get(name, CheckResult(name))
        if not r.details:
            return "0"
        tags = []
        for d in r.details:
            m = re.search(r"'(\S+)'", d)
            if m:
                tags.append(m.group(1))
        if tags:
            return f"{r.count} ({', '.join(tags[:10])}{'...' if r.count > 10 else ''})"
        return str(r.count)

    entry = f"""## [{now}] lint | {passed}/{total}
- Orphan pages: {format_list('Orphan Pages')}
- Broken links: {get_count('Broken Wikilinks')}
- Missing from index: {get_count('Index Completeness')}
- Frontmatter errors: {get_count('Frontmatter Validation')}
- Stale pages: {get_count('Stale Content')}
- Contradictions: {get_count('Contradictions')}
- Oversized pages: {get_count('Page Size')}
- Unknown tags: {format_tags('Tag Audit')}
- Raw existence: {get_count('Raw Existence Check')}
- Log size: {get_count('Log Rotation')} entries

"""

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except (OSError, IOError) as e:
        print(f"WARN: Could not append to {log_path}: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <wiki_root>", file=sys.stderr)
        return 1

    wiki_root = Path(sys.argv[1]).resolve()
    if not wiki_root.is_dir():
        print(f"FAIL: {wiki_root} is not a directory", file=sys.stderr)
        return 1

    print(f"Wiki root: {wiki_root}")
    print()

    # Discover pages
    all_md = find_md_files(wiki_root)
    pages = get_wiki_pages(wiki_root)

    if not pages:
        print("WARN: No wiki pages found.")

    # Parse frontmatter for all pages (and excluded files that might be referenced)
    all_frontmatters: Dict[Path, Dict] = {}
    for md_file in all_md:
        try:
            text = md_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if fm is not None:
                all_frontmatters[md_file] = fm
        except (OSError, IOError):
            pass

    # Run checks
    results = []
    results.append(check_orphan_pages(wiki_root, pages, all_frontmatters))
    results.append(check_broken_wikilinks(wiki_root, pages, all_frontmatters))
    results.append(check_index_completeness(wiki_root, pages))
    results.append(check_frontmatter(wiki_root, pages, all_frontmatters))
    results.append(check_stale_content(wiki_root, pages, all_frontmatters))
    results.append(check_contradictions(wiki_root, pages, all_frontmatters))
    results.append(check_page_size(wiki_root, pages))
    results.append(check_tag_audit(wiki_root, pages, all_frontmatters))
    results.append(check_raw_existence(wiki_root, pages, all_frontmatters))
    results.append(check_log_rotation(wiki_root))

    # Print report
    report = format_report(results)
    print(report)

    # Append to log
    append_log(wiki_root, results)

    # Determine exit code
    has_fail = any(r.status == "FAIL" for r in results)
    has_warn = any(r.status == "WARN" for r in results)

    if has_fail:
        return 1
    if has_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
