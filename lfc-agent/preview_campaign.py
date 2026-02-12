#!/usr/bin/env python3
"""
Preview the LFC City match campaign
Shows what will be posted without actually posting
"""

import sys
import asyncio
from pathlib import Path

sys.path.append('src')
from automation.scheduler import LFCContentScheduler

async def preview_campaign():
    print("🔍 LFC vs CITY CAMPAIGN PREVIEW")
    print("=" * 50)
    
    scheduler = LFCContentScheduler()
    fixture = scheduler.monitor.get_next_fixture()
    schedule = scheduler.monitor.get_content_schedule(fixture)
    
    print(f"📅 Match: LFC vs {fixture['opponent']}")
    print(f"⏰ Days until: {fixture['days_until']}")
    print(f"📋 Posts: {len(schedule)} scheduled")
    print()
    
    for i, post in enumerate(schedule):
        print(f"{i+1}️⃣  {post['day']} {post['time']}: {post['content_type']}")
        
        # Generate preview for first 3 posts
        if i < 3:
            try:
                print("    🎨 Generating content...")
                content = scheduler.generate_content_for_post(post)
                
                # Show caption preview
                caption = content['caption']
                preview_caption = caption[:150] + "..." if len(caption) > 150 else caption
                print(f"    💬 Caption: {preview_caption}")
                
                # Show image info
                image_name = Path(content['image_path']).name
                print(f"    📊 Image: {image_name}")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
        else:
            print(f"    ⏸️  (Preview available - run with --full to see all)")
        
        print()
    
    print("🔥 CAMPAIGN READY FOR SCHEDULING!")
    print()
    print("Next steps:")
    print("1. Schedule with cron")
    print("2. Or run: python launch_campaign.py")

if __name__ == "__main__":
    asyncio.run(preview_campaign())