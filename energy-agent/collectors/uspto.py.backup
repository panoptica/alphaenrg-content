"""
USPTO Patent Collector using the new PatentSearch API.

The old PatentsView API was deprecated May 1, 2025.
New API requires an API key: https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18

API docs: https://search.patentsview.org/docs/docs/Search%20API/SearchAPIReference/
Rate limit: 45 requests/minute per API key
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import time
import os

from .base import BaseCollector
from config.settings import TECHNOLOGY_KEYWORDS, TIER_1_COMPANIES, TIER_2_COMPANIES

logger = logging.getLogger(__name__)


class USPTOCollector(BaseCollector):
    """Collector for USPTO patents via PatentSearch API."""
    
    def __init__(self, api_key: str = None):
        super().__init__('uspto')
        self.base_url = "https://search.patentsview.org/api/v1/patent"
        self.api_key = api_key or os.getenv("PATENTSVIEW_API_KEY", "")
        self.rate_limit_delay = 1.5  # Stay under 45 req/min
        
        if not self.api_key:
            logger.warning("No PatentsView API key set. Get one at: https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18")
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect patents filed within date range.
        
        Default: Yesterday's filings.
        """
        if not self.api_key:
            logger.error("No API key - cannot collect from USPTO")
            return []
        
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=1)
        
        all_signals = []
        
        # Collect patents for each technology domain
        for domain, keywords in TECHNOLOGY_KEYWORDS.items():
            logger.info(f"Collecting {domain} patents...")
            try:
                signals = self._collect_by_keywords(keywords, date_from, date_to, domain)
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"Error collecting {domain} patents: {e}")
        
        # Deduplicate by patent number
        seen = set()
        unique_signals = []
        for sig in all_signals:
            if sig['source_id'] not in seen:
                seen.add(sig['source_id'])
                unique_signals.append(sig)
        
        logger.info(f"Collected {len(unique_signals)} unique patents")
        return unique_signals
    
    def _collect_by_keywords(
        self, 
        keywords: List[str], 
        date_from: datetime, 
        date_to: datetime,
        domain: str
    ) -> List[Dict[str, Any]]:
        """Collect patents matching keywords in title or abstract."""
        
        date_from_str = date_from.strftime('%Y-%m-%d')
        date_to_str = date_to.strftime('%Y-%m-%d')
        
        # Build query for new PatentSearch API
        # Use _text_any for keyword matching
        keyword_conditions = [{"_text_any": {"patent_abstract": kw}} for kw in keywords[:5]]
        
        query = {
            "_and": [
                {"_gte": {"patent_date": date_from_str}},
                {"_lte": {"patent_date": date_to_str}},
                {"_or": keyword_conditions}
            ]
        }
        
        # Fields to retrieve
        fields = [
            "patent_id",
            "patent_title", 
            "patent_abstract",
            "patent_date",
            "patent_type",
            "assignees.assignee_organization",
            "inventors.inventor_name_first",
            "inventors.inventor_name_last",
            "cpcs.cpc_group_id"
        ]
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "f": fields,
            "o": {"size": 100}
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"USPTO API request failed: {e}")
            return []
        except ValueError as e:
            logger.error(f"Failed to parse USPTO response: {e}")
            return []
        
        if data.get('error'):
            logger.error(f"USPTO API error: {data}")
            return []
        
        patents = data.get('patents', [])
        signals = []
        
        for patent in patents:
            if not patent:
                continue
                
            # Extract entities
            entities = self._extract_entities(patent, domain)
            
            # Build URL
            patent_id = patent.get('patent_id', '')
            url = f"https://patents.google.com/patent/US{patent_id}"
            
            signal = self._standardize_signal(
                raw_data=patent,
                source_id=patent_id,
                title=patent.get('patent_title', ''),
                abstract=patent.get('patent_abstract', ''),
                date=self._parse_date(patent.get('patent_date')),
                url=url,
                entities=entities
            )
            
            # Add domain tag
            signal['domain'] = domain
            
            signals.append(signal)
        
        logger.info(f"Found {len(signals)} patents for {domain}")
        return signals
    
    def _extract_entities(self, patent: Dict, domain: str) -> Dict[str, List[str]]:
        """Extract companies and technologies from patent data."""
        entities = {
            'companies': [],
            'technologies': [domain]
        }
        
        # Extract assignee (company)
        assignees = patent.get('assignees', [])
        if assignees:
            for assignee in assignees:
                if assignee and isinstance(assignee, dict):
                    org = assignee.get('assignee_organization', '')
                    if org:
                        entities['companies'].append(org)
                        # Check tier
                        for t1 in TIER_1_COMPANIES:
                            if t1.lower() in org.lower():
                                entities['tier'] = 1
                                break
                        for t2 in TIER_2_COMPANIES:
                            if t2.lower() in org.lower():
                                entities['tier'] = entities.get('tier', 2)
        
        # Extract technology keywords from abstract
        abstract = (patent.get('patent_abstract') or '').lower()
        title = (patent.get('patent_title') or '').lower()
        text = f"{title} {abstract}"
        
        for tech_domain, keywords in TECHNOLOGY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text:
                    if tech_domain not in entities['technologies']:
                        entities['technologies'].append(tech_domain)
        
        return entities
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string from USPTO."""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return datetime.now()


# TRL detection from claims/abstract
TRL_KEYWORDS = {
    7: ["field trial", "pilot", "commercial", "customer", "production", "deployed"],
    6: ["demonstration", "prototype", "system test", "validation", "validated"],
    5: ["component test", "subsystem", "proof of concept", "lab scale", "laboratory"],
}


def estimate_trl(text: str) -> int:
    """Estimate Technology Readiness Level from text."""
    text_lower = text.lower()
    for trl, keywords in sorted(TRL_KEYWORDS.items(), reverse=True):
        for kw in keywords:
            if kw in text_lower:
                return trl
    return 4  # Default: basic research


if __name__ == "__main__":
    # Test the collector
    import os
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("PATENTSVIEW_API_KEY")
    if not api_key:
        print("Set PATENTSVIEW_API_KEY environment variable")
        print("Get a key at: https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18")
        exit(1)
    
    collector = USPTOCollector(api_key)
    
    # Collect last 7 days for testing
    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    
    signals = collector.collect(date_from, date_to)
    
    print(f"\nCollected {len(signals)} patents")
    for sig in signals[:5]:
        print(f"\n--- {sig['source_id']} ---")
        print(f"Title: {sig['title'][:80]}...")
        print(f"Domain: {sig.get('domain')}")
        print(f"Companies: {sig['entities'].get('companies', [])}")
        print(f"URL: {sig['url']}")
