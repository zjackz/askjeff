import logging
from datetime import date, timedelta
from typing import Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.amazon_ads import AmazonStore
from app.config import settings
from app.db import engine
# Import from our standalone package
from jeff_data_core.core.engine import JeffDataEngine
from jeff_data_core.connectors.amazon_ads import AmazonAdsConnector, AmazonAdsConfig
from jeff_data_core.storage.postgres import PostgresStorage

logger = logging.getLogger(__name__)

class DataEngineService:
    """
    Service to bridge AskJeff domain with Jeff Data Core.
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize Storage with AskJeff's existing DB engine
        self.storage = PostgresStorage(engine=engine)
        self.engine = JeffDataEngine(storage_backend=self.storage)

    def sync_search_term_report(self, store_id: UUID, days: int = 7) -> Dict[str, Any]:
        """
        Triggers a Search Term Report sync for the given store.
        """
        store = self.db.query(AmazonStore).filter(AmazonStore.id == store_id).first()
        if not store:
            raise ValueError(f"Store {store_id} not found")

        # In a real scenario, we would decrypt the refresh token here
        # For now, we assume it's available or we use a placeholder if testing
        refresh_token = store.advertising_api_refresh_token or "mock_token"
        
        # Configure Connector
        config = AmazonAdsConfig(
            name=f"amazon_ads_{store.store_name}",
            client_id=getattr(settings, 'amazon_ads_client_id', None) or "mock_id",
            client_secret=getattr(settings, 'amazon_ads_client_secret', None) or "mock_secret",
            refresh_token=refresh_token,
            profile_id=store.seller_id, # Usually profile_id is different from seller_id, but using as placeholder
            region="NA" # Default to NA
        )
        
        connector = AmazonAdsConnector(config)
        
        # Define date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Triggering JDC sync for store {store.store_name} ({start_date} - {end_date})")
        
        # Execute Sync
        result = self.engine.run_sync(connector, start_date, end_date)
        
        return result
