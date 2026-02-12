#!/usr/bin/env python3
"""
X Integration for AlphaENRG - Post daily intelligence to X
"""

import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timezone
import random

load_dotenv()

class AlphaENRGPoster:
    def __init__(self):
        """Initialize X client for AlphaENRG"""
        
        # X API credentials
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Initialize Twitter client
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

    def post_daily_intelligence(self, intelligence_summary):
        """Post daily intelligence summary to X"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Create engaging intelligence post
        post_text = f"""⚡ AlphaENRG Daily Intelligence • {timestamp}

{intelligence_summary}

🎯 Institutional-grade analysis
📊 Data: ArXiv + Patents + SEC  
🔬 AI-powered synthesis

#EnergyIntelligence #InvestmentSignals #CleanTech #QuantumComputing"""

        try:
            # Post to X
            response = self.client.create_tweet(text=post_text)
            
            if response.data:
                tweet_id = response.data['id']
                print(f"✅ Daily intelligence posted to X!")
                print(f"🔗 Tweet ID: {tweet_id}")
                print(f"📊 View: https://x.com/AlphaENRG/status/{tweet_id}")
                return True
            else:
                print("❌ Failed to post intelligence to X")
                return False
                
        except Exception as e:
            print(f"❌ X posting error: {e}")
            return False

    def post_breaking_alert(self, alert_text):
        """Post breaking energy alert"""
        
        alerts = [
            f"🚨 BREAKING ENERGY INTEL:\n\n{alert_text}\n\n📊 AlphaENRG analysis flagged this as high-impact\n\n#BreakingEnergy #EnergyAlerts",
            f"⚡ ALPHA SIGNAL DETECTED:\n\n{alert_text}\n\n🎯 Institutional investors take note\n\n#AlphaSignals #EnergyMarkets"
        ]
        
        post_text = random.choice(alerts)
        
        try:
            response = self.client.create_tweet(text=post_text)
            if response.data:
                print("🚨 Breaking alert posted to X!")
                return True
            return False
        except Exception as e:
            print(f"❌ Alert posting error: {e}")
            return False

def integrate_with_daily_agent(intelligence_text):
    """Integration function for the main energy agent"""
    
    poster = AlphaENRGPoster()
    
    # Extract key insights for X post (keep under 280 chars)
    summary_lines = intelligence_text.split('\n')[:3]  # First 3 lines
    summary = '\n'.join(summary_lines)
    
    # Truncate if too long
    if len(summary) > 180:  # Leave room for hashtags
        summary = summary[:177] + "..."
    
    # Post to X
    success = poster.post_daily_intelligence(summary)
    
    return success

if __name__ == "__main__":
    # Test posting
    test_intelligence = """Quantum computing patents surge 47% this quarter
Clean energy storage innovations accelerating  
Semiconductor supply chain showing resilience"""
    
    result = integrate_with_daily_agent(test_intelligence)
    print(f"Test posting result: {result}")