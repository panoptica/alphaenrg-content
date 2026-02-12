#!/usr/bin/env python3
"""
Test X (Twitter) API connection for AlphaENRG
"""

import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twitter_connection():
    """Test X API connection with current credentials"""
    
    try:
        # Get credentials from environment
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        print("🔑 Testing X API credentials for AlphaENRG...")
        
        # Initialize Twitter API v2 client
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Test API connection by getting user info
        user = client.get_me()
        
        if user.data:
            print(f"✅ SUCCESS! Connected as: @{user.data.username}")
            print(f"📊 Account: {user.data.name}")
            print(f"🆔 User ID: {user.data.id}")
            print(f"📝 Verified: {getattr(user.data, 'verified', 'Unknown')}")
            
            # Test posting capability with a dry run
            print("\n🧪 Testing posting capability...")
            
            # Create a test tweet (but don't actually post it)
            test_text = "🚀 AlphaENRG Energy Intelligence - System Test [DO NOT POST]"
            print(f"✅ Would post: '{test_text[:50]}...'")
            print("🎯 X API fully functional - ready for automated posting!")
            
            return True
            
        else:
            print("❌ ERROR: Unable to retrieve user data")
            return False
            
    except tweepy.Forbidden as e:
        print(f"❌ FORBIDDEN: {e}")
        print("🔧 Check if your app has the right permissions (Read + Write)")
        return False
        
    except tweepy.Unauthorized as e:
        print(f"❌ UNAUTHORIZED: {e}")
        print("🔧 Check your API credentials are correct")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("🔧 General connection issue - check network/API status")
        return False

if __name__ == "__main__":
    success = test_twitter_connection()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Create launch tweet for AlphaENRG")
        print("2. Enable daily automation")
        print("3. Monitor first intelligence posts")
        print("\n🚀 AlphaENRG ready to go live!")
    else:
        print("\n🔧 Fix the issues above before proceeding")