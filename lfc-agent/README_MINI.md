# LFC Agent - Mac Mini Operation Guide

## Quick Start

1. **Run setup** (one-time):
```bash
cd ~/lfc-agent
chmod +x mini_setup.sh
./mini_setup.sh
```

2. **Test posting** (dry run):
```bash
source venv/bin/activate
python src/automation/scheduler.py
```

3. **Schedule City campaign**:
```bash
python scripts/schedule_posts.py
```

## Commands

### Content Generation
```bash
# Test single post
python demo_content.py

# Generate full campaign
python src/automation/scheduler.py

# Check next fixture
python src/fixtures/monitor.py
```

### Posting
```bash
# Dry run (test only)
python src/automation/scheduler.py

# Live posting (when ready)
# Edit scheduler.py: dry_run=False
```

### Scheduling
```bash
# Schedule with OpenClaw cron
python scripts/schedule_posts.py

# Check scheduled jobs
openclaw cron list

# Run job manually
openclaw cron run <jobId>
```

## File Structure
```
~/lfc-agent/
├── src/
│   ├── automation/          # Browser posting
│   ├── fixtures/            # Match detection
│   ├── generation/          # Caption creation
│   ├── visuals/            # Image creation
│   └── publishing/         # API posting (backup)
├── assets/                 # Generated images
├── db/                    # Database setup
└── scripts/              # Utility scripts
```

## Configuration

**.env file:**
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
INSTAGRAM_USERNAME=YNWA4Reds
INSTAGRAM_PASSWORD=...

# Database
DATABASE_URL=postgresql://macmini@localhost:5432/lfc_agent

# Optional
FACEBOOK_ACCESS_TOKEN=...  # For API posting
INSTAGRAM_ACCOUNT_ID=...   # For API posting
```

## Troubleshooting

**Browser issues:**
- Check Instagram login on Safari first
- Run with headless=False for debugging
- Clear browser cache if login fails

**Content generation slow:**
- Anthropic API calls take 5-10 seconds each
- Full campaign (7 posts) takes ~2 minutes

**Scheduling:**
- OpenClaw cron jobs show in `openclaw cron list`
- Jobs trigger system events, not direct posting
- For automatic posting, use browser automation

## City Match Campaign

**Timeline:** Fri-Sun before LFC vs City
**Posts:** 7 total (2 Fri, 3 Sat, 2 Sun)
**Content:** Stats, atmosphere, banter, famous reds

**Ready to launch!** 🔴