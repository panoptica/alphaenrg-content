#!/usr/bin/env python3
"""
AlphaENRG Launch Tweet - First Intelligence Post
"""

import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def post_launch_tweet():
    """Post AlphaENRG launch tweet"""
    
    try:
        # Get credentials from environment
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Initialize Twitter API client
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # AlphaENRG Launch Tweet
        launch_text = """🚀 AlphaENRG Energy Intelligence is now LIVE!

Daily automated analysis combining:
📊 ArXiv research papers
📋 Patent filings (USPTO)  
📈 SEC regulatory data
🔬 Market trend synthesis

🎯 Target: Actionable energy investment signals for institutional investors

⏰ Daily briefings at 7:00 AM GMT
🔬 Focus: Clean energy, quantum computing, semiconductors

#EnergyIntelligence #CleanTech #QuantumComputing #InvestmentSignals

Let's revolutionize energy market intelligence! 🌟"""

        # Post the tweet
        response = client.create_tweet(text=launch_text)
        
        if response.data:
            tweet_id = response.data['id']
            print(f"🎉 SUCCESS! AlphaENRG launch tweet posted!")
            print(f"🔗 Tweet ID: {tweet_id}")
            print(f"📊 View: https://x.com/AlphaENRG/status/{tweet_id}")
            print(f"\n📝 Posted text:\n{launch_text}")
            return True
        else:
            print("❌ Failed to post launch tweet")
            return False
            
    except Exception as e:
        print(f"❌ ERROR posting launch tweet: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Posting AlphaENRG launch tweet...")
    success = post_launch_tweet()
    
    if success:
        print("\n🎯 AlphaENRG is now LIVE on X!")
        print("✅ Daily automation ready")
        print("✅ Intelligence feed active") 
        print("✅ Market signals incoming")
        print("\n🔥 Welcome to the future of energy intelligence!")
    else:
        print("\n🔧 Check the error above and try again")