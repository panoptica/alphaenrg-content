#!/bin/bash

# AlphaENRG Multi-Platform Automation Installation Script

echo "🚀 Installing AlphaENRG Multi-Platform Automation..."
echo "======================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the energy-agent directory"
    exit 1
fi

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install automation requirements
echo "📥 Installing automation dependencies..."
pip install -r requirements_automation.txt

# Install ChromeDriver for Substack automation
echo "🌐 Installing ChromeDriver..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        echo "📦 Installing ChromeDriver via Homebrew..."
        brew install --cask chromedriver 2>/dev/null || echo "⚠️ ChromeDriver may already be installed"
    else
        echo "⚠️ Homebrew not found. Please install ChromeDriver manually:"
        echo "   https://chromedriver.chromium.org/downloads"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "📦 Installing ChromeDriver for Linux..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y chromium-chromedriver
    else
        echo "⚠️ apt-get not found. Please install ChromeDriver manually:"
        echo "   https://chromedriver.chromium.org/downloads"
    fi
else
    echo "⚠️ Unsupported OS. Please install ChromeDriver manually:"
    echo "   https://chromedriver.chromium.org/downloads"
fi

# Make scripts executable
echo "🔒 Making scripts executable..."
chmod +x setup_automation.py
chmod +x multi_platform_publisher.py
chmod +x main_with_publishing.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run setup: python setup_automation.py"
echo "2. Configure credentials in .env file"
echo "3. Test posting: python multi_platform_publisher.py test"
echo ""
echo "📚 Available scripts:"
echo "  setup_automation.py          - Configure all API credentials"
echo "  multi_platform_publisher.py  - Test individual platform publishing"  
echo "  main_with_publishing.py      - Full intelligence collection + publishing"
echo "  facebook_integration.py      - Facebook-only publishing"
echo "  substack_integration.py      - Substack-only publishing"
echo ""