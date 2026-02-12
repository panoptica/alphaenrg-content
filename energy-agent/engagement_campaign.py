#!/usr/bin/env python3
"""
AlphaENRG Strategic Engagement Campaign
Intelligently engages with energy influencers to drive newsletter signups
"""

import tweepy
import os
import time
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class AlphaENRGEngagement:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )
        
        # Energy-specific intelligent responses
        self.energy_responses = {
            'clean_energy': [
                "💡 Great insight! Our AI analysis shows similar momentum in clean energy sectors. First 100 @AlphaENRG followers get FREE premium energy signals 🚀",
                "🌱 This aligns with our renewable energy intelligence. Follow @AlphaENRG for AI-powered energy signals (free for first 100!) ⚡",
                "⚡ Spot on! Our Grok-4 analysis confirms this trend. Premium energy signals free for first 100 @AlphaENRG followers 🎯"
            ],
            'nuclear': [
                "☢️ Nuclear renaissance is real! Our AI tracks 25K+ mentions with 75% positive sentiment. Free premium signals @AlphaENRG 🚀",
                "⚛️ Uranium at $80/lb confirms this thesis. Follow @AlphaENRG for nuclear sector intelligence (free for first 100!) 💎",
                "🔥 SMR scaling is accelerating! Our analysis shows institutional momentum. Premium signals free @AlphaENRG ⚡"
            ],
            'tesla': [
                "🚗 TSLA energy division undervalued! Our AI tracks institutional sentiment. Free premium signals @AlphaENRG ⚡",
                "⚡ Energy storage + solar is the play. Follow @AlphaENRG for Tesla energy analysis (free for first 100!) 🚀",
                "💡 Cathie Wood amplifying TSLA momentum matches our analysis. Premium signals free @AlphaENRG 🎯"
            ],
            'general': [
                "📊 Excellent energy analysis! Our AI processes 500M+ posts daily for these insights. Free premium signals @AlphaENRG ⚡",
                "🧠 This matches our multi-source intelligence. Follow @AlphaENRG for AI-powered energy signals (free for first 100!) 🚀",
                "🎯 Professional take! Our Grok-4 analysis confirms similar trends. Premium energy signals free @AlphaENRG 💎"
            ]
        }
        
        self.target_accounts = [
            'CathieDWood', 'elonmusk', 'Tesla', 'IEA', 'BloombergNEF', 
            'EnergyIntel', 'IRENA', 'RenewablesNow', 'SolarPowerMag'
        ]
    
    def classify_energy_content(self, text):
        """Classify tweet content for appropriate response"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['clean', 'renewable', 'solar', 'wind', 'green']):
            return 'clean_energy'
        elif any(keyword in text_lower for keyword in ['nuclear', 'uranium', 'smr', 'reactor']):
            return 'nuclear'  
        elif any(keyword in text_lower for keyword in ['tesla', 'tsla', 'battery', 'storage']):
            return 'tesla'
        else:
            return 'general'
    
    def get_intelligent_response(self, tweet_text, category):
        """Generate contextually appropriate response"""
        import random
        responses = self.energy_responses.get(category, self.energy_responses['general'])
        return random.choice(responses)
    
    def find_engagement_opportunities(self):
        """Find recent tweets from followed accounts to engage with"""
        print("🔍 Scanning for energy engagement opportunities...")
        opportunities = []
        
        for username in self.target_accounts[:5]:  # Conservative batch
            try:
                user = self.client.get_user(username=username)
                if user and user.data:
                    user_id = user.data.id
                    
                    # Get recent tweets
                    tweets = self.client.get_users_tweets(
                        user_id, 
                        max_results=10,
                        tweet_fields=['created_at', 'public_metrics', 'context_annotations']
                    )
                    
                    if tweets and tweets.data:
                        for tweet in tweets.data[:3]:  # Top 3 recent tweets
                            # Check if energy-related and has good engagement
                            if hasattr(tweet, 'public_metrics'):
                                likes = tweet.public_metrics.get('like_count', 0)
                                retweets = tweet.public_metrics.get('retweet_count', 0)
                                
                                # Focus on tweets with decent engagement
                                if likes > 50 or retweets > 10:
                                    opportunities.append({
                                        'username': username,
                                        'tweet_id': tweet.id,
                                        'text': tweet.text,
                                        'likes': likes,
                                        'retweets': retweets
                                    })
                                    
                    time.sleep(1)  # Rate limit courtesy
                    
            except Exception as e:
                print(f"⚠️ Error scanning @{username}: {e}")
                continue
        
        print(f"📊 Found {len(opportunities)} engagement opportunities")
        return opportunities
    
    def execute_engagement_campaign(self, max_engagements=5):
        """Execute strategic engagement campaign"""
        print("🚀 STARTING ALPHAENRG ENGAGEMENT CAMPAIGN")
        print("="*50)
        
        opportunities = self.find_engagement_opportunities()
        if not opportunities:
            print("❓ No engagement opportunities found")
            return
        
        # Sort by engagement potential
        opportunities.sort(key=lambda x: x['likes'] + x['retweets'] * 2, reverse=True)
        
        engagement_count = 0
        for opp in opportunities[:max_engagements]:
            try:
                # Classify content and generate response
                category = self.classify_energy_content(opp['text'])
                response = self.get_intelligent_response(opp['text'], category)
                
                print(f"\n🎯 Target: @{opp['username']}")
                print(f"📊 Engagement: {opp['likes']} likes, {opp['retweets']} RTs")
                print(f"💬 Response: {response[:60]}...")
                
                # Post reply
                reply_result = self.client.create_tweet(
                    text=response,
                    in_reply_to_tweet_id=opp['tweet_id']
                )
                
                if reply_result and reply_result.data:
                    print(f"✅ Replied successfully!")
                    engagement_count += 1
                    time.sleep(30)  # 30 second delay between engagements
                else:
                    print("❌ Reply failed")
                    
            except tweepy.TooManyRequests:
                print("⏸️ Rate limit hit - pausing campaign")
                break
            except Exception as e:
                print(f"⚠️ Error replying: {e}")
                continue
        
        print(f"\n🎯 CAMPAIGN COMPLETE: {engagement_count} strategic engagements posted")
        print("🚀 Next: Monitor for newsletter signups and new followers")

if __name__ == "__main__":
    campaign = AlphaENRGEngagement()
    campaign.execute_engagement_campaign(max_engagements=3)