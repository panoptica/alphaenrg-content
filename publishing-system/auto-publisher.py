#!/usr/bin/env python3
"""
Auto Publisher - Integrates with Energy Agent
Reads daily signals and publishes to X automatically
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from x_publisher import XPublisher

def load_energy_signals(date_str=None):
    """Load signals from energy agent output"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Look for energy agent output files
    possible_paths = [
        f"../energy-agent/output/signals-{date_str}.json",
        f"../energy-agent/signals-{date_str}.json", 
        f"energy-agent/output/signals-{date_str}.json",
        f"signals-{date_str}.json",
        f"test-signals-{date_str}.json"  # Test data
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"📂 Loading signals from: {path}")
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get('signals', data) if isinstance(data, dict) else data
    
    print(f"⚠️ No signals file found for {date_str}")
    print("   Searched:", possible_paths)
    return []

def filter_signals(signals, min_score=7.0, max_count=3):
    """Filter and rank signals for publishing"""
    if not signals:
        return []
    
    # Filter by score
    high_value_signals = [s for s in signals if s.get('score', 0) >= min_score]
    
    # Sort by score descending
    sorted_signals = sorted(high_value_signals, key=lambda x: x.get('score', 0), reverse=True)
    
    return sorted_signals[:max_count]

def should_publish_today():
    """Check if we should publish today (avoid spam)"""
    # Simple logic: publish if we have good signals and haven't posted in last 20 hours
    last_publish_file = "last_publish.txt"
    
    if not os.path.exists(last_publish_file):
        return True
        
    with open(last_publish_file, 'r') as f:
        last_publish_str = f.read().strip()
    
    try:
        last_publish = datetime.fromisoformat(last_publish_str)
        hours_since = (datetime.now() - last_publish).total_seconds() / 3600
        return hours_since >= 20  # At least 20 hours between posts
    except:
        return True

def record_publish():
    """Record that we published today"""
    with open("last_publish.txt", 'w') as f:
        f.write(datetime.now().isoformat())

def main():
    """Main auto-publisher logic"""
    print(f"🚀 Auto Publisher starting at {datetime.now()}")
    
    # Load environment settings
    min_score = float(os.getenv('MIN_SIGNAL_SCORE', '7.0'))
    max_signals = int(os.getenv('MAX_SIGNALS_PER_THREAD', '3'))
    
    # Check if we should publish
    if not should_publish_today():
        print("⏭️ Skipping publish - posted recently")
        return
    
    # Load today's signals
    signals = load_energy_signals()
    if not signals:
        print("❌ No signals found - skipping publish")
        return
    
    print(f"📊 Loaded {len(signals)} total signals")
    
    # Filter for publishing
    publish_signals = filter_signals(signals, min_score, max_signals)
    
    if not publish_signals:
        print(f"❌ No signals meet publishing criteria (score >= {min_score})")
        return
    
    print(f"✅ {len(publish_signals)} signals selected for publishing")
    for signal in publish_signals:
        print(f"   • {signal.get('title', 'Untitled')} (score: {signal.get('score', 'N/A')})")
    
    # Initialize publisher
    publisher = XPublisher()
    if not publisher.client:
        print("❌ X publisher not configured - check credentials")
        return
    
    # Generate and publish thread
    thread = publisher.signal_to_thread(publish_signals)
    
    print("\n📝 Generated thread preview:")
    for i, tweet in enumerate(thread[:2]):  # Show first 2 tweets
        print(f"\nTweet {i+1}: {tweet[:100]}...")
    
    # Ask for confirmation in interactive mode
    if len(sys.argv) == 1:  # No args = interactive
        confirm = input("\n🤔 Publish this thread? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Publish cancelled")
            return
    
    # Publish the thread
    if publisher.publish_thread(thread):
        record_publish()
        print("🎉 Thread published successfully!")
    else:
        print("❌ Failed to publish thread")

if __name__ == "__main__":
    main()