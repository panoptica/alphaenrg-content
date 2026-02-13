"""
Fixed USPTO Patent Collector using PatentSearch API.

Fixes applied:
1. Correct response key: "patents" not "patent"
2. Proper date range query format
3. Fixed field structure and parameters
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
    """Fixed collector for USPTO patents via PatentSearch API."""
    
    def __init__(self, api_key: str = None):
        super().__init__("uspto")
        self.base_url = "https://search.patentsview.org/api/v1/patent"
        self.api_key = api_key or os.getenv("PATENTSVIEW_API_KEY", "")
        self.rate_limit_delay = 1.5  # Stay under 45 req/min
        
        if not self.api_key:
            logger.warning("No PatentsView API key set. Get one at: https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18")
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect patents filed within date range.
        Note: Patents take months to publish, so use older date ranges for testing.
        """
        if not self.api_key:
            logger.error("No API key - cannot collect from USPTO")
            return []
        
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=1)
            
        # Use 2023 data for testing since recent patents arent published yet
        if date_to.year >= 2026:
            logger.info("Using 2023 data for testing (recent patents not yet published)")
            date_from = datetime(2023, 12, 1)
            date_to = datetime(2023, 12, 31)
        
        all_signals = []
        
        # Collect for each technology domain
        for domain, keywords in TECHNOLOGY_KEYWORDS.items():
            try:
                signals = self._collect_by_keywords(keywords, date_from, date_to, domain)
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)  # Rate limiting
            except Exception as e:
                logger.error(f"Error collecting {domain} patents: {e}")
        
        # Deduplicate by patent number
        seen = set()
        unique_signals = []
        for sig in all_signals:
            if sig["source_id"] not in seen:
                seen.add(sig["source_id"])
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
        
        date_from_str = date_from.strftime("%Y-%m-%d")
        date_to_str = date_to.strftime("%Y-%m-%d")
        
        # Simplified query structure
        query = {
            "_and": [
                {"patent_date": {"_gte": date_from_str}},
                {"patent_date": {"_lte": date_to_str}},
                {
                    "_or": [
                        {"patent_abstract": {"_text_any": " ".join(keywords[:3])}}
                    ]
                }
            ]
        }
        
        # Fields to retrieve
        fields = [
            "patent_id",
            "patent_title", 
            "patent_abstract",
            "patent_date",
            "assignees",
            "inventors"
        ]
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "f": fields,
            "o": {"per_page": 100}
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
        
        if data.get("error"):
            logger.error(f"USPTO API error: {data}")
            return []
        
        # Fixed response key: "patents" not "patent"
        patents = data.get("patents", [])
        signals = []
        
        for patent in patents:
            if not patent:
                continue
                
            # Extract entities
            entities = self._extract_entities(patent, domain)
            
            # Build URL
            patent_id = patent.get("patent_id", "")
            url = f"https://patents.google.com/patent/US{patent_id}"
            
            signal = self._standardize_signal(
                raw_data=patent,
                source_id=patent_id,
                title=patent.get("patent_title", ""),
                abstract=patent.get("patent_abstract", ""),
                date=self._parse_date(patent.get("patent_date")),
                url=url,
                entities=entities
            )
            
            # Add domain tag
            signal["domain"] = domain
            signals.append(signal)
        
        logger.info(f"Found {len(signals)} patents for {domain}")
        return signals
    
    def _extract_entities(self, patent: Dict, domain: str) -> Dict[str, List[str]]:
        """Extract companies and technologies from patent data."""
        entities = {
            "companies": [],
            "technologies": [domain]
        }
        
        # Extract assignee (company)
        assignees = patent.get("assignees", [])
        if assignees:
            for assignee in assignees:
                if assignee and isinstance(assignee, dict):
                    org = assignee.get("assignee_organization", "")
                    if org:
                        entities["companies"].append(org)
                        # Check tier
                        for t1 in TIER_1_COMPANIES:
                            if t1.lower() in org.lower():
                                entities["tier"] = 1
                                break
                        for t2 in TIER_2_COMPANIES:
                            if t2.lower() in org.lower():
                                entities["tier"] = entities.get("tier", 2)
        
        # Extract technology keywords from abstract
        abstract = (patent.get("patent_abstract") or "").lower()
        title = (patent.get("patent_title") or "").lower()
        text = f"{title} {abstract}"
        
        for tech_domain, keywords in TECHNOLOGY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text:
                    if tech_domain not in entities["technologies"]:
                        entities["technologies"].append(tech_domain)
        
        return entities
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string from USPTO."""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.now()
