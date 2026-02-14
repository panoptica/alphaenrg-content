#!/bin/bash

# AlphaENRG Daily Publishing Script
# Run this daily via cron for automated intelligence publishing

cd /Users/macmini/.openclaw/workspace/energy-agent

# Activate virtual environment
source venv/bin/activate

# Run daily collection and publishing
echo "$(date): Starting AlphaENRG daily run..."
python main_with_publishing.py --mode publish

echo "$(date): AlphaENRG daily run completed."
