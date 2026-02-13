#!/usr/bin/env python3

import requests

api_key = "N4vIXj2M.tZo5TVasHzojYgbHbEq4b2k4RlveyJW1"

# Try direct patent lookup (should be simplest)
base_url = "https://search.patentsview.org/api/v1/patent"

# Get requests don't need complex queries
try:
    response = requests.get(f"{base_url}/10000000", headers={"X-Api-Key": api_key})
    print(f"GET Status: {response.status_code}")
    if response.status_code == 200:
        print("GET works!")
        print(response.json())
    else:
        print("GET Error:", response.text)
except Exception as e:
    print("GET Exception:", e)

# Try POST with very basic query
query = {"patent_id": "10000000"}
payload = {
    "q": query,
    "f": ["patent_id", "patent_title"]
}

headers = {
    "X-Api-Key": api_key,
    "Content-Type": "application/json"
}

try:
    response = requests.post(base_url, headers=headers, json=payload)
    print(f"POST Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("POST Success:", data)
    else:
        print("POST Error:", response.text)
except Exception as e:
    print("POST Exception:", e)