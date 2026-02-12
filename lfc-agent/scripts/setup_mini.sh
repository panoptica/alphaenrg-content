#!/bin/bash
# Setup script for Mac Mini
# Run after Homebrew is installed

set -e

echo "🔴 LFC Agent - Mac Mini Setup"
echo "=============================="

# Check Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install it first:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

echo "✅ Homebrew found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
brew install postgresql@15 python@3.11 ffmpeg

# Add PostgreSQL to PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# Start PostgreSQL
echo ""
echo "🐘 Starting PostgreSQL..."
brew services start postgresql@15

# Wait for PostgreSQL to start
sleep 3

# Create database and user
echo ""
echo "🗄️  Setting up database..."
createuser -s macmini 2>/dev/null || echo "User macmini already exists"
createdb lfc_agent -O macmini 2>/dev/null || echo "Database lfc_agent already exists"

# Create Python virtual environment
echo ""
echo "🐍 Setting up Python environment..."
cd ~/lfc-agent
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo ""
echo "📊 Running database migrations..."
psql -d lfc_agent -f db/init_db.sql

# Seed data
echo ""
echo "🌱 Seeding initial data..."
psql -d lfc_agent -f db/seeds/quotes.sql
psql -d lfc_agent -f db/seeds/stats.sql

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Edit .env with your API keys!"
fi

echo ""
echo "=============================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Test: python src/fixtures/monitor.py"
