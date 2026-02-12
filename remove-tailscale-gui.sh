#!/bin/bash
# Complete Tailscale GUI App Removal

echo "🗑️  Completely removing Tailscale GUI app..."

# 1. Stop the app and daemon
echo "1. Stopping Tailscale services..."
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale down || true
killall Tailscale 2>/dev/null || true

# 2. Remove the app bundle
echo "2. Removing app bundle..."
sudo rm -rf /Applications/Tailscale.app

# 3. Remove LaunchAgents/LaunchDaemons
echo "3. Removing launch services..."
sudo launchctl unload /Library/LaunchDaemons/com.tailscale.tailscaled.plist 2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.tailscale.ipn.macos.login-item.plist 2>/dev/null || true

sudo rm -f /Library/LaunchDaemons/com.tailscale.tailscaled.plist
rm -f ~/Library/LaunchAgents/com.tailscale.ipn.macos.login-item.plist

# 4. Remove configuration and data
echo "4. Removing configuration files..."
sudo rm -rf /var/lib/tailscale
rm -rf ~/Library/Containers/io.tailscale.ipn.macos
rm -rf ~/Library/Containers/io.tailscale.ipn.macos.network-extension
rm -rf ~/Library/Application\ Support/Tailscale
rm -rf ~/Library/Caches/io.tailscale.ipn.macos
rm -rf ~/Library/Preferences/io.tailscale.ipn.macos.plist

# 5. Remove system extensions
echo "5. Removing system extensions..."
# List current extensions
echo "Current system extensions:"
systemextensionsctl list

echo ""
echo "To remove Tailscale system extensions manually:"
echo "  System Preferences → Privacy & Security → Extensions"
echo "  Find Tailscale entries and remove them"

# 6. Remove any remaining processes
sudo pkill -f tailscale 2>/dev/null || true
sudo pkill -f tailscaled 2>/dev/null || true

echo ""
echo "✅ Tailscale GUI app removal complete!"
echo ""
echo "🚀 Now install CLI version:"
echo "  brew install tailscale"
echo "  sudo \$(brew --prefix)/bin/tailscaled install-system-daemon"
echo "  sudo \$(brew --prefix)/bin/tailscale up --ssh --accept-routes"