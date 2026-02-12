#!/bin/bash
# Publishing System Setup Script

echo "🚀 Setting up Energy Intelligence Publishing System"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Copy environment template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✏️  Edit .env with your X API credentials"
else
    echo "✅ .env already exists"
fi

# Make scripts executable
chmod +x *.py

echo ""
echo "🎯 Next Steps:"
echo "1. Get X API credentials from: https://developer.twitter.com/en/portal/dashboard"
echo "2. Edit .env file with your credentials"
echo "3. Test: python3 x-publisher.py"
echo "4. Run: python3 auto-publisher.py"
echo ""
echo "🔄 To automate daily publishing, add to crontab:"
echo "   0 9 * * * cd $(pwd) && python3 auto-publisher.py --auto"