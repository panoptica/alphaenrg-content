#!/bin/bash
# Setup script to run directly on Mac Mini
# Downloads and configures LFC Agent for local operation

echo "🔴 LFC AGENT - MAC MINI SETUP"
echo "============================="

cd ~/lfc-agent

# Update .env with Instagram credentials
echo "⚙️  Adding Instagram credentials..."
cat >> .env << 'EOF'

# Instagram automation
INSTAGRAM_USERNAME=YNWA4Reds
INSTAGRAM_PASSWORD=neqzid-bazsif-7gAzsy
EOF

# Install Playwright
echo "📦 Installing browser automation..."
source venv/bin/activate
pip install playwright
playwright install chromium

# Test the system
echo "🧪 Testing automation framework..."
python -c "
import sys
import asyncio
sys.path.append('src')

print('Testing imports...')
from fixtures.monitor import FixtureMonitor
from generation.generator import generate_variants
from visuals.compositor import create_stat_graphic
print('✅ Core modules working')

try:
    from automation.instagram_poster import InstagramPoster
    from automation.scheduler import LFCContentScheduler
    print('✅ Automation modules working')
except ImportError as e:
    print(f'⚠️  Automation modules need sync: {e}')

# Test content generation
print('\\n🎨 Testing content generation...')
monitor = FixtureMonitor()
fixture = monitor.get_next_fixture()
print(f'📅 Next fixture: LFC vs {fixture[\"opponent\"]} in {fixture[\"days_until\"]} days')

if fixture['days_until'] <= 7:
    print('✅ Content generation will be triggered')
    schedule = monitor.get_content_schedule(fixture)
    print(f'📋 {len(schedule)} posts scheduled')
else:
    print('⏸️  Too early for content generation')
"

echo ""
echo "✅ Mac Mini setup complete!"
echo ""
echo "🔥 NEXT STEPS:"
echo "1. Test posting: python src/automation/scheduler.py"
echo "2. Schedule campaign: python scripts/schedule_posts.py"
echo "3. Monitor: tail -f logs/lfc-agent.log"