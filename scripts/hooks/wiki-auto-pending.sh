#!/usr/bin/env bash
read -r JSON
FILE=$(echo "$JSON" | jq -r '.tool_input.path')
if [ -z "$FILE" ] || [ "$FILE" = "null" ]; then
    exit 0
fi
echo "$FILE" | grep -qE '(/wiki/|/node_modules/|/__pycache__/|/\.venv/)' && exit 0
echo "$FILE" | grep -qE '\.(md|py|js|ts|tsx|sh|yml|yaml|json|toml|conf|service|timer|html|css)$' || exit 0
REPO=$(echo "$FILE" | sed 's|/home/akn/local/||; s|/.*||')
echo "$(date '+%Y-%m-%d %H:%M')|$(git -C /home/akn/local rev-parse --short HEAD 2>/dev/null || echo 'unknown')|$REPO|$FILE" >> /home/akn/local/wiki/.pending
exit 0
