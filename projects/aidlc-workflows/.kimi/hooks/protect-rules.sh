#!/bin/bash
# PreToolUse hook: Protect aws-aidlc-rules/ and aws-aidlc-rule-details/ from
# renames, moves, or deletions. Expects JSON context on stdin.
# Exit 0 = allow.
# Exit 2 = block and feed reason back to LLM.

set -euo pipefail

read -r JSON
FILE=$(echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")
TOOL=$(echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))")

# Check if the target file lives inside the protected directories.
if echo "$FILE" | grep -qE '(aws-aidlc-rules/|aws-aidlc-rule-details/)'; then
    # Block renames/moves/deletions of existing rule files.
    # Allow writes to existing files (content updates) and creation of new files.
    if [[ "$TOOL" == "Shell" ]]; then
        CMD=$(echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))")
        if echo "$CMD" | grep -qE '\b(mv|rm|rmdir|git mv|git rm)\b'; then
            echo "Error: Renaming, moving, or deleting files under aws-aidlc-rules/ or aws-aidlc-rule-details/ is not allowed. These paths are part of the public contract." >&2
            exit 2
        fi
    fi
fi

exit 0
