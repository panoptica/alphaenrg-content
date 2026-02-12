#!/bin/bash
cd /Users/macmini/.openclaw/workspace/energy-agent
source venv/bin/activate
python3 run_digest.py >> /Users/macmini/.openclaw/workspace/energy-agent/logs/cron.log 2>&1
