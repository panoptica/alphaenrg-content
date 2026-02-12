# Energy Intelligence Publishing System

Automated posting system that converts daily energy intelligence signals into engaging social media content.

## Features

🔋 **Signal-to-Content Pipeline**: Converts energy agent signals into Twitter threads  
📊 **Smart Filtering**: Only posts high-quality signals (score ≥7.0)  
🤖 **Automated Scheduling**: Posts daily at optimal times  
📈 **Multi-Platform Ready**: X/Twitter implemented, Substack/Medium coming  

## Quick Start

1. **Setup**
   ```bash
   cd publishing-system
   ./setup.sh
   ```

2. **Configure X API**
   - Get credentials: https://developer.twitter.com/en/portal/dashboard
   - Edit `.env` file with your keys

3. **Test**
   ```bash
   python3 x-publisher.py  # Test thread generation
   python3 auto-publisher.py  # Test full pipeline
   ```

## Usage

### Manual Publishing
```bash
python3 auto-publisher.py
```

### Automated Daily Publishing
Add to crontab for 9 AM daily posts:
```bash
0 9 * * * cd /path/to/publishing-system && python3 auto-publisher.py --auto
```

## Configuration

Edit `.env` file:

```env
# X API Credentials
X_BEARER_TOKEN=your_token
X_CONSUMER_KEY=your_key
X_CONSUMER_SECRET=your_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_secret

# Publishing Settings
MAX_SIGNALS_PER_THREAD=3  # Max signals per post
MIN_SIGNAL_SCORE=7.0      # Minimum score to publish
```

## Thread Format

Generated threads follow this structure:

1. **Opener**: Date, signal count, hook
2. **Signal Tweets**: Top 3 signals with scores and context  
3. **Closer**: CTA and hashtags

Example:
```
🔋 Energy Intelligence Alert 2026-02-11

Our AI just flagged 1,168 signals across energy/cooling/quantum domains. 
Here are the top picks that could shape markets 12-18 months out 👇

1/ 🎯 Nanovortex-driven optical diffusion breakthrough
📊 Score: 10.0/10
🏷️ Domain: SMR/Nuclear
💡 Why it matters: Novel approach could boost SMR efficiency 40%
```

## Integration

Reads signals from energy agent output:
- `../energy-agent/output/signals-YYYY-MM-DD.json`
- `../energy-agent/signals-YYYY-MM-DD.json`

Expected signal format:
```json
{
  "title": "Signal title",
  "score": 9.5,
  "domain": "Quantum Computing", 
  "summary": "Brief explanation"
}
```

## Coming Soon

- 📰 **Substack Integration**: Auto-publish weekly deep-dives
- 📝 **Medium Support**: Cross-post evergreen content
- 📊 **Analytics Dashboard**: Track engagement and ROI
- 🎨 **Visual Content**: Auto-generate charts and infographics