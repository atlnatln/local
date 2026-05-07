#!/bin/bash
# wiki-post-commit.sh — Leaves a marker for the proactive wiki manager.
# This hook is symlinked into multiple git repos.
# On every commit, it appends a line to the marker file so kimi-cli
# can ask "wiki güncelleyelim mi?" on the next session.
#
# KURAL: Eğer commit mesajı "docs(wiki):" ile başlıyorsa, bu zaten bir
# wiki ingest/cleanup commit'idir — tekrar marker'a yazma. Aksi halde
# sonsuz döngü oluşur (ingest commit'i → marker → sonraki session ingest → ...)

REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%s)
DATE=$(date '+%Y-%m-%d %H:%M')

# Eğer bu commit zaten bir wiki ingest/cleanup ise atla
if echo "$COMMIT_MSG" | grep -qE "^docs\(wiki\):"; then
    exit 0
fi

# Detect changed files in this commit
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD | tr '\n' ',')

# Marker file (persistent across reboots)
MARKER="/home/akn/local/wiki/.pending"

# Append one line per commit
echo "${DATE}|${COMMIT_SHA}|${REPO_NAME}|${CHANGED_FILES}" >> "$MARKER"
