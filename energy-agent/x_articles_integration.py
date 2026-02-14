#!/usr/bin/env python3
"""
X Articles Integration for AlphaENRG - Publish long-form intelligence articles
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
import tweepy

load_dotenv()

class XArticlesPublisher:
    def __init__(self):
        """Initialize X Articles publisher"""
        
        # X API credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter client for regular tweets
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
    def create_article(self, title, content, tags=None):
        """
        Create an X Article (long-form content)
        
        Note: X Articles API is currently limited. This implementation uses
        a workaround approach with thread creation for now.
        """
        
        # For now, we'll create a comprehensive thread as X Articles API
        # access is limited. When full API access is available, this can be updated.
        
        return self._create_comprehensive_thread(title, content, tags)
    
    def _create_comprehensive_thread(self, title, content, tags=None):
        """Create a comprehensive Twitter thread as an alternative to Articles"""
        
        try:
            # Split content into tweet-sized chunks
            thread_tweets = self._split_content_for_thread(title, content, tags)
            
            # Post the thread
            tweet_ids = []
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(thread_tweets):
                if previous_tweet_id:
                    # Reply to previous tweet
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    # First tweet
                    response = self.client.create_tweet(text=tweet_text)
                
                if response.data:
                    tweet_id = response.data['id']
                    tweet_ids.append(tweet_id)
                    previous_tweet_id = tweet_id
                    print(f"✅ Thread tweet {i+1}/{len(thread_tweets)} posted: {tweet_id}")
                else:
                    print(f"❌ Failed to post thread tweet {i+1}")
                    return False
            
            # Post summary with link to first tweet
            first_tweet_url = f"https://x.com/AlphaENRG/status/{tweet_ids[0]}"
            print(f"✅ X Thread published successfully!")
            print(f"🔗 Thread URL: {first_tweet_url}")
            print(f"📊 {len(tweet_ids)} tweets in thread")
            
            return {
                'success': True,
                'thread_url': first_tweet_url,
                'tweet_ids': tweet_ids,
                'tweet_count': len(tweet_ids)
            }
            
        except Exception as e:
            print(f"❌ X Thread creation error: {e}")
            return False
    
    def _split_content_for_thread(self, title, content, tags=None):
        """Split long-form content into tweet-sized chunks for threading"""
        
        tweets = []
        max_tweet_length = 280
        
        # First tweet - title and intro
        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y")
        
        first_tweet = f"""📄 AlphaENRG Intelligence Report • {timestamp}

{title}

🧵 Thread below with full analysis ↓

#EnergyIntelligence #AlphaENRG"""
        
        tweets.append(first_tweet)
        
        # Split content into sections
        sections = content.split('\n\n')
        current_tweet = ""
        tweet_number = 2
        
        for section in sections:
            # Clean up section
            section = section.strip()
            if not section:
                continue
                
            # If section is too long, split it further
            if len(section) > max_tweet_length - 50:  # Leave room for numbering
                words = section.split(' ')
                current_section = ""
                
                for word in words:
                    test_length = len(current_section) + len(word) + 20  # Room for numbering
                    
                    if test_length < max_tweet_length:
                        current_section += word + " "
                    else:
                        # Add current section to tweets
                        if current_section.strip():
                            tweets.append(f"{tweet_number}/ {current_section.strip()}")
                            tweet_number += 1
                        current_section = word + " "
                
                # Add remaining content
                if current_section.strip():
                    tweets.append(f"{tweet_number}/ {current_section.strip()}")
                    tweet_number += 1
            else:
                # Section fits in one tweet
                tweets.append(f"{tweet_number}/ {section}")
                tweet_number += 1
        
        # Add tags to final tweet if provided
        if tags:
            tags_text = " ".join([f"#{tag}" for tag in tags])
            final_tweet = f"{tweet_number}/ End of analysis.\n\n{tags_text}\n\n📧 Subscribe: alphaenergy.substack.com"
            tweets.append(final_tweet)
        
        return tweets

    def publish_intelligence_article(self, intelligence_data, signals_count=0):
        """Publish daily intelligence as an X Article/Thread"""
        
        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y")
        
        title = f"daily energy intelligence • {timestamp.lower()}"
        
        # Create comprehensive article content
        content = f"""institutional-grade energy market analysis

## today's key developments

{intelligence_data}

## methodology

our AI systems process multiple data streams:

• arxiv research papers → emerging tech trends
• patent filings → corporate R&D directions  
• SEC data → financial market signals
• OSINT intelligence → sentiment analysis

## signal strength

today's analysis processed {signals_count} signals, identifying the highest-impact developments for energy sector positioning.

## outlook

these developments suggest accelerating convergence in quantum computing, energy storage, and grid infrastructure. institutional investors should monitor patent activity in these intersecting domains.

the energy transition is accelerating. the smart money is positioning now."""
        
        tags = ['EnergyIntelligence', 'CleanTech', 'InvestmentSignals', 'QuantumComputing', 'AlphaENRG']
        
        return self.create_article(title, content, tags)

    def publish_breaking_analysis(self, topic, analysis, urgency="HIGH"):
        """Publish breaking analysis as X Article/Thread"""
        
        timestamp = datetime.now(timezone.utc).strftime("%H:%M UTC")
        
        urgency_prefix = {
            "CRITICAL": "🚨 CRITICAL",
            "HIGH": "⚡ BREAKING", 
            "MEDIUM": "📊 ANALYSIS",
            "LOW": "💡 INSIGHT"
        }
        
        prefix = urgency_prefix.get(urgency, "📊 ANALYSIS")
        title = f"{prefix}: {topic}"
        
        content = f"""real-time energy intelligence analysis

## situation

{analysis}

## implications

this development has significant implications for energy markets and investor positioning.

## next steps

alphaenrg systems will continue monitoring this development. updates will follow as the situation evolves.

---

automated analysis by alphaenrg intelligence systems • {timestamp}"""
        
        tags = ['BreakingNews', 'EnergyMarkets', 'AlphaSignals', 'RealTimeIntel']
        
        return self.create_article(title, content, tags)

def integrate_with_daily_agent(intelligence_text, signals_count=0):
    """Integration function for the main energy agent"""
    
    try:
        publisher = XArticlesPublisher()
        
        # Publish as X Article/Thread
        result = publisher.publish_intelligence_article(intelligence_text, signals_count)
        
        return result
        
    except Exception as e:
        print(f"❌ X Articles publishing error: {e}")
        return False

def test_article_publishing():
    """Test X Articles functionality"""
    
    test_intelligence = """🔬 quantum computing patents surge 47% this quarter, with breakthrough developments in error correction

🌊 offshore wind development accelerating across northern europe, new installations exceeding 2026 targets

⚡ grid storage innovations reaching commercial viability, costs dropping below critical thresholds

💰 clean energy VC funding up 23% quarter-over-quarter, signaling strong institutional confidence

🔋 solid-state battery patents from automotive giants suggest imminent commercial deployment"""
    
    publisher = XArticlesPublisher()
    result = publisher.publish_intelligence_article(test_intelligence, signals_count=156)
    
    if result:
        print(f"\n🎉 Test successful!")
        if isinstance(result, dict):
            print(f"📊 Thread details: {result}")
    else:
        print("\n❌ Test failed")

if __name__ == "__main__":
    test_article_publishing()