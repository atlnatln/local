#!/usr/bin/env python3
"""
MathLock Play i18n migration script.
Moves hardcoded strings from layouts and Kotlin code into strings.xml (TR + EN).
"""
import os
import re
from collections import OrderedDict

BASE = "/home/akn/local/projects/mathlock-play/app/src/main"
STRINGS_TR = os.path.join(BASE, "res/values/strings.xml")
STRINGS_EN = os.path.join(BASE, "res/values-en/strings.xml")
LAYOUT_DIR = os.path.join(BASE, "res/layout")
JAVA_DIR = os.path.join(BASE, "java/com/akn/mathlock")


def slugify(text):
    """Convert text to snake_case slug, removing punctuation."""
    # Remove emojis
    emoji_pat = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U00002600-\U000026FF"
        "]+", flags=re.UNICODE,
    )
    text = emoji_pat.sub("", text).strip()
    if not text:
        return None
    # Keep alphanumerics and Turkish chars, spaces -> underscore
    text = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", "", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", "_", text)
    text = text[:50].strip("_")
    return text


def read_existing_strings(path):
    """Parse existing strings.xml into (names_set, value_to_name_dict, content)."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    names = set()
    val2name = {}
    for m in re.finditer(r'<string name="([^"]+)">(.*?)</string>', content, re.DOTALL):
        name, value = m.group(1), m.group(2)
        names.add(name)
        val2name[value] = name
    return names, val2name, content


def make_name(text, prefix, existing_names, new_names_set):
    """Generate a unique string resource name."""
    if text in val2name:
        return val2name[text]
    base = slugify(text)
    if not base:
        return None
    name = f"{prefix}_{base}"
    # dedupe
    counter = 1
    orig = name
    while name in existing_names or name in new_names_set:
        name = f"{orig}_{counter}"
        counter += 1
    return name


def is_emoji_only(text):
    """Return True if text is only emojis / whitespace."""
    return bool(re.fullmatch(
        r"[\s\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        r"\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251"
        r"\U0001F900-\U0001F9FF\U00002600-\U000026FF]+", text, flags=re.UNICODE
    ))


# ------------------------------------------------------------------
# 1. Load existing TR strings
# ------------------------------------------------------------------
existing_names, val2name, tr_content = read_existing_strings(STRINGS_TR)
_, _, en_content = read_existing_strings(STRINGS_EN)

new_strings = OrderedDict()          # value -> name (for TR insertion)
new_name_set = set()                 # quick lookup for dedup

# ------------------------------------------------------------------
# 2. Process layouts
# ------------------------------------------------------------------
layout_changes = []
for fname in sorted(os.listdir(LAYOUT_DIR)):
    if not fname.endswith(".xml"):
        continue
    path = os.path.join(LAYOUT_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content

    prefix = fname.replace("activity_", "").replace("fragment_", "").replace("dialog_", "").replace("item_", "").replace(".xml", "")

    # Replace all android:text="..." that are NOT @string/ references
    matches = list(re.finditer(r'android:text="([^"]*)"', content))
    # iterate in reverse so string replacements don't shift later indices
    for m in reversed(matches):
        text = m.group(1)
        if text.startswith("@string/") or text.startswith("@android:string/"):
            continue
        if re.fullmatch(r"\d+", text):          # pure number, skip
            continue
        if is_emoji_only(text):                  # emoji-only, skip
            continue
        if not text.strip():                     # empty string, skip
            continue

        name = make_name(text, prefix, existing_names, new_name_set)
        if name is None:
            continue
        if text not in val2name and text not in new_strings:
            new_strings[text] = name
            new_name_set.add(name)
        else:
            name = val2name.get(text, new_strings.get(text, name))

        old = f'android:text="{text}"'
        new = f'android:text="@string/{name}"'
        # replace only this occurrence using the exact slice position
        content = content[:m.start()] + new + content[m.end():]

    if content != original:
        layout_changes.append(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print(f"[LAYOUT] Processed {len(layout_changes)} files, {len(new_strings)} new strings so far.")

# ------------------------------------------------------------------
# 3. Process Kotlin code  (.text = "...", Toast, Dialog, etc.)
# ------------------------------------------------------------------
# We handle several patterns:
#   binding.xxx.text = "..."
#   findViewById<...>(...).text = "..."
#   Toast.makeText(..., "...", ...)
#   .setTitle("...")
#   .setMessage("...")
#   .setNegativeButtonText("...")
#
# For string literals that contain Kotlin interpolation (${...}) we SKIP
# them in this simple script because they need getString(R.string.x, args)
# refactoring which is too risky to auto-convert blindly.
# ------------------------------------------------------------------

kt_files = []
for root, _, files in os.walk(JAVA_DIR):
    for fname in files:
        if fname.endswith(".kt"):
            kt_files.append(os.path.join(root, fname))

code_patterns = [
    # binding.xxx.text = "..."
    (re.compile(r'(\b[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\.text\s*=\s*)"([^"]*)"'),
     "kt_text"),
    # findViewById<...>(...).text = "..."
    (re.compile(r'(findViewById<[^>]+>\([^)]+\)\.text\s*=\s*)"([^"]*)"'),
     "kt_text2"),
    # Toast.makeText(..., "...", ...)
    (re.compile(r'(Toast\.makeText\([^,]+,\s*)"([^"]*)"(\s*,)'),
     "toast"),
    # .setTitle("...")
    (re.compile(r'(\.setTitle\(\s*)"([^"]*)"(\s*\))'),
     "title"),
    # .setMessage("...")
    (re.compile(r'(\.setMessage\(\s*)"([^"]*)"(\s*\))'),
     "msg"),
    # .setNegativeButtonText("...")
    (re.compile(r'(\.setNegativeButtonText\(\s*)"([^"]*)"(\s*\))'),
     "negbtn"),
]

skipped_interpolated = []

for path in kt_files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    prefix = os.path.basename(path).replace(".kt", "")

    for pat, ptype in code_patterns:
        matches = list(pat.finditer(content))
        for m in reversed(matches):
            before, text = m.group(1), m.group(2)
            after = m.group(3) if len(m.groups()) > 2 else ""
            # Skip if it contains any Kotlin string interpolation ($var or ${expr})
            if "$" in text:
                skipped_interpolated.append((path, text))
                continue
            if text.startswith("@string/"):
                continue
            if not text.strip():
                continue
            # Skip very short pure symbols / numbers that are likely not UI text
            if re.fullmatch(r"[\d\s\W]+", text) and len(text) <= 3:
                continue

            name = make_name(text, prefix, existing_names, new_name_set)
            if name is None:
                continue
            if text not in val2name and text not in new_strings:
                new_strings[text] = name
                new_name_set.add(name)
            else:
                name = val2name.get(text, new_strings.get(text, name))

            # Build replacement based on pattern type
            if ptype in ("kt_text", "kt_text2"):
                repl = f'{before}getString(R.string.{name})'
            elif ptype == "toast":
                repl = f'{before}getString(R.string.{name}){after}'
            elif ptype in ("title", "msg", "negbtn"):
                repl = f'{before}getString(R.string.{name}){after}'
            else:
                repl = m.group(0)

            content = content[:m.start()] + repl + content[m.end():]

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print(f"[CODE]   Processed {len(kt_files)} Kotlin files.")
print(f"[CODE]   Skipped {len(skipped_interpolated)} interpolated strings (need manual args).")

# ------------------------------------------------------------------
# 4. Insert new strings into TR strings.xml
# ------------------------------------------------------------------
if new_strings:
    insert_lines = "\n".join(
        f'    <string name="{name}">{value}</string>'
        for value, name in new_strings.items()
    )
    tr_content = tr_content.replace("</resources>", insert_lines + "\n</resources>")
    with open(STRINGS_TR, "w", encoding="utf-8") as f:
        f.write(tr_content)
    print(f"[TR]     Inserted {len(new_strings)} new strings into {STRINGS_TR}")

# ------------------------------------------------------------------
# 5. Insert same strings into EN strings.xml (as placeholders)
# ------------------------------------------------------------------
if new_strings:
    en_insert = "\n".join(
        f'    <string name="{name}">{value}</string>'
        for value, name in new_strings.items()
    )
    en_content = en_content.replace("</resources>", en_insert + "\n</resources>")
    with open(STRINGS_EN, "w", encoding="utf-8") as f:
        f.write(en_content)
    print(f"[EN]     Inserted {len(new_strings)} placeholder strings into {STRINGS_EN}")
    print("[WARN]   Please review EN translations manually!")

if skipped_interpolated:
    print("\n[INFO]   The following interpolated strings need manual conversion to getString(R.string.x, args):")
    for path, text in skipped_interpolated[:30]:
        print(f"         {path}: \"{text}\"")
    if len(skipped_interpolated) > 30:
        print(f"         ... and {len(skipped_interpolated)-30} more")
