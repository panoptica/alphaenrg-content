#!/bin/bash
# GitHub Integration Setup

echo "🚀 Setting up GitHub integration..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    brew install gh || echo "Please install GitHub CLI manually"
fi

# Check git config
echo "📝 Checking Git configuration..."
git config user.name >/dev/null || git config --global user.name "Matt OpenClaw"
git config user.email >/dev/null || git config --global user.email "oc@cloudmonkey.io"

# Create repository if it doesn't exist
echo "📦 Setting up repository..."
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "No GitHub remote found. Creating repository..."
    read -p "Repository name (default: openclaw-intelligence): " REPO_NAME
    REPO_NAME=${REPO_NAME:-openclaw-intelligence}
    
    # Create repo and add remote
    gh repo create "$REPO_NAME" --private --source . --remote origin --push
else
    echo "✅ GitHub remote already configured"
fi

# Set up GitHub secrets for CI
echo "🔐 Setting up GitHub secrets..."
echo "You'll need to set these manually in GitHub Settings > Secrets:"
echo "- TELEGRAM_BOT_TOKEN: (your bot token)"
echo "- TELEGRAM_CHAT_ID: 6005711731"

# Create initial commit with current state
echo "📤 Committing current state..."
git add .
git commit -m "Initial commit: OpenClaw Intelligence workspace

- Energy Intelligence Agent with Lens.org integration
- Model hierarchy: Opus > Qwen 2.5 > Llama 3
- CI/CD pipeline with automated testing
- Daily documentation updates
- Cost optimization: £50/day -> £5/day" || echo "Nothing to commit"

git push origin master 2>/dev/null || git push origin main 2>/dev/null || echo "⚠️ Push manually after setup"

echo "✅ GitHub setup complete!"
echo "🔗 Repository URL: $(git remote get-url origin 2>/dev/null || echo 'Not set')"
echo ""
echo "Next steps:"
echo "1. Go to GitHub.com > Settings > Secrets"
echo "2. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
echo "3. Enable GitHub Actions if prompted"
echo "4. Test workflow with: git push"