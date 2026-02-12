#!/bin/bash
# Setup Tailscale for permanent connection

echo "🔗 Setting up Tailscale for permanent connection..."

MAC_MINI="192.168.154.44"
USER="macmini"
PASS="!1Longmore@@"

echo "Installing and configuring Tailscale on Mac Mini..."

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$MAC_MINI" << 'EOF'
    echo "1. Checking if Tailscale is installed..."
    
    if command -v tailscale &> /dev/null; then
        echo "✅ Tailscale already installed"
        tailscale status
    else
        echo "Installing Tailscale..."
        
        # Download and install Tailscale
        curl -fsSL https://pkgs.tailscale.com/stable/tailscale_1.78.3_amd64.tgz | tar xzf - --strip-components=1
        sudo cp tailscale tailscaled /usr/local/bin/
        
        # Or use homebrew if available
        if command -v brew &> /dev/null; then
            echo "Installing via Homebrew..."
            brew install tailscale
        fi
    fi
    
    echo ""
    echo "2. Current Tailscale status:"
    if command -v tailscale &> /dev/null; then
        tailscale status || echo "Tailscale not connected"
        echo ""
        echo "To connect Tailscale:"
        echo "  sudo tailscale up"
        echo ""
        echo "This will give you a URL to authorize the device."
    else
        echo "❌ Tailscale installation failed"
        echo ""
        echo "Manual installation:"
        echo "  1. Visit: https://tailscale.com/download/mac"
        echo "  2. Download and install Tailscale"
        echo "  3. Run: sudo tailscale up"
    fi
EOF

echo ""
echo "3. Next steps for permanent connection:"
echo ""
echo "Option A - Tailscale (Recommended):"
echo "  1. SSH to Mac Mini: ssh $USER@$MAC_MINI"  
echo "  2. Connect Tailscale: sudo tailscale up"
echo "  3. Follow auth URL to connect device"
echo "  4. Share the Tailscale IP with me"
echo ""
echo "Option B - Alternative methods:"
echo "  See permanent-connection-setup.md for other options"