#!/usr/bin/env python3
"""
Schedule LFC Agent posts using OpenClaw cron
"""

import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from fixtures.monitor import FixtureMonitor

def schedule_with_openclaw():
    """Schedule posts using OpenClaw cron system"""
    
    print("🔴 SCHEDULING LFC POSTS WITH OPENCLAW CRON")
    print("=" * 50)
    
    # Get fixture and schedule
    monitor = FixtureMonitor()
    fixture = monitor.get_next_fixture()
    schedule = monitor.get_content_schedule(fixture)
    
    print(f"📅 Fixture: LFC vs {fixture['opponent']}")
    print(f"⏰ Match: {fixture['date']}")
    print(f"📋 Posts to schedule: {len(schedule)}")
    
    # OpenClaw gateway URL (adjust if needed)
    gateway_url = "http://localhost:18789"
    
    jobs_created = 0
    
    for post in schedule:
        # Create cron job for each post
        scheduled_time = post['scheduled']
        
        # Format for cron (ISO string)
        cron_time = scheduled_time.isoformat() + 'Z'
        
        # Job payload - runs the automation script
        job_data = {
            "name": f"LFC Post - {post['day']} {post['time']} ({post['content_type']})",
            "schedule": {
                "kind": "at",
                "atMs": int(scheduled_time.timestamp() * 1000)
            },
            "payload": {
                "kind": "systemEvent",
                "text": f"🔴 LFC Agent: Posting {post['content_type']} content for {fixture['opponent']} match"
            },
            "sessionTarget": "main",
            "enabled": True
        }
        
        try:
            # Create the cron job
            response = requests.post(
                f"{gateway_url}/api/cron",
                json={"action": "add", "job": job_data},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Scheduled: {post['day']} {post['time']} - {post['content_type']}")
                jobs_created += 1
            else:
                print(f"❌ Failed to schedule: {post['day']} {post['time']}")
                
        except Exception as e:
            print(f"❌ Error scheduling {post['day']} {post['time']}: {e}")
    
    print(f"\\n🔥 Scheduled {jobs_created}/{len(schedule)} posts successfully!")
    
    if jobs_created > 0:
        print(f"\\n📋 To view scheduled jobs: openclaw cron list")
        print(f"📋 To run a job manually: openclaw cron run <jobId>")
    
    return jobs_created

def create_posting_command():
    """Create a standalone posting command"""
    command_script = Path(__file__).parent / 'post_now.py'
    
    with open(command_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Run LFC Agent posting now
"""

import sys
import asyncio
from pathlib import Path

# Add src to path  
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from automation.scheduler import LFCContentScheduler

async def post_now():
    scheduler = LFCContentScheduler()
    
    # Get next post to make
    fixture = scheduler.monitor.get_next_fixture()
    schedule = scheduler.monitor.get_content_schedule(fixture)
    
    print(f"🔴 Posting next scheduled content...")
    
    # Find the next post that should be posted
    for post in schedule:
        result = await scheduler.post_scheduled_content(post, dry_run=False)
        break  # Just do the first one
    
    print(f"✅ Posting complete")

if __name__ == "__main__":
    asyncio.run(post_now())
''')
    
    os.chmod(command_script, 0o755)
    print(f"📝 Created posting command: {command_script}")

if __name__ == "__main__":
    schedule_with_openclaw()
    create_posting_command()