#!/bin/bash
# Domain Guard — Cross-domain write protection for AI-DLC multi-agent workflow
# Usage: PreToolUse hook for WriteFile/StrReplaceFile
# Exit 0 = allow, Exit 2 = block

read JSON
FILE=$(echo "$JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")

# Domain mapping: which paths belong to which agent scope
# Note: construction-coder has access to ALL src/ paths (full-stack)
case "$FILE" in
  src/*|infrastructure/*|tests/*)
    ALLOWED="src/|infrastructure/|tests/"
    ;;
  aidlc-docs/inception/*)
    ALLOWED="aidlc-docs/inception/"
    ;;
  aidlc-docs/construction/*/code/*)
    ALLOWED="aidlc-docs/construction/.*/code/"
    ;;
  aidlc-docs/construction/build-and-test/*)
    ALLOWED="aidlc-docs/construction/build-and-test/"
    ;;
  aidlc-docs/operations/*)
    ALLOWED="aidlc-docs/operations/"
    ;;
  aidlc-docs/aidlc-state.md|aidlc-docs/audit.md)
    ALLOWED="aidlc-docs/aidlc-state.md|aidlc-docs/audit.md"
    ;;
  .kimi/*)
    ALLOWED=".kimi/"
    ;;
  *)
    ALLOWED=""
    ;;
esac

if [ -n "$ALLOWED" ] && ! echo "$FILE" | grep -qE "$ALLOWED"; then
    echo "Error: Cross-domain write blocked. Cannot write to $FILE" >&2
    exit 2
fi
exit 0
