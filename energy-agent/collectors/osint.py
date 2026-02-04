"""
OSINT Collector - Pulls Reddit/News data from Kali box
"""
import subprocess
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from .base import BaseCollector

# Kali box connection
KALI_HOST = "192.168.154.193"
KALI_USER = "oc"
KALI_PASS = "Apple24"
KALI_DB = "/home/oc/energy-osint/data/osint.db"


class OSINTCollector(BaseCollector):
    """Collector for social/news OSINT from Kali scraping node"""
    
    def __init__(self):
        super().__init__("osint")
        self.source_weights = {
            # Reddit communities - weight by quality
            "wallstreetbets": 0.6,  # Noisy but early signals
            "stocks": 0.8,
            "investing": 0.9,
            "energy": 1.0,
            "nuclear": 1.2,
            "fusion": 1.3,
            "batteries": 1.1,
            "QuantumComputing": 1.2,
            "datacenter": 1.1,
            "immersioncooling": 1.5,  # Niche = high signal
            
            # News feeds - weight by credibility
            "reuters_energy": 1.3,
            "energy_gov": 1.2,
            "datacenter_knowledge": 1.2,
            "seeking_alpha_energy": 1.0,
            "hacker_news": 1.1,
            "cleantechnica": 0.9,
            "the_register": 0.8,
            "ars_technica": 0.9,
        }
    
    def _run_kali_query(self, query: str) -> list[dict]:
        """Execute SQLite query on Kali box via SSH"""
        cmd = f"""sshpass -p '{KALI_PASS}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 {KALI_USER}@{KALI_HOST} "sqlite3 -json '{KALI_DB}' \\"{query}\\"" """
        
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            return []
        except Exception as e:
            print(f"Kali query error: {e}")
            return []
    
    def collect(self, date_from: datetime = None, date_to: datetime = None, days_back: int = 1) -> List[Dict[str, Any]]:
        """Collect OSINT signals from Kali"""
        signals = []
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()
        
        # Collect Reddit posts
        reddit_query = f"""
            SELECT id, subreddit, title, selftext, author, score, 
                   num_comments, url, created_utc, keywords_matched
            FROM reddit_posts 
            WHERE scraped_at > '{cutoff}'
            AND keywords_matched IS NOT NULL
            ORDER BY score DESC
            LIMIT 200
        """
        
        reddit_posts = self._run_kali_query(reddit_query)
        for post in reddit_posts:
            signals.append(self._reddit_to_signal(post))
        
        # Collect news items
        news_query = f"""
            SELECT id, feed, title, summary, link, published, keywords_matched
            FROM news_items 
            WHERE scraped_at > '{cutoff}'
            AND keywords_matched IS NOT NULL
            ORDER BY published DESC
            LIMIT 200
        """
        
        news_items = self._run_kali_query(news_query)
        for item in news_items:
            signals.append(self._news_to_signal(item))
        
        print(f"OSINT: {len(reddit_posts)} Reddit + {len(news_items)} news = {len(signals)} signals")
        return signals
    
    def _reddit_to_signal(self, post: dict) -> Dict[str, Any]:
        """Convert Reddit post to standardized signal dict"""
        subreddit = post.get("subreddit", "unknown")
        keywords = json.loads(post.get("keywords_matched", "[]")) if post.get("keywords_matched") else []
        
        # Calculate attention score from Reddit metrics
        score = post.get("score", 0) or 0
        comments = post.get("num_comments", 0) or 0
        attention = min(1.0 + (score / 100) + (comments / 50), 3.0)
        weight = self.source_weights.get(subreddit, 1.0)
        
        return self._standardize_signal(
            raw_data=post,
            source_id=f"reddit_{post.get('id', '')}",
            title=post.get("title", "")[:200],
            abstract=post.get("selftext", "")[:500] if post.get("selftext") else "",
            date=datetime.fromtimestamp(post.get("created_utc", 0)) if post.get("created_utc") else datetime.now(),
            url=post.get("url", ""),
            entities={
                "keywords": keywords,
                "subreddit": subreddit,
                "author": post.get("author"),
                "reddit_score": score,
                "num_comments": comments,
                "attention_multiplier": attention * weight
            }
        )
    
    def _news_to_signal(self, item: dict) -> Dict[str, Any]:
        """Convert news item to standardized signal dict"""
        feed = item.get("feed", "unknown")
        keywords = json.loads(item.get("keywords_matched", "[]")) if item.get("keywords_matched") else []
        weight = self.source_weights.get(feed, 1.0)
        
        return self._standardize_signal(
            raw_data=item,
            source_id=f"news_{item.get('id', '')}",
            title=item.get("title", "")[:200],
            abstract=item.get("summary", "")[:500] if item.get("summary") else "",
            date=datetime.now(),  # Would need to parse the published string
            url=item.get("link", ""),
            entities={
                "keywords": keywords,
                "feed": feed,
                "attention_multiplier": weight
            }
        )


# Test
if __name__ == "__main__":
    collector = OSINTCollector()
    signals = collector.collect(days_back=7)
    
    print(f"\nCollected {len(signals)} OSINT signals")
    for s in signals[:5]:
        kw = s.get('entities', {}).get('keywords', [])
        print(f"  [{s['source']}] {s['title'][:60]}... (keywords: {kw[:3]})")
