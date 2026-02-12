#!/usr/bin/env python3
"""
Test real Instagram posting
"""

import asyncio
import sys
sys.path.append('src')
from automation.instagram_poster import InstagramPoster
from visuals.compositor import create_stat_graphic

async def test_real_post():
    print("🔴 TESTING FULL POST WORKFLOW")
    print("=" * 50)
    
    # Create a test image
    print("1️⃣ Creating test graphic...")
    stat_data = {
        "headline": "92 WINS",
        "label": "Liverpool vs City (All Time)",
        "supporting": [
            {"value": "54", "label": "Home Wins"},
            {"value": "16", "label": "City Wins"}
        ]
    }
    image_path = create_stat_graphic(stat_data)
    print(f"   📊 Image created: {image_path}")
    
    caption = """🔴 The numbers don't lie. 92 wins. 54 at Anfield alone.

This is what history looks like. Sunday, we add to it.

#LFC #YNWA #LiverpoolFC #Liverpool #ManchesterCity #MCILIV #PremierLeague #Anfield #Football"""
    
    print("2️⃣ Logging into Instagram...")
    poster = InstagramPoster(headless=True)
    
    try:
        await poster.start_browser()
        await poster.login()
        print("   ✅ Login successful")
        
        print("3️⃣ Posting to Instagram...")
        result = await poster.post_image(image_path, caption, dry_run=False)
        
        if result["status"] == "success":
            print("🔥 POST SUCCESSFUL!")
        else:
            print(f"❌ Post failed: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await poster.close()

if __name__ == "__main__":
    asyncio.run(test_real_post())