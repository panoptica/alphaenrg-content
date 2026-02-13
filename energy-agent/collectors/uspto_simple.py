"""
USPTO Patent Collector - Simple Exact Matches Only.

Since the API only supports exact equality, this version searches 
for exact organization matches without date filtering.
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import time
import os

from .base import BaseCollector
from config.settings import TIER_1_COMPANIES, TIER_2_COMPANIES

logger = logging.getLogger(__name__)


class USPTOCollector(BaseCollector):
    """Simplified USPTO patent collector - exact matches only."""
    
    def __init__(self, api_key: str = None):
        super().__init__("uspto")
        self.base_url = "https://search.patentsview.org/api/v1/patent"
        self.api_key = api_key or os.getenv("PATENTSVIEW_API_KEY", "")
        self.rate_limit_delay = 2.0
        
        # Exact company names (must match exactly in API)
        self.exact_companies = [
            "Tesla, Inc.",
            "General Electric Company", 
            "Microsoft Corporation",
            "Apple Inc.",
            "Samsung Electronics Co., Ltd.",
            "Toyota Motor Corporation",
            "Ford Motor Company",
            "General Motors LLC",
            "Panasonic Corporation",
            "LG Energy Solution, Ltd."
        ]
        
        if not self.api_key:
            logger.warning("No PatentsView API key set")
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect patents from major companies.
        Note: Date filtering not supported, gets recent patents from these companies.
        """
        if not self.api_key:
            logger.error("No API key - cannot collect from USPTO")
            return []
        
        all_signals = []
        
        # Search each company (limit to first few to avoid rate limits)
        for company in self.exact_companies[:5]:
            try:
                signals = self._collect_by_exact_company(company)
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)
                
                if len(all_signals) >= 30:  # Limit total
                    break
                    
            except Exception as e:
                logger.error(f"Error collecting {company} patents: {e}")
        
        # Deduplicate 
        seen = set()
        unique_signals = []
        for sig in all_signals:
            if sig["source_id"] not in seen:
                seen.add(sig["source_id"])
                unique_signals.append(sig)
        
        logger.info(f"Collected {len(unique_signals)} unique patents")
        return unique_signals
    
    def _collect_by_exact_company(self, company: str) -> List[Dict[str, Any]]:
        """Collect patents from exact company name match."""
        
        # Simple exact match query (known to work)
        query = {"assignees.assignee_organization": company}
        
        fields = [
            "patent_id",
            "patent_title", 
            "patent_abstract",
            "patent_date",
            "assignees"
        ]
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "f": fields,
            "o": {"per_page": 10}  # Small batches
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
            logger.error(f"USPTO API request failed for {company}: {e}")
            return []
        except ValueError as e:
            logger.error(f"Failed to parse response for {company}: {e}")
            return []
        
        if data.get("error"):
            logger.error(f"USPTO API error for {company}: {data}")
            return []
        
        patents = data.get("patents", [])
        signals = []
        
        for patent in patents:
            if not patent:
                continue
                
            # Extract entities
            entities = {
                "companies": [company],
                "technologies": [self._classify_domain(patent)]
            }
            
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
            
            signal["domain"] = self._classify_domain(patent)
            signals.append(signal)
        
        logger.info(f"Found {len(signals)} patents for {company}")
        return signals
    
    def _classify_domain(self, patent: Dict) -> str:
        """Classify patent into technology domain."""
        title = patent.get("patent_title", "")
        abstract = patent.get("patent_abstract", "")
        text = (title + " " + abstract).lower()
        
        if any(kw in text for kw in ["battery", "lithium", "cell"]):
            return "battery"
        elif any(kw in text for kw in ["solar", "photovoltaic"]):
            return "solar"
        elif any(kw in text for kw in ["wind", "turbine"]):
            return "wind"
        elif any(kw in text for kw in ["hydrogen", "fuel cell"]):
            return "hydrogen"
        else:
            return "energy"
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string."""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.now()
