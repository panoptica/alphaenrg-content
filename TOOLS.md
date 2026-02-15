# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

### Image Generation
- **Grok Imagine** (xAI Pro sub) — primary
- **Gemini Imagen** (Google Pro sub) — secondary
- **NO local image gen** — ComfyUI was evaluated and rejected (too heavy for 16GB Mac Mini)
- Cloud APIs only. This is a locked decision.

### X/Twitter API
- Bearer token + full OAuth 1.0a creds in Mac Mini's energy-agent/.env
- Use bearer token for search, OAuth for posting (@AlphaENRG)
- X API v2 endpoints — DON'T scrape x.com, use the API

---

Add whatever helps you do your job. This is your cheat sheet.

## Last Synced
<!-- Updated automatically by scripts/sync-workspace-to-macmini.sh or heartbeat -->
**2026-02-15 15:34 GMT** — MacBook Air → Mac Mini
