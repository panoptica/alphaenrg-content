"""
USPTO Patent Collector - Company-Based Approach.

Since text searches are failing, this version searches for patents 
from major energy companies instead of keywords.
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
    """Company-based USPTO patent collector."""
    
    def __init__(self, api_key: str = None):
        super().__init__("uspto")
        self.base_url = "https://search.patentsview.org/api/v1/patent"
        self.api_key = api_key or os.getenv("PATENTSVIEW_API_KEY", "")
        self.rate_limit_delay = 2.0  # Stay under 45 req/min
        
        # Major energy companies to search for
        self.energy_companies = [
            "Tesla", "General Electric", "Siemens", "Microsoft", "Google",
            "Apple", "Samsung", "Toyota", "Ford", "GM", "Volkswagen",
            "BYD", "CATL", "Panasonic", "LG Energy", "SK Innovation",
            "Vestas", "Orsted", "NextEra", "Enel", "EDF", "Shell",
            "BP", "ExxonMobil", "TotalEnergies", "Chevron"
        ]
        
        if not self.api_key:
            logger.warning("No PatentsView API key set")
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect patents from major energy companies.
        Uses 2023 data since recent patents aren\""t published yet.
        """
        if not self.api_key:
            logger.error("No API key - cannot collect from USPTO")
            return []
        
        # Use 2023 data (patents take time to publish)
        logger.info("Using 2023 data (recent patents not yet published)")
        date_from = datetime(2023, 1, 1)
        date_to = datetime(2023, 12, 31)
        
        all_signals = []
        
        # Search for each company
        for company in self.energy_companies:
            try:
                signals = self._collect_by_company(company, date_from, date_to)
                all_signals.extend(signals)
                time.sleep(self.rate_limit_delay)  # Rate limiting
                
                if len(all_signals) >= 50:  # Limit total results
                    break
                    
            except Exception as e:
                logger.error(f"Error collecting {company} patents: {e}")
        
        # Deduplicate by patent number
        seen = set()
        unique_signals = []
        for sig in all_signals:
            if sig["source_id"] not in seen:
                seen.add(sig["source_id"])
                unique_signals.append(sig)
        
        logger.info(f"Collected {len(unique_signals)} unique patents")
        return unique_signals
    
    def _collect_by_company(
        self, 
        company: str,
        date_from: datetime, 
        date_to: datetime
    ) -> List[Dict[str, Any]]:
        """Collect patents from a specific company."""
        
        date_from_str = date_from.strftime("%Y-%m-%d")
        date_to_str = date_to.strftime("%Y-%m-%d")
        
        # Company + date query (known to work)
        query = {
            "_and": [
                {"patent_date": {"_gte": date_from_str}},
                {"patent_date": {"_lte": date_to_str}},
                {"assignees.assignee_organization": {"_contains": company}}
            ]
        }
        
        # Fields to retrieve
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
            "o": {"per_page": 20}  # Limit per company
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
            logger.error(f"Failed to parse USPTO response for {company}: {e}")
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
            entities = self._extract_entities(patent, company)
            
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
            
            # Add domain tag based on content
            signal["domain"] = self._classify_domain(patent)
            signals.append(signal)
        
        logger.info(f"Found {len(signals)} patents for {company}")
        return signals
    
    def _extract_entities(self, patent: Dict, company: str) -> Dict[str, List[str]]:
        """Extract companies and technologies from patent data."""
        entities = {
            "companies": [company],
            "technologies": []
        }
        
        # Extract all assignees
        assignees = patent.get("assignees", [])
        for assignee in assignees:
            if assignee and isinstance(assignee, dict):
                org = assignee.get("assignee_organization", "")
                if org and org not in entities["companies"]:
                    entities["companies"].append(org)
                    
                # Check tier
                for t1 in TIER_1_COMPANIES:
                    if t1.lower() in org.lower():
                        entities["tier"] = 1
                        break
                for t2 in TIER_2_COMPANIES:
                    if t2.lower() in org.lower():
                        entities["tier"] = entities.get("tier", 2)
        
        return entities
    
    def _classify_domain(self, patent: Dict) -> str:
        """Classify patent into technology domain based on title/abstract."""
        title = patent.get("patent_title", "")
        abstract = patent.get("patent_abstract", "")
        text = (title + " " + abstract).lower()
        abstract = patent.get("patent_abstract", "")
        text = f"{title} {abstract}".lower()
        if any(kw in text for kw in ["battery", "lithium", "cell", "energy storage"]):
            return "battery"
        elif any(kw in text for kw in ["solar", "photovoltaic", "pv"]):
            return "solar"
        elif any(kw in text for kw in ["wind", "turbine"]):
            return "wind"
        elif any(kw in text for kw in ["hydrogen", "fuel cell", "electrolysis"]):
            return "hydrogen"
        elif any(kw in text for kw in ["nuclear", "reactor", "uranium"]):
            return "nuclear"
        elif any(kw in text for kw in ["cooling", "thermal", "heat"]):
            return "cooling"
        else:
            return "energy"
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string from USPTO."""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.now()
