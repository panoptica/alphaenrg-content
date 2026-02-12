#!/usr/bin/env python3
"""
Generate all 7 posts for City match
"""

import sys
sys.path.append('src')
from generation.generator import generate_variants
from visuals.compositor import create_stat_graphic, create_quote_graphic

print("🔴 GENERATING FULL CITY MATCH CONTENT SET")
print("=" * 60)

# Post schedule
posts = [
    {"day": "Friday", "time": "11:00", "type": "iconic_moment", "desc": "Klopp celebration"},
    {"day": "Friday", "time": "19:00", "type": "stat_graphic", "desc": "92 wins dominance"},
    {"day": "Saturday", "time": "09:00", "type": "crowd_atmosphere", "desc": "YNWA power"},
    {"day": "Saturday", "time": "13:00", "type": "comedy_banter", "desc": "115 charges"},
    {"day": "Saturday", "time": "17:00", "type": "famous_red", "desc": "Demis Nobel"},
    {"day": "Sunday", "time": "10:00", "type": "stat_graphic", "desc": "Anfield fortress"},
    {"day": "Sunday", "time": "14:00", "type": "crowd_atmosphere", "desc": "Pre-match hype"}
]

for i, post in enumerate(posts):
    print(f"\n{i+1}️⃣  {post['day']} {post['time']}: {post['desc']}")
    
    if post['type'] == 'stat_graphic':
        if i == 1:  # Friday stat
            stat_data = {
                "headline": "92 WINS",
                "label": "Liverpool vs City (All Time)",
                "supporting": [
                    {"value": "54", "label": "Home Wins"},
                    {"value": "16", "label": "City Wins"}
                ]
            }
        else:  # Sunday stat  
            stat_data = {
                "headline": "54-16",
                "label": "Liverpool vs City at Anfield",
                "supporting": [
                    {"value": "97", "label": "Total Games"},
                    {"value": "27", "label": "Draws"}
                ]
            }
        
        path = create_stat_graphic(stat_data)
        print(f"   📊 Graphic: {path}")
        
        context = {"opponent": "Manchester City", "date": "2026-02-08", "stat_json": str(stat_data)}
        variants = generate_variants("stat_graphic", context)
        print(f"   📝 Caption: {variants['variant_a']['caption'][:100]}...")
        
    elif post['type'] == 'famous_red':
        context = {
            "name": "Demis Hassabis",
            "achievement": "Nobel Prize in Chemistry 2024",
            "lfc_connection": "Lifelong Liverpool supporter",
            "opponent": "Manchester City"
        }
        variants = generate_variants("famous_red", context)
        print(f"   📝 Caption: {variants['variant_c']['caption'][:100]}...")
        
    elif post['type'] == 'comedy_banter':
        context = {
            "opponent": "Manchester City",
            "date": "2026-02-08",
            "topic": "115 charges vs Liverpool's organic success", 
            "angle": "History vs oil money"
        }
        variants = generate_variants("comedy_banter", context)
        print(f"   📝 Caption: {variants['variant_b']['caption'][:100]}...")
        
    else:  # iconic_moment, crowd_atmosphere
        if 'crowd' in post['type']:
            context = {
                "opponent": "Manchester City",
                "date": "2026-02-08",
                "asset_description": "YNWA being sung at Anfield before big match"
            }
            variants = generate_variants("crowd_atmosphere", context)
        else:
            context = {
                "opponent": "Manchester City",
                "date": "2026-02-08", 
                "asset_description": "Klopp celebrating with fans",
                "context": "Manager-crowd connection moments"
            }
            variants = generate_variants("iconic_moment", context)
            
        print(f"   📝 Caption: {variants['variant_a']['caption'][:100]}...")

print(f"\n🔥 7 POSTS GENERATED - Ready for manual posting!")
print(f"📋 Next: Copy captions + upload images to Instagram")