#!/usr/bin/env python3

import requests

api_key = "N4vIXj2M.tZo5TVasHzojYgbHbEq4b2k4RlveyJW1"
base_url = "https://search.patentsview.org/api/v1/patent"

# Fixed query - _text_any expects an array
query = {
    "_and": [
        {"patent_date": {"_gte": "2023-01-01", "_lte": "2023-12-31"}},
        {"_text_any": {"patent_abstract": ["battery", "lithium"]}}
    ]
}

payload = {
    "q": query,
    "f": ["patent_id", "patent_title", "patent_date", "assignees"],
    "o": {"per_page": 3}
}

headers = {
    "X-Api-Key": api_key,
    "Content-Type": "application/json"
}

response = requests.post(base_url, headers=headers, json=payload)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    patents = data.get("patents", [])
    total = data.get("total_hits", 0)
    print(f"SUCCESS! Found: {len(patents)} patents (total: {total})")
    
    for i, patent in enumerate(patents):
        patent_id = patent.get("patent_id", "unknown")
        title = patent.get("patent_title", "No title")
        print(f"{i+1}. {patent_id}: {title[:50]}...")
        
        assignees = patent.get("assignees", [])
        if assignees and assignees[0]:
            org = assignees[0].get("assignee_organization", "Unknown")
            print(f"   Company: {org}")
        print()
else:
    print(f"Error: {response.text}")
