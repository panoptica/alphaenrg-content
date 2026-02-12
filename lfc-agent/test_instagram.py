#!/usr/bin/env python3
"""
Test Instagram API connection
"""

import sys
sys.path.append('src')
from publishing.publisher import InstagramPublisher
import requests

print("🔴 TESTING INSTAGRAM API CONNECTION")
print("=" * 50)

publisher = InstagramPublisher()

# Test 1: Dry run
result = publisher.publish_image(
    image_url="https://example.com/test.jpg",
    caption="Test post #LFC #YNWA", 
    dry_run=True
)
print(f"✅ Dry run: {result['status']}")

# Test 2: Account info
print("\n📱 Account details:")
url = f"https://graph.facebook.com/v18.0/{publisher.ig_account_id}"
params = {
    "fields": "account_type,username,name",
    "access_token": publisher.access_token
}

response = requests.get(url, params=params)
data = response.json()

if "error" in data:
    print(f"❌ API Error: {data['error']['message']}")
    print(f"   Error code: {data['error'].get('code', 'N/A')}")
else:
    print(f"✅ Connected to: @{data.get('username', 'unknown')}")
    print(f"   Account: {data.get('name', 'N/A')}")
    print(f"   Type: {data.get('account_type', 'N/A')}")

print(f"\n🔥 Ready to post to Instagram!")