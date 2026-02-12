#!/usr/bin/env python3
"""
Automated posting scheduler for LFC Agent
Generates content and posts to Instagram at scheduled times
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from fixtures.monitor import FixtureMonitor
from generation.generator import generate_variants
from visuals.compositor import create_stat_graphic, create_quote_graphic
from automation.instagram_poster import InstagramPoster
from dotenv import load_dotenv

load_dotenv()

class LFCContentScheduler:
    def __init__(self):
        self.monitor = FixtureMonitor()
        self.poster = InstagramPoster()
        self.assets_dir = Path(__file__).parent.parent.parent / 'assets'
        
    def generate_content_for_post(self, post_config):
        """Generate content (image + caption) for a specific post"""
        content_type = post_config['content_type']
        
        print(f"🎨 Generating {content_type} content...")
        
        if content_type == 'stat_graphic':
            # Create stat graphic
            if 'anfield' in post_config.get('desc', '').lower():
                stat_data = {
                    "headline": "54-16",
                    "label": "Liverpool vs City at Anfield",
                    "supporting": [
                        {"value": "97", "label": "Total Games"},
                        {"value": "27", "label": "Draws"}
                    ]
                }
            else:
                stat_data = {
                    "headline": "92 WINS",
                    "label": "Liverpool vs City (All Time)",
                    "supporting": [
                        {"value": "54", "label": "Home Wins"},
                        {"value": "16", "label": "City Wins"}
                    ]
                }
            
            image_path = create_stat_graphic(stat_data)
            
            # Generate caption
            context = {
                "opponent": "Manchester City",
                "date": "2026-02-08",
                "stat_json": str(stat_data)
            }
            variants = generate_variants("stat_graphic", context)
            
        elif content_type == 'famous_red':
            # Generate Demis Hassabis post
            quote_data = {
                "quote": "From the Kop to the Nobel Prize",
                "author": "Demis Hassabis",
                "year": 2024
            }
            image_path = create_quote_graphic(quote_data)
            
            context = {
                "name": "Demis Hassabis",
                "achievement": "Nobel Prize in Chemistry 2024",
                "lfc_connection": "Lifelong Liverpool supporter",
                "opponent": "Manchester City"
            }
            variants = generate_variants("famous_red", context)
            
        elif content_type == 'comedy_banter':
            # Create banter graphic
            quote_data = {
                "quote": "Built different ✅ Bought different ❌",
                "author": "@YNWA4Reds",
                "year": 2026
            }
            image_path = create_quote_graphic(quote_data)
            
            context = {
                "opponent": "Manchester City",
                "date": "2026-02-08",
                "topic": "115 charges vs Liverpool's organic success",
                "angle": "History vs oil money"
            }
            variants = generate_variants("comedy_banter", context)
            
        else:  # iconic_moment, crowd_atmosphere
            # Create inspirational quote graphic
            if 'crowd' in content_type:
                quote_data = {
                    "quote": "You'll Never Walk Alone",
                    "author": "The Kop",
                    "year": 1963
                }
                context_type = "crowd_atmosphere"
            else:
                quote_data = {
                    "quote": "This means more",
                    "author": "Jürgen Klopp", 
                    "year": 2019
                }
                context_type = "iconic_moment"
                
            image_path = create_quote_graphic(quote_data)
            
            context = {
                "opponent": "Manchester City",
                "date": "2026-02-08",
                "asset_description": quote_data["quote"]
            }
            variants = generate_variants(context_type, context)
        
        # Use variant A by default
        caption = variants['variant_a']['caption']
        hashtags = ' '.join(variants['variant_a']['hashtags'][:15])
        full_caption = f"{caption}\\n\\n{hashtags}"
        
        return {
            "image_path": image_path,
            "caption": full_caption,
            "variants": variants
        }
    
    async def post_scheduled_content(self, post_config, dry_run=True):
        """Generate and post content for a scheduled post"""
        print(f"\\n📅 {post_config['day']} {post_config['time']}: {post_config['content_type']}")
        
        try:
            # Generate content
            content = self.generate_content_for_post(post_config)
            
            print(f"   📊 Image: {Path(content['image_path']).name}")
            print(f"   📝 Caption preview: {content['caption'][:100]}...")
            
            # Post to Instagram
            result = await self.poster.post_with_retry(
                content['image_path'],
                content['caption'],
                max_retries=2
            )
            
            if not dry_run and result['status'] == 'success':
                print(f"   ✅ Posted successfully!")
            elif dry_run:
                print(f"   🔍 Dry run complete")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_full_campaign(self, dry_run=True):
        """Generate and post all content for the upcoming fixture"""
        print("🔴 LFC AGENT - AUTOMATED CAMPAIGN")
        print("=" * 50)
        
        # Get fixture and schedule
        fixture = self.monitor.get_next_fixture()
        schedule = self.monitor.get_content_schedule(fixture)
        
        print(f"📅 Fixture: LFC vs {fixture['opponent']}")
        print(f"⏰ Days until: {fixture['days_until']}")
        print(f"📋 Posts scheduled: {len(schedule)}")
        
        results = []
        for i, post in enumerate(schedule):
            result = await self.post_scheduled_content(post, dry_run=dry_run)
            results.append({"post": post, "result": result})
            
            # Wait between posts to avoid spam detection
            if i < len(schedule) - 1:
                await asyncio.sleep(2)
                
        print(f"\\n🔥 Campaign complete: {len([r for r in results if r['result']['status'] == 'success'])} successful")
        return results

async def main():
    """Test the automated scheduler"""
    scheduler = LFCContentScheduler()
    
    # Run full campaign in dry-run mode
    results = await scheduler.run_full_campaign(dry_run=True)
    
    print(f"\\n📊 RESULTS:")
    for result in results:
        post = result['post']
        status = result['result']['status']
        print(f"   {post['day']} {post['time']} - {post['content_type']}: {status}")

if __name__ == "__main__":
    asyncio.run(main())