#!/bin/bash
# wiki-post-commit.sh — Leaves a marker for the proactive wiki manager.
# This hook is symlinked into multiple git repos.
# On every commit, it appends a line to the marker file so kimi-cli
# can ask "wiki güncelleyelim mi?" on the next session.
#
# KURAL: Eğer commit mesajı "docs(wiki):" ile başlıyorsa, bu zaten bir
# wiki ingest/cleanup commit'idir — tekrar marker'a yazma. Aksi halde
# sonsuz döngü oluşur.
#
# YENI: .pending otomatik olarak ayrı bir commit olarak atilir.
# Böylece kullanıcı ekstra adım atmak zorunda kalmaz,
# ve .pending GitHub'a otomatik gider (cross-machine sync).

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

# Otomatik olarak ayrı bir commit at — .pending GitHub'a gitsin
# Bu commit "docs(wiki):" ile başladığı için post-commit hook bunu atlar
# (sonsuz döngü oluşmaz)
cd "$REPO_ROOT" || exit 0
git add "$MARKER" || true
git commit --no-verify -m "docs(wiki): auto-sync pending marker" --quiet || true
