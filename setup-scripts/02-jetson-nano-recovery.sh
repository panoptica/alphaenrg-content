#!/bin/bash
# Jetson Nano Password Recovery & Setup

echo "🦀 Jetson Nano Recovery & CV Setup..."

JETSON="192.168.154.124"

echo "1. Testing connection to Jetson Nano..."
if ping -c 1 $JETSON > /dev/null 2>&1; then
    echo "✅ Jetson Nano is reachable"
    
    echo "2. Trying known credentials..."
    # From memory - we cracked this before
    echo "Trying: deepseek/jetson_orin"
    if sshpass -p 'jetson_orin' ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no deepseek@$JETSON 'echo "Success!"' 2>/dev/null; then
        echo "✅ Login successful with deepseek/jetson_orin"
        
        echo "3. Setting up satellite imagery CV stack..."
        sshpass -p 'jetson_orin' ssh deepseek@$JETSON << 'EOF'
            # Update system
            sudo apt update && sudo apt upgrade -y
            
            # Install CV dependencies
            sudo apt install -y python3-pip python3-dev
            pip3 install --upgrade pip
            
            # Install satellite imagery tools
            pip3 install rasterio geopandas folium opencv-python-headless
            pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
            
            # Create project structure
            mkdir -p ~/satellite-cv/{data,models,scripts}
            
            echo "✅ Jetson setup complete"
EOF
    else
        echo "❌ Known credentials failed"
        echo ""
        echo "Password Recovery Options:"
        echo ""
        echo "A) Physical Recovery (requires monitor/keyboard):"
        echo "   1. Boot into recovery mode (hold FORCE_RECOVERY pin)"
        echo "   2. Flash new image with known credentials"
        echo ""
        echo "B) Single User Mode:"
        echo "   1. Edit GRUB: add 'single' to boot params"
        echo "   2. Reset password: passwd username"
        echo ""
        echo "C) SD Card Recovery:"
        echo "   1. Remove SD card, mount on another Linux machine"
        echo "   2. Edit /etc/passwd and /etc/shadow"
        echo "   3. Replace password hash with known value"
        echo ""
        echo "D) Network Boot Recovery:"
        echo "   1. Set up TFTP server"
        echo "   2. Boot from network with custom image"
        
        echo ""
        echo "💡 Recommended: Try option B first (single user mode)"
        echo "   Requires physical access to keyboard during boot"
    fi
else
    echo "❌ Jetson Nano unreachable at $JETSON"
    echo "   Check power, network connection, IP address"
fi