#!/bin/bash
# Executable script to fix Tailscale SSH on Mac Mini

echo "🔧 Fixing Tailscale SSH on Mac Mini..."

# 1. Enable system SSH
echo "1. Enabling SSH..."
sudo systemsetup -setremotelogin on
sudo systemsetup -getremotelogin

# 2. Check current Tailscale status
echo "2. Checking Tailscale..."
tailscale status
tailscale ip -4

# 3. Fix the GUI app limitation - install CLI Tailscale
echo "3. Installing CLI Tailscale..."

# Stop GUI version
echo "Stopping GUI Tailscale..."
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale down || true

# Install CLI version via Homebrew
if ! command -v /opt/homebrew/bin/tailscale &> /dev/null; then
    echo "Installing Tailscale CLI..."
    brew install tailscale
else
    echo "✅ Tailscale CLI already installed"
fi

# Install system daemon
echo "Installing system daemon..."
sudo /opt/homebrew/bin/tailscaled install-system-daemon

# Connect with SSH enabled
echo "Connecting with SSH enabled..."
sudo /opt/homebrew/bin/tailscale up --ssh --accept-routes --hostname="macmini-m4"

echo "4. Testing SSH over Tailscale..."
sleep 10
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no macmini@100.97.28.29 'echo "✅ Tailscale SSH working!"'; then
    echo "✅ SUCCESS! Tailscale SSH is working!"
else
    echo "❌ Still not working, checking firewall..."
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/sbin/sshd
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/sbin/sshd
    
    echo "Testing again after firewall fix..."
    sleep 5
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no macmini@100.97.28.29 'echo "✅ Tailscale SSH working!"' || echo "❌ Still failing - may need manual intervention"
fi

echo ""
echo "✅ Tailscale SSH fix complete!"
echo "Test from MacBook Air: ssh macmini@100.97.28.29"