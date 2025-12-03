from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api import deps
from app.models.user import User
from app.models.import_batch import ImportBatch, ProductRecord
from app.models.extraction import ExtractionTask, ExtractionItem
from app.models.extraction_run import ExtractionRun
from app.models.export_job import ExportJob
from app.models.system_log import SystemLog

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.delete("/data")
def delete_all_data(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete all data (Admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete data in order of dependencies
    # 1. Logs (referencing tasks/batches/products?) - Logs usually independent or loose
    db.query(SystemLog).delete()
    
    # 2. Extraction Items (referencing tasks and products)
    db.query(ExtractionItem).delete()
    
    # 3. Extraction Tasks (referencing batches)
    db.query(ExtractionTask).delete()
    
    # 3.5 Extraction Runs (referencing batches)
    db.query(ExtractionRun).delete()
    
    # 4. Products (referencing batches)
    db.query(ProductRecord).delete()
    
    # 5. Import Batches
    db.query(ImportBatch).delete()
    
    # 6. Export Jobs
    db.query(ExportJob).delete()
    
    # Reset sequences if needed (optional, but good for "clean slate")
    # db.execute(text("ALTER SEQUENCE products_id_seq RESTART WITH 1"))
    
    db.commit()
    
    return {"message": "All data deleted successfully"}
