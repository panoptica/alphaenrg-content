from integrated_memory_search import memory_search

# Test with lower threshold
result = memory_search("Mac Mini", maxResults=5, minScore=0.1)
print(f"Found {len(result[results])} results")

for i, r in enumerate(result[results][:3], 1):
    print(f"{i}. Source: {r.get(source, unknown)}")
    print(f"   Score: {r.get(score, 0):.2f}")
    print(f"   Snippet: {r.get(snippet, )[:100]}...")
    print()
