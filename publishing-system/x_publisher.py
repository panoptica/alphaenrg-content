#!/usr/bin/env python3
"""
X (Twitter) Publisher for Energy Intelligence Signals
Converts daily digest signals into engaging X threads
"""

import os
import json
import tweepy
from typing import List, Dict
from datetime import datetime

class XPublisher:
    def __init__(self):
        # X API v2 credentials (to be set via environment)
        self.bearer_token = os.getenv('X_BEARER_TOKEN')
        self.consumer_key = os.getenv('X_CONSUMER_KEY') 
        self.consumer_secret = os.getenv('X_CONSUMER_SECRET')
        self.access_token = os.getenv('X_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
        
        if not all([self.bearer_token, self.consumer_key, self.consumer_secret, 
                   self.access_token, self.access_token_secret]):
            print("⚠️ X API credentials not found. Set X_* environment variables.")
            self.client = None
            return
            
        # Initialize Tweepy client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
    
    def signal_to_thread(self, signals: List[Dict]) -> List[str]:
        """Convert top signals into X thread format"""
        if not signals:
            return []
            
        # Take top 3 signals
        top_signals = signals[:3]
        
        # Thread opener
        today = datetime.now().strftime('%Y-%m-%d')
        opener = f"🔋 Energy Intelligence Alert {today}\n\nOur AI just flagged {len(signals)} signals across energy/cooling/quantum domains. Here are the top picks that could shape markets 12-18 months out 👇"
        
        thread = [opener]
        
        # Add each signal as thread tweet
        for i, signal in enumerate(top_signals, 1):
            tweet = f"{i}/ 🎯 {signal.get('title', 'Untitled Signal')}\n"
            
            # Add score if available
            if 'score' in signal:
                tweet += f"📊 Score: {signal['score']}/10\n"
            
            # Add domain context
            if 'domain' in signal:
                tweet += f"🏷️ Domain: {signal['domain']}\n"
                
            # Add brief context/why it matters
            if 'summary' in signal:
                summary = signal['summary'][:150]  # Twitter length limit consideration
                tweet += f"\n💡 Why it matters: {summary}"
                
            thread.append(tweet)
        
        # Thread closer with CTA
        closer = f"🧠 This intelligence comes from monitoring {len(signals)} sources daily - patents, papers, filings, grants.\n\n🔔 Follow for daily energy/quantum investment signals\n\n#EnergyIntel #QuantumComputing #CleanTech"
        thread.append(closer)
        
        return thread
    
    def publish_thread(self, thread: List[str]) -> bool:
        """Publish thread to X, return success status"""
        if not self.client:
            print("❌ X client not initialized")
            return False
            
        try:
            tweet_ids = []
            
            # Post first tweet
            response = self.client.create_tweet(text=thread[0])
            tweet_ids.append(response.data['id'])
            print(f"✅ Posted opener: {response.data['id']}")
            
            # Post replies in thread
            for i, tweet_text in enumerate(thread[1:], 1):
                response = self.client.create_tweet(
                    text=tweet_text, 
                    in_reply_to_tweet_id=tweet_ids[-1]
                )
                tweet_ids.append(response.data['id'])
                print(f"✅ Posted tweet {i+1}: {response.data['id']}")
                
            print(f"🎉 Thread published successfully! {len(tweet_ids)} tweets")
            return True
            
        except Exception as e:
            print(f"❌ Failed to publish thread: {e}")
            return False

def main():
    """Test/demo function"""
    publisher = XPublisher()
    
    # Sample signals for testing
    test_signals = [
        {
            "title": "Nanovortex-driven optical diffusion breakthrough",
            "score": 10.0,
            "domain": "SMR/Nuclear", 
            "summary": "Novel optical approach could revolutionize small modular reactor efficiency by 40%"
        },
        {
            "title": "Quantum error correction via topological braiding",
            "score": 9.2,
            "domain": "Quantum Computing",
            "summary": "IBM breakthrough makes fault-tolerant quantum computing commercially viable by 2027"
        }
    ]
    
    thread = publisher.signal_to_thread(test_signals)
    
    print("Generated Thread:")
    for i, tweet in enumerate(thread):
        print(f"\n--- Tweet {i+1} ---")
        print(tweet)
        print(f"Length: {len(tweet)} chars")
    
    # Uncomment to actually post (when credentials are set)
    # publisher.publish_thread(thread)

if __name__ == "__main__":
    main()