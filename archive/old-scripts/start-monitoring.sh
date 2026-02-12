#!/bin/bash
# Start Empire Monitoring on Mac Mini M4

echo "🦀 Starting Empire Monitoring System..."

MAC_MINI="192.168.154.44"
USER="macmini" 
PASS="!1Longmore@@"

echo "1. Starting monitoring daemon on Mac Mini..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$MAC_MINI" << 'EOF'
    cd empire-heartbeat
    
    # Kill any existing monitoring
    pkill -f "monitor.py" 2>/dev/null || true
    pkill -f "dashboard.py" 2>/dev/null || true
    
    # Start fresh monitoring in background
    echo "Starting monitoring daemon..."
    nohup python3 monitor.py > monitor.log 2>&1 &
    
    # Start web dashboard
    echo "Starting web dashboard..."
    nohup python3 dashboard.py > dashboard.log 2>&1 &
    
    sleep 3
    
    # Check status
    echo "Empire monitoring status:"
    ./status.sh
    
    echo ""
    echo "🌐 Web dashboard: http://192.168.154.44:8888"
EOF

echo ""
echo "2. Checking monitoring from local side..."
sleep 5

# Try to access the dashboard API
echo "Testing web dashboard API..."
if curl -s "http://$MAC_MINI:8888/api/status" > /dev/null 2>&1; then
    echo "✅ Web dashboard accessible at http://$MAC_MINI:8888"
else
    echo "⚠️  Web dashboard not yet accessible (may need a moment to start)"
fi

echo ""
echo "✅ Monitoring system started!"
echo ""
echo "🔧 Commands to check status:"
echo "  curl http://$MAC_MINI:8888/api/status | jq"
echo "  ssh $USER@$MAC_MINI 'cd empire-heartbeat && ./status.sh'"
echo ""
echo "🌐 Web Interface: http://$MAC_MINI:8888"