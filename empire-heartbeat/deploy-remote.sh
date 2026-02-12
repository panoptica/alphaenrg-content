#!/bin/bash
# Deploy Empire Heartbeat to Mac Mini M4 for local network monitoring

echo "🦀 Deploying Empire Heartbeat to Mac Mini M4..."

MAC_MINI="192.168.154.44"
USER="macmini"
PASS="!1Longmore@@"

echo "This will deploy the monitoring system TO the Mac Mini"
echo "so it can monitor the local network from inside your environment."
echo ""

# Test connection first
echo "Testing SSH connection..."
if sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$MAC_MINI" 'echo "Connection successful"' 2>/dev/null; then
    echo "✅ SSH connection successful"
else
    echo "❌ Cannot connect to Mac Mini via SSH"
    echo "Make sure you can run: ssh $USER@$MAC_MINI"
    exit 1
fi

echo ""
echo "Copying monitoring system to Mac Mini..."

# Create tar of monitoring system
tar -czf empire-heartbeat.tar.gz empire-heartbeat/

# Copy to Mac Mini
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no empire-heartbeat.tar.gz "$USER@$MAC_MINI:~/"

# Deploy and setup on Mac Mini  
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$MAC_MINI" << 'EOF'
    echo "Extracting monitoring system..."
    tar -xzf empire-heartbeat.tar.gz
    cd empire-heartbeat
    
    echo "Installing dependencies..."
    # Check if brew exists, install if needed
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install sshpass if needed
    if ! command -v sshpass &> /dev/null; then
        brew install sshpass
    fi
    
    # Install Python packages
    pip3 install requests || python3 -m pip install requests
    
    # Make scripts executable
    chmod +x *.py *.sh
    
    echo "✅ Empire Heartbeat deployed to Mac Mini"
    echo ""
    echo "To start monitoring:"
    echo "  ssh macmini@192.168.154.44"
    echo "  cd empire-heartbeat"
    echo "  ./monitor.py &"
    echo ""
    echo "Or install as service:"
    echo "  ./install.sh"
EOF

# Cleanup
rm empire-heartbeat.tar.gz

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🚀 Next steps:"
echo "1. SSH to Mac Mini: ssh $USER@$MAC_MINI"
echo "2. Start monitoring: cd empire-heartbeat && ./monitor.py &"
echo "3. Check status: ./status.sh"
echo "4. Web dashboard: ./dashboard.py & (then visit http://$MAC_MINI:8888)"