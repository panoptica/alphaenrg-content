#!/bin/bash
# Fix SSH access to Mac Mini via Tailscale

echo "🔧 Troubleshooting Tailscale SSH access..."

TAILSCALE_IP="100.97.28.29"
LOCAL_IP="192.168.154.44"
USER="macmini"

echo "1. Testing local network SSH first..."
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $USER@$LOCAL_IP 'echo "Local SSH works"'; then
    echo "✅ Local SSH working"
    
    echo "2. Enabling SSH via local connection..."
    ssh -o StrictHostKeyChecking=no $USER@$LOCAL_IP << 'EOF'
        echo "Checking SSH service status..."
        if sudo systemctl is-active --quiet ssh 2>/dev/null; then
            echo "✅ SSH service is running"
        elif launchctl list | grep -q ssh; then
            echo "✅ SSH service is running (launchd)"
        else
            echo "🔧 Enabling SSH service..."
            # On macOS, enable Remote Login
            sudo systemsetup -setremotelogin on
            echo "✅ SSH enabled"
        fi
        
        echo "Checking Tailscale SSH settings..."
        tailscale status --peers
        
        echo "Testing Tailscale IP from inside Mac Mini..."
        tailscale ip -4
EOF
    
    echo "3. Testing Tailscale connection again..."
    sleep 3
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $USER@$TAILSCALE_IP 'echo "🦀 Tailscale SSH works!"'; then
        echo "✅ Tailscale SSH connection successful!"
    else
        echo "❌ Still can't connect via Tailscale"
        echo ""
        echo "Manual steps needed:"
        echo "1. SSH locally: ssh $USER@$LOCAL_IP"
        echo "2. Enable Remote Login: sudo systemsetup -setremotelogin on"
        echo "3. Check Tailscale: tailscale status"
    fi
    
else
    echo "❌ Local SSH also failing"
    echo ""
    echo "Need to check:"
    echo "1. Mac Mini is actually on 192.168.154.44"
    echo "2. SSH service is running"
    echo "3. Username/password are correct"
fi