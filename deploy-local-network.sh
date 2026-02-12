#!/bin/bash
# Deploy via local network instead of Tailscale
sed 's/100.97.28.29/192.168.154.44/g' deploy-optimizations.sh > deploy-local-network.sh
chmod +x deploy-local-network.sh
echo "Created deploy-local-network.sh using local IP instead"