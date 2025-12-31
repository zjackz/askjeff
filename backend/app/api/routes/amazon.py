from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.amazon_sync_service import AmazonSyncService

router = APIRouter()

@router.post("/stores/{store_id}/sync")
async def sync_store_data(
    store_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Trigger full synchronization for a store (Inventory, Business Reports, Ads).
    Runs in background.
    """
    service = AmazonSyncService(db)
    
    # Run sync in background to avoid timeout
    background_tasks.add_task(service.sync_all, store_id=store_id)
    
    return {"message": "Sync started in background"}
