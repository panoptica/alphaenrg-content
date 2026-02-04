"""
ArXiv Academic Papers Collector.

ArXiv API is free and provides access to preprints.
API docs: https://info.arxiv.org/help/api/user-manual.html

Relevant categories:
- cs.AI (Artificial Intelligence)
- physics.app-ph (Applied Physics) 
- cond-mat (Condensed Matter)
- quant-ph (Quantum Physics)
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time
import re

from .base import BaseCollector
from config.settings import TECHNOLOGY_KEYWORDS, TIER_1_COMPANIES, TIER_2_COMPANIES

logger = logging.getLogger(__name__)


class ArxivCollector(BaseCollector):
    """Collector for ArXiv academic papers."""
    
    def __init__(self):
        super().__init__('arxiv')
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limit_delay = 3.0  # ArXiv asks for 3 seconds between requests
        
        # Relevant ArXiv categories
        self.categories = [
            'cond-mat.mtrl-sci',  # Materials science (batteries, cooling materials)
            'cond-mat.supr-con',  # Superconductivity
            'physics.app-ph',     # Applied physics
            'quant-ph',           # Quantum physics
            'cs.ET',              # Emerging technologies
        ]
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect papers from ArXiv.
        
        Note: ArXiv date filtering is by submission date, not publication.
        We search by keywords within categories.
        """
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=7)  # Last week
        
        all_signals = []
        
        # Search each technology domain
        for domain, keywords in TECHNOLOGY_KEYWORDS.items():
            logger.info(f"Searching ArXiv for {domain} papers...")
            try:
                signals = self._search_domain(domain, keywords[:3])  # Limit keywords
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"Error collecting {domain} from ArXiv: {e}")
        
        # Deduplicate by ArXiv ID
        seen = set()
        unique_signals = []
        for sig in all_signals:
            if sig['source_id'] not in seen:
                seen.add(sig['source_id'])
                unique_signals.append(sig)
        
        logger.info(f"Collected {len(unique_signals)} unique papers from ArXiv")
        return unique_signals
    
    def _search_domain(self, domain: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search ArXiv for papers matching keywords."""
        
        # Build search query
        # Format: (keyword1 OR keyword2) AND (cat:physics.app-ph OR cat:cond-mat.*)
        keyword_query = ' OR '.join([f'"{kw}"' for kw in keywords])
        category_query = ' OR '.join([f'cat:{cat}' for cat in self.categories])
        
        search_query = f'({keyword_query}) AND ({category_query})'
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': 50,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"ArXiv API request failed: {e}")
            return []
        
        # Parse XML response
        signals = self._parse_response(response.text, domain)
        return signals
    
    def _parse_response(self, xml_text: str, domain: str) -> List[Dict[str, Any]]:
        """Parse ArXiv API XML response."""
        signals = []
        
        # Define namespace
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error(f"Failed to parse ArXiv XML: {e}")
            return []
        
        for entry in root.findall('atom:entry', ns):
            try:
                # Extract fields
                arxiv_id = entry.find('atom:id', ns).text
                # Clean up ID (http://arxiv.org/abs/2401.12345v1 -> 2401.12345)
                arxiv_id = arxiv_id.split('/')[-1].split('v')[0] if arxiv_id else ''
                
                title = entry.find('atom:title', ns).text or ''
                title = ' '.join(title.split())  # Normalize whitespace
                
                abstract = entry.find('atom:summary', ns).text or ''
                abstract = ' '.join(abstract.split())
                
                published = entry.find('atom:published', ns).text
                pub_date = self._parse_date(published)
                
                # Get authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None and name.text:
                        authors.append(name.text)
                
                # Get categories
                categories = []
                for cat in entry.findall('atom:category', ns):
                    term = cat.get('term')
                    if term:
                        categories.append(term)
                
                # Build URL
                url = f"https://arxiv.org/abs/{arxiv_id}"
                
                # Extract entities
                entities = self._extract_entities(title, abstract, authors, domain)
                
                signal = self._standardize_signal(
                    raw_data={
                        'authors': authors,
                        'categories': categories,
                        'arxiv_id': arxiv_id
                    },
                    source_id=arxiv_id,
                    title=title,
                    abstract=abstract[:2000],  # Truncate long abstracts
                    date=pub_date,
                    url=url,
                    entities=entities
                )
                
                signal['domain'] = domain
                signals.append(signal)
                
            except Exception as e:
                logger.warning(f"Failed to parse ArXiv entry: {e}")
                continue
        
        return signals
    
    def _extract_entities(self, title: str, abstract: str, authors: List[str], domain: str) -> Dict:
        """Extract companies and technologies from paper."""
        entities = {
            'companies': [],
            'technologies': [domain],
            'authors': authors[:5]  # Keep top 5 authors
        }
        
        text = f"{title} {abstract}".lower()
        
        # Check for company affiliations/mentions
        for company in TIER_1_COMPANIES:
            if company.lower() in text:
                entities['companies'].append(company)
                entities['tier'] = 1
        
        for company in TIER_2_COMPANIES:
            if company.lower() in text:
                entities['companies'].append(company)
                if 'tier' not in entities:
                    entities['tier'] = 2
        
        # Extract technology mentions
        for tech_domain, keywords in TECHNOLOGY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text and tech_domain not in entities['technologies']:
                    entities['technologies'].append(tech_domain)
        
        return entities
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO date from ArXiv."""
        if not date_str:
            return datetime.now()
        try:
            # Format: 2024-01-15T12:34:56Z
            return datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime.now()


if __name__ == "__main__":
    # Test the collector
    logging.basicConfig(level=logging.INFO)
    collector = ArxivCollector()
    
    signals = collector.collect()
    
    print(f"\nCollected {len(signals)} papers")
    for sig in signals[:5]:
        print(f"\n--- {sig['source_id']} ---")
        print(f"Title: {sig['title'][:80]}...")
        print(f"Domain: {sig.get('domain')}")
        print(f"Authors: {sig['entities'].get('authors', [])[:3]}")
        print(f"URL: {sig['url']}")
