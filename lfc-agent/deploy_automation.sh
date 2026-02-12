#!/bin/bash
# Complete automation deployment script

echo "🔴 LFC AGENT - AUTOMATION DEPLOYMENT"
echo "======================================"

# Rsync all files to Mini
echo "📂 Syncing files to Mac Mini..."
rsync -avz --progress lfc-agent/ macmini@192.168.154.44:~/lfc-agent/

# SSH and complete setup
ssh macmini@192.168.154.44 << 'EOF'
cd ~/lfc-agent

echo "⚙️  Updating environment..."
# Add Instagram credentials
echo "" >> .env
echo "# Instagram automation" >> .env  
echo "INSTAGRAM_USERNAME=YNWA4Reds" >> .env
echo "INSTAGRAM_PASSWORD=neqzid-bazsif-7gAzsy" >> .env

echo "📦 Installing Playwright..."
source venv/bin/activate
pip install playwright
playwright install chromium

echo "🧪 Testing automation (dry run)..."
python -c "
import sys
import asyncio
sys.path.append('src')
from automation.scheduler import LFCContentScheduler

async def test():
    scheduler = LFCContentScheduler()
    print('✅ Content scheduler ready')
    
    # Test content generation only
    fixture = scheduler.monitor.get_next_fixture()
    print(f'📅 Next fixture: LFC vs {fixture[\"opponent\"]}')
    
asyncio.run(test())
"

echo "✅ Automation deployment complete!"
echo "🔥 Ready to schedule City match campaign!"
EOF