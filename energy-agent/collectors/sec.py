"""
SEC EDGAR Collector.

Free access to SEC filings - no API key required.
Uses the full-text search API and RSS feeds.

Relevant forms:
- 8-K: Material events (acquisitions, agreements, leadership changes)
- 10-K: Annual reports (MD&A sections for strategic insights)
- 10-Q: Quarterly reports
- Form 4: Insider trading

API docs: https://www.sec.gov/search-filings/edgar-search-assistance
Full-text search: https://efts.sec.gov/LATEST/search-index
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import time
import re

from .base import BaseCollector
from config.settings import TECHNOLOGY_KEYWORDS, TIER_1_COMPANIES, TIER_2_COMPANIES

logger = logging.getLogger(__name__)

# Companies to monitor for energy/cooling/quantum filings
WATCHLIST_COMPANIES = [
    # Hyperscalers (data center demand)
    "Alphabet", "Google", "Microsoft", "Amazon", "Meta", "Nvidia",
    # Cooling/thermal specialists
    "Vertiv", "nVent", "Schneider Electric", "Boyd", "Modine",
    # Energy/nuclear
    "NuScale", "Oklo", "Centrus Energy", "BWX Technologies", "Fluor",
    # Industrials with energy exposure
    "GE Vernova", "Siemens", "Rolls-Royce", "Honeywell",
    # Quantum
    "IonQ", "Rigetti", "D-Wave",
]

# CIK numbers for key companies (Central Index Key for SEC)
COMPANY_CIKS = {
    "Alphabet": "1652044",
    "Google": "1652044",  # Same as Alphabet
    "Microsoft": "789019",
    "Amazon": "1018724",
    "Meta": "1326801",
    "Nvidia": "1045810",
    "Vertiv": "1674101",
    "nVent": "1720635",
    "NuScale": "1822966",
    "Oklo": "1849056",
    "IonQ": "1838359",
    "Rigetti": "1838349",
}


class SECCollector(BaseCollector):
    """Collector for SEC EDGAR filings."""
    
    def __init__(self):
        super().__init__('sec')
        self.search_url = "https://efts.sec.gov/LATEST/search-index"
        self.filings_url = "https://data.sec.gov/submissions"
        self.rate_limit_delay = 0.5  # SEC asks for 10 req/sec max
        
        # Required by SEC: identify yourself
        self.headers = {
            "User-Agent": "EnergyIntelligenceAgent/1.0 (contact@example.com)",
            "Accept-Encoding": "gzip, deflate"
        }
    
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect SEC filings.
        
        Strategy:
        1. Search for keyword mentions in recent filings
        2. Check watchlist companies for any new filings
        """
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=7)
        
        all_signals = []
        
        # Strategy 1: Keyword search across all filings
        logger.info("Searching SEC filings by keywords...")
        keyword_signals = self._search_by_keywords(date_from, date_to)
        all_signals.extend(keyword_signals)
        
        # Strategy 2: Check watchlist companies
        logger.info("Checking watchlist company filings...")
        watchlist_signals = self._check_watchlist(date_from, date_to)
        all_signals.extend(watchlist_signals)
        
        # Deduplicate
        seen = set()
        unique = []
        for sig in all_signals:
            if sig['source_id'] not in seen:
                seen.add(sig['source_id'])
                unique.append(sig)
        
        logger.info(f"Collected {len(unique)} unique SEC filings")
        return unique
    
    def _search_by_keywords(self, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Search SEC filings for energy/cooling/quantum keywords."""
        
        # Key search terms (SEC full-text search)
        search_terms = [
            '"data center" AND (cooling OR thermal)',
            '"liquid cooling" OR "immersion cooling"',
            '"small modular reactor" OR SMR',
            'nuclear AND (energy OR power) AND agreement',
            'quantum AND (computing OR technology)',
            '"energy storage" OR "battery storage"',
            'hydrogen AND (production OR fuel)',
        ]
        
        all_results = []
        
        for term in search_terms:
            try:
                results = self._full_text_search(term, date_from, date_to)
                all_results.extend(results)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"SEC search failed for '{term}': {e}")
        
        return all_results
    
    def _full_text_search(self, query: str, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Execute full-text search on SEC EDGAR."""
        
        # SEC full-text search API
        url = "https://efts.sec.gov/LATEST/search-index"
        
        params = {
            "q": query,
            "dateRange": "custom",
            "startdt": date_from.strftime('%Y-%m-%d'),
            "enddt": date_to.strftime('%Y-%m-%d'),
            "forms": "8-K,10-K,10-Q",  # Focus on material filings
            "from": 0,
            "size": 50
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"SEC API error: {e}")
            return []
        except ValueError:
            # SEC sometimes returns HTML error pages
            logger.error("SEC returned non-JSON response")
            return []
        
        hits = data.get('hits', {}).get('hits', [])
        signals = []
        
        for hit in hits:
            source = hit.get('_source', {})
            filing_id = hit.get('_id', '')
            
            # Extract domain from search query
            domain = self._infer_domain(query)
            
            signal = self._standardize_signal(
                raw_data=source,
                source_id=filing_id,
                title=f"{source.get('form', 'Filing')} - {source.get('display_names', ['Unknown'])[0]}",
                abstract=source.get('file_description', ''),
                date=self._parse_date(source.get('file_date')),
                url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&filenum={source.get('file_num', '')}",
                entities=self._extract_entities(source)
            )
            signal['domain'] = domain
            signal['form_type'] = source.get('form', '')
            signal['company'] = source.get('display_names', ['Unknown'])[0]
            
            signals.append(signal)
        
        return signals
    
    def _check_watchlist(self, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Check for new filings from watchlist companies."""
        signals = []
        
        for company, cik in COMPANY_CIKS.items():
            try:
                company_filings = self._get_company_filings(cik, company, date_from, date_to)
                signals.extend(company_filings)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.warning(f"Failed to get filings for {company}: {e}")
        
        return signals
    
    def _get_company_filings(self, cik: str, company: str, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Get recent filings for a specific company."""
        
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch filings for CIK {cik}: {e}")
            return []
        
        filings = data.get('filings', {}).get('recent', {})
        
        signals = []
        forms = filings.get('form', [])
        dates = filings.get('filingDate', [])
        accessions = filings.get('accessionNumber', [])
        descriptions = filings.get('primaryDocDescription', [])
        
        for i, (form, date_str, accession, desc) in enumerate(zip(forms, dates, accessions, descriptions)):
            # Parse date and check range
            try:
                filing_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                continue
            
            if not (date_from <= filing_date <= date_to):
                continue
            
            # Only interested in certain form types
            if form not in ['8-K', '10-K', '10-Q', '4', 'S-1', 'DEFA14A']:
                continue
            
            accession_clean = accession.replace('-', '')
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}"
            
            signal = self._standardize_signal(
                raw_data={'form': form, 'date': date_str, 'accession': accession},
                source_id=accession,
                title=f"{form} - {company}: {desc or 'Filing'}",
                abstract=desc or f"{form} filing",
                date=filing_date,
                url=filing_url,
                entities={
                    'companies': [company],
                    'technologies': [],
                    'tier': 1 if company in TIER_1_COMPANIES else 2
                }
            )
            signal['domain'] = 'general'  # Will be refined during scoring
            signal['form_type'] = form
            signal['company'] = company
            
            # 8-K Item analysis (if available)
            if form == '8-K':
                signal['priority'] = 'high'  # 8-Ks are time-sensitive
            
            signals.append(signal)
            
            # Limit per company
            if len(signals) >= 10:
                break
        
        return signals
    
    def _extract_entities(self, source: Dict) -> Dict[str, List[str]]:
        """Extract entities from SEC filing data."""
        entities = {
            'companies': [],
            'technologies': []
        }
        
        # Get company names
        names = source.get('display_names', [])
        entities['companies'] = names
        
        # Check tiers
        for name in names:
            for t1 in TIER_1_COMPANIES:
                if t1.lower() in name.lower():
                    entities['tier'] = 1
                    break
        
        return entities
    
    def _infer_domain(self, query: str) -> str:
        """Infer technology domain from search query."""
        query_lower = query.lower()
        
        if 'cooling' in query_lower or 'thermal' in query_lower:
            return 'cooling'
        elif 'nuclear' in query_lower or 'smr' in query_lower:
            return 'smr'
        elif 'quantum' in query_lower:
            return 'quantum'
        elif 'hydrogen' in query_lower:
            return 'hydrogen'
        elif 'battery' in query_lower or 'storage' in query_lower:
            return 'battery'
        else:
            return 'general'
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date from SEC data."""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str[:10], '%Y-%m-%d')
        except ValueError:
            return datetime.now()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = SECCollector()
    
    # Test: last 30 days
    date_to = datetime.now()
    date_from = date_to - timedelta(days=30)
    
    signals = collector.collect(date_from, date_to)
    
    print(f"\nCollected {len(signals)} SEC filings")
    for sig in signals[:10]:
        print(f"\n{sig.get('form_type', '?')} | {sig['title'][:60]}...")
        print(f"  Date: {sig['date'].strftime('%Y-%m-%d')}")
        print(f"  Domain: {sig.get('domain')}")
        print(f"  URL: {sig['url']}")
