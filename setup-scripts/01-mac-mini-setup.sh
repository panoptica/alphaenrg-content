#!/bin/bash
# Mac Mini M4 Optimization Setup

echo "🦀 Setting up Mac Mini M4 for optimized compute..."

MAC_MINI="192.168.154.44"
USER="macmini"
PASS="!1Longmore@@"

echo "1. Testing connection to Mac Mini..."
if ping -c 1 $MAC_MINI > /dev/null 2>&1; then
    echo "✅ Mac Mini is reachable"
else
    echo "❌ Mac Mini unreachable at $MAC_MINI"
    exit 1
fi

echo "2. Checking Ollama status..."
if curl -s http://$MAC_MINI:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
    curl -s http://$MAC_MINI:11434/api/tags | jq '.models[].name'
else
    echo "⚠️  Ollama not responding - need to start it"
    echo "Run on Mac Mini: OLLAMA_HOST=0.0.0.0 ollama serve &"
fi

echo "3. Setting up Stable Diffusion for image generation..."
echo "Options:"
echo "  A) ComfyUI (easier setup)"
echo "  B) Automatic1111 (more features)"
echo "  C) Invoke AI (professional)"

echo "4. Models to install:"
echo "  - llama3:8b (fast, good for bulk work)"
echo "  - llama3:70b (slower, better quality)"
echo "  - codellama:34b (specialized for code)"

echo "5. Next steps:"
echo "  SSH to Mac Mini: ssh $USER@$MAC_MINI"
echo "  Start Ollama: OLLAMA_HOST=0.0.0.0 ollama serve &"
echo "  Install models: ollama pull llama3:8b"
echo "  Setup image gen: Choose option A/B/C above"