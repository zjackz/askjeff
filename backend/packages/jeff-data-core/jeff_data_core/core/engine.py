from typing import Any, Dict, Optional
from datetime import date
import logging

from jeff_data_core.connectors.base import BaseConnector
from jeff_data_core.storage.base import BaseStorage

logger = logging.getLogger(__name__)

class JeffDataEngine:
    """
    The Orchestrator.
    Manages the flow of data from Connectors to Storage.
    """
    
    def __init__(self, storage_backend: BaseStorage):
        self.storage = storage_backend

    def run_sync(self, connector: BaseConnector, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Executes a sync job for a given connector.
        """
        logger.info(f"Starting sync for {connector.source_type} from {start_date} to {end_date}")
        
        if not connector.validate_credentials():
            raise ValueError(f"Invalid credentials for {connector.source_type}")

        record_count = 0
        try:
            # Fetch data generator
            for record in connector.fetch_data(start_date, end_date):
                # Save to Raw Store
                # We wrap the record in a structure that identifies its type
                # For Search Term Reports, 'record' is a single row. 
                # Ideally, we might want to batch save, but for simplicity we save row-by-row 
                # or if the connector yields pages/reports, we save those.
                
                # NOTE: AmazonAdsConnector yields individual rows. 
                # Saving every row as a separate JSONB entry might be too granular/slow.
                # A better approach for the connector would be to yield chunks or the whole report.
                # But assuming 'record' is a meaningful unit:
                
                self.storage.save_raw(
                    source=connector.source_type,
                    data_type="search_term_report_row", # TODO: Make this dynamic based on connector
                    payload=record,
                    meta={
                        "start_date": str(start_date),
                        "end_date": str(end_date)
                    }
                )
                record_count += 1
                
            logger.info(f"Sync completed. Fetched and saved {record_count} records.")
            return {
                "status": "success",
                "records_synced": record_count
            }
            
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
