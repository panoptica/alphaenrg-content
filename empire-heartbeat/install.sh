#!/bin/bash
# Empire Heartbeat Monitor Installation

echo "🦀 Installing Empire Heartbeat Monitor..."

# Check dependencies
echo "Checking dependencies..."
for cmd in python3 sshpass ping; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ Missing: $cmd"
        if [[ "$cmd" == "sshpass" ]]; then
            echo "   Install: brew install sshpass  (or apt-get install sshpass)"
        fi
        exit 1
    else
        echo "✅ Found: $cmd"
    fi
done

# Install Python requirements
echo "Installing Python requirements..."
pip3 install requests > /dev/null 2>&1 || echo "⚠️  requests already installed"

# Make executable
chmod +x monitor.py
chmod +x status.sh

# Create systemd service (Linux)
if command -v systemctl &> /dev/null; then
    echo "Creating systemd service..."
    
    cat > empire-heartbeat.service << EOF
[Unit]
Description=Empire Heartbeat Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) $(pwd)/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "To enable auto-start:"
    echo "  sudo cp empire-heartbeat.service /etc/systemd/system/"
    echo "  sudo systemctl enable empire-heartbeat"
    echo "  sudo systemctl start empire-heartbeat"
fi

# Create launchd service (macOS)
if command -v launchctl &> /dev/null; then
    echo "Creating launchd service..."
    
    PLIST_PATH="$HOME/Library/LaunchAgents/com.openclaw.empire-heartbeat.plist"
    
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.empire-heartbeat</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$(pwd)/monitor.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$(pwd)/monitor.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/monitor.error.log</string>
</dict>
</plist>
EOF

    echo "To enable auto-start on macOS:"
    echo "  launchctl load \"$PLIST_PATH\""
    echo "  launchctl start com.openclaw.empire-heartbeat"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "  ./monitor.py                 # Run once"
echo "  ./status.sh                  # Check current status"
echo "  ./monitor.py &              # Run in background"
echo ""
echo "📊 Files created:"
echo "  empire-state.json           # Monitoring state"
echo "  monitor.log                 # Output log (if using service)"