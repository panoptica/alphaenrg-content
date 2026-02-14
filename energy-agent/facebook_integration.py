#!/usr/bin/env python3
"""
Facebook Integration for AlphaENRG - Auto-publish to Facebook Page
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
import json

load_dotenv()

class FacebookPublisher:
    def __init__(self):
        """Initialize Facebook Graph API client"""
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.base_url = 'https://graph.facebook.com/v19.0'
        
        if not self.access_token or not self.page_id:
            raise ValueError("Missing Facebook credentials. Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env")

    def post_to_page(self, message, link=None, image_url=None):
        """Post content to Facebook Page"""
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        payload = {
            'message': message,
            'access_token': self.access_token
        }
        
        # Add link if provided
        if link:
            payload['link'] = link
        
        # Add image if provided  
        if image_url:
            payload['picture'] = image_url
            
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if 'id' in result:
                print(f"✅ Facebook post successful!")
                print(f"📋 Post ID: {result['id']}")
                print(f"🔗 URL: https://facebook.com/{result['id']}")
                return result['id']
            else:
                print(f"❌ Facebook posting failed: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Facebook API error: {e}")
            return False

    def post_daily_intelligence(self, intelligence_summary, signals_count=0):
        """Post daily intelligence summary to Facebook"""
        
        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y")
        
        # Create engaging Facebook post
        facebook_text = f"""⚡ AlphaENRG Daily Energy Intelligence • {timestamp}

{intelligence_summary}

📊 Today's Analysis:
• {signals_count} new energy signals processed
• Institutional-grade research synthesis  
• AI-powered market trend identification

🎯 Actionable insights for clean energy investors
🔬 Data sources: ArXiv research + Patent filings + SEC data

#EnergyIntelligence #CleanTech #InvestmentSignals #RenewableEnergy #QuantumComputing

Stay ahead of energy market movements with AlphaENRG intelligence."""

        return self.post_to_page(facebook_text)

    def post_breaking_alert(self, alert_text, urgency="HIGH"):
        """Post breaking energy market alert"""
        
        urgency_emojis = {
            "CRITICAL": "🚨🔥",
            "HIGH": "⚡📈", 
            "MEDIUM": "📊💡",
            "LOW": "📋📌"
        }
        
        emoji = urgency_emojis.get(urgency, "📊")
        
        facebook_text = f"""{emoji} BREAKING ENERGY INTELLIGENCE

{alert_text}

🎯 AlphaENRG real-time analysis has flagged this development as potentially market-moving for energy sector investors.

⏱️ Alert Level: {urgency}
🤖 Automated intelligence synthesis
📊 Institutional-grade analysis

#BreakingNews #EnergyMarkets #AlphaSignals #InvestmentAlert"""

        return self.post_to_page(facebook_text)

    def schedule_post(self, message, scheduled_publish_time):
        """Schedule a post for future publication"""
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        payload = {
            'message': message,
            'published': False,  # Draft mode
            'scheduled_publish_time': scheduled_publish_time,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Facebook post scheduled for {scheduled_publish_time}")
            print(f"📋 Draft ID: {result.get('id', 'Unknown')}")
            return result.get('id')
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Facebook scheduling error: {e}")
            return False

def integrate_with_daily_agent(intelligence_text, signals_count=0):
    """Integration function for the main energy agent"""
    
    try:
        publisher = FacebookPublisher()
        
        # Extract key insights for Facebook post
        summary_lines = intelligence_text.split('\n')[:4]  # First 4 lines
        summary = '\n'.join(summary_lines)
        
        # Post to Facebook
        success = publisher.post_daily_intelligence(summary, signals_count)
        
        return success
        
    except ValueError as e:
        print(f"⚠️ Facebook integration not configured: {e}")
        return None
    except Exception as e:
        print(f"❌ Facebook posting error: {e}")
        return False

if __name__ == "__main__":
    # Test posting
    test_intelligence = """🔋 Quantum battery breakthrough patents filed by 3 major tech companies this week

🌊 Offshore wind development accelerating in Northern Europe  

⚡ Grid storage innovations reaching commercial viability

💰 Clean energy VC funding up 23% quarter-over-quarter"""
    
    result = integrate_with_daily_agent(test_intelligence, signals_count=156)
    print(f"Test posting result: {result}")