from typing import Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.services.data_engine_service import DataEngineService

router = APIRouter()

@router.post("/sync/{store_id}", response_model=Dict[str, Any])
def trigger_sync(
    store_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    days: int = 7
) -> Any:
    """
    Trigger a data sync for the specified store.
    Runs in background.
    """
    service = DataEngineService(db)
    
    # Check if store exists
    try:
        # We run it synchronously for now to see immediate errors, 
        # but in prod this should be a Celery task.
        # For the API response, we can just say "Started".
        # But for debugging, let's run it and return result.
        
        # background_tasks.add_task(service.sync_search_term_report, store_id, days)
        # return {"message": "Sync started in background"}
        
        result = service.sync_search_term_report(store_id, days)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
