from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseStorage(ABC):
    """
    Abstract Base Class for Data Storage.
    Responsible for persisting Raw Data (ELT 'Load' step).
    """

    @abstractmethod
    def save_raw(self, source: str, data_type: str, payload: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> str:
        """
        Saves a raw data record.
        
        Args:
            source: The origin of data (e.g., 'amazon_ads')
            data_type: The specific type (e.g., 'search_term_report')
            payload: The actual data dictionary
            meta: Additional metadata (e.g., report_id, fetch_time)
            
        Returns:
            The ID of the saved record.
        """
        pass
