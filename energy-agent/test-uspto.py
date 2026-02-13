#!/usr/bin/env python3

import requests
import json

api_key = "N4vIXj2M.tZo5TVasHzojYgbHbEq4b2k4RlveyJW1"
base_url = "https://search.patentsview.org/api/v1/patent"

# Simple test query
query = {"patent_date": {"_gte": "2023-01-01"}}

payload = {
    "q": query,
    "f": ["patent_id", "patent_date"],
    "o": {"per_page": 2}
}

headers = {
    "X-Api-Key": api_key,
    "Content-Type": "application/json"
}

response = requests.post(base_url, headers=headers, json=payload)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    total = data.get("total_hits", 0)
    patents = data.get("patent", [])
    print(f"Total hits: {total}")
    print(f"Returned: {len(patents)}")
    for i, p in enumerate(patents):
        print(f"{i+1}. {p.get('patent_id')} - {p.get('patent_date')}")
else:
    print("Error:", response.text)