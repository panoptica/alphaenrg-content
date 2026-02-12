# Publishing System Deployment Guide

## System Status (2026-02-11)

### ✅ Ready
- **Publishing Code**: X automation complete
- **Mac Mini Ollama**: Online (Tailscale 100.98.31.10:11434)
- **Energy Agent**: Daily digests working

### ⚠️ Needs Attention  
- **ComfyUI**: Offline on Mac Mini (needed for visual content)
- **Empire Monitoring**: Not installed
- **X API Credentials**: Need setup

## Deployment Steps

### 1. X API Setup (Priority 1)
Matt needs to:
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create new app/project
3. Generate Bearer Token, Consumer Keys, Access Tokens
4. Copy credentials to `publishing-system/.env`

### 2. System Health Fixes
- **ComfyUI Restart**: SSH to Mac Mini, restart ComfyUI service
  ```bash
  ssh macmini@100.98.31.10
  cd ComfyUI && source venv/bin/activate && python main.py --listen 0.0.0.0
  ```
- **Empire Monitor**: Install monitoring system for health checks

### 3. First Test Run
```bash
cd publishing-system
python3 auto-publisher.py  # Manual test
```

### 4. Automation Setup
Add to cron for daily 9 AM posts:
```bash
crontab -e
# Add: 0 9 * * * cd /Users/macmini/.openclaw/workspace/publishing-system && python3 auto-publisher.py --auto
```

## Expected Timeline
- **Today**: X API setup + first test post
- **This Week**: Daily automation + system monitoring
- **Next Week**: Substack/Medium integration

## Integration Points
- **Energy Agent**: Reads daily signals automatically  
- **Visual Content**: ComfyUI for charts/infographics (when online)
- **Analytics**: Track engagement, optimize posting times