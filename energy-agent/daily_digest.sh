#!/bin/bash
cd /Users/mattmcconnon/.openclaw/workspace/energy-agent
/opt/homebrew/bin/python3 run_digest.py >> /Users/mattmcconnon/.openclaw/workspace/energy-agent/logs/cron.log 2>&1
