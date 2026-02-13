#!/bin/bash

SOURCE_DIR="/Users/macmini/.openclaw/workspace/"
DEST_USER="macmini"
DEST_HOST="100.98.31.10"
DEST_DIR="/Users/macmini/.openclaw/workspace/"

# Use rsync over SSH to synchronize files
# -a: archive mode (recursively, preserve permissions, etc.)
# -v: verbose
# -z: compress file data during the transfer
# --delete: delete extraneous files from dest dir (not in source)
# --exclude: exclude specified files/directories

rsync -avz --delete \
  --exclude ".git/" \
  --exclude "node_modules/" \
  --exclude "*.log" \
  --exclude "tmp/" \
  --exclude "__pycache__/" \
  "$SOURCE_DIR" "$DEST_USER@$DEST_HOST:$DEST_DIR"

# Update TOOLS.md with the current sync timestamp
CURRENT_TIME=$(date -u +"%Y-%m-%d %H:%M GMT")
perl -i -pe "s/^# Last Synced.*$/# Last Synced\n<!-- Updated automatically by scripts\/sync-workspace-to-macmini.sh or heartbeat -->\n**$CURRENT_TIME** — MacBook Air → Mac Mini/" TOOLS.md
