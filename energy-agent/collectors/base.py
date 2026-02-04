"""
Base collector class that all data collectors inherit from.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for all data collectors."""
    
    def __init__(self, name: str):
        self.name = name
        self.collected_at = None
    
    @abstractmethod
    def collect(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        """
        Collect signals from the data source.
        
        Args:
            date_from: Start date for collection (default: yesterday)
            date_to: End date for collection (default: today)
            
        Returns:
            List of signal dictionaries with standardized fields:
            - source: str (e.g., 'uspto', 'sec', 'arxiv')
            - source_id: str (unique ID from source)
            - title: str
            - abstract: str
            - date: datetime
            - url: str
            - raw_data: dict (original response)
            - entities: dict (extracted companies, technologies)
        """
        pass
    
    def _standardize_signal(self, raw_data: Dict, **kwargs) -> Dict[str, Any]:
        """Convert raw data to standardized signal format."""
        return {
            'source': self.name,
            'source_id': kwargs.get('source_id', ''),
            'title': kwargs.get('title', ''),
            'abstract': kwargs.get('abstract', ''),
            'date': kwargs.get('date', datetime.now()),
            'url': kwargs.get('url', ''),
            'raw_data': raw_data,
            'entities': kwargs.get('entities', {'companies': [], 'technologies': []}),
            'collected_at': datetime.now()
        }
