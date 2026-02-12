#!/usr/bin/env python3
"""
Setup OAuth 2.0 for X API email access
Need OAuth 2.0 User Context (not OAuth 1.0a) for email scope
"""

import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

def setup_oauth2_email_access():
    """Set up OAuth 2.0 flow for email access"""
    
    print("🔑 Setting up OAuth 2.0 for email access...")
    
    # Client ID and secret for OAuth 2.0 (different from OAuth 1.0a)
    client_id = os.getenv('TWITTER_CLIENT_ID')  # Need this from X app settings
    client_secret = os.getenv('TWITTER_CLIENT_SECRET')  # Need this too
    
    if not client_id or not client_secret:
        print("❌ Missing OAuth 2.0 credentials:")
        print("   Need TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET")
        print("   These are different from OAuth 1.0a API key/secret")
        print("   Get from X Developer Portal > App > Keys and Tokens")
        return False
    
    # Scopes needed for email access
    scopes = ['tweet.read', 'users.read', 'users.email']
    
    # OAuth 2.0 User Context flow
    oauth2_handler = tweepy.OAuth2UserHandler(
        client_id=client_id,
        redirect_uri="https://localhost:8080/callback",  # Must match app settings
        scope=scopes,
        client_secret=client_secret
    )
    
    # Get authorization URL
    auth_url = oauth2_handler.get_authorization_url()
    print(f"📱 Visit this URL to authorize: {auth_url}")
    print("   After authorizing, you'll get a callback with 'code' parameter")
    
    # Wait for authorization code
    auth_code = input("🔗 Enter the authorization code from callback URL: ")
    
    try:
        # Exchange code for access token
        access_token = oauth2_handler.fetch_token(auth_code)
        
        print("✅ OAuth 2.0 access token obtained!")
        print("📧 Email scope should now be accessible")
        
        # Test email access
        client = tweepy.Client(oauth2_handler)
        user = client.get_me(user_fields=['confirmed_email'])
        
        if hasattr(user.data, 'confirmed_email'):
            print(f"🎯 Email access confirmed: {user.data.confirmed_email}")
        else:
            print("⚠️  Email field not available yet")
            
        return True
        
    except Exception as e:
        print(f"❌ OAuth 2.0 setup failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 AlphaENRG OAuth 2.0 Email Access Setup")
    print("=" * 50)
    
    # Current status
    print("📊 Current Setup: OAuth 1.0a (basic API access)")
    print("🎯 Target: OAuth 2.0 User Context (email scope)")
    print("📋 Required: CLIENT_ID and CLIENT_SECRET from X Developer Portal")
    print("")
    
    setup_oauth2_email_access()