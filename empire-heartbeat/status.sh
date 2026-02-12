#!/bin/bash
# Quick Empire Status Check

echo "🦀 Empire Compute Status"
echo "=========================="
echo ""

# Check if monitor is running
if pgrep -f "monitor.py" > /dev/null; then
    echo "✅ Heartbeat Monitor: RUNNING (PID: $(pgrep -f monitor.py))"
else
    echo "❌ Heartbeat Monitor: STOPPED"
fi

echo ""

# Quick device ping check
devices=(
    "100.98.31.10:Mac Mini M4"
    "100.127.194.8:Kali Y2K" 
    "192.168.154.124:Jetson Orin"
)

echo "📡 Network Connectivity:"
for device in "${devices[@]}"; do
    IFS=':' read -r ip name <<< "$device"
    if [[ "$name" == "Mac Mini M4" ]]; then
        if curl -s --connect-timeout 3 "http://$ip:11434/api/tags" > /dev/null 2>&1; then
            echo "  ✅ $name ($ip)"
            echo "     ✅ Ollama API"
            # Also check SSH if curl for Ollama succeeded
            if nc -z -w3 "$ip" 22 2>/dev/null; then
                echo "     ✅ SSH"
            else
                echo "     ❌ SSH"
            fi
        else
            echo "  ❌ $name ($ip) - OFFLINE (Ollama/Connectivity issue)"
        fi
    elif [[ "$name" == "Kali Y2K" ]]; then
        if nc -z -w3 "$ip" 22 2>/dev/null; then
            echo "  ✅ $name ($ip)"
            echo "     ✅ SSH"
        else
            echo "  ❌ $name ($ip) - OFFLINE (SSH/Connectivity issue)"
        fi
    else # For Jetson Orin and any other future devices
        # Fallback to SSH check for general connectivity
        if nc -z -w3 "$ip" 22 2>/dev/null; then
            echo "  ✅ $name ($ip)"
            echo "     ✅ SSH"
        else
            echo "  ❌ $name ($ip) - OFFLINE (SSH/Connectivity issue)"
        fi
    fi
done

echo ""

# Check state file
if [[ -f "empire-state.json" ]]; then
    echo "📊 Last Monitor Run:"
    if command -v jq > /dev/null 2>&1; then
        # Parse with jq if available
        last_check=$(jq -r '.devices.mac_mini.last_check // "unknown"' empire-state.json 2>/dev/null)
        if [[ "$last_check" != "unknown" && "$last_check" != "null" ]]; then
            echo "  Last Check: $last_check"
        else
            echo "  State file exists but no timestamp"
        fi
    else
        echo "  State file: $(stat -c %y empire-state.json 2>/dev/null || stat -f %Sm empire-state.json 2>/dev/null)"
    fi
else
    echo "📊 No monitoring state found (monitor never ran)"
fi

echo ""

# OpenClaw status
if command -v openclaw > /dev/null 2>&1; then
    echo "🦀 OpenClaw Gateway:"
    if openclaw gateway status 2>/dev/null | grep -q "running"; then
        echo "  ✅ Gateway running"
    else
        echo "  ❌ Gateway stopped"
    fi
else
    echo "🦀 OpenClaw: Not in PATH"
fi

echo ""
echo "🔧 Quick Commands:"
echo "  ./monitor.py &              # Start monitoring"  
echo "  pkill -f monitor.py         # Stop monitoring"
echo "  tail -f monitor.log         # Watch logs"
echo ""