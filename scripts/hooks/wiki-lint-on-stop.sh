#!/bin/bash
# wiki-lint-on-stop.sh — Session sonunda wiki lint çalıştır

# Sessizce çalıştır, hata olursa session'ı engelleme
~/.kimi/skills/local-wiki/scripts/wiki_lint.py /home/akn/local/wiki > /dev/null 2>&1 || true
exit 0
