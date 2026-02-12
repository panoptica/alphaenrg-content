#!/bin/bash
# Commands to run ON THE MAC MINI to fix Tailscale SSH

echo "🔧 Tailscale SSH Fix Commands"
echo "Run these ON THE MAC MINI (ssh macmini@192.168.154.44 first)"
echo "============================================================="

cat << 'EOF'

# 1. Enable system SSH (Remote Login)
echo "1. Enabling SSH..."
sudo systemsetup -setremotelogin on
sudo systemsetup -getremotelogin  # Should show "Remote Login: On"

# 2. Check current Tailscale status
echo "2. Checking Tailscale..."
tailscale status
tailscale ip -4  # Should show 100.97.28.29

# 3. Fix the GUI app limitation - install CLI Tailscale
echo "3. Installing CLI Tailscale..."

# Stop GUI version
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale down || true

# Install CLI version via Homebrew
if ! command -v /opt/homebrew/bin/tailscale &> /dev/null; then
    echo "Installing Tailscale CLI..."
    brew install tailscale
fi

# Install system daemon
sudo /opt/homebrew/bin/tailscaled install-system-daemon

# Connect with SSH enabled
sudo /opt/homebrew/bin/tailscale up --ssh --accept-routes --hostname="macmini-m4"

echo "4. Testing SSH over Tailscale..."
# Test locally first
sleep 5
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no macmini@100.97.28.29 'echo "✅ Tailscale SSH working!"' || echo "❌ Still not working"

echo ""
echo "5. If still failing, check firewall..."
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/sbin/sshd
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/sbin/sshd

echo ""
echo "✅ Tailscale SSH should now work from external machines!"
echo "Test from MacBook Air: ssh macmini@100.97.28.29"

EOF

echo ""
echo "🚀 Next: After fixing SSH, we can deploy optimizations with 24/7 access!"