# Perplexity Pro Integration

## Why Perplexity Pro?
- **Cost**: ~10x cheaper than Claude for research tasks
- **Real-time web**: Sonar Pro has live web access (vs Claude's training cutoff)
- **Research quality**: Excellent for analysis, synthesis, fact-checking
- **Already integrated**: We have API key, just need to expand usage

## Current Usage
✅ **Web Search**: Perplexity Sonar Pro (already working)
- Tool: `web_search` 
- Model: `perplexity/sonar-pro`
- Use: Search queries, real-time info

## Expanded Usage (New)
🚀 **General Reasoning**: 
- **Research synthesis**: Perplexity → Claude polish
- **Web content analysis**: Pure Perplexity (faster + cheaper)
- **Fact-checking**: Real-time verification
- **News analysis**: Live updates, market intel

## Models Available
- `perplexity/sonar-pro` - Web-connected reasoning
- `perplexity/llama-3.1-70b-instruct` - Pure reasoning (no web)
- `perplexity/llama-3.1-8b-instruct` - Fast, cheap tasks

## Routing Strategy
```
Web Research → Perplexity Sonar Pro (real-time)
Market Analysis → Perplexity Sonar Pro → Claude narrative
News Digests → Perplexity bulk → Claude summary
Fact Verification → Perplexity Sonar Pro
Creative Writing → Still use Gemini/Claude
```

## Cost Impact
- **Energy Agent**: Research collection could be 80% Perplexity
- **Daily digests**: Bulk analysis → Perplexity, final narrative → Claude
- **Estimated savings**: 40-60% on research-heavy tasks

## Perfect For
- SEC filing analysis
- Patent research  
- Market intelligence
- News synthesis
- Technical documentation
- Real-time data analysis