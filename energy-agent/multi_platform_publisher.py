#!/usr/bin/env python3
"""
Multi-Platform Publisher for AlphaENRG
Publishes content to X/Twitter, Facebook, and Substack simultaneously
"""

import os
import sys
from datetime import datetime, timezone
import json
from dotenv import load_dotenv

# Import our platform-specific publishers
from x_integration import AlphaENRGPoster as XPoster
from x_articles_integration import XArticlesPublisher
from facebook_integration import FacebookPublisher
from substack_integration import SubstackPublisher

load_dotenv()

class MultiPlatformPublisher:
    def __init__(self):
        """Initialize all platform publishers"""
        self.platforms = {}
        self.failed_platforms = []
        
        # Initialize X/Twitter
        try:
            self.platforms['twitter'] = XPoster()
            print("✅ Twitter/X initialized")
        except Exception as e:
            print(f"❌ Twitter/X initialization failed: {e}")
            self.failed_platforms.append('twitter')
        
        # Initialize X Articles
        try:
            self.platforms['x_articles'] = XArticlesPublisher()
            print("✅ X Articles initialized")
        except Exception as e:
            print(f"⚠️ X Articles initialization failed: {e}")
            self.failed_platforms.append('x_articles')
        
        # Initialize Facebook
        try:
            self.platforms['facebook'] = FacebookPublisher()
            print("✅ Facebook initialized")
        except Exception as e:
            print(f"⚠️ Facebook initialization failed: {e}")
            self.failed_platforms.append('facebook')
        
        # Initialize Substack
        try:
            self.platforms['substack'] = SubstackPublisher()
            print("✅ Substack initialized")
        except Exception as e:
            print(f"⚠️ Substack initialization failed: {e}")
            self.failed_platforms.append('substack')
    
    def publish_daily_intelligence(self, intelligence_text, signals_count=0, platforms=None):
        """
        Publish daily intelligence to multiple platforms
        
        Args:
            intelligence_text (str): The main intelligence content
            signals_count (int): Number of signals processed
            platforms (list): Specific platforms to publish to, or None for all
        """
        
        if platforms is None:
            platforms = ['twitter', 'facebook', 'substack']
        
        results = {}
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        
        print(f"\n🚀 Multi-Platform Publishing Started • {timestamp}")
        print("=" * 60)
        
        # Twitter/X Publishing
        if 'twitter' in platforms and 'twitter' in self.platforms:
            print("\n🐦 Publishing to Twitter/X...")
            try:
                # Extract summary for Twitter (character limit)
                twitter_summary = self._format_for_twitter(intelligence_text)
                success = self.platforms['twitter'].post_daily_intelligence(twitter_summary)
                results['twitter'] = {'success': success, 'platform': 'Twitter/X'}
                
                if success:
                    print("✅ Twitter/X: SUCCESS")
                else:
                    print("❌ Twitter/X: FAILED")
                    
            except Exception as e:
                print(f"❌ Twitter/X: ERROR - {e}")
                results['twitter'] = {'success': False, 'error': str(e)}
        
        # Facebook Publishing  
        if 'facebook' in platforms and 'facebook' in self.platforms:
            print("\n📘 Publishing to Facebook...")
            try:
                facebook_summary = self._format_for_facebook(intelligence_text)
                success = self.platforms['facebook'].post_daily_intelligence(facebook_summary, signals_count)
                results['facebook'] = {'success': success, 'platform': 'Facebook'}
                
                if success:
                    print("✅ Facebook: SUCCESS")
                else:
                    print("❌ Facebook: FAILED")
                    
            except Exception as e:
                print(f"❌ Facebook: ERROR - {e}")
                results['facebook'] = {'success': False, 'error': str(e)}
        
        # Substack Publishing
        if 'substack' in platforms and 'substack' in self.platforms:
            print("\n📝 Publishing to Substack...")
            try:
                substack_content = self._format_for_substack(intelligence_text)
                success = self.platforms['substack'].create_daily_intelligence_article(substack_content, signals_count)
                results['substack'] = {'success': success, 'platform': 'Substack'}
                
                if success:
                    print("✅ Substack: SUCCESS")
                else:
                    print("❌ Substack: FAILED")
                    
            except Exception as e:
                print(f"❌ Substack: ERROR - {e}")
                results['substack'] = {'success': False, 'error': str(e)}
        
        # Summary
        self._print_summary(results)
        return results
    
    def _format_for_twitter(self, text):
        """Format content for Twitter's character limit"""
        lines = text.split('\n')[:3]  # First 3 lines
        summary = '\n'.join(lines)
        
        # Truncate if too long (leave room for hashtags)
        if len(summary) > 180:
            summary = summary[:177] + "..."
        
        return summary
    
    def _format_for_facebook(self, text):
        """Format content for Facebook (longer form)"""
        lines = text.split('\n')[:5]  # First 5 lines
        return '\n'.join(lines)
    
    def _format_for_substack(self, text):
        """Format content for Substack (full article)"""
        # Return full text for Substack article
        return text
    
    def publish_as_x_article(self, intelligence_text, signals_count=0):
        """
        Publish intelligence as X Article/Thread (long-form content)
        """
        
        if 'x_articles' not in self.platforms:
            print("❌ X Articles not initialized")
            return False
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        
        print(f"\n📄 Publishing X Article/Thread • {timestamp}")
        print("=" * 60)
        
        try:
            result = self.platforms['x_articles'].publish_intelligence_article(intelligence_text, signals_count)
            
            if result and isinstance(result, dict):
                print(f"✅ X Article/Thread: SUCCESS")
                print(f"🔗 Thread URL: {result.get('thread_url', 'N/A')}")
                print(f"📊 {result.get('tweet_count', 0)} tweets in thread")
                return True
            elif result:
                print("✅ X Article/Thread: SUCCESS")
                return True
            else:
                print("❌ X Article/Thread: FAILED")
                return False
                
        except Exception as e:
            print(f"❌ X Article/Thread: ERROR - {e}")
            return False

    def _print_summary(self, results):
        """Print publishing summary"""
        print("\n" + "=" * 60)
        print("📊 PUBLISHING SUMMARY")
        print("=" * 60)
        
        successful = []
        failed = []
        
        for platform, result in results.items():
            if result['success']:
                successful.append(platform.upper())
            else:
                failed.append(platform.upper())
        
        if successful:
            print(f"✅ SUCCESSFUL: {', '.join(successful)}")
        
        if failed:
            print(f"❌ FAILED: {', '.join(failed)}")
        
        total = len(results)
        success_count = len(successful)
        
        print(f"\n📈 Success Rate: {success_count}/{total} ({(success_count/total*100):.0f}%)")
        
        if self.failed_platforms:
            print(f"\n⚠️ Platforms not configured: {', '.join(self.failed_platforms).upper()}")

    def publish_breaking_alert(self, alert_text, urgency="HIGH", platforms=None):
        """Publish breaking alert across platforms"""
        
        if platforms is None:
            platforms = ['twitter', 'facebook']  # Don't spam Substack with alerts
        
        results = {}
        
        print(f"\n🚨 BREAKING ALERT PUBLISHING • Urgency: {urgency}")
        print("=" * 60)
        
        # Twitter Alert
        if 'twitter' in platforms and 'twitter' in self.platforms:
            try:
                success = self.platforms['twitter'].post_breaking_alert(alert_text)
                results['twitter'] = {'success': success}
                print(f"🐦 Twitter: {'✅ SUCCESS' if success else '❌ FAILED'}")
            except Exception as e:
                print(f"🐦 Twitter: ❌ ERROR - {e}")
                results['twitter'] = {'success': False, 'error': str(e)}
        
        # Facebook Alert  
        if 'facebook' in platforms and 'facebook' in self.platforms:
            try:
                success = self.platforms['facebook'].post_breaking_alert(alert_text, urgency)
                results['facebook'] = {'success': success}
                print(f"📘 Facebook: {'✅ SUCCESS' if success else '❌ FAILED'}")
            except Exception as e:
                print(f"📘 Facebook: ❌ ERROR - {e}")
                results['facebook'] = {'success': False, 'error': str(e)}
        
        return results

