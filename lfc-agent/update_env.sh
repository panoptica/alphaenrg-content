#!/bin/bash
# Update .env with Instagram credentials

cd ~/lfc-agent

# Add Instagram credentials to .env
echo "" >> .env
echo "# Instagram automation" >> .env  
echo "INSTAGRAM_USERNAME=YNWA4Reds" >> .env
echo "INSTAGRAM_PASSWORD=neqzid-bazsif-7gAzsy" >> .env

echo "✅ Instagram credentials added to .env"

# Test basic connection
source venv/bin/activate
echo "🧪 Testing automation framework..."
python -c "
import sys
sys.path.append('src')
from automation.instagram_poster import InstagramPoster
print('✅ Automation modules ready')
"