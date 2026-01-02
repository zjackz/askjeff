from datetime import datetime
from typing import Any, Dict, Optional
import logging

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

from .base import BaseStorage

logger = logging.getLogger(__name__)

Base = declarative_base()

class RawDataLog(Base):
    """
    Table to store raw JSON data from external sources.
    This is the 'Lake' in our Data Lakehouse.
    """
    __tablename__ = 'jdc_raw_data_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), index=True, nullable=False)      # e.g., 'amazon_ads'
    data_type = Column(String(50), index=True, nullable=False)   # e.g., 'search_term_report'
    
    # The payload is stored as JSONB for efficient querying if needed, 
    # but primarily it's for archival.
    payload = Column(JSONB, nullable=False)
    
    # Metadata like report_id, request_params, etc.
    meta_info = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class PostgresStorage(BaseStorage):
    """
    PostgreSQL implementation of Raw Data Storage.
    """
    
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        
        # Auto-create table if it doesn't exist
        # In production, you might want to use Alembic, but for a standalone lib, 
        # this ensures it works out-of-the-box.
        Base.metadata.create_all(self.engine)

    def save_raw(self, source: str, data_type: str, payload: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> str:
        session = self.Session()
        try:
            log = RawDataLog(
                source=source,
                data_type=data_type,
                payload=payload,
                meta_info=meta
            )
            session.add(log)
            session.commit()
            return str(log.id)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save raw data: {e}")
            raise e
        finally:
            session.close()
