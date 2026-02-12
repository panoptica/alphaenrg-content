# Compute Optimization Plan

## 1. Local Model Integration (Mac Mini M4)
- Add Ollama models to OpenClaw config
- Set up routing: Llama 3 8B for bulk work, Claude for complex tasks
- Cost reduction target: 60-80% for routine tasks

## 2. Image Generation Setup
Options:
- **Local**: Stable Diffusion on Mac Mini M4 (ComfyUI or A1111)
- **Cloud**: Midjourney API, DALL-E 3, or Flux
- Target: Content creation, diagrams, social media

## 3. Cloud Provider Integration
- **Perplexity Pro**: Sonar Pro + Llama models (excellent for research/web analysis)
- **Gemini Pro**: Google's competitive pricing
- **Bedrock**: AWS Claude at potentially lower cost
- **GCP**: Vertex AI for specialized tasks

## 4. Hardware Recovery
- **Jetson Nano**: Password reset, get back online
- **Kali**: Already working, optimize OSINT stack

## 5. Smart Routing Logic
```
Bulk Analysis → Llama 3 8B (local)
Code Generation → Llama 3 8B → Claude review
Research + Web Analysis → Perplexity Sonar Pro
Research Synthesis → Perplexity Pro → Claude polish
Complex Reasoning → Claude Sonnet/Opus
Creative Writing → Gemini Pro or local
Image Gen → Local SD or cloud API
```

## Cost Targets
- Current: ~100% Claude API calls  
- Target: 25% Claude, 40% local, 35% cheaper options (Perplexity/Gemini)
- Perplexity Pro: Excellent for research tasks at ~10x cheaper than Claude