#!/usr/bin/env python3
"""
AlphaENRG EMERGENCY 100 FOLLOWERS CAMPAIGN
CRITICAL MISSION: 0 → 100 followers by 5 PM GMT (4 hours remaining)

EXECUTION STRATEGY:
1. Viral content every 30 minutes
2. Aggressive engagement on high-traffic posts  
3. Strategic following of energy professionals
4. Newsletter CTA in every interaction
5. Hourly progress tracking
"""

import tweepy
import os
import time
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import random
import subprocess
import sys

load_dotenv()

class Emergency100Followers:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )
        
        # Campaign tracking
        self.start_time = datetime.now(timezone.utc)
        self.deadline = self.start_time.replace(hour=17, minute=0, second=0, microsecond=0)
        self.target_followers = 100
        self.hourly_targets = [25, 50, 75, 100]  # Follower targets per hour
        
        # Track campaign stats
        self.stats = {
            'viral_posts': 0,
            'viral_replies': 0,
            'strategic_follows': 0,
            'newsletter_mentions': 0,
            'current_followers': 0
        }
    
    def get_current_followers(self):
        """Get current follower count"""
        try:
            user = self.client.get_me()
            if user and user.data:
                me = self.client.get_user(user.data.id, user_fields=['public_metrics'])
                if me and me.data and hasattr(me.data, 'public_metrics'):
                    followers = me.data.public_metrics['followers_count']
                    self.stats['current_followers'] = followers
                    return followers
        except Exception as e:
            print(f"⚠️ Error getting follower count: {e}")
        
        return self.stats['current_followers']
    
    def time_remaining(self):
        """Calculate time remaining until deadline"""
        now = datetime.now(timezone.utc)
        remaining = self.deadline - now
        
        if remaining.total_seconds() <= 0:
            return "DEADLINE PASSED"
        
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def calculate_required_rate(self):
        """Calculate required followers per hour to hit target"""
        current = self.get_current_followers()
        needed = self.target_followers - current
        
        now = datetime.now(timezone.utc)
        remaining_seconds = (self.deadline - now).total_seconds()
        remaining_hours = remaining_seconds / 3600
        
        if remaining_hours <= 0:
            return 0
        
        return round(needed / remaining_hours, 1)
    
    def campaign_status_report(self):
        """Generate detailed campaign status"""
        current = self.get_current_followers()
        needed = self.target_followers - current
        rate_needed = self.calculate_required_rate()
        time_left = self.time_remaining()
        
        print("="*60)
        print("🚨 ALPHAENRG EMERGENCY FOLLOWER CAMPAIGN STATUS")
        print("="*60)
        print(f"⏰ Time Remaining: {time_left}")
        print(f"📊 Current Followers: {current}")
        print(f"🎯 Target Followers: {self.target_followers}")
        print(f"📈 Followers Needed: {needed}")
        print(f"⚡ Required Rate: {rate_needed} followers/hour")
        print("")
        print("📊 CAMPAIGN STATS:")
        print(f"🚀 Viral Posts: {self.stats['viral_posts']}")
        print(f"💬 Viral Replies: {self.stats['viral_replies']}")
        print(f"👥 Strategic Follows: {self.stats['strategic_follows']}")
        print(f"📧 Newsletter CTAs: {self.stats['newsletter_mentions']}")
        print("="*60)
        
        # Alert if rate is too high
        if rate_needed > 30:
            print("🚨 WARNING: Required rate exceeds 30 followers/hour!")
            print("💡 Recommendation: Increase viral content frequency")
            print("🎯 Focus on highest-engagement opportunities")
        
        return {
            'current': current,
            'needed': needed,
            'rate_needed': rate_needed,
            'time_left': time_left
        }
    
    def execute_viral_content_burst(self):
        """Execute viral content posting"""
        print("\n🔥 EXECUTING VIRAL CONTENT BURST")
        
        try:
            # Run viral content generator
            result = subprocess.run([
                sys.executable, 'viral_content_generator.py'
            ], cwd='energy-agent', capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Viral content campaign completed!")
                self.stats['viral_posts'] += 4  # 4 posts per burst
                self.stats['newsletter_mentions'] += 4
            else:
                print(f"❌ Viral content failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error executing viral content: {e}")
    
    def execute_aggressive_engagement(self):
        """Execute aggressive engagement campaign"""
        print("\n💥 EXECUTING AGGRESSIVE ENGAGEMENT")
        
        try:
            # Run aggressive engagement
            result = subprocess.run([
                sys.executable, 'aggressive_engagement.py'  
            ], cwd='energy-agent', capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("✅ Aggressive engagement completed!")
                self.stats['viral_replies'] += 10  # Estimated replies per burst
                self.stats['newsletter_mentions'] += 10
            else:
                print(f"❌ Aggressive engagement failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error executing engagement: {e}")
    
    def execute_strategic_following(self):
        """Execute strategic following campaign"""
        print("\n👥 EXECUTING STRATEGIC FOLLOWING")
        
        # High-value energy accounts to follow
        energy_targets = [
            'EnergyGangster', 'CleanTechnica', 'EnergyIntel', 'NuclearEnergyX',
            'RenewablesNow', 'SolarPowerMag', 'EnergyTransition', 'GridModernNews',
            'NuclearIndustry', 'CleanEnergyNews', 'StorageIndustry', 'WindPowerEng'
        ]
        
        follows_executed = 0
        target_follows = 20  # Conservative batch
        
        for username in random.sample(energy_targets, min(len(energy_targets), target_follows)):
            try:
                user = self.client.get_user(username=username)
                if user and user.data:
                    user_id = user.data.id
                    
                    # Follow the user
                    follow_result = self.client.follow_user(user_id)
                    
                    if follow_result:
                        print(f"✅ Followed @{username}")
                        follows_executed += 1
                        self.stats['strategic_follows'] += 1
                        
                        # Brief delay to avoid rate limits
                        time.sleep(3)
                    else:
                        print(f"❌ Failed to follow @{username}")
                        
            except Exception as e:
                print(f"⚠️ Error following @{username}: {e}")
                continue
                
            if follows_executed >= 10:  # Conservative limit per batch
                break
        
        print(f"📊 Strategic follows completed: {follows_executed}")
    
    def execute_full_campaign_cycle(self):
        """Execute one complete campaign cycle"""
        print("\n🚀 STARTING FULL CAMPAIGN CYCLE")
        print("="*50)
        
        # 1. Status report
        status = self.campaign_status_report()
        
        # 2. Viral content burst
        self.execute_viral_content_burst()
        time.sleep(30)  # Brief pause
        
        # 3. Aggressive engagement
        self.execute_aggressive_engagement()  
        time.sleep(30)  # Brief pause
        
        # 4. Strategic following
        self.execute_strategic_following()
        
        # 5. Final status update
        print("\n📊 CAMPAIGN CYCLE COMPLETE!")
        final_followers = self.get_current_followers()
        cycle_growth = final_followers - status['current']
        
        print(f"📈 Followers gained this cycle: +{cycle_growth}")
        print(f"📊 Current total: {final_followers}")
        
        return cycle_growth
    
    def run_emergency_campaign(self):
        """Run the full emergency campaign until deadline"""
        print("🚨 ALPHAENRG EMERGENCY 100 FOLLOWERS CAMPAIGN")
        print("⚡ MISSION: CRITICAL FOLLOWER ACCELERATION")
        print("🎯 DEADLINE: 5 PM GMT")
        print("="*60)
        
        cycle_count = 0
        
        while datetime.now(timezone.utc) < self.deadline:
            cycle_count += 1
            print(f"\n🔄 CAMPAIGN CYCLE #{cycle_count}")
            
            growth = self.execute_full_campaign_cycle()
            
            current = self.get_current_followers()
            if current >= self.target_followers:
                print("\n🎉 🎉 🎉 MISSION ACCOMPLISHED! 🎉 🎉 🎉")
                print(f"✅ Target reached: {current} followers")
                print("🚀 AlphaENRG 100 followers achieved!")
                break
            
            # Wait before next cycle (30 minutes)
            next_cycle = datetime.now(timezone.utc) + timedelta(minutes=30)
            
            if next_cycle < self.deadline:
                wait_minutes = 30
                print(f"\n⏰ Waiting {wait_minutes} minutes before next cycle...")
                print(f"🔄 Next cycle at: {next_cycle.strftime('%H:%M GMT')}")
                
                time.sleep(wait_minutes * 60)
            else:
                print("\n⏰ Not enough time for another full cycle")
                break
        
        # Final campaign report
        print("\n" + "="*60)
        print("📊 FINAL CAMPAIGN REPORT")
        print("="*60)
        
        final_status = self.campaign_status_report()
        
        if final_status['current'] >= self.target_followers:
            print("🎉 SUCCESS: 100 follower target achieved!")
        else:
            print(f"⚠️ Target not reached. Final count: {final_status['current']}")
            print(f"📈 Growth achieved: {final_status['current'] - 0} followers")
        
        print("\n🚀 AlphaENRG Emergency Campaign Complete!")

if __name__ == "__main__":
    campaign = Emergency100Followers()
    campaign.run_emergency_campaign()