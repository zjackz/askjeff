from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.import_batch import ImportBatch, ProductRecord
from app.models.extraction import ExtractionTask, ExtractionItem
from app.models.extraction_run import ExtractionRun
from app.models.export_job import ExportJob
from app.models.system_log import SystemLog
from app.models.query_session import QuerySession
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.delete("/data")
def delete_all_data(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete all data except users and reset ID sequences (Admin only).
    
    注意: 此操作会删除所有业务数据,但保留用户表(users),
    确保管理员账号不会被删除,避免无法登录系统。
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 1. Delete data in order of dependencies
    # 注意: 用户表(users)被保留,不会被删除
    # Logs and sessions (independent or loosely coupled)
    db.query(SystemLog).delete()
    db.query(AuditLog).delete()
    db.query(QuerySession).delete()
    
    # Extraction Items (referencing tasks and products)
    db.query(ExtractionItem).delete()
    
    # Extraction Tasks (referencing batches)
    db.query(ExtractionTask).delete()
    
    # Extraction Runs (referencing batches)
    db.query(ExtractionRun).delete()
    
    # Products (referencing batches)
    db.query(ProductRecord).delete()
    
    # Import Batches
    db.query(ImportBatch).delete()
    
    # Export Jobs
    db.query(ExportJob).delete()
    
    # 2. Reset ID sequences for tables with Identity/autoincrement
    sequences_to_reset = [
        "import_batches_id_seq",
        "extraction_runs_id_seq",
        "export_jobs_id_seq",
        "system_logs_id_seq",
    ]
    
    for seq_name in sequences_to_reset:
        db.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
    
    db.commit()
    
    return {"message": "All data deleted and ID sequences reset successfully"}
