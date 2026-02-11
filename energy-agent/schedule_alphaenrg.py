#!/usr/bin/env python3
"""
Schedule AlphaENRG for automated daily posting and engagement
"""

import schedule
import time
import subprocess
import os
from datetime import datetime

def run_daily_intelligence():
    """Run the daily intelligence post"""
    print(f"🚀 {datetime.now()}: Running AlphaENRG daily intelligence...")
    
    try:
        # Change to energy-agent directory
        os.chdir('/Users/macmini/.openclaw/workspace/energy-agent')
        
        # Activate venv and run
        result = subprocess.run([
            'bash', '-c', 
            'source venv/bin/activate && python alphaenrg_engine.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ AlphaENRG daily intelligence posted successfully!")
        else:
            print(f"❌ Error running daily intelligence: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Failed to run daily intelligence: {e}")

def run_engagement_blitz():
    """Run engagement activities"""
    print(f"🤝 {datetime.now()}: Running AlphaENRG engagement...")
    
    # Import and run engagement functions
    from alphaenrg_engine import AlphaENRGEngine
    
    engine = AlphaENRGEngine()
    engine.engage_with_energy_sector()

def main():
    """Set up AlphaENRG posting schedule"""
    
    print("🎯 Setting up AlphaENRG automated schedule...")
    print("=" * 50)
    
    # Daily intelligence at 7:00 AM GMT
    schedule.every().day.at("07:00").do(run_daily_intelligence)
    
    # Additional engagement throughout the day
    schedule.every().day.at("12:30").do(run_engagement_blitz)  # Lunch time engagement
    schedule.every().day.at("18:00").do(run_engagement_blitz)  # Evening engagement
    
    print("📅 AlphaENRG Schedule:")
    print("• 07:00 GMT: Daily Intelligence Thread")
    print("• 12:30 GMT: Midday Engagement")  
    print("• 18:00 GMT: Evening Engagement")
    print("\n🚀 AlphaENRG will dominate X automatically!")
    print("Press Ctrl+C to stop scheduler\n")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Run one immediate cycle for testing
    print("🔥 Running immediate AlphaENRG cycle for testing...")
    run_daily_intelligence()
    
    # Then start scheduler
    main()