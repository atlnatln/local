#!/bin/bash
# PostToolUse hook: Auto-run markdown lint after .md files are modified.
# Expects JSON context on stdin with tool_input.file_path.
# Exit 0 = allow (with optional stdout feedback).
# Exit 2 = block operation and feed stderr back to LLM.

set -euo pipefail

read -r JSON
FILE=$(echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")

if [[ "$FILE" == *.md ]]; then
    # Run markdownlint on the specific file; if it fails, report but do NOT block.
    # Blocking would interrupt the agent's workflow; feedback is usually enough.
    if ! npx markdownlint-cli2 "$FILE" 2>/dev/null; then
        echo "⚠️ Markdown lint issues detected in $FILE. Run \`npx markdownlint-cli2 --fix '$FILE'\` to auto-fix."
    fi
fi

exit 0
