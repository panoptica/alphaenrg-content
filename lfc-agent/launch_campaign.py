#!/usr/bin/env python3
"""
Launch LFC City match campaign
Run this manually when you want to post
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from automation.scheduler import LFCContentScheduler

async def launch_campaign():
    print("🔴 LAUNCHING LFC vs CITY CAMPAIGN")
    print("=" * 50)
    
    scheduler = LFCContentScheduler()
    
    # Show what will be posted
    fixture = scheduler.monitor.get_next_fixture()
    schedule = scheduler.monitor.get_content_schedule(fixture)
    
    print(f"📅 Match: LFC vs {fixture['opponent']}")
    print(f"⏰ {fixture['days_until']} days until kickoff")
    print(f"📋 Campaign: {len(schedule)} posts ready")
    print()
    
    for i, post in enumerate(schedule):
        print(f"{i+1}. {post['day']} {post['time']}: {post['content_type']}")
    
    print()
    response = input("🚀 Launch campaign? (y/N): ")
    
    if response.lower() == 'y':
        print("\n🔥 LAUNCHING CAMPAIGN...")
        
        # Run full campaign (dry run first)
        results = await scheduler.run_full_campaign(dry_run=True)
        
        print(f"\n✅ Generated {len(results)} posts")
        
        # Ask if ready to go live
        live_response = input("\n📸 Post to Instagram now? (y/N): ")
        
        if live_response.lower() == 'y':
            print("\n🔴 GOING LIVE...")
            live_results = await scheduler.run_full_campaign(dry_run=False)
            print(f"🔥 Posted {len(live_results)} to Instagram!")
        else:
            print("📝 Content generated - ready for manual posting")
    else:
        print("Campaign cancelled")

if __name__ == "__main__":
    asyncio.run(launch_campaign())