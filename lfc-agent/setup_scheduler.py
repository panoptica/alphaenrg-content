#!/usr/bin/env python3
"""
Set up macOS launchd jobs for LFC Agent posting
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

def create_launchd_job(name, time_str, script_path):
    """Create a launchd plist file"""
    
    # Parse time (e.g., "Friday 11:00")
    day_map = {"Friday": 5, "Saturday": 6, "Sunday": 0}  # launchd weekday format
    day, time = time_str.split(" ")
    hour, minute = map(int, time.split(":"))
    weekday = day_map[day]
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lfcagent.{name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/macmini/lfc-agent/venv/bin/python</string>
        <string>{script_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>{weekday}</integer>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>/Users/macmini/lfc-agent</string>
    <key>StandardOutPath</key>
    <string>/Users/macmini/lfc-agent/logs/cron.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/macmini/lfc-agent/logs/cron.log</string>
</dict>
</plist>"""
    
    # Create plist file
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(exist_ok=True)
    
    plist_file = plist_dir / f"com.lfcagent.{name}.plist"
    with open(plist_file, 'w') as f:
        f.write(plist_content)
    
    return plist_file

def setup_lfc_scheduler():
    """Set up all LFC posting jobs"""
    print("🔴 SETTING UP LFC AGENT SCHEDULER")
    print("=" * 50)
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create post script
    post_script = Path("scripts/post_single.py")
    post_script_content = '''#!/usr/bin/env python3
import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from automation.scheduler import LFCContentScheduler

async def post_next():
    scheduler = LFCContentScheduler()
    fixture = scheduler.monitor.get_next_fixture()
    schedule = scheduler.monitor.get_content_schedule(fixture)
    
    # Find next post to make based on current time
    from datetime import datetime
    now = datetime.now()
    
    for post in schedule:
        # Simple logic - just post the first one for now
        result = await scheduler.post_scheduled_content(post, dry_run=False)
        print(f"Posted: {post['content_type']} - {result['status']}")
        break

if __name__ == "__main__":
    asyncio.run(post_next())
'''
    
    with open(post_script, 'w') as f:
        f.write(post_script_content)
    os.chmod(post_script, 0o755)
    
    # Schedule times for City match
    schedule_times = [
        ("friday11", "Friday 11:00"),
        ("friday19", "Friday 19:00"), 
        ("saturday09", "Saturday 09:00"),
        ("saturday13", "Saturday 13:00"),
        ("saturday17", "Saturday 17:00"),
        ("sunday10", "Sunday 10:00"),
        ("sunday14", "Sunday 14:00"),
    ]
    
    jobs_created = 0
    for name, time_str in schedule_times:
        try:
            plist_file = create_launchd_job(name, time_str, str(post_script.absolute()))
            print(f"✅ Created job: {time_str} -> {plist_file}")
            
            # Load the job
            os.system(f"launchctl load {plist_file}")
            jobs_created += 1
            
        except Exception as e:
            print(f"❌ Failed to create {time_str}: {e}")
    
    print(f"\n🔥 Created {jobs_created}/7 scheduled jobs!")
    print(f"\nTo check jobs: launchctl list | grep lfcagent")
    print(f"To remove jobs: launchctl remove com.lfcagent.<name>")

if __name__ == "__main__":
    setup_lfc_scheduler()