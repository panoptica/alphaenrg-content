#!/usr/bin/env python3
"""
Daily OpenClaw Intelligence Brief
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from research import OpenClawResearcher
from email_generator import IntelligenceEmailer
from datetime import datetime
import json

def main():
    print("🚀 OpenClaw Daily Intelligence Brief")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    try:
        # 1. Research
        print("\n🔍 PHASE 1: Research")
        researcher = OpenClawResearcher()
        findings = researcher.research_daily()
        
        # 2. Generate and send email
        print("\n📧 PHASE 2: Email Generation")
        emailer = IntelligenceEmailer()
        success = emailer.send_email(findings, "oc@cloudmonkey.io")
        
        if success:
            print("✅ Daily intelligence brief delivered successfully!")
        else:
            print("❌ Failed to send email, but research data saved")
            
        # 3. Archive findings
        os.makedirs("archive", exist_ok=True)
        archive_file = f"archive/intel_{findings['date']}.json"
        
        with open(archive_file, 'w') as f:
            json.dump(findings, f, indent=2)
        
        print(f"📁 Research archived: {archive_file}")
        
    except Exception as e:
        print(f"❌ Error in daily intelligence: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())