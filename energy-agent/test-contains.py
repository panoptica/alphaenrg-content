#!/usr/bin/env python3

import requests

api_key = "N4vIXj2M.tZo5TVasHzojYgbHbEq4b2k4RlveyJW1"
base_url = "https://search.patentsview.org/api/v1/patent"

query = {"patent_title": {"_contains": "battery"}}
payload = {"q": query, "f": ["patent_id", "patent_title"], "o": {"per_page": 3}}
headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

response = requests.post(base_url, headers=headers, json=payload)
print(f"Contains search status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    patents = data.get("patents", [])
    total = data.get("total_hits", 0)
    print(f"SUCCESS! Found {total} patents with 'battery' in title")
    for i, p in enumerate(patents):
        patent_id = p.get("patent_id", "unknown")
        title = p.get("patent_title", "")[:60]
        print(f"{i+1}. {patent_id}: {title}...")
else:
    print(f"Error: {response.text}")