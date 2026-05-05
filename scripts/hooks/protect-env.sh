#!/usr/bin/env bash
read -r JSON
FILE=$(echo "$JSON" | jq -r '.tool_input.path')
if [ -z "$FILE" ] || [ "$FILE" = "null" ]; then
    echo "Warning: Could not extract path from tool input" >&2
    exit 0
fi
echo "$FILE" | grep -qE '\.env$|\.env\.local$' && {
    echo "Error: Direct modification of .env files is not allowed. Use .env.example instead." >&2
    exit 2
}
exit 0
