#!/usr/bin/env python3
"""
Quick profile optimization for AlphaENRG
"""

import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

def update_profile():
    """Update AlphaENRG profile with killer bio"""
    
    try:
        # OAuth 1.0a for profile updates
        auth = tweepy.OAuth1UserHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET'),
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        api = tweepy.API(auth)
        
        # Killer institutional bio (under 160 chars)
        bio = "⚡ Premium Energy Intelligence & Investment Signals\n🔬 AI Analysis: ArXiv + Patents + SEC\n🎯 Daily 7AM GMT\n🦀 Institutional Grade"

        # Update profile
        api.update_profile(
            description=bio,
            location="🌐 Global Energy Markets",
            url="https://github.com/panoptica/energy-intelligence"
        )
        
        print("✅ AlphaENRG profile optimized!")
        print(f"📊 New bio: {bio[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Profile update error: {e}")
        return False

if __name__ == "__main__":
    update_profile()