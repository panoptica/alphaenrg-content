#!/usr/bin/env python3
"""
Fixture Monitor - Detects upcoming LFC matches and triggers content generation.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RIVALS = [
    "Manchester City",
    "Manchester United",
    "Arsenal", 
    "Chelsea",
    "Everton",
    "Real Madrid",
    "Barcelona",
    "Tottenham"
]

class FixtureMonitor:
    def __init__(self, db_connection=None):
        self.db = db_connection
        
    def get_next_fixture(self):
        """Get next upcoming fixture from database."""
        if not self.db:
            # Return hardcoded City fixture for MVP
            return {
                "fixture_id": 1,
                "opponent": "Manchester City",
                "date": "2026-02-08T16:30:00Z",
                "competition": "Premier League",
                "venue": "Anfield",
                "is_rival": True,
                "is_home": True,
                "days_until": self._days_until("2026-02-08")
            }
        
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT id, opponent, match_date, competition, venue, is_rival, is_home
            FROM fixtures 
            WHERE match_date > NOW()
            ORDER BY match_date ASC
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            return {
                "fixture_id": row[0],
                "opponent": row[1],
                "date": row[2].isoformat(),
                "competition": row[3],
                "venue": row[4],
                "is_rival": row[5],
                "is_home": row[6],
                "days_until": self._days_until(row[2])
            }
        return None
    
    def _days_until(self, date):
        """Calculate days until match."""
        if isinstance(date, str):
            match_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        else:
            match_date = date
        
        now = datetime.now(match_date.tzinfo) if match_date.tzinfo else datetime.now()
        delta = match_date - now
        return delta.days
    
    def should_trigger_content(self, fixture):
        """Determine if we should generate content for this fixture."""
        days = fixture.get('days_until', 99)
        is_rival = fixture.get('is_rival', False)
        
        # Big games: start 7 days out
        if is_rival and days <= 7:
            return True
        
        # Regular games: start 3 days out
        if days <= 3:
            return True
            
        return False
    
    def get_content_schedule(self, fixture):
        """Generate posting schedule for a fixture."""
        match_date = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00'))
        posts = []
        
        # Thursday - 1 post (Famous Red / news hook)
        if fixture['days_until'] >= 3:
            posts.append({
                "day": "Thursday",
                "time": "18:00",
                "content_type": "famous_red",
                "scheduled": (match_date - timedelta(days=3)).replace(hour=18, minute=0)
            })
        
        # Friday - 2 posts
        if fixture['days_until'] >= 2:
            fri = match_date - timedelta(days=2)
            posts.extend([
                {"day": "Friday", "time": "11:00", "content_type": "iconic_moment", 
                 "scheduled": fri.replace(hour=11, minute=0)},
                {"day": "Friday", "time": "19:00", "content_type": "stat_graphic",
                 "scheduled": fri.replace(hour=19, minute=0)}
            ])
        
        # Saturday - 3 posts
        if fixture['days_until'] >= 1:
            sat = match_date - timedelta(days=1)
            posts.extend([
                {"day": "Saturday", "time": "09:00", "content_type": "crowd_atmosphere",
                 "scheduled": sat.replace(hour=9, minute=0)},
                {"day": "Saturday", "time": "13:00", "content_type": "comedy_banter",
                 "scheduled": sat.replace(hour=13, minute=0)},
                {"day": "Saturday", "time": "17:00", "content_type": "iconic_moment",
                 "scheduled": sat.replace(hour=17, minute=0)}
            ])
        
        # Match day - 2 posts (before kickoff only)
        posts.extend([
            {"day": "Sunday", "time": "10:00", "content_type": "stat_graphic",
             "scheduled": match_date.replace(hour=10, minute=0)},
            {"day": "Sunday", "time": "14:00", "content_type": "crowd_atmosphere",
             "scheduled": match_date.replace(hour=14, minute=0)}
        ])
        
        return posts


def main():
    """Test the fixture monitor."""
    monitor = FixtureMonitor()
    fixture = monitor.get_next_fixture()
    
    print("=" * 50)
    print("LFC FIXTURE MONITOR")
    print("=" * 50)
    print(f"\nNext fixture: Liverpool vs {fixture['opponent']}")
    print(f"Date: {fixture['date']}")
    print(f"Venue: {fixture['venue']}")
    print(f"Competition: {fixture['competition']}")
    print(f"Days until: {fixture['days_until']}")
    print(f"Is rival: {fixture['is_rival']}")
    
    if monitor.should_trigger_content(fixture):
        print("\n✅ CONTENT GENERATION TRIGGERED")
        schedule = monitor.get_content_schedule(fixture)
        print(f"\nPosting schedule ({len(schedule)} posts):")
        for post in schedule:
            print(f"  - {post['day']} {post['time']}: {post['content_type']}")
    else:
        print("\n⏸️  Not yet time for content generation")


if __name__ == "__main__":
    main()
