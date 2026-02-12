#!/usr/bin/env python3
"""
Test Instagram publishing endpoint
"""

import sys
sys.path.append('src')
from publishing.publisher import InstagramPublisher
import requests
import os
from dotenv import load_dotenv

load_dotenv()

print("🔴 TESTING INSTAGRAM PUBLISHING ENDPOINT")
print("=" * 50)

publisher = InstagramPublisher()

# Test 1: Check accessible pages/accounts
print("1️⃣ Checking accessible pages...")
me_url = "https://graph.facebook.com/v18.0/me/accounts"
me_params = {"access_token": publisher.access_token}
me_response = requests.get(me_url, params=me_params)
me_data = me_response.json()

if "error" in me_data:
    print(f"❌ Pages error: {me_data['error']['message']}")
else:
    pages = me_data.get('data', [])
    print(f"✅ Found {len(pages)} accessible page(s)")
    for page in pages:
        print(f"   - {page.get('name', 'Unknown')}: {page.get('id', 'N/A')}")

# Test 2: Try media creation endpoint (dry run style)
print("\n2️⃣ Testing media creation endpoint...")
media_url = f"https://graph.facebook.com/v18.0/{publisher.ig_account_id}/media"
print(f"   URL: {media_url}")
print(f"   Account ID: {publisher.ig_account_id}")

# Test 3: Check Instagram account info through different endpoint
print("\n3️⃣ Alternative Instagram account check...")
ig_url = f"https://graph.facebook.com/v18.0/{publisher.ig_account_id}"
ig_params = {
    "fields": "id,username",
    "access_token": publisher.access_token
}

ig_response = requests.get(ig_url, params=ig_params)
ig_data = ig_response.json()

if "error" in ig_data:
    print(f"❌ Instagram error: {ig_data['error']['message']}")
    print(f"   Error code: {ig_data['error'].get('code', 'N/A')}")
    print(f"   Error type: {ig_data['error'].get('type', 'N/A')}")
else:
    print(f"✅ Instagram account: @{ig_data.get('username', 'unknown')}")
    print(f"   ID: {ig_data.get('id', 'N/A')}")

print(f"\n🚀 Ready to test actual posting!")