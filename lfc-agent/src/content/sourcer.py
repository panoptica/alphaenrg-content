#!/usr/bin/env python3
"""
Content Sourcer - Downloads assets from YouTube, Twitter, Wikimedia.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

ASSETS_DIR = Path(__file__).parent.parent.parent / 'assets'

# YouTube queries for LFC vs City content
YOUTUBE_QUERIES = [
    "Liverpool Manchester City best goals",
    "Liverpool vs City Anfield atmosphere",
    "Gerrard vs Manchester City",
    "Liverpool 4-3 Manchester City 2018",
    "Liverpool fans YNWA before City",
    "Klopp Liverpool City celebrations",
]

# Twitter accounts to monitor
TWITTER_ACCOUNTS = [
    "@LFC",
    "@TheKopTimes",
    "@AnfieldWatch", 
    "@JamieCarragher",
]


class YouTubeSourcer:
    """Download video clips from YouTube using yt-dlp."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or ASSETS_DIR / 'videos' / 'raw')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def search_and_download(self, query: str, max_results: int = 3, max_duration: int = 180) -> List[Dict]:
        """
        Search YouTube and download matching videos.
        
        Args:
            query: Search query
            max_results: Maximum videos to download
            max_duration: Maximum video duration in seconds
        
        Returns:
            List of downloaded video metadata
        """
        downloads = []
        
        # yt-dlp search and download
        cmd = [
            'yt-dlp',
            f'ytsearch{max_results}:{query}',
            '--match-filter', f'duration < {max_duration}',
            '--format', 'best[height<=720]',
            '--output', str(self.output_dir / '%(title)s_%(id)s.%(ext)s'),
            '--write-info-json',
            '--no-playlist',
            '--restrict-filenames',
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse downloaded files from output
            for line in result.stdout.split('\n'):
                if '[download] Destination:' in line:
                    filepath = line.split('Destination: ')[1].strip()
                    
                    # Load metadata
                    json_path = filepath.rsplit('.', 1)[0] + '.info.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            metadata = json.load(f)
                        
                        downloads.append({
                            'type': 'video',
                            'source_type': 'youtube',
                            'local_path': filepath,
                            'source_url': metadata.get('webpage_url'),
                            'attribution': f"YouTube: {metadata.get('channel', 'Unknown')}",
                            'copyright_risk': 'medium',
                            'metadata': {
                                'title': metadata.get('title'),
                                'duration': metadata.get('duration'),
                                'channel': metadata.get('channel'),
                                'upload_date': metadata.get('upload_date'),
                            }
                        })
            
            return downloads
            
        except subprocess.TimeoutExpired:
            print(f"Timeout downloading: {query}")
            return []
        except Exception as e:
            print(f"Error downloading: {e}")
            return []
    
    def download_specific(self, url: str) -> Optional[Dict]:
        """Download a specific YouTube video."""
        cmd = [
            'yt-dlp',
            url,
            '--format', 'best[height<=720]',
            '--output', str(self.output_dir / '%(title)s_%(id)s.%(ext)s'),
            '--write-info-json',
            '--restrict-filenames',
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            for line in result.stdout.split('\n'):
                if '[download] Destination:' in line:
                    filepath = line.split('Destination: ')[1].strip()
                    json_path = filepath.rsplit('.', 1)[0] + '.info.json'
                    
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            metadata = json.load(f)
                        
                        return {
                            'type': 'video',
                            'source_type': 'youtube',
                            'local_path': filepath,
                            'source_url': url,
                            'attribution': f"YouTube: {metadata.get('channel', 'Unknown')}",
                            'copyright_risk': 'medium',
                            'metadata': metadata
                        }
            
            return None
            
        except Exception as e:
            print(f"Error: {e}")
            return None


class WikimediaSourcer:
    """Download CC-licensed images from Wikimedia Commons."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or ASSETS_DIR / 'images' / 'raw')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_url = 'https://commons.wikimedia.org/w/api.php'
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Wikimedia Commons for images."""
        params = {
            'action': 'query',
            'format': 'json',
            'generator': 'search',
            'gsrsearch': query,
            'gsrnamespace': 6,  # File namespace
            'gsrlimit': limit,
            'prop': 'imageinfo',
            'iiprop': 'url|extmetadata',
        }
        
        response = requests.get(self.api_url, params=params)
        data = response.json()
        
        results = []
        pages = data.get('query', {}).get('pages', {})
        
        for page_id, page in pages.items():
            imageinfo = page.get('imageinfo', [{}])[0]
            metadata = imageinfo.get('extmetadata', {})
            
            # Check license
            license_info = metadata.get('LicenseShortName', {}).get('value', '')
            if not any(lic in license_info.lower() for lic in ['cc', 'public domain', 'pd']):
                continue
            
            results.append({
                'title': page.get('title'),
                'url': imageinfo.get('url'),
                'description': metadata.get('ImageDescription', {}).get('value', ''),
                'license': license_info,
                'attribution': metadata.get('Artist', {}).get('value', 'Wikimedia Commons'),
            })
        
        return results
    
    def download(self, url: str, filename: str = None) -> Optional[Dict]:
        """Download an image from Wikimedia."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if not filename:
                filename = url.split('/')[-1]
            
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return {
                'type': 'image',
                'source_type': 'wikimedia',
                'local_path': str(filepath),
                'source_url': url,
                'copyright_risk': 'low',
            }
            
        except Exception as e:
            print(f"Error downloading: {e}")
            return None


class ManualAssets:
    """Handle manually curated assets."""
    
    @staticmethod
    def add_quote(quote: str, author: str, context: str = None, year: int = None, tags: List[str] = None) -> Dict:
        """Create a quote asset."""
        return {
            'type': 'quote',
            'source_type': 'manual',
            'quote_text': quote,
            'author': author,
            'context': context,
            'year': year,
            'tags': tags or [],
            'copyright_risk': 'low',
        }
    
    @staticmethod  
    def add_stat(stat_type: str, opponent: str, data: Dict) -> Dict:
        """Create a stat asset."""
        return {
            'type': 'stat',
            'source_type': 'manual',
            'stat_type': stat_type,
            'opponent': opponent,
            'stat_data': data,
            'copyright_risk': 'low',
        }


def gather_city_content():
    """Gather content for LFC vs City match."""
    print("🔴 Gathering content for LFC vs Manchester City")
    print("=" * 50)
    
    all_assets = []
    
    # YouTube content
    print("\n📹 Searching YouTube...")
    yt = YouTubeSourcer()
    
    for query in YOUTUBE_QUERIES[:2]:  # Limit for testing
        print(f"  Searching: {query}")
        videos = yt.search_and_download(query, max_results=2, max_duration=120)
        all_assets.extend(videos)
        print(f"  Found: {len(videos)} videos")
    
    # Wikimedia content
    print("\n🖼️  Searching Wikimedia...")
    wiki = WikimediaSourcer()
    
    wiki_queries = ["Liverpool FC Anfield", "Liverpool FC 1970s", "Steven Gerrard"]
    for query in wiki_queries:
        print(f"  Searching: {query}")
        results = wiki.search(query, limit=3)
        print(f"  Found: {len(results)} images")
        
        for result in results[:1]:  # Download 1 per query
            asset = wiki.download(result['url'])
            if asset:
                asset['attribution'] = result['attribution']
                all_assets.append(asset)
    
    print(f"\n✅ Total assets gathered: {len(all_assets)}")
    return all_assets


def test_sourcer():
    """Test content sourcing."""
    print("Testing Content Sourcer")
    print("=" * 50)
    
    # Test Wikimedia search only (no downloads)
    wiki = WikimediaSourcer()
    results = wiki.search("Liverpool FC Anfield", limit=5)
    
    print(f"\nWikimedia search results:")
    for r in results:
        print(f"  - {r['title'][:50]}... ({r['license']})")
    
    print("\n✅ Sourcer test complete")


if __name__ == "__main__":
    test_sourcer()
