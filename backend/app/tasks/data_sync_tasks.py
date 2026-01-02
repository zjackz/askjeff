import logging
from app.celery_app import celery_app
from app.db import SessionLocal
from app.models.amazon_ads import AmazonStore
from app.services.data_engine_service import DataEngineService

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.sync_all_stores_search_terms")
def sync_all_stores_search_terms(days: int = 7):
    """
    Scheduled task to sync Search Term Reports for all active stores.
    """
    logger.info("Starting scheduled Search Term Report sync...")
    
    db = SessionLocal()
    try:
        # Fetch all active stores
        stores = db.query(AmazonStore).filter(AmazonStore.is_active == True).all()
        logger.info(f"Found {len(stores)} active stores.")
        
        service = DataEngineService(db)
        
        for store in stores:
            try:
                logger.info(f"Syncing store: {store.store_name} ({store.id})")
                service.sync_search_term_report(store.id, days=days)
            except Exception as e:
                logger.error(f"Failed to sync store {store.store_name}: {e}")
                # Continue to next store even if one fails
                continue
                
    except Exception as e:
        logger.error(f"Critical error in sync task: {e}")
    finally:
        db.close()
