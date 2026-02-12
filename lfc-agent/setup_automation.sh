#!/bin/bash
# Setup automation on Mac Mini

echo "🔴 Setting up LFC Agent automation..."

# Update requirements
cd ~/lfc-agent
source venv/bin/activate

# Install Playwright if not already installed
pip install playwright
playwright install chromium

# Test the automation
echo "🧪 Testing automation (dry run)..."
python src/automation/scheduler.py

echo "✅ Automation setup complete!"
echo ""
echo "To schedule posts with OpenClaw cron:"
echo "1. Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env"
echo "2. Run: python scripts/schedule_posts.py"