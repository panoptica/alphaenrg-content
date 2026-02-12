#!/usr/bin/env python3
"""
End-to-end pipeline test for LFC Agent
Generates a complete Instagram post: content + visual + caption
"""

import os
import sys
sys.path.append('src')

from fixtures.monitor import FixtureMonitor
from generation.generator import generate_variants
from visuals.compositor import create_stat_graphic
from dotenv import load_dotenv

load_dotenv()

def test_full_pipeline():
    print("🔴 LFC AGENT - FULL PIPELINE TEST")
    print("=" * 50)
    
    # 1. Get fixture
    print("\n1️⃣  Checking fixture...")
    monitor = FixtureMonitor()
    fixture = monitor.get_next_fixture()
    print(f"   ✅ LFC vs {fixture['opponent']}, {fixture['days_until']} days")
    
    # 2. Generate stat graphic content
    print("\n2️⃣  Creating stat graphic...")
    stat_data = {
        "headline": "92 WINS",
        "label": f"Liverpool vs {fixture['opponent']} (All Time)",
        "supporting": [
            {"value": "54", "label": "LFC Wins"},
            {"value": "16", "label": "City Wins"}, 
            {"value": "27", "label": "Draws"}
        ]
    }
    
    graphic_path = create_stat_graphic(stat_data)
    print(f"   ✅ Stat graphic: {graphic_path}")
    
    # 3. Generate captions
    print("\n3️⃣  Generating captions...")
    context = {
        "opponent": fixture['opponent'],
        "date": fixture['date'],
        "stat_json": str(stat_data)
    }
    
    try:
        variants = generate_variants("stat_graphic", context)
        print(f"   ✅ Generated {len(variants)} caption variants")
        
        # Show best variant
        variant_a = variants.get('variant_a', {})
        caption = variant_a.get('caption', 'No caption')
        hashtags = ' '.join(variant_a.get('hashtags', [])[:8])
        
        print(f"\n   📝 Sample caption:")
        print(f"      {caption}")
        print(f"      {hashtags}")
        
    except Exception as e:
        print(f"   ❌ Caption generation failed: {e}")
        return False
    
    # 4. Show posting schedule  
    print("\n4️⃣  Posting schedule:")
    schedule = monitor.get_content_schedule(fixture)
    for post in schedule[:3]:
        print(f"   📅 {post['day']} {post['time']}: {post['content_type']}")
    print(f"   ... {len(schedule)} total posts scheduled")
    
    print(f"\n🔥 PIPELINE TEST: SUCCESS")
    print(f"Ready to generate all 7 posts for the match!")
    return True

if __name__ == "__main__":
    test_full_pipeline()