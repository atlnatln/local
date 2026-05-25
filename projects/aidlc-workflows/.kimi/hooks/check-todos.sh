#!/bin/bash
# Stop hook: Warn if incomplete todos or running background tasks exist.
# Expects JSON context on stdin (though Stop event context is minimal).
# Exit 0 = allow (with optional stdout feedback to LLM context).

set -euo pipefail

# Check for running background shell/agent tasks via ps.
# This is a heuristic; precise checking depends on session state.
if pgrep -af "kimi.*background" >/dev/null 2>&1 || pgrep -af "uv run pytest" >/dev/null 2>&1; then
    echo "⚠️ Background tasks appear to be running. Consider checking their status before ending the session."
fi

# Reminder about todo list.
echo "💡 Reminder: If you have incomplete todos, use the SetTodoList tool to update or clear them before finishing."

exit 0
