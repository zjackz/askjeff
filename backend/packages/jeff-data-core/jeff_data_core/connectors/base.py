from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator
from datetime import date
from pydantic import BaseModel

class ConnectorConfig(BaseModel):
    """Base configuration for all connectors"""
    name: str
    timeout: int = 30
    max_retries: int = 3

class BaseConnector(ABC):
    """
    Abstract Base Class for all Data Connectors.
    Enforces a standard interface for fetching data.
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Check if the provided credentials are valid."""
        pass

    @abstractmethod
    def fetch_data(self, start_date: date, end_date: date, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Yields raw data records (dicts) from the source.
        Using a generator allows handling large datasets without memory issues.
        """
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Returns the type of source (e.g., 'amazon_ads', 'shopify')."""
        pass
