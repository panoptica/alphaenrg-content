"""
Local LLM Synthesis Module
Uses Ollama (Llama 3 8B) on Mac Mini for zero-cost AI synthesis
"""
import requests
import json
from typing import Optional
from datetime import datetime

# Mac Mini Ollama endpoint
OLLAMA_URL = "http://192.168.154.44:11434"
MODEL = "llama3:8b"


def generate(prompt: str, system: str = None, max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
    """Generate text using local Llama 3"""
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"LLM generation error: {e}")
        return None


def synthesize_signals(signals: list[dict], limit: int = 10) -> str:
    """Generate a narrative synthesis of top signals"""
    
    # Format signals for the prompt
    signal_text = "\n".join([
        f"- [{s.get('final_score', 0):.1f}] {s.get('title', 'Untitled')[:100]} "
        f"(Source: {s.get('source', 'unknown')}, Domain: {s.get('domain', 'unknown')})"
        for s in signals[:limit]
    ])
    
    system = """You are an energy sector investment analyst. Your job is to synthesize 
intelligence signals into actionable insights for investors looking 12-18 months ahead.
Focus on: emerging technologies, regulatory changes, major capital movements, and convergence signals.
Be concise and direct. Highlight the most actionable opportunities."""

    prompt = f"""Today's top energy intelligence signals:

{signal_text}

Provide a brief synthesis (3-4 paragraphs):
1. Key themes emerging from these signals
2. Most promising investment opportunities
3. Risks or concerns to watch
4. Recommended actions for the next 30 days"""

    return generate(prompt, system=system, max_tokens=800)


def generate_digest_narrative(signals: list[dict], stats: dict) -> str:
    """Generate the narrative section of the daily digest email"""
    
    # Group signals by domain
    by_domain = {}
    for s in signals:
        domain = s.get('domain', 'other')
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(s)
    
    domain_summary = "\n".join([
        f"- {domain.upper()}: {len(items)} signals, top score {max(s.get('final_score', 0) for s in items):.1f}"
        for domain, items in sorted(by_domain.items(), key=lambda x: -len(x[1]))
    ])
    
    system = """You are writing the executive summary for a daily energy intelligence digest.
Be professional, concise, and actionable. Write for sophisticated investors."""

    prompt = f"""Daily Energy Intelligence Digest - {datetime.now().strftime('%B %d, %Y')}

Stats:
- Total signals: {stats.get('total', 0)}
- Strong signals (≥7): {stats.get('strong', 0)}
- Critical signals (≥12): {stats.get('critical', 0)}

By Domain:
{domain_summary}

Top 5 Signals:
{chr(10).join([f"- [{s.get('final_score', 0):.1f}] {s.get('title', '')[:80]}" for s in signals[:5]])}

Write a 2-paragraph executive summary highlighting:
1. The most significant developments today
2. Key actions investors should consider"""

    return generate(prompt, system=system, max_tokens=500)


def analyze_convergence(signals: list[dict]) -> str:
    """Analyze signals for convergence patterns (multiple sources pointing to same trend)"""
    
    # Group by keywords/themes
    themes = {}
    for s in signals:
        keywords = s.get('entities', {}).get('keywords', [])
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in themes:
                themes[kw_lower] = []
            themes[kw_lower].append(s)
    
    # Find themes with multiple signals
    convergent = {k: v for k, v in themes.items() if len(v) >= 3}
    
    if not convergent:
        return "No strong convergence patterns detected today."
    
    convergence_text = "\n".join([
        f"- '{theme}': {len(signals)} signals from {len(set(s.get('source', '') for s in signals))} sources"
        for theme, signals in sorted(convergent.items(), key=lambda x: -len(x[1]))[:5]
    ])
    
    prompt = f"""Convergence Analysis - Multiple signals pointing to same trends:

{convergence_text}

In 2-3 sentences, explain what this convergence suggests for investors."""

    return generate(prompt, max_tokens=200)


# Test
if __name__ == "__main__":
    print("Testing LLM connection...")
    result = generate("What is immersion cooling for data centers? Answer in one sentence.")
    if result:
        print(f"✅ LLM working: {result}")
    else:
        print("❌ LLM connection failed")
