#!/bin/bash
# wiki-post-commit.sh — Leaves a marker for the proactive wiki manager.
# This hook is symlinked into multiple git repos.
# On every commit, it appends a line to the marker file so kimi-cli
# can ask "wiki güncelleyelim mi?" on the next session.

REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
COMMIT_SHA=$(git rev-parse HEAD)
DATE=$(date '+%Y-%m-%d %H:%M')

# Detect changed files in this commit
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD | tr '\n' ',')

# Marker file (persistent across reboots)
MARKER="/home/akn/local/wiki/.pending"

# Append one line per commit
echo "${DATE}|${COMMIT_SHA}|${REPO_NAME}|${CHANGED_FILES}" >> "$MARKER"
