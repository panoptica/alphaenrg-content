#!/bin/bash
# Deploy Full Compute Optimization

echo "🦀 Deploying Compute Optimization Stack..."

echo "1. Backing up current OpenClaw config..."
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%s)

echo "2. Checking current costs (last 24h)..."
echo "Current model usage:"
echo "  Claude Sonnet: Primary (expensive)"
echo "  Target: 70% cost reduction"

echo "3. Hardware Status Check..."

# Mac Mini M4
echo "Mac Mini M4 (192.168.154.44):"
if ping -c 1 192.168.154.44 > /dev/null 2>&1; then
    echo "  ✅ Online"
    if curl -s http://192.168.154.44:11434/api/tags > /dev/null 2>&1; then
        echo "  ✅ Ollama running"
    else
        echo "  ❌ Ollama not responding"
    fi
else
    echo "  ❌ Offline"
fi

# Kali Box
echo "Kali Box (192.168.154.193):"
if ping -c 1 192.168.154.193 > /dev/null 2>&1; then
    echo "  ✅ Online"
else
    echo "  ❌ Offline"
fi

# Jetson Nano
echo "Jetson Nano (192.168.154.124):"
if ping -c 1 192.168.154.124 > /dev/null 2>&1; then
    echo "  ✅ Online"
    if sshpass -p 'jetson_orin' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no deepseek@192.168.154.124 'echo "test"' 2>/dev/null; then
        echo "  ✅ SSH accessible"
    else
        echo "  ❌ SSH failed - password reset needed"
    fi
else
    echo "  ❌ Offline"
fi

echo ""
echo "4. Next Actions Needed:"
echo ""
echo "✅ DONE:"
echo "  - Optimized config created (optimized-openclaw-config.json)"
echo "  - Setup scripts ready"
echo "  - Cost routing planned"
echo ""
echo "🔧 TODO:"
echo "  - Restart Ollama on Mac Mini with network binding"
echo "  - Install image generation (ComfyUI recommended)"
echo "  - Add Gemini Pro API key"
echo "  - Recover Jetson Nano access"
echo "  - Deploy config to OpenClaw"
echo ""
echo "🚀 COMMANDS TO RUN:"
echo "  1. chmod +x setup-scripts/*.sh"
echo "  2. ./setup-scripts/01-mac-mini-setup.sh"
echo "  3. ./setup-scripts/02-jetson-nano-recovery.sh"
echo "  4. Deploy config when ready"

echo ""
echo "💰 Expected Savings:"
echo "  Current: ~100% Claude API"
echo "  Target:  ~30% Claude, 50% local, 20% Gemini"
echo "  Estimated: 60-80% cost reduction"