#!/bin/bash
# Enable OpenClaw Gateway network access

echo "🦀 Enabling OpenClaw Gateway network binding..."

MAC_MINI="192.168.154.44"
USER="macmini"
PASS="!1Longmore@@"

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$MAC_MINI" << 'EOF'
    # Check if OpenClaw is installed
    if ! command -v openclaw &> /dev/null; then
        echo "❌ OpenClaw not found on Mac Mini"
        echo "Need to install OpenClaw on Mac Mini first"
        exit 1
    fi
    
    echo "Backing up current OpenClaw config..."
    cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup
    
    echo "Enabling network gateway binding..."
    # This would modify the config to bind to 0.0.0.0 instead of loopback
    # But we need the actual config modification logic here
    
    echo "Manual step needed:"
    echo "Edit ~/.openclaw/openclaw.json"
    echo "Change: \"bind\": \"loopback\""  
    echo "To:     \"bind\": \"0.0.0.0\""
    echo "Then:   openclaw gateway restart"
EOF

echo ""
echo "Alternative: Just use simple Tailscale connection"
echo "Run: sudo tailscale up --accept-routes"
echo "Then share the Tailscale IP (100.x.x.x) with me"