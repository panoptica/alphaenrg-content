#!/usr/bin/env python3
"""
Find correct Instagram Business Account ID
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("FACEBOOK_ACCESS_TOKEN")

print("🔍 FINDING CORRECT INSTAGRAM ACCOUNT ID")
print("=" * 50)

# Method 1: Check me/accounts for pages
me_url = "https://graph.facebook.com/v18.0/me/accounts"
me_params = {"access_token": token}
me_response = requests.get(me_url, params=me_params)
me_data = me_response.json()

print(f"1️⃣ Pages accessible: {len(me_data.get('data', []))}")
for page in me_data.get('data', []):
    page_id = page.get('id')
    page_name = page.get('name')
    print(f"   Page: {page_name} ({page_id})")
    
    # Check if page has Instagram account
    ig_url = f"https://graph.facebook.com/v18.0/{page_id}"
    ig_params = {
        "fields": "instagram_business_account",
        "access_token": token
    }
    ig_response = requests.get(ig_url, params=ig_params)
    ig_data = ig_response.json()
    
    if 'instagram_business_account' in ig_data:
        ig_account_id = ig_data['instagram_business_account']['id']
        print(f"   ✅ Instagram ID: {ig_account_id}")
        
        # Test this Instagram account
        test_url = f"https://graph.facebook.com/v18.0/{ig_account_id}"
        test_params = {
            "fields": "username,account_type",
            "access_token": token
        }
        test_response = requests.get(test_url, params=test_params)
        test_data = test_response.json()
        
        if 'error' not in test_data:
            print(f"   ✅ @{test_data.get('username', 'unknown')}")
        else:
            print(f"   ❌ Error: {test_data['error']['message']}")
    else:
        print(f"   ❌ No Instagram account linked")

# If no pages found, check token info
if not me_data.get('data'):
    print("\n2️⃣ Token debug info:")
    debug_url = "https://graph.facebook.com/v18.0/me"
    debug_params = {"access_token": token}
    debug_response = requests.get(debug_url, params=debug_params)
    debug_data = debug_response.json()
    
    if 'error' not in debug_data:
        print(f"   User: {debug_data.get('name', 'Unknown')}")
        print(f"   ID: {debug_data.get('id', 'N/A')}")
    else:
        print(f"   Error: {debug_data['error']['message']}")