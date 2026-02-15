# HEARTBEAT.md — Proactive Checks

## Quick Checks (rotate through these)
1. **Workspace sync** — run `scripts/sync-workspace-to-macmini.sh` to push core files to Mac Mini
2. **Git status** — any uncommitted work in workspace? Push if clean.
3. **Memory maintenance** — scan recent memory/*.md files, update MEMORY.md if stale.
4. **Mac Mini ping** — `ssh 100.87.48.20 'uptime && pgrep -f openclaw | head -1'`

## Rules
- Late night (23:00-07:00 GMT): HEARTBEAT_OK unless urgent
- Nothing new since last check: HEARTBEAT_OK
- Do ONE check per heartbeat, rotate through the list
- Track last check in memory/heartbeat-state.json
- Workspace sync should run at least once per day

## If nothing to check: HEARTBEAT_OK