def setup_all_platforms():
    """Setup authentication for all platforms"""
    
    print("🔧 Multi-Platform Setup")
    print("=" * 50)
    
    # Check environment variables
    required_vars = {
        'Twitter': ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET'],
        'Facebook': ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID'],
        'Substack': ['SUBSTACK_EMAIL', 'SUBSTACK_PASSWORD', 'SUBSTACK_URL']
    }
    
    missing_configs = []
    
    for platform, vars_list in required_vars.items():
        missing = [var for var in vars_list if not os.getenv(var)]
        if missing:
            missing_configs.append((platform, missing))
    
    if missing_configs:
        print("❌ Missing Configuration:")
        for platform, missing_vars in missing_configs:
            print(f"\n{platform}:")
            for var in missing_vars:
                print(f"  - {var}")
        
        print("\n📝 Please add these to your .env file")
        return False
    
    # Setup Substack authentication specifically
    print("\n🔐 Setting up Substack authentication...")
    from substack_integration import setup_substack_auth
    substack_success = setup_substack_auth()
    
    if substack_success:
        print("\n✅ All platforms configured successfully!")
        return True
    else:
        print("\n⚠️ Some platforms may not be fully configured")
        return False

def integrate_with_daily_agent(intelligence_text, signals_count=0, platforms=None):
    """Main integration function for the daily energy agent"""
    
    publisher = MultiPlatformPublisher()
    results = publisher.publish_daily_intelligence(intelligence_text, signals_count, platforms)
    
    # Return overall success status
    return any(result.get('success', False) for result in results.values())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        # Run platform setup
        setup_all_platforms()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test publishing
        test_intelligence = """🔋 quantum computing patents surge 47% this quarter

🌊 offshore wind development accelerating in northern europe

⚡ grid storage innovations reaching commercial viability

💰 clean energy VC funding up 23% quarter-over-quarter"""
        
        publisher = MultiPlatformPublisher()
        results = publisher.publish_daily_intelligence(test_intelligence, signals_count=156)
        
    elif len(sys.argv) > 1 and sys.argv[1] == "alert":
        # Test breaking alert
        test_alert = "Major breakthrough in solid-state battery technology announced by 3 automotive giants simultaneously"
        
        publisher = MultiPlatformPublisher()
        results = publisher.publish_breaking_alert(test_alert, urgency="HIGH")
        
    elif len(sys.argv) > 1 and sys.argv[1] == "article":
        # Test X Article publishing
        test_intelligence = """🔬 quantum computing patents surge 47% this quarter with breakthrough developments in error correction

🌊 offshore wind development accelerating across northern europe, new installations exceeding 2026 targets

⚡ grid storage innovations reaching commercial viability, costs dropping below critical thresholds

💰 clean energy VC funding up 23% quarter-over-quarter, signaling strong institutional confidence

🔋 solid-state battery patents from automotive giants suggest imminent commercial deployment

these developments suggest accelerating convergence in quantum computing, energy storage, and grid infrastructure"""
        
        publisher = MultiPlatformPublisher()
        result = publisher.publish_as_x_article(test_intelligence, signals_count=234)
        
    else:
        print("""
🚀 AlphaENRG Multi-Platform Publisher

Usage:
  python multi_platform_publisher.py setup    - Setup platform authentication
  python multi_platform_publisher.py test     - Test publishing to all platforms  
  python multi_platform_publisher.py alert    - Test breaking alert publishing
  python multi_platform_publisher.py article  - Test X Article/Thread publishing
        """)