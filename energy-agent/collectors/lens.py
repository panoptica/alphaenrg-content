"""
Lens.org Patent & Scholarly Data Collector.

Lens.org provides free access to patents and scholarly articles.
Free tier: 50 requests/month, 50 results per request
Pro tier: £500/year for enhanced access

API docs: https://docs.api.lens.org/
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time
import os

from .base import BaseCollector
from config.settings import TECHNOLOGY_KEYWORDS, TIER_1_COMPANIES, TIER_2_COMPANIES

logger = logging.getLogger(__name__)


class LensPatentCollector(BaseCollector):
    """Collector for patents via Lens.org API."""
    
    def __init__(self, api_key: str = None):
        super().__init__('lens_patent')
        self.base_url = "https://api.lens.org/patent/search"
        self.api_key = api_key or os.getenv("LENS_API_KEY", "")
        self.rate_limit_delay = 2.0
        
        if not self.api_key:
            logger.warning("No Lens.org API key. Get one free at: https://www.lens.org/lens/user/subscriptions")
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """Collect patents from Lens.org."""
        if not self.api_key:
            logger.error("No Lens.org API key - cannot collect")
            return []
        
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=7)
        
        all_signals = []
        
        for domain, keywords in TECHNOLOGY_KEYWORDS.items():
            logger.info(f"Collecting {domain} patents from Lens.org...")
            try:
                signals = self._search_domain(domain, keywords[:3], date_from, date_to)
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"Error collecting {domain} from Lens.org: {e}")
        
        # Deduplicate
        seen = set()
        unique = []
        for sig in all_signals:
            if sig['source_id'] not in seen:
                seen.add(sig['source_id'])
                unique.append(sig)
        
        logger.info(f"Collected {len(unique)} unique patents from Lens.org")
        return unique
    
    def _search_domain(
        self, 
        domain: str, 
        keywords: List[str],
        date_from: datetime,
        date_to: datetime
    ) -> List[Dict[str, Any]]:
        """Search Lens.org for patents matching keywords."""
        
        # Build Lens.org query
        keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": keyword_query,
                                "fields": ["title", "abstract", "claims.claim_text"]
                            }
                        },
                        {
                            "range": {
                                "date_published": {
                                    "gte": date_from.strftime('%Y-%m-%d'),
                                    "lte": date_to.strftime('%Y-%m-%d')
                                }
                            }
                        }
                    ]
                }
            },
            "size": 50,  # Free tier limit
            "sort": [{"date_published": "desc"}],
            "include": [
                "lens_id",
                "title",
                "abstract",
                "date_published",
                "jurisdiction",
                "kind",
                "applicants",
                "inventors",
                "classifications_cpc",
                "cited_by_count",
                "families.simple_family.size"
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=query,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Lens.org API request failed: {e}")
            return []
        
        results = data.get('data', [])
        signals = []
        
        for patent in results:
            entities = self._extract_entities(patent, domain)
            lens_id = patent.get('lens_id', '')
            
            signal = self._standardize_signal(
                raw_data=patent,
                source_id=lens_id,
                title=patent.get('title', ''),
                abstract=patent.get('abstract', ''),
                date=self._parse_date(patent.get('date_published')),
                url=f"https://www.lens.org/lens/patent/{lens_id}",
                entities=entities
            )
            signal['domain'] = domain
            signal['citations'] = patent.get('cited_by_count', 0)
            signal['family_size'] = patent.get('families', {}).get('simple_family', {}).get('size', 1)
            
            signals.append(signal)
        
        return signals
    
    def _extract_entities(self, patent: Dict, domain: str) -> Dict:
        """Extract entities from Lens.org patent data."""
        entities = {
            'companies': [],
            'technologies': [domain]
        }
        
        # Extract applicants (companies)
        for applicant in patent.get('applicants', []):
            if isinstance(applicant, dict):
                name = applicant.get('name', '')
            else:
                name = str(applicant)
            if name:
                entities['companies'].append(name)
                for t1 in TIER_1_COMPANIES:
                    if t1.lower() in name.lower():
                        entities['tier'] = 1
                        break
        
        return entities
    
    def _parse_date(self, date_str: str) -> datetime:
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str[:10], '%Y-%m-%d')
        except ValueError:
            return datetime.now()


class LensScholarCollector(BaseCollector):
    """Collector for scholarly articles via Lens.org API."""
    
    def __init__(self, api_key: str = None):
        super().__init__('lens_scholar')
        self.base_url = "https://api.lens.org/scholarly/search"
        self.api_key = api_key or os.getenv("LENS_API_KEY", "")
        self.rate_limit_delay = 2.0
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """Collect scholarly articles from Lens.org."""
        if not self.api_key:
            logger.error("No Lens.org API key")
            return []
        
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=30)
        
        all_signals = []
        
        for domain, keywords in TECHNOLOGY_KEYWORDS.items():
            logger.info(f"Collecting {domain} papers from Lens.org...")
            try:
                signals = self._search_domain(domain, keywords[:3], date_from, date_to)
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"Error: {e}")
        
        seen = set()
        unique = [s for s in all_signals if not (s['source_id'] in seen or seen.add(s['source_id']))]
        return unique
    
    def _search_domain(self, domain: str, keywords: List[str], date_from: datetime, date_to: datetime) -> List[Dict]:
        keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": keyword_query, "fields": ["title", "abstract"]}},
                        {"range": {"date_published": {"gte": date_from.strftime('%Y-%m-%d'), "lte": date_to.strftime('%Y-%m-%d')}}}
                    ]
                }
            },
            "size": 50,
            "sort": [{"date_published": "desc"}],
            "include": ["lens_id", "title", "abstract", "date_published", "authors", "source", "citations_count", "doi"]
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        try:
            response = requests.post(self.base_url, headers=headers, json=query, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Lens.org scholar API failed: {e}")
            return []
        
        signals = []
        for paper in data.get('data', []):
            lens_id = paper.get('lens_id', '')
            doi = paper.get('doi', '')
            url = f"https://doi.org/{doi}" if doi else f"https://www.lens.org/lens/scholar/{lens_id}"
            
            signal = self._standardize_signal(
                raw_data=paper,
                source_id=lens_id,
                title=paper.get('title', ''),
                abstract=paper.get('abstract', ''),
                date=datetime.strptime(paper.get('date_published', '')[:10], '%Y-%m-%d') if paper.get('date_published') else datetime.now(),
                url=url,
                entities={'technologies': [domain], 'companies': []}
            )
            signal['domain'] = domain
            signal['citations'] = paper.get('citations_count', 0)
            signals.append(signal)
        
        return signals


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("LENS_API_KEY")
    if not api_key:
        print("Set LENS_API_KEY environment variable")
        print("Get a free key at: https://www.lens.org/lens/user/subscriptions")
        exit(1)
    
    collector = LensPatentCollector(api_key)
    signals = collector.collect()
    
    print(f"\nCollected {len(signals)} patents")
    for sig in signals[:5]:
        print(f"\n{sig['source_id']}: {sig['title'][:60]}...")
        print(f"  Citations: {sig.get('citations', 0)}")
